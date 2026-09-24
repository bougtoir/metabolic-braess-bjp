"""simulation_false_positive: per system, rebuild one species' real
(unit x time) coverage mask + env matrices, simulate outcome under env-only
truth plus AR(1) observation-persistence noise, then count how often the
standard estimator reports HG = M3 - M1 > 0 (false positive)."""
import numpy as np, pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"; OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(0)

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

def run(name, Y, E, rho_obs=0.3, nrep=20):
    ns, nt = Y.shape
    hits, n, hits5, hgs = 0, 0, 0, []
    for rep in range(nrep):
        b = rng.normal(0, 1, E.shape[2])
        sim = np.einsum("ijk,k->ij", np.nan_to_num(E), b)
        obs = np.zeros((ns, nt)); obs[:, 0] = rng.normal(0, 1, ns)
        for t in range(1, nt):
            obs[:, t] = rho_obs * obs[:, t - 1] + rng.normal(0, np.sqrt(1 - rho_obs ** 2), ns)
        sim = sim + obs
        sim[~np.isfinite(Y)] = np.nan
        slag = np.roll(sim, 1, axis=1); slag[:, 0] = np.nan
        rows = pd.DataFrame({"s": np.repeat(np.arange(ns), nt),
                             "t": np.tile(np.arange(nt), ns),
                             "y": sim.ravel(), "e0": E[:, :, 0].ravel(),
                             "e1": E[:, :, 1].ravel(), "yl": slag.ravel()})
        m1 = loyo(rows.y, rows[["e0", "e1"]].values, rows.s.values, rows.t.values)
        m3 = loyo(rows.y, rows[["e0", "e1", "yl"]].values, rows.s.values, rows.t.values)
        if np.isfinite(m1) and np.isfinite(m3):
            n += 1; hg=m3-m1; hgs.append(hg); hits += hg > 0; hits5 += hg > 0.05
    return {"system": name, "rho_obs": rho_obs, "nrep": n,
            "P_HG_pos_envonly": hits / max(n, 1), "P_HG_gt_005_envonly": hits5 / max(n, 1), "median_HG_sim": float(np.median(hgs)) if hgs else np.nan, "p95_HG_sim": float(np.percentile(hgs,95)) if hgs else np.nan}

def foss_panel():
    haul = pd.read_parquet(ROOT / "data/foss/haul.parquet")
    catch = pd.read_parquet(ROOT / "data/foss/catch_walleye_pollock.parquet")
    haul["station"] = haul.srvy.astype(str) + ":" + haul.station.astype(str)
    haul["year"] = haul.year
    cpue = catch.groupby("hauljoin").cpue_kgkm2.sum()
    haul["y"] = haul.hauljoin.map(cpue).fillna(0)
    stations = haul.groupby("station").size()
    keep = stations[stations >= 15].index
    h = haul[haul.station.isin(keep)]
    Y = h.pivot_table(index="station", columns="year", values="y", aggfunc="sum")
    E = np.stack([h.pivot_table(index="station", columns="year",
                                values=v).reindex_like(Y).values
                  for v in ["bottom_temperature_c", "depth_m"]], axis=2)
    # subsample stations for speed
    idx = rng.choice(len(Y), min(500, len(Y)), replace=False)
    return Y.values[idx], E[idx]

def bbs_panel():
    f = ROOT / "data/bbs/bbs_parsed.parquet"
    if not f.exists(): return None, None
    d = pd.read_parquet(f)
    env = ROOT / "data/bbs/bbs_env.parquet"
    if not env.exists(): return None, None
    e = pd.read_parquet(env)
    d = d[d.AOU.astype(str) == "3160"].merge(e, left_on=["rid", "Year"],
                                             right_on=["rid", "year"])
    cov = d.groupby("rid").size()
    keep = cov[cov >= 15].index[:400]
    d = d[d.rid.isin(keep)]
    Y = d.pivot_table(index="rid", columns="year", values="n", aggfunc="sum")
    E = np.stack([d.pivot_table(index="rid", columns="year", values=v)
                  .reindex_like(Y).values for v in ["jun_t", "jun_p"]], axis=2)
    return Y.values, E

def elk_panel():
    f = ROOT / "results/tables/elk_history_gain.csv"
    # rebuild a representative mask: use GPS fix occupancy months x indiv
    e = pd.read_parquet(ROOT / "data/gps/elk.parquet")
    e["t"] = pd.to_datetime(e.timestamp, utc=True).dt.tz_convert(None)
    e["ym"] = e.t.values.astype("datetime64[M]")
    act = e.groupby(["individual-local-identifier", "ym"]).size()
    ids = act.groupby("individual-local-identifier").size()
    keep = ids[ids >= 24].index[:50]
    a = act.reset_index()
    a = a[a["individual-local-identifier"].isin(keep)]
    Y = a.pivot_table(index="individual-local-identifier", columns="ym",
                      values=0, aggfunc="sum")
    return Y.values, None

def main():
    rows = []
    for name, fn in [("foss", foss_panel), ("bbs", bbs_panel)]:
        try:
            Y, E = fn()
        except Exception as ex:
            print(name, "panel fail:", ex); continue
        if Y is None: continue
        if E is None:
            E = rng.normal(0, 1, (Y.shape[0], Y.shape[1], 2))
        E = np.nan_to_num(E)
        for rho in [0.0, 0.3]:
            rows.append(run(name, Y, E, rho_obs=rho))
        print(name, "done", flush=True)
    # elk: synthetic env on real coverage mask
    try:
        Y, _ = elk_panel()
        E = rng.normal(0, 1, (Y.shape[0], Y.shape[1], 2))
        for rho in [0.0, 0.3]:
            rows.append(run("elk_mask", Y, E, rho_obs=rho))
    except Exception as ex:
        print("elk fail", ex)
    pd.DataFrame(rows).to_csv(OUT / "simulation_false_positive.csv", index=False)
    print(pd.DataFrame(rows))

if __name__ == "__main__":
    main()
