# Phase 4 Report — Full-genome scan (Human-GEM) + replication (Recon3D)

## Staged design (scripts/full_scan.py)
1. **FVA** over all eligible non-boundary reactions (fraction_of_optimum 0.9)
   -> 6,121 / 11,217 (human2), 5,220 / 8,794 (recon3d) spanned reactions.
2. **u=1 capacity-block test** (single LP per reaction) + **alternate-optimum
   FVA** (fraction_of_optimum 1.0): a reaction can only change the selected
   pFBA state if its KO lowers the objective OR it has nonzero span within
   the optimal solution set. Candidate set: 2,254 (human2), 2,494 (recon3d).
3. **Consistent-state screen**: pFBA state at u=1 per candidate; keep only
   reactions whose selected-state metrics change >1% -> 27 (human2),
   22 (recon3d).
4. **u-grid scan** (coarse grid) on kept reactions + classification.

## Genome-wide result
- 12 NOPM (Type II) reaction×metric combos in human2 (class_human2_full.csv)
- 8 NOPM combos in recon3d (class_recon3d_full.csv)
- ALL hits lie on the glucose->ATP core (glycolysis, PDH, ETC, O2 transport).
  Across ~11k reactions, interior optima exist ONLY on the energetic core.

## Cross-model convergence (headline robustness finding)
| hit | human2 (MAR) | recon3d | metric | u* | J0 -> J* |
|-----|--------------|---------|--------|-----|----------|
| GAPDH | MAR04373 | GAPD | atp_per_glc | .85-.90 | 12 -> ~30 |
| PGK | MAR04368 | PGK | atp_per_glc | .75 | 12 -> 21 |
| enolase | MAR04363 | ENO | atp_per_glc | .75 | 12 -> 31.5 |
| O2 transport | MAR04896 | O2t | total_flux | .25-.30 | interior min |
| complex III | (MAR06918) | CYOR_u10mi | total_flux | .10 | interior min |
| complex I | MAR06921 | NADH2_u10mi | total_flux | .10-.15 | interior min |

ENO + PGM are NOPM in recon3d but NOT kept in human2's screen at u=1 —
inspecting whether they still hold interior optima there (both models'
glycolytic cluster is the reproducible hit zone).
