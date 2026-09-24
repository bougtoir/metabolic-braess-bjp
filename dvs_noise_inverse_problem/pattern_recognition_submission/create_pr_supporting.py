#!/usr/bin/env python3
"""Supporting files for the Pattern Recognition submission.

Runs the manuscript builder (create_pr_docx.build) so that the figure/table
registry and the numbers are the ones actually placed in the manuscript, then
writes:

  highlights.docx                 3-5 bullets, <= 85 characters each (Elsevier rule)
  title_page.docx                 title, author placeholders, corresponding author, word counts
  cover_letter.docx
  figure_legends.docx             all figure captions (for Editorial Manager upload)
  tables_editable.docx            every table as an editable Word table (Table Grid style)
  figures_tables_editable.pptx    one figure or table per slide, English, editable
  data_and_code_statement.md      data sources, access procedure, code, checksums
  REPRODUCIBILITY.md              one-command rebuild instructions, environment, checksums
  comparator_feasibility.md       Supplementary Table S1 as Markdown
  supplementary_material.docx     written by create_pr_docx.build (Tables S1-S6)

reviewer_report.md (hand-written, not generated) records the reviewer-perspective
findings by priority and how each was addressed.

No number is written literally here: everything comes from create_pr_docx.N
(results/*.json) or from the registry of the built manuscript.
"""

import hashlib
import json
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from docx import Document
from docx.shared import Pt
from PIL import Image
from pptx import Presentation
from pptx.util import Inches as PInches
from pptx.util import Pt as PPt

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
import create_pr_docx as pr

N = pr.N


def _doc(spacing=1.5):
    doc = Document()
    st = doc.styles['Normal']
    st.font.name = 'Times New Roman'
    st.font.size = Pt(pr.BODY_PT)
    st.paragraph_format.line_spacing = spacing
    return doc


def highlights():
    hand_frac = N['hyb']['ynoise_full']['handoff']['auc']['mean'] / N['hyb']['ynoise_cv_reference']['auc_mean']
    items = [
        'Per-pixel Poisson tail test as self-calibrating unsupervised anomaly detection',
        f'False-alarm budget met without labels on {N["n_rec"]} EBSSA recordings, two sensors',
        f'Window as expected count transfers across sensors; ms window loses up to {pr.zk_max_drop("edlr"):.2f} AUC',
        f'Label-free hand-over gives YNoise {pr.pct(hand_frac, 1)} of its label-tuned accuracy',
        f'DND21 ({N["dnd_n_rec"]} exact-label mixtures) bounds the method to sparse-transient scenes',
    ]
    for it in items:
        assert len(it) <= 85, f'highlight too long ({len(it)}): {it}'
    doc = _doc(1.0)
    doc.add_paragraph('Highlights').runs[0].bold = True
    doc.add_paragraph(pr.TITLE)
    for it in items:
        doc.add_paragraph(it, style='List Bullet')
    doc.save(HERE / 'highlights.docx')
    return items


def title_page(n_words_body):
    doc = _doc(1.0)
    p = doc.add_paragraph()
    r = p.add_run(pr.TITLE)
    r.bold = True
    r.font.size = Pt(pr.TITLE_PT)
    for line in (pr.AUTHOR, pr.AFFILIATION,
                 f'Corresponding author: {pr.AUTHOR}, {pr.AFFILIATION}, {pr.ADDRESS}; '
                 f'telephone: {pr.PHONE}; e-mail: {pr.EMAIL}'):
        doc.add_paragraph().add_run(line).font.size = Pt(pr.AUTHOR_PT)
    doc.add_paragraph('')
    doc.add_paragraph(f'Manuscript type: Regular paper. Word count (Abstract to Conclusion, excluding '
                      f'captions, tables and references): {n_words_body:,}. '
                      f'Figures: {len(pr.FIGURES)}. Tables: {len(pr.TABLES)}. '
                      f'Supplementary material: {len(pr.SUPP_FIGURES)} figures, {len(pr.SUPP_TABLES)} tables. '
                      f'References: {len(pr.jd.CITE_ORDER)}.')
    doc.add_paragraph('Prior presentation: none. Preprint: none.')
    doc.add_paragraph('Declarations of interest: none.')
    doc.add_paragraph('Funding: none.')
    doc.save(HERE / 'title_page.docx')


