# Phase-8B Analysis Plan — Ecological Spatial Memory Across Ecosystems

## Systems
- **A (individual GPS)**: Banff/Ya Ha Tinda elk (Movebank, 175 indiv, 2001–2020; ≥24 tracked months → 54 retained). Bathurst caribou was unavailable (Movebank permission-gated); elk used as the individual-level substitute. Banff wolf (19 indiv, median 7 tracked months) attempted but too sparse — reported only descriptively.
- **B (population)**: NOAA FOSS bottom-trawl CPUE, station × year panel, 6 prespecified groundfish (walleye pollock, Pacific cod, yellowfin sole, northern rock sole, arrowtooth flounder, Pacific halibut), 1982–2024.
- **C (population)**: BBS route × year totals for the 10 most prevalent species (top route-year occupancy), 1997–2024, June climate per route (NASA POWER T2M + PRECTOTCORR).
- **Supplementary**: NEON small-mammal box trapping DP1.10072.001 (site × month), monthly resolution — added opportunistically when NEON access was granted.

## Definitions (frozen from spec §3–4)
- HG = OOS(M3 env+history) − OOS(M1 env); EG = OOS(M3) − OOS(M2 history).
- Model hierarchy M0 static / M1 env / M2 history / M3 env+history / M4 extended memory / M5 lagged env / M6 full.
- Validation: leave-one-year-out; outcomes unit-demeaned (station / indiv×cell / route) to absorb static geography (M0 baseline).

## Env covariates
- FOSS: bottom temp, surface temp, depth per station-year.
- BBS: June T2M + precip per route-year (NASA POWER).
- Elk: monthly temp/precip/snowfall (ERA5/Open-Meteo daily→monthly) shared across cells; cell-level EVI/snow unavailable past 2011 — limitation noted.
- NEON: monthly T2M + precip per site (NASA POWER).

## Falsification battery
- Temporally blocked CV (LOYO); no random splits.
- History vs lagged env: M5 (lagged env, no history) vs M6.
- Static geography: unit-demeaned residuals; M0 baseline.
- Observation persistence: env-only simulation with AR(1) measurement noise on the real coverage mask; report P(HG>0) and P(HG>0.05) plus simulated HG magnitudes (`simulation_false_positive.csv`).
- Matched-environment path dependence: outcomes at near-identical env compared across prior-year state (matched_env CSVs).
- Env-shift redistribution: post-shift CPUE/usage changes on pre-registered |anomaly|>1sd years (shift_lag CSVs).
- Memory decay: OOS R2 at lags 1/2/3/5(+12) bins (memory_decay CSVs).

## GO criteria (spec §final)
STRONG GO: HG>0 in ≥2 systems incl. one GPS-individual + one population, surviving static/season/lagged-env/observation-persistence controls, matched-env path dependence, measurable redistribution lag. History that reduces to static geography, lagged env, or observation autocorrelation → NO-GO.

## Terminology (spec §38)
"Distributional inertia"/"history dependence" for population data; "route fidelity"/"individual spatial memory" only if GPS evidence justifies; "hysteresis" only with matched-env evidence.
