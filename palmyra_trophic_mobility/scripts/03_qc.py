"""Telemetry QC: dedup, impossible coords, step length, speed flags.

Flags are added but rows are NOT deleted.
Outputs data/processed/tracks_qc.csv and
outputs/tables/individual_tracking_summary.csv plus diagnostic track maps.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PALMYRA = (5.877, -162.078)

# crude biologically-plausible speed ceilings (km/h) used ONLY for flagging
SPEED_MAX = {
    "grey reef shark": 15, "Galapagos shark": 15, "blue marlin": 20,
    "reef manta ray": 15, "yellowfin tuna": 15,
    "melon-headed whale": 20, "bottlenose dolphin": 20,
    "great frigatebird": 120, "red-footed booby": 120, "sooty tern": 80,
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def main():
    tr = pd.read_csv(os.path.join(ROOT, "data/processed/tracks.csv"),
                     )
    tr["timestamp_utc"]=pd.to_datetime(tr["timestamp_utc"],utc=True,format="mixed")
    tr = tr.sort_values(["individual_id", "timestamp_utc"])
    tr["dup"] = tr.duplicated(["individual_id", "timestamp_utc", "lat", "lon"])
    tr["bad_coord"] = ~(tr["lat"].between(-90, 90) & tr["lon"].between(-180, 180)) | \
                      ((tr["lat"] == 0) & (tr["lon"] == 0))

    out = []
    for (sp, iid), g in tr.groupby(["species", "individual_id"], sort=True):
        g = g.sort_values("timestamp_utc")
        dt_h = g["timestamp_utc"].diff().dt.total_seconds() / 3600
        step = haversine_km(g["lat"].shift(), g["lon"].shift(), g["lat"], g["lon"])
        speed = step / dt_h
        smax = SPEED_MAX.get(sp, 30)
        flag = (step > 0) & (dt_h > 0) & (speed > smax) & ~g["bad_coord"]
        tr.loc[g.index, "dt_h"] = dt_h.values
        tr.loc[g.index, "step_km"] = step.values
        tr.loc[g.index, "speed_kmh"] = speed.values
        tr.loc[g.index, "flag_speed"] = flag.values
        out.append({
            "species": sp, "individual_id": iid, "n_records": len(g),
            "tracking_days": (g["timestamp_utc"].max() - g["timestamp_utc"].min()).total_seconds() / 86400,
            "median_sampling_interval_hours": dt_h[dt_h > 0].median(),
            "median_step_km": step[(dt_h > 0) & ~g["bad_coord"]].median(),
            "p95_step_km": step[(dt_h > 0) & ~g["bad_coord"]].quantile(0.95),
            "median_speed_kmh": speed[(dt_h > 0) & ~g["bad_coord"]].median(),
            "p95_speed_kmh": speed[(dt_h > 0) & ~g["bad_coord"]].quantile(0.95),
            "fraction_flagged": (flag | g["dup"] | g["bad_coord"]).mean(),
            "start_date": g["timestamp_utc"].min(), "end_date": g["timestamp_utc"].max(),
        })
    tr["flagged"] = tr["flag_speed"].fillna(False) | tr["dup"] | tr["bad_coord"]
    tr.to_csv(os.path.join(ROOT, "data/processed/tracks_qc.csv"), index=False)
    pd.DataFrame(out).to_csv(
        os.path.join(ROOT, "outputs/tables/individual_tracking_summary.csv"), index=False)

    # representative track plots per species (first individual with most records)
    fig, axes = plt.subplots(3, 3, figsize=(13, 10))
    for ax, (sp, g) in zip(axes.flat, tr.groupby("species")):
        iid = g.groupby("individual_id").size().idxmax()
        d = g[g["individual_id"] == iid].sort_values("timestamp_utc")
        ok = ~d["flagged"]
        ax.plot(d.loc[ok, "lon"], d.loc[ok, "lat"], ".", ms=1.5, color="tab:blue")
        ax.plot(d.loc[~ok, "lon"], d.loc[~ok, "lat"], ".", ms=2, color="red")
        ax.plot(PALMYRA[1], PALMYRA[0], "^", color="green", ms=8)
        ax.set_title(f"{sp}\n{iid}", fontsize=8)
    fig.suptitle("Representative tracks (red = flagged)")
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "outputs/diagnostics/representative_tracks.png"), dpi=150)

    # full tracking map
    fig, ax = plt.subplots(figsize=(10, 8))
    for sp, g in tr[~tr["flagged"]].groupby("species"):
        ax.plot(g["lon"], g["lat"], ".", ms=0.3, label=sp)
    ax.plot(PALMYRA[1], PALMYRA[0], "^", color="red", ms=10)
    ax.set_xlim(-180, -150)
    ax.set_ylim(-5, 15)
    ax.legend(markerscale=8, fontsize=7)
    ax.set_title("All tracks (unflagged)")
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "outputs/figures/tracking_map.png"), dpi=150)
    print(pd.DataFrame(out).groupby("species")["fraction_flagged"].median())


if __name__ == "__main__":
    main()
