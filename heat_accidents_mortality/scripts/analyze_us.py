#!/usr/bin/env python3
"""
US analysis: does ambient heat raise daily traffic-crash mortality (FARS)?

Time-series quasi-Poisson models on a state x day panel (2016-2022), adjusting
for state fixed effects, division-specific season (natural spline of day of
year), long-term trend and day of week:

  (A) Absolute-temperature model -> descriptive exposure-response (confounded by
      the seasonal driving-exposure envelope; peaks at mild temperatures).
  (B) Temperature-ANOMALY model (primary) -> effect of days hotter/colder than
      the local seasonal norm, decomposed over lag windows (same-day, 1-3 d,
      4-10 d). Isolates acute heat from the seasonal envelope.

All manuscript numbers derive from FARS + GHCN-Daily; nothing is hard-coded.
"""
import os
import numpy as np
import pandas as pd
from patsy import dmatrix
from model import (fit_model, cumulative_curve, bin_response, attributable,
                   project_warming, BINS, VAR_DF)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "output")
os.makedirs(OUT, exist_ok=True)

DIVISION = {
    9: 1, 23: 1, 25: 1, 33: 1, 44: 1, 50: 1,
    34: 2, 36: 2, 42: 2,
    17: 3, 18: 3, 26: 3, 39: 3, 55: 3,
    19: 4, 20: 4, 27: 4, 29: 4, 31: 4, 38: 4, 46: 4,
    10: 5, 11: 5, 12: 5, 13: 5, 24: 5, 37: 5, 45: 5, 51: 5, 54: 5,
    1: 6, 21: 6, 28: 6, 47: 6,
    5: 7, 22: 7, 40: 7, 48: 7,
    4: 8, 8: 8, 16: 8, 30: 8, 32: 8, 35: 8, 49: 8, 56: 8,
    2: 9, 6: 9, 15: 9, 41: 9, 53: 9,
}


def load_panel():
    fars = pd.read_csv(os.path.join(PROC, "fars_state_day.csv"), parse_dates=["date"])
    fars["state"] = fars.STATE.astype(int)
    temp = pd.read_csv(os.path.join(PROC, "state_day_temperature.csv"), parse_dates=["date"])
    temp["state"] = temp.state_fips.astype(int)

    # state-level annual controls (population, VMT)
    sc_path = os.path.join(PROC, "state_controls.csv")
    if os.path.exists(sc_path):
        sc = pd.read_csv(sc_path)
        sc["year"] = sc.year.astype(int)
        temp["year"] = temp.date.dt.year
        temp = temp.merge(sc[["state", "year", "population", "vmt_millions"]],
                          on=["state", "year"], how="left")
        temp = temp.drop(columns=["year"])

    # humidity / heat-stress metrics (GHCN-Daily ADPT/RHAV/AWBT)
    hum_path = os.path.join(PROC, "state_day_humidity.csv")
    if os.path.exists(hum_path):
        hum = pd.read_csv(hum_path, parse_dates=["date"])
        hum["state"] = hum.state_fips.astype(int)
        temp = temp.merge(hum[["state", "date", "humidex", "heat_index", "wbgt_est"]],
                          on=["state", "date"], how="left")

    states = sorted(set(fars.state) & set(temp.state))
    dates = pd.date_range(fars.date.min(), fars.date.max(), freq="D")
    grid = pd.MultiIndex.from_product([states, dates], names=["state", "date"]).to_frame(index=False)
    df = grid.merge(fars[["state", "date", "deaths"]], on=["state", "date"], how="left")
    df["deaths"] = df.deaths.fillna(0).astype(int)
    merge_cols = ["state", "date", "tmean", "prcp"]
    if "population" in temp.columns:
        merge_cols += ["population", "vmt_millions"]
    if "humidex" in temp.columns:
        merge_cols += ["humidex", "heat_index", "wbgt_est"]
    df = df.merge(temp[merge_cols], on=["state", "date"], how="left")
    df = df.sort_values(["state", "date"]).reset_index(drop=True)
    df["unit"] = df.state
    df["dow"] = df.date.dt.dayofweek
    df["doy"] = df.date.dt.dayofyear
    df["division"] = df.state.map(DIVISION)
    df["t_index"] = (df.date - df.date.min()).dt.days
    n0 = len(df); df = df.dropna(subset=["tmean"]).reset_index(drop=True)

    # seasonal climatology for temperature and any available heat-stress metrics
    clim_metrics = ["tmean"] + [c for c in ("humidex", "heat_index", "wbgt_est") if c in df.columns]
    parts = []
    for _, g in df.groupby("state"):
        g = g.sort_values("date").copy()
        B = np.asarray(dmatrix("cc(doy, df=6)", g, return_type="dataframe"))
        for m in clim_metrics:
            v = g[m].values
            ok = ~np.isnan(v)
            if ok.sum() > 6:
                g[f"clim_{m}"] = np.nan
                coef = np.linalg.lstsq(B[ok], v[ok], rcond=None)[0]
                g[f"clim_{m}"] = B @ coef
            else:
                g[f"clim_{m}"] = np.nan
        parts.append(g)
    df = pd.concat(parts).sort_values(["state", "date"]).reset_index(drop=True)
    df["anom"] = df.tmean - df.clim_tmean
    for m in clim_metrics:
        if f"clim_{m}" in df.columns and m != "tmean":
            df[f"{m}_anom"] = df[m] - df[f"clim_{m}"]
    print(f"panel: {len(df):,} state-days ({n0-len(df):,} dropped for missing temp), "
          f"{df.state.nunique()} states, {int(df.deaths.sum()):,} deaths")
    return df


