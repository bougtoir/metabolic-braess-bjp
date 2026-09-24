# Analysis plan — methodological_beta_bias

## Empirical decomposition (Morrison worked example)

`analysis/07_morrison_empirical_decomposition.py` produces the sequential
attenuation table — each step a row with Δβ and 95% CI:

1. naive guild Δβ (genus, Jaccard);
2. gamma-matched null position;
3. frequency-matched null position;
4. −Allosaurus;
5. species resolution;
6. duration + occurrence-count adjustment (extent residual);
7. sampling/preservation model contribution.

## Simulations

`analysis/01`–`06`: synthetic fossil communities with known Δβ_true; the
output of every scenario is Bias = Δβ_obs − Δβ_true and sign classification
(preserved / attenuated / reversed / false-difference-from-zero).

## External comparator

`analysis/08_optional_external_validation.py` applies the same diagnostic
workflow to the Nemegt PBDB pull (already acquired with provenance) as a
*comparator* — not as a confirmatory replication.

## Figures (per plan)

- fig1: narrative emergence and disappearance under correction;
- fig2: Morrison sequential attenuation waterfall;
- fig3: simulation heatmap of sign-reversal / false-positive regions;
- fig4: taxonomic-lumping effect;
- fig5: temporal averaging + dominant-taxon effects.
