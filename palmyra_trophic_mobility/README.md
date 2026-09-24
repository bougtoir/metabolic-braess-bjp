# Palmyra trophic mobility — feasibility & data audit

Feasibility assessment of whether the publicly available **Palmyra Bluewater
Research Marine Animal Telemetry Dataset, 2022–2023**
(DOI: [10.24431/rw1k8ez](https://doi.org/10.24431/rw1k8ez), US public domain;
related paper: Gilmour et al. 2025, GCB, doi:10.1111/gcb.70138) supports a
rigorous event-based test of perturbation propagation through a multi-trophic
telemetry network.

This is an audit, not a result: no hypothesis is tested confirmatorily and no
manuscript is produced.

## Layout

- `data/raw/` — not committed. `scripts/download_data.py` fetches all 88
  archive members with MD5 verification (manifest: `metadata/dataone_manifest.json`).
- `data/processed/` — derived tables (tracks.csv, tracks_qc.csv, individual_day,
  species_day, env_daily); regenerable.
- `metadata/` — dataset inventory, environmental product list, guild table.
- `scripts/` — numbered pipeline 01–07.
- `outputs/tables`, `outputs/figures` — audit artefacts.
- `docs/` — DATA_AUDIT.md, FEASIBILITY.md (Q1–Q10 + GO/WEAK GO/NO-GO),
  ANALYSIS_PLAN_DRAFT.md.

## Reproduce

```bash
pip install -r requirements.txt
python3 scripts/download_data.py     # ~350 MB, MD5-checked, extracts zips to data/raw/extracted/
python3 scripts/01_ingest_tracks.py
python3 scripts/02_species_overlap.py
python3 scripts/03_qc.py
python3 scripts/04_spatial.py
python3 scripts/05_environment.py    # NOAA ERDDAP downloads, chunked curl
python3 scripts/06_events.py
python3 scripts/07_models.py
```

or `make all`.
