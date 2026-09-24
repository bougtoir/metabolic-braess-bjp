# Reproducibility report

Environment: cobrapy + GLPK; see environment used in repo blueprint.

Deterministic rebuild:
  python3 scripts/run_qc.py                     # Phase 1: model QC + sha256
  python3 -m pytest tests/                       # Phase 2: module tests (12)
  python3 scripts/pilot_scan.py                 # Phase 3
  python3 scripts/full_scan.py human2           # Phase 4 (hours)
  python3 scripts/full_scan.py recon3d
  python3 scripts/classify_scan.py              # Phase 5
  python3 scripts/robustness_scan.py            # Phase 6 (hours)
  python3 scripts/make_figures.py               # Phase 8: figs + manuscript_values.csv
  python3 scripts/make_fig1.py; python3 scripts/make_fig5.py
  python3 scripts/make_tables.py                # tables 1 & 4

Provenance: models SHA-256 frozen (data/raw/acquisition_ledger.csv).
Traceability: every manuscript number maps to a row of
manuscript/manuscript_values.csv regenerated from results/scans/*.csv.
Known nondeterminism: none observed; LP optima with alternate optima are
resolved by deterministic solver defaults; u* values are grid points.