def cover_letter():
    hand_frac = N['hyb']['ynoise_full']['handoff']['auc']['mean'] / N['hyb']['ynoise_cv_reference']['auc_mean']
    doc = _doc(1.15)
    doc.add_paragraph('[Date]')
    doc.add_paragraph('Editor-in-Chief\nPattern Recognition\nElsevier')
    doc.add_paragraph('Dear Editor,')
    doc.add_paragraph(
        f'I submit for consideration as a regular paper the manuscript entitled "{pr.TITLE}".')
    ae, ad = N['aednet_ebssa'], N['aednet_dnd']
    m = N['methods']
    n_unsup = sum(1 for k in m if not m[k]['supervised'] and not k.startswith('edlr'))
    doc.add_paragraph(
        'The paper addresses an unsupervised anomaly-detection problem on sparse, asynchronous event streams: '
        'separating a few structured events from a per-pixel Poisson background whose rate must be learned from '
        'the stream itself. Its argument runs in three steps. First, the detector on its own, with no prior '
        'knowledge of the stream: an event-driven Poisson likelihood-ratio test whose output is a calibrated '
        'probability, so that a stated false-alarm budget is met without labels. On all '
        f'{N["n_rec"]} labelled recordings of the public EBSSA dataset (two sensor models), against '
        f'{n_unsup} unsupervised comparators with grouped cross-validated tuning, two supervised networks '
        'and a released supervised denoiser (AEDNet) applied unchanged, the untuned detector reaches a mean '
        f'ROC-AUC of {pr.auc(N, "edlr")}, below the best label-tuned filter ({pr.auc(N, "ynoise")}) and the '
        f'supervised networks, and above the released network ({pr.fmt(ae["aednet_mean_auc"])}). Second, the '
        'detector as a source of parameters: because its window is stated as an expected background count it '
        'transfers between sensor models where a window in milliseconds does not, and handed to the heuristic '
        f'filter YNoise as its time constant it recovers {pr.pct(hand_frac, 1)} of the accuracy that filter '
        'otherwise needs labelled tuning to reach; a screen-then-confirm cascade improves on both. The point is '
        'general: the fixed constants of event filters encode a scale chosen by the designer for one sensor, and '
        'replacing that scale with one the stream itself supplies is what makes the setting portable. Third, the '
        'regime in which either helps: on an independent public benchmark recorded with a third sensor (DND21, '
        f'{N["dnd_n_rec"]} mixtures with exact origin labels), dominated by dense scenes close to the training '
        f'distribution of the released network, the detector reaches only {pr.dauc(N, "zero_knowledge")} against '
        f'{pr.dauc(N, "ynoise_default")} for the default filter and {pr.fmt(ad["aednet_mean_auc"])} for AEDNet, '
        'and the hand-over helps only on the sparse scenes. I report this negative result in full and use it to '
        'bound the method: a label-free calibrator and parameter source for sparse, transient streams, not a '
        'general event denoiser. I believe this framing, and the explicit statement of where an unsupervised '
        'parametric model does and does not help, is of interest to the pattern-recognition community beyond '
        'event cameras.')
    doc.add_paragraph(
        'Fit to Pattern Recognition: the manuscript proposes and evaluates an unsupervised detection method with '
        'an explicit statistical model, a calibration procedure and a cross-dataset generalisation study, and it '
        'documents the feasibility of recent learning-based comparators under a common protocol. The Discussion '
        'states where we would and would not use the method (label-free commissioning of a new sensor, faint '
        'moving sources such as resident space objects, a first setting for an existing filter; not dense or '
        'dwelling scenes).')
    doc.add_paragraph(
        'The manuscript has not been published and is not under consideration by any other journal.')
    doc.add_paragraph(
        'All analysis and manuscript-generation code, the result files from which every number, table and figure '
        'is generated, and a one-command build are provided in the repository named in the Data availability '
        'statement, together with a statement of which result files re-run end-to-end from the public data. I am the sole author and have '
        'no competing interests to declare.')
    doc.add_paragraph('Suggested reviewers: [to be completed by the author].')
    doc.add_paragraph('Yours sincerely,')
    doc.add_paragraph(f'{pr.AUTHOR}\n{pr.AFFILIATION}\n{pr.EMAIL}')
    doc.save(HERE / 'cover_letter.docx')


