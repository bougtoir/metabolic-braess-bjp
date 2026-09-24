#!/usr/bin/env python3
"""Effect sizes with confidence intervals and cluster-level sensitivity tests.

Reads the frozen per-recording result files and adds what a paired Wilcoxon
p-value alone does not give a reader:

* EBSSA (results/sp_per_recording.json, 43 recordings): for every comparator,
  the mean paired AUC difference (proposed minus comparator) with a
  percentile bootstrap 95% CI over recordings, the number of recordings on
  which the proposal is ahead, and the matched-pairs rank-biserial
  correlation as a standardised effect size.

* DND21 (results/dnd21_per_recording.json, 80 mixtures): the 80 mixtures are
  not independent, because each signal segment is mixed with every noise
  condition and only four signal sources exist.  The main text therefore
  reports, next to the mixture-level Wilcoxon test, a sensitivity analysis at
  the level of the *signal segment* (mean AUC over the noise conditions of one
  segment; 20 segments) and the sign pattern at the level of the *signal
  source* (4 sources).  Bootstrap CIs on DND21 resample segments, i.e. they
  are cluster bootstraps.

Output: results/pr_effect_sizes.json
"""

import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

RESULTS = Path(__file__).resolve().parent / 'results'
N_BOOT = 10000
SEED = 42

EBSSA_PROPOSED = 'edlr'
DND_TUNED = ['edlr_adaptive', 'ynoise', 'bilateral', 'pfd', 'dwf', 'knoise', 'temporal', 'plr', 'mlpf', 'edncnn']
DND_FREE = ['edlr_adaptive_ebssa', 'ynoise_default', 'ynoise_ebssa', 'ynoise_handoff', 'hybrid_0.1', 'hybrid_0.2']
DND_PAIRS = ([('edlr', k) for k in DND_TUNED]                 # nested-CV proposal minus tuned/supervised method
             + [('zero_knowledge', k) for k in DND_FREE]     # fixed-deployment proposal minus label-free method
             + [('ynoise_handoff', 'ynoise_default'), ('edlr_adaptive', 'edlr')])


def paired_stats(a, b, rng, clusters=None):
    """Summary of d = a - b.  If clusters is given the bootstrap resamples clusters."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    n = len(d)
    if clusters is None:
        idx_sets = [np.array([i]) for i in range(n)]
    else:
        clusters = np.asarray(clusters)
        idx_sets = [np.flatnonzero(clusters == c) for c in np.unique(clusters)]
    boot = np.empty(N_BOOT)
    for i in range(N_BOOT):
        pick = rng.integers(0, len(idx_sets), len(idx_sets))
        boot[i] = np.concatenate([d[idx_sets[j]] for j in pick]).mean()
    lo, hi = np.percentile(boot, [2.5, 97.5])
    nz = d[d != 0]
    if len(nz) >= 5 and not np.all(nz == nz[0]):
        p = float(wilcoxon(a, b).pvalue)
    else:
        p = float('nan')
    # matched-pairs rank-biserial correlation: (W+ - W-) / (W+ + W-)
    ranks = np.argsort(np.argsort(np.abs(nz))) + 1.0
    w_pos = ranks[nz > 0].sum()
    w_neg = ranks[nz < 0].sum()
    rb = float((w_pos - w_neg) / (w_pos + w_neg)) if (w_pos + w_neg) > 0 else 0.0
    return {'n': int(n), 'mean_diff': float(d.mean()), 'median_diff': float(np.median(d)),
            'ci95': [float(lo), float(hi)], 'n_a_better': int((d > 0).sum()), 'n_ties': int((d == 0).sum()),
            'rank_biserial': rb, 'p_wilcoxon': p, 'n_clusters': len(idx_sets)}


def ebssa():
    recs = json.load(open(RESULTS / 'sp_per_recording.json'))
    rng = np.random.default_rng(SEED)
    keys = sorted(recs[0]['metrics'])
    out = {}
    for k in keys:
        if k == EBSSA_PROPOSED:
            continue
        a = [r['metrics'][EBSSA_PROPOSED]['auc'] for r in recs]
        b = [r['metrics'][k]['auc'] for r in recs]
        out[k] = paired_stats(a, b, rng)
    return {'proposed': EBSSA_PROPOSED, 'unit': 'recording', 'n': len(recs), 'vs': out}


def dnd21():
    recs = json.load(open(RESULTS / 'dnd21_per_recording.json'))
    rng = np.random.default_rng(SEED)
    seg_id = [f"{r['source']}_s{int(round(r['segment_start_s'] * 1e3))}" for r in recs]
    segs = sorted(set(seg_id))
    srcs = sorted({r['source'] for r in recs})

    def per_seg(k):
        return [np.mean([r['metrics'][k]['auc'] for r, s in zip(recs, seg_id) if s == seg]) for seg in segs]

    def per_src(k):
        return {src: float(np.mean([r['metrics'][k]['auc'] for r in recs if r['source'] == src])) for src in srcs}

    out = {}
    for a_key, b_key in DND_PAIRS:
        a = [r['metrics'][a_key]['auc'] for r in recs]
        b = [r['metrics'][b_key]['auc'] for r in recs]
        mix = paired_stats(a, b, rng, clusters=seg_id)
        seg = paired_stats(per_seg(a_key), per_seg(b_key), rng)
        sa, sb = per_src(a_key), per_src(b_key)
        src = {s: sa[s] - sb[s] for s in srcs}
        out[f'{a_key}_vs_{b_key}'] = {
            'a': a_key, 'b': b_key,
            'mixture_level': mix,          # 80 mixtures; CI is a cluster bootstrap over segments
            'segment_level': seg,          # 20 segments (mean over noise conditions)
            'source_level': {'diff_by_source': src, 'n_sources_a_better': int(sum(v > 0 for v in src.values())),
                             'n_sources': len(srcs)},
        }
    return {'unit_primary': 'mixture', 'n_mixtures': len(recs), 'n_segments': len(segs), 'n_sources': len(srcs),
            'segments_per_source': {s: sum(1 for g in segs if g.startswith(s + '_s')) for s in srcs},
            'conditions_per_segment': int(len(recs) / len(segs)), 'pairs': out}


def main():
    res = {'n_boot': N_BOOT, 'seed': SEED, 'ci': 'percentile bootstrap, 95%',
           'effect_size': 'matched-pairs rank-biserial correlation',
           'ebssa': ebssa(), 'dnd21': dnd21()}
    out = RESULTS / 'pr_effect_sizes.json'
    json.dump(res, open(out, 'w'), indent=1)
    e = res['ebssa']['vs']
    d = res['dnd21']['pairs']
    print(f'wrote {out}')
    for k in ('ynoise', 'bilateral', 'edncnn', 'plr'):
        v = e[k]
        print(f"EBSSA edlr - {k}: {v['mean_diff']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}] rb={v['rank_biserial']:+.2f}")
    for k, v in d.items():
        m, s = v['mixture_level'], v['segment_level']
        print(f"DND21 {k}: mix {m['mean_diff']:+.3f} [{m['ci95'][0]:+.3f}, {m['ci95'][1]:+.3f}] p={m['p_wilcoxon']:.3g}; "
              f"seg p={s['p_wilcoxon']:.3g} ({s['n_a_better']}/{s['n']}); sources {v['source_level']['n_sources_a_better']}/4")


if __name__ == '__main__':
    main()
