PY ?= python3

# Cross-system ecology program targets (see docs/CORE_PROTOCOL_V1.md).
# System targets never silently re-run or overwrite validated analyses;
# `common_metrics` and `synthesis` only read committed result tables.

.PHONY: dinosaur cenozoic quaternary ancient_marine modern_terrestrial modern_marine common_metrics synthesis regression

dinosaur:
	$(MAKE) -C dinosaur_migration_foodweb stage1

cenozoic:
	$(MAKE) -C cenozoic_mammals all

quaternary:
	@echo "quaternary pipeline lands with the parallel session; adapter spec in protocols/quaternary/"

ancient_marine:
	@echo "ancient_marine pipeline lands with the parallel session; adapter spec in protocols/ancient_marine/"

modern_terrestrial:
	$(MAKE) -C phase9 || echo "phase9 requires downloaded data; see phase9/README.md"

modern_marine:
	$(MAKE) -C ecomega_trophic_propagation all
	$(MAKE) -C topp_tracking_modes all
	$(MAKE) -C capelin_seabird_positive_control all
	$(MAKE) -C palmyra_trophic_mobility all

common_metrics:
	$(PY) src/common/export_common_metrics.py

synthesis: common_metrics
	$(PY) src/common/cross_system_comparison.py

regression:
	$(PY) -m pytest tests/regression -q
