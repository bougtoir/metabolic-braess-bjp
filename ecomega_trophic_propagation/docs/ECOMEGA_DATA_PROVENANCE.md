# ECOMEGA_DATA_PROVENANCE

## Dataset selected for Task 4

Applied California Current Ecosystem Studies (ACCESS), distributed via the
California Ocean Observing Systems (CalOOS/CeNCOOS) data portal.

- Portal: https://data.caloos.org/#module-metadata/f712b555-d8ff-4345-83e4-9de2a337c7a4
- Host program: Point Blue Conservation Science + Greater Farallones & Cordell
  Bank National Marine Sanctuaries (NOAA).
- License/access: public open download via GeoServer WFS
  (https://data.axds.co/gs/wfs). No formal DOI per layer; citation suggested by
  the portal (Elliott & Jahncke 2023 for CTD).
- Region: northern/central California shelf-slope, ~35.35–38.60N,
  123.77–121.29W.

### Layers downloaded (raw files in data/raw/access/)

| layer | WFS typeName | coverage | format | key columns |
|---|---|---|---|---|
| seabird | cencoos:bird_density_2004_2024 | 2004-05-20 – 2024-09-25 | Darwin Core | eventID, eventDate, lat/lon, vernacularName, count_per_km2 |
| non-bird (mammals etc.) | cencoos:others_density_2004_2024 | same | Darwin Core | eventID, eventDate, lat/lon, scientificName, count_per_km |
| zooplankton | cencoos:access_zooplankton_2024 | 2004-07-26 – 2024-09-24 | Darwin Core | eventID, eventDate, lat/lon, scientificName, count_per_m3, gear |
| euphausiid | cencoos:euphasiid_geoserver | 2004–2017+ | custom | event_id, eventDate, lat/lon, count_per_10m3 |
| CTD | ism-cencoos-access-ctd-* (per-station, erddap.sensors.axds.co) | 2004-2024 | profile | chl-a, temp, salinity per cast |

Note: `cencoos:bird` / `cencoos:mammal` layers on the same server are COASST
beached-carcass surveys — NOT ACCESS — and were explicitly excluded.

### Environmental forcing (independent of animals)

- Bakun upwelling index, 39N 125W, 6-hourly: NOAA CoastWatch ERDDAP
  `erdUI396hr` (wind-derived Ekman transport; m3/s per 100 m coastline).
- SST: NOAA OISST v2.1 daily 0.25° (`ncdcOisst21Agg_LonPM180`), ACCESS box.
- Geostrophic currents available via `nesdisSSH1day` (not used for advection:
  survey abundances, not tracks).

### Spatial/temporal compatibility

All ACCESS layers share eventID/eventDate within cruises; matching is
performed at tow↔sighting level with tolerance grid (6/12/24/48 h ×
5/10/20 km). Raw layer granularity: sighting point (birds/mammals), net tow
(zooplankton), station cast (CTD). Datasets were not merged before tolerance
sensitivity was computed (metadata/matching_sensitivity.csv).

### Known gaps

- No acoustic forage-fish layer in ACCESS → Layer 2 "forage fish" is absent;
  the tested chain is environment → zooplankton/krill → seabirds/mammals.
- ACCESS surveys are Apr–Oct, 3–4 cruises/yr; winter unsampled.
- Predator measurements are strip-transect densities, not tracks: these are
  *aggregation responses*, not movement measurements (Task-4 §14 wording).
