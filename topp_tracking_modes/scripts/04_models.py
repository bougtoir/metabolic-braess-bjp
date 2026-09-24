"""H1-H4 competing models + predictive-cueing test + event-held-out CV.

Outcome y = daily active displacement magnitude (|R| = |obs - advected|),
computed from consecutive-day fixes with vector current subtraction.
Predictors: uwi (E), sst_anom, chl (K, INDIRECT prey), predicted future chl
(Khat = CV prediction of chl_{t+8} ~ env_t, built per training fold to avoid
leakage).

Models per species:
  M_E   y ~ uwi + sst_anom
  M_K   y ~ chl
  M_EK  y ~ uwi + sst_anom + chl
  M_LAG y ~ uwi_l7 + chl_l7
  M_PREDICTIVE y ~ uwi + Khat_future
CV: leave-one-event-out (event_id groups) on event-window animal-days;
    fallback: animal-level fold split when a species lacks events.

Outputs: outputs/tables/model_comparison.csv, event_holdout_results.csv,
         future_prey_prediction.csv
"""
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "outputs/tables")
PROC = os.path.join(ROOT, "data/processed")

ad = pd.read_parquet(os.path.join(PROC, "animal_day_env.parquet"))

# active displacement: subtract integrated current (nearest grid, per day)
# displacement vector: lat/lon diff in km; advected = u,v * dt
ad = ad.sort_values(["animal", "date"])
ad["dlat"] = ad.groupby("animal")["lat"].diff()
ad["dlon360"] = ad.groupby("animal")["lon360"].diff()
consec = ad.groupby("animal")["date"].diff().dt.days == 1
ad["dy_km"] = np.where(consec, ad["dlat"] * 111.0, np.nan)
ad["dx_km"] = np.where(
    consec, ad["dlon360"] * 111.0 * np.cos(np.radians(ad["lat"])), np.nan)
ad["adv_x"] = ad["u_cur"] * 86400 / 1000   # km per day
ad["adv_y"] = ad["v_cur"] * 86400 / 1000
ad["Rx"] = ad["dx_km"] - ad["adv_x"]
ad["Ry"] = ad["dy_km"] - ad["adv_y"]
ad["active_km"] = np.sqrt(ad["Rx"] ** 2 + ad["Ry"] ** 2)
ad["active_ratio"] = ad["active_km"] / np.sqrt(ad["dx_km"] ** 2 + ad["dy_km"] ** 2)
ad["y"] = np.log1p(ad["active_km"])

# lagged env: uwi 7d before; future chl: chl at t+8d
ad["date_p8"] = ad["date"] + pd.Timedelta(days=8)
chl_map = ad[["date", "lat", "lon360", "chl"]].rename(
    columns={"date": "chl_date"})
# lag/future columns on a complete per-animal daily index (gap rows kept)
def fshift(g):
    g = g.set_index("date").sort_index()
    g = g[~g.index.duplicated()]
    g = g.reindex(pd.date_range(g.index.min(), g.index.max(), freq="D",
                                tz="UTC"))
    g.index.name = "date"
    g["chl_f8"] = g["chl"].shift(-8)
    g["uwi_l7"] = g["uwi"].shift(7)
    g["chl_l7"] = g["chl"].shift(7)
    return g.reset_index()
ad = ad.groupby("animal", group_keys=False).apply(
    fshift).reset_index(drop=True)
ad["animal"] = ad["animal"].ffill()  # reindex introduced NaN rows
ad["species"] = ad["species"].ffill()
ad = ad.dropna(subset=["lat"])  # drop reindex-only rows
ad.to_parquet(os.path.join(PROC, "animal_day_model.parquet"), index=False)

d = ad.dropna(subset=["y", "uwi", "chl"]).copy()
d["month"] = d["date"].dt.month
d["year"] = d["date"].dt.year
d["K"] = np.log1p(d["chl"])
d["E"] = d["uwi"]

SPECIES = [s for s, g in d.groupby("species")
           if g["animal"].nunique() >= 5 and len(g) >= 800]

MCOLS = {"E": "uwi + sst_anom", "K": "K", "EK": "uwi + sst_anom + K",
         "LAG": "uwi_l7 + chl_l7"}

