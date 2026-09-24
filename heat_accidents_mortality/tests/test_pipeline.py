import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
PROC = os.path.join(ROOT, "data", "processed")

from dlnm import DistLagBins, lag_matrix          # noqa: E402
from model import fit_poisson_irls                # noqa: E402
import build_japan as bj                          # noqa: E402


def test_dms_conversion():
    # 43 deg 02' 34.789" N  -> 43.0430...
    lat = bj.dms(pd.Series(["430234789"]), 2).iloc[0]
    assert abs(lat - (43 + 2 / 60 + 34.789 / 3600)) < 1e-6
    lon = bj.dms(pd.Series(["1412612831"]), 3).iloc[0]
    assert abs(lon - (141 + 26 / 60 + 12.831 / 3600)) < 1e-6


def test_lag_matrix_shifts():
    df = pd.DataFrame({"unit": [1, 1, 1, 2, 2], "date": pd.date_range("2020-01-01", periods=3).tolist()
                       + pd.date_range("2020-01-01", periods=2).tolist(),
                       "x": [10.0, 11.0, 12.0, 20.0, 21.0]})
    idx, lag = lag_matrix(df, "unit", "date", "x", 1)
    lag = lag[np.argsort(idx)]
    assert lag[0, 0] == 10.0 and np.isnan(lag[0, 1])   # first day, no lag-1
    assert lag[1, 1] == 10.0                            # lag-1 of day2 = day1


def _ar1(rng, n, phi=0.85, sd=4.0):
    """Autocorrelated series resembling daily temperature anomalies."""
    e = rng.normal(scale=sd, size=n)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = phi * x[i - 1] + e[i]
    return x


def test_crossbasis_full_rank_and_cumulative():
    rng = np.random.default_rng(0)
    x = _ar1(rng, 6000)
    cb = DistLagBins(x, [(0, 0), (1, 3), (4, 10)], var_df=3)
    df = pd.DataFrame({"unit": 1, "date": pd.date_range("2016-01-01", periods=len(x)), "x": x})
    idx, lagged = lag_matrix(df, "unit", "date", "x", cb.maxlag)
    lagged = lagged[np.argsort(idx)]
    B = cb.transform(lagged[~np.isnan(lagged).any(axis=1)])
    assert B.shape[1] == 3 * cb.vx
    # realistic autocorrelated exposure keeps the distributed-lag basis identifiable
    assert np.linalg.matrix_rank(B) == B.shape[1]
    # sustained exposure = sum of per-window bases at that value
    cum = cb.cumulative_basis([2.0])
    per = sum(cb.bin_basis([2.0], i) for i in range(3))
    assert np.allclose(cum, per)


def test_irls_recovers_poisson_slope():
    rng = np.random.default_rng(1)
    n = 20000
    x = rng.normal(size=n)
    X = np.column_stack([np.ones(n), x])
    y = rng.poisson(np.exp(0.5 + 0.3 * x))
    beta, cov, mu, pear = fit_poisson_irls(X, y)
    assert abs(beta[1] - 0.3) < 0.05
    assert np.all(np.isfinite(cov))


def test_result_outputs_finite():
    for f in ("us_attributable.csv", "us_lag_response.csv", "us_projection.csv",
              "us_subgroup_response.csv", "us_timeofday_response.csv"):
        p = os.path.join(PROC, f)
        if not os.path.exists(p):
            continue
        d = pd.read_csv(p)
        num = d.select_dtypes("number")
        assert np.isfinite(num.values).all()


def test_warming_projection_monotone_and_positive():
    """project_warming should give a positive, delta-increasing extra-death curve
    for a monotone-increasing heat exposure-response (synthetic check)."""
    from model import project_warming
    rng = np.random.default_rng(3)
    x = _ar1(rng, 4000)
    cb = DistLagBins(x, [(0, 0), (1, 3), (4, 10)], var_df=4)
    df = pd.DataFrame({"unit": 1, "date": pd.date_range("2016-01-01", periods=len(x)),
                       "anom": x, "deaths": 5})
    idx, lagged = lag_matrix(df, "unit", "date", "anom", cb.maxlag)
    lagged = lagged[np.argsort(idx)]
    full = ~np.isnan(lagged).any(axis=1)
    # positive slope of cumulative response wrt exposure
    beta = np.linalg.lstsq(cb.cumulative_basis(x[full]), 0.02 * x[full], rcond=None)[0]
    m = dict(cb=cb, beta=beta, cov=np.eye(len(beta)) * 1e-6,
             d=df.loc[df.index[full]])
    proj = project_warming(m, "anom", [1.0, 2.0, 3.0], nsim=50)
    assert (proj.extra_deaths_per_year > 0).all()
    assert proj.extra_deaths_per_year.is_monotonic_increasing
    assert np.isfinite(proj.values.astype(float)).all()
