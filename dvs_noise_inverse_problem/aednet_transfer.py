"""Zero-shot transfer of the released AEDNet weights to EBSSA and DND21.

AEDNet (Fang et al., ACM Multimedia 2022) is a supervised point-set network
that classifies every event from the (x, y) offsets of the events in a
spatio-temporal neighbourhood.  The authors released the code and one set of
trained weights (DVSCLEAN background-activity model, 1280 x 720 sensor).  No
weights for DAVIS-class sensors exist and no labelled training set comparable
to DVSCLEAN exists for EBSSA or DND21, so the only faithful thing that can be
done with the public artefacts is to apply the released model unchanged.  That
is what this script does; it is a transfer test of a fixed model, not a
re-training, and it is reported as such.

What is reproduced from the official repository
-----------------------------------------------
* the network (``BA_noise_removal/aednet.py``, ``ResAEDNet``) and the released
  ``AEDNet_model.pth`` / ``AEDNet_params.pth`` (pinned commit and SHA-256 below)
* the patch construction of ``dataprocess.AEDPatchDataset.select_patch_points``
  (x_lim = 25, y_lim = 15, points_per_patch = 50, 'point' centring,
  t_lim = duration / round(n / 5000)), re-implemented here with numpy because
  the official loader is a per-event Python loop and the official inference
  script is CUDA-only.  ``--parity`` checks the re-implementation against the
  official loader and model on the authors' own sample file.

What is different from the official inference
---------------------------------------------
* CPU inference (the official ``test_net.py`` calls ``.cuda()`` unconditionally)
* the sensor frame is set to the actual sensor of each recording instead of
  1280 x 720; the pixel-unit neighbourhood (25 x 15 px) is kept as released
* the whole recording is one 'shape' (the official script cuts files into
  100 000-event chunks); recordings here are <= 200 000 events
* the softmax probability of the 'noise' class is used as a continuous score
  so that ROC-AUC can be computed; the official script thresholds at argmax
* only a stratified random subset of events per recording is scored (CPU
  cost ~50 events/s); ROC-AUC is invariant to class prior, so the subset AUC
  is an unbiased estimate of the full-stream AUC.  The subset AUC of the
  label-free detector is reported next to its full-stream AUC as a direct
  measurement of the sampling error.

Usage
-----
    python3 aednet_transfer.py --parity          # official-vs-reimplementation check
    python3 aednet_transfer.py --dataset dnd21   # 80 DND21 mixtures
    python3 aednet_transfer.py --dataset ebssa   # 43 EBSSA recordings
    python3 aednet_transfer.py --summarise       # results/aednet_transfer.json
"""

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

import event_driven as ed
import sp_evaluation as sp

HERE = Path(__file__).resolve().parent
RESULTS = HERE / 'results'
CACHE = RESULTS / 'sp_cache'
AEDNET_DIR = HERE / 'data' / 'aednet' / 'AEDNet'

REPO_URL = 'https://github.com/Fanghuachen/AEDNet'
REPO_COMMIT = '4fca5c512fb01b7b92be1ac5531aed2d46f3d3a4'
WEIGHTS_URL = f'{REPO_URL}/releases/download/AEDNet/AEDNet_model.pth'
WEIGHTS_SHA256 = 'e20c3da6c43345b8905380b62bc7f9ce4535fc2b135eb0f60096701651583e30'
PAPER_DOI = '10.1145/3503161.3548048'

# released hyper-parameters (models/BA_noise_removal_model/AEDNet_params.pth)
X_LIM, Y_LIM, POINTS_PER_PATCH = 25, 15, 50
N_PER_CLASS = 1500          # scored events per class per recording
SEED = sp.SEED
BATCH = 256


