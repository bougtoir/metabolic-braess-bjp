# Task 5 figures per spec section 26.
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "outputs", "figures")
TAB = os.path.join(ROOT, "outputs", "tables")
os.makedirs(FIG, exist_ok=True)
ad = pd.read_parquet(os.path.join(ROOT, "data", "processed",
                                  "animal_day_model.parquet"))
ad["date_naive"] = pd.to_datetime(ad["date"], utc=True).dt.tz_localize(None)

# 1 mechanism_schematic
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.axis("off")
boxes = {"Environment\n(UWI, SST)": (0.15, 0.75),
         "Prey field\n(chl-a, INDIRECT)": (0.5, 0.75),
         "Predator\n(active displacement)": (0.85, 0.75)}
for t, (x, y) in boxes.items():
    ax.text(x, y, t, ha="center", va="center", fontsize=10,
            bbox=dict(boxstyle="round", fc="#eef", ec="#44a"))
arr = dict(arrowstyle="->", color="#333", lw=1.5)
ax.annotate("", xy=(0.41, 0.75), xytext=(0.24, 0.75), arrowprops=arr)
ax.annotate("", xy=(0.76, 0.75), xytext=(0.59, 0.75), arrowprops=arr)
ax.annotate("", xy=(0.85, 0.60), xytext=(0.15, 0.60), arrowprops=arr)
ax.text(0.33, 0.80, "H2: E->K", ha="center", fontsize=9)
ax.text(0.68, 0.80, "H2: K->P", ha="center", fontsize=9)
ax.text(0.5, 0.55, "H1/H3: E->P direct (common environment)", fontsize=9)
ax.annotate("", xy=(0.5, 0.30), xytext=(0.15, 0.45), arrowprops=dict(
    arrowstyle="->", color="#a44", lw=1.5, linestyle="--"))
ax.text(0.28, 0.34, "H4: E_t -> K_{t+d} (predictive cueing)", fontsize=9,
        color="#a44")
