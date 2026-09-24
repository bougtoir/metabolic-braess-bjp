# Structural asymmetries distort guild-level beta-diversity contrasts
*(blinded main text — double-anonymous review)*

## Abstract
See GEB_structured_abstract.md (structured, ≤300 words).

## Introduction
Beta diversity — the compositional variation of assemblages across space — is a
foundational currency of macroecology and biogeography (Whittaker, 1960;
Tuomisto, 2010a; Anderson et al., 2011). Pairwise dissimilarity, multiple-site
metrics and the decay of similarity with distance are used to infer connectivity,
dispersal limitation, environmental filtering and biogeographic differentiation
(Nekola & White, 1999; Soininen et al., 2007; Morlon et al., 2008; Baselga,
2010). Comparative studies increasingly apply these measures across taxonomic
or functional groups — asking, for example, whether one guild is more spatially
homogeneous than another — because such contrasts promise inference about
group-specific spatial ecology (Heino et al., 2015). All of these applications
are scale-dependent: turnover varies with the spatial grain and extent of the
data (Wiens, 1989; Barton et al., 2013). When such measures are compared
between guilds, clades or functional
groups, the comparison carries an implicit assumption: that the two assemblages
are structurally comparable — that differences in their regional pool size,
dominance structure, taxonomic resolution, temporal span and sampling intensity
do not themselves alter measured turnover.

In practice, however, guilds and assemblages differ routinely in exactly these
properties. A predator guild and its prey guild typically differ in pool size;
a dominant species can occupy most of the sampled sites while its comparison
guild has none; one group may be identifiable to species while another is only
resolvable to genus; one dataset may integrate a decade of sampling while
another pools centuries; and the two sides may have been collected under
different effort regimes. Each of these structural properties is individually
known to affect diversity metrics. Measured beta diversity depends
on the size and composition of the regional species pool (Kraft et al., 2011;
Chase et al., 2011; Pärtel et al., 2011; Zobel, 2016), and comparisons across
assemblages of unequal richness are a known source of scale-dependent distortion
(Chase et al., 2018). Dominant species and the shape of the occupancy–frequency
distribution can drive dissimilarity values regardless of underlying spatial
processes (Lennon et al., 2004; McGeoch & Gaston, 2002; McGill et al., 2007;
Hillebrand et al., 2008). The taxonomic grain at which data are recorded alters
diversity patterns (Bertrand et al., 2006; Bevilacqua et al., 2012), temporal
aggregation reshapes apparent community change (Olszewski, 1999; Korhonen et al.,
2010; Blowes et al., 2019), and unequal sampling effort and incomplete detection
bias comparisons when they are not standardized (Gotelli & Colwell, 2001;
MacKenzie et al., 2002; Colwell et al., 2012; Chao et al., 2014). Because these
mechanisms co-occur in real data and interact, treating them as independent
additive corrections is itself an untested assumption. Each mechanism is
established; what is missing is a quantitative account of how large their
separate and joint effects on guild-level turnover contrasts can be.

This is not merely a fossil problem. Much of the biodiversity evidence now used
in macroecology is historically aggregated: museum and herbarium collections,
long-term monitoring compilations, archaeological faunas, pollen and sedimentary
records are all assembled over uneven taxonomic, temporal and sampling structure
(Shaffer et al., 1998; Graham et al., 2004; Pyke & Ehrlich, 2010; Lavoie, 2013).
Palaeoecological assemblages are the extreme end of the same spectrum — they push
every structural asymmetry further, with small and uneven taxon pools, strong
dominance, coarse taxonomic resolution and temporal averaging over thousands to
millions of years (Kidwell & Behrensmeyer, 1991; Olszewski, 1999; Behrensmeyer et
al., 2000; Badgley, 2010; Smith & McGowan, 2007; Vilhena & Smith, 2013). If
structural bias in guild-level turnover comparisons is consequential anywhere,
it should be consequential there. The fossil record therefore serves as an
informative stress test for a general inferential problem rather than a special
case with its own rules (Uhen et al., 2013; Peters & McClennen, 2015).

