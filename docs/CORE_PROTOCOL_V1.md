# Core Protocol v1 — cross-system ecological comparison

Defines the shared conceptual interface for the six-system migration /
trophic-coupling program.

**Relationship to the frozen `CORE_PROTOCOL_v1` (docx, 2026-09-21).** A
frozen, program-wide falsification protocol already exists
(`docs/reference/CORE_PROTOCOL_v1.docx`): its fixed items F1–F7 (primary
contrast, effect direction, sampling-pool, time-aggregation,
distance-decay/static-spatial control, negative control, robustness labels),
variable items V1–V5, and process rules (pre-registration, GO/NO-GO,
forward-chaining primary inference, train-only preprocessing, no spec
changes to rescue conclusions, branch-per-phase) are **process rules this
document inherits unchanged** — a study here is "on-protocol" only if it
also satisfies the docx items where they apply. This document adds the
*ecological-metric* layer (the trophic/spatial quantities to measure) that
the docx deliberately leaves as variable content. Robustness labels map:
docx `ROBUST`→A, `WEAK`→B, `NULL`→C/D (context-dependent vs failed),
`UNSUPPORTED`→D; both label sets are exported (`robustness_class` uses the
A–D set, `notes` may carry the docx label).
 The core protocol fixes **what is measured**, not
**how the raw data are processed**. System adapters (see `protocols/<system>/`)
translate each system's observation model onto this interface.

Two harmonization tiers are defined:

- **Tier 1 — STRICT REPLICATION** (dinosaur, cenozoic_mammals, quaternary):
  implement the same estimand, metrics, sampling corrections, and null
  structure as the dinosaur reference. Deviations only where data force them,
  each logged in `PROTOCOL_DEVIATIONS.md`.
- **Tier 2 — ECOLOGICAL TRANSLATION** (ancient_marine, modern_terrestrial,
  modern_marine): may use different observation/sampling models but must
  export the same standardized summary metrics into
  `results/common_metrics/common_metrics_<system>.csv`.
- **Tier 3 — SYNTHESIS**: consumes only standardized exports; never pools
  native metrics.

## Fixed vs variable items (必ず共通にする項目 / 系ごとに変更可能な項目)

**FIXED — identical across all six systems, non-negotiable:**

| Fixed item | Definition |
|---|---|
| Primary contrast | lower-trophic / resource-tracking component vs higher-trophic / consumer-predator component |
| Effect direction convention | `lower>higher`, `lower<higher`, or `no detectable contrast` on every exported row |
| Sampling-pool test | every system must report effect under restricted pool − effect under reference pool |
| Time-aggregation test | every system must report effect at coarse temporal resolution − effect at fine temporal resolution (NA only if scientifically impossible, with justification) |
| Distance-decay test | a dissimilarity-vs-distance (or mapped equivalent) estimate per guild plus a contrast |
| Negative control / null | at least one preregistered-style null or positive control per system |
| Robustness classification | the shared A/B/C/D classes (§M9); heterogeneous-but-reproducible results are C, never D |

**VARIABLE — system-specific, must be declared in the adapter:**

| Variable item | Declared in |
|---|---|
| Database / data source | `config.yaml` + `OBSERVATION_MODEL.md` |
| Spatial unit | `config.yaml` `spatial_unit` |
| Temporal resolution / bin width | `config.yaml` `temporal_unit` |
| Observation-process corrections | `OBSERVATION_MODEL.md` |
| Guild definition detail (which taxa are lower/higher) | `config.yaml` + `VARIABLE_MAP.md` |
| Raw data structure, preservation model, covariates | `OBSERVATION_MODEL.md` |

An adapter may change HOW a fixed item is measured but may never drop it
silently — an inapplicable metric is exported as `NA` with written
justification, and every change is logged in `PROTOCOL_DEVIATIONS.md`.

## The mandatory shared comparison

Every system must separate **BIOLOGICAL SIGNAL** from **OBSERVATION
PROCESS**, and must estimate the directional contrast

> lower-trophic / resource-tracking component
> vs
> higher-trophic / consumer-or-predator component

on the metrics below. `effect_direction` is always reported as
`lower>higher`, `lower<higher`, or `no detectable contrast`.

## Core metrics

Each metric lists: meaning · required inputs · preferred implementation ·
allowable alternative · direction · normalization · exported variable(s).
Exported variable names appear in `metric` column values of the common
schema (`results/common_metrics/schema.yaml`).

### M1. Trophic spatial-turnover contrast (Δβ)
- **Meaning**: do higher-trophic assemblages turn over in space faster than
  lower-trophic assemblages? Sign tests the core hypothesis that consumers
  are more spatially persistent (Δβ<0) or more spatially structured (Δβ>0).
- **Inputs**: guild × spatial-unit incidence matrix; pairwise distances.
- **Preferred**: Δβ = mean pairwise Simpson turnover(predator) − (herbivore),
  genus incidence per collection; bootstrap CIs (collections resampled with
  replacement, n=999).
- **Alternatives**: Sorensen/Jaccard dissimilarity (sensitivity, report
  alongside); occupancy turnover on survey routes (modern); assemblage
  turnover among palaeogeographic units (marine fossil).
