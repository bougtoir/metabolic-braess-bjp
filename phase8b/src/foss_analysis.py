"""FOSS population-level history test. Station-year CPUE panels for prespecified
groundfish species; M0-M6 hierarchy, LOYO by year, HG/EG, decay, matched-env,
disequilibrium after environmental shifts."""
import numpy as np, pandas as pd
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
TAB = Path(__file__).resolve().parents[1] / "results" / "tables"
TAB.mkdir(parents=True, exist_ok=True)

SPP = ["walleye_pollock", "pacific_cod", "yellowfin_sole",
       "northern_rock_sole", "arrowtooth_flounder", "pacific_halibut"]

def loyo_r2(yM, Xmats, years):
    """Station-demeaned OLS; leave-one-year-out. yM: n_st x n_yr."""
    X = np.stack(Xmats, -1); n_s, T = yM.shape
    pred = np.full_like(yM, np.nan)
    for y in np.unique(years):
        tr = years != y; te = years == y
        yv = yM[:, tr].ravel(); Xv = X[:, tr].reshape(-1, X.shape[2])
        si = np.repeat(np.arange(n_s), tr.sum())
        m = np.isfinite(yv) & np.isfinite(Xv).all(1)
        yv, Xv, si = yv[m], Xv[m], si[m]
        cnt = np.bincount(si, minlength=n_s); cnt[cnt == 0] = 1
        ym = np.bincount(si, weights=yv, minlength=n_s) / cnt
        xm = np.stack([np.bincount(si, weights=Xv[:, j], minlength=n_s) / cnt
                       for j in range(X.shape[2])]).T
        beta, *_ = np.linalg.lstsq(Xv - xm[si], yv - ym[si], rcond=None)
        yte = yM[:, te].ravel(); Xte = X[:, te].reshape(-1, X.shape[2])
        si2 = np.repeat(np.arange(n_s), te.sum())
        pred[:, te] = ((Xte - xm[si2]) @ beta + ym[si2]).reshape(n_s, -1)
    yv, pv = yM.ravel(), pred.ravel()
    m = np.isfinite(yv) & np.isfinite(pv)
    return 1 - np.sum((yv[m] - pv[m]) ** 2) / np.sum((yv[m] - yv[m].mean()) ** 2)

def lagged(M, h):
    L = np.roll(M, h, axis=1)
    L[:, :h] = np.nan
    return L