# ---------------------------------------------------------------------------
# Official artefacts
# ---------------------------------------------------------------------------

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_aednet():
    if not (AEDNET_DIR / 'BA_noise_removal' / 'aednet.py').exists():
        AEDNET_DIR.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--quiet', REPO_URL, str(AEDNET_DIR)], check=True)
    subprocess.run(['git', '-C', str(AEDNET_DIR), 'checkout', '--quiet', REPO_COMMIT], check=True)
    weights = AEDNET_DIR / 'models' / 'BA_noise_removal_model' / 'AEDNet_model.pth'
    if not weights.exists() or sha256(weights) != WEIGHTS_SHA256:
        print(f'downloading {WEIGHTS_URL}', flush=True)
        urllib.request.urlretrieve(WEIGHTS_URL, weights)
    digest = sha256(weights)
    if digest != WEIGHTS_SHA256:
        raise RuntimeError(f'AEDNet_model.pth sha256 {digest} != {WEIGHTS_SHA256}')
    return AEDNET_DIR


def load_model():
    root = ensure_aednet()
    sys.path.insert(0, str(root / 'BA_noise_removal'))
    from aednet import ResAEDNet
    params = torch.load(root / 'models' / 'BA_noise_removal_model' / 'AEDNet_params.pth',
                        map_location='cpu', weights_only=False)
    assert (params.points_per_patch, params.x_lim, params.y_lim) == (POINTS_PER_PATCH, X_LIM, Y_LIM)
    model = ResAEDNet(num_points=params.points_per_patch, output_dim=2,
                      use_point_stn=params.use_point_stn, use_feat_stn=params.use_feat_stn,
                      sym_op=params.sym_op)
    state = torch.load(root / 'models' / 'BA_noise_removal_model' / 'AEDNet_model.pth',
                       map_location='cpu')
    model.load_state_dict(state)
    model.eval()
    return model, params


# ---------------------------------------------------------------------------
# Patch construction (numpy re-implementation of select_patch_points)
# ---------------------------------------------------------------------------

def t_lim_official(t):
    """dataprocess.load_test_shape: t_lim = (t_max - t_min) / round(num / 5000)."""
    return (t.max() - t.min()) / max(round(len(t) / 5000), 1)


def _axis_bounds(c, lim, frame):
    if c <= lim / 2:
        return -np.inf, lim
    if c >= frame - lim / 2:
        return frame - lim, np.inf
    return c - lim / 2, c + lim / 2


def build_patches(x, y, t, centre_idx, x_frame, y_frame, t_lim,
                  x_lim=X_LIM, y_lim=Y_LIM, k=POINTS_PER_PATCH):
    """Return (len(centre_idx), k, 2) float32 offsets exactly as the official loader.

    x, y, t must already be sorted by t (the official loader sorts once per file).
    """
    out = np.zeros((len(centre_idx), k, 2), dtype=np.float32)
    half = int(0.5 * k)
    for j, i in enumerate(centre_idx):
        lo = np.searchsorted(t, t[i] - t_lim, side='left')
        hi = np.searchsorted(t, t[i] + t_lim, side='right')
        xs, ys = x[lo:hi], y[lo:hi]
        xa, xb = _axis_bounds(x[i], x_lim, x_frame)
        ya, yb = _axis_bounds(y[i], y_lim, y_frame)
        keep = (xs >= xa) & (xs <= xb) & (ys >= ya) & (ys <= yb)
        idx = np.nonzero(keep)[0] + lo
        c = int(np.searchsorted(idx, i))
        n = len(idx)
        if n < k:
            sel = np.full(k, idx[c])
            sel[:n] = idx
        elif c <= half:
            sel = idx[:k]
        elif c >= n - half:
            sel = idx[n - k:]
        else:
            sel = idx[c - half:c + half]
        out[j, :, 0] = x[sel] - x[i]
        out[j, :, 1] = y[sel] - y[i]
    return out


@torch.no_grad()
def noise_probability(model, patches):
    """Softmax probability of the AEDNet 'noise' class (label 1 in the released data)."""
    p = np.empty(len(patches), dtype=np.float64)
    for s in range(0, len(patches), BATCH):
        pts = torch.from_numpy(patches[s:s + BATCH]).transpose(2, 1)   # (B, 2, k)
        logits, _, _, _ = model(pts)
        p[s:s + BATCH] = F.softmax(logits, dim=1)[:, 1].numpy()
    return p


