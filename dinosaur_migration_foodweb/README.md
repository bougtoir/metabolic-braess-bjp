# Migration sustained dinosaur food webs

Tests whether Late Jurassic (Morrison Formation) dinosaur food webs were
spatially coupled by seasonal movement of large herbivorous dinosaurs, and
whether migratory prey bias fossil predator/prey ratios.

Full analysis plan: see `ANALYSIS_PLAN.md`. Data sources and provenance:
`DATA_SOURCES.md` and `metadata/sources.csv`.

## Reproduce

```bash
pip install -r requirements.txt
python3 src/download/fetch_data.py   # Dryad download requires Chrome via CDP
make stage1                         # data audit -> beta diversity -> sensitivity
```

## Repository layout

```
data/{raw,interim,processed}   datasets (raw never overwritten; sha256 logged)
metadata/                      sources.csv, taxonomy_reconciliation.csv
src/download/                  data acquisition with provenance
analysis/                      numbered pipeline scripts (01-06 = Stage 1)
results/{tables,models,diagnostics}
figures/{main,extended_data}
manuscript/
tests/
```

## Stage 1 status

See `STATUS.md` and `results/stage1_report.md`.