def figure_legends():
    doc = _doc(1.5)
    doc.add_paragraph('Figure legends').runs[0].bold = True
    for f in pr.FIGURES:
        doc.add_paragraph(f['caption'])
    if pr.SUPP_FIGURES:
        doc.add_paragraph('Supplementary figures').runs[0].bold = True
        for f in pr.SUPP_FIGURES:
            doc.add_paragraph(f['caption'])
    doc.add_paragraph('Graphical abstract. Label-free path of the proposed detector on the two datasets: the '
                      'per-pixel rate estimate fixes the window and the threshold, the window is handed to '
                      'YNoise, and the achieved ROC-AUC is compared with the label-tuned reference.')
    doc.save(HERE / 'figure_legends.docx')


def tables_editable():
    doc = _doc(1.0)
    doc.add_paragraph('Tables (editable)').runs[0].bold = True
    for t in pr.TABLES + pr.SUPP_TABLES:
        p = doc.add_paragraph(t['caption'])
        p.paragraph_format.space_before = Pt(14)
        p.runs[0].font.size = Pt(10)
        tbl = doc.add_table(rows=1, cols=len(t['headers']))
        tbl.style = 'Table Grid'
        for c, h in zip(tbl.rows[0].cells, t['headers']):
            c.text = str(h)
            for r in c.paragraphs[0].runs:
                r.bold = True
                r.font.size = Pt(8)
        for row in t['rows']:
            cells = tbl.add_row().cells
            for c, v in zip(cells, row):
                c.text = str(v)
                for r in c.paragraphs[0].runs:
                    r.font.size = Pt(8)
    doc.save(HERE / 'tables_editable.docx')


def pptx():
    prs = Presentation()
    prs.slide_width, prs.slide_height = PInches(13.333), PInches(7.5)
    blank = prs.slide_layouts[6]

    def add_title(slide, text):
        tb = slide.shapes.add_textbox(PInches(0.4), PInches(0.2), PInches(12.5), PInches(0.6))
        tf = tb.text_frame
        tf.text = text
        tf.paragraphs[0].runs[0].font.size = PPt(22)
        tf.paragraphs[0].runs[0].font.bold = True

    def add_caption(slide, text, top):
        tb = slide.shapes.add_textbox(PInches(0.4), PInches(top), PInches(12.5), PInches(7.3 - top))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.text = text
        for p in tf.paragraphs:
            for r in p.runs:
                r.font.size = PPt(11)

    for f in pr.FIGURES + pr.SUPP_FIGURES + [{'file': 'graphical_abstract.png',
                            'caption': 'Graphical abstract. Label-free path of the proposed detector on EBSSA and DND21.'}]:
        s = prs.slides.add_slide(blank)
        title = f['caption'].split('. ')[0] if f['caption'].startswith('Fig') else 'Graphical abstract'
        add_title(s, title)
        img = HERE / f['file']
        w, h = Image.open(img).size
        max_w, max_h = 12.5, 5.0
        scale = min(max_w / w, max_h / h)
        dw, dh = w * scale, h * scale
        s.shapes.add_picture(str(img), PInches((13.333 - dw) / 2), PInches(0.9), PInches(dw), PInches(dh))
        add_caption(s, f['caption'], 0.9 + dh + 0.1)

    for t in pr.TABLES + pr.SUPP_TABLES:
        s = prs.slides.add_slide(blank)
        add_title(s, t['caption'].split('. ')[0])
        n_rows, n_cols = len(t['rows']) + 1, len(t['headers'])
        row_h = min(0.35, 5.2 / n_rows)
        shape = s.shapes.add_table(n_rows, n_cols, PInches(0.4), PInches(0.9), PInches(12.5),
                                   PInches(row_h * n_rows))
        tbl = shape.table
        fs = PPt(9 if n_rows < 14 else 7)
        for j, h in enumerate(t['headers']):
            cell = tbl.cell(0, j)
            cell.text = str(h)
            for p in cell.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = fs
                    r.font.bold = True
        for i, row in enumerate(t['rows'], start=1):
            for j, v in enumerate(row):
                cell = tbl.cell(i, j)
                cell.text = str(v)
                for p in cell.text_frame.paragraphs:
                    for r in p.runs:
                        r.font.size = fs
        add_caption(s, t['caption'], 0.9 + row_h * n_rows + 0.15)
    prs.save(HERE / 'figures_tables_editable.pptx')


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


RESULT_FILES = ['sp_evaluation_summary.json', 'sp_per_recording.json', 'sparsity_cost.json',
                'partial_auc.json', 'self_calibration.json', 'zero_knowledge.json', 'hybrid_screening.json',
                'qualitative_example.json', 'dnd21_evaluation_summary.json', 'dnd21_per_recording.json',
                'comparator_feasibility.json', 'pr_effect_sizes.json', 'aednet_transfer.json']
