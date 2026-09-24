# Lag profiles, reverse-time, placebos, LOEO, species tracking modes.
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "outputs", "tables")
os.makedirs(OUT, exist_ok=True)

ad = pd.read_parquet(os.path.join(PROC, "animal_day_model.parquet"),
                     engine="pyarrow")
ad["month"] = ad["date"].dt.month
ad["K"] = np.log1p(ad["chl"])
ad["E"] = ad["uwi"]
ad["y"] = np.log1p(ad["active_km"])

SPECIES = [s for s, g in ad.dropna(subset=["y", "uwi", "chl"]).groupby("species")
           if g["animal"].nunique() >= 5 and len(g) >= 800]

# ---------- lag profiles: per-animal shifted predictors, pooled OLS ----------
def lag_coef(d, formula, shifts, col_map):
    """col_map: {new_col: (base_col, shift_days)} computed per animal on the
    complete daily index already built in 04 (reindexed)."""
    out = []
    for sh in shifts:
        dd = d.copy()
        for nc, (bc, _) in col_map.items():
            dd[nc] = (dd.sort_values("date")
                      .groupby("animal")[bc].shift(-sh).values)
        ds = dd.dropna(subset=["y"] + list(col_map) + ["E", "month"])
        if len(ds) < 200:
            out.append(np.nan); continue
        try:
            m = smf.ols(formula, data=ds).fit()
            out.append(float(m.params.iloc[1]))
        except Exception:
            out.append(np.nan)
    return out

LAGS = list(range(-14, 15))
lag_rows = []
for sp in SPECIES:
    d = ad[ad["species"] == sp].copy()
    # E_t -> predator y_{t+lag}: coef of E predicting future/past y
    for L in LAGS:
        dd = d.copy()
        dd["y_lag"] = (dd.sort_values("date")
                       .groupby("animal")["y"].shift(-L))
        ds = dd.dropna(subset=["y_lag", "E", "month"])
        coef = np.nan
        if len(ds) > 200:
            try:
                coef = float(smf.ols("y_lag ~ E + sst_anom + C(month)",
                                     data=ds).fit().params["E"])
            except Exception:
                pass
        lag_rows.append({"species": sp, "link": "E->P", "lag": L,
                         "coef": coef})
        # prey -> predator: K_t predicting y_{t+lag}
        ds = dd.dropna(subset=["y_lag", "K", "month"])
        coef = np.nan
        if len(ds) > 200:
            try:
                coef = float(smf.ols("y_lag ~ K + sst_anom + C(month)",
                                     data=ds).fit().params["K"])
            except Exception:
                pass
        lag_rows.append({"species": sp, "link": "K->P", "lag": L,
                         "coef": coef})
        # E -> prey: E_t predicting chl_{t+lag}
        dd["K_lag"] = (dd.sort_values("date")
                       .groupby("animal")["K"].shift(-L))
        ds = dd.dropna(subset=["K_lag", "E"])
        coef = np.nan
        if len(ds) > 200:
            try:
                coef = float(smf.ols("K_lag ~ E + sst_anom + C(month)",
                                     data=ds).fit().params["E"])
            except Exception:
                pass
        lag_rows.append({"species": sp, "link": "E->K", "lag": L,
                         "coef": coef})
lagdf = pd.DataFrame(lag_rows)
lagdf.to_csv(os.path.join(OUT, "lag_results.csv"), index=False)
# peak lags
peak = (lagdf.dropna().groupby(["species", "link"])
        .apply(lambda g: g.loc[g["coef"].abs().idxmax(), "lag"], include_groups=False)
        .rename("peak_lag").reset_index())
peak.to_csv(os.path.join(OUT, "lag_peaks.csv"), index=False)

# ---------- reverse time: E leads y by +7d vs y leads E ----------
rev_rows = []
for sp in SPECIES:
    d = ad[ad["species"] == sp].copy()
    d["y_p7"] = d.sort_values("date").groupby("animal")["y"].shift(-7)
    d["y_m7"] = d.sort_values("date").groupby("animal")["y"].shift(7)
    for name, yc in [("E_t->P_t+7", "y_p7"), ("E_t->P_t-7_rev", "y_m7")]:
        ds = d.dropna(subset=[yc, "E", "sst_anom", "month"])
        if len(ds) < 200:
            continue
        try:
            m = smf.ols(f"{yc} ~ E + sst_anom + C(month)", data=ds).fit(
                cov_type="cluster", cov_kwds={"groups": ds["animal"]})
            rev_rows.append({"species": sp, "direction": name,
                             "E_coef": float(m.params["E"]),
                             "p": float(m.pvalues["E"]), "n": int(m.nobs)})
        except Exception:
            pass
