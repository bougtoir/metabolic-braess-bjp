"""Candidate environmental events (from environmental data ONLY), independence
filtering across separation windows, event-species coverage, and preliminary
event-level response summaries incl. passive-advection comparison.

Outputs:
  outputs/tables/environmental_events.csv
  outputs/tables/event_independence.csv
  outputs/tables/event_species_coverage.csv
  outputs/tables/event_response.csv
  outputs/figures/environment_time_series.png
  outputs/figures/event_examples.png
  outputs/figures/event_response_by_guild.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

ROOT = os.path.join(os.path.dirname(__file__), "..")
PALMYRA = (5.877, -162.078)
PRE = (-7, -1)
EVT = (0, 2)
POST = (3, 14)


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


env = pd.read_csv(os.path.join(ROOT, "data/processed/env_daily.csv"),
                  parse_dates=["date"]).set_index("date")
env["dchl"] = env["chl_mean"].diff()
env["dchl_log"] = np.log10(env["chl_mean"]).diff()
# seasonal baseline: 31-day rolling stats
env["dchl_z"] = (env["dchl_log"] - env["dchl_log"].rolling(31, center=True).mean()) / \
                env["dchl_log"].rolling(31, center=True).std()
env["centroid_step"] = haversine_km(env["chl_centroid_lat"].shift(),
                                    env["chl_centroid_lon"].shift(),
                                    env["chl_centroid_lat"],
                                    env["chl_centroid_lon"])

p95 = env["dchl_log"].quantile(0.95)
p05 = env["dchl_log"].quantile(0.05)
c95 = env["centroid_step"].quantile(0.95)

defs = {
    "A_zscore": np.abs(env["dchl_z"]) > 2,
    "B_percentile": (env["dchl_log"] > p95) | (env["dchl_log"] < p05),
    "C_front": env["centroid_step"] > c95,
    "D_persistent": ((np.abs(env["dchl_z"]) > 2)
                     & (np.abs(env["dchl_z"].shift()) > 2).fillna(False).astype(bool)),
}


def independent_events(mask, sep_days):
    """Greedy: keep first day of clusters; drop events within sep_days of kept."""
    days = mask[mask].index.sort_values()
    kept = []
    for d in days:
        if not kept or (d - kept[-1]).days > sep_days:
            kept.append(d)
    return kept


spday = pd.read_csv(os.path.join(ROOT, "data/processed/species_day.csv"),
                    parse_dates=["date"])

GUILD = {
    "reef manta ray": "A_plankton_feeding_mobile",
    "yellowfin tuna": "D_mobile_predator",
    "blue marlin": "D_mobile_predator",
    "grey reef shark": "C_mesopredator",
    "melon-headed whale": "D_mobile_predator",
    "bottlenose dolphin": "D_mobile_predator",
    "great frigatebird": "E_seabird_predator",
    "red-footed booby": "E_seabird_predator",
    "sooty tern": "E_seabird_predator",
}
spday["guild"] = spday["species"].map(GUILD)

# ssh grids for advection analysis + distance-to-chl-max
ssh = xr.merge([xr.open_dataset(os.path.join(ROOT, f"data/raw/env/ssh_{v}.nc"))
                for v in ("sla", "ugos", "vgos")])
chl_grid = xr.open_dataset(os.path.join(ROOT, "data/raw/env/chl.nc"))["chlor_a"].squeeze()

tracks = pd.read_csv(os.path.join(ROOT, "data/processed/tracks_qc.csv"),
                     low_memory=False)
tracks["timestamp_utc"] = pd.to_datetime(tracks["timestamp_utc"], utc=True, format="mixed")
tracks = tracks[~tracks["flagged"]]
tracks["date"] = tracks["timestamp_utc"].dt.normalize().dt.tz_localize(None)
tracks["guild"] = tracks["species"].map(GUILD)

idday = pd.read_csv(os.path.join(ROOT, "data/processed/individual_day.csv"),
                    parse_dates=["date"])
idday["guild"] = idday["species"].map(GUILD)

event_rows = []
indep_rows = []
cover_rows = []
resp_rows = []

for defname, mask in defs.items():
    raw_days = mask[mask].index
    for sep in (3, 7, 14):
        evs = independent_events(mask, sep)
        indep_rows.append({
            "definition": defname, "separation_days": sep,
            "n_raw_event_days": int(mask.sum()),
            "n_independent_events": len(evs),
        })
        if sep != 7:
            continue  # downstream analysis on the 7-day convention
        for e in evs:
            # coverage: guilds with >=1 tracked individual on event window
            win = spday[(spday["date"] >= e + pd.Timedelta(days=EVT[0]))
                        & (spday["date"] <= e + pd.Timedelta(days=EVT[1]))]
            guild_n = win.groupby("guild")["n_individuals"].sum()
            n_guilds = (guild_n > 0).sum()
            max_ind = win.groupby("guild")["n_individuals"].max().max() if len(win) else 0
            event_rows.append({
                "definition": defname, "event_date": e.date(),
                "n_guilds_tracked": n_guilds, "max_individuals_per_guild": max_ind,
                "dchl_log": env.loc[e, "dchl_log"] if e in env.index else np.nan,
                "sst_mean": env.loc[e, "sst_mean"] if e in env.index else np.nan,
            })
            for guild, g in guild_n.items():
                cover_rows.append({"definition": defname, "event_date": e.date(),
                                   "guild": guild, "n_individual_days": int(g)})

            # per-species response (event level): pre vs post changes
            for sp, sd in spday.groupby("species"):
                pre = sd[(sd["date"] >= e + pd.Timedelta(days=PRE[0]))
                         & (sd["date"] <= e + pd.Timedelta(days=PRE[1]))]
                ev = sd[(sd["date"] >= e + pd.Timedelta(days=EVT[0]))
                        & (sd["date"] <= e + pd.Timedelta(days=EVT[1]))]
                post = sd[(sd["date"] >= e + pd.Timedelta(days=POST[0]))
                          & (sd["date"] <= e + pd.Timedelta(days=POST[1]))]
                if len(pre) < 2 or len(post) < 2 or len(ev) < 1:
                    continue
                c_pre = (pre["centroid_lat"].mean(), pre["centroid_lon"].mean())
                c_post = (post["centroid_lat"].mean(), post["centroid_lon"].mean())
                resp_rows.append({
                    "definition": defname, "event_date": e.date(), "species": sp,
                    "guild": GUILD[sp],
                    "n_ind_pre": pre["n_individuals"].mean(),
                    "n_ind_evt": ev["n_individuals"].mean(),
                    "n_ind_post": post["n_individuals"].mean(),
                    "centroid_shift_km": haversine_km(*c_pre, *c_post),
                    "d_dist_palmyra_km": (post["median_dist_palmyra_km"].median()
                                        - pre["median_dist_palmyra_km"].median()),
                    "d_rog_km": post["mean_rog"].mean() - pre["mean_rog"].mean(),
                    "d_path_km": post["mean_path"].mean() - pre["mean_path"].mean(),
                })

pd.DataFrame(event_rows).to_csv(
    os.path.join(ROOT, "outputs/tables/environmental_events.csv"), index=False)
pd.DataFrame(indep_rows).to_csv(
    os.path.join(ROOT, "outputs/tables/event_independence.csv"), index=False)
pd.DataFrame(cover_rows).to_csv(
    os.path.join(ROOT, "outputs/tables/event_species_coverage.csv"), index=False)
resp = pd.DataFrame(resp_rows)
resp.to_csv(os.path.join(ROOT, "outputs/tables/event_response.csv"), index=False)

# ---- advection check: daily displacement vs ugos/vgos at centroid ----
ugos = ssh["ugos"]; vgos = ssh["vgos"]
lats = ugos["latitude"].values; lons = ugos["longitude"].values
obs = []
for (sp, iid), g in tracks.groupby(["species", "individual_id"]):
    d = g.set_index("timestamp_utc").sort_index()
    for day, gd in d.groupby(d.index.normalize()):
        if len(gd) < 2:
            continue
        dx_km = haversine_km(gd["lat"].iloc[0], gd["lon"].iloc[0],
                             gd["lat"].iloc[-1], gd["lon"].iloc[-1])
        if dx_km < 0.5:
            continue
        # observed displacement as an east/north km vector
        ox = (gd["lon"].iloc[-1] - gd["lon"].iloc[0]) * 111.2 * np.cos(np.radians(gd["lat"].mean()))
        oy = (gd["lat"].iloc[-1] - gd["lat"].iloc[0]) * 111.2
        obs_norm = np.hypot(ox, oy)
        ux, uy = ox / obs_norm, oy / obs_norm
        dt_s = (gd.index[-1] - gd.index[0]).total_seconds()
        if dt_s <= 0:
            continue
        try:
            t0 = np.datetime64(day)
            sel = ssh.sel(time=t0, method="nearest")
            ilat = np.abs(lats - gd["lat"].mean()).argmin()
            ilon = np.abs(lons - gd["lon"].mean()).argmin()
            u_c = float(sel["ugos"].values[ilat, ilon])  # m/s
            v_c = float(sel["vgos"].values[ilat, ilon])
        except Exception:
            continue
        if not np.isfinite(u_c) or not np.isfinite(v_c):
            continue
        # expected passive displacement vector over the actual fix interval
        ex, ey = u_c * dt_s / 1000, v_c * dt_s / 1000  # km
        enorm = np.hypot(ex, ey)
        align = (ux * ex + uy * ey) / enorm if enorm > 1e-6 else np.nan
        resid = np.hypot(ox - ex, oy - ey) / obs_norm
        obs.append({"species": sp, "individual_id": iid, "date": day,
                    "displacement_km": dx_km, "dt_hours": dt_s / 3600,
                    "current_disp_km": enorm,
                    "alignment": align,
                    "residual_fraction": resid})
adv = pd.DataFrame(obs)
adv.to_csv(os.path.join(ROOT, "outputs/tables/advection_alignment.csv"), index=False)
print(adv.groupby("species")[["alignment", "residual_fraction"]].median())

# ---- figures ----
fig, axes = plt.subplots(4, 1, figsize=(12, 11), sharex=True)
axes[0].plot(env.index, env["chl_mean"], lw=0.8); axes[0].set_ylabel("chl-a mg/m3")
axes[1].plot(env.index, env["sst_mean"], lw=0.8, color="tab:red"); axes[1].set_ylabel("SST C")
axes[2].plot(env.index, env["sla_mean"], lw=0.8, color="tab:green"); axes[2].set_ylabel("SLA m")
axes[3].plot(env.index, env["eke_mean"], lw=0.8, color="tab:purple"); axes[3].set_ylabel("EKE m2/s2")
for name, mask in defs.items():
    pass
ev7 = independent_events(defs["B_percentile"], 7)
for a in axes:
    for e in ev7:
        a.axvline(e, color="k", alpha=0.2, lw=0.7)
fig.suptitle("Environmental time series; vertical lines = percentile events (7-day sep)")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/environment_time_series.png"), dpi=150)

# event examples: chl field around 3 largest percentile events
big = env.loc[ev7, "dchl_log"].abs().sort_values(ascending=False).head(3).index
fig, axes = plt.subplots(1, len(big), figsize=(4 * len(big), 4))
if len(big) == 1:
    axes = [axes]
for ax, e in zip(axes, big):
    sel = chl_grid.sel(time=np.datetime64(e), method="nearest")
    ax.pcolormesh(sel["longitude"], sel["latitude"], np.log10(sel.values),
                  cmap="viridis", vmin=-1.5, vmax=0.5, shading="auto")
    ax.plot(*PALMYRA[::-1], "r^")
    ax.set_title(str(e.date()))
fig.suptitle("chl-a (log10) on largest events")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/event_examples.png"), dpi=150)

# response by guild
if len(resp):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, metric in zip(axes, ["centroid_shift_km", "d_rog_km", "d_path_km"]):
        data = [resp.loc[resp["guild"] == g, metric].dropna().values
                for g in sorted(resp["guild"].unique())]
        ax.boxplot(data, tick_labels=[g.split("_")[0] for g in sorted(resp["guild"].unique())])
        ax.axhline(0, color="grey", lw=0.6)
        ax.set_title(metric)
    fig.suptitle("Event-level responses by guild (definition B, 7-day separation)")
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "outputs/figures/event_response_by_guild.png"), dpi=150)

print(resp.groupby("guild")[["centroid_shift_km", "d_rog_km"]].median())
print(pd.DataFrame(indep_rows))
