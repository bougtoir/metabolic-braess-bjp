# Numerical audit — every manuscript number vs source output

All values verified directly against `results/tables/*.csv` on
2026-09-20. Registry: `results/manuscript_values.csv` (value_id →
source_script → source_output → figure_panel → manuscript_location).

| # | manuscript value | value_id | verified | unit | source_output |
|---|---|---|---|---|---|
| 1 | gamma pool2 bias −0.412 (−0.443, −0.398) | sim01_bias_p2 | ✓ | Δβ | sim01_gamma_bias.csv |
| 2 | gamma pool4 bias −0.170 (−0.187, −0.157) | sim01_bias_p4 | ✓ | Δβ | sim01_gamma_bias.csv |
| 3 | false-contrast rate 100% | sim01_falsecontrast_p4 | ✓ (see note A) | proportion | sim01_gamma_bias.csv |
| 4 | dominance p_D=0.5 (Allosaurus-like) −0.071 | sim02_bias_pD0.5_allolike | ✓ | Δβ | sim02_dominance_bias.csv |
| 5 | dominance p_D=0.9 −0.210 | sim02_bias_pD0.9 | ✓ | Δβ | sim02_dominance_bias.csv |
| 6 | lumping k=6 B_lumping +0.099 | sim03_B_lumping_k6 | ✓ | β units | sim03_taxonomic_lumping.csv |
| 7 | lumping Δβ shift k=6 −0.099 | sim03_shift_..._k6 | ✓ | Δβ | sim03_taxonomic_lumping.csv |
| 8 | temporal width1 −0.031 / width8 −0.001 | sim04_db_width1/8 | ✓ | Δβ | sim04_temporal_averaging.csv |
| 9 | sampling 8× −0.024 (range −0.024, −0.023) | sim05_bias_range_* | ✓ | Δβ | sim05_sampling_bias.csv |
| 10 | factorial max |bias| −0.910 cell | sim06_max_abs_bias | ✓ | Δβ | sim06_factorial.csv |
| 11 | factorial max false-difference rate 100% | sim06_false_difference_max | ✓ | proportion | sim06_factorial.csv |
| 12 | Morrison Δβ genus −0.550 (−0.630, −0.457) | emp_db_naive | ✓ | Δβ | morrison_decomposition.csv |
| 13 | Morrison Δβ species −0.322 (−0.426, −0.234) | emp_db_species | ✓ | Δβ | morrison_decomposition.csv |
| 14 | Δβ excl. Allosaurus −0.020 (−0.128, +0.024) | emp_db_minus_allosaurus | ✓ | Δβ | morrison_decomposition.csv |
| 15 | Allosaurus extent residual −36.6 km | — (in dec note, step 6) | ✓ | km | allo_extent_model.csv |
| 16 | extent z = −0.16 | emp_allo_extent_z | ✓ | z | morrison_decomposition.csv |
| 17 | pseudo-R² = 0.46 (unpenalized, non-converged) | emp_presence_pseudoR2 | ✓ | pseudo-R² | allo_presence_logit.csv |
| 18 | pseudo-R² = 0.34 penalized (L2, C=1, converged) | emp_presence_pseudoR2_penalized | ✓ | pseudo-R² | presence_model_robustness.csv |
| 19 | Nemegt Δβ +0.094 (−0.079, +0.300) | nem_db_full | ✓ | Δβ | nemegt_comparator_decomposition.csv |

**Note A — "false contrast 100%" definition.** Simulation 01:
200 replicates per predator-pool size, seed 20260922; a "false
contrast" is defined as |Δβ_obs| > 0.1 on the mean-pairwise Jaccard
contrast (a magnitude-plus-sign threshold on the point estimate — NOT
a CI or p-value criterion; the replicate distribution itself provides
the interval). The 100% rate holds at predator pools 2 and 4 (and the
all-negative-sign rate holds through pool 20). Reported in Results 1
with this definition stated.

**Note B — temporal-averaging wording.** Simulation 04's per-slice
faunas are drawn with identical guild parameters (Δβ_true = 0 in
expectation); the −0.031 at fine bins is residual gamma-imbalance
bias, not a designed ecological contrast. Temporal pooling attenuates
*any* observed contrast toward zero (and mechanically deflates
per-guild beta via presence-union pooling). Results.md wording revised
accordingly — the "erases true ecological structure" claim is now
framed as: pooling attenuates contrasts whether structural or
ecological, demonstrated here on the bias-driven contrast.
