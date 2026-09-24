# STATUS

## Completed
- Repo scaffold: docs, data dirs, Makefile, requirements, provenance tracking.
- Data acquisition: Maidment et al. 2024 Dryad package (9 files, sha256
  recorded in metadata/sources.csv) + Zenodo R code (4 files). Dryad requires
  a real browser (AWS WAF); fetch script uses Playwright/CDP.
- Stage 1 pipeline 01–06 run end-to-end on the dinosaur subset
  (651 occurrences, 239 collections, 38 genera; 26 herbivore / 12 predator
  genera; 206 herbivore / 114 predator collections).
- Figure 2 (map + beta-vs-distance curves) in figures/main/.
- results/stage1_report.md generated from output tables.

## Key numerical results
- Delta-beta (Simpson) = -0.62, bootstrap 95% CI [-0.61, -0.48],
  P(Δ>0) = 0. Predator turnover is LOWER than herbivore turnover.
- Mantel r ~ 0 for both guilds (no distance decay detected).
- Result robust to dominant-quarry exclusion, singleton exclusion,
  equalized collections, and 1-degree spatial thinning.

## Interpretation
- H1 (beta_P > beta_H) is contradicted in its literal form, confounded by
  gamma-pool asymmetry (predators: 12 genera, ~70% Allosaurus).
- Alternative reading: ubiquitous Allosaurus is compatible with predators
  tracking mobile prey subsidies. Needs Stage-2/4 machinery to adjudicate.

## Failed approaches
- Plain HTTP download of Dryad files (AWS WAF 401/403) -> switched to
  Playwright-driven Chrome downloads.

## Stage structure (post-falsification protocol)
- Stage 1a (frozen): original confirmatory H1 falsified. Freeze commit:
  4f4b637287751c66ff8a53613792c29c2e1309e1
  (results/stage1_original_hypothesis_report.md)
- Stage 1b: exploratory characterization of the reverse signal
  (results/stage1b_exploratory_reverse_signal.md)
- Stage 1c: independent confirmatory validation under preregistered
  hypothesis (VALIDATION_HYPOTHESES.md) — locked before validation data
  are analysed
- Stage 2: modern movement-ecology validation (revised; does not assume
  prey are the more mobile guild)

## Unresolved / next
- Stage 1c Nemegt: **NO REPLICATION (Outcome D)** — Δβ_full = +0.094
  (95% CI [-0.079, +0.300]), preregistered commit e9acfdad. Report:
  results/stage1c_nemegt_validation.md. Hell Creek not analysed per
  locked rule (only on Outcome A/B).
- Stage 2 (modern movement ecology) gated on the dominant-predator
  pattern replicating — currently not triggered.
- Bootstrap bugfix post-freeze: collection bootstrap now resamples
  incidence-matrix rows with replacement (was `isin` collapse); overall
  Δβ estimand = mean pairwise difference (Δβ_Simpson = -0.543,
  CI [-0.623, -0.452]). Falsification verdict unchanged.
