# Modern marine variable map

| Core metric | Existing analogue | Source | Status |
|---|---|---|---|
| M1 trophic turnover contrast | indirect — env→prey and prey→predator path coefficients (ecomega M1/M2 mediation); not a spatial Δβ | `ecomega_trophic_propagation` | translated: export path contrasts; spatial Δβ missing → NA |
| M2 spatial response | centroid displacement, spatial figures | ecomega `07_spatial_figs.py`, palmyra `04_spatial.py` | direct |
| M3 distance decay | centroid displacement vs distance; connectivity implicit | ecomega/palmyra | translated |
| M4 temporal lag | native — lag curves, placebos, reverse-time (ecomega `05_lag_placebo.py`, topp `05_lag_modes.py`) | ecomega/topp | direct: `temporal_lag` = predator lag − prey/env lag |
| M5 sampling-pool | matched-unit sensitivity, LOEO, species/mobility robustness | ecomega `06_robustness_species.py` | translated |
| M6 time-aggregation | event separation windows 3/7/14 d | ecomega `03_events_env.py` | translated (window sensitivity) |
| M7 nulls | placebos + reverse-time + capelin positive control | ecomega, capelin | direct |
| M8 observation bias | tow-matching, sensor/survey structure, detection process documented per project docs | ecomega/topp/palmyra | partial — formal `observation_bias_score` pending final system selection |
| M9 robustness | NATURE_ROUTE_GATE verdicts | ecomega docs | map: ecomega = context-dependent/Type-A result |
