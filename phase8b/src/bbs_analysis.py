"""BBS system: route-year species totals, June climate per route (Open-Meteo
ERA5 archive), M0-M6 LOYO model hierarchy, HG/EG, decay, matched-env,
shift-lag. Annual bins -> each bin is a year."""
import json, time, urllib.request, urllib.parse
import numpy as np, pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "bbs"
OUT = Path(__file__).resolve().parents[1] / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

def era5_june(lat, lon, y0=1997, y1=2024):
    """June mean temp / precip at one site per year via Open-Meteo archive."""
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point?"
           "parameters=T2M,PRECTOTCORR&community=AG"
           f"&longitude={lon}&latitude={lat}&start={y0}&end={y1}&format=JSON")
    with urllib.request.urlopen(url, timeout=60) as r:
        d = json.load(r)["properties"]["parameter"]
    tt = {int(k[:4]): v for k, v in d["T2M"].items() if k.endswith("06")}
    pp = {int(k[:4]): v for k, v in d["PRECTOTCORR"].items() if k.endswith("06")}
    df = pd.DataFrame({"year": sorted(tt), "jun_t": [tt[y] for y in sorted(tt)],
                       "jun_p": [pp.get(y) for y in sorted(tt)]})
    return df

def loyo_r2(y, X, years):
    """LOYO CV R2 of site-demeaned OLS."""
    y = np.asarray(y, float); X = np.asarray(X, float)
    years = np.asarray(years)
    ok = np.isfinite(y) & np.isfinite(X).all(1)
    y, X, years = y[ok], X[ok], years[ok]
    if len(y) < 30:
        return np.nan
    y = y - np.array([y[years == t].mean() for t in years])
    pred = np.full(len(y), np.nan)
    for t in np.unique(years):
        tr, te = years != t, years == t
        if tr.sum() < X.shape[1] + 5 or te.sum() == 0:
            continue
        Xd = np.c_[np.ones(tr.sum()), X[tr] - X[tr].mean(0)]
        yd = y[tr] - y[tr].mean()
        beta, *_ = np.linalg.lstsq(Xd, yd, rcond=None)
        pred[te] = np.c_[np.ones(te.sum()), X[te] - X[tr].mean(0)] @ beta
    ok = np.isfinite(pred)
    ss = 1 - np.sum((y[ok] - pred[ok]) ** 2) / np.sum(y[ok] ** 2)
    return ss

def main():
    bbs = pd.read_parquet(DATA / "bbs_parsed.parquet")
    top = pd.read_csv(DATA / "bbs_top_species.csv", header=None)[0].astype(str)
    coords = pd.read_csv(DATA / "route_coords.csv")
    # env: fetch June climate for routes with >=15 years coverage
    cov = bbs.groupby("rid").Year.nunique()
    keep_routes = cov[cov >= 15].index
    print("routes kept:", len(keep_routes), flush=True)
    envf = DATA / "bbs_env.parquet"
    chunk_dir = DATA / "env_chunks"; chunk_dir.mkdir(exist_ok=True)
    if envf.exists():
        env = pd.read_parquet(envf)
    else:
        done_ids = {p.stem for p in chunk_dir.glob("*.parquet")}
        for i, rid in enumerate(keep_routes):
            if rid in done_ids:
                continue
            c = coords[coords.rid == rid]
            if c.empty:
                continue
            try:
                e = era5_june(float(c.Latitude.iloc[0]), float(c.Longitude.iloc[0]))
                e["rid"] = rid
                e.to_parquet(chunk_dir / f"{rid}.parquet")
            except Exception:
                continue
            if i % 50 == 0:
                print(i, flush=True)
            time.sleep(0.15)
        env = pd.concat([pd.read_parquet(p) for p in chunk_dir.glob("*.parquet")])
        env.to_parquet(envf)
    hg_rows, dec_rows, me_rows, sl_rows = [], [], [], []
    for aou in top:
        d = bbs[bbs.AOU == aou][["rid", "Year", "n"]]
        d = d.merge(env, left_on=["rid", "Year"], right_on=["rid", "year"])
        if d.empty:
            continue
        wide = d.pivot_table(index="rid", columns="Year", values="n",
                             aggfunc="sum")
        Et = d.pivot_table(index="rid", columns="Year", values="jun_t")
        Ep = d.pivot_table(index="rid", columns="Year", values="jun_p")
        years = np.sort(d.Year.unique())
        # z-scored env anomalies per route
        Et = (Et - Et.mean(1).values[:, None])
        Ep = (Ep - Ep.mean(1).values[:, None])
        def M(yv, hist_lag, env_cols, years):
            Xr, yr, tr = [], [], []
            for rid in yv.index:
                for j, yy in enumerate(yv.columns):
                    tr.append(yy); yr.append(yv.loc[rid, yy])
                    row = []
                    for c in env_cols:
                        row.append(c.loc[rid, yy] if yy in c.columns else np.nan)
                    for h in hist_lag:
                        row.append(yv.loc[rid, yy - h] if (yy - h) in yv.columns
                                   else np.nan)
                    Xr.append(row)
            return loyo_r2(yr, np.array(Xr), tr)
        r = {"species": aou, "system": "bbs",
             "M0": M(wide, [], [] , years),
             "M1": M(wide, [], [Et, Ep], years),
             "M2": M(wide, [1], [], years),
             "M3": M(wide, [1], [Et, Ep], years),
             "M4": M(wide, [1, 2, 3], [Et, Ep], years),
             "M5": M(wide, [1], [Et, Ep,
                                 Et.shift(axis=1), Ep.shift(axis=1)], years),
             }
        r["M6"] = M(wide, [1, 2, 3],
                    [Et, Ep, Et.shift(axis=1), Ep.shift(axis=1)], years)
        r["HG"] = r["M3"] - r["M1"]; r["EG"] = r["M3"] - r["M2"]
        hg_rows.append(r)
        for h in [1, 2, 3, 5]:
            dec_rows.append({"species": aou, "horizon": h,
                             "oos": M(wide, [h], [Et, Ep], years)})
        # matched-env: years where June temp within 0.5C of route median
        occ = (wide > 0).astype(float)
        for rid in wide.index:
            bt = Et.loc[rid]
            med = bt.median()
            cy = bt.index[(bt - med).abs() < 0.5]
            for yy in cy:
                if yy - 1 in occ.columns:
                    me_rows.append({"species": aou, "rid": rid, "year": yy,
                                    "occ_t": occ.loc[rid, yy],
                                    "occ_tm1": occ.loc[rid, yy - 1]})
        # shift years: route-level June temp |anomaly|>1sd (anomaly per route)
        an = Et.abs().max(1)  # route's max |anomaly| already z-ish per route? no
        sd = Et.std(1)
        for rid in wide.index:
            sh = Et.loc[rid][(Et.loc[rid].abs() > sd[rid])].index
            for yy in sh:
                if yy + 1 in wide.columns:
                    sl_rows.append({"species": aou, "rid": rid, "year": yy,
                                    "cpue_shift": wide.loc[rid, yy + 1]
                                    - wide.loc[rid, yy]})
    pd.DataFrame(hg_rows).to_csv(OUT / "bbs_history_gain.csv", index=False)
    pd.DataFrame(dec_rows).to_csv(OUT / "bbs_memory_decay.csv", index=False)
    pd.DataFrame(me_rows).to_csv(OUT / "bbs_matched_env.csv", index=False)
    pd.DataFrame(sl_rows).to_csv(OUT / "bbs_shift_lag.csv", index=False)
    print(pd.DataFrame(hg_rows)[["species", "HG", "EG"]])

if __name__ == "__main__":
    main()
