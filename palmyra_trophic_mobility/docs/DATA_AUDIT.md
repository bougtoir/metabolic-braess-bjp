# DATA_AUDIT — Palmyra multi-species telemetry feasibility

## 1. Source dataset

- **Palmyra Bluewater Research Marine Animal Telemetry Dataset, 2022–2023**
- DOI: https://doi.org/10.24431/rw1k8ez (Research Workspace / DataONE member
  node `urn:node:RW`, base URL `https://dataone.researchworkspace.com/mn`)
- USGS catalog id `USGS:d285a4ff-dec1-4820-8bce-5f3aa3ade139`
- License: US public domain. Related paper: Gilmour et al., *Global Change
  Biology* 2025, doi:10.1111/gcb.70138.
- 88 member objects (~350 MB zipped). Full object list, sizes and MD5
  checksums: `metadata/dataset_inventory.csv` / `metadata/dataone_manifest.json`.
- Raw archives are **not committed**; `scripts/download_data.py` re-downloads
  and MD5-verifies every object.

## 2. Ingested coverage (scripts/01_ingest_tracks.py)

307,049 position fixes across 9 species / 85 individuals
(2022-02-27 – 2023-05-30):

| species | n ind | fixes | span | median tracked days/ind |
|---|---|---|---|---|
| grey reef shark | 6 | 5,300 | 366 d | 187.5 |
| reef manta ray | 4 | 1,795 | 332 d | 194.8 |
| yellowfin tuna | 9 | 2,033 | 179 d | 33.4 |
| blue marlin | 1 | 345 | 70 d | 68.5 |
| melon-headed whale | 8 | 1,215 | 19 d | 10.2 |
| bottlenose dolphin | 5 | 1,176 | 27 d | 15.6 |
| great frigatebird | 7 | 135,316 | 301 d | 37.4 |
| red-footed booby | 31 | 151,531 | 164 d | 2.3 |
| sooty tern | 12 | 8,338 | 19 d | 5.0 |

Not ingested / caveats:

- **Galapagos shark (CARGAL)**: tag never transmitted — legitimately absent.
- `THUALB_2022_12`: Argos-only tag, no usable locations.
- RFBO `pinpoint` files: Lotek PINPOINT gps csv; only `Status == "Valid"` fixes.
- SOTE `pinpoint_24xx`: Argos-GPS store format; corrupt dates filtered to
  2022–2023. Deployment windows June 2022 only.
- Tag heterogeneity is large: birds ~1–5 min fixes; fish/cetaceans ~1–12 h
  (GPE3 most-probable tracks, Argos). Species-day products are therefore
  aggregated per individual first, never pooled as raw fixes.

## 3. QC (scripts/03_qc.py)

Per-record flags: `dup`, `bad_coord`, `flag_speed` (species-appropriate
ceilings: sharks/fish 15 km/h, cetaceans 20, frigatebird/booby 120, tern 80).
Rows are **flagged, not deleted** — downstream scripts exclude `flagged`
but the raw audit trail remains in `data/processed/tracks_qc.csv`.

## 4. Spatial support (scripts/04_spatial.py)

Per individual-day: centroid, radius of gyration, displacement, path length,
distance from Palmyra (5.877°N, 162.078°W). Per species-day: multi-individual
centroid, dispersion, n_individuals, n_fixes. No trajectory averaging without
retaining n.

## 5. Environmental fields (scripts/05_environment.py)

All NOAA CoastWatch ERDDAP, public, no auth — see
`metadata/environmental_products.csv`. Daily region-mean series
(±7° box around Palmyra): chl-a (VIIRS NOAA-20), SST (OISST), SLA +
geostrophic u/v + EKE (NESDIS SSH), concentration-weighted chl centroid and
gradient magnitude. Bathymetry GEBCO 2020 for context.

Limitations discovered:

- `noaacwN20VIIRSchlaDaily` is **not** gap-filled: ~67 % of pixels cloud-masked
  per day (documented via `chl_frac_missing`).
- `erdQAekm1day` Ekman currents are NaN throughout the near-equatorial band —
  **unusable**; advection analysis uses geostrophic u/v instead.
- OSCAR (`jplOscar`) ends 2014 — unusable for 2022–23.

## 6. Event inventory (scripts/06_events.py)

Events defined **exclusively from environmental data** (no circularity):

| def | criterion | raw event-days | independent events @3/7/14 d |
|---|---|---|---|
| A_zscore | \|Δlog10 chl\| z-score > 2 (31-d rolling baseline) | 22 | 15 / 14 / 12 |
| B_percentile | Δlog10 chl beyond 5th/95th pctile | 50 | 31 / 22 / 18 |
| C_front | chl-centroid daily displacement > 95th pctile | 25 | 22 / 18 / 17 |
| D_persistent | A persisting ≥ 2 days | 6 | 6 / 6 / 6 |

Median event duration ≈ 1 day (max 3). Of the 22 B events (7-day separation),
16 have ≥ 2 guilds tracked in the 0–2 d event window — but only ~10 events
(Jun–Nov 2022) have ≥ 2 guilds with ≥ 5 individual-days; post-Nov-2022 events
are covered mainly by shark + manta only.