What is missing from the literature is not awareness that these biases exist but
their magnitudes under controlled conditions: how large can a structurally
generated guild contrast become when no true ecological difference exists?
Can structural asymmetry reverse the sign of a contrast? And does it alter only
the mean of dissimilarity, or also the shape of spatial turnover — the
distance-decay relationship that underlies biogeographic inference? Answering
these questions requires ground truth, which empirical assemblages cannot
provide; it requires simulation.

Here we combine (i) controlled simulations in which the true guild contrast is
zero by construction, on a one-dimensional spatial axis and, as a robustness
check, a two-dimensional lattice; (ii) a factorial map identifying joint
conditions that produce false differences and sign reversals; (iii) an analysis
of how structural asymmetry distorts distance-decay slopes, not just mean
dissimilarity; and (iv) an empirical fossil stress test — dinosaur assemblages of
the Late Jurassic Morrison Formation (Maidment et al., 2024) — in which an
initially strong guild-level turnover contrast is decomposed stepwise under
structural controls, with the Nemegt Formation as an external comparator. Our
central equation is Δβ_observed ≠ Δβ_ecological whenever the compared guilds
differ in assemblage structure. Our objectives are to quantify the magnitude of
structural bias under controlled conditions, to identify conditions causing
false differentiation, lost differentiation and sign reversal, to decompose the
Morrison signal empirically, and to derive a practical diagnostic workflow for
guild-level beta-diversity inference in structurally heterogeneous data.

## Methods
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

## Results
## Results 1 — Gamma-diversity imbalance alone creates strong apparent guild contrasts

With the true guild contrast fixed at zero, reducing one guild's
regional taxon pool generated substantial apparent turnover bias despite
identical true guild turnover: at a predator pool of 4 taxa (against 26
herbivore taxa — a realistic Morrison-like asymmetry) mean Δβ_obs was
−0.170 (95% replicate interval −0.187, −0.157), and under the most
extreme tested condition, a two-taxon pool, bias reached −0.412
(−0.443, −0.398) (Fig. 2a). A "false contrast" is defined here as
|Δβ_obs| > 0.1 on the mean-pairwise Jaccard contrast (a
magnitude-and-sign threshold on the point estimate — not a CI or
p-value criterion; replicate spread supplies the interval): the
false-contrast rate was 100% at predator pools of both 2 and 4 taxa
(200 replicates each, seed 20260922), and the all-negative-sign rate
persisted through pools of 20. Only at equal pools (26 vs 26) did
Δβ_obs centre on zero (−0.0001; −0.008, +0.008).

A lightweight two-dimensional replication (40×40 lattice, disc-shaped
ranges, identical pool asymmetry; 100 replicates, seed 20260924)
reproduced the qualitative pattern: bias ≈ −0.21 at a four-taxon pool
and ≈ −0.47 at the extreme two-taxon pool, confirming the phenomenon is
not an artefact of one-dimensional range geometry. Pool asymmetry also
inflated the small-pool guild's apparent distance-decay slope
(≈0.028 lattice-units⁻¹ versus ≈0.006 for the comparison guild under
identical true spatial processes): the bias distorts the spatial form
of turnover, not only its mean (Fig. 3).

## Results 2 — Dominance, taxonomic lumping, temporal averaging and sampling

**Dominant taxon.** A single dominant predator lowered Δβ_obs
monotonically with its prevalence: bias ≈ −0.07 at p_D = 0.5 — the
cell bracketing Allosaurus's observed 45.6% occupancy — and ≈ −0.21
at p_D = 0.9 (Fig. 2b).

**Taxonomic lumping.** We define B_lumping = β_species − β_genus of the
manipulated guild; positive values mean genus pooling makes the guild
appear *more* spatially continuous. Collapsing k geographically
partitioned species into one genus produced B_lumping up to +0.099 at
k = 6, shifting Δβ_obs from −0.001 (species-resolved) to −0.101
(genus-pooled; Fig. 4a) — i.e., lumping fabricated apparent predator
continuity.

