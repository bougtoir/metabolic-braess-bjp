# Results skeleton

Numbers below must be regenerated from `results/manuscript_values.csv`
- no value may be hard-coded.

1. Data inventory. N occurrences across 6 clades, N collections, N
   genera; >97% of occurrences carry rotated paleocoordinates.
   (`data_inventory.csv`, values `n_occurrences_total`,
   `n_collections_total`, `n_genera_*`).

2. Feasibility. Eligible stage-level datasets per clade range 91-138
   (`feasibility_by_stage.csv`, `dataset_summary.csv`).

3. Reference beta/decay. `core_beta_reference.csv`.

4. Pool-size perturbation. Eligible datasets: stage =
   `n_eligible_datasets_pool_stage`, 10-Myr =
   `n_eligible_datasets_pool_10myr`. Mean Bias_beta at
   pool_fraction=0.5 =
   `bias_beta_pool50_mean`; proportion of replicates with reduced beta
   = 1 - `bias_beta_pool50_prop_positive`. Decay-slope bias =
   `bias_decay_pool50_mean`. Direction is consistent across all six
   clades (`cross_clade_summary.csv`).

5. Sampling x pool interaction. `sampling_factorial_replicates.csv`;
   mean beta across the factorial grid spans
   [`beta_full_grid_min`, `beta_full_grid_max`].

6. Temporal aggregation. Mean Bias_time for Jaccard beta =
   `bias_time_stage_to_stage2_mean` (stage->2-stage) and
   `bias_time_5_to_10myr_mean` (5->10 Myr).

7. Cross-clade replication. F6 / `cross_clade_summary.csv` — sign of
   Bias_beta is uniform across clades; magnitudes are heterogeneous.

8. 2-D simulation. `sim2d_paleozoic_pool.csv` — pool contraction in the
   shared engine reproduces the same directional biases.
