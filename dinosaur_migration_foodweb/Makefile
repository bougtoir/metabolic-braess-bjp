PY ?= python3

.PHONY: all data stage1 figures clean

data:
	$(PY) src/download/fetch_data.py

stage1:
	$(PY) analysis/01_data_audit.py
	$(PY) analysis/02_occurrence_cleaning.py
	$(PY) analysis/03_taxonomy.py
	$(PY) analysis/04_spatial_occupancy.py
	$(PY) analysis/05_beta_diversity.py
	$(PY) analysis/06_sampling_bias.py

all: stage1

clean:
	rm -f results/tables/*.csv results/diagnostics/*.txt
	rm -f figures/main/*.png figures/extended_data/*.png
