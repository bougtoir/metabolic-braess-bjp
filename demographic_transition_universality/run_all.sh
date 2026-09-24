#!/usr/bin/env bash
# One-command reproduction of every result, figure and the manuscript.
# Usage: bash run_all.sh
# Requires: python3 with the packages in requirements.txt. Sub-national fetch (s06) needs
# network access and, for US crude birth rates, a free CENSUS_API_KEY environment variable.
set -euo pipefail
cd "$(dirname "$0")/scripts"

python3 s02_reproduce_baseline.py        # pooled calendar segmentation (baseline)
python3 s03_transition_onset.py          # country-specific transition onsets
python3 s04_event_alignment.py           # calendar vs event-time collapse & conserved-quantity CV
python3 s05_changepoint_uncertainty.py   # bootstrap / posterior of the single change year
python3 s06_subnational.py               # sub-national (Eurostat, US, HMD) heterogeneity
python3 s10_sensitivity.py               # robustness to onset tuning
python3 s11_time_rescaling.py            # time-axis rescaling (duration normalisation) test
python3 s07_figures.py                   # figures (PNG + SVG)
python3 s08_pptx.py                      # editable English PPTX of the figures
python3 s09_manuscript.py                # EHS Perspective manuscript (docx)
python3 s09_commentary.py                # EHS Commentary manuscript (docx)
echo "Done. See results/, figs/ and manuscript/."