PRODUCER = {'sp_evaluation_summary.json': 'sp_evaluation.py', 'sp_per_recording.json': 'sp_evaluation.py',
            'sparsity_cost.json': 'sparsity_cost.py', 'partial_auc.json': 'operating_points.py',
            'self_calibration.json': 'operating_points.py', 'zero_knowledge.json': 'zero_knowledge.py',
            'hybrid_screening.json': 'hybrid_screening.py', 'qualitative_example.json': 'qualitative_example.py',
            'dnd21_evaluation_summary.json': 'dnd21_evaluation.py', 'dnd21_per_recording.json': 'dnd21_evaluation.py',
            'comparator_feasibility.json': 'comparator_feasibility.py', 'pr_effect_sizes.json': 'pr_effect_sizes.py',
            'aednet_transfer.json': 'aednet_transfer.py'}
EBSSA_FILES = {f for f, s in PRODUCER.items()
               if s in {'sp_evaluation.py', 'sparsity_cost.py', 'operating_points.py', 'zero_knowledge.py',
                        'hybrid_screening.py', 'qualitative_example.py'}}


def _provenance():
    """Scripts that build_pr_submission.py actually ran in this build (empty when run stand-alone)."""
    p = PROJECT / 'results' / 'build_provenance.json'
    if not p.exists():
        return {'rerun_scripts': [], 'derived_scripts': []}
    return json.loads(p.read_text())


def file_status(f):
    prov = _provenance()
    s = PRODUCER[f]
    if s in prov['rerun_scripts']:
        return 're-run in this build'
    if s in prov['derived_scripts']:
        return 'derived in this build from the tracked result files'
    return 'tracked output (not re-derived in this build)'
PACKAGES = ['numpy', 'scipy', 'numba', 'torch', 'scikit-learn', 'matplotlib', 'python-docx', 'python-pptx',
            'tonic', 'gdown', 'pillow']


def _versions():
    out = {'python': platform.python_version(), 'platform': platform.platform()}
    for p in PACKAGES:
        try:
            out[p] = version(p)
        except PackageNotFoundError:
            out[p] = 'not installed'
    return out


def checksums():
    results = PROJECT / 'results'
    return {f: (_sha(results / f) if (results / f).exists() else None) for f in RESULT_FILES}


