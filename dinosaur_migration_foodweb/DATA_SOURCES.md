# Data sources

| Dataset | Source | DOI | License | Contents |
|---|---|---|---|---|
| maidment2024_dryad | Dryad | 10.5061/dryad.6m905qg77 | CC0-1.0 | Morrison Formation tetrapod/dinosaur occurrences with systems tracts, lat/lng, taxonomy; derived diversity tables. PBDB-derived, accessed by authors 2022-12-23; 1397 body-fossil occurrences, 300 collections (vertebrates); dinosaur subset 651 occurrences / 239 collections / 38 genera. |
| maidment2024_zenodo_code | Zenodo | 10.5281/zenodo.10727148 | MIT | R scripts of the published analysis (diversity, collector curves, iNEXT SQS). Provenance only; our pipeline is Python. |

Checksums and access dates are recorded in `metadata/sources.csv`.

## Acquisition notes

- Dryad sits behind an AWS WAF challenge: `urllib`/`curl` are rejected
  (401/403). `src/download/fetch_data.py` drives the session Chrome via
  Playwright CDP (`CDP_URL`, default `http://localhost:29229`).
- Zenodo files download over plain HTTPS.

## Planned (Stage 2+)

- Modern GPS movement datasets for migratory ungulate/predator systems
  (e.g. Movebank) — search and acquisition pending Stage-1 gate.
- PBDB refresh query for updated Morrison occurrences (optional sensitivity).
