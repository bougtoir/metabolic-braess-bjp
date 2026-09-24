# ecomega_trophic_propagation

Task 4: Distinguishing common environmental tracking (Type A) from trophic
propagation (Type B) in the California Current ecomega system, using ACCESS
(Applied California Current Ecosystem Studies) matched survey data.

Chain tested: environment (upwelling) → krill/zooplankton → seabirds/whales.

## Pipeline
```
python3 scripts/01_download.py      # WFS ACCESS layers + ERDDAP forcing
python3 scripts/02_build_units.py   # tow-anchored matched units + sensitivity
python3 scripts/03_events_env.py    # upwelling events (3/7/14d separation)
python3 scripts/04_models.py        # M0/M1/M2 + mediation + TypeA/B + holdout
python3 scripts/05_lag_placebo.py   # lag curves + placebos + reverse-time
python3 scripts/06_robustness_species.py  # LOEO + species/mobility
python3 scripts/07_spatial_figs.py  # centroid displacement + figures
```
Raw data (~120 MB) are not committed; download_data step is reproducible.

## Headline verdict
COMMON-ENVIRONMENT DOMINATED — env→predator significant, env→prey and
prey→predator null, no attenuation, env-only wins event-holdout CV.
See docs/NATURE_ROUTE_GATE.md.
