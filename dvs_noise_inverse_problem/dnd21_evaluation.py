#!/usr/bin/env python3
"""Cross-dataset, cross-sensor evaluation on DND21 (DAVIS346) recordings.

EBSSA (sp_evaluation.py) provides the primary benchmark: real astronomical
recordings with bounding-box labels from two sensor configurations.  This
module answers the generalisation question with a second, independent
dataset recorded on a third sensor (DAVIS346, 346 x 260 pixels): the DND21
benchmark of Guo and Delbruck (IEEE TPAMI 2022, https://sites.google.com/view/dnd21).

DND21 follows the standard protocol of the event-denoising literature: a
signal recording that is free of, or nearly free of, background activity is
mixed with *measured* sensor noise recorded with the lens capped or under
constant illumination.  Because every event is known to come from either the
signal recording or the noise recording, the labels are exact.  The mixing
here is documented completely so that it can be reproduced:

* signal sources: the ``hotel-bar`` DAVIS346 recording (real scene, the
  segment published as the low-noise reference), the ``driving`` sequence
  (v2e rendering with shot and leak noise disabled), and the two sparse
  synthetic targets ``5-dots-barely-visible`` and ``accelerating-dot``
  (v2e, noise disabled).  The two sparse targets are the closest analogue in
  DND21 to the point-like transits of EBSSA.
* noise sources: the measured DAVIS346 recordings ``noise dark 5p3Hz`` (lens
  capped, about 5.4 Hz per pixel) and ``light background activity`` (uniform
  illumination, about 0.1 Hz per pixel).  The dark recording is thinned by
  independent Bernoulli sampling to the nominal per-pixel rates of
  ``NOISE_RATES_HZ``; the light recording is used at its native rate.
* segments: from every signal source ``N_SEGMENTS`` evenly spaced windows of
  at most ``SEGMENT_S`` seconds are cut; each is paired with a distinct slice
  of the noise recording so that no noise event is reused across segments.
  A segment mixed with one noise condition is one "recording" of the
  evaluation and is truncated to ``sp_evaluation.MAX_EVENTS`` events.

Cross-validation is grouped by *signal source* (leave-one-source-out), so a
tuned or trained comparator never sees the scene it is scored on.  The same
nested selection as in sp_evaluation.py is used for every gridded method and
the supervised MLPF-style and EDnCNN-style classifiers are trained inside the
folds.  In addition, the label-free deployment path is scored without any
tuning on DND21:

* ``ebssa_transfer``  every gridded method at the configuration selected on
                      EBSSA (modal CV choice of sp_evaluation_summary.json)
* ``zero_knowledge``  the rate-adaptive proposed detector at its fixed
                      deployment configuration
* ``ynoise_default``  YNoise at its published parameters
* ``ynoise_handoff``  YNoise with dt set to the window W that the proposed
                      detector derived from the stream (no labels)
* ``hybrid``          the two-stage screen-then-confirm front end with the
                      hand-over parameters

Outputs: results/dnd21_evaluation_summary.json, results/dnd21_per_recording.json
Resumable through results/sp_cache/dnd21_*.
"""

import hashlib
import json
import time
from pathlib import Path

import numpy as np
import torch
from scipy.stats import wilcoxon

import event_driven as ed
import sp_evaluation as sp
from aedat2 import read_aedat2

RESULTS = Path(__file__).resolve().parent / 'results'
CACHE = RESULTS / 'sp_cache'
DATA = Path(__file__).resolve().parent / 'data' / 'dnd21'
EBSSA_SUMMARY = RESULTS / 'sp_evaluation_summary.json'

SENSOR = (260, 346)  # DAVIS346 (H, W)
SEGMENT_S = 1.0
N_SEGMENTS = 5
TARGET_EVENTS = 100000  # segment duration is shortened so that a mixed segment stays near this
NOISE_RATES_HZ = (0.5, 1.0, 3.0, 5.0)
SCREEN_FRACTIONS = (0.1, 0.2)
SEED = sp.SEED

