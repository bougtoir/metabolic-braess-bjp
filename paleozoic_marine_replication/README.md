# Paleozoic Marine Replication of the Fossil Spatial-Bias Protocol

Strict conceptual and computational replication of
`dinosaur_migration_foodweb/methodological_beta_bias` on Paleozoic
marine occurrences from the Paleobiology Database (PBDB).

Primary question (spec): does the Paleozoic marine fossil record
reproduce the qualitative distortions found in the dinosaur system
when the observable taxonomic pool, sampling intensity, and temporal
aggregation are perturbed? Direction and functional form — not effect
size — are the replication targets.

## Pipeline

| step | script | output |
|------|--------|--------|
| fetch PBDB (6 clades, Cambrian–Permian, marine) | `00_fetch_pbdb.py` | `data/raw/*.json`, `data/processed/occs_*.csv`, `provenance.jsonl` |
| inventory + feasibility | `01_inventory.py` | `data_inventory.csv`, `feasibility_by_stage.csv` |
| harmonise bins/units | `02_harmonize.py` | `harmonized_occurrences.csv`, `time_bins.csv`, `dataset_summary.csv` |
| core beta + distance decay | `03_core_beta.py` | `core_beta_reference.csv` |
| pool perturbation | `04_pool_perturbation.py` | `pool_perturbation_replicates.csv` |
| sampling x pool factorial | `05_sampling_factorial.py` | `sampling_factorial_replicates.csv` |
| temporal aggregation | `06_temporal_aggregation.py` | `temporal_aggregation.csv` |
| cross-clade + export | `07_cross_clade_export.py` | `cross_system_export.csv`, `cross_clade_summary.csv` |
| figures F1–F6 | `08_figures.py` | `results/figures/*.png` |
| manuscript values + stop rule | `09_manuscript_values.py` | `manuscript_values.csv`, `stop_rule_report.md` |
| shared 2-D simulation engine | `10_sim_2d_paleozoic.py` | `sim2d_paleozoic_pool.csv`, `parameter_registry.csv` |

Run order: `make fetch harmonize core perturb export figures values`
(or `make all` after `fetch`/`harmonize`).

## Design invariants (shared with the dinosaur protocol)

- Mean pairwise **Jaccard** dissimilarity on presence/absence
  site x genus matrices (`mean_beta_jaccard`, identical formula).
- Baselga partition: Sorensen = turnover (Simpson) + nestedness.
- Distance decay: OLS slope of pairwise Jaccard vs pairwise distance
  (great-circle km on paleocoordinates here; lattice distance in the
  dinosaur sim — same linear model family).
- Pool perturbation: spatial framework fixed, genus pool contracted to
  {1, 0.75, 0.5, 0.25}; every Monte Carlo replicate stored.
- 2-D simulation: `13_2d_robustness` functions imported unchanged;
  parameter differences logged in `parameter_registry.csv`.
- Predefined thresholds: min 5 sites, min 5 genera, min 10 site pairs
  for decay.

## Temporal schemes

stage (PBDB 'age' level), 2-stage pairs, and 5/10/20 Myr absolute bins
anchored at the Cambrian base (538.8 Ma).

## Reproduce

```
cd analysis
python3 00_fetch_pbdb.py   # ~300k occurrences, requires network
python3 01_inventory.py && python3 02_harmonize.py
python3 03_core_beta.py
python3 04_pool_perturbation.py && python3 05_sampling_factorial.py
python3 06_temporal_aggregation.py && python3 10_sim_2d_paleozoic.py
python3 07_cross_clade_export.py && python3 08_figures.py
python3 09_manuscript_values.py
```
