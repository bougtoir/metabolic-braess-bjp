"""Spatial support metrics: ranges, distance from Palmyra, daily centroids,
species-day aggregates (retaining n individuals)."""
import os

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PALMYRA = (5.877, -162.078)


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


tr = pd.read_csv(os.path.join(ROOT, "data/processed/tracks_qc.csv"),
                 )
tr["timestamp_utc"]=pd.to_datetime(tr["timestamp_utc"],utc=True,format="mixed")
tr = tr[~tr["flagged"]].copy()
tr["date"] = tr["timestamp_utc"].dt.date
tr["dist_palmyra"] = haversine_km(tr["lat"], tr["lon"], *PALMYRA)

# --- per individual ---
ind = []
for (sp, iid), g in tr.groupby(["species", "individual_id"]):
    dist = g["dist_palmyra"]
    ind.append({
        "species": sp, "individual_id": iid,
        "n_records_qc": len(g),
        "lat_range_deg": g["lat"].max() - g["lat"].min(),
        "lon_range_deg": g["lon"].max() - g["lon"].min(),
        "approx_range_km": haversine_km(g["lat"].min(), g["lon"].min(),
                                        g["lat"].max(), g["lon"].max()),
        "max_dist_palmyra_km": dist.max(),
        "median_dist_palmyra_km": dist.median(),
        "radius_of_gyration_km": np.sqrt(
            (haversine_km(g["lat"], g["lon"], g["lat"].mean(), g["lon"].mean()) ** 2).mean()),
    })
pd.DataFrame(ind).to_csv(
    os.path.join(ROOT, "outputs/tables/individual_spatial_summary.csv"), index=False)

# recompute within-day steps on the QC-filtered series (QC step_km spans
# flagged rows and day boundaries)
tr = tr.sort_values(["individual_id", "timestamp_utc"])
tr["step_qc"] = tr.groupby("individual_id", group_keys=False).apply(
    lambda g: haversine_km(g["lat"].shift(), g["lon"].shift(), g["lat"], g["lon"]))
same_day = tr["date"] == tr.groupby("individual_id")["date"].shift()
tr.loc[~same_day, "step_qc"] = 0.0  # day-boundary step assigned to neither day

# --- individual-day ---
idday = []
for (sp, iid, d), g in tr.groupby(["species", "individual_id", "date"]):
    clat, clon = g["lat"].mean(), g["lon"].mean()
    rg = np.sqrt((haversine_km(g["lat"], g["lon"], clat, clon) ** 2).mean())
    g2 = g.sort_values("timestamp_utc")
    idday.append({
        "species": sp, "individual_id": iid, "date": d,
        "n_fixes": len(g),
        "centroid_lat": clat, "centroid_lon": clon,
        "median_dist_palmyra_km": g["dist_palmyra"].median(),
        "radius_of_gyration_km": rg,
        "daily_displacement_km": haversine_km(g2["lat"].iloc[0], g2["lon"].iloc[0],
                                              g2["lat"].iloc[-1], g2["lon"].iloc[-1]),
        "path_length_km": g2["step_qc"].sum(),
    })
idday = pd.DataFrame(idday)
idday.to_csv(os.path.join(ROOT, "data/processed/individual_day.csv"), index=False)

# --- species-day ---
spday = (idday.groupby(["species", "date"])
         .agg(centroid_lat=("centroid_lat", "mean"),
              centroid_lon=("centroid_lon", "mean"),
              median_dist_palmyra_km=("median_dist_palmyra_km", "median"),
              dispersion_km=("radius_of_gyration_km", "median"),
              n_individuals=("individual_id", "nunique"),
              n_fixes=("n_fixes", "sum"),
              mean_rog=("radius_of_gyration_km", "mean"),
              mean_path=("path_length_km", "mean"))
         .reset_index())
spday.to_csv(os.path.join(ROOT, "data/processed/species_day.csv"), index=False)
print(spday.groupby("species")["n_individuals"].describe()[["mean", "max"]])