rows, ho_rows, fp_rows = [], [], []
for sp in SPECIES:
    dd = d[d["species"] == sp].copy().reset_index(drop=True)
    # H4: predict future prey Khat_{t+8} from env_t, event-grouped CV
    dev = dd.dropna(subset=["chl_f8"])
    dev = dev[~dev["event_id"].isna()] if dev["event_id"].notna().sum() else dev
    groups = dev["event_id"].dropna().unique()
    if len(groups) < 3:
        groups = dd["animal"].unique()
        dev = dd.dropna(subset=["chl_f8"])
        gspl = "animal"
    else:
        gspl = "event_id"
    preds = pd.Series(np.nan, index=dev.index)
    for g in groups:
        tr = dev[dev[gspl] != g]
        te = dev[dev[gspl] == g]
        if len(tr) < 100 or len(te) < 3:
            continue
        try:
            m = smf.ols("np.log1p(chl_f8) ~ uwi + sst_anom", data=tr).fit()
            preds.loc[te.index] = m.predict(te)
        except Exception:
            pass
    dd["Khat"] = dd.index.to_series().map(preds)
    # predictability = CV corr of future prey ~ env
    ok = dev.dropna(subset=["chl_f8", "uwi"])
    ok = ok.loc[preds.dropna().index]
    if len(ok) > 50:
        fp_rows.append({"species": sp, "split": gspl, "n": len(ok),
                        "corr": float(np.corrcoef(np.log1p(ok["chl_f8"]),
                                                preds.loc[ok.index])[0, 1]),
                        "r2": float(np.corrcoef(np.log1p(ok["chl_f8"]),
                                                preds.loc[ok.index])[0, 1] ** 2)})

    # in-sample coefficients
    for name, form in {
            "M_E": "y ~ E + sst_anom + C(month)",
            "M_K": "y ~ K + C(month)",
            "M_EK": "y ~ E + sst_anom + K + C(month)",
            "M_LAG": "y ~ uwi_l7 + chl_l7 + C(month)",
            "M_PREDICTIVE": "y ~ E + sst_anom + Khat + C(month)",
    }.items():
        try:
            need = [c for c in ["y", "E", "sst_anom", "K", "uwi_l7", "chl_l7",
                                "Khat", "month", "animal"]
                    if c in form or c in ("y", "month", "animal")]
            ds = dd.dropna(subset=need)
            m = smf.ols(form, data=ds).fit(
                cov_type="cluster", cov_kwds={"groups": ds["animal"]})
            rows.append({"species": sp, "model": name, "n": int(m.nobs),
                         "r2": m.rsquared,
                         "E_coef": m.params.get("E", np.nan),
                         "K_coef": m.params.get("K", np.nan),
                         "Khat_coef": m.params.get("Khat", np.nan)})
        except Exception as ex:
            rows.append({"species": sp, "model": name, "n": 0,
                         "r2": np.nan, "E_coef": np.nan, "K_coef": np.nan,
                         "Khat_coef": np.nan})

    # event-holdout CV
    cv = dd.dropna(subset=["event_id"])
    evs = cv["event_id"].unique()
    if len(evs) < 3:
        cv = dd; evs = cv["animal"].unique(); gspl2 = "animal"
    else:
        gspl2 = "event_id"
    for g in evs:
        tr = cv[cv[gspl2] != g]
        te = cv[cv[gspl2] == g]
        if len(te) < 10 or len(tr) < 200:
            continue
        for name, form in {
                "M_E": "y ~ E + sst_anom + C(month)",
                "M_K": "y ~ K + C(month)",
                "M_EK": "y ~ E + sst_anom + K + C(month)",
                "M_PREDICTIVE": "y ~ E + sst_anom + Khat + C(month)",
        }.items():
            try:
                # rebuild Khat on training events only
                tr2 = tr.dropna(subset=["chl_f8"])
                mk = smf.ols("np.log1p(chl_f8) ~ uwi + sst_anom",
                             data=tr2).fit() if len(tr2) > 100 else None
                tt = te.copy(); rr = tr.copy()
                if mk is not None:
                    tt["Khat"] = mk.predict(tt)
                    rr = rr.copy()
                    rr.loc[:, "Khat"] = mk.predict(rr)
                m = smf.ols(form.replace(" + C(month)", ""), data=rr).fit()
                pr = m.predict(tt)
                ok = np.isfinite(pr) & np.isfinite(tt["y"])
                if ok.sum() < 10:
                    continue
                yv = tt["y"][ok]; pr = pr[ok]
                ho_rows.append({"species": sp, "split": gspl2,
                                "held_out": g, "model": name,
                                "rmse": float(np.sqrt(np.mean((yv - pr) ** 2))),
                                "corr": float(np.corrcoef(yv, pr)[0, 1])
                                if np.std(pr) > 0 else np.nan,
                                "n": int(ok.sum())})
            except Exception as ex:
                ho_rows.append({"species": sp, "split": gspl2,
                                "held_out": g, "model": name,
                                "rmse": np.nan, "corr": np.nan, "n": 0})

pd.DataFrame(rows).to_csv(os.path.join(OUT, "model_comparison.csv"), index=False)
pd.DataFrame(ho_rows).to_csv(os.path.join(OUT, "event_holdout_results.csv"),
                             index=False)
pd.DataFrame(fp_rows).to_csv(os.path.join(OUT, "future_prey_prediction.csv"),
                             index=False)
ho = pd.DataFrame(ho_rows)
print(ho.groupby(["species", "model"])["corr"].mean().unstack().round(3))
print(pd.DataFrame(fp_rows).to_string(index=False))
