# Marine trophic-mobility dataset screen (Task 3)

Discovery and ranking only — no biological model fitting.

- `scripts/search_catalogs.py` — DataCite API queries + logged manual catalog searches
- `scripts/build_candidate_inventory.py` — `metadata/marine_candidate_datasets.csv` (23 candidates)
- `scripts/score_candidates.py` — 20-point screen + penalties -> `outputs/tables/marine_candidate_ranking.csv`
- `docs/TOP10_MARINE_SYSTEMS.md`, `docs/SYSTEM_COMPARISON.md`
