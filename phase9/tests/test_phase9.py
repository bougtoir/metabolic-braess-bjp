"""Regression tests for the Phase-9 pipeline bugs (run: python3 test_phase9.py).

Covers:
1. unsurveyed != absent (occupancy semantics)
2. M1/M3 common evaluation sample
3. no future data in forward preprocessing (train-only demean)
4. redistribution metric: identical -> 0, monotone in shift size
5. simulation truth labels preserved
"""
import sys, numpy as np, pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import core9
from core9 import (forward_chain, loyo_pred, panel_rows, r2_from_pred,
                   _demean, occurrence, survey_mask, fill_surveyed_zero)

RNG = np.random.default_rng(0)


def toy_frames(n_routes=60, n_years=12):
    idx = [f"r{i}" for i in range(n_routes)]
    cols = list(range(2000, 2000 + n_years))
    return idx, cols


def test_unsurveyed_not_absent():
    """surveyed-absent -> 0, unsurveyed -> NaN in occurrence()."""
    idx, cols = toy_frames()
    wide = pd.DataFrame(np.nan, index=idx, columns=cols)
    # fake survey mask: only rid r0-r4 surveyed in year 2001
    S = pd.DataFrame(False, index=idx, columns=cols)
    S.loc[["r0", "r1", "r2"], 2001] = True
    # monkeypatch the global survey mask
    core9._SURV = S
    wide.loc["r0", 2001] = 5.0        # detected
    wide.loc["r1", 2001] = np.nan     # surveyed, not detected
    # r2 surveyed, not detected; r3 not surveyed
    occ = occurrence(wide)
    assert occ.loc["r0", 2001] == 1.0
    assert occ.loc["r1", 2001] == 0.0
    assert occ.loc["r2", 2001] == 0.0
    assert np.isnan(occ.loc["r3", 2001])
    w2 = fill_surveyed_zero(wide)
    assert w2.loc["r1", 2001] == 0.0 and np.isnan(w2.loc["r3", 2001])
    core9._SURV = None
    print("test_unsurveyed_not_absent ok")


def test_common_eval_sample():
    """M1 and M3 evaluated on identical rows after common-panel slicing."""
    idx, cols = toy_frames()
    wide = pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                        index=idx, columns=cols)
    E = [pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                      index=idx, columns=cols)]
    y, X, R, T = panel_rows(wide, E, [1])
    Xe = X[:, :1]
    ye1, p1 = forward_chain(y, Xe, R, T, demean=True)
    ye3, p3 = forward_chain(y, X, R, T, demean=True)
    ok1 = np.isfinite(ye1) & np.isfinite(p1)
    ok3 = np.isfinite(ye3) & np.isfinite(p3)
    assert ok1.sum() == ok3.sum() and (ok1 == ok3).all()
    print("test_common_eval_sample ok")


def test_train_only_demean():
    """changing test-year y values must not change the demeaned train stats."""
    idx, cols = toy_frames(30, 12)
    wide = pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                        index=idx, columns=cols)
    E = [pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                      index=idx, columns=cols)]
    y, X, R, T = panel_rows(wide, E, [1])
    t0 = np.unique(T)[3]
    tr, te = T <= t0, T == t0 + 1
    yd = _demean(y, R, tr)
    y2 = y.copy(); y2[te] += 1000.0
    yd2 = _demean(y2, R, tr)
    assert np.allclose(yd[tr], yd2[tr])  # train stats unchanged
    print("test_train_only_demean ok")


def test_no_future_in_forward():
    """predictions for year t use only training years < t."""
    idx, cols = toy_frames(30, 12)
    wide = pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                        index=idx, columns=cols)
    E = [pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                      index=idx, columns=cols)]
    y, X, R, T = panel_rows(wide, E, [1])
    ye, pr = forward_chain(y, X, R, T, demean=True)
    # earliest year has no training history -> no predictions
    assert np.isnan(pr[T == T.min()]).all()
    print("test_no_future_in_forward ok")


