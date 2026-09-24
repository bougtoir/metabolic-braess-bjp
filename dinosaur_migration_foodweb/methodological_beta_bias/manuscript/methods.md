# Methods

## Overview

We combine (i) controlled simulation of fossil guild assemblages, in
which the true ecological turnover contrast is known, with (ii) a
sequential empirical decomposition of a real guild-level beta-diversity
contrast in the Upper Jurassic Morrison Formation, and (iii) a negative
external comparator from the Nemegt Formation. All estimators, null
models, seeds and output files are frozen and versioned; every number
cited in the manuscript is traced in `results/manuscript_values.csv`.

## Terminology and estimand

Throughout, beta diversity is measured between assemblages as the
mean pairwise Jaccard dissimilarity computed on incidence matrices,
equivalently one minus the mean pairwise Jaccard index. The focal
contrast is

Δβ = β_P − β_H

where β_P and β_H are mean pairwise Jaccard beta diversities of the
predator and herbivore guilds. The estimand is the mean of pairwise
dissimilarities, identical for the point estimate and the bootstrap
distribution (collection resampling with replacement on incidence
rows). Under a simulated scenario, bias is defined as

Bias = Δβ_obs − Δβ_true.

Sign conventions: Δβ < 0 indicates predators are *more* spatially
homogeneous than herbivores; Δβ > 0 indicates greater predator
turnover. A lumping manipulation that lowers predator beta raises
β_H − β_P and therefore produces Δβ < 0 (apparent predator
continuity); we report lumping effects as B_lumping = β_species − β_genus
of the manipulated guild and as Δβ shifts with explicit sign annotation.

## Simulation design

Artificial fossil assemblages are generated on a 1-D spatial axis of
N = 200 localities (analysis/sim_core.py). Each taxon occupies a
contiguous range of width `breadth` (fraction of the axis) centred at
a uniform random location; within its range it is recorded with
probability `occ_p` per locality. Guild incidence matrices are built
independently for herbivores (26 taxa) and predators from identical
per-taxon parameters, so the two guilds share the same underlying
spatial process — contiguous random ranges, equal occupancy
probability — and Δβ_true = 0 in expectation; the guilds differ only
in pool size. The simulator is deliberately one-dimensional
(contiguous 1-D ranges): bias magnitudes are demonstrations of
sufficiency, not calibrated estimates for real palaeolandscapes.
The conceptual decomposition
Δβ_obs = Δβ_eco + B_γ + B_D + B_T + B_L + B_S + ε is a scaffold, not
a fitted causal partition; the five terms can interact, which is why
Simulation 6 is factorial. Default
parameters: breadth = 0.45, occ_p = 0.35, N_H = 26, N_P = 12. All
sweeps use 100–200 replicates per cell with frozen seeds
(20260922–20260923).

### Two-dimensional robustness and distance decay
A confirmatory simulator generates assemblages on a 40×40 square
lattice: each taxon occupies a disc of radius 0.225·L centred at a
uniform-random location, recording with occ_p = 0.35 per lattice cell
(analysis/13_2d_robustness.py, seed 20260924, 100 replicates). Beyond
mean pairwise β, we compute distance-decay slopes as the linear
regression slope of pairwise Jaccard dissimilarity on pairwise
Euclidean distance (lattice units) per replicate and guild; slope
comparisons report small-pool versus comparison-guild apparent decay
under identical true spatial processes.

### Simulation 1 — gamma-diversity imbalance
Herbivore richness fixed at 26; predator richness swept 2–26.
Δβ_true = 0 by construction. Output: mean Δβ_obs, 95% quantile
interval, proportion of replicates with Δβ_obs < 0 and with
|Δβ_obs| > 0.1 (false-contrast rate).

### Simulation 2 — dominant taxon
One predator taxon is elevated to a dominant that occurs in proportion
p_D of all localities, independent of range; p_D swept 0–0.9.