# Google Drive file ids of the DND21 release (folder 1fR8x3lTcO7qpxfItNjvAbTx_6hyiI6i9)
FILES = {
    'hotel_bar': ('1v8XHwOZIl0N9MPdfYN1w-cQBzp1TPcUL', 'hotel-bar-segment.aedat'),
    'driving': ('10pZoLZWwuz0eyzARAH6QuodKsr-Ed-VV', 'driving.aedat'),
    'dots5': ('19ES2ELRcaXZENDKBk-8ttrmPTC9Hfbfn', '5-dots-barely-viisible.aedat'),
    'accel_dot': ('1tiQwLEvhzkk5c3LwgXK2cxeSI86Xli0X', 'accelerating-dot-2-pixels.aedat'),
    'noise_dark': ('10_LIC0xbLJ9TKNLB_IRSI6wvWqp0lzdX',
                   'Davis346blue-2021-06-14T20-09-08+0200-00000003-0 noise dark 5p3Hz.aedat'),
    'noise_light': ('1YRtzTHQBIIHw1D1AfMnhWUDc4cbYq9N1',
                    'Davis346blue-2020-10-17T13-42-27+0200-00000002-0 light background activity.aedat'),
}
SIGNAL_SOURCES = {
    'hotel_bar': 'real DAVIS346 indoor scene (low-noise reference segment)',
    'driving': 'v2e rendering of a driving video, noise disabled',
    'dots5': 'v2e, five barely visible moving dots, noise disabled',
    'accel_dot': 'v2e, accelerating two-pixel dot, noise disabled',
}
# (label, source key, nominal per-pixel rate in Hz or None for native rate)
NOISE_CONDITIONS = [('light_native', 'noise_light', None)] + [
    (f'dark_{r:g}hz', 'noise_dark', r) for r in NOISE_RATES_HZ]

EVENT_DTYPE = np.dtype([('x', '<i8'), ('y', '<i8'), ('t', '<i8'), ('p', '<i8')])


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

def fetch(key):
    file_id, name = FILES[key]
    path = DATA / name
    if not path.exists():
        import gdown
        DATA.mkdir(parents=True, exist_ok=True)
        gdown.download(id=file_id, output=str(path), quiet=False)
    return path


def load(key):
    ev = read_aedat2(fetch(key))
    out = np.empty(len(ev), dtype=EVENT_DTYPE)
    for f in ('x', 'y', 't', 'p'):
        out[f] = ev[f]
    out['t'] -= out['t'].min()
    return out


def slice_time(ev, t0_us, t1_us):
    lo, hi = np.searchsorted(ev['t'], [t0_us, t1_us])
    return ev[lo:hi]


def per_pixel_rate(ev):
    dur = (ev['t'].max() - ev['t'].min()) / 1e6
    return len(ev) / dur / (SENSOR[0] * SENSOR[1])