def data_statement():
    lines = ['# Data and code statement', '',
             '## Data sources (all public; no data were created or modified)', '',
             f'* **EBSSA** (Afshar et al., 2020): labelled split, {N["n_rec"]} recordings from a 180 x 240 and a '
             '240 x 304-pixel sensor. Accessed through `tonic.datasets.EBSSA` (Tonic 1.6.0), which downloads '
             '`labelled_ebssa.h5` from the authors\' Google Drive release. Ground truth: published object '
             'annotations (10 x 10-pixel box, 10 ms). The Drive file is subject to Google download '
             'quotas; the same file is served by the authors\' institutional mirror as '
             f'`{N["ebssa_h5_mirror"]}` ({N["ebssa_h5_bytes"]:,} bytes, SHA-256 `{N["ebssa_h5_sha256"]}`, '
             'constants `EBSSA_H5_*` in `sp_evaluation.py`); save it as '
             '`data/EBSSA/labelled_ebssa.h5` and Tonic uses it without downloading.',
             '* **DND21** (Guo and Delbruck, 2022): public AEDAT-2.0 recordings from the DND21 Drive folder '
             '(ids listed in `dnd21_evaluation.py:FILES`), DAVIS346 (346 x 260 px). Mixtures are constructed by '
             '`dnd21_evaluation.build_recordings()` from a signal recording and a *distinct* slice of a measured '
             'noise recording; labels are the exact origin of each event. These are synthetic combinations of '
             'two real recordings and are described as such in the manuscript.', '',
             '## Result files (inputs of every number in the manuscript)', '',
             'Status is read from `results/build_provenance.json`, written by `build_pr_submission.py`: '
             '*re-run in this build* = the producing analysis script was executed in the build that wrote this '
             'statement; *derived in this build* = recomputed from the tracked result files; *tracked output* = '
             'shipped as committed and checked by checksum only. Every file is produced by the released code; the '
             'clean-clone scope of each analysis is stated under "Data access".', '']
    for f, h in checksums().items():
        lines.append(f'* `results/{f}` ({file_status(f)}) sha256 = `{h}`' if h else f'* `results/{f}` (missing)')
    lines += ['', '## Code', '',
              '* `event_driven.py` proposed detector; `sp_evaluation.py` EBSSA framework and comparators; '
              '`dnd21_evaluation.py` DND21 protocol; `aedat2.py` AEDAT-2.0 reader; '
              '`comparator_feasibility.py` Supplementary Table S1 metadata; `pr_effect_sizes.py` effect sizes, bootstrap CIs and '
              'the DND21 segment/source-level sensitivity analysis (results/pr_effect_sizes.json); '
              '`aednet_transfer.py` zero-shot CPU transfer of the released AEDNet weights to EBSSA and DND21 '
              '(clones github.com/Fanghuachen/AEDNet at a pinned commit, downloads the release weights and '
              'checks their SHA-256, checks parity with the official loader/model on the released sample, '
              'then scores every EBSSA recording and DND21 mixture; results/aednet_transfer.json).',
              '* `pattern_recognition_submission/` manuscript, figure and supporting-file generators '
              '(`make_pr_figures.py`, `create_pr_docx.py`, `create_pr_supporting.py`; driven by '
              '`../build_pr_submission.py`).', '',
              '## Data access', '',
              '* The EBSSA Google Drive file that Tonic downloads is subject to Google download quotas ("Too many '
              'users have viewed or downloaded this file recently" was returned during this revision); the '
              'institutional mirror above serves the same file and its SHA-256 is recorded in `sp_evaluation.py`. '
              f'The EBSSA result files in `results/` ({", ".join(sorted(EBSSA_FILES))}) are shipped with their '
              'checksums; whether they were re-derived in the build that wrote this statement is given by their '
              'status above. The tracked `sp_evaluation_summary.json` and `sp_per_recording.json` were written by '
              '`sp_evaluation.py` run on the mirror file (SHA-256 above); every metric matched the earlier '
              'Drive-sourced run to floating-point precision, only wall-clock timings differed. The DND21 '
              'analysis downloads its public AEDAT files directly and re-runs end-to-end with `--full`.', '',
              '## Public mirror', '',
              '* The manuscript names `https://github.com/bougtoir/dvs-noise-inverse-pattern-recognition` as the '
              'release repository. It is populated by the `sync-to-repos` workflow of the development repository; '
              'the clean-clone check in REPRODUCIBILITY.md must be repeated on that mirror before submission '
              '(see reviewer_report.md, item R1).']
    (HERE / 'data_and_code_statement.md').write_text('\n'.join(lines) + '\n')


