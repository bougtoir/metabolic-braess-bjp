# ECOMEGA_MECHANISM_REPORT

## Does the data support env→prey→predator, vs env→prey + env→predator?

**This is the first sentence of the scientific conclusion:**
The observed predator redistribution is better explained by independent
tracking of environmental forcing (Type A: env→prey + env→predator) than by
trophic propagation through an intermediate prey field (Type B). The data are
**compatible with common-environment tracking** and do not support a detectable
krill-mediated propagation channel at the ACCESS survey scale.

## Setup
- Matched units (zooplankton tows ↔ predator sightings ≤24 h/≤10 km): 1726
  units, 73 ACCESS cruises 2004–2024; 1702 with all covariates. Krill
  non-detection coded as 0 (ACCESS records all taxa per tow); bird and mammal
  layers matched on their own time/coords.
- Prey layer: krill (Euphausia pacifica + Thysanoessa spinifera + Euphausiidae).
- Forcing: Bakun upwelling index 39N125W (wind-derived; independent of biology).
- Model comparison (Type A vs Type B) and mediation are in
  outputs/tables/typeA_typeB_model_comparison.csv and mediation_results.csv.

## Headline estimates
| estimate | value | note |
|---|---|---|
| E→P (M0, env only) | +0.0027 log(birds/km²) per m³/s·100m, p=0.0002 | positive, significant |
| E→K (env→prey) | −0.0003, p=0.57 | ~null |
| K→P|E (prey→predator) | +0.0150, p=0.60 | ~null |
| indirect E→K→P | ≈ −5e−6 [−1e−4, +7e−5] | ~zero |
| attenuation E→P after prey | none (E coef unchanged) | consistent with Type A |
| holdout corr A vs B | 0.368 vs 0.356 (event split); 0.115 vs 0.119 (cruise) | env-only equal or better |

## Temporal ordering
- E→P lag curve peaks at lag ≈2d (positive but small); E→K ~flat; E→Z
  small positive around 10d; K→P within-cruise-lagged at 6d (n small).
- No ordering consistent with a clean env→prey→predator delay cascade.

## Placebos and reverse-time
- Temporal placebos: UWI shifted −60d/−30d/+30d → small/null; +60d gives
  *significant negative* (−0.00093, p=0.016) — consistent with seasonal
  autocorrelation carrying the forward signal, so the +0.0025 E→P should be
  read as a modest real correlation, not a large effect.
- Trophic placebo (future prey +7d → P): significant positive — a spatial
  artifact of within-cruise day-matching (adjacent-day tows cluster
  spatially); interpretation flagged, not used against forward estimates.
- Reverse-time E(+7d)→P: null (p=0.39), supporting correct direction.

## LOEO stability
- E→P: leave-one-cruise-out range 0.0020–0.0028, 0 sign reversals — stable.
- E→K: −0.0012–−0.0004, 0 reversals — stable ~zero.
- K→P|E: +0.005–+0.029, 0 reversals — stable ~zero.

## Spatial propagation
Only 1 event has ≥5 units inside + outside windows under the strict
onset definition; centroid-shift comparison is uninformative — the survey
box is too small for strong foot-print claims.

## Species heterogeneity / mobility
- 12 species' env-response coefficients are all ~zero except Black-footed
  Albatross (p=0.013); log-mobility and trophic-level predictors of response
  magnitude are non-significant (mobility p=0.16, trophic p=0.15, n=11).
- No mobility gradient evidence — consistent with weak overall predator signal.

## Largest validity threats
1. Tow-to-sighting spatial matching (10 km) may decouple prey-predator linkage
   even when it exists — prey patches are sub-mesoscale.
2. ACCESS cruises are intermittent (3–4 cruises/season): only 7 upwelling
   events have full matched trophic coverage; Type B propagation may be
   invisible at this cadence.
3. UWI is a regional index at 39N125W; local wind heterogeneity isn't captured.
4. Seasonal confounding: +60d temporal placebo is significant, so part of the
   E→P association may reflect shared seasonality rather than pulse response.

## Classification
**COMMON-ENVIRONMENT DOMINATED** (see NATURE_ROUTE_GATE.md).

## Reproducibility
scripts/01_download.py … 07_spatial_figs.py run in order; all values in this
report are regenerated from outputs/tables/. No hand-edited numbers.
