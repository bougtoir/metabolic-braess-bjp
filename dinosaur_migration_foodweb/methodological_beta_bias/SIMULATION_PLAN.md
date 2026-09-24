# Simulation plan

Goal: map where observed guild contrasts diverge from known truth,
especially sign-reversal and false-difference regions.

## Community generator

Localities on a 1-D (or 2-D) spatial axis. Each taxon occupies localities
via a spatial occurrence process with a range parameter (spatial breadth)
and prevalence parameter. Guilds P (predator) and H (herbivore) are
generated with true guild turnover β_true set by shared-vs-endemic taxon
structure; Δβ_true = β_P − β_H is known by construction.

Variable factors (factorial where indicated):

- true ecological beta diversity β_true
- gamma diversity (taxon pool size per guild)
- dominant-taxon prevalence p_D ∈ [0.1, 0.9]
- taxonomic lumping rate (fraction of species collapsed into a genus)
- stratigraphic duration / temporal bin width
- sampling intensity (collections per locality, occurrence detection prob)
- preservation heterogeneity (environment-linked sampling)

## Outputs

For each scenario × replicate: Δβ_obs, Bias = Δβ_obs − Δβ_true, sign flag.

- 01 gamma: sweep H/P pool-size ratio.
- 02 dominance: sweep p_D at fixed turnover.
- 03 lumping: collapse geographically-partitioned species into one genus;
  report B_lumping = β_species − β_genus.
- 04 temporal: taxa occupy regions in different time slices; aggregate
  into wider bins; Δβ vs bin width.
- 05 sampling: heterogeneous collection intensity and detection
  probability; guild-specific sampling.
- 06 factorial: grid over (gamma ratio, p_D, lumping rate) → heatmap of
  Bias and sign-reversal indicator (Figure 3).

Calibration: parameter ranges anchored to Morrison empirics (γ_H ≈ 26,
γ_P ≈ 12; p_D(Allosaurus) ≈ 0.46 of collections; observed Δβ = −0.55).
