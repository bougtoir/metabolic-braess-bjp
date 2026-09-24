.PHONY: all fetch harmonize core perturb export figures values

all: core perturb export figures values

fetch:
	cd analysis && python3 00_fetch_pbdb.py && python3 01_inventory.py

harmonize:
	cd analysis && python3 02_harmonize.py

core:
	cd analysis && python3 03_core_beta.py

perturb:
	cd analysis && python3 04_pool_perturbation.py && python3 05_sampling_factorial.py && python3 06_temporal_aggregation.py && python3 10_sim_2d_paleozoic.py

export:
	cd analysis && python3 07_cross_clade_export.py

figures:
	cd analysis && python3 08_figures.py

values:
	cd analysis && python3 09_manuscript_values.py