pd.DataFrame(rev_rows).to_csv(os.path.join(OUT, "reverse_time_results.csv"),
                              index=False)

# ---------- placebos + LOEO ----------
pl_rows, loeo_rows = [], []
rng = np.random.default_rng(42)
for sp in SPECIES:
    d = ad[ad["species"] == sp].dropna(subset=["y", "E", "sst_anom", "month"]).copy()
    if len(d) < 300:
        continue
    base = smf.ols("y ~ E + sst_anom + C(month)", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["animal"]})
    bE = float(base.params["E"])
    # temporal placebos: uwi shifted +/-30d on station daily series approximated
    # by per-animal shift of the station-aligned uwi
    for sh, lab in [(-30, "uwi_m30"), (30, "uwi_p30")]:
        d["Ep"] = d.sort_values("date").groupby("animal")["E"].shift(-sh)
        ds = d.dropna(subset=["Ep"])
        try:
            m = smf.ols("y ~ Ep + sst_anom + C(month)", data=ds).fit()
            pl_rows.append({"species": sp, "placebo": lab,
                            "coef": float(m.params["Ep"]),
                            "observed": bE})
        except Exception:
            pass
    # spatial placebo: permute station->uwi mapping across animals within species
    d["uwi_perm"] = rng.permutation(d["E"].values)
    try:
        m = smf.ols("y ~ uwi_perm + sst_anom + C(month)", data=d).fit()
        pl_rows.append({"species": sp, "placebo": "uwi_permuted",
                        "coef": float(m.params["uwi_perm"]), "observed": bE})
    except Exception:
        pass
    # trophic placebo: SST used as pseudo-prey (biologically wrong layer)
    dk = ad[ad["species"] == sp].dropna(subset=["y", "K", "month"]).copy()
    dk["sst_pseudo"] = dk["sst"]
    try:
        m = smf.ols("y ~ sst_pseudo + E + C(month)", data=dk).fit()
        pl_rows.append({"species": sp, "placebo": "sst_as_prey",
                        "coef": float(m.params["sst_pseudo"]),
                        "observed": np.nan})
    except Exception:
        pass
    # event-intensity placebo: model y on |uwi| centred noise? use within-event
    # day index: response should not trend with days-since-start alone
    de = ad[(ad["species"] == sp) & ad["event_id"].notna()].copy()
    if len(de) > 100:
        ev_st = pd.read_csv(os.path.join(OUT, "independent_events.csv"),
                            parse_dates=["start_date"])[
            ["event_id", "start_date"]]
        de = de.merge(ev_st, on="event_id", how="left")
        de["t_in_ev"] = (pd.to_datetime(de["date"], utc=True).dt.tz_localize(None)
                         - pd.to_datetime(de["start_date"], utc=True)
                         .dt.tz_localize(None)).dt.days
        try:
            m = smf.ols("y ~ t_in_ev", data=de).fit()
            pl_rows.append({"species": sp, "placebo": "event_day_trend",
                            "coef": float(m.params["t_in_ev"]),
                            "observed": np.nan})
        except Exception:
            pass
    # LOEO on E->y
    evs = d["event_id"].dropna().unique()
    for e in evs:
        ds = d[d["event_id"] != e]
        if len(ds) < 300:
            continue
        try:
            m = smf.ols("y ~ E + sst_anom + C(month)", data=ds).fit()
            loeo_rows.append({"species": sp, "dropped_event": e,
                              "E_coef": float(m.params["E"])})
        except Exception:
            pass
pd.DataFrame(pl_rows).to_csv(os.path.join(OUT, "placebo_results.csv"),
                             index=False)
pd.DataFrame(loeo_rows).to_csv(os.path.join(OUT, "LOEO_results.csv"),
                              index=False)
print("lags", len(lagdf), "rev", len(rev_rows), "plac", len(pl_rows),
      "loeo", len(loeo_rows))