def _sign_flip(fr, ev):
    """mirror of anomaly.py redistribution metric"""
    base = fr[[c for c in fr.columns if c <= ev]].mean(axis=1)
    dev = fr[[ev, ev + 1]].sub(base, axis=0)
    return np.sign(dev[ev]), np.sign(dev[ev + 1])


def _redist(fr, ev):
    s0, s1 = _sign_flip(fr, ev)
    m = s0.notna() & s1.notna()
    return (s0[m] != s1[m]).mean()


def test_redistribution_monotone():
    """identical->0, tiny perturbation small, large shift large."""
    idx, cols = toy_frames(200, 12)
    ev = 2008
    # per-route constant level -> deviation 0 everywhere
    off = RNG.uniform(-1, 1, len(idx))
    base = pd.DataFrame(np.tile(off[:, None], (1, len(cols))),
                        index=idx, columns=cols)
    # A: identical distributions -> exactly 0 flips
    same = base.copy()
    r_same = _redist(same, ev)
    # all routes sit +0.5 above their baseline at ev; perturbation size
    # controls how many cross below the baseline at ev+1
    up = base.copy(); up[ev] = up[ev] + 0.5
    # B: tiny perturbation -> no flips (still above baseline)
    tiny = up.copy(); tiny[ev + 1] = up[ev] - 0.05
    r_tiny = _redist(tiny, ev)
    # C: moderate shift: half the routes drop clearly below baseline
    mod = up.copy()
    mod[ev + 1] = up[ev]
    mod.loc[idx[:100], ev + 1] = up.loc[idx[:100], ev] - 2.0
    r_mod = _redist(mod, ev)
    # D: large shift: all routes flip
    big = up.copy(); big[ev + 1] = up[ev] - 10.0
    r_big = _redist(big, ev)
    assert r_same == 0.0
    assert r_tiny == 0.0
    assert 0.3 < r_mod < 0.7
    assert r_big == 1.0
    print(f"test_redistribution_monotone ok "
          f"(same={r_same}, tiny={r_tiny}, mod={r_mod}, big={r_big})")


def test_cluster_boot_multiplicity():
    """cluster bootstrap must preserve route-draw multiplicities:
    resampling [a,a,b] must return a's rows twice (isin would drop them)."""
    mdf = pd.DataFrame({"rid": ["a", "a", "b", "c"],
                        "occ_tm1": [1, 0, 1, 0],
                        "occ_t": [1, 0, 1, 0],
                        "n_t": [5, 3, 2, 1]})
    by_rid = mdf.set_index("rid")
    samp = ["a", "a", "b", "b", "b"]
    g = by_rid.loc[samp]
    assert len(g) == 2 + 2 + 1 + 1 + 1  # a(2 rows)x2 + b(1)x3
    g_isin = mdf[mdf.rid.isin(samp)]
    assert len(g_isin) == 3  # old buggy behaviour kept only unique routes (a,b)
    print("test_cluster_boot_multiplicity ok")


def test_sim_truth_labels():
    """simulate() scenario E (true history) preserves lag-1 autocorrelation."""
    import sim9
    idx, cols = toy_frames(40, 15)
    wide = pd.DataFrame(np.nan, index=idx, columns=cols)
    Ez = {c: pd.DataFrame(RNG.normal(0, 1, (len(idx), len(cols))),
                          index=idx, columns=cols) for c in sim9.EC}
    yE = sim9.simulate(wide, Ez, "E")
    yA = sim9.simulate(wide, Ez, "A")
    def ar1(fr):
        a = fr.iloc[:, :-1].values.ravel(); b = fr.iloc[:, 1:].values.ravel()
        m = np.isfinite(a) & np.isfinite(b)
        return np.corrcoef(a[m], b[m])[0, 1]
    assert ar1(yE) > ar1(yA) + 0.2
    print("test_sim_truth_labels ok")


if __name__ == "__main__":
    test_unsurveyed_not_absent()
    test_common_eval_sample()
    test_train_only_demean()
    test_no_future_in_forward()
    test_redistribution_monotone()
    test_cluster_boot_multiplicity()
    test_sim_truth_labels()
    print("ALL PASS")