**Temporal averaging.** Pooling 8 thin time slices into progressively
wider bins attenuated the observed guild contrast from −0.031
(single-slice bins) to −0.001 (full pooling; Fig. 4b) — pooling
drives Δβ toward zero whether the contrast is structural or
ecological, because union-pooling inflates within-bin occupancy and
mechanically deflates per-guild beta diversity. Temporal averaging can
therefore erase structure, not only create it.

**Sampling asymmetry.** An 8-fold predator-sampling asymmetry between
environmental blocks produced comparatively small bias under the
parameter range examined (Δβ_obs between −0.024 and −0.023; Fig. S#);
we do not claim sampling bias is unimportant in general.

## Results 3 — Factorial simulation: sign-reversal and false-difference regions

The five structural terms are not independent. In the factorial grid
(n_pred_taxa × p_dominant × n_lumped), biases compound non-additively:
the most extreme cell reached Bias = −0.91 and the false-difference
rate (|Δβ_obs| > 0.1 under Δβ_true = 0) reached 100% in the
low-gamma, high-dominance, high-lumping region (Fig. 5). Because
interactions dominate the corner cases, no single-bias correction is
sufficient.

## Results 4 — Morrison worked example: the naive guild contrast

On the primary specification (collection assemblages, genus level,
Jaccard), Morrison predators were much more spatially homogeneous than
herbivores: Δβ = −0.550 (bootstrap 95% CI −0.630, −0.457). Read
naively this would imply exceptional predator spatial continuity —
exactly the class of signal Simulations 1–3 show can arise
structurally.

## Results 5 — Sequential empirical decomposition

Applying the diagnostic cascade (Fig. 6):

1. **Gamma-matched null.** Δβ = −0.550 lies inside the pool-matched
   null interval (−0.534 to −0.229): unequal taxon pools account for
   much of the magnitude.
2. **Frequency-matched null.** The observed value is more negative
   than the frequency-matched null interval (−0.124 to −0.095):
   occupancy-frequency structure alone does not produce the signal.
3. **Dominant-taxon exclusion.** Removing Allosaurus collapses Δβ to
   −0.020 (−0.128, +0.024).
4. **Taxonomic resolution.** At species level Δβ attenuates to −0.322
   (−0.426, −0.234), direction consistent with Simulation 3.
5. **Duration + sampling adjustment.** After regressing geographic
   extent on stratigraphic duration and occurrence count, Allosaurus's
   extent residual is −36.6 km (z = −0.16): not geographically
   exceptional for its sampling footprint.
6. **Preservation/collection model (exploratory).** The unpenalized
   model reached pseudo-R² = 0.46 but did not fully converge
   (quasi-separation; state coefficients ≈ 17). An L2-penalized
   logistic refit converged and yielded pseudo-R² = 0.34 — the same
   qualitative conclusion that collection covariates carry substantial
   presence structure. Both are retained as exploratory diagnostics
   only.

## Results 6 — Nemegt comparator

Under the identical locked pipeline, Nemegt (herbivore gamma 8 <
predator gamma 26 — the reverse asymmetry) yields Δβ = +0.094
(95% CI −0.079, +0.300): the Morrison direction is not reproduced.
Nemegt functions here as a structural comparator showing the pattern is
not a universal predator-guild phenomenon; extended Tarbosaurus
diagnostics appear in the Supplementary Material.

## Results 7 — Independent evidence audit

A bounded review of isotopic, ichnological and feeding-trace evidence
identified nothing contradicting the methodological interpretation;
the strongest independent evidence supports dietary generalism rather
than exceptional mobility, and no direct test of Allosaurus movement
was identified (Supplementary Material).

## Discussion
### Main conceptual result

Our simulations demonstrate two symmetric inferential failures. Under a true
guild contrast of zero (Δβ_true = 0), structural asymmetry alone — unequal
regional pools, dominance, taxonomic lumping — generated observed contrasts as
large as |Δβ_obs| ≈ 0.17 for a realistic four-taxon pool and ≈ 0.41 under the
most extreme two-taxon pool, a false-positive mechanism. Conversely, temporal
aggregation attenuated observed contrasts toward zero (2-D: −0.045 → −0.018), a
false-negative mechanism. Assemblage construction can thus both create and erase
apparent ecological spatial structure. These magnitudes are scenario-specific
demonstrations of sufficiency, not universal constants, but the two failure
directions are qualitative properties of guild-level comparisons rather than
artifacts of any single parameterization. The two failure directions are also asymmetric
in where they hide: false differentiation is invisible to naive replication —
repeating the same contrast on structurally similar data reproduces the same
bias — whereas lost differentiation is invisible precisely because nothing is
seen. A diagnostic workflow must therefore test both directions rather than
searching only for spurious signal.

### Gamma diversity

The largest single bias source was gamma-diversity imbalance. Richness effects
on dissimilarity metrics are recognized (Kraft et al., 2011; Chase et al., 2011),
but the magnitudes observed here — a four-taxon pool yielding a fully
reproducible apparent contrast of −0.17 against a 26-taxon pool under Δβ_true =
0 — show that pool-size-matched nulls are not optional refinements but a minimal
requirement. The qualitative result replicated across spatial geometries: on a
2-D lattice the same conditions produced −0.21 (pool 4) and −0.47 (pool 2),
indicating the phenomenon is not an artifact of one-dimensional range geometry.
Comparisons among guilds or regions with different pool structures remain
vulnerable even after standard diversity partitioning (Chase et al., 2018).

### Distance-decay distortion

A result of particular relevance to biogeographic inference is that structural
asymmetry distorts the *shape* of turnover, not only its mean. In the 2-D
simulations, the small-pool guild showed an inflated apparent distance-decay
slope (≈0.028) relative to the comparison guild (≈0.006) under identical true
spatial processes. Distance decay is a core tool for diagnosing dispersal
limitation and environmental filtering (Nekola & White, 1999; Soininen et al.,
2007; Morlon et al., 2008); our result implies that guild or regional
differences in pool size alone can mimic steeper turnover gradients, so decay
comparisons require the same structural controls as mean dissimilarity.
Practically, a reported difference in distance-decay slopes between groups may
reflect differential sensitivity to pool size rather than differential
dispersal; pool-matched or richness-standardized decay curves are the analogue
of the matched-null requirement for mean Δβ.

### Dominance and taxonomic aggregation

A single dominant taxon shifted Δβ by ≈−0.07 at realistic prevalence and
≈−0.21 at extreme dominance — consistent with the known sensitivity of
assemblage dissimilarity to common species (Lennon et al., 2004; Hillebrand et
al., 2008; McGeoch & Gaston, 2002). Genus-level pooling of geographically
differentiated species produced an apparent continuity shift of +0.099
(B_lumping = β_species − β_genus; positive = more apparent continuity),
mirroring taxonomic-sufficiency effects documented for assemblage analyses
(Bertrand et al., 2006; Bevilacqua et al., 2012; Lane et al., 2003). In the
Morrison case, dominant-taxon exclusion and species-level resolution each
collapsed or attenuated the naive contrast — an empirical illustration, not a
general estimate. The two mechanisms are usefully distinguished: dominance
changes which *sites* are occupied (fewer occupied sites than the pool implies,
biasing β downward in the dominant guild), whereas lumping changes which
*entities* are counted (multiple spatially segregated species fused into one
widespread genus, erasing turnover at the finer taxonomic grain). Both inflate
apparent spatial continuity but through different data construction paths, so
the diagnostics differ: occupancy-frequency inspection for the former,
resolution sensitivity for the latter.

### Temporal aggregation

Pooling eight temporal slices into one bin attenuated the observed contrast
toward zero (1-D: −0.031 → −0.001; 2-D: −0.045 → −0.018). Time averaging is
expected to homogenize assemblages (Kidwell & Behrensmeyer, 1991; Olszewski,
1999; Kowalewski, 1996; Tomašových & Kidwell, 2010), but the symmetric framing
matters: temporal aggregation is primarily a *false-negative* mechanism, erasing
genuine structure rather than manufacturing it, whereas gamma imbalance,
dominance and lumping chiefly generate *false-positive* differentiation.

### Sampling

An eight-fold sampling asymmetry produced comparatively small bias (≈−0.024)
within the tested parameter range. We do not infer that sampling is unimportant
— fossil databases are demonstrably sampling-structured (Smith & McGowan, 2007;
Vilhena & Smith, 2013) — only that under our parameterization its isolated
effect was smaller than pool-size, dominance and lumping effects.

### Empirical stress test

In the Morrison Formation, a naive predator–herbivore Δβ of −0.550 fell within
the gamma-matched null interval, exceeded the frequency-matched null, and
collapsed to −0.020 after exclusion of the single dominant taxon; species-level
resolution gave −0.322, and the dominant taxon was not geographically
exceptional after duration and occurrence adjustment (extent residual −36.6 km,
z = −0.16). Collection covariates explained substantial presence structure
(pseudo-R² 0.46 unpenalized, 0.34 under L2 penalization — exploratory, with an
MLE convergence warning; the penalized fit reaches the same qualitative
conclusion). The correct interpretation is not that the ecological account was
disproven, but that structural explanations became sufficient — a biologically
compelling narrative was no longer required. Nemegt, run through the identical
locked pipeline, showed Δβ = +0.094 (−0.079, +0.300): the Morrison direction is
not a universal predator-guild property.

### Factorial interaction

Because gamma diversity, dominance, taxonomic resolution and sampling co-vary in
real assemblages, the bias terms cannot be treated as independent additive
corrections. The factorial simulation — the appropriate summary for applied
inference — shows interactions large enough to reverse sign (the extreme corner
reached −0.91). This is why single-mechanism corrections under-protect: fixing
only pool size leaves dominance and lumping free to generate a contrast; the
diagnostic workflow must therefore be sequential and cross-checked rather than
a single covariate adjustment.

### General applicability

The mechanisms quantified here apply wherever comparisons are made between
assemblages differing in pool size, dominance, taxonomic grain, temporal span or
sampling structure — museum and herbarium records, multi-year monitoring
compilations, archaeological faunas, and sedimentary records (Shaffer et al.,
1998; Pyke & Ehrlich, 2010; Lavoie, 2013; Graham et al., 2004). These are
conceptual analogues; direct tests in each domain are needed, and our magnitudes
should not be transported quantitatively. The growing reliance on aggregated
occurrence datasets for biodiversity-change inference (Blowes et al., 2019)
makes the asymmetry between the two failure modes especially consequential:
structurally generated contrasts are likely to be interpreted as ecological
signal, while temporally erased contrasts are invisible and therefore never
tested for. Among the candidate biases we isolated, the pool-size mechanism has
the clearest parallel outside palaeontology — cross-guild and cross-region
richness asymmetries are ubiquitous in modern occurrence data — whereas
temporal averaging is most acute in archives that integrate time, and taxonomic
lumping sits between the two wherever identification effort varies across
groups.

### Practical workflow

Before interpreting guild-level beta-diversity contrasts: (1) compare guild
gamma diversity; (2) run pool-size-matched nulls; (3) inspect dominance and run
leave-one-dominant-taxon analyses; (4) harmonize taxonomic resolution and test
sensitivity across levels; (5) test temporal aggregation; (6) inspect sampling
asymmetry and detection structure; (7) examine distance-decay slopes, not only
mean dissimilarity; (8) map interactions across these factors; (9) only then
infer ecological connectivity, mobility or filtering. The same discipline
applies to non-fossil assemblage comparisons (Socolar et al., 2016).

### Limitations

Our simulators use simplified ecology and synthetic guild construction;
parameter ranges were chosen to bracket plausible assemblage structures but the
reported magnitudes are not calibrated estimates for real landscapes. The bias
mechanisms are non-independent — the factorial map, not the additive
decomposition, is the appropriate summary. The 2-D replication improves but does
not reproduce real landscape complexity. Morrison is one worked example and
species-resolution analyses depend on identification completeness. Structural
sufficiency is not causal attribution: demonstrating that a contrast *can* be
generated structurally does not prove it *was*.

## References
See bibliography.md (52 DOI-verified entries; reference_audit.csv).
