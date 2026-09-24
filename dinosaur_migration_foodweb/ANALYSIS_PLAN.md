# Analysis plan

Nature-target framing: herbivore migration as *mobile energetic infrastructure*
coupling spatially separated predator communities. Central testable claim:

> Large herbivore migration may have repeatedly subsidised multiple predator
> populations, so fossil predator/prey ratios reflect time-integrated
> projections of moving populations, not instantaneous local ratios.

## Hypotheses

- **H1 spatial continuity**: predator communities turn over geographically
  faster than herbivore communities: Delta-beta(d) = beta_P(d) - beta_H(d) > 0.
  (Preferred over raw range-size comparisons, which genus-level ubiquity of
  e.g. *Allosaurus* can mask.)
- **H2 mobile biomass reuse**: spatial reuse factor SRF > 1 for migratory
  populations; fossil occupancy over-represents instantaneous biomass.
- **H3 fossil-ratio distortion**: H_fossil inflated relative to
  H_instantaneous; corrected predator/prey ratio
  R_corrected = P_fossil / (H_fossil / SRF).

## Stage gates (do not skip)

1. Morrison data: is Delta-beta > 0 supported after sampling correction?
   If strongly contradicted, reassess the central story.
2. Modern GPS artificial-fossilization: does prey migration meaningfully bias
   apparent predator/prey ratios?
3. SRF estimation + fossil ratio correction.
4. Dynamic food-web simulation (movement vs residency worlds, TRF /
   predator persistence).
5. Remote-collapse network analysis (seasonal-range centrality).

## Stage 1 implementation (this repo, `analysis/`)

| Script | Task |
|---|---|
| 01_data_audit.py | N collections/occurrences/taxa, resolution, missingness, coverage |
| 02_occurrence_cleaning.py | guild assignment (Sauropoda+Ornithischia=herbivore, Theropoda=predator), genus-level incidence, collection table, taxonomy reconciliation |
| 03_taxonomy.py | per-guild genus lists, resolution summary |
| 04_spatial_occupancy.py | grid occupancy at 0.5/1/2 deg; genus max ranges |
| 05_beta_diversity.py | incidence matrices, pairwise haversine distances, Simpson & Sorensen beta(d) curves, Delta-beta + bootstrap CI, Mantel tests, Figure 2 |
| 06_sampling_bias.py | dominant-quarry exclusion, singleton exclusion, equalized collections, 1-degree spatial thinning |

Metrics: Simpson turnover (primary; richness-insensitive) and Sorensen
(alternative-metric sensitivity). Bootstrap over collections (999 reps);
Mantel tests with 9999 permutations; fixed seeds in each script.

## Falsification criteria

Weaken/reject the core hypothesis if predator turnover is not greater than
herbivore turnover, if modern artificial fossilization shows negligible bias,
if residency models match movement models, if SRF ~ 1, or if results vanish
after sampling correction. Negative findings are documented, not rescued.

## Later stages (not yet implemented)

07 modern GPS validation (Movebank), 08 artificial fossilization,
09 SRF estimator, 10 ratio correction, 11 energetics, 12 movement simulation,
13 food-web persistence, 14 remote collapse, 15 global sensitivity.
