# ANALYTIC_MULTIVERSE_LOG — ecomega trophic propagation

## PRIMARY choices
- Matched unit: zooplankton tow anchored, predators within 24 h / 10 km.
  Grid tested: 6 h/5 km, 12 h/10 km, 24 h/10 km, 48 h/20 km.
- Environmental forcing: Bakun upwelling index (39N 125W), + SST anomaly as
  covariate. Events = 7-day-mean UWI above Apr–Oct 75th percentile, onset
  requires ≥3 consecutive days below median; separation rule 7 days
  (3d and 14d run as sensitivity).
- Response transforms: log1p(density) for krill/zoop (count_per_m3), birds
  (count_per_km2), whales (count_per_km).
- Models: OLS with month + year fixed effects; cruise-level cluster-robust
  SEs (cruise = ACCESS sampling cruise, >4-day date gaps).
- Mediation bootstrap: resample cruises (500 draws), NOT row-level.
- Cross-validation: leave-one-event-out AND leave-one-cruise-out; no row splits.

## SENSITIVITY variants
- Prey layer definition: krill only vs all-zooplankton (M2b: K→Z substitution).
- Separations 3d/7d/14d for event counting.
- Multispecies density vs top-4 krill-feeder density.
- Whale density alternative outcome (n=780 matched units).

## EXPLORATORY
- K→P lag grid 0–14d via within-cruise day-matched prey exposure.
- Species-level environmental-response coefficients regressed on mobility
  + trophic level.

## Decisions and justification
- Chose krill over "all zooplankton" as PRIMARY prey: euphausiids are the
  canonical seabird/whale prey in this system and give a cleaner Layer-2 test.
- Did NOT merge CTD chl into matched units: per-station sparse coverage;
  used as supporting env only.
- UWI chosen over SST as primary forcing: wind-derived, exogenous to biology;
  SST used as covariate.
- Did NOT attempt movement-based propagation metrics: ACCESS records are
  densities (aggregation responses), not tracks.
