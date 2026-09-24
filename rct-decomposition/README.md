# KOTHA Framework — Reproducible Manuscript Pipeline

This repository contains the empirical validation, figures, and manuscript-generation pipeline for the KOTHA (Knowledge-driven Observational-Trial Harmonization Approach) Framework manuscript.

## Dependencies

- Python 3.x with `emcee`, `python-docx`, `python-pptx`, `numpy`, `pandas`, `scipy`, `matplotlib`, and `lxml`
- [pandoc](https://pandoc.org/) (the build script searches `~/.local/pandoc/bin/pandoc` and the system `PATH`)

## One-command builds

```bash
make all              # run validation and generate the RSM-target manuscript
make clinical_trials  # generate the Clinical Trials submission package
make jbs              # generate the Journal of Biopharmaceutical Statistics submission package
```

`make clinical_trials` reuses the pre-computed CCTC outputs and produces:
`05_paper_clinical_trials.md`, `KOTHA_Framework_ClinicalTrials.docx`, `KOTHA_Framework_ClinicalTrials_tables.docx`, `KOTHA_Framework_ClinicalTrials_figures.pptx`, `KOTHA_Framework_ClinicalTrials_supplementary_figures.pptx`, `KOTHA_Framework_ClinicalTrials_supplementary_tables.docx`, `cover_letter_ClinicalTrials.docx`, and `submission_package_ClinicalTrials.zip`.

`make jbs` reuses the pre-computed CCTC outputs and produces:
`05_paper_jbs.md`, `KOTHA_Framework_JBS.docx` (inline figures/tables), `KOTHA_Framework_JBS_submission.docx` (legends only, for separate figure upload), `KOTHA_Framework_JBS_tables.docx`, `KOTHA_Framework_JBS_figures.pptx`, `KOTHA_Framework_JBS_supplementary_figures.pptx`, `KOTHA_Framework_JBS_supplementary_tables.docx`, `cover_letter_JBS.docx`, `JBS_figures/` high-resolution PNGs, and `submission_package_JBS.zip`.

## Pipeline steps

1. **Data** — `data/magnesium_ami.csv`, `data/statins_hf_obs.csv`, and `data/statins_hf_rct.csv` contain the study-level inputs and are documented in `data/SOURCES.md`.
2. **Analysis** — `validation/run_validation.py` reads the CSVs and produces:
   - `validation/figures/*.png` (eight figures)
   - `validation/results_summary.txt` (numerical summary)
3. **Manuscript** — `build_paper.py` reads `paper_template.md`, injects the computed results, tables, and figures, and writes `04_paper_rsm.md`. `build_paper_cct.py` writes `05_paper_cctc.md`, and `build_paper_clinical_trials.py` restructures it for *Clinical Trials*.
4. **DOCX / PPTX** — `generate_cct_docx.py` converts the markdown into `KOTHA_Framework_ClinicalTrials.docx` with inline figures, tables, and Sage Vancouver superscript citations.

## Reproducibility principle

No study-level counts, effect estimates, or summary statistics are hard-coded in the manuscript source. All numbers in `04_paper_rsm.md`, `05_paper_cctc.md`, `05_paper_clinical_trials.md`, `05_paper_jbs.md`, and the generated Word documents are produced by `build_paper.py` / `build_paper_cct.py` / `build_paper_clinical_trials.py` / `build_paper_jbs.py` from the CSVs and the analysis code. Edit `paper_template.md` for prose; rerun `make all`, `make clinical_trials`, or `make jbs` to refresh all numbers, tables, figures, and supplementary files.
