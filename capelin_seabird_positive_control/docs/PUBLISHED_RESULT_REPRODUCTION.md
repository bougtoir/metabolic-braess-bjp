# PUBLISHED_RESULT_REPRODUCTION — Davoren et al. 2024 (J Anim Ecol)

Dataset: Dryad doi:10.5061/dryad.jq2bvq8k8 (SHA-256 verified).

## Target result 1 — bird abundance peaks near first day of spawning

- Published: within years, seabird abundance peaked near the first day of
  capelin spawning (DiffSpawn ≈ 0), not with contemporaneous biomass.
- Reproduced: pooled quadratic `log1p(birds/bin) ~ tau + tau^2` has vertex at
  **tau = −2.7 days** (coefficients −0.0042, −0.00078). Peak essentially at
  spawn onset.
- Direction agreement: **yes**. Effect-size agreement: qualitative (vertex
  position), not numeric — the paper used per-species GLMMs not fully
  specified in the archived data alone.
- **Classification: CLOSE.**

## Target result 2 — biomass pulse 5–619× (mean 146 ± 59)

- Our window-based estimates depend on the baseline convention:
  - mean(tau 0..+3) / mean(tau −14..−1): 0.2–13.8× (7 computable years)
  - peak post-onset / pre-arrival (tau ≤ −14) baseline: mean ~322×, range
    0.02–2795× (2010 dominates)
- Both confirm a large prey pulse in most years; the exact published range is
  not reproduced — the paper's baseline convention (pre-arrival biomass near
  zero, peak shoal metrics) differs from windowed means.
- **Classification: DIRECTIONALLY CONSISTENT** (pulse exists and is large in
  peak-vs-baseline terms; magnitude not exactly reproduced).

## Target result 3 — across-year response magnitude vs pulse magnitude/phenology

Not attempted quantitatively (would require the paper's full model spec);
directional check only. Recorded as a residual discrepancy.

## Overall reproduction classification: DIRECTIONALLY CONSISTENT

Unavoidable discrepancies: the paper's exact GLMM specification (families,
offsets, covariates) is not archived with the data; weekly surveys limit
event-window granularity (0–3 surveys per window per year).
