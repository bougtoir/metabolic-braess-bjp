"""Build matched trophic units.

Analytical unit = ACCESS sampling event (zooplankton tow or bird/mammal
sighting cluster). Layers share eventID/eventDate within a cruise.

Unit chosen: zooplankton tow as anchor (has position, time, prey density);
predator density joined from bird/mammal sighting events within spatial and
temporal tolerance (primary: 24 h, 10 km). Also produce a cruise-day aggregate
table as a secondary unit.

Outputs:
  data/processed/ecomega_matched_trophic_units.parquet  (tow-level, 24h/10km)
  metadata/matching_sensitivity.csv  (unit counts under tolerance grid)
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(ROOT, "data/raw/access")
OUT = os.path.join(ROOT, "data/processed")
os.makedirs(OUT, exist_ok=True)

EARTH_KM = 6371.0
def hav_km(lat1, lon1, lat2, lon2):
    a = (np.sin(np.radians(lat2 - lat1) / 2) ** 2
         + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2))
         * np.sin(np.radians(lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_KM * np.arcsin(np.sqrt(a))

# ---------------- load layers ----------------
z = pd.read_csv(os.path.join(RAW, "access_zooplankton_2024.csv"), low_memory=False)
z["time"] = pd.to_datetime(z["eventDate"], errors="coerce", utc=True)
z = z.dropna(subset=["time", "decimalLatitude", "decimalLongitude"])
z["is_krill"] = z["scientificName"].astype(str).str.contains(
    "Euphaus|Thysanoessa|Euphausi", case=False)
z["count_per_m3"] = pd.to_numeric(z["count_per_m3"], errors="coerce")

# tow-level prey table
tow = z.groupby("eventID").agg(
    time=("time", "first"), lat=("decimalLatitude", "first"),
    lon=("decimalLongitude", "first"),
    depth_min=("minimumDepthInMeters", "first"),
    depth_max=("maximumDepthInMeters", "first"),
    gear=("samplingProtocol", "first"),
    # krill absence = true non-detection (ACCESS records all taxa per tow);
    # empty krill subset -> 0, not NaN
    krill_m3=("count_per_m3", lambda s: s[z.loc[s.index, "is_krill"]].sum()),
    zoop_m3=("count_per_m3", "sum"),
    n_taxa=("scientificName", "nunique")).reset_index()

# predators: birds (count/km2) + mammals (count/km)
b = pd.read_csv(os.path.join(RAW, "bird_density_2004_2024.csv"), low_memory=False)
b["time"] = pd.to_datetime(b["eventDate"], errors="coerce", utc=True)
b["density"] = pd.to_numeric(b["count_per_km2"], errors="coerce")
b = b.dropna(subset=["time", "decimalLatitude", "decimalLongitude", "density"])
b["is_effort"] = b["vernacularName"].astype(str).str.contains("effort", case=False)

KRILL_BIRDS = ["Cassin's Auklet", "Common Murre", "Sooty Shearwater",
               "Rhinoceros Auklet", "Red Phalarope", "Red-necked Phalarope"]
b["krill_feeder"] = b["vernacularName"].isin(KRILL_BIRDS)
bird_ev = b.groupby("eventID").agg(
    time=("time", "first"), lat=("decimalLatitude", "first"),
    lon=("decimalLongitude", "first"),
    bird_km2=("density", "sum"),
    krillbird_km2=("density", lambda s: s[b.loc[s.index, "krill_feeder"]].sum(min_count=1)),
    effort_km2=("density", lambda s: s[b.loc[s.index, "is_effort"]].sum(min_count=1)),
    ).reset_index()

o = pd.read_csv(os.path.join(RAW, "others_density_2004_2024.csv"), low_memory=False)
o["time"] = pd.to_datetime(o["eventDate"], errors="coerce", utc=True)
o["density"] = pd.to_numeric(o["count_per_km"], errors="coerce")
o = o.dropna(subset=["time", "decimalLatitude", "decimalLongitude", "density"])
o["is_whale"] = o["scientificName"].isin(
    ["Megaptera novaeangliae", "Balaenoptera musculus", "Balaenoptera acutorostrata",
     "Balaenoptera physalus", "Eschrichtius robustus"])
mam_ev = o.groupby("eventID").agg(
    time=("time", "first"), lat=("decimalLatitude", "first"),
    lon=("decimalLongitude", "first"),
    mammal_km=("density", "sum"),
    whale_km=("density", lambda s: s[o.loc[s.index, "is_whale"]].sum(min_count=1)),
    ).reset_index()

# cruise id: cluster all sample dates with >4-day gaps (zooplankton eventID is
# a numeric index, not cruise-coded, so cluster on dates across all layers)
all_dates = pd.Series(sorted(
    pd.concat([tow["time"], bird_ev["time"], mam_ev["time"]])
    .dt.floor("D").unique()))
cruise_map = dict(zip(all_dates, (all_dates.diff().dt.days > 4).cumsum()))
for df, tag in [(tow, "tow"), (bird_ev, "bird"), (mam_ev, "mam")]:
    df["date"] = df["time"].dt.floor("D")
    df["cruise"] = df["date"].map(cruise_map)
    if tag == "tow": tow = df
    elif tag == "bird": bird_ev = df
    else: mam_ev = df

# ---------------- matching ----------------
def match(prey, pred_events, max_h, max_km):
    """For each tow, mean predator density of sightings within tolerance."""
    out = []
    for _, t in prey.iterrows():
        cand = pred_events[
            (pred_events["time"] >= t["time"] - pd.Timedelta(hours=max_h)) &
            (pred_events["time"] <= t["time"] + pd.Timedelta(hours=max_h))]
        if len(cand):
            d = hav_km(t["lat"], t["lon"], cand["lat"].values, cand["lon"].values)
            cand = cand[d <= max_km]
        if len(cand):
            r = dict(t)
            for c in cand.columns:
                if c.endswith("_km2") or c.endswith("_km"):
                    r[c] = cand[c].mean()
            out.append(r)
    return pd.DataFrame(out)

sens = []
tables = {}
for hh, kk in [(6, 5), (12, 10), (24, 10), (48, 20)]:
    # match each predator layer on its OWN time/coords, then merge per tow
    mb = match(tow, bird_ev, hh, kk)[
        ["eventID", "bird_km2", "krillbird_km2", "effort_km2"]]
    mm = match(tow, mam_ev, hh, kk)[
        ["eventID", "mammal_km", "whale_km"]]
    m = tow.merge(mb, on="eventID", how="left").merge(
        mm, on="eventID", how="left")
    m = m.dropna(subset=["bird_km2", "mammal_km"], how="all")
    sens.append({"tol_h": hh, "tol_km": kk, "matched_tows": len(m)})
    tables[(hh, kk)] = m
    m.to_parquet(os.path.join(OUT, f"units_{hh}h_{kk}km.parquet"), index=False)

pd.DataFrame(sens).to_csv(os.path.join(ROOT, "metadata/matching_sensitivity.csv"),
                          index=False)
prim = tables[(24, 10)]
prim.to_parquet(os.path.join(OUT, "ecomega_matched_trophic_units.parquet"),
                index=False)
prim.to_csv(os.path.join(ROOT, "outputs/tables/matched_trophic_units.csv"),
            index=False)
print("primary units:", len(prim), "cruises:", prim["cruise"].nunique())
print(pd.DataFrame(sens))
