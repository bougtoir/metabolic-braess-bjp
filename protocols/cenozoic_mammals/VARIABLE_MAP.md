# Cenozoic mammals variable map

| Core metric | Implementation | Source table |
|---|---|---|
| M1 Δβ Simpson / Sorensen | `cenozoic_mammals/analysis/03_beta_diversity.py` | `cenozoic_mammals/results/tables/beta_summary.csv`, `beta_vs_distance_*.csv` |
| M2 range extent | `analysis/02_clean.py` + `03_beta_diversity.py` | `genus_ranges.csv`, `range_summary.csv` |
| M3 distance decay | Mantel in `03_beta_diversity.py` | `beta_summary.csv` |
| M4 temporal lag | interval lead/lag via aggregation ladder | `aggregation_sensitivity.csv` (secondary) |
| M5 sampling-pool | `analysis/04_sampling_bias.py` | `sampling_sensitivity.csv` |
| M6 time-aggregation | `analysis/05_aggregation.py` (pooled/epoch/subepoch/1 Ma) | `aggregation_sensitivity.csv` |
| M7 nulls | genus-pool size-matched + frequency-matched nulls | `pool_null.csv` |
| M8 observation bias | collection-intensity skew, monodominant Lagerstätten exclusion | `audit.csv`, `sampling_sensitivity.csv` |
| M9 robustness | classification vs dinosaur reference | `beta_summary.csv` + `PROTOCOL_DEVIATIONS.md` |

Mammal-specific traits (body size, hypsodonty, locomotion, browser/grazer)
are **secondary extensions** — none enter the primary analysis.
