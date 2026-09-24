# Core Protocol v1 — cross-system fossil spatial-bias framework

Status: v1 (frozen). Every study in this program (dinosaur guilds,
Paleozoic marine, Cenozoic mammal, Quaternary, modern terrestrial,
modern marine, and future phases) MUST implement this protocol. The
purpose is comparability: as papers accumulate, the fixed items must
not drift.

A study is "on-protocol" iff it implements every FIXED item below,
declares every VARIABLE item explicitly in its analysis plan before
results are seen, and keeps honest nulls.

Structure and process rules follow the user's reference
CORE_PROTOCOL_v1 (cross-system falsification framework); item names
are specialised to the spatial-bias question.

## 1. Fixed items (identical across all systems)

### F1. Primary contrast

Every study has exactly ONE pre-declared primary contrast: the
pool-size perturbation experiment — metrics computed on the observed
assemblage vs the same spatial framework after contracting the
observable regional taxon pool to the fixed schedule
{1.00, 0.75, 0.50, 0.25}, with Monte Carlo draws (default 200
replicates; every planned replicate stored, including invalid draws
flagged with NaN metrics — never silently dropped).

Form: Bias_x = metric_perturbed − metric_reference, for x ∈
{mean pairwise Jaccard beta, distance-decay slope}.

No secondary contrast may silently replace the primary one;
additional contrasts are labelled secondary/exploratory.

### F2. Effect direction

The sign convention and pre-registered direction are fixed before
analysis: under the pool-size bias hypothesis, pool contraction
LOWERS mean pairwise Jaccard beta (Bias_beta < 0) and steepens the
decay slope (Bias_decay > 0), matching the dinosaur reference
system. Reversing the sign convention after seeing results is
prohibited. Direction and functional form are the replication
targets; effect size is not required to match.

### F3. Sampling-pool test

Every estimate is computed on a well-defined observation universe:
the (site, time-bin) units actually sampled. Surveyed-present,
surveyed-absent and not-surveyed are three distinct states; a site
without records is not evidence of absence. Denominators (occupancy,
alpha/gamma, coverage) use sampled units only. Sampling intensity is
perturbed independently of the taxonomic pool: subsample collections
(and/or occurrences) to the same fractions {1, 0.75, 0.5, 0.25} in a
full factorial with pool fraction, so pool effects and effort
effects are separable.

### F4. Time-aggregation test

Every spatial-structure claim must survive a change of temporal
grain: progressively merge adjacent bins along at least one
predefined ladder (e.g. stage → 2-stage; 5 → 10 → 20 Myr) and report
Bias_time = metric_aggregated − metric_finest for beta, turnover,
nestedness and decay slope. The realised duration of every bin is
recorded.

### F5. Distance-decay (spatial structure test)

Every study estimates distance decay as the linear (OLS) slope of
pairwise Jaccard dissimilarity vs pairwise site distance in the
system's natural distance metric (e.g. great-circle km on
paleocoordinates; lattice distance in simulation). Store slope,
uncertainty, model fit, number of site pairs and the distance
distribution. Report the decay-slope bias under pool contraction as
a co-primary outcome (Bias_decay in F1).

### F6. Negative control

At least one negative control per study, from a fixed menu:

- simulated null through the identical pipeline (the shared 2-D
  lattice engine; identical code, parameter differences logged in
  parameter_registry.csv),
- randomised taxon labels,
- equal-pool contrast where the true pool difference is zero by
  construction,
- placebo clade/guild contrast.

### F7. Robustness classification

Every claim is labelled by the protocol, not ad hoc per paper:

- ROBUST — survives all fixed checks with consistent sign/magnitude.
- WEAK — survives some checks, bounded by identified limits.
- NULL — consistent with a declared null mechanism.
- UNSUPPORTED — contradicted by the fixed checks.

Per-clade replication is mandatory: run the full protocol separately
for each sufficiently sampled clade before any cross-clade pooling,
and report cross-clade heterogeneity. Null or heterogeneous results
are retained and reported.

## 2. Variable items (system-specific; must be declared a priori)

