# Capelin–seabird positive control

Positive-control / mechanism-validation analysis: does the same event-based
framework used on Palmyra telemetry recover a *known* ecological response —
seabird aggregation following the annual capelin spawning pulse in coastal
Newfoundland?

Dataset: Davoren et al. 2024, J Anim Ecol (doi:10.1111/1365-2656.14214),
data on Dryad doi:10.5061/dryad.jq2bvq8k8 (CC0).

## Reproduce

```bash
pip install pandas openpyxl matplotlib statsmodels numpy
python3 scripts/download_data.py   # see note: Dryad uses Anubis; browser download may be required
python3 scripts/01_load.py         # SHA-256 verified
python3 scripts/02_events.py
python3 scripts/03_robustness.py
python3 scripts/04_figures.py
```

or `make all`.

## Verdict

WEAK POSITIVE CONTROL — see docs/CAPELIN_FEASIBILITY.md.