ax.set_title("Competing mechanisms of predator tracking (Task 5)")
fig.savefig(os.path.join(FIG, "mechanism_schematic.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# 2 event_example: UWI vs chl vs predator activity around biggest event
ev = pd.read_csv(os.path.join(TAB, "independent_events.csv"),
                 parse_dates=["start_date"])
ev["start_date"] = pd.to_datetime(ev["start_date"], utc=True).dt.tz_localize(None)
bev = ev[ev.in_season].sort_values("intensity", ascending=False).iloc[0]
st = int(bev["station_lat"])
uwi = pd.read_csv(os.path.join(ROOT, "data", "raw", "forcing",
                               f"uwi_{st}N.csv"), skiprows=[1],
                  parse_dates=["time"])
uwi.columns = [c.lower() for c in uwi.columns]
uwi = uwi.set_index("time")["upwelling_index"].astype(float)
uwi = uwi.resample("D").mean()
uwi.index = uwi.index.tz_localize(None)
w = slice(bev.start_date - pd.Timedelta(days=30),
          bev.start_date + pd.Timedelta(days=40))
fig, ax = plt.subplots(figsize=(8, 4))
uwi[w].plot(ax=ax, color="#07a", label=f"UWI {st}N")
ax.axvline(bev.start_date, color="k", ls="--", label="event onset")
m = ad[(ad["date_naive"] >= bev.start_date - pd.Timedelta(days=30)) &
       (ad["date_naive"] <= bev.start_date + pd.Timedelta(days=40)) &
       (ad["lat"].between(st - 2, st + 2))]
if len(m):
    mm = m.groupby("date_naive")["active_km"].median()
    ax2 = ax.twinx()
    mm.plot(ax=ax2, color="#c40", label="median active_km", alpha=0.7)
    ax2.set_ylabel("active displacement (km/d)")
ax.set_title(f"Event {bev.event_id} ({bev.start_date.date()}, {st}N)")
ax.legend(loc="upper left")
fig.savefig(os.path.join(FIG, "event_example.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# 3 lag_response
lag = pd.read_csv(os.path.join(TAB, "lag_results.csv"))
fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)
for ax, link in zip(axes, ["E->K", "E->P", "K->P"]):
    g = lag[lag.link == link]
    for sp, s in g.groupby("species"):
        ax.plot(s.lag, s.coef, alpha=0.6, label=sp, lw=1)
    ax.axvline(0, color="k", ls=":", lw=0.8)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_title(link); ax.set_xlabel("lag (days)")
axes[0].set_ylabel("standardized coefficient")
axes[0].legend(fontsize=6)
fig.suptitle("Lag profiles (-14..+14d), per species")
fig.savefig(os.path.join(FIG, "lag_response.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# 4 event_holdout_comparison
ho = pd.read_csv(os.path.join(TAB, "event_holdout_results.csv"))
fig, ax = plt.subplots(figsize=(7, 4))
if len(ho):
    hm = ho.groupby(["model", "species"])["corr"].mean().unstack()
    hm.plot(kind="bar", ax=ax)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("event-held-out correlation")
ax.set_title("Event-held-out predictive performance (y = active km)")
fig.savefig(os.path.join(FIG, "event_holdout_comparison.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# 5 species_mode_matrix
sm = pd.read_csv(os.path.join(TAB, "species_tracking_mode.csv"))
fig, ax = plt.subplots(figsize=(9, 4))
cats = {"MODE-SEPARATION SUPPORT": 4, "ENVIRONMENTAL-CUE DOMINATED": 3,
        "PREY-MEDIATED DOMINATED": 2, "MIXED-WEAK": 1, "INCONCLUSIVE": 0}
sm["v"] = sm["best_supported_mode"].map(cats)
ax.scatter(range(len(sm)), sm["v"], s=80)
for i, r in sm.iterrows():
    ax.annotate(r["species"], (i, r["v"]), fontsize=8,
                xytext=(4, 4), textcoords="offset points")
ax.set_yticks(list(cats.values())); ax.set_yticklabels(list(cats), fontsize=8)
ax.set_xticks([]); ax.set_title("Best-supported tracking mode per species")
fig.savefig(os.path.join(FIG, "species_mode_matrix.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# 6 predictability_mode_relationship
mob = pd.read_csv(os.path.join(ROOT, "metadata", "topp_species_mobility.csv"))
mr = sm.merge(mob, on="species", how="left")
fig, ax = plt.subplots(figsize=(7, 4))
ax.scatter(mr["predictability_futureprey_from_env"],
           np.log10(mr["median_daily_disp_km"]))
for i, r in mr.iterrows():
    ax.annotate(r["species"].split()[0],
                (r["predictability_futureprey_from_env"],
                 np.log10(r["median_daily_disp_km"])), fontsize=7,
                xytext=(3, 3), textcoords="offset points")
ax.set_xlabel("predictability: env_t -> chl_{t+8} (CV corr)")
ax.set_ylabel("log10 median daily displacement (km)")
ax.set_title("Prey predictability vs predator mobility")
fig.savefig(os.path.join(FIG, "predictability_mode_relationship.png"),
            dpi=150, bbox_inches="tight"); plt.close(fig)

# 7 cross_system_summary
sys = pd.DataFrame([
    {"system": "Palmyra", "finding": "null (weak go)",
     "env_dom": np.nan, "value": 0},
    {"system": "Capelin-seabird", "finding": "weak positive control",
     "env_dom": np.nan, "value": 1},
    {"system": "ACCESS ecomega", "finding": "common-env dominated",
     "env_dom": 1, "value": 2},
    {"system": "TOPP CCS", "finding": "mixed-weak / inconclusive",
     "env_dom": np.nan, "value": 1},
])
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.barh(sys.system, sys.value, color=["#aaa", "#4a4", "#47a", "#a74"])
for i, r in sys.iterrows():
    ax.text(r.value + 0.03, i, r.finding, va="center", fontsize=8)
ax.set_yticks(range(len(sys))); ax.set_yticklabels(sys.system)
ax.set_xlim(0, 3); ax.set_xticks([0, 1, 2, 3])
ax.set_xticklabels(["null", "weak signal", "env-dominated", ""])
ax.set_title("Cross-system comparison (Tasks 1-5)")
fig.savefig(os.path.join(FIG, "cross_system_summary.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

# supplementaries
fig, ax = plt.subplots(figsize=(8, 4))
ad.dropna(subset=["active_km"]).groupby(
    ad["date_naive"].dt.to_period("M"))["active_km"].median().plot(ax=ax)
ax.set_ylabel("median active displacement (km/d)")
ax.set_title("Suppl: active displacement over time (all CCS animals)")
fig.savefig(os.path.join(FIG, "suppl_active_km_timeseries.png"), dpi=150,
            bbox_inches="tight"); plt.close(fig)

pl = pd.read_csv(os.path.join(TAB, "placebo_results.csv"))
if len(pl):
    fig, ax = plt.subplots(figsize=(7, 4))
    for plname, g in pl.groupby("placebo"):
        ax.scatter([plname] * len(g), g["coef"], alpha=0.6)
        if g["observed"].notna().any():
            ax.scatter([plname], [g["observed"].dropna().iloc[0]],
                       marker="*", s=120, c="k")
    ax.tick_params(axis="x", rotation=20); ax.axhline(0, color="k", lw=0.5)
    ax.set_ylabel("coef"); ax.set_title("Suppl: placebo coefficients vs observed (*)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "suppl_placebos.png"), dpi=150)
    plt.close(fig)
print("figures done")
