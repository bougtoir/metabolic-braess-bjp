# Results

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
