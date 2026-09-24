# Reproducibility

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

Fixed seed 42; sensor-specific constants and grids are in `sp_evaluation.py` and `dnd21_evaluation.py`.
`dnd21_evaluation.py` is resumable: a cache under `results/sp_cache/` is keyed by a fingerprint of every protocol constant
and is discarded automatically when a constant changes.

Tests: `python3 -m pytest tests/ -q` (AEDAT-2.0 decoding, timestamp rollover/reset, PFD ranking).

AEDNet: the official inference script is CUDA-only; `aednet_transfer.py` re-implements its patch construction
and runs the released `ResAEDNet` weights on the CPU. `results/aednet_transfer.json` records the pinned commit,
the weights checksum, the parity check against the official loader and model, every adaptation from the
published protocol, and the PyTorch version used. It is a transfer test of a fixed model, not a reproduction
of the published training or evaluation.

## Environment used for this package

* python: `3.10.12`
* platform: `Linux-6.8.0-1061-aws-x86_64-with-glibc2.35`
* numpy: `1.26.4`
* scipy: `1.14.1`
* numba: `0.67.0`
* torch: `2.13.0+cpu`
* scikit-learn: `1.6.0`
* matplotlib: `3.10.0`
* python-docx: `1.2.0`
* python-pptx: `1.0.2`
* tonic: `1.6.0`
* gdown: `6.2.0`
* pillow: `11.0.0`

## Result-file checksums (SHA-256)

The re-run/derived/tracked status of each file in the build that wrote this document is listed in
data_and_code_statement.md (from `results/build_provenance.json`). A clean-clone rebuild of the documents must
reproduce the manuscript text from exactly these files.

* `results/sp_evaluation_summary.json` `4f839ff6d1c2016c71069c1610360adabe5899257a5f6cd2f98b5cc97911859c`
* `results/sp_per_recording.json` `5cbe231317af7b6058315706b8b999bc573a838fa65047eb4b54011ec51fdcbe`
* `results/sparsity_cost.json` `cfded7c002ca6fd23877a385351a934c7a202beb120390525862ed6abb695484`
* `results/partial_auc.json` `e8bf4f53ac1cc9ebb558d3a12d5552303246db9742f90e3f16a9a8caaf100222`
* `results/self_calibration.json` `e0459477ed5dfa5fd1b2fb5b689ec8060b9b1fd4c3442fea8baadc96e225192b`
* `results/zero_knowledge.json` `74003aa3b210a9a4c85e49f6948938c4242dc51b609c0ddb9c3534fc340c3a46`
* `results/hybrid_screening.json` `e3125ef51a03cbebf033cb636f411646729ec342525462a5906f5d660a924545`
* `results/qualitative_example.json` `d883ead11e317ca5b64890965443f49a580a134ce13d62c0713f1a98d0514b54`
* `results/dnd21_evaluation_summary.json` `8048d536185a64ce4229a216fb65ce7208870f40ea01e15c7b86e6034649250f`
* `results/dnd21_per_recording.json` `020dcc4b2e23759aef717f0a3d93365a2b86b6ab77dc7998b77bb5541bdcea15`
* `results/comparator_feasibility.json` `f6a2c1fd5b2fc45d452b1cb9ecb56335f9ff95d690b33dfc8bc94a016ad1b620`
* `results/pr_effect_sizes.json` `f9273986f6045861f9d8652a66d993db60e8509b887617486dff6653086949bb`
* `results/aednet_transfer.json` `c3bff81addbd34cbbc308a29668d31beff8695e5a2cd7ceeb73c4d7337bcec60`

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