def reproducibility():
    txt = f"""# Reproducibility

One command regenerates every figure, table and number of the Pattern Recognition manuscript:

```bash
pip install -r requirements.txt            # numpy, scipy, numba, torch, scikit-learn, matplotlib, python-docx, python-pptx, tonic, gdown, pillow
python3 sp_evaluation.py                   # EBSSA: uses data/EBSSA/labelled_ebssa.h5 (Tonic download, or the mirror named in the data statement), writes results/sp_*.json  (hours)
python3 sparsity_cost.py && python3 operating_points.py && python3 zero_knowledge.py && python3 hybrid_screening.py && python3 qualitative_example.py
python3 dnd21_evaluation.py                # DND21: downloads the public AEDAT files, writes results/dnd21_*.json (~1 h)
python3 comparator_feasibility.py          # results/comparator_feasibility.json
python3 pr_effect_sizes.py                 # results/pr_effect_sizes.json (bootstrap CIs, rank-biserial r, DND21 segment/source analysis)
python3 aednet_transfer.py --dataset ebssa && python3 aednet_transfer.py --dataset dnd21 && python3 aednet_transfer.py --summarise   # results/aednet_transfer.json (CPU, ~40 min; needs git + network for the AEDNet code and weights)
python3 build_pr_submission.py             # figures, manuscript, supplementary file, supporting files, zip (documents only)
```

Equivalently `python3 build_pr_submission.py [--full]` runs the whole chain (the `--full` flag reruns the
analyses; without it only the documents are rebuilt from the tracked `results/*.json`).

Fixed seed {N["seed"]}; sensor-specific constants and grids are in `sp_evaluation.py` and `dnd21_evaluation.py`.
`dnd21_evaluation.py` is resumable: a cache under `results/sp_cache/` is keyed by a fingerprint of every protocol constant
and is discarded automatically when a constant changes.

Tests: `python3 -m pytest tests/ -q` (AEDAT-2.0 decoding, timestamp rollover/reset, PFD ranking).

AEDNet: the official inference script is CUDA-only; `aednet_transfer.py` re-implements its patch construction
and runs the released `ResAEDNet` weights on the CPU. `results/aednet_transfer.json` records the pinned commit,
the weights checksum, the parity check against the official loader and model, every adaptation from the
published protocol, and the PyTorch version used. It is a transfer test of a fixed model, not a reproduction
of the published training or evaluation.

## Environment used for this package

{chr(10).join(f'* {k}: `{v}`' for k, v in _versions().items())}

## Result-file checksums (SHA-256)

The re-run/derived/tracked status of each file in the build that wrote this document is listed in
data_and_code_statement.md (from `results/build_provenance.json`). A clean-clone rebuild of the documents must
reproduce the manuscript text from exactly these files.

{chr(10).join(f'* `results/{f}` `{h}`' for f, h in checksums().items() if h)}

## Clean-clone check

```bash
git clone <repository> check && cd check
pip install -r requirements.txt
python3 build_pr_submission.py            # documents only, from the tracked results/*.json
python3 -m pytest tests/ -q
```

The manuscript text produced in `check/` must be identical to the shipped `manuscript_pattern_recognition.docx`
(compare paragraph text with python-docx). This check has been run on the development repository; it must be
repeated on the public mirror named in the Data availability statement once the mirror is populated.

Outputs of `build_pr_submission.py` (in `pattern_recognition_submission/`):
`manuscript_pattern_recognition.docx` (inline figures/tables; Times New Roman 10 pt, captions 8 pt, 1.5 line
spacing, A4 with 4.3/4.8/4.3/4.8 cm margins, numbered lines and pages), `supplementary_material.docx` (Figs. S1-S2, Tables S1-S7), `highlights.docx`, `title_page.docx`, `cover_letter.docx`,
`figure_legends.docx`, `tables_editable.docx`, `figures_tables_editable.pptx`, `fig*.png`/`fig*.tiff` (300 dpi),
`graphical_abstract.png`, `data_and_code_statement.md`, `comparator_feasibility.md`,
`pattern_recognition_submission.zip`. `reviewer_report.md` (not in the zip) lists the pre-submission review findings.

"""
    (HERE / 'REPRODUCIBILITY.md').write_text(txt)


def feasibility_md():
    t = pr.SUPP_TABLES[0]
    lines = ['# ' + t['caption'], '', '| ' + ' | '.join(t['headers']) + ' |',
             '|' + '---|' * len(t['headers'])]
    for row in t['rows']:
        lines.append('| ' + ' | '.join(str(v) for v in row) + ' |')
    lines += ['', 'Caveats (from results/comparator_feasibility.json):', '']
    for m in N['feas_methods']:
        lines.append(f"* **{m['name']}**: {m['caveat']}")
    lines += ['', 'Datasets considered:', '']
    for d in N['feas_datasets']:
        lines.append(f"* **{d['name']}** ({d['reference']}): labels: {d['labels']}; ROC feasible: "
                     f"{d['roc_feasible']}; executed here: {d['executed_here']}")
    (HERE / 'comparator_feasibility.md').write_text('\n'.join(lines) + '\n')


def body_word_count(docx_path):
    doc = Document(docx_path)
    words, on = 0, False
    for p in doc.paragraphs:
        t = p.text.strip()
        if t == 'Abstract':
            on = True
        if t.startswith('CRediT'):
            break
        if on and not (t.startswith('Fig. ') or t.startswith('Table ')):
            words += len(t.split())
    return words


def main():
    out = pr.build()
    n_words = body_word_count(out)
    items = highlights()
    title_page(n_words)
    cover_letter()
    figure_legends()
    tables_editable()
    pptx()
    data_statement()
    reproducibility()
    feasibility_md()
    json.dump({'body_words': n_words, 'n_figures': len(pr.FIGURES), 'n_tables': len(pr.TABLES),
               'n_supp_figures': len(pr.SUPP_FIGURES), 'n_supp_tables': len(pr.SUPP_TABLES),
               'n_references': len(pr.jd.CITE_ORDER), 'highlights': items,
               'result_checksums_sha256': checksums(), 'environment': _versions()},
              open(HERE / 'package_manifest.json', 'w'), indent=1)
    print(f'body words {n_words}, figures {len(pr.FIGURES)}, tables {len(pr.TABLES)}, '
          f'supp {len(pr.SUPP_FIGURES)}F/{len(pr.SUPP_TABLES)}T, refs {len(pr.jd.CITE_ORDER)}')


if __name__ == '__main__':
    main()
