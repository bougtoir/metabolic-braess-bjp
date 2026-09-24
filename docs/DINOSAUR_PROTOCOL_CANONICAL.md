# Dinosaur protocol — canonical reference

Extracted verbatim from `dinosaur_migration_foodweb/` at merge into
`devin/1789995032-core-protocol-refactor`. This document is the Tier-1
reference: Cenozoic and Quaternary adapters must match it point-for-point or
log a deviation in their `PROTOCOL_DEVIATIONS.md`.

| Element | Canonical choice |
|---|---|
| Data source | Maidment et al. 2024 Dryad package `10.5061/dryad.6m905qg77` (PBDB-derived); Nemegt validation via PBDB 1.2 API |
| Taxonomic scope | Dinosauria, genus resolution; indeterminate rows flagged `resolution='indeterminate'` and excluded from matrices |
| Trophic guilds | herbivore = Sauropoda + Ornithischia; predator = Theropoda (PBDB `class` field) |
| Primary endpoint | Δβ = mean pairwise Simpson turnover(predator) − mean pairwise Simpson turnover(herbivore) |
| Spatial unit | collection (quarry/locality aggregate), centroid = median lng/lat |
| Temporal unit | Morrison Formation assemblage (single pooled window); interval-level sensitivity in Stage 1b |
| Distance | great-circle km (haversine, R=6371) between collection centroids |
| β(d) curve | 100 km bins, mean pairwise dissimilarity per bin |
| Uncertainty | collection bootstrap, rows resampled with replacement, n=999; Mantel Spearman, 9999 permutations |
| Sampling-pool tests | (B) drop collections >p95 occurrence count; (C) drop collections <2 genera; (D) equalize guild collection counts (999 reps); (E) 1° spatial thinning (999 reps) |
| Time-aggregation test | Stage 1b `stage1b_E_intervals` (Kimmeridgian/Tithonian bins) — sensitivity analysis |
| Distance-decay | Mantel r per guild + β(d) curves (Simpson primary, Sorensen sensitivity) |
| Null models | Stage 1b: taxon-pool size-matched null (`A`), frequency-matched null (`B`), dominant-taxon removal (`C`), systems-tract (`D`), interval (`E`), resolution (`F`), metric scale (`G`) |
| Simulation | `simulation/` baseline = 2-D ecological + observation-process model (modular per Core Protocol §17) |
| Robustness | preregistered validation on Nemegt (`VALIDATION_HYPOTHESES.md`); outcome classes A–D |
| Manuscript figures | `figures/main/figure2_morrison_beta_diversity.png` (map + β(d) curves) |
| Key values | Δβ_Simpson = −0.543 [−0.623, −0.452]; P(Δ>0)=0; Mantel r≈0 both guilds; Nemegt Δβ_full = +0.094 [−0.079, +0.300] (Outcome D) |

## Reproduce

```bash
cd dinosaur_migration_foodweb
pip install -r requirements.txt
python3 src/download/fetch_data.py   # Dryad needs Chrome/CDP; committed processed data suffices for analyses
make stage1                          # 01..06
python3 analysis/99_stage1_report.py # regenerate report from tables
```

## Frozen results

- Stage 1a freeze commit `4f4b6372` → `results/stage1_original_hypothesis_report.md`
- Stage 1c preregistration commit `e9acfdad` → `results/stage1c_nemegt_validation.md`

Regression baselines for refactoring are in `tests/regression/` (repo root).
No numeric output of this pipeline may change under refactoring; any change
must land as an explicitly new analysis.
