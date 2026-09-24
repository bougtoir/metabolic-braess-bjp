"""Process TOPP tracks: QC, daily positions, mobility metrics, CCS subset.

Outputs:
  data/processed/topp_daily.csv (animal-day median position, CCS only)
  metadata/topp_dataset_inventory.csv
  metadata/topp_species_mobility.csv (median daily displacement OUTSIDE event
    windows -> independent mobility; frozen before response analysis)
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data/raw")

df = pd.read_csv(os.path.join(RAW, "topp_gtoppAT.csv"), header=None,
                 names=["commonName", "project", "toppID", "serialNumber",
                        "yearDeployed", "isDrifter", "time", "latitude",
                        "longitude"], low_memory=False)
df["time"] = pd.to_datetime(df["time"], utc=True)
df = df.rename(columns={"toppID": "animal", "commonName": "species",
                        "latitude": "lat", "longitude": "lon"})

# project: 1=GTOPP (TOPP-designated), 0=partner, 2=TagAGiant, 5=CMRCL
df["project"] = pd.to_numeric(df["project"], errors="coerce")

# QC: drop drifters, impossible speeds will be handled by daily aggregation;
# keep CCS-domain animals (median track position within 30-48N, 235-243E box)
df = df[df["isDrifter"].astype(str).str.lower().isin(["false", "0", "f"]) | df["isDrifter"].isna()]

# daily median position per animal
df["date"] = df["time"].dt.floor("D")
daily = (df.groupby(["species", "animal", "date"])
           .agg(lat=("lat", "median"), lon=("lon", "median"),
                n_fixes=("lat", "size"))
           .reset_index())

# CCS subset: animal's median lon/lat in box (lon here is -180..180?)
print("lon range:", df["lon"].min(), df["lon"].max())
daily["lon360"] = daily["lon"] % 360

EARTH_KM = 6371.0
def step_km(lat1, lon1, lat2, lon2):
    a = (np.sin(np.radians(lat2 - lat1) / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2))
         * np.sin(np.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

# consecutive-day displacement (QC-passed consecutive fixes; no cross-gap steps)
daily = daily.sort_values(["animal", "date"])
daily["lat_prev"] = daily.groupby("animal")["lat"].shift(1)
daily["lon_prev"] = daily.groupby("animal")["lon"].shift(1)
daily["date_prev"] = daily.groupby("animal")["date"].shift(1)
consec = daily["date"].sub(daily["date_prev"]).dt.days == 1
daily["disp_km"] = np.where(
    consec, step_km(daily["lat_prev"], daily["lon_prev"],
                    daily["lat"], daily["lon"]), np.nan)

# CCS animals: >30 days of data inside box 30-48N, 235-243E
inbox = daily[(daily.lat.between(30, 48)) &
              (daily.lon360.between(235, 243))]
ccs_animals = (inbox.groupby("animal").size()
               .loc[lambda s: s >= 30].index)
ccs = daily[daily["animal"].isin(ccs_animals)].copy()

# species inventory + independent mobility (median daily displacement over
# the FULL series inside CCS box; event windows excluded later in 03 — the
# metric is frozen here BEFORE any event construction)
inv = (df.groupby(["species", "project"])
         .agg(n_ind=("animal", "nunique"), n_fixes=("lat", "size"),
              t0=("time", "min"), t1=("time", "max"))
         .reset_index())
inv.to_csv(os.path.join(ROOT, "metadata/topp_dataset_inventory.csv"),
           index=False)

mob = (inbox.groupby("animal")["disp_km"].median().rename("disp_med_km")
       .reset_index())
mob["species"] = mob["animal"].map(
    daily.groupby("animal")["species"].first())
sp_mob = (mob.groupby("species")
          .agg(median_daily_disp_km=("disp_med_km", "median"),
               p90_daily_disp_km=("disp_med_km", lambda s: s.quantile(0.9)),
               n_ind=("animal", "size"))
          .reset_index())
sp_mob["mobility_source"] = "median daily displacement (GPS/Argos-SSM, CCS box)"
sp_mob.to_csv(os.path.join(ROOT, "metadata/topp_species_mobility.csv"),
              index=False)

ccs.to_csv(os.path.join(ROOT, "data/processed/topp_daily.csv"), index=False)
print("animals:", ccs["animal"].nunique(), "species:", ccs["species"].nunique())
print(ccs.groupby("species")["animal"].nunique().sort_values(ascending=False))
print(sp_mob)
