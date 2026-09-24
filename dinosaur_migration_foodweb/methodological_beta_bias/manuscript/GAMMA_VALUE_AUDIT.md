# Gamma-headline value audit

Searched the repository for `-0.41`, `-0.17`, `pool 2`, `pool 4`,
`gamma`, `false contrast`, `100%`. All manuscript-level references
verified against `results/tables/sim01_gamma_bias.csv`
(200 replicates/cell, seed 20260922).

| location | current_text | expected_value | status | action |
|---|---|---|---|---|
| manuscript/results.md Results 1 | "pool of 2 taxa … −0.412; at 4 predator taxa Δβ_obs = −0.170" | pool2 −0.412, pool4 −0.170 | OK | keep |
| manuscript/methods.md | sweeps only, no values | — | OK | none |
| manuscript/figure_captions.md Fig.2a | describes sweep, no pool-specific values | — | OK | none |
| results/manuscript_values.csv | sim01_bias_p2 = −0.4125; sim01_bias_p4 = −0.1704 | same | OK | none |
| results/methodological_project_report.md | table shows n_pred=2 → −0.412 (auto-generated) | — | OK | none |
| OPEN_STATISTICAL_ISSUES.md #1 | documents the protocol–run discrepancy | — | OK | resolved |
| figures/fig2a (fig1/3 panels) | no pool-specific text labels | — | OK | none |

**No stale "pool 4 = −0.41" statements exist anywhere.** The draft and
all tables already attribute −0.412 to pool 2 and −0.170 to pool 4.

Reporting hierarchy adopted (per directive):
- Main representative example: pool 4 → Bias ≈ −0.17.
- Extreme scenario, explicitly labelled: pool 2 → Bias ≈ −0.41.
