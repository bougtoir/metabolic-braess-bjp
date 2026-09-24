# Dinosaur variable map

| Core metric | Implementation | Source table |
|---|---|---|
| M1 Δβ Simpson / Sorensen | `analysis/05_beta_diversity.py` | `dinosaur_migration_foodweb/results/tables/stage1_beta_summary.csv`, `stage1_beta_vs_distance_*.csv` |
| M2 range extent | `analysis/04_spatial_occupancy.py` | `stage1_genus_ranges.csv`, `stage1_range_summary.csv`, `stage1_grid_occupancy.csv` |
| M3 distance decay | `analysis/05_beta_diversity.py` (Mantel) | `stage1_beta_summary.csv` |
| M4 temporal lag | not natively defined (pooled formation window); interval sensitivity = `stage1b_E_intervals.csv` | `stage1b_E_intervals.csv` |
| M5 sampling-pool sensitivity | `analysis/06_sampling_bias.py` | `stage1_sampling_sensitivity.csv` |
| M6 time-aggregation | Stage 1b interval analysis | `stage1b_E_intervals.csv` |
| M7 nulls | Stage 1b A/B/G + Nemegt preregistered validation | `stage1b_*`, `nemegt_*.csv` |
| M8 observation bias | taphonomic diagnostics on Nemegt; quarry exclusions | `nemegt_taph_*.csv`, `stage1_audit.csv` |
| M9 robustness class | Stage 1c outcome A–D | `results/stage1c_nemegt_validation.md` (D) |
