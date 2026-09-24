# Integration-readiness report

## Cross-system export

`results/tables/cross_system_export.csv` contains exactly the shared
schema columns:

system, realm, geological_period, time_bin, time_start_ma,
time_end_ma, duration_myr, clade, taxonomic_level,
spatial_resolution, n_sites, n_collections, n_occurrences, gamma,
median_alpha, pool_fraction, sampling_fraction,
temporal_aggregation, beta_metric, beta_value, distance_decay_model,
distance_decay_slope, replicate, analysis_version

No Paleozoic-specific column is required to interpret the primary
experiment; Paleozoic-only fields (beta_reference, decay_reference,
bias_beta, bias_decay per replicate) live in
`paleozoic_extended.csv`. The export is directly concatenable with a
dinosaur export written to the same schema (`metrics_row` in
`analysis/03_core_beta.py` is the canonical constructor).

## Controlled vocabulary

- system = `paleozoic_marine`; realm = `marine`
- taxonomic_level = `genus`
- temporal_aggregation = `stage`, `stage2`, `5myr`, `10myr`, `20myr`
- beta_metric = `jaccard`, `sorensen`, `turnover`, `nestedness`
- distance_decay_model = `ols_jaccard_km`
- analysis_version = `paleo_v1`

## Hierarchical-model hooks

The export carries `pool_fraction`, `sampling_fraction`,
`temporal_aggregation`, `clade` and `system`, so the planned model
`Bias ~ pool_ratio + sampling + aggregation + interactions +
(1|system) + (1|clade)` can be fitted on concatenated exports once
the dinosaur export is written to the same schema.

## Provenance

- PBDB query URLs + download timestamps: `data/raw/provenance.jsonl`
- Random seeds: `RNG_SEED = 20260921` (all scripts)
- Parameter registry: `results/tables/parameter_registry.csv`
- Time-bin realisations: `results/tables/time_bins.csv`
- Software: Python 3.10, numpy/pandas/matplotlib (see Makefile).
