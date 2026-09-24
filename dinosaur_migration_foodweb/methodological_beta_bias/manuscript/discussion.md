# Discussion

## Two symmetric methodological failures

Our results frame a paired problem. First, a **false positive**: even
with Δβ_true = 0, structural differences between guilds generated
apparent contrasts — a realistic four-taxon predator pool produced
bias ≈ −0.17, and the most extreme two-taxon pool (an explicitly
extreme scenario) reached ≈ −0.41. Second, a **false negative**:
temporal pooling attenuated observed contrasts toward zero regardless
of whether the underlying contrast was structural or ecological.
Fossil assemblage construction can therefore both *create* and *erase*
apparent ecological spatial structure. Neither direction of distortion
requires any biological difference between the guilds.

## Gamma-diversity imbalance

Low-richness guilds appear artificially homogeneous because each
pairwise comparison draws from a smaller, overlapping subset of the
regional pool. This is not a subtle effect: gamma asymmetry alone was
the largest single-bias term in our grid and generated apparent
contrasts as large as the raw Morrison signal. Pool-size-matched nulls
are therefore a minimal requirement before interpreting any guild
contrast — in Morrison, the observed Δβ fell *inside* the
gamma-matched null interval, meaning unequal pools alone predict much
of the magnitude.

## Dominant taxa

A single high-occupancy taxon compresses within-guild turnover because
it contributes shared presences to most pairwise comparisons. At
Allosaurus-like prevalence (p_D ≈ 0.46–0.5) the effect was ≈ −0.07 —
small relative to gamma imbalance but non-negligible, and growing to
≈ −0.21 under near-ubiquitous dominance. Leave-one-dominant-taxon
analysis is the direct empirical check; in Morrison it alone collapsed
Δβ from −0.550 to −0.020.

## Taxonomic resolution

Genus-level pooling merges geographically partitioned species, so
apparent continuity increases mechanically with lumping (B_lumping up
to +0.099 at k = 6 in simulation; Morrison genus → species
resolution attenuated Δβ from −0.550 to −0.322). The sign convention
matters: lumping here *increased apparent continuity* (lowered within-
guild β), it did not increase beta diversity. Fossil analyses that can
only be run at coarse taxonomic resolution inherit this bias by
construction.

## Temporal averaging and sampling asymmetry

Union-pooling across time slices inflates within-bin occupancy and
drives Δβ_obs → 0 — a false-negative mechanism distinct from the
false positives above. Asymmetric sampling produced smaller effects
within our parameterization (≈ −0.024 at 8-fold asymmetry), but this
ranking is parameter-dependent; where sampling covaries with
environment and guild jointly, larger effects remain plausible.

## Factorial interaction

Because γ, dominance, lumping and sampling interact non-additively,
single-bias corrections cannot be chained into a total correction. The
factorial map delimits the joint region in which apparent contrasts
are guaranteed artefacts — in its extreme corner, every replicate
produced a false difference.

## The Morrison worked example

Morrison functions in this paper as a methodological demonstration,
not a biological discovery. An initially compelling ecological signal
(Δβ = −0.550) was progressively attenuated by structural corrections:
pool-matched nulls absorbed much of the magnitude, dominant-taxon
removal collapsed it (−0.020), species resolution left −0.322, and
after stratigraphic-duration and occurrence adjustment Allosaurus was
not geographically exceptional (extent residual −36.6 km, z = −0.16).
We do not claim the ecological interpretation was *wrong* — rather,
the structural explanation became sufficient, and biological
exceptionalism was no longer required to account for the pattern.

## Nemegt comparator

The identical pipeline on Nemegt — a system with the reverse
guild-size asymmetry — gave Δβ = +0.094 (−0.079, +0.300): the
Morrison direction is not universal. This bounds the generality of
any guild-continuity claim independent of the bias decomposition.

## Presence-model status

The collection-covariate model of Allosaurus presence is exploratory:
the unpenalized fit (pseudo-R² = 0.46) showed quasi-separation and
non-convergence; an L2-regularized logistic refit converged and gave
pseudo-R² = 0.34 — the same qualitative conclusion that collection
structure carries substantial presence information. Neither estimate
enters the inferential chain.

## Limitations

(i) The simulator is one-dimensional with contiguous ranges; reported
magnitudes demonstrate sufficiency of the biases, not calibrated
values for real palaeolandscapes. (ii) The additive decomposition is a
conceptual scaffold, not an estimable partition. (iii) Species-level
Morrison results depend on the subset with resolved identifications.
(iv) Sampling-asymmetry conclusions are bounded by the explored
parameter range. (v) Simulations establish ground truth only within
simulated scenarios; empirical analyses demonstrate plausibility and
attenuation, not exact causal partitioning.

## A practical workflow

Before interpreting fossil guild-level beta diversity as evidence of
differential mobility, habitat breadth or spatial connectivity:

1. compare gamma diversity across guilds;
2. run pool-size-matched nulls;
3. inspect dominance structure and run leave-one-dominant-taxon
   analyses;
4. test taxonomic-resolution sensitivity;
5. reduce temporal averaging where data permit;
6. assess preservation and collection structure;
7. only then interpret ecologically.

Strong guild contrasts that survive this sequence are candidates for
ecological interpretation; those that collapse, like Morrison's,
should be reported as structural-bias case studies — which we argue
are themselves publishable, because they mark exactly where the fossil
record's architecture, not its ecology, is doing the work.
