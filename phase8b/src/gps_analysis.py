"""System A substitute: Banff/Ya Ha Tinda elk GPS, individual-level.
Panel: individual x month x EVI-grid-cell usage share.
History predictor: same-cell usage lag-1-month and lag-12-month.
Env per cell-month: EVI + snow cover. LOYO by year; unit-demeaned by
(individual, cell) to absorb static geography (M0 control).
Writes elk_history_gain.csv / memory_decay / matched_env / shift_lag."""
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
SPP = sys.argv[1] if len(sys.argv) > 1 else "elk"
GPS = ROOT / "data" / "gps" / (SPP + ".parquet")
REMOTE = ROOT.parents[0] / "banff_phase4" / "data" / "remote"
OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)

def loyo(y, X, unit, fold):
    y = np.asarray(y, float); X = np.asarray(X, float)
    ok = np.isfinite(y) & np.isfinite(X).all(1)
    y, X, unit, fold = y[ok], X[ok], unit[ok], fold[ok]
    if len(y) < 50: return np.nan
    # demean within unit
    s = pd.Series(y); yd = (s - s.groupby(unit).transform("mean")).values
    pred = np.full(len(y), np.nan)
    for f in np.unique(fold):
        tr, te = fold != f, fold == f
        if tr.sum() < X.shape[1] + 5 or te.sum() == 0: continue
        mu = X[tr].mean(0)
        beta, *_ = np.linalg.lstsq(np.c_[np.ones(tr.sum()), X[tr] - mu],
                                   yd[tr], rcond=None)
        pred[te] = np.c_[np.ones(te.sum()), X[te] - mu] @ beta
    ok = np.isfinite(pred)
    if np.sum(yd[ok] ** 2) == 0: return np.nan
    return 1 - np.sum((yd[ok] - pred[ok]) ** 2) / np.sum(yd[ok] ** 2)

