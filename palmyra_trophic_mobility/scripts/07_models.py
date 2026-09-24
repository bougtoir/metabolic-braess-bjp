"""Exploratory event-level models, leave-one-event-out, temporal placebo.

Outputs:
  outputs/tables/leave_one_event_out.csv
  outputs/tables/placebo_comparison.csv
  outputs/figures/leave_one_event_out.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRE, EVT, POST = (-7, -1), (0, 2), (3, 14)

resp = pd.read_csv(os.path.join(ROOT, "outputs/tables/event_response.csv"))
resp["event_date"] = pd.to_datetime(resp["event_date"])
resp = resp[resp["definition"] == "B_percentile"].copy()
MOB = {"A_plankton_feeding_mobile": 1, "C_mesopredator": 2,
       "D_mobile_predator": 3, "E_seabird_predator": 4}
resp["mobility_rank"] = resp["guild"].map(MOB)
resp = resp[resp["centroid_shift_km"].notna()]

# per event x guild median (keeps n information)
ev_g = resp.groupby(["event_date", "guild", "mobility_rank"],
                    as_index=False).agg(shift=("centroid_shift_km", "median"),
                                        n=("centroid_shift_km", "size"))


def slope(df):
    """Response-vs-mobility slope within each event, averaged over events."""
    s = []
    for _, g in df.groupby("event_date"):
        if g["guild"].nunique() < 2:
            continue
        s.append(np.polyfit(g["mobility_rank"], np.log10(g["shift"] + 1), 1)[0])
    return np.array(s)


obs = slope(ev_g)
print("observed per-event slopes (log10 shift vs mobility rank):",
      np.round(obs, 3), "median:", np.median(obs))

# leave-one-event-out
loeo = []
for e in ev_g["event_date"].unique():
    s = slope(ev_g[ev_g["event_date"] != e])
    loeo.append({"dropped_event": e.date(), "median_slope": np.median(s),
                 "n_events": len(s)})
lo = pd.DataFrame(loeo)
lo.to_csv(os.path.join(ROOT, "outputs/tables/leave_one_event_out.csv"), index=False)

# OLS event-level: log shift ~ mobility_rank + event fixed effects
X = pd.concat([ev_g["mobility_rank"],
               pd.get_dummies(ev_g["event_date"], prefix="ev",
                              drop_first=True, dtype=float)], axis=1)
X = sm.add_constant(X)
m = sm.OLS(np.log10(ev_g["shift"] + 1).values, X).fit(
    cov_type="cluster", cov_kwds={"groups": ev_g["event_date"]})
print(m.params["mobility_rank"], m.pvalues["mobility_rank"])

# temporal placebo: shift each event date by +/- a fixed offset within same
# season, recompute responses, recompute slopes
spday = pd.read_csv(os.path.join(ROOT, "data/processed/species_day.csv"),
                    parse_dates=["date"])
SPECIES_GUILD = {
    "reef manta ray": "A_plankton_feeding_mobile",
    "yellowfin tuna": "D_mobile_predator", "blue marlin": "D_mobile_predator",
    "grey reef shark": "C_mesopredator", "melon-headed whale": "D_mobile_predator",
    "bottlenose dolphin": "D_mobile_predator", "great frigatebird": "E_seabird_predator",
    "red-footed booby": "E_seabird_predator", "sooty tern": "E_seabird_predator"}
spday["guild"] = spday["species"].map(SPECIES_GUILD)


def resp_for_date(e):
    rows = []
    for sp, sd in spday.groupby("species"):
        pre = sd[(sd["date"] >= e + pd.Timedelta(days=PRE[0])) & (sd["date"] <= e + pd.Timedelta(days=PRE[1]))]
        ev = sd[(sd["date"] >= e + pd.Timedelta(days=EVT[0])) & (sd["date"] <= e + pd.Timedelta(days=EVT[1]))]
        post = sd[(sd["date"] >= e + pd.Timedelta(days=POST[0])) & (sd["date"] <= e + pd.Timedelta(days=POST[1]))]
        if len(pre) < 2 or len(post) < 2 or len(ev) < 1:
            continue
        def hav(a, b, c, d):
            r = 6371.0; p1, p2 = np.radians(a), np.radians(c)
            aa = np.sin(np.radians(c - a) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(d - b) / 2) ** 2
            return 2 * r * np.arcsin(np.sqrt(aa))
        rows.append({"guild": SPECIES_GUILD[sp],
            "shift": hav(pre["centroid_lat"].mean(), pre["centroid_lon"].mean(),
                         post["centroid_lat"].mean(), post["centroid_lon"].mean())})
    d = pd.DataFrame(rows)
    if d.empty:
        return np.nan
    d["mobility_rank"] = d["guild"].map(MOB)
    g = d.groupby(["guild", "mobility_rank"], as_index=False)["shift"].median()
    if g["guild"].nunique() < 2:
        return np.nan
    return np.polyfit(g["mobility_rank"], np.log10(g["shift"] + 1), 1)[0]


rng = np.random.default_rng(0)
events = sorted(ev_g["event_date"].unique())
plac = []
for e in events:
    # season-matched placebo: +/- 30-60 day offsets staying inside data range
    for off in rng.choice([-60, -45, -30, 30, 45, 60], size=4, replace=False):
        pd_date = pd.Timestamp(e) + pd.Timedelta(days=int(off))
        if pd_date < spday["date"].min() or pd_date > spday["date"].max() - pd.Timedelta(days=14):
            continue
        plac.append({"event_date": e.date(), "placebo_date": pd_date.date(),
                     "offset_days": int(off), "slope": resp_for_date(pd_date)})
pl = pd.DataFrame(plac)
pl.to_csv(os.path.join(ROOT, "outputs/tables/placebo_comparison.csv"), index=False)
print("real slopes median:", np.median(obs), "placebo median:", pl["slope"].median(),
      "| placebo >= real frac:", (pl["slope"].dropna() >= np.median(obs)).mean())

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].bar(range(len(lo)), lo["median_slope"])
ax[0].axhline(np.median(obs), color="r", ls="--")
ax[0].set_ylabel("median slope w/o event"); ax[0].set_title("Leave-one-event-out")
ax[0].set_xticks(range(len(lo)))
ax[0].set_xticklabels(lo["dropped_event"], rotation=90, fontsize=6)
ax[1].hist(pl["slope"].dropna(), bins=20, alpha=0.7, label="placebo")
ax[1].axvline(np.median(obs), color="r", lw=2, label="observed median")
ax[1].legend(); ax[1].set_title("Temporal placebo slopes")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/leave_one_event_out.png"), dpi=150)
