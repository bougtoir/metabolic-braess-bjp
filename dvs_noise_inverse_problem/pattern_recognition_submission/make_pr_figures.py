#!/usr/bin/env python3
"""Figures for the Pattern Recognition manuscript (single-column page, larger type).

Figures 3-7 reuse the plotting code of jatis_submission/make_jatis_figures.py
(same result JSON files) with a larger type size enforced for every text
element, as required for a single-column layout printed at the full text
width; Fig. 1 (method), Fig. 2 (label-tuned and label-free AUC), Fig. S2
(qualitative example), Fig. 7 (DND21 cross-dataset evaluation) and the
graphical abstract are defined here.
All text is English.  Outputs: fig*.png (300 dpi) and fig*.tiff (LZW) in this
directory.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
RESULTS = PROJECT / 'results'
sys.path.insert(0, str(PROJECT / 'jatis_submission'))
import make_jatis_figures as jf

MIN_PT = 8.0        # smallest type allowed anywhere in a figure
BASE_PT = 10.0
SCALE = 1.25        # figures are drawn larger and printed at the 6.5-inch text width


def _min_font(kw, key='fontsize', floor=MIN_PT):
    v = kw.get(key)
    if v is None or (isinstance(v, (int, float)) and v < floor):
        kw[key] = floor
    return kw


# Legends of the shared panels that overlap their data at the larger type size are moved
# below the axes (keyed by panel title).
LEGEND_OVERRIDES = {
    '(a) Total cost': {'loc': 'upper left', 'bbox_to_anchor': (0.0, -0.32), 'ncol': 2},
    '(c) Threshold transfer': {'figure': True, 'loc': 'upper center', 'bbox_to_anchor': (0.7, 0.1),
                               'ncol': 3},
}


def _patch():
    """Raise every explicit type size in the shared plotting code to MIN_PT or more."""
    plt.rcParams.update({
        'font.size': BASE_PT, 'axes.titlesize': BASE_PT + 1, 'axes.labelsize': BASE_PT,
        'legend.fontsize': MIN_PT + 1, 'xtick.labelsize': MIN_PT + 1, 'ytick.labelsize': MIN_PT + 1,
    })
    A = matplotlib.axes.Axes
    for name in ('legend', 'set_title', 'set_xlabel', 'set_ylabel', 'text', 'set_xticklabels',
                 'set_yticklabels', 'annotate'):
        orig = getattr(A, name)

        def wrapped(self, *a, _orig=orig, _name=name, **kw):
            _min_font(kw)
            if _name == 'legend':
                _min_font(kw, 'title_fontsize')
                kw.update(LEGEND_OVERRIDES.get(self.get_title(), {}))
                if kw.pop('figure', False):
                    # a figure-level legend is ignored by tight_layout, so the panels keep their size
                    h, l = self.get_legend_handles_labels()
                    return self.figure.legend(h, l, **kw)
            return _orig(self, *a, **kw)
        setattr(A, name, wrapped)
    orig_savefig = matplotlib.figure.Figure.savefig

    def savefig(self, *a, **kw):
        kw.setdefault('bbox_inches', 'tight')
        return orig_savefig(self, *a, **kw)
    matplotlib.figure.Figure.savefig = savefig
    orig_subplots = plt.subplots

    def subplots(*a, **kw):
        if 'figsize' in kw:
            w, h = kw['figsize']
            kw['figsize'] = (w * SCALE, h * SCALE)
        return orig_subplots(*a, **kw)
    plt.subplots = subplots
    jf.plt = plt


def load(name):
    return json.load(open(RESULTS / name))


DND_LABEL = {
    'edlr': 'Proposed, fixed W (nested CV)',
    'edlr_adaptive': 'Proposed, rate-adaptive W (nested CV)',
    'zero_knowledge': 'Proposed, zero-knowledge (no tuning)',
    'edlr_adaptive_ebssa': 'Proposed, EBSSA-selected k',
    'ynoise': 'YNoise (nested CV)',
    'ynoise_ebssa': 'YNoise, EBSSA-selected',
    'ynoise_default': 'YNoise, published default',
    'ynoise_handoff': 'YNoise, dt = W handed over',
    'bilateral': 'Event bilateral (nested CV)',
    'knoise': 'kNoise (nested CV)',
    'dwf': 'DWF (nested CV)',
    'temporal': 'Background-activity filter (nested CV)',
    'pfd': 'PFD-A (nested CV)',
    'plr': 'Voxelised Poisson LR (nested CV)',
    'mlpf': 'MLPF (supervised, leave-one-scene-out)',
    'edncnn': 'EDnCNN-style (supervised, leave-one-scene-out)',
}


def fig1_method(out):
    """Method schematic; the two output boxes state what the detector delivers without labels."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.0)
    ax.axis('off')

    def box(x, y, w, h, text, fc='#f4f6f7', ec='#2c3e50', lw=0.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05', fc=fc, ec=ec, lw=lw))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=6.2, linespacing=1.25)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=9, lw=0.8,
                                     color='#2c3e50'))

    box(0.05, 1.35, 1.45, 1.3, 'Event stream\n$(x_i, y_i, t_i, p_i)$\nsorted by time')
    box(1.95, 2.35, 3.15, 1.3, 'Per-pixel background rate\n$\\hat{\\lambda}_{xy}$ from inter-event\nintervals (quantile)')
    box(1.95, 0.35, 3.15, 1.3, 'Causal count $N_i$: events in\n$(2r+1)^2$ px within the last $W$\n'
                               '$W = k/\\bar{\\Lambda}$, $k$ background events\n(not a fixed number of ms)')
    box(5.5, 1.35, 1.9, 1.3, 'Poisson tail probability\n$P_i = \\Pr(N \\geq N_i \\mid \\Lambda_i)$\n'
                             '$\\Lambda_i = W\\sum_{nbhd}\\hat{\\lambda}$', fc='#fdecea')
    box(7.75, 2.35, 2.2, 1.3, 'Operating point\n$\\alpha$-quantile of $P_i$ on the\n'
                              'stream itself = requested\nfalse-alarm rate, no labels', fc='#eaf2f8', ec='#2980b9')
    box(7.75, 0.35, 2.2, 1.3, 'Window $W$ carries across\nsensor models and sets\nanother filter\'s time constant\n'
                              '$O(\\log n + (2r+1)^2)$ per event', fc='#eaf2f8', ec='#2980b9')
    arrow(1.5, 2.2, 1.95, 2.9)
    arrow(1.5, 1.8, 1.95, 1.1)
    arrow(5.1, 2.9, 5.5, 2.2)
    arrow(5.1, 1.1, 5.5, 1.8)
    arrow(7.4, 2.2, 7.75, 2.9)
    arrow(7.4, 1.8, 7.75, 1.1)
    ax.text(0.775, 1.05, 'input', ha='center', fontsize=6.2, color='#555555')
    ax.text(3.525, 3.8, 'self-calibration from the stream', ha='center', fontsize=6.2, color='#555555')
    ax.text(8.85, 3.8, 'delivered without labels', ha='center', fontsize=6.2, color='#2980b9')
    fig.savefig(out, bbox_inches='tight')
    plt.close(fig)