def build_recordings():
    """Yield (recording_id, source, condition, events, labels, meta)."""
    rng = np.random.default_rng(SEED)
    noise = {k: load(k) for k in ('noise_dark', 'noise_light')}
    noise_rate = {k: per_pixel_rate(v) for k, v in noise.items()}
    noise_cursor = {k: 0.0 for k in noise}  # seconds of the noise stream already used
    n_pix = SENSOR[0] * SENSOR[1]
    for src in SIGNAL_SOURCES:
        sig = load(src)
        sig_dur = sig['t'].max() / 1e6
        sig_rate = len(sig) / sig_dur
        n_seg = max(1, min(N_SEGMENTS, int(sig_dur // SEGMENT_S)))
        starts = np.linspace(0.0, max(sig_dur - SEGMENT_S, 0.0), n_seg)
        for s_idx, start in enumerate(starts):
            # a fresh slice of measured noise for every (source, segment); the
            # same slice is thinned to every nominal rate of that segment
            slice_start = dict(noise_cursor)
            for nkey in noise_cursor:
                noise_cursor[nkey] += SEGMENT_S
            for cond, nkey, rate in NOISE_CONDITIONS:
                r = noise_rate[nkey] if rate is None else rate
                if r > noise_rate[nkey] * 1.001:
                    continue  # cannot thin upwards
                dur = min(SEGMENT_S, sig_dur - start, TARGET_EVENTS / (sig_rate + r * n_pix))
                seg = slice_time(sig, int(start * 1e6), int((start + dur) * 1e6))
                n0 = slice_start[nkey]
                nz = slice_time(noise[nkey], int(n0 * 1e6), int((n0 + dur) * 1e6))
                keep_p = r / noise_rate[nkey]
                if keep_p < 1.0:
                    nz = nz[rng.random(len(nz)) < keep_p]
                nz = nz.copy()
                nz['t'] = nz['t'] - int(n0 * 1e6) + int(start * 1e6)
                ev = np.concatenate([seg, nz])
                lab = np.concatenate([np.ones(len(seg), bool), np.zeros(len(nz), bool)])
                order = np.argsort(ev['t'], kind='stable')
                ev, lab = ev[order], lab[order]
                if len(ev) > sp.MAX_EVENTS:
                    ev, lab = ev[:sp.MAX_EVENTS], lab[:sp.MAX_EVENTS]
                if lab.sum() < 50 or (~lab).sum() < 50:
                    continue
                meta = {'segment_start_s': float(start), 'duration_s': float(dur),
                        'nominal_noise_rate_hz': float(r),
                        'noise_source_rate_hz': float(noise_rate[nkey]),
                        'noise_slice_start_s': float(n0)}
                yield f'{src}_s{s_idx}_{cond}', src, cond, ev, lab, meta


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

GRIDS = {**sp.GRID_METHODS, **sp.EXTRA_GRID_METHODS}


def fingerprint():
    cfg = {'grids': {k: v[1] for k, v in GRIDS.items()},
           'zk': sp.ZERO_KNOWLEDGE_CONFIG, 'segment_s': SEGMENT_S, 'n_segments': N_SEGMENTS,
           'target': TARGET_EVENTS, 'rates': NOISE_RATES_HZ, 'fractions': SCREEN_FRACTIONS,
           'max_events': sp.MAX_EVENTS, 'seed': SEED, 'sensor': SENSOR,
           'conditions': NOISE_CONDITIONS, 'files': sorted(FILES.items()),
           'signal_sources': sorted(SIGNAL_SOURCES), 'patch_r': sp.PATCH_R, 'tau_us': sp.TAU_US,
           'schema': 2}
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def auc(lab, p):
    return sp.compute_metrics(lab, p)['auc']


def score_recording(rec_id, ev, lab, meta):
    shape = SENSOR
    r = {'recording_id': rec_id, 'n_events': len(ev), 'signal_fraction': float(lab.mean()),
         'event_rate_hz': float(len(ev) / max(meta['duration_s'], 1e-6)), 'metrics': {},
         'grid_auc': {}, 'time_s': {}}
    scores, timings = sp.run_unsupervised(ev, shape, 0)
    r['metrics'].update({m: sp.compute_metrics(lab, p) for m, p in scores.items()})
    r['time_s'].update({m: float(t) for m, t in timings.items()})
    for name, (fn, grid) in GRIDS.items():
        t0 = time.time()
        r['grid_auc'][name] = [auc(lab, fn(ev, shape, **cfg)) for cfg in grid]
        r['time_s'][name] = (time.time() - t0) / len(grid)
    # label-free deployment path
    zc = sp.ZERO_KNOWLEDGE_CONFIG
    t0 = time.perf_counter()
    rate, window_us = ed.adaptive_window_us(ev, shape, zc['radius'], zc['expected_count'],
                                            zc['interval_quantile'])
    p1 = np.asarray(ed.sliding_window_lr(ev, shape, radius=zc['radius'], window_us=window_us,
                                         rate=rate), dtype=np.float64)
    r['time_s']['zero_knowledge'] = time.perf_counter() - t0
    r['window_us'] = float(window_us)
    r['metrics']['zero_knowledge'] = sp.compute_metrics(lab, p1)
    p_def = sp.ynoise_filter(ev, shape, dt_us=30e3, radius=2)
    p_hand = sp.ynoise_filter(ev, shape, dt_us=window_us, radius=zc['radius'])
    r['metrics']['ynoise_default'] = sp.compute_metrics(lab, p_def)
    r['metrics']['ynoise_handoff'] = sp.compute_metrics(lab, p_hand)
    for f in SCREEN_FRACTIONS:
        thr = np.quantile(p1, f)
        cand = p1 < thr
        if cand.sum() < 0.5 * f * len(p1):
            cand = p1 <= thr
        if cand.sum() < 10:
            continue
        p2 = np.asarray(sp.ynoise_filter(ev[cand], shape, dt_us=window_us, radius=zc['radius']),
                        dtype=np.float64)
        ph = 0.5 + 0.5 * p1
        ph[cand] = 0.5 * p2
        r['metrics'][f'hybrid_{f:g}'] = sp.compute_metrics(lab, ph)
        r['metrics'][f'hybrid_{f:g}']['passed_fraction'] = float(cand.mean())
    return r


def score_pass():
    CACHE.mkdir(parents=True, exist_ok=True)
    partial = CACHE / 'dnd21_pass1.json'
    recs = []
    if partial.exists():
        saved = json.load(open(partial))
        if saved.get('fingerprint') == fingerprint():
            recs = saved['records']
        else:
            print('discarding dnd21_pass1.json: settings changed')
    done = {r['recording_id'] for r in recs}
    for rec_id, src, cond, ev, lab, meta in build_recordings():
        if rec_id in done:
            continue
        t0 = time.time()
        r = score_recording(rec_id, ev, lab, meta)
        r.update({'source': src, 'condition': cond, **meta})
        feats = sp.extract_features(ev, SENSOR)
        np.save(CACHE / f'dnd21_feat_{rec_id}.npy', feats)
        np.save(CACHE / f'dnd21_lab_{rec_id}.npy', lab)
        r['n_features'] = int(feats.shape[1])
        recs.append(r)
        print(f'{rec_id} n={len(ev)} sig={lab.mean():.3f} W={r["window_us"] / 1e3:.0f}ms '
              f'edlr_zk={r["metrics"]["zero_knowledge"]["auc"]:.3f} '
              f'ynoise_def={r["metrics"]["ynoise_default"]["auc"]:.3f} '
              f'handoff={r["metrics"]["ynoise_handoff"]["auc"]:.3f} ({time.time() - t0:.0f}s)',
              flush=True)
        tmp = partial.with_suffix('.tmp')
        json.dump({'fingerprint': fingerprint(), 'records': recs}, open(tmp, 'w'))
        tmp.replace(partial)
    return recs


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def paired(ref, other):
    d = np.asarray(ref) - np.asarray(other)
    if np.allclose(d, 0):
        return {'auc_diff_mean': 0.0, 'p_raw': 1.0}
    return {'auc_diff_mean': float(d.mean()), 'p_raw': float(wilcoxon(ref, other).pvalue)}


def holm(tests):
    order = sorted(tests, key=lambda m: tests[m]['p_raw'])
    prev = 0.0
    for rank, m in enumerate(order):
        adj = min(1.0, max(prev, (len(order) - rank) * tests[m]['p_raw']))
        prev = adj
        tests[m]['p_holm'] = adj


def main():
    recs = score_pass()
    sources = list(SIGNAL_SOURCES)
    folds = {src: i for i, src in enumerate(sources)}
    for r in recs:
        r['fold'] = folds[r['source']]

    # nested selection of every gridded configuration, leave-one-source-out
    selected = {name: {} for name in GRIDS}
    for name, (_, grid) in GRIDS.items():
        for fold in range(len(sources)):
            train = [r for r in recs if r['fold'] != fold]
            mean_auc = [float(np.mean([r['grid_auc'][name][c] for r in train]))
                        for c in range(len(grid))]
            selected[name][fold] = int(np.argmax(mean_auc))
        for r in recs:
            c = selected[name][r['fold']]
            r['metrics'][name] = {'auc': r['grid_auc'][name][c]}
            r.setdefault('selected_config', {})[name] = grid[c]

    # EBSSA-selected configurations applied unchanged (no DND21 labels used)
    ebssa = json.load(open(EBSSA_SUMMARY)) if EBSSA_SUMMARY.exists() else None
    transfer_cfg = {}
    if ebssa is not None:
        for name, (_, grid) in sp.GRID_METHODS.items():
            cfg = sp.modal_config(ebssa, name)
            keys = [json.dumps(c, sort_keys=True) for c in grid]
            c = keys.index(json.dumps(cfg, sort_keys=True))
            transfer_cfg[name] = cfg
            for r in recs:
                r['metrics'][f'{name}_ebssa'] = {'auc': r['grid_auc'][name][c]}

    # supervised classifiers, trained inside the folds
    rng = np.random.default_rng(SEED)
    k = 2 * sp.PATCH_R + 1
    n_feat = recs[0]['n_features']
    for fold in range(len(sources)):
        train = [r for r in recs if r['fold'] != fold]
        test = [r for r in recs if r['fold'] == fold]
        xs, ys = [], []
        for r in train:
            f = np.load(CACHE / f"dnd21_feat_{r['recording_id']}.npy")
            lab = np.load(CACHE / f"dnd21_lab_{r['recording_id']}.npy")
            pos, neg = np.flatnonzero(lab), np.flatnonzero(~lab)
            n_pos = min(len(pos), sp.TRAIN_EVENTS_PER_REC // 2)
            n_neg = min(len(neg), sp.TRAIN_EVENTS_PER_REC - n_pos)
            sel = np.concatenate([rng.choice(pos, n_pos, replace=False),
                                  rng.choice(neg, n_neg, replace=False)])
            xs.append(f[sel])
            ys.append(lab[sel])
        x_train, y_train = np.concatenate(xs), np.concatenate(ys)
        torch.manual_seed(SEED + fold)
        for name, model in (('mlpf', sp.MLPF(n_feat)), ('edncnn', sp.EDnCNNStyle(k))):
            sp.train_supervised(model, x_train, y_train)
            for r in test:
                f = np.load(CACHE / f"dnd21_feat_{r['recording_id']}.npy")
                lab = np.load(CACHE / f"dnd21_lab_{r['recording_id']}.npy")
                r['metrics'][name] = sp.compute_metrics(lab, sp.predict_supervised(model, f))
        print(f'fold {fold} (held out: {sources[fold]}) supervised done', flush=True)

    methods = sorted({m for r in recs for m in r['metrics']})
    label_free = (['zero_knowledge', 'ynoise_default', 'ynoise_handoff']
                  + [f'hybrid_{f:g}' for f in SCREEN_FRACTIONS]
                  + [f'{n}_ebssa' for n in transfer_cfg])

    def agg(subset):
        return {m: sp._summarise([r['metrics'][m]['auc'] for r in subset if m in r['metrics']])
                for m in methods}

    tests_tuned = {m: paired([r['metrics'][sp.PROPOSED]['auc'] for r in recs],
                             [r['metrics'][m]['auc'] for r in recs])
                   for m in list(GRIDS) + sp.UNSUPERVISED + sp.SUPERVISED if m != sp.PROPOSED}
    holm(tests_tuned)
    tests_free = {m: paired([r['metrics']['zero_knowledge']['auc'] for r in recs],
                            [r['metrics'][m]['auc'] for r in recs])
                  for m in label_free if m != 'zero_knowledge' and all(m in r['metrics'] for r in recs)}
    holm(tests_free)
    handoff_vs_default = paired([r['metrics']['ynoise_handoff']['auc'] for r in recs],
                                [r['metrics']['ynoise_default']['auc'] for r in recs])

    strata = {}
    for cond, _, _ in NOISE_CONDITIONS:
        sub = [r for r in recs if r['condition'] == cond]
        if sub:
            strata[f'noise_{cond}'] = {'n_recordings': len(sub), **agg(sub)}
    for src in sources:
        sub = [r for r in recs if r['source'] == src]
        strata[f'source_{src}'] = {'n_recordings': len(sub), **agg(sub)}

    summary = {
        'dataset': 'DND21 (Guo and Delbruck, IEEE TPAMI 2022), DAVIS346, 346x260 px',
        'sensor_shape': list(SENSOR),
        'signal_sources': SIGNAL_SOURCES,
        'noise_conditions': [{'label': c, 'source': s, 'nominal_rate_hz': r}
                             for c, s, r in NOISE_CONDITIONS],
        'ground_truth': 'exact: origin recording of every event (signal or measured noise)',
        'n_recordings': len(recs),
        'n_signal_sources': len(sources),
        'max_events_per_recording': sp.MAX_EVENTS,
        'segment_s': SEGMENT_S,
        'seed': SEED,
        'cv': {'type': 'leave-one-signal-source-out (grouped by scene)',
               'n_folds': len(sources), 'train_events_per_recording': sp.TRAIN_EVENTS_PER_REC},
        'proposed_method': sp.PROPOSED,
        'label_free_methods': label_free,
        'ebssa_transfer_configs': transfer_cfg,
        'zero_knowledge_config': sp.ZERO_KNOWLEDGE_CONFIG,
        'methods': agg(recs),
        'paired_tests_vs_proposed_tuned': tests_tuned,
        'paired_tests_vs_zero_knowledge': tests_free,
        'ynoise_handoff_vs_default': handoff_vs_default,
        'window_us': sp._summarise([r['window_us'] for r in recs]),
        'window_us_by_condition': {c: sp._summarise([r['window_us'] for r in recs if r['condition'] == c])
                                   for c, _, _ in NOISE_CONDITIONS
                                   if any(r['condition'] == c for r in recs)},
        'strata': strata,
        'runtime_s_per_recording': {m: sp._summarise([r['time_s'][m] for r in recs])
                                    for m in recs[0]['time_s']},
        'hyperparameter_grids': {name: grid for name, (_, grid) in GRIDS.items()},
        'selected_config_per_fold': {name: {str(f): GRIDS[name][1][c]
                                            for f, c in sel.items()}
                                     for name, sel in selected.items()},
    }
    RESULTS.mkdir(exist_ok=True)
    json.dump(summary, open(RESULTS / 'dnd21_evaluation_summary.json', 'w'), indent=1)
    slim = [{k: v for k, v in r.items() if k != 'grid_auc'} for r in recs]
    json.dump(slim, open(RESULTS / 'dnd21_per_recording.json', 'w'), indent=1)
    print(json.dumps({m: round(v['mean'], 3) for m, v in summary['methods'].items()}, indent=1))


if __name__ == '__main__':
    main()