| item | description | examples |
|------|-------------|----------|
| V1. Database / data source | which occurrence system | PBDB, museum compilations, modern survey data |
| V2. Spatial unit | analysis unit + sensitivity resolutions | paleocoord grid cells 5°/10°/20°, basins, formations |
| V3. Temporal resolution | native binning + aggregation ladder | PBDB stages, 2-stage pairs, 5/10/20 Myr bins |
| V4. Observation-process correction | detection/preservation/env handling | environment or lithology stratification, preservation covariates |
| V5. Guild / clade definition | taxon inclusion rule | phylum/clade lists, genus-level primary, species sensitivity |

Variable items may differ across systems; once declared for a given
phase they are frozen for that phase. Species- and genus-level
estimates are never combined in one contrast. Predefined minimum
thresholds (e.g. ≥5 sites, ≥5 taxa, ≥10 site pairs) are part of the
declaration and must not be tuned to the outcome.

## 3. Process rules (fixed)

- Pre-registration discipline: analysis plan (contrasts, fractions,
  thresholds, GO/NO-GO) written before results are examined.
- GO/NO-GO verdicts per phase; honest nulls are valued equally with
  positive results.
- No spec changes to rescue a conclusion. Specification changes may
  only fix bugs; every bug fix triggers a pre/post impact audit.
- No fabricated data; no hard-coded results. All manuscript numbers
  are regenerated from pipeline outputs (results CSVs → docx
  builder; manuscript_values.csv is the trace).
- Raw source data preserved unchanged; query strings + download
  dates logged (provenance.jsonl); seeds, software versions and
  parameter registries stored.
- Branch-per-phase, PR-per-phase; prior phases are frozen once their
  PR is opened.
- Shared output schema: every study writes cross_system_export.csv
  with exactly the columns below — directly concatenable across
  systems; system-only fields go to a separate extended table:

      system, realm, geological_period, time_bin, time_start_ma,
      time_end_ma, duration_myr, clade, taxonomic_level,
      spatial_resolution, n_sites, n_collections, n_occurrences,
      gamma, median_alpha, pool_fraction, sampling_fraction,
      temporal_aggregation, beta_metric, beta_value,
      distance_decay_model, distance_decay_slope, replicate,
      analysis_version

## 4. Instantiation example — Paleozoic marine phase

| protocol item | Paleozoic-marine implementation | status |
|---|---|---|
| F1 primary contrast | pool {1,.75,.5,.25} × 200 MC; Bias_beta, Bias_decay stored per replicate | done |
| F2 direction | Bias_beta < 0, Bias_decay > 0 pre-declared | fixed pre-analysis |
| F3 sampling pool | sampled collection/site cells only; pool × sampling factorial (50 reps/cell) | done |
| F4 time aggregation | stage → 2-stage; 5 → 10 → 20 Myr ladders | done |
| F5 distance-decay | OLS Jaccard ~ great-circle km on PBDB paleocoords | done |
| F6 negative control | shared 2-D lattice engine reused verbatim; parameter registry | done |
| F7 robustness | all 6 clades: Bias_beta negative, decay positive — direction ROBUST, magnitude heterogeneous (WEAK) | assigned |
| V1 | PBDB occs, envtype=marine, Cambrian–Permian | — |
| V2 | 10° paleocoord grid (5°, 20° sensitivity) | — |
| V3 | stage + absolute-duration bins | — |
| V4 | none in core; env stratification deferred | — |
| V5 | six clades, genus level | — |

Deferred per protocol order: paleoenvironment sensitivity (V4),
mass-extinction and GOBE counterfactuals (post-core extensions).

## 5. Change control

Protocol text may only change by a dedicated PR labelled
protocol-change, with a changelog entry here and a stated reason.
Changes that would retroactively alter a finished phase's verdict
are prohibited; they apply to future phases only.

Changelog:
- v1 (2026-09-21): initial freeze; fixed items F1–F7, variable items
  V1–V5, process rules, Paleozoic-marine instantiation. Structure
  mirrors the cross-system falsification Core Protocol v1 supplied
  by the user.