- **Direction**: positive = higher trophic turns over faster.
- **Normalization**: dissimilarity is already unit-free [0,1]; report native
  Δβ plus `standardized_effect` = Δβ / pooled SD of within-guild β.
- **Exports**: `delta_beta_simpson`, `delta_beta_sorensen`, CIs, p(Δ>0).

### M2. Spatial response / range extent
- **Meaning**: geographic extent (range size) of each guild — are higher
  trophic taxa more widespread?
- **Inputs**: occurrence coordinates per taxon.
- **Preferred**: median maximum pairwise distance per taxon per guild;
  Mann–Whitney contrast.
- **Alternatives**: convex-hull area, latitudinal range.
- **Exports**: `range_extent_contrast` (km or standardized difference).

### M3. Distance-decay
- **Meaning**: does similarity decline with distance, and does the decay
  slope differ between guilds?
- **Inputs**: pairwise dissimilarity × pairwise distance.
- **Preferred**: Mantel test (Spearman, 9999 permutations) per guild +
  β(d) curves in 100 km bins; contrast = predator Mantel r − herbivore r.
- **Alternatives**: distance-decay regression slope; centroid-displacement
  vs distance (marine telemetry); negative exponential fit.
- **Exports**: `mantel_r_herbivore`, `mantel_r_predator`, `mantel_r_contrast`,
  with p-values.

### M4. Temporal persistence / lag
- **Meaning**: does the higher-trophic signal lag the lower-trophic /
  environmental signal in time?
- **Inputs**: time-indexed occurrence/abundance or matched survey units.
- **Preferred**: lagged response model; standardized lag =
  higher-trophic lag − lower-trophic lag.
- **Alternatives**: cross-correlation of guild time series per bin
  (fossil: bin-level turnover lead/lag); event-based lag curves (marine).
- **Exports**: `temporal_lag` (native time units + notes on units).

### M5. Sampling-pool sensitivity
- **Meaning**: how much of the contrast survives restriction of the species
  / collection pool? Separates signal from gamma-pool asymmetry.
- **Inputs**: incidence matrix + pool definitions.
- **Preferred**: effect under restricted pool − effect under reference pool
  (e.g. equalized collections, dominant-quarry exclusion, singleton
  exclusion, spatial thinning); each reported with replicate distribution.
- **Exports**: `sampling_pool_sensitivity` (Δ effect restricted − reference),
  per-correction rows.

### M6. Temporal aggregation sensitivity
- **Meaning**: does the contrast depend on time-bin width?
- **Inputs**: occurrences with age estimates.
- **Preferred**: effect at coarse bin − effect at fine bin across a defined
  bin ladder (e.g. stage vs subepoch vs 1 Ma).
- **Exports**: `time_aggregation_sensitivity`.

### M7. Null / negative control
- **Meaning**: each system needs at least one null that would catch a
  methodological artifact: taxon-pool size-matched null, frequency-matched
  null, placebo/reverse-time test, or positive control.
- **Exports**: `null_model_result` rows (metric=null_*, effect vs null
  distribution quantile).

### M8. Observation-bias characterization
- **Meaning**: document the observation model per system
  (`OBSERVATION_MODEL.md`) and score bias sensitivity numerically where
  possible (observer effects, detectability, taphonomic filters, collection
  intensity).
- **Exports**: `observation_bias_score` (system-defined 0–1 or NA with
  justification) + qualitative columns in `observation_model_matrix.csv`.

### M9. Robustness classification
- **Meaning**: each primary contrast is classified A–D:
  - A — STRONG REPLICATION: core pattern reproduced and robust.
  - B — PARTIAL REPLICATION: direction reproduced, secondary mechanisms differ.
  - C — CONTEXT DEPENDENT: effect varies systematically with region/interval/
    sampling — *not* a failure when the contextual pattern is reproducible.
  - D — FAILED REPLICATION: pattern does not reproduce under adequate data.
- **Exports**: `robustness_class` ∈ {A,B,C,D}.

## Common result schema

Authoritative definition: `results/common_metrics/schema.yaml`. Every system
writes `results/common_metrics/common_metrics_<system>.csv` with the fixed
columns listed there. `NA` where a metric is scientifically inapplicable —
translated values are never fabricated; a metric that has no defensible
analogue is `NA`, not imputed.

## Standardized effect space (Tier-3 inputs)

| Quantity | Definition |
|---|---|
| Direction | `lower>higher` / `lower<higher` / `no detectable contrast` |
| Standardized magnitude | z-standardized effect, standardized mean difference, or normalized slope difference — method named in `effect_scale` |
| Temporal lag | higher-trophic lag − lower-trophic lag |
| Spatial turnover contrast | standardized Δβ (or mapped equivalent) |
| Sampling sensitivity | effect_restricted − effect_reference |
| Time-aggregation sensitivity | effect_coarse − effect_fine |

## Non-negotiables

- System adapters may not redefine the biological question; they may only
  re-map the measurement.
- No hard-coded numbers in manuscript-facing outputs — every exported value
  must be regenerated by an `analysis_script` named in the row.
- Existing validated system-specific outputs are never overwritten by the
  synthesis layer (`make synthesis` only reads committed exports).
- Random seeds are frozen per system config (`config.yaml` records them).