def fig2_methods(out):
    """Label-tuned AUC (bars) with the label-free fixed-configuration AUC overlaid (open markers)."""
    from matplotlib.lines import Line2D
    d = load('sp_evaluation_summary.json')
    zk = load('zero_knowledge.json')['published_defaults']
    m = d['methods']
    names, means, stds, colours, lf = [], [], [], [], []
    seps = []
    for _, keys, col in jf.GROUPS:
        keys = sorted(keys, key=lambda k: -m[k]['auc']['mean'])
        for k in keys:
            names.append(jf.SHORT[k])
            means.append(m[k]['auc']['mean'])
            stds.append(m[k]['auc']['std'])
            colours.append(col)
            lf.append(zk[k]['auc_mean'] if k in zk else None)
        seps.append(len(names))
    y = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(6.5, 5.6))
    ax.barh(y, means, xerr=stds, color=colours, ecolor='#555555', capsize=2, error_kw={'lw': 0.7})
    for yi, v in zip(y, lf):
        if v is not None:
            ax.plot(v, yi, marker='o', ms=5.5, mfc='white', mec='k', mew=1.0, ls='', zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlim(0.3, 1.0)
    ax.axvline(0.5, color='k', ls=':', lw=0.7)
    ax.axvline(zk['edlr_adaptive']['auc_mean'], color='#c0392b', ls='--', lw=0.8)
    for s in seps[:-1]:
        ax.axhline(s - 0.5, color='#999999', lw=0.5)
    ax.set_xlabel(f"ROC-AUC, mean \u00b1 SD over {d['n_recordings']} EBSSA recordings")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in jf.GROUPS]
    labels = [g for g, _, _ in jf.GROUPS]
    handles.append(plt.Rectangle((0, 0), 1, 1, fc='white', ec='#555555'))
    labels.append('Bars: configuration tuned on labels (grouped CV; supervised: trained)')
    handles.append(Line2D([], [], marker='o', ms=5.5, mfc='white', mec='k', mew=1.0, ls=''))
    labels.append('Open circles: no labels, one fixed configuration (published default)')
    handles.append(Line2D([], [], color='#c0392b', ls='--', lw=0.8))
    labels.append('Proposed, rate-adaptive window, no labels')
    ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.3, -0.08), frameon=False, ncol=1)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def fig8_qualitative(out):
    """Same panels as the shared Fig. S2 with titles short enough for seven columns at MIN_PT."""
    meta = load('qualitative_example.json')
    imgs = np.load(RESULTS / 'qualitative_example.npz')
    f_screen = meta['screen_fraction']
    panels = [('raw', 'All events\n(input)'), ('object', 'Annotated\nobject'),
              ('proposal_zk', 'Proposed,\nno labels'), ('ynoise_default', 'YNoise,\ndefault dt'),
              ('ynoise_handoff', 'YNoise,\ndt = W handed over'),
              ('two_stage', f'Two-stage,\nscreen f = {f_screen:g}'), ('fano', 'Fano factor\n(ablation)')]
    keys = list(meta['recordings'])
    fig, axes = plt.subplots(len(keys), len(panels), figsize=(6.8, 1.35 * len(keys) + 0.5))
    letters = 'abcdefghijklmn'
    for i, key in enumerate(keys):
        m = meta['recordings'][key]
        for j, (name, title) in enumerate(panels):
            ax = axes[i, j]
            img = imgs[f'{key}_{name}'].astype(float)
            ax.imshow(np.log1p(img), cmap='gray_r', interpolation='nearest', aspect='equal')
            ax.set_xticks([])
            ax.set_yticks([])
            lab = f'({letters[i * len(panels) + j]}) {title}'
            if name in m['methods']:
                mm = m['methods'][name]
                lab += f'\nTPR {mm["tpr"]:.2f}\nFPR {mm["fpr"]:.4f}'
            elif name == 'raw':
                lab += f'\n{m["n_events"]} events\n{m["duration_s"]:.1f} s'
            else:
                lab += f'\n{m["n_object"]} events\n'
            ax.set_title(lab, fontsize=MIN_PT, pad=2, linespacing=1.1)
            if j == 0:
                sensor = key.replace('x', ' \u00d7 ')
                ax.set_ylabel(f'{sensor} px\nW = {m["window_ms"]:.0f} ms', fontsize=MIN_PT)
    fig.tight_layout(h_pad=0.4, w_pad=0.2)
    fig.savefig(out)
    plt.close(fig)


