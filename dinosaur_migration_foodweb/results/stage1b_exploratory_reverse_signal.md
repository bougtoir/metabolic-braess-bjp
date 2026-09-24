# Stage 1b — Exploratory reverse-signal characterization

**Status: exploratory, post hoc, hypothesis-generating.** The original
confirmatory hypothesis (Δβ > 0) was falsified and frozen in
`results/stage1_original_hypothesis_report.md`. Nothing here is confirmatory
evidence for the reverse biological hypothesis.

## Observed reverse effect

Δβ (Simpson, genus level, collection scale) = **-0.543**
(bootstrap 95% CI excludes 0; see Stage-1a report).

## A. Taxon-pool matched null (B=10,000)

Herbivore guilds subsampled to predator gamma diversity (12 genera):

- null mean -0.424, median -0.420,
  95% null interval [-0.643, -0.241]
- observed -0.543; fraction of nulls ≤ observed:
  0.099

→ The observed Δβ falls **inside** the size-matched null interval: regional
gamma-pool asymmetry alone can produce effects of this sign and magnitude.

## B. Frequency-matched null (B=10,000)

Herbivore genera caliper-matched to predator occupancy frequencies:

- null mean -0.185, 95% null interval
  [-0.204, -0.166]
- observed -0.543; fraction of nulls ≤ observed:
  0.000

→ Even after matching occupancy/dominance structure, the observed Δβ is
**more negative than every matched realisation** — the reverse signal is not
reproduced by dominance structure alone.

## C. Allosaurus dependence

| Scenario | Δβ | Notes |
|---|---|---|
| C1 full | -0.543 | — |
| C2 exclude Allosaurus | -0.003 | signal collapses to ~0 |
| C3 downsample to median | 0.059 | [0.032, 0.074] |
| C3 downsample to p75 | 0.070 | [0.036, 0.092] |
| C3 downsample to p90 | 0.075 | [0.043, 0.103] |
| C3 downsample 50% | -0.289 | [-0.349, -0.232] |
| C4 species split | -0.157 | n_taxa=15 |
| C5 Allosaurus only | — | 109 collections (0.956 of predator collections), lat range 13.093°, lng range 8.446° |

→ The reverse signal is **mostly Allosaurus-driven**: removing it leaves
Δβ ≈ 0, and downsampling it to typical predator counts flips the sign
slightly positive. Splitting Allosaurus to species retains a moderate
negative value.

## D. Systems-tract stratification

|   systems_tract |   n_herbivore_collections |   n_herbivore_taxa |   n_predator_collections |   n_predator_taxa | note                     |     beta_H |      beta_P |   delta_beta |       lo95 |       hi95 |
|----------------:|--------------------------:|-------------------:|-------------------------:|------------------:|:-------------------------|-----------:|------------:|-------------:|-----------:|-----------:|
|               2 |                         4 |                  5 |                        4 |                 2 | insufficient collections | nan        | nan         |   nan        | nan        | nan        |
|               3 |                        15 |                 11 |                        8 |                 3 | nan                      |   0.566667 |   0         |    -0.566667 |  -0.738889 |  -0.371429 |
|               4 |                        52 |                 16 |                       33 |                 8 | nan                      |   0.577086 |   0.153093  |    -0.423993 |  -0.575305 |  -0.274393 |
|               5 |                        32 |                 20 |                       19 |                 7 | nan                      |   0.607479 |   0.0224172 |    -0.585062 |  -0.708491 |  -0.436964 |
|               6 |                        42 |                 14 |                       24 |                 9 | nan                      |   0.6006   |   0.131039  |    -0.469561 |  -0.616804 |  -0.322298 |

→ Δβ < 0 within every sufficiently sampled systems tract (3–6), with
bootstrap CIs entirely negative — the signal is not confined to one
depositional window.

## E. Stratigraphic control (interval bins)

| interval      |   n_herbivore_collections |   n_predator_collections |     beta_H |       beta_P |   delta_beta | note                     |
|:--------------|--------------------------:|-------------------------:|-----------:|-------------:|-------------:|:-------------------------|
| Kimmeridgian  |                       171 |                       96 |   0.631769 |   0.107182   |    -0.524587 | nan                      |
| Other/undated |                         1 |                        1 | nan        | nan          |   nan        | insufficient collections |
| Oxfordian     |                         1 |                        3 | nan        | nan          |   nan        | insufficient collections |
| Tithonian     |                        33 |                       14 |   0.677273 |   0.00915751 |    -0.668115 | nan                      |

→ Persists within the Kimmeridgian and Tithonian bins; Oxfordian and
undated bins are too sparse.

## F. Taxonomic-resolution symmetry

| level         | guild     |   n_collections |   n_taxa |   beta_simpson |
|:--------------|:----------|----------------:|---------:|---------------:|
| genus_level   | herbivore |             206 |       26 |      0.635436  |
| genus_level   | predator  |             114 |       12 |      0.0920768 |
| genus_level   | DELTA     |             nan |      nan |     -0.543359  |
| species_level | herbivore |             206 |       52 |      0.751332  |
| species_level | predator  |             114 |       22 |      0.485792  |
| species_level | DELTA     |             nan |      nan |     -0.265541  |

→ Genus-level Δβ = -0.543;
species-level Δβ = -0.266
(still negative, attenuated — consistent with Allosaurus splitting raising
predator turnover).

## G. Metric and spatial-scale robustness

| unit       | metric   |   beta_H |    beta_P |   delta_beta |
|:-----------|:---------|---------:|----------:|-------------:|
| collection | simpson  | 0.635436 | 0.0920768 |    -0.543359 |
| collection | sorensen | 0.784334 | 0.235193  |    -0.549141 |
| collection | jaccard  | 0.838013 | 0.288279  |    -0.549734 |
| grid_50km  | simpson  | 0.44748  | 0.0671922 |    -0.380287 |
| grid_50km  | sorensen | 0.712603 | 0.309844  |    -0.402759 |
| grid_50km  | jaccard  | 0.796285 | 0.391936  |    -0.404349 |
| grid_100km | simpson  | 0.432879 | 0.0860253 |    -0.346853 |
| grid_100km | sorensen | 0.71637  | 0.351696  |    -0.364674 |
| grid_100km | jaccard  | 0.800107 | 0.441018  |    -0.359089 |
| grid_150km | simpson  | 0.355703 | 0.050754  |    -0.304949 |
| grid_150km | sorensen | 0.683915 | 0.392982  |    -0.290933 |
| grid_150km | jaccard  | 0.778953 | 0.501651  |    -0.277302 |

→ Δβ < 0 for Simpson/Sorensen/Jaccard at collection scale and at 50/100/150 km
grid pooling; magnitude attenuates with aggregation (−0.55 → −0.28).

## Exploratory interpretation

**Classification: ALLOSAURUS-SPECIFIC** (with a residual artifact
contribution from gamma-pool asymmetry).

- The signal is real in the statistical sense (robust across tracts,
  intervals, metrics, scales, and frequency-matched nulls), but it is
  carried overwhelmingly by one ubiquitous predator genus rather than being
  a guild-wide predator property (C2: Δβ ≈ 0 without Allosaurus).
- Movement cannot be inferred from continuity alone. Candidate mechanisms
  for Allosaurus ubiquity include mobility, dietary generalism, taxonomic
  lumping, and preservational structure.

## Implication for Stage 1c

A defensible confirmatory question is the narrower one: **is predator
community spatial turnover lower than herbivore turnover in an independent
formation, at a preregistered metric/scale, with per-taxon occupancy or
gamma-pool matching controls?** See `VALIDATION_HYPOTHESES.md`.