def main():
    haul = pd.read_parquet(DATA / "foss" / "haul.parquet")
    haul = haul[haul.srvy.isin(["EBS", "GOA", "AI", "NBS", "BSS"])]
    haul = haul.dropna(subset=["station"])
    haul["station"] = haul.srvy + ":" + haul.station
    stations = sorted(haul.station.unique())
    years = np.arange(haul.year.min(), haul.year.max() + 1)
    si = {s: i for i, s in enumerate(stations)}
    yi = {y: i for i, y in enumerate(years)}
    n_s, T = len(stations), len(years)
    # effort + env surfaces
    effort = np.zeros((n_s, T)); BT = np.full((n_s, T), np.nan)
    ST = np.full((n_s, T), np.nan); DEP = np.full((n_s, T), np.nan)
    for r in haul.itertuples(index=False):
        i, j = si[r.station], yi[r.year]
        effort[i, j] += 1
        if pd.notna(r.bottom_temperature_c): BT[i, j] = r.bottom_temperature_c
        if pd.notna(r.surface_temperature_c): ST[i, j] = r.surface_temperature_c
        if pd.notna(r.depth_m): DEP[i, j] = r.depth_m
    print("stations", n_s, "years", T, "effort cells", (effort > 0).sum())
    rows, decay_rows, match_rows, shift_rows = [], [], [], []
    envshift = pd.Series(np.nanmean(BT, 0), index=years)
    envshift = (envshift - envshift.mean()) / envshift.std()
    shift_years = envshift[envshift.abs() > 1.0].index.tolist()
    print("env shift years:", shift_years)
    for sp in SPP:
        c = pd.read_parquet(DATA / "foss" / f"catch_{sp}.parquet")
        X = np.zeros((n_s, T))
        for r in c.itertuples(index=False):
            hj = r.hauljoin
            hh = haul[haul.hauljoin == hj]
            if len(hh) == 0: continue
            i, j = si[hh.station.iloc[0]], yi[hh.year.iloc[0]]
            X[i, j] += r.cpue_kgkm2 if pd.notna(r.cpue_kgkm2) else 0
        X[effort == 0] = np.nan
        # restrict to stations with >=15 sampled years for stability
        keep = np.isfinite(X).sum(1) >= 15
        X, BTs, STs, DEPs = X[keep], BT[keep], ST[keep], DEP[keep]
        lX = np.log1p(X)
        yv = np.array(years)
        L1, L2, L3, L5 = lagged(lX, 1), lagged(lX, 2), lagged(lX, 3), lagged(lX, 5)
        lagE1 = lagged(BTs, 1); lagE2 = lagged(BTs, 2)
        seas = np.zeros_like(lX)  # annual: no sub-annual season term
        r2 = {}
        r2["M0_static"] = loyo_r2(lX, [np.zeros_like(lX)], yv)
        r2["M1_env"] = loyo_r2(lX, [BTs, STs, DEPs], yv)
        r2["M2_hist"] = loyo_r2(lX, [L1], yv)
        r2["M3_env_hist"] = loyo_r2(lX, [BTs, STs, DEPs, L1], yv)
        r2["M4_mem"] = loyo_r2(lX, [BTs, STs, DEPs, L1, L2], yv)
        r2["M5_lagenv"] = loyo_r2(lX, [BTs, STs, DEPs, lagE1, lagE2], yv)
        r2["M6_full"] = loyo_r2(lX, [BTs, STs, DEPs, lagE1, lagE2, L1, L2], yv)
        HG = r2["M3_env_hist"] - r2["M1_env"]
        EG = r2["M3_env_hist"] - r2["M2_hist"]
        rows.append(dict(system="foss", species=sp, **r2, HG=HG, EG=EG))
        print(sp, "HG", round(HG, 3), "EG", round(EG, 3))
        for h, L in [(1, L1), (2, L2), (3, L3), (5, L5)]:
            d = loyo_r2(lX, [BTs, STs, DEPs, L], yv) - r2["M1_env"]
            decay_rows.append(dict(system="foss", species=sp, horizon=h, HG_h=d))
        # matched-environment: within station, bins where BT ~ median; compare
        # occupancy by prior-year occupancy
        occ = (X > 0).astype(float); occ[effort[keep] == 0] = np.nan
        bt_flat = BTs.ravel(); ok = np.isfinite(bt_flat)
        med = np.nanmedian(BTs)
        close = np.isfinite(BTs) & (np.abs(BTs - med) < 0.5)
        prev_occ = lagged(occ, 1)
        use, no_use = [], []
        for i in range(X.shape[0]):
            for t in range(1, T):
                if close[i, t] and np.isfinite(prev_occ[i, t]) and np.isfinite(occ[i, t]):
                    (use if prev_occ[i, t] > 0 else no_use).append(occ[i, t])
        match_rows.append(dict(system="foss", species=sp,
                               P_occ_given_prior=np.mean(use) if use else np.nan,
                               P_occ_given_no_prior=np.mean(no_use) if no_use else np.nan,
                               n_matched=len(use) + len(no_use)))
        # disequilibrium: distance obs vs env-only prediction after shift years
        # D_t = mean |obs - env_pred| post-shift vs baseline
        pred_env = np.full_like(lX, np.nan)
        Xs = np.stack([BTs, STs, DEPs], -1)
        for y in np.unique(yv):
            tr = yv != y; te = yv == y
            yvt = lX[:, tr].ravel(); Xvt = Xs[:, tr].reshape(-1, 3)
            siv = np.repeat(np.arange(lX.shape[0]), tr.sum())
            m = np.isfinite(yvt) & np.isfinite(Xvt).all(1)
            yvt, Xvt, siv = yvt[m], Xvt[m], siv[m]
            cnt = np.bincount(siv, minlength=lX.shape[0]); cnt[cnt == 0] = 1
            ym = np.bincount(siv, weights=yvt, minlength=lX.shape[0]) / cnt
            xm = np.stack([np.bincount(siv, weights=Xvt[:, j], minlength=lX.shape[0]) / cnt for j in range(3)]).T
            beta, *_ = np.linalg.lstsq(Xvt - xm[siv], yvt - ym[siv], rcond=None)
            si2 = np.repeat(np.arange(lX.shape[0]), te.sum())
            pred_env[:, te] = ((Xs[:, te].reshape(-1, 3) - xm[si2]) @ beta + ym[si2]).reshape(lX.shape[0], -1)
        D = np.abs(lX - pred_env)
        for yr in shift_years:
            if yr not in yi: continue
            j = yi[yr]
            if j + 3 < T:
                shift_rows.append(dict(system="foss", species=sp, shift_year=yr,
                                       anomaly_sd=envshift[yr],
                                       D_shift=np.nanmean(D[:, j]),
                                       D_post3=np.nanmean(D[:, j + 1:j + 4])))
    pd.DataFrame(rows).to_csv(TAB / "foss_history_gain.csv", index=False)
    pd.DataFrame(decay_rows).to_csv(TAB / "foss_memory_decay.csv", index=False)
    pd.DataFrame(match_rows).to_csv(TAB / "foss_matched_env.csv", index=False)
    pd.DataFrame(shift_rows).to_csv(TAB / "foss_shift_lag.csv", index=False)
    print("done")

if __name__ == "__main__":
    main()
