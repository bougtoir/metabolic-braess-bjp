"""Species temporal coverage and pairwise overlap."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
tracks = pd.read_csv(os.path.join(ROOT, "data/processed/tracks.csv"),
                     )
tracks["timestamp_utc"]=pd.to_datetime(tracks["timestamp_utc"],utc=True,format="mixed")
tracks["date"] = tracks["timestamp_utc"].dt.date

# per-species summary
sp = []
for species, g in tracks.groupby("species"):
    days = g["date"].nunique()
    indiv = g.groupby("individual_id")
    per_id_day = g.groupby(["individual_id", "date"]).size()
    sp.append({
        "species": species,
        "n_individuals": g["individual_id"].nunique(),
        "n_records": len(g),
        "first_obs": g["timestamp_utc"].min(),
        "last_obs": g["timestamp_utc"].max(),
        "tracking_days_span": (g["date"].max() - g["date"].min()).days + 1,
        "unique_calendar_days": days,
        "median_obs_per_individual_day": per_id_day.groupby("individual_id").median().median(),
    })
sp = pd.DataFrame(sp)
sp.to_csv(os.path.join(ROOT, "outputs/tables/species_summary.csv"), index=False)

# pairwise overlap in unique calendar days
days = {s: set(g["date"].unique()) for s, g in tracks.groupby("species")}
species = sorted(days)
n = len(species)
overlap_days = pd.DataFrame(np.zeros((n, n)), index=species, columns=species)
overlap_frac = overlap_days.copy()
for i, a in enumerate(species):
    for j, b in enumerate(species):
        ov = len(days[a] & days[b])
        overlap_days.loc[a, b] = ov
        m = min(len(days[a]), len(days[b]))
        overlap_frac.loc[a, b] = ov / m if m else 0
overlap_days.to_csv(os.path.join(ROOT, "outputs/tables/species_temporal_overlap_days.csv"))
overlap_frac.to_csv(os.path.join(ROOT, "outputs/tables/species_temporal_overlap.csv"))

fig, ax = plt.subplots(figsize=(8, 6.5))
im = ax.imshow(overlap_frac.values, cmap="viridis", vmin=0, vmax=1)
ax.set_xticks(range(n), species, rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(n), species, fontsize=8)
for i in range(n):
    for j in range(n):
        ax.text(j, i, f"{overlap_frac.values[i, j]:.2f}\n({int(overlap_days.values[i, j])}d)",
                ha="center", va="center", fontsize=6,
                color="white" if overlap_frac.values[i, j] < 0.6 else "black")
fig.colorbar(im, label="overlap fraction (days / min tracking days)")
ax.set_title("Pairwise species temporal overlap (unique calendar days)")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/species_temporal_overlap.png"), dpi=150)
print(overlap_frac.round(2))