def stratified_subset(lab, rng, n_per_class=N_PER_CLASS):
    sig = np.flatnonzero(lab)
    noi = np.flatnonzero(~lab)
    pick = np.concatenate([rng.choice(sig, min(n_per_class, len(sig)), replace=False),
                           rng.choice(noi, min(n_per_class, len(noi)), replace=False)])
    return np.sort(pick)


def score_recording(model, ev, lab, shape, rng):
    """shape is (H, W) as everywhere else in this project."""
    h, w = shape
    x = ev['x'].astype(np.float64)
    y = ev['y'].astype(np.float64)
    t = ev['t'].astype(np.float64)
    assert np.all(np.diff(t) >= 0)
    sub = stratified_subset(lab, rng)
    t0 = time.perf_counter()
    patches = build_patches(x, y, t, sub, w, h, t_lim_official(t))
    p_noise = noise_probability(model, patches)
    dt = time.perf_counter() - t0
    m_sub = sp.compute_metrics(lab[sub], p_noise)
    # label-free detector on the full stream, then restricted to the same subset:
    # the gap between the two AUCs is the sampling error of the subset design
    zc = sp.ZERO_KNOWLEDGE_CONFIG
    rate, window_us = ed.adaptive_window_us(ev, shape, zc['radius'], zc['expected_count'],
                                            zc['interval_quantile'])
    p_zk = np.asarray(ed.sliding_window_lr(ev, shape, radius=zc['radius'], window_us=window_us,
                                           rate=rate), dtype=np.float64)
    p_yn = np.asarray(sp.ynoise_filter(ev, shape, dt_us=30e3, radius=2), dtype=np.float64)
    return {
        'n_events': len(ev), 'n_scored': len(sub),
        'n_scored_signal': int(lab[sub].sum()), 'n_scored_noise': int((~lab[sub]).sum()),
        'sensor_hw': [int(h), int(w)], 't_lim_us': float(t_lim_official(t)),
        'aednet_auc_subset': m_sub['auc'],
        'aednet_removal_rate_subset': m_sub['removal_rate'],
        'aednet_nrr_subset': m_sub['nrr'], 'aednet_spr_subset': m_sub['spr'],
        'zero_knowledge_auc_subset': sp.compute_metrics(lab[sub], p_zk[sub])['auc'],
        'zero_knowledge_auc_full': sp.compute_metrics(lab, p_zk)['auc'],
        'ynoise_default_auc_subset': sp.compute_metrics(lab[sub], p_yn[sub])['auc'],
        'ynoise_default_auc_full': sp.compute_metrics(lab, p_yn)['auc'],
        'aednet_time_s': float(dt),
    }


# ---------------------------------------------------------------------------
# Parity with the official loader / model on the authors' sample file
# ---------------------------------------------------------------------------

def parity(model, n_check=400):
    root = ensure_aednet()
    sys.path.insert(0, str(root / 'BA_noise_removal'))
    if not hasattr(np, 'int'):
        np.int = int  # the official loader uses the numpy<1.24 alias
    import dataprocess as official
    sample = root / 'data' / 'AEDNetTestset_BA' / 'MAH00444_50.npy'
    raw = np.load(sample)
    n_total = len(raw)
    ds = official.AEDPatchDataset(
        root=str(sample.parent), shapes_list_file=None, shape_num=n_total,
        points_per_patch=POINTS_PER_PATCH, x_limitation=X_LIM, y_limitation=Y_LIM,
        x_frame=1280, y_frame=720, seed=SEED, center='point', cache_capacity=1,
        shape_names=[sample.stem], train=False, label=True)
    shape = ds.shape_cache.get(0)
    # released .npy layout: [label, x, y, t, polarity]; label 1 = noise
    x, y, t = shape.pts[:, 0].astype(float), shape.pts[:, 1].astype(float), shape.pts[:, 2].astype(float)
    rng = np.random.default_rng(SEED)
    idx = np.sort(rng.choice(len(x), n_check, replace=False))
    mine = build_patches(x, y, t, idx, 1280, 720, shape.t_lim)
    theirs = np.stack([ds[int(i)][0].numpy() for i in idx]).astype(np.float32)
    patch_diff = float(np.abs(mine - theirs).max())
    p_mine = noise_probability(model, mine)
    p_theirs = noise_probability(model, theirs)
    labels = shape.labels[idx].astype(int)
    acc = float(((p_mine > 0.5).astype(int) == labels).mean())
    auc_sample = sp.compute_metrics(labels == 0, p_mine)['auc']
    return {'sample_file': sample.name, 'n_events_in_file': int(n_total), 'n_checked': int(n_check),
            'max_abs_patch_difference': patch_diff,
            'max_abs_probability_difference': float(np.abs(p_mine - p_theirs).max()),
            'accuracy_on_sample_at_0.5': acc, 'auc_on_sample': auc_sample,
            't_lim_us': float(shape.t_lim)}


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------