def main():
    elk = pd.read_parquet(GPS)
    elk["t"] = pd.to_datetime(elk.timestamp, utc=True).dt.tz_convert(None)
    elk = elk.dropna(subset=["t"])
    evi_d = np.load(REMOTE / "evi.npz")
    lats, lons = evi_d["lats"], evi_d["lons"]
    # cell index for each fix
    iy = np.argmin(np.abs(lats[:, None] - elk["location-lat"].values), 0)
    ix = np.argmin(np.abs(lons[:, None] - elk["location-long"].values), 0)
    elk["cell"] = iy * len(lons) + ix
    elk["ym"] = elk.t.values.astype("datetime64[M]")
    # usage share per individual x ym x cell
    grp = elk.groupby(["individual-local-identifier", "ym", "cell"]).size()
    tot = elk.groupby(["individual-local-identifier", "ym"]).size()
    u = (grp / tot).rename("u").reset_index()
    u.columns = ["ind", "ym", "cell", "u"]
    u["ym"] = pd.PeriodIndex(u.ym, freq="M")
    # complete panel: every cell ever used by ind x every month ind was tracked
    frames = []
    for ind, di in u.groupby("ind"):
        months = pd.period_range(di.ym.min(), di.ym.max(), freq="M")
        grid = pd.MultiIndex.from_product([di.cell.unique(), months],
                                          names=["cell", "ym"]).to_frame(index=False)
        grid["ind"] = ind
        frames.append(grid.merge(di, on=["ind", "cell", "ym"], how="left"))
    u = pd.concat(frames)
    u["u"] = u.u.fillna(0.0)
    u = u[u.groupby(["ind", "ym"]).u.transform("sum") > 0]  # months with tracking
    # env per ym: ERA5 monthly mean temp + snowfall + precip over elk range
    # (cell-level EVI/snow ends 2011; monthly climate covers 2001-2020)
    envf = DATA = ROOT / "data" / "elk_env.parquet"
    if envf.exists():
        env = pd.read_parquet(envf)
    else:
        import urllib.request, json
        lat, lon = 51.5, -115.3  # centroid across Banff + Ya Ha Tinda elk fixes
        url = ("https://archive-api.open-meteo.com/v1/archive?"
               f"latitude={lat}&longitude={lon}&start_date=2001-01-01"
               "&end_date=2020-12-31&daily=temperature_2m_mean,"
               "precipitation_sum,snowfall_sum&timezone=UTC")
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)["daily"]
        env = pd.DataFrame({"date": pd.to_datetime(d["time"]),
                            "temp": d["temperature_2m_mean"],
                            "precip": d["precipitation_sum"],
                            "snowfall": d["snowfall_sum"]})
        env["ym"] = pd.PeriodIndex(env.date, freq="M")
        env = env.groupby("ym").agg(temp=("temp", "mean"),
                                    precip=("precip", "sum"),
                                    snowfall=("snowfall", "sum")).reset_index()
        env.to_parquet(envf)
    u = u.merge(env, on="ym", how="left")
    u = u.sort_values(["ind", "cell", "ym"])
    # history lags within ind x cell (months are consecutive in index space)
    u["ymi"] = u.ym.dt.year * 12 + u.ym.dt.month
    u["year"] = u.ym.dt.year
    for h in [1, 2, 3, 5, 12]:
        key = u.set_index(["ind", "cell", "ymi"]).u
        u[f"u_lag{h}"] = [key.get((i, c, m - h), np.nan)
                         for i, c, m in zip(u.ind, u.cell, u.ymi)]
    u["unit"] = u.ind.astype(str) + "|" + u.cell.astype(str)
    u = u[u.groupby("ind").ym.transform("nunique") >= 12]
    print("panel rows:", len(u), "indiv:", u.ind.nunique())

    envcols = ["temp", "precip", "snowfall"]
    # lagged env predictors (per month, shared across cells)
    for v in envcols:
        lagmap = env.set_index("ym")[v]
        u[v + "_lag"] = [lagmap.get(m - 1, np.nan) for m in u.ym]
    specs = {"M0": [], "M1": envcols, "M2": ["u_lag1"],
             "M3": envcols + ["u_lag1"],
             "M4": envcols + ["u_lag1", "u_lag12"],
             "M5": envcols + ["temp_lag", "precip_lag", "snowfall_lag"],
             "M6": envcols + ["temp_lag", "precip_lag", "snowfall_lag",
                              "u_lag1", "u_lag12"]}
    rows = []
    for ind, d in u.groupby("ind"):
        r = {"ind": ind, "n_rows": len(d)}
        for k, cols in specs.items():
            r[k] = loyo(d.u.values, d[cols].values if cols else np.zeros((len(d), 0)),
                        d.unit.values, d.year.values)
        r["HG"] = r["M3"] - r["M1"]; r["EG"] = r["M3"] - r["M2"]
        rows.append(r)
    hg = pd.DataFrame(rows); hg.to_csv(OUT / (SPP + "_history_gain.csv"), index=False)
    # decay
    dec = []
    for ind, d in u.groupby("ind"):
        for h in [1, 2, 3, 5, 12]:
            dec.append({"ind": ind, "horizon": h,
                        "oos": loyo(d.u.values, d[envcols + [f"u_lag{h}" if h != 12 else "u_lag12"]].values,
                                    d.unit.values, d.year.values)})
    pd.DataFrame(dec).to_csv(OUT / (SPP + "_memory_decay.csv"), index=False)
    # matched-env: months where cell EVI within 0.05 of cell's median -> compare
    # usage as f(prior-year same month usage)
    me = []
    for (ind, c), d in u.groupby(["ind", "cell"]):
        d = d.set_index("ymi")
        med = d.temp.median()
        for m in d.index[(d.temp - med).abs() < 0.5]:
            if (m - 12) in d.index:
                me.append({"ind": ind, "cell": c, "ym": m,
                           "u_t": d.loc[m, "u"], "u_tm12": d.loc[m - 12, "u"]})
    pd.DataFrame(me).to_csv(OUT / (SPP + "_matched_env.csv"), index=False)
    print(hg[["M1", "M2", "M3", "M4", "M5", "M6", "HG", "EG"]].describe())

if __name__ == "__main__":
    main()
