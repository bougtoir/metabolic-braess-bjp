PY ?= python3

.PHONY: all data audit clean beta sampling aggregation null report

data:
	$(PY) src/fetch_pbdb_cenozoic.py

pipeline: audit clean beta sampling aggregation null

audit:
	$(PY) analysis/01_audit.py

clean:
	$(PY) analysis/02_clean.py

beta:
	$(PY) analysis/03_beta_diversity.py

sampling:
	$(PY) analysis/04_sampling_bias.py

aggregation:
	$(PY) analysis/05_aggregation.py

null:
	$(PY) analysis/06_pool_null.py

all: pipeline