def iter_dnd21():
    import dnd21_evaluation as dnd
    for rec_id, src, cond, ev, lab, meta in dnd.build_recordings():
        yield rec_id, ev, lab, dnd.SENSOR, {'source': src, 'condition': cond, **meta}


def iter_ebssa():
    for idx, ev, lab, shape, rec_id in sp.load_recordings():
        yield str(rec_id), ev, lab, shape, {'index': int(idx)}


def run(dataset, model):
    CACHE.mkdir(parents=True, exist_ok=True)
    partial = CACHE / f'aednet_{dataset}.json'
    done = json.loads(partial.read_text()) if partial.exists() else {}
    rng = np.random.default_rng(SEED)
    it = iter_dnd21() if dataset == 'dnd21' else iter_ebssa()
    for rec_id, ev, lab, shape, meta in it:
        # the rng must advance identically whether or not a record is cached
        sub_rng = np.random.default_rng(rng.integers(2**63))
        if rec_id in done:
            continue
        r = score_recording(model, ev, lab, shape, sub_rng)
        r.update({'recording_id': rec_id, **meta})
        done[rec_id] = r
        partial.write_text(json.dumps(done, indent=1))
        print(f"{rec_id} n={r['n_events']} aednet={r['aednet_auc_subset']:.3f} "
              f"zk_sub={r['zero_knowledge_auc_subset']:.3f} zk_full={r['zero_knowledge_auc_full']:.3f} "
              f"({r['aednet_time_s']:.0f}s)", flush=True)
    return done


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def _boot_mean_diff(a, b, clusters, rng, n_boot=2000):
    a, b = np.asarray(a), np.asarray(b)
    d = a - b
    labs = np.unique(clusters)
    groups = [np.flatnonzero(clusters == c) for c in labs]
    boots = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.integers(len(groups), size=len(groups))
        idx = np.concatenate([groups[g] for g in pick])
        boots[i] = d[idx].mean()
    return {'mean': float(d.mean()), 'ci95': [float(np.percentile(boots, 2.5)),
                                             float(np.percentile(boots, 97.5))],
            'n_units': len(d), 'n_clusters': len(groups)}


