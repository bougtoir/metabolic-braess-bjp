# Modern terrestrial variable map (phase8b / phase9 / geb → Core Protocol)

| Core metric | Existing analogue | Source | Status |
|---|---|---|---|
| M1 trophic turnover contrast | none natively — BBS pipeline is not guild-structured | — | **missing**: minimal add = re-run route-year incidence split into a defensible forage-vs-raptor guild pair (see below) |
| M2 spatial response | route occupancy extent per species | phase8b/9 species panels | direct |
| M3 distance decay | spatial autocorrelation is characterized as persistent route heterogeneity rather than decay-vs-distance | phase9 `species_hg.py`, `matched.py` | translated: report spatial-persistence (route-demeaned vs raw history-gain contrast) under `distance_decay_effect` with scale note |
| M4 temporal lag | native — lagged-state predictability, lag-1 history terms, LOYO vs forward | phase9 tables | direct: `temporal_lag` = abundance prior-state effect; hysteresis = 0 |
| M5 sampling-pool | prevalence-inclusion (116 widespread species), surveyed-panel occupancy controls | phase9 `audit_fix.py` | translated |
| M6 time-aggregation | annual resolution only; coarsening = secondary | — | NA primary |
| M7 nulls | placebo / reverse-time, simulation `sim9.py`/`sim_fp.py`, matched-environment contrast=0 | phase8b/9 | direct |
| M8 observation bias | observer continuity, detectability, survey effort, spatial autocorrelation documented; observer-persistence control identified as pending | `geb/docs/GEB_GAP_AUDIT.md` | partial — pending control |
| M9 robustness | verdict language (WEAK GO / falsified) | `phase9/docs` | map to C (context-dependent) for hysteresis-falsified occupancy; B/A for abundance state dependence |

## Minimal additional analyses needed for M1

Reusing the committed BBS pipeline outputs, add `analysis/` step computing
route-level genus/species incidence turnover between a lower-guild
(granivore/herbivore-passerine grouping per guild table) and higher-guild
(raptors/corvid predators). Must be run on the same routes/years and use the
same Δβ estimand (Simpson, route bootstrap). If the guild structure is not
defensible in BBS, export `NA` with justification — do not force it.
