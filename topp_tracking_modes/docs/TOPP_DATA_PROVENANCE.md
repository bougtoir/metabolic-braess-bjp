# TOPP Data Provenance — Task 5

## Tagging data
- **Source**: NOAA ERDDAP (oceanview.pfeg.noaa.gov) tabledap dataset
  `gtoppAT` — "TOPP Historical Tagged Animals" (Tagging of Pacific
  Predators program, Block et al. 2011, Nature doi:10.1038/nature10082).
- **Access**: public ERDDAP, no authentication. Downloaded as headerless CSV
  (`csv0`) with fields commonName, project, toppID, serialNumber,
  yearDeployed, isDrifter, time, latitude, longitude.
- **Size**: 579,485 raw fixes; lon stored 0–360.
- **License/terms**: NOAA ERDDAP open access; cite Block et al. 2011 and the
  TOPP program.
- **QC in this pipeline**: drifters excluded (`isDrifter` false); daily median
  position per animal; `disp_km` computed only between consecutive days
  (no steps across temporal gaps); CCS analysis window 30–48°N,
  235–243°E; CCS-relevant animals = ≥30 daily positions inside box →
  287 animals, 12 species.

## Environmental fields (all NOAA ERDDAP, public)
| Field | Dataset id | Resolution | Notes |
|---|---|---|---|
| Bakun coastal upwelling index | `erdUI33..45N6hr` | 6-hourly, 5 stations (33–45°N) | event definition source |
| SST | `ncdcOisst21Agg_LonPM180` | daily, 0.25° (stride 4 used) | anomaly vs CCS box mean |
| Chlorophyll-a (INDIRECT prey proxy) | `erdSW2018chla8day` (SeaWiFS) | 8-day composite, ~4 km | 2003–2009 coverage; mission ends Dec 2009 |
| Geostrophic currents | `erdTAgeo1day` (TOPEX/AVISO) | ~6-day steps, 1/3° | advection correction only |

## Prey layer honesty
No co-located direct prey measurement exists inside TOPP tracks. Chlorophyll-a
is used as an **INDIRECT** prey-availability proxy (primary production →
forage base). All models treat `chl` as INDIRECT; results must not be
described as direct prey tracking.

## Component compatibility
Only `gtoppAT` is used — the OBIS-SEAMAP TOPP SSM summary dataset
(doi:10.82144/d127533f) requires login and was NOT merged; per the task spec,
TOPP components were not merged since compatibility could not be verified.

## Reproducibility
`scripts/01_download.py` re-downloads every layer (no auth). Raw CSVs are
gitignored; processed parquet under `data/processed/`.