### Simulation 3 — taxonomic lumping
k geographically partitioned species (disjoint sub-ranges, joint
occupancy ~0.6) are collapsed into a single genus column. Bias is
reported as β_species − β_genus for the predator guild and as the
change in Δβ between species- and genus-level matrices.

### Simulation 4 — temporal averaging
Each taxon's occurrence pattern is re-drawn independently across 8
time slices (true within-slice contrast = 0 across slices but guild
turnover exists per slice); locality rows are then pooled into bins of
8, 4, 2, or 1 slice(s) (pooled presence = slice-wise OR).

### Simulation 5 — asymmetric sampling
The spatial axis is divided into alternating 20-locality environment
blocks; predator occurrences in environment A are retained with a
sampling multiplier of 1–8× relative to environment B (truncated at 1).

### Simulation 6 — factorial
Full grid of n_pred_taxa (2–26) × p_dominant (0–0.9) × n_lumped
(1, 3, 6 partitioned species), 100 replicates per cell, to map
sign-reversal (Δβ_obs sign opposite Δβ_true) and false-difference
(|Δβ_obs| > 0.1) regions; the five bias terms are not assumed
independent — the factorial design is the primary evidence on
interaction.

## Empirical worked example — Morrison Formation

Occurrence data derive from the Maidment et al. (2024) Dryad dataset
(DOI 10.5061/dryad.6m905qg77; CC0), hashed with sha256 and listed in
`metadata/sources.csv`: 651 dinosaur occurrences, 239 collections,
38 resolved genera. Guilds follow the published taxonomy; predators =
theropod taxa, herbivores = ornithischian + sauropodomorph taxa.
Analyses use the collection (assemblage) as the spatial unit, genus
resolution, Jaccard metric, and a 999-replicate collection bootstrap
(seed 20260920).

The sequential decomposition applies, in fixed order:
1. naive genus-level Δβ;
2. gamma-matched null (B = 10,000 replicates reassigning guild labels
   across genera while preserving pool sizes);
3. frequency-matched null (occupancy-frequency matched);
4. exclusion of the dominant predator (Allosaurus);
5. species-level resolution (Allosaurus split into named species);
6. stratigraphic-duration + occurrence-count OLS on geographic extent
   (extent ~ duration + n_occurrences), reporting the Allosaurus
   residual and z-score;
7. an exploratory collection-covariate logistic model of Allosaurus
   presence (environment, lithology, collection type, count type),
   reported only as pseudo-R². The unpenalized fit showed
   quasi-separation (state coefficients ≈ 17, MLE non-convergence);
   an L2-penalized logistic refit (sklearn, C = 1, 0.1, 10) converged
   and is reported as a robustness check alongside it. Both remain
   exploratory and carry no inferential weight.

## External comparator — Nemegt Formation

Nemegt dinosaur occurrences were pulled from the Paleobiology Database
(Paleodata API; collections filtered to Nemegt-bearing collections in
Mongolia, Maastrichtian), with sha256 provenance: 319 dinosaur
occurrences, 124 collections; body-fossil genus-resolved subset: 89
collections, predator 116 occurrences / 26 genera, herbivore
34 occurrences / 8 genera. The identical locked pipeline (Jaccard,
collection level, genus, 999 bootstrap, seed 20260920) yields the
comparator Δβ. The gamma-matched null degenerates here because
herbivore gamma (8 genera) is smaller than predator gamma — Nemegt is
used strictly as a comparator of opposite structure, not as a
biological replication test.

## Independent evidence audit

A bounded literature scan (stable isotopes, trackways, feeding traces,
ontogenetic structure, palaeobiogeography) classifies each evidence
class on a five-point scale from "supports exceptional mobility" to
"contradictory"; the full classification is in
INDEPENDENT_EVIDENCE_AUDIT.md.

## Reproducibility

All random seeds are frozen; scripts 01–11 under
`methodological_beta_bias/analysis/` regenerate every table and figure.
`results/manuscript_values.csv` maps each cited number to its source
script, output file, figure panel and manuscript location.
