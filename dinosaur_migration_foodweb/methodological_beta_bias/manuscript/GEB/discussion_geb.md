## Discussion (GEB revision)

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