def summarise():
    rng = np.random.default_rng(SEED)
    out = {
        'method': 'AEDNet, released DVSCLEAN background-activity weights applied unchanged (zero-shot transfer)',
        'paper_doi': PAPER_DOI, 'code_url': REPO_URL, 'code_commit': REPO_COMMIT,
        'weights_url': WEIGHTS_URL, 'weights_sha256': WEIGHTS_SHA256,
        'released_hyperparameters': {'points_per_patch': POINTS_PER_PATCH, 'x_lim_px': X_LIM,
                                     'y_lim_px': Y_LIM, 'patch_center': 'point',
                                     'training_sensor': '1280x720 (DVSCLEAN)',
                                     't_lim_rule': 'duration / round(n_events / 5000)'},
        'adaptations': ['CPU inference (official test_net.py is CUDA-only)',
                        'sensor frame set to the recording sensor; 25x15 px neighbourhood kept',
                        'whole recording as one shape (official: 100000-event chunks)',
                        'softmax noise probability used as a ranking score for ROC-AUC',
                        f'stratified subset of <= {N_PER_CLASS} signal + {N_PER_CLASS} noise events per recording'],
        'environment': {'python': platform.python_version(), 'torch': torch.__version__,
                        'cuda_available': bool(torch.cuda.is_available()), 'machine': platform.machine()},
        'n_per_class': N_PER_CLASS, 'seed': SEED,
    }
    par = CACHE / 'aednet_parity.json'
    if par.exists():
        out['official_parity'] = json.loads(par.read_text())
    for ds in ('dnd21', 'ebssa'):
        partial = CACHE / f'aednet_{ds}.json'
        if not partial.exists():
            continue
        recs = list(json.loads(partial.read_text()).values())
        if ds == 'dnd21':
            # '<source>_s<k>_<condition>' -> '<source>_s<k>' (conditions have one '_')
            clusters = np.array([r['recording_id'].rsplit('_', 2)[0] for r in recs])
        else:
            clusters = np.arange(len(recs))
        ae = np.array([r['aednet_auc_subset'] for r in recs])
        zk_s = np.array([r['zero_knowledge_auc_subset'] for r in recs])
        zk_f = np.array([r['zero_knowledge_auc_full'] for r in recs])
        yn_s = np.array([r['ynoise_default_auc_subset'] for r in recs])
        yn_f = np.array([r['ynoise_default_auc_full'] for r in recs])
        s = {
            'n_recordings': len(recs),
            'aednet_mean_auc': float(ae.mean()), 'aednet_median_auc': float(np.median(ae)),
            'aednet_sd_auc': float(ae.std(ddof=1)) if len(ae) > 1 else 0.0,
            'aednet_min_auc': float(ae.min()), 'aednet_max_auc': float(ae.max()),
            'aednet_fraction_below_chance': float((ae < 0.5).mean()),
            'aednet_mean_removal_rate': float(np.mean([r['aednet_removal_rate_subset'] for r in recs])),
            'zero_knowledge_mean_auc_subset': float(zk_s.mean()),
            'zero_knowledge_mean_auc_full': float(zk_f.mean()),
            'ynoise_default_mean_auc_subset': float(yn_s.mean()),
            'ynoise_default_mean_auc_full': float(yn_f.mean()),
            'subset_sampling_error_max_abs': float(max(np.abs(zk_s - zk_f).max(), np.abs(yn_s - yn_f).max())),
            'zero_knowledge_minus_aednet': _boot_mean_diff(zk_s, ae, clusters, rng),
            'ynoise_default_minus_aednet': _boot_mean_diff(yn_s, ae, clusters, rng),
            'wins_zero_knowledge_over_aednet': int((zk_s > ae).sum()),
            'mean_seconds_per_recording': float(np.mean([r['aednet_time_s'] for r in recs])),
        }
        if ds == 'dnd21':
            s['by_source'] = {src: float(np.mean([r['aednet_auc_subset'] for r in recs if r['source'] == src]))
                              for src in sorted({r['source'] for r in recs})}
            s['by_condition'] = {c: float(np.mean([r['aednet_auc_subset'] for r in recs if r['condition'] == c]))
                                 for c in sorted({r['condition'] for r in recs})}
        out[ds] = {'summary': s, 'per_recording': sorted(recs, key=lambda r: r['recording_id'])}
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'aednet_transfer.json').write_text(json.dumps(out, indent=1) + '\n')
    for ds in ('dnd21', 'ebssa'):
        if ds in out:
            s = out[ds]['summary']
            print(f"{ds}: AEDNet {s['aednet_mean_auc']:.3f}  ZK(subset) {s['zero_knowledge_mean_auc_subset']:.3f} "
                  f"ZK(full) {s['zero_knowledge_mean_auc_full']:.3f}  YN(subset) {s['ynoise_default_mean_auc_subset']:.3f}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parity', action='store_true')
    ap.add_argument('--dataset', choices=['dnd21', 'ebssa'])
    ap.add_argument('--summarise', action='store_true')
    args = ap.parse_args()
    torch.manual_seed(SEED)
    if args.parity or args.dataset:
        model, _ = load_model()
    if args.parity:
        CACHE.mkdir(parents=True, exist_ok=True)
        res = parity(model)
        (CACHE / 'aednet_parity.json').write_text(json.dumps(res, indent=1))
        print(json.dumps(res, indent=1))
    if args.dataset:
        run(args.dataset, model)
    if args.summarise or args.dataset:
        summarise()


if __name__ == '__main__':
    main()
