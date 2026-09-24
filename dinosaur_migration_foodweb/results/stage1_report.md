# Stage 1 report — Morrison Formation beta diversity

Generated from `results/tables/*.csv` by `analysis/99_stage1_report.py`.

## Data summary (Maidment et al. 2024, Dryad 10.5061/dryad.6m905qg77)

| Quantity | Value |
|---|---|
| Tetrapod occurrences | 1391 total; 651 dinosaur |
| Collections (dinosaurs) | 206 herbivore, 114 predator |
| Genera | 38 dinosaur genera (26 herbivore, 12 predator) |
| Taxonomic resolution | all dinosaur occurrences resolve to genus or better in the accepted taxonomy |
| Spatial coverage | lat 33.8–46.9, lng -111.7–-102.8 |
| Missingness | 0 lat/lng missing; 115 dinosaur occurrences lack a systems tract |

## Primary test: Delta-beta = beta_predator - beta_herbivore

Simpson turnover dissimilarity on genus incidence matrices; pairwise
great-circle distances; bootstrap over collections (999 replicates).

| Metric | beta_herbivore | beta_predator | Delta-beta | boot 95% CI | P(Delta>0) |
|---|---|---|---|---|---|
| Simpson | 0.635 | 0.092 | -0.543 | [-0.623, -0.452] | 0.000 |
| Sorensen | 0.784 | 0.235 | -0.549 | [-0.623, -0.465] | 0.000 |

Mantel tests (Spearman, distance vs dissimilarity):
herbivore r=-0.005 (p=0.849);
predator r=-0.028 (p=0.561).

## Sensitivity to sampling corrections

| correction            |   delta_beta_mean |      lo95 |      hi95 |   prop_gt0 |   n_rep |
|:----------------------|------------------:|----------:|----------:|-----------:|--------:|
| raw                   |         -0.543359 | -0.543359 | -0.543359 |          0 |       1 |
| no_dominant_quarries  |         -0.571091 | -0.571091 | -0.571091 |          0 |       1 |
| no_singletons         |         -0.432027 | -0.432027 | -0.432027 |          0 |       1 |
| equalized_collections |         -0.542123 | -0.590477 | -0.490509 |          0 |     999 |
| spatial_thinning_1deg |         -0.58106  | -0.703586 | -0.441655 |          0 |     999 |

## Genus geographic ranges

| guild     |   count |    mean |   median |     max |
|:----------|--------:|--------:|---------:|--------:|
| herbivore |      26 | 514.208 |  560.142 | 1204.22 |
| predator  |      12 | 481.305 |  550.421 | 1460.63 |

## Verdict

**The naive Delta-beta > 0 prediction is CONTRADICTED.** Predator assemblages
show *lower* pairwise turnover than herbivore assemblages under both metrics
and every sampling correction (Delta-beta ~ -0.5).

## Interpretation and caveats

1. **Taxonomic asymmetry**: predators have 12
   genera vs 26 herbivore genera, and
   *Allosaurus* alone accounts for ~70% of predator occurrences. Low predator
   beta partly reflects regional-pool poverty plus a single ubiquitous genus,
   not necessarily weaker geographic partitioning of rarer predators.
2. Simpson turnover is insensitive to alpha-richness differences but not to
   gamma-pool size; a guild-level null model (genus-label permutation) is the
   next refinement before concluding.
3. **Alternative reading**: ubiquitous *Allosaurus* is itself consistent with
   predators tracking mobile prey subsidies across the basin — i.e. low
   predator turnover may reflect subsidy-following rather than residency.
   This requires the Stage-2/4 machinery (SRF, energetics, movement models)
   to distinguish.
4. Herbivore turnover is high; whether it is *seasonal* (migratory taxa
   occupying different collections at different times) vs *ecogeographic*
   partitioning cannot be separated by occurrence data alone — the systems-
   tract column enables a temporal-stratified repeat of this analysis.

## Decision

H1 in its literal form is contradicted, but the result is confounded by
guild-level diversity asymmetry. Recommended before abandoning: (a) genus-
pool size-matched null model; (b) systems-tract-stratified beta curves;
(c) proceed to Stage 2 only if the signal survives refinement, per the
stage-gate policy.
