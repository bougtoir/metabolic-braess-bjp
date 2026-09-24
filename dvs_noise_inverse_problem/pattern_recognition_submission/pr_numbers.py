"""Numbers quoted in the Pattern Recognition manuscript, all read from results/*.json.

Extends jatis_submission/manuscript_numbers.py (EBSSA analyses) with the DND21
cross-dataset evaluation (results/dnd21_evaluation_summary.json,
results/dnd21_per_recording.json) and the comparator feasibility table
(results/comparator_feasibility.json).  No estimate, sample size or statistic
is written literally in the document generators.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
RESULTS = PROJECT / 'results'
sys.path.insert(0, str(PROJECT))
import dnd21_evaluation as dnd
import sp_evaluation as sp

_spec = importlib.util.spec_from_file_location('jatis_numbers', PROJECT / 'jatis_submission' / 'manuscript_numbers.py')
_jn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_jn)
auc, auc_sd, fmt, pct, scaling = _jn.auc, _jn.auc_sd, _jn.fmt, _jn.pct, _jn.scaling
_load_ebssa = _jn.load_numbers


def _load(name):
    with open(RESULTS / name) as f:
        return json.load(f)


def load_numbers():
    N = _load_ebssa()
    d = _load('dnd21_evaluation_summary.json')
    recs = _load('dnd21_per_recording.json')
    feas = _load('comparator_feasibility.json')
    es = _load('pr_effect_sizes.json')
    aed = _load('aednet_transfer.json')
    sig = np.array([r['signal_fraction'] for r in recs])
    win = np.array([r['window_us'] for r in recs])
    dur = np.array([r['duration_s'] for r in recs])
    n_ev = np.array([r['n_events'] for r in recs])
    conds = [c['label'] for c in d['noise_conditions'] if f"noise_{c['label']}" in d['strata']]
    N.update({
        'dnd': d,
        'dnd_recs': recs,
        'dnd_methods': d['methods'],
        'dnd_tests_tuned': d['paired_tests_vs_proposed_tuned'],
        'dnd_tests_free': d['paired_tests_vs_zero_knowledge'],
        'dnd_strata': d['strata'],
        'dnd_n_rec': d['n_recordings'],
        'dnd_n_sources': d['n_signal_sources'],
        'dnd_sources': d['signal_sources'],
        'dnd_conditions': conds,
        'dnd_rates_hz': list(dnd.NOISE_RATES_HZ),
        'dnd_segment_s': dnd.SEGMENT_S,
        'dnd_n_segments': dnd.N_SEGMENTS,
        'dnd_target_events': dnd.TARGET_EVENTS,
        'dnd_screen_fractions': list(dnd.SCREEN_FRACTIONS),
        'dnd_shape': tuple(d['sensor_shape']),
        'ebssa_h5_mirror': sp.EBSSA_H5_MIRROR, 'ebssa_h5_bytes': sp.EBSSA_H5_BYTES,
        'ebssa_h5_sha256': sp.EBSSA_H5_SHA256,
        'dnd_sig_min': float(sig.min()), 'dnd_sig_max': float(sig.max()),
        'dnd_sig_median': float(np.median(sig)),
        'dnd_dur_min': float(dur.min()), 'dnd_dur_max': float(dur.max()),
        'dnd_events_min': int(n_ev.min()), 'dnd_events_max': int(n_ev.max()),
        'dnd_events_total': int(n_ev.sum()),
        'dnd_window_ms': {**{k: v / 1e3 for k, v in d['window_us'].items() if k != 'n'},
                          'median': float(np.median(win) / 1e3), 'min': float(win.min() / 1e3),
                          'max': float(win.max() / 1e3)},
        'dnd_transfer_cfg': d['ebssa_transfer_configs'],
        'dnd_noise_source_rate': {r['condition']: r['noise_source_rate_hz'] for r in recs},
        'dnd_pfd_grid': d['hyperparameter_grids']['pfd'] if 'hyperparameter_grids' in d else None,
        'es': es,
        'es_ebssa': es['ebssa']['vs'],
        'es_dnd': es['dnd21']['pairs'],
        'es_n_boot': es['n_boot'],
        'dnd_n_segment_clusters': es['dnd21']['n_segments'],
        'feas_methods': feas['methods'],
        'feas_datasets': feas['datasets'],
        'n_methods_executed': sum(1 for m in feas['methods'] if m['executed_here'].startswith('yes')),
        'aednet': aed,
        'aednet_dnd': aed['dnd21']['summary'],
        'aednet_dnd_recs': aed['dnd21']['per_recording'],
        'aednet_parity': aed['official_parity'],
        'aednet_ebssa': aed['ebssa']['summary'],
        'aednet_ebssa_recs': aed['ebssa']['per_recording'],
    })
    assert N['aednet_dnd']['n_recordings'] == d['n_recordings'], 'AEDNet transfer must cover every DND21 mixture'
    assert N['aednet_ebssa']['n_recordings'] == N['n_rec'], 'AEDNet transfer must cover every EBSSA recording'
    assert {r['index'] for r in N['aednet_ebssa_recs']} == {r['idx'] for r in _load('sp_per_recording.json')}, \
        'AEDNet EBSSA transfer must use the same recordings as the main analysis'
    return N


def dauc(N, key, nd=3):
    return fmt(N['dnd_methods'][key]['mean'], nd)


def dauc_sd(N, key, nd=3):
    a = N['dnd_methods'][key]
    return f"{fmt(a['mean'], nd)} \u00b1 {fmt(a['std'], nd)}"


def pfmt(p):
    return f'= {p:.3f}' if p >= 0.001 else '< 0.001'