def fig9_dnd21(out):
    d = load('dnd21_evaluation_summary.json')
    recs = load('dnd21_per_recording.json')
    m = d['methods']
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.4),
                             gridspec_kw={'width_ratios': [1.25, 1]})

    # (a) mean AUC per method, grouped by how the parameters were obtained
    ax = axes[0]
    groups = [
        ('No labels, no tuning on DND21', ['zero_knowledge', 'ynoise_default', 'ynoise_handoff',
                                           'edlr_adaptive_ebssa', 'ynoise_ebssa'], '#c0392b'),
        ('Tuned on DND21 (nested leave-one-scene-out)', ['edlr', 'edlr_adaptive', 'ynoise', 'bilateral',
                                                          'knoise', 'dwf', 'temporal', 'pfd', 'plr'], '#2c3e50'),
        ('Supervised (trained on the other scenes)', ['mlpf', 'edncnn'], '#2980b9'),
    ]
    hybrid = sorted(k for k in m if k.startswith('hybrid_'))
    groups[0] = (groups[0][0], groups[0][1] + hybrid, groups[0][2])
    names, means, stds, cols, seps = [], [], [], [], []
    for _, keys, col in groups:
        keys = [k for k in keys if k in m]
        for k in keys:
            names.append(DND_LABEL.get(k, k.replace('hybrid_', 'Two-stage, f = ')))
            means.append(m[k]['mean'])
            stds.append(m[k]['std'])
            cols.append(col)
        seps.append(len(names))
    y = np.arange(len(names))
    ax.barh(y, means, xerr=stds, color=cols, ecolor='#555555', capsize=2, error_kw={'lw': 0.7})
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlim(0.4, 1.0)
    ax.axvline(0.5, color='k', ls=':', lw=0.7)
    for s in seps[:-1]:
        ax.axhline(s - 0.5, color='#999999', lw=0.5)
    ax.set_xlabel(f"ROC-AUC, mean \u00b1 SD over {d['n_recordings']} DND21 mixtures")
    ax.set_title('(a) All conditions')
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in groups]
    ax.legend(handles, [g for g, _, _ in groups], loc='upper center', frameon=False,
              bbox_to_anchor=(0.5, -0.18), ncol=1)

    # (b) label-free path against the nominal noise rate, per signal source
    ax = axes[1]
    conds = [c['label'] for c in d['noise_conditions']]
    series = (('zero_knowledge', '#c0392b', '-'), ('ynoise_default', '#bdc3c7', '--'),
              ('ynoise_handoff', '#8e44ad', '-'))
    xt = []
    for ci, cond in enumerate(conds):
        for key, col, ls in series:
            vals = [r['metrics'][key]['auc'] for r in recs if r['condition'] == cond]
            if vals:
                ax.errorbar(ci + {'zero_knowledge': -0.15, 'ynoise_default': 0, 'ynoise_handoff': 0.15}[key],
                            np.mean(vals), yerr=np.std(vals), fmt='o', ms=4, color=col, capsize=2, lw=1)
        xt.append(cond.replace('light_native', 'light\n(native)').replace('dark_', 'dark\n').replace('hz', ' Hz'))
    ax.set_xticks(range(len(conds)))
    ax.set_xticklabels(xt)
    ax.set_xlabel('Measured-noise condition\n(nominal rate per pixel)')
    ax.set_ylabel('ROC-AUC (mean \u00b1 SD over scenes and segments)')
    ax.set_ylim(0.4, 1.02)
    ax.set_title('(b) Label-free path by noise level')
    from matplotlib.lines import Line2D
    ax.legend([Line2D([], [], marker='o', color=c, ls='') for _, c, _ in series],
              ['Proposed, zero-knowledge', 'YNoise, default', 'YNoise, dt = W handed over'],
              frameon=False, loc='lower left')
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def graphical_abstract(out):
    """One-panel summary: label-free path on both datasets (numbers from the JSON files)."""
    e = load('sp_evaluation_summary.json')
    h = load('hybrid_screening.json')
    d = load('dnd21_evaluation_summary.json')
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    labels = ['Proposed\n(zero-knowledge,\nno labels)', 'YNoise\n(published\ndefault)',
              'YNoise\n(dt = W handed\nover, no labels)', 'YNoise\n(label-tuned CV)']
    ebssa = [h['stage1']['auc']['mean'], h['ynoise_full']['default']['auc']['mean'],
             h['ynoise_full']['handoff']['auc']['mean'], e['methods']['ynoise']['auc']['mean']]
    dnd = [d['methods']['zero_knowledge']['mean'], d['methods']['ynoise_default']['mean'],
           d['methods']['ynoise_handoff']['mean'], d['methods']['ynoise']['mean']]
    x = np.arange(4)
    w = 0.36
    b1 = ax.bar(x - w / 2, ebssa, w, color='#c0392b', label=f"EBSSA, {e['n_recordings']} sky recordings (2 sensors)")
    b2 = ax.bar(x + w / 2, dnd, w, color='#2980b9', label=f"DND21, {d['n_recordings']} mixtures (3rd sensor)")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.005, f'{b.get_height():.2f}',
                    ha='center', va='bottom', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0.5, 1.0)
    ax.set_ylabel('Mean ROC-AUC', fontsize=11)
    ax.set_title('Self-calibrating anomaly detection for sparse event streams:\n'
                 'the per-pixel Poisson test needs no labels and hands its window W to a heuristic filter',
                 fontsize=11)
    ax.legend(frameon=False, fontsize=10, loc='upper left')
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


def to_tiff(png):
    with Image.open(png) as im:
        im.save(png.with_suffix('.tiff'), compression='tiff_lzw', dpi=im.info.get('dpi', (300, 300)))


def main():
    _patch()
    figs = [
        ('fig1_method.png', fig1_method),
        ('fig2_methods_auc.png', fig2_methods),
        ('fig3_paired.png', jf.fig3_paired),
        ('fig4_sparsity_cost.png', jf.fig4_sparsity),
        ('fig5_calibration.png', jf.fig5_calibration),
        ('fig6_zero_knowledge.png', jf.fig6_zero_knowledge),
        ('fig7_hybrid.png', jf.fig7_hybrid),
        ('fig8_qualitative.png', fig8_qualitative),
        ('fig9_dnd21.png', fig9_dnd21),
        ('graphical_abstract.png', graphical_abstract),
    ]
    for name, fn in figs:
        out = HERE / name
        fn(out)
        to_tiff(out)
        print('wrote', out.name)


if __name__ == '__main__':
    main()
