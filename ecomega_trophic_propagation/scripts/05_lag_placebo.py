"""Lag-response curves, temporal/spatial/trophic placebos, reverse-time tests.

Outputs: outputs/tables/lag_estimates.csv, placebo_results.csv,
         outputs/figures/trophic_lag_curves.png
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
os.makedirs(FIG, exist_ok=True)

u = pd.read_parquet(os.path.join(ROOT, "data/processed/units_with_env.parquet"))
d = u.dropna(subset=["krill_m3", "bird_km2", "uwi"]).copy()
d["P"] = np.log1p(d["bird_km2"])
d["K"] = np.log1p(d["krill_m3"])
d["Z"] = np.log1p(d["zoop_m3"])
d["E"] = d["uwi"]
d["month"] = d["time"].dt.month
d["year"] = d["time"].dt.year
d["cruise"] = d["cruise"].astype(str)
CTRL = " + C(month) + C(year)"

uw = pd.read_csv(os.path.join(ROOT, "data/raw/forcing/upwelling_39N125W.csv"),
                 skiprows=[1])
uw["time"] = pd.to_datetime(uw["time"], utc=True)
uw["uwi"] = pd.to_numeric(uw["upwelling_index"], errors="coerce")
uwi_d = uw.set_index("time")["uwi"].resample("1D").mean()

# ---- lag curves: E shifted by L days before tow date; and P as function of
# E(-L); plus K->P and F->P lags via dates offsets where feasible ----
lags = range(0, 15)
rows = []
for L in lags:
    dd = d.copy()
    dd["E_lag"] = dd["date"].map(lambda x: uwi_d.get(x - pd.Timedelta(days=L)))
    dd = dd.dropna(subset=["E_lag"])
    # E->K
    m = smf.ols("K ~ E_lag" + CTRL, data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["cruise"]})
    rows.append({"link": "E->K", "lag": L, "coef": m.params["E_lag"],
                 "p": m.pvalues["E_lag"], "n": len(dd)})
    # E->P
    m = smf.ols("P ~ E_lag" + CTRL, data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["cruise"]})
    rows.append({"link": "E->P", "lag": L, "coef": m.params["E_lag"],
                 "p": m.pvalues["E_lag"], "n": len(dd)})
    # E->Z
    m = smf.ols("Z ~ E_lag" + CTRL, data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["cruise"]})
    rows.append({"link": "E->Z", "lag": L, "coef": m.params["E_lag"],
                 "p": m.pvalues["E_lag"], "n": len(dd)})

# K->P and Z->P lag approximations: mean K of tows L days before within cruise
for L in lags:
    dd = d.copy()
    # mean krill in same cruise L days before tow date
    km = d.groupby(["cruise", "date"])["krill_m3"].mean().rename("Km")
    km.index = km.index.set_names(["cruise", "date"])
    dd["Km_lag"] = [km.get((c, t - pd.Timedelta(days=L)), np.nan)
                    for c, t in zip(dd["cruise"], dd["date"])]
    dd2 = dd.dropna(subset=["Km_lag"])
    if len(dd2) < 100:
        rows.append({"link": "K->P", "lag": L, "coef": np.nan, "p": np.nan,
                     "n": len(dd2)})
        continue
    m = smf.ols("P ~ np.log1p(Km_lag)" + CTRL, data=dd2).fit(
        cov_type="cluster", cov_kwds={"groups": dd2["cruise"]})
    rows.append({"link": "K->P", "lag": L,
                 "coef": m.params["np.log1p(Km_lag)"],
                 "p": m.pvalues["np.log1p(Km_lag)"], "n": len(dd2)})

lagdf = pd.DataFrame(rows)
lagdf.to_csv(os.path.join(OUT, "lag_estimates.csv"), index=False)

fig, ax = plt.subplots(figsize=(8, 4.5))
for link in ["E->Z", "E->K", "E->P", "K->P"]:
    s = lagdf[lagdf.link == link]
    ax.plot(s.lag, s.coef, "o-", label=link)
ax.axhline(0, color="k", lw=0.5)
ax.set_xlabel("lag (days, forcing before response)")
ax.set_ylabel("coefficient")
ax.legend()
ax.set_title("Lag-response curves (ACCESS matched units)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "trophic_lag_curves.png"), dpi=130)

# ---- placebos ----
plac = []
# temporal placebo: shift UWI series by +/-30, +/-60 days
for shift in (-60, -30, 30, 60):
    dd = d.copy()
    dd["E_s"] = dd["date"].map(lambda x: uwi_d.get(x + pd.Timedelta(days=shift)))
    dd = dd.dropna(subset=["E_s"])
    m = smf.ols("P ~ E_s" + CTRL, data=dd).fit(
        cov_type="cluster", cov_kwds={"groups": dd["cruise"]})
    plac.append({"test": f"temporal_placebo_UWI_shift_{shift:+d}d",
                 "coef": m.params["E_s"], "p": m.pvalues["E_s"], "n": len(dd)})
# trophic placebo: reverse ordering - future prey predicts past predator
dd = d.copy()
km = d.groupby(["cruise", "date"])["krill_m3"].mean()
dd["Km_future"] = [km.get((c, t + pd.Timedelta(days=7)), np.nan)
                   for c, t in zip(dd["cruise"], dd["date"])]
dd2 = dd.dropna(subset=["Km_future"])
m = smf.ols("P ~ np.log1p(Km_future)" + CTRL, data=dd2).fit(
    cov_type="cluster", cov_kwds={"groups": dd2["cruise"]})
plac.append({"test": "trophic_placebo_future_prey+7d",
             "coef": m.params["np.log1p(Km_future)"],
             "p": m.pvalues["np.log1p(Km_future)"], "n": len(dd2)})
# predator preceding forcing: E(+7d) predicts P(today)
dd = d.copy()
dd["E_fwd"] = dd["date"].map(lambda x: uwi_d.get(x + pd.Timedelta(days=7)))
dd2 = dd.dropna(subset=["E_fwd"])
m = smf.ols("P ~ E_fwd" + CTRL, data=dd2).fit(
    cov_type="cluster", cov_kwds={"groups": dd2["cruise"]})
plac.append({"test": "reverse_time_E+7d->P", "coef": m.params["E_fwd"],
             "p": m.pvalues["E_fwd"], "n": len(dd2)})
# forward benchmark same n
m = smf.ols("P ~ E" + CTRL, data=d).fit(
    cov_type="cluster", cov_kwds={"groups": d["cruise"]})
plac.append({"test": "forward_E->P_benchmark", "coef": m.params["E"],
             "p": m.pvalues["E"], "n": len(d)})

pd.DataFrame(plac).to_csv(os.path.join(OUT, "placebo_results.csv"), index=False)
print(lagdf.groupby("link").apply(lambda s: s.loc[s["coef"].abs().idxmax(), "lag"]))
print(pd.DataFrame(plac).to_string(index=False))
