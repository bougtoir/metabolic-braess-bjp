"""NEON small mammal (DP1.10072.001): site x month x species captures /
trap-nights, monthly resolution. M0-M6 LOYO with env = monthly mean temp +
precip (Open-Meteo ERA5) per site. Bin = site-month."""
import json, time, urllib.request
import numpy as np, pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data" / "neon"
OUT = Path(__file__).resolve().parents[1] / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

def era5_monthly(lat, lon, y0=2010, y1=2024):
    url = ("https://power.larc.nasa.gov/api/temporal/monthly/point?"
           "parameters=T2M,PRECTOTCORR&community=AG&"
           f"longitude={lon}&latitude={lat}&start={y0}&end={y1}&format=JSON")
    with urllib.request.urlopen(url, timeout=60) as r:
        p = json.load(r)["properties"]["parameter"]
    ks = [k for k in p["T2M"] if 1 <= int(k[4:]) <= 12]
    t = pd.PeriodIndex(sorted(ks), freq="M")
    get = lambda d, k: np.nan if d.get(k, -999) <= -900 else d[k]
    return pd.DataFrame({"ym": t,
                         "t": [get(p["T2M"], k) for k in t.strftime("%Y%m")],
                         "p": [get(p["PRECTOTCORR"], k) for k in t.strftime("%Y%m")]})

SITES = {  # NEON terrestrial site coords (decimal deg) for sites w/ small-mammal data
}

def loyo(y, X, unit, fold):
    y = np.asarray(y, float); X = np.asarray(X, float)
    ok = np.isfinite(y) & np.isfinite(X).all(1)
    y, X, unit, fold = y[ok], X[ok], unit[ok], fold[ok]
    if len(y) < 50: return np.nan
    yd = (pd.Series(y) - pd.Series(y).groupby(unit).transform("mean")).values
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
    caps = sorted((DATA / "cap_chunks").glob("*.parquet"))
    cap = pd.concat([pd.read_parquet(f) for f in caps], ignore_index=True)
    eff = pd.concat([pd.read_parquet(f) for f in
                     sorted((DATA / "eff_chunks").glob("*.parquet"))],
                    ignore_index=True) if (DATA / "eff_chunks").exists() else pd.DataFrame()
    cap["ym"] = pd.PeriodIndex(pd.to_datetime(cap.collectDate), freq="M")
    cap = cap[cap.taxonID.str.len() >= 4]
    cnt = cap.groupby(["siteID", "ym", "taxonID"]).size().rename("n")
    # species selection: top by site-month prevalence
    prev = cnt.reset_index().groupby("taxonID").size().sort_values(ascending=False)
    top = prev.head(6).index.tolist()
    print("top:", top)
    # site coords: use NEON site table via api
    TOKEN = (DATA / "token.txt").read_text().strip()
    envf = DATA / "neon_env.parquet"
    if envf.exists():
        env = pd.read_parquet(envf)
    else:
        req = urllib.request.Request("https://data.neonscience.org/api/v0/locations/sites",
                                     headers={"X-API-Token": TOKEN})
        with urllib.request.urlopen(req, timeout=60) as r:
            loc = json.load(r)["data"]
        coords = {x["siteCode"]: (float(x["locationDecimalLatitude"]),
                                  float(x["locationDecimalLongitude"]))
                  for x in loc if "locationDecimalLatitude" in x}
        cd_ = DATA / "neon_env_chunks"; cd_.mkdir(exist_ok=True)
        rows = []
        for site in cnt.reset_index().siteID.unique():
            if site not in coords: continue
            cf = cd_ / f"{site}.parquet"
            if cf.exists():
                rows.append(pd.read_parquet(cf)); continue
            lat, lon = coords[site]
            try:
                e = era5_monthly(lat, lon)
            except Exception as ex:
                print("env fail", site, ex); continue
            e["siteID"] = site
            e.to_parquet(cf); rows.append(e); time.sleep(0.2)
        env = pd.concat(rows, ignore_index=True)
        env["ym"] = pd.PeriodIndex(env.ym, freq="M")
        env.to_parquet(envf)
    c = cnt.reset_index().merge(env, on=["siteID", "ym"])
    hg_rows, dec_rows, me_rows = [], [], []
    for sp in top:
        d = c[c.taxonID == sp]
        wide = d.pivot_table(index="siteID", columns="ym", values="n", aggfunc="sum")
        Et = d.pivot_table(index="siteID", columns="ym", values="t")
        Ep = d.pivot_table(index="siteID", columns="ym", values="p")
        # demean env per site (anomaly)
        Et = Et.sub(Et.mean(1), axis=0); Ep = Ep.sub(Ep.mean(1), axis=0)
        yms = list(wide.columns)
        ymi = {m: m.year * 12 + m.month for m in yms}
        def M(env_frames, lags):
            Y, X, U, F = [], [], [], []
            for s in wide.index:
                for m in wide.columns:
                    Y.append(wide.loc[s, m]); U.append(s); F.append(m.year)
                    row = [fr.loc[s, m] if (s in fr.index and m in fr.columns) else np.nan
                           for fr in env_frames]
                    mm = pd.PeriodIndex([m], freq="M")[0]
                    for h in lags:
                        pm = mm - h
                        row.append(wide.loc[s, pm] if pm in wide.columns else np.nan)
                    X.append(row)
            return loyo(Y, np.array(X), np.array(U), np.array(F))
        r = {"species": sp, "system": "neon",
             "M0": M([], []), "M1": M([Et, Ep], []), "M2": M([], [1]),
             "M3": M([Et, Ep], [1]), "M4": M([Et, Ep], [1, 12]),
             "M5": M([Et, Ep, Et.shift(axis=1), Ep.shift(axis=1)], []),
             "M6": M([Et, Ep, Et.shift(axis=1), Ep.shift(axis=1)], [1, 12])}
        r["HG"] = r["M3"] - r["M1"]; r["EG"] = r["M3"] - r["M2"]
        hg_rows.append(r)
        for h in [1, 2, 3, 6, 12]:
            dec_rows.append({"species": sp, "horizon": h,
                             "oos": M([Et, Ep], [h])})
        for s in wide.index:
            bt = Et.loc[s]; med = bt.median()
            for m in bt.index[(bt - med).abs() < 1.0]:
                pm = m - 1
                if pm in wide.columns:
                    me_rows.append({"species": sp, "site": s, "ym": str(m),
                                    "n_t": wide.loc[s, m],
                                    "n_tm1": wide.loc[s, pm]})
    pd.DataFrame(hg_rows).to_csv(OUT / "neon_history_gain.csv", index=False)
    pd.DataFrame(dec_rows).to_csv(OUT / "neon_memory_decay.csv", index=False)
    pd.DataFrame(me_rows).to_csv(OUT / "neon_matched_env.csv", index=False)
    print(pd.DataFrame(hg_rows)[["species", "HG", "EG"]])

if __name__ == "__main__":
    main()
