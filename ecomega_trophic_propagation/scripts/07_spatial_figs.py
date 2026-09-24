"""Spatial propagation metrics + remaining figures.

Outputs:
  outputs/tables/propagation_metrics.csv
  outputs/figures/{event_examples,path_model,typeA_vs_typeB,
                   event_holdout_prediction,spatial_propagation}.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "outputs/tables")
FIG = os.path.join(ROOT, "outputs/figures")

u = pd.read_parquet(os.path.join(ROOT, "data/processed/units_with_env.parquet"))
d = u.dropna(subset=["krill_m3", "bird_km2", "uwi"]).copy()
d["P"] = np.log1p(d["bird_km2"])
d["K"] = np.log1p(d["krill_m3"])
d["month"] = d["time"].dt.month
d["year"] = d["time"].dt.year
d["cruise"] = d["cruise"].astype(str)
CTRL = " + C(month) + C(year)"

# ---- spatial propagation: per-cruise centroids, in vs out of event windows
events = pd.read_csv(os.path.join(OUT, "independent_events.csv"),
                     parse_dates=["start_date", "peak_date", "end_date"])
ev_in = events[events["in_season"]]
cen_rows = []
for _, e in ev_in.iterrows():
    inside = d[(d["date"] >= e["start_date"]) & (d["date"] <= e["end_date"])]
    outside = d[(d["date"] >= e["start_date"] - pd.Timedelta(days=30)) &
                (d["date"] < e["start_date"])]
    if len(inside) < 5 or len(outside) < 5:
        continue
    for val, layer in [("krill_m3", "krill"), ("bird_km2", "predator")]:
        def cent(df, v):
            w = np.clip(df[v].fillna(0), 0, None)
            if w.sum() <= 0:
                return np.nan, np.nan
            return np.average(df["lat"], weights=w), np.average(df["lon"], weights=w)
        (ilat, ilon) = cent(inside, val)
        (olat, olon) = cent(outside, val)
        if np.isnan(ilat) or np.isnan(olat):
            continue
        dist = 6371 * np.arccos(np.clip(
            np.sin(np.radians(ilat)) * np.sin(np.radians(olat))
            + np.cos(np.radians(ilat)) * np.cos(np.radians(olat))
            * np.cos(np.radians(ilon - olon)), -1, 1))
        cen_rows.append({"event_id": e["event_id"], "layer": layer,
                         "centroid_shift_km": dist})
cen = pd.DataFrame(cen_rows)

# propagation metrics: SAR/TR/PV approximations
met_rows = []
if len(cen):
    pv = cen.pivot(index="event_id", columns="layer", values="centroid_shift_km")
    pv["TR_predator_over_krill"] = pv.get("predator") / pv.get("krill")
    met_rows.append({"metric": "TR pred/krill centroid shift",
                     "median": pv["TR_predator_over_krill"].median(),
                     "n_events": pv.dropna().shape[0]})
    met_rows.append({"metric": "predator centroid shift km",
                     "median": pv["predator"].median(), "n_events": len(pv)})
    met_rows.append({"metric": "krill centroid shift km",
                     "median": pv["krill"].median(), "n_events": len(pv)})
pd.DataFrame(met_rows).to_csv(os.path.join(OUT, "propagation_metrics.csv"), index=False)
cen.to_csv(os.path.join(OUT, "event_centroid_shifts.csv"), index=False)

# ---- figures ----
# 1 event examples: daily UWI with event onsets and cruise coverage
uw = pd.read_csv(os.path.join(ROOT, "data/raw/forcing/upwelling_39N125W.csv"),
                 skiprows=[1])
uw["time"] = pd.to_datetime(uw["time"], utc=True)
uw["uwi"] = pd.to_numeric(uw["upwelling_index"], errors="coerce")
uwi_d = uw.set_index("time")["uwi"].resample("1D").mean()
fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=False)
yrs = [2010, 2015, 2019, 2024]
crd = u["date"]
for ax, y in zip(axes, yrs):
    s = uwi_d[f"{y}-04-01":f"{y}-10-31"]
    ax.plot(s.index, s.values, lw=0.8)
    for _, e in ev_in.iterrows():
        if e["start_date"].year == y:
            ax.axvline(e["start_date"], color="r", alpha=0.4)
    cd = crd[crd.dt.year == y]
    for cday in cd.dt.floor("D").unique():
        ax.axvline(cday, color="g", alpha=0.15)
    ax.set_title(str(y)); ax.set_ylabel("UWI")
axes[0].legend(["UWI daily", "event onset", "cruise days"], loc="upper right",
               fontsize=7)
fig.suptitle("Upwelling pulses vs ACCESS cruise coverage")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "event_examples.png"), dpi=120)

# 2 path model diagram
m0 = smf.ols("P ~ uwi" + CTRL, data=d).fit(cov_type="cluster",
    cov_kwds={"groups": d["cruise"]})
mk = smf.ols("K ~ uwi" + CTRL, data=d).fit(cov_type="cluster",
    cov_kwds={"groups": d["cruise"]})
m2 = smf.ols("P ~ uwi + K" + CTRL, data=d).fit(cov_type="cluster",
    cov_kwds={"groups": d["cruise"]})
fig, ax = plt.subplots(figsize=(6.5, 4))
pos = {"E": (0, 0.5), "K": (0.5, 1.0), "P": (1, 0.5)}
for k2, (x, y) in pos.items():
    ax.scatter([x], [y], s=4000, color="#dbe9f6", edgecolor="k", zorder=3)
    ax.text(x, y, {"E": "Environment\n(upwelling)", "K": "Krill\n(prey)", "P": "Predator\n(seabirds)"}[k2],
            ha="center", va="center", fontsize=9)
def arrow(a, b, coef, p, offset=0.0):
    ax.annotate("", xy=pos[b], xytext=pos[a],
                arrowprops=dict(arrowstyle="->", lw=2,
                                shrinkA=28, shrinkB=28))
    mx, my = (pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2 + offset
    ax.text(mx, my, f"{coef:.4f} (p={p:.3f})", fontsize=8, ha="center")
arrow("E", "K", mk.params["uwi"], mk.pvalues["uwi"], 0.08)
arrow("K", "P", m2.params["K"], m2.pvalues["K"], 0.08)
arrow("E", "P", m2.params["uwi"], m2.pvalues["uwi"], -0.12)
ax.set_xlim(-0.2, 1.2); ax.set_ylim(0.2, 1.2); ax.axis("off")
ax.set_title("Path model: standardized structure (OLS coefficients)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "path_model.png"), dpi=130)

# 3 Type A vs B
cmpd = pd.read_csv(os.path.join(OUT, "typeA_typeB_model_comparison.csv"))
ho = pd.read_csv(os.path.join(OUT, "event_holdout_results.csv"))
fig, ax = plt.subplots(figsize=(6.5, 4))
for name, mk2 in [("A_env", "o"), ("B_env_prey", "s")]:
    for split in ["event_id", "cruise"]:
        s = ho[(ho.model == name) & (ho["split"] == split)]
        ax.scatter([f"{split}\n{name}"] * len(s), s["rmse"], alpha=0.3, s=15)
        ax.plot(f"{split}\n{name}", s["rmse"].mean(), mk2, ms=12,
                color="red", mec="k")
ax.set_ylabel("holdout RMSE"); ax.set_title("Type A (env only) vs Type B (env+prey): event/cruise holdout")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "typeA_vs_typeB.png"), dpi=120)
fig, ax = plt.subplots(figsize=(6.5, 4))
for name in ["A_env", "B_env_prey"]:
    s = ho[(ho.model == name) & (ho["split"] == "event_id")].sort_values("held_out")
    ax.plot(range(len(s)), s["corr"], "o-", label=name)
ax.set_ylabel("held-out event correlation (obs vs pred)")
ax.set_xlabel("held-out event index"); ax.legend()
ax.set_title("Event-holdout predictive skill")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "event_holdout_prediction.png"), dpi=120)

# 4 spatial propagation
fig, ax = plt.subplots(figsize=(6, 4))
if len(cen):
    for layer in ["krill", "predator"]:
        s = cen[cen.layer == layer]["centroid_shift_km"]
        ax.hist(s.dropna(), bins=15, alpha=0.6, label=layer)
ax.set_xlabel("event-associated centroid shift (km)")
ax.legend(); ax.set_title("Spatial propagation: centroid displacement by layer")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "spatial_propagation.png"), dpi=120)

print("centroid events:", cen["event_id"].nunique() if len(cen) else 0)
print(pd.DataFrame(met_rows).to_string(index=False))