def confounders(df, season_df=8):
    nyears = df.date.dt.year.nunique()
    return dmatrix("C(state) + C(division):cr(doy, df=%d) + cr(t_index, df=%d) + C(dow)"
                   % (season_df, 3 * nyears), df, return_type="dataframe")


def _std(x):
    """Z-score a pandas/numpy vector, returning a Series indexed like the input."""
    s = pd.Series(np.asarray(x), index=x.index if hasattr(x, "index") else None)
    mu, sd = s.mean(), s.std(ddof=0)
    return (s - mu) / (sd if sd > 0 else 1)


VIF_THRESHOLD = 5.0


def _vif(X, col):
    """Variance inflation factor for a single column of the design matrix."""
    if col not in X.columns:
        return np.nan
    y = X[col].values.astype(float)
    Xo = X.drop(columns=[col]).values.astype(float)
    Xo = np.column_stack([np.ones(len(Xo), dtype=float), Xo])
    coef, *_ = np.linalg.lstsq(Xo, y, rcond=None)
    pred = Xo @ coef
    ss_res = np.sum((y - pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return float(1.0 / max(1.0 - r2, 1e-12))


def _fit_vif_screened(df, exposure, confounder_fn, extra, offset, group, label,
                      vif_threshold=VIF_THRESHOLD):
    """Iteratively remove added controls whose VIF exceeds the threshold.

    Returns the final model, the VIF dict for retained controls, and a list of
    dropped variables with their pre-drop VIFs.
    """
    remaining = list(extra.columns)
    current_extra = extra.copy()
    dropped = []
    while remaining:
        m = fit_model(df, exposure, confounder_fn, extra=current_extra,
                      offset=offset, group=group)
        present = [c for c in remaining if c in m["X"].columns]
        if not present:
            dropped.extend(remaining)
            break
        vifs = {c: _vif(m["X"], c) for c in present}
        worst = max(vifs, key=vifs.get)
        if vifs[worst] <= vif_threshold:
            break
        dropped.append(f"{worst} (VIF={vifs[worst]:.1f})")
        remaining.remove(worst)
        current_extra = current_extra[remaining]
    m = fit_model(df, exposure, confounder_fn, extra=current_extra,
                  offset=offset, group=group)
    row, v = _sensitivity_row(m, label, remaining)
    row["dropped"] = "; ".join(dropped) if dropped else "none"
    return row, v, dropped


def _sensitivity_row(m, label, extra_cols=None):
    s0 = bin_response(m, 9.0, 0.0).iloc[0]
    s9 = cumulative_curve(m, [9.0], 0.0).iloc[0]
    vif = {}
    if extra_cols and "X" in m:
        for c in extra_cols:
            v = _vif(m["X"], c)
            if not np.isnan(v):
                vif[c] = v
    row = {
        "model": label,
        "sameday_RR_anom+9C": round(float(s0.rr), 3),
        "sameday_RR_lo": round(float(s0.lo), 3),
        "sameday_RR_hi": round(float(s0.hi), 3),
        "cumRR_anom+9C": round(float(s9.rr), 3),
        "cumRR_lo": round(float(s9.lo), 3),
        "cumRR_hi": round(float(s9.hi), 3),
    }
    if vif:
        row["max_control_VIF"] = round(max(vif.values()), 2)
    else:
        row["max_control_VIF"] = np.nan
    return row, vif


def main():
    df = load_panel()

    mabs = fit_model(df, "tmean", confounders, group="unit"); mabs["expname"] = "tmean"
    tgrid = np.linspace(*np.percentile(df.tmean, [0.5, 99.5]), 200)
    lo, hi = np.percentile(df.tmean, [1, 99])
    raw = np.array([mabs["cb"].cumulative_basis([t])[0] @ mabs["beta"] for t in tgrid])
    inr = (tgrid >= lo) & (tgrid <= hi)
    mmt = float(tgrid[np.where(inr)[0][np.argmin(raw[inr])]])
    cumulative_curve(mabs, tgrid, mmt).rename(columns={"x": "tmean"}).to_csv(
        os.path.join(PROC, "us_exposure_response_abs.csv"), index=False)

    m = fit_model(df, "anom", confounders, group="unit"); m["expname"] = "anom"
    agrid = np.linspace(*np.percentile(df.anom, [0.5, 99.5]), 200)
    cumulative_curve(m, agrid, 0.0).rename(columns={"x": "anom"}).to_csv(
        os.path.join(PROC, "us_anomaly_response.csv"), index=False)
    br = bin_response(m, 9.0, 0.0)
    br.to_csv(os.path.join(PROC, "us_lag_response.csv"), index=False)

    an_hot, sims_hot = attributable(m, "anom", ref=0.0, only="hot")
    y = m["d"].deaths.values; total = int(y.sum()); nyears = m["d"].date.dt.year.nunique()
    rr9 = cumulative_curve(m, [9.0], 0.0).iloc[0]; rr_same = br.iloc[0]

    res = {
        "total_deaths": total, "years": nyears,
        "mmt_abs_degC": round(mmt, 2), "dispersion_phi": round(float(m["phi"]), 3),
        "cumRR_anom+9C": round(float(rr9.rr), 3), "cumRR_anom+9C_lo": round(float(rr9.lo), 3),
        "cumRR_anom+9C_hi": round(float(rr9.hi), 3),
        "sameday_RR_anom+9C": round(float(rr_same.rr), 3),
        "sameday_RR_anom+9C_lo": round(float(rr_same.lo), 3),
        "sameday_RR_anom+9C_hi": round(float(rr_same.hi), 3),
        "net_heat_attributable_deaths": round(float(an_hot.sum()), 1),
        "net_heat_attributable_lo": round(float(np.percentile(sims_hot, 2.5)), 1),
        "net_heat_attributable_hi": round(float(np.percentile(sims_hot, 97.5)), 1),
        "net_heat_attributable_per_year": round(float(an_hot.sum() / nyears), 1),
        "net_heat_attributable_fraction_pct": round(float(100 * an_hot.sum() / total), 3),
    }
    for a in (3, 6, 9, 12):
        c = cumulative_curve(m, [float(a)], 0.0).iloc[0]
        res[f"net_cumRR_anom+{a}C"] = f"{c.rr:.3f} ({c.lo:.3f}-{c.hi:.3f})"

    proj = project_warming(m, "anom", [1.0, 2.0, 3.0])
    proj.to_csv(os.path.join(PROC, "us_projection.csv"), index=False)
    for _, r in proj.iterrows():
        res[f"warming+{int(r.delta_degC)}C_extra_deaths_per_year"] = \
            f"{r.extra_deaths_per_year:.0f} ({r.extra_lo:.0f}-{r.extra_hi:.0f})"

    sensitivity_rows = []
    vif_rows = []
    ctrl_path = os.path.join(PROC, "driving_controls.csv")
    if os.path.exists(ctrl_path):
        c = pd.read_csv(ctrl_path, parse_dates=["date"])
        cc = df.merge(c, on="date", how="left")
        extra = pd.DataFrame(index=df.index)
        for col in ("vmt", "gasoline"):
            extra[col] = _std(cc[col].values)
        mc = fit_model(df, "anom", confounders, extra=extra, group="unit")
        row, v = _sensitivity_row(mc, "with_national_VMT_gasoline", list(extra.columns))
        sensitivity_rows.append(row)
        for col, val in v.items():
            vif_rows.append({"model": row["model"], "variable": col, "VIF": round(val, 2)})

    if "population" in df.columns and df.population.notna().any():
        log_pop = np.log(df.population)

        # Staged state-level controls, adding one variable at a time to avoid
        # simultaneous inclusion of multiple highly correlated heat-stress metrics.
        base = pd.DataFrame(index=df.index)
        base["vmt_state"] = _std(df.vmt_millions)

        m_pop = fit_model(df, "anom", confounders, offset=log_pop, group="unit")
        row, _ = _sensitivity_row(m_pop, "with_population_offset")
        sensitivity_rows.append(row)

        m_vmt = fit_model(df, "anom", confounders, extra=base, offset=log_pop, group="unit")
        row, v = _sensitivity_row(m_vmt, "with_population_stateVMT", ["vmt_state"])
        sensitivity_rows.append(row)
        for col, val in v.items():
            vif_rows.append({"model": row["model"], "variable": col, "VIF": round(val, 2)})

        extra = base.copy(); extra["prcp"] = _std(df.prcp)
        m_prcp = fit_model(df, "anom", confounders, extra=extra, offset=log_pop, group="unit")
        row, v = _sensitivity_row(m_prcp, "with_population_stateVMT_prcp", ["vmt_state", "prcp"])
        sensitivity_rows.append(row)
        for col, val in v.items():
            vif_rows.append({"model": row["model"], "variable": col, "VIF": round(val, 2)})

        for metric, label in (("humidex_anom", "humidex"),
                              ("heat_index_anom", "heat_index"),
                              ("wbgt_est_anom", "wbgt")):
            if metric in df.columns and df[metric].notna().any():
                e2 = extra.copy()
                e2[metric] = _std(df[metric])
                m_h = fit_model(df, "anom", confounders, extra=e2, offset=log_pop, group="unit")
                extra_cols = ["vmt_state", "prcp", metric]
                row, v = _sensitivity_row(m_h,
                    f"with_population_stateVMT_prcp_{label}", extra_cols)
                sensitivity_rows.append(row)
                for col, val in v.items():
                    vif_rows.append({"model": row["model"], "variable": col, "VIF": round(val, 2)})

        # VIF-screened full-controls: begin with state VMT, precipitation and all
        # available heat-stress metrics, then iteratively drop the control with the
        # highest VIF until all retained controls have VIF < threshold.  Report
        # thresholds 5 and 10, plus an unscreened full-controls model, so the
        # manuscript can choose the most robust primary specification.
        vif_candidates = base.copy()
        vif_candidates["prcp"] = _std(df.prcp)
        for metric, label in (("humidex_anom", "humidex"),
                              ("heat_index_anom", "heat_index"),
                              ("wbgt_est_anom", "wbgt")):
            if metric in df.columns and df[metric].notna().any():
                vif_candidates[metric] = _std(df[metric])

        # Unscreened full-controls (free) model
        m_free = fit_model(df, "anom", confounders, extra=vif_candidates,
                           offset=log_pop, group="unit")
        free_row, free_vifs = _sensitivity_row(m_free, "with_population_stateVMT_prcp_VIFfree", list(vif_candidates.columns))
        free_row["dropped"] = "none"
        sensitivity_rows.append(free_row)
        for col, val in free_vifs.items():
            vif_rows.append({"model": free_row["model"], "variable": col, "VIF": round(val, 2)})

        # VIF thresholds 5 and 10
        vif_row5, v_vif5, dropped5 = _fit_vif_screened(
            df, "anom", confounders, vif_candidates, log_pop, "unit",
            "with_population_stateVMT_prcp_VIFscreened", vif_threshold=5.0)
        sensitivity_rows.append(vif_row5)
        for col, val in v_vif5.items():
            vif_rows.append({"model": vif_row5["model"], "variable": col, "VIF": round(val, 2)})

        vif_row10, v_vif10, dropped10 = _fit_vif_screened(
            df, "anom", confounders, vif_candidates, log_pop, "unit",
            "with_population_stateVMT_prcp_VIFscreened10", vif_threshold=10.0)
        sensitivity_rows.append(vif_row10)
        for col, val in v_vif10.items():
            vif_rows.append({"model": vif_row10["model"], "variable": col, "VIF": round(val, 2)})

        chosen = vif_row10
        res["sameday_RR_+9C_ctrl"] = chosen["sameday_RR_anom+9C"]
        res["sameday_RR_+9C_ctrl_lo"] = chosen["sameday_RR_lo"]
        res["sameday_RR_+9C_ctrl_hi"] = chosen["sameday_RR_hi"]
        res["cumRR_+9C_ctrl"] = chosen["cumRR_anom+9C"]
        res["cumRR_+9C_ctrl_lo"] = chosen["cumRR_lo"]
        res["cumRR_+9C_ctrl_hi"] = chosen["cumRR_hi"]
        res["max_control_VIF"] = chosen.get("max_control_VIF")
    elif sensitivity_rows:
        chosen = sensitivity_rows[0]
        res["sameday_RR_+9C_ctrl"] = chosen["sameday_RR_anom+9C"]
        res["sameday_RR_+9C_ctrl_lo"] = chosen["sameday_RR_lo"]
        res["sameday_RR_+9C_ctrl_hi"] = chosen["sameday_RR_hi"]
        res["cumRR_+9C_ctrl"] = chosen["cumRR_anom+9C"]
        res["cumRR_+9C_ctrl_lo"] = chosen["cumRR_lo"]
        res["cumRR_+9C_ctrl_hi"] = chosen["cumRR_hi"]
        res["max_control_VIF"] = chosen.get("max_control_VIF")

    if sensitivity_rows:
        pd.DataFrame(sensitivity_rows).to_csv(
            os.path.join(PROC, "us_sensitivity_controls.csv"), index=False)
    if vif_rows:
        pd.DataFrame(vif_rows).to_csv(
            os.path.join(PROC, "us_sensitivity_vif.csv"), index=False)

    dfy = m["d"].assign(an=an_hot, year=m["d"].date.dt.year)
    per_year = dfy.groupby("year").agg(deaths=("deaths", "sum"), heat_an=("an", "sum")).reset_index()
    per_year["heat_af_pct"] = 100 * per_year.heat_an / per_year.deaths
    per_year.to_csv(os.path.join(PROC, "us_attributable_by_year.csv"), index=False)
    pd.DataFrame([res]).to_csv(os.path.join(PROC, "us_attributable.csv"), index=False)

    with open(os.path.join(OUT, "us_model_summary.txt"), "w") as f:
        f.write(f"US temperature-anomaly distributed-lag model, bins={BINS}, var_df={VAR_DF}\n")
        f.write(f"observations: {len(y):,}  deaths: {total:,}  states: {m['d'].state.nunique()}\n")
        f.write(f"quasi-Poisson dispersion phi = {m['phi']:.3f}\n\n")
        f.write("Lag-window RR for a +9C anomaly vs seasonal norm:\n")
        for _, r in br.iterrows():
            f.write(f"  {r.window:9s}: {r.rr:.3f} ({r.lo:.3f}-{r.hi:.3f})\n")
        f.write("\n")
        for k, v in res.items():
            f.write(f"{k}: {v}\n")
    print(open(os.path.join(OUT, "us_model_summary.txt")).read())


if __name__ == "__main__":
    main()
