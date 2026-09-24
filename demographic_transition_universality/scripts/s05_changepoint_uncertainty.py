"""Uncertainty of the single calendar change point, and its relation to per-country onset.

The paper locates a single calendar change point "near 1950" by partitioning the pooled
lambda-e0 data into calendar segments, fitting each segment independently with its best form
(power law lambda=C/e0^p or exponential lambda=C/exp(e0/c)), and maximising the total R^2
(their Fig. 1A/B). We reproduce that objective and quantify how well-localised the single
change year is by (i) a nonparametric country bootstrap and (ii) a profile-likelihood posterior
over the change year. We then compare that single number with the empirical distribution of the
country-specific fertility-transition onsets, showing "1950" is the central summary of a broad,
heterogeneous mixture rather than a synchronous transition.

For speed, per-country cumulative sufficient statistics (through-origin fits) are precomputed so
each bootstrap replicate is a fast weighted sum.
"""
import json
import os

import numpy as np
import pandas as pd

from common import RESULTS_DIR, ensure_dirs, load_panel

CANDIDATE_YEARS = np.arange(1900, 1991)
POWER_EXPONENTS = [0.5, 1, 2, 3, 4, 5]
EXP_CONSTANTS = list(range(15, 26))
E0_MIN = 30.0  # the paper fits the segmentation on e0>30


def _forms(e0):
    cols = [1.0 / (e0 ** p) for p in POWER_EXPONENTS] + [1.0 / np.exp(e0 / c) for c in EXP_CONSTANTS]
    return np.column_stack(cols)  # (n_obs, n_forms)


def precompute(panel):
    panel = panel[panel["e0"] > E0_MIN]
    countries = sorted(panel["country"].unique())
    nc, nt = len(countries), len(CANDIDATE_YEARS)
    nf = len(POWER_EXPONENTS) + len(EXP_CONSTANTS)
    preXX = np.zeros((nc, nf, nt)); preXY = np.zeros((nc, nf, nt)); preY2 = np.zeros((nc, nt))
    totXX = np.zeros((nc, nf)); totXY = np.zeros((nc, nf)); totY2 = np.zeros(nc)
    for ci, c in enumerate(countries):
        g = panel[panel["country"] == c]
        e0 = g["e0"].values; y = g["lambda"].values; yr = g["year"].values
        X = _forms(e0)                       # (n, nf)
        xx = X ** 2; xy = X * y[:, None]     # (n, nf)
        totXX[ci] = xx.sum(0); totXY[ci] = xy.sum(0); totY2[ci] = (y ** 2).sum()
        for ti, t in enumerate(CANDIDATE_YEARS):
            pre = yr < t
            preXX[ci, :, ti] = xx[pre].sum(0)
            preXY[ci, :, ti] = xy[pre].sum(0)
            preY2[ci, ti] = (y[pre] ** 2).sum()
    return dict(countries=countries, preXX=preXX, preXY=preXY, preY2=preY2,
                totXX=totXX, totXY=totXY, totY2=totY2, n_obs=len(panel))


def _sse_curve(pc, w):
    """Total SSE for every candidate year given per-country weights w (best form per segment)."""
    preXX = np.tensordot(w, pc["preXX"], axes=(0, 0))   # (nf, nt)
    preXY = np.tensordot(w, pc["preXY"], axes=(0, 0))
    preY2 = w @ pc["preY2"]                              # (nt,)
    totXX = w @ pc["totXX"]; totXY = w @ pc["totXY"]; totY2 = w @ pc["totY2"]
    postXX = totXX[:, None] - preXX; postXY = totXY[:, None] - preXY; postY2 = totY2 - preY2
    with np.errstate(divide="ignore", invalid="ignore"):
        sse_pre = preY2[None, :] - np.where(preXX > 0, preXY ** 2 / preXX, 0.0)
        sse_post = postY2[None, :] - np.where(postXX > 0, postXY ** 2 / postXX, 0.0)
    return sse_pre.min(axis=0) + sse_post.min(axis=0)   # (nt,)


def main():
    ensure_dirs()
    panel = load_panel()
    onset = pd.read_csv(os.path.join(RESULTS_DIR, "country_onset.csv"))["t_fert"].dropna()
    pc = precompute(panel)
    nc = len(pc["countries"])

    # point estimate on the full sample
    sse_full = _sse_curve(pc, np.ones(nc))
    best_year = int(CANDIDATE_YEARS[np.argmin(sse_full)])

    # profile-likelihood posterior over the change year (flat prior)
    n = pc["n_obs"]
    loglik = -0.5 * n * np.log(sse_full / n)
    loglik -= loglik.max()
    post = np.exp(loglik); post /= post.sum()
    cdf = np.cumsum(post)
    post_lo = int(CANDIDATE_YEARS[np.searchsorted(cdf, 0.025)])
    post_hi = int(CANDIDATE_YEARS[min(np.searchsorted(cdf, 0.975), len(CANDIDATE_YEARS) - 1)])

    # country bootstrap of the single best change year
    rng = np.random.default_rng(0)
    n_boot = 2000
    boot_years = np.empty(n_boot, dtype=int)
    for b in range(n_boot):
        w = np.bincount(rng.integers(0, nc, size=nc), minlength=nc).astype(float)
        boot_years[b] = CANDIDATE_YEARS[np.argmin(_sse_curve(pc, w))]

    out = {
        "global_change_year_point_estimate": best_year,
        "global_change_year_posterior": {
            "mean": float(np.sum(CANDIDATE_YEARS * post)),
            "sd": float(np.sqrt(np.sum((CANDIDATE_YEARS - np.sum(CANDIDATE_YEARS * post)) ** 2 * post))),
            "credible95_lo": post_lo, "credible95_hi": post_hi,
        },
        "global_change_year_bootstrap": {
            "mean": float(boot_years.mean()), "sd": float(boot_years.std()),
            "ci95_lo": float(np.percentile(boot_years, 2.5)),
            "ci95_hi": float(np.percentile(boot_years, 97.5)), "n_boot": n_boot,
        },
        "per_country_onset": {
            "n": int(len(onset)), "min": int(onset.min()), "max": int(onset.max()),
            "median": float(onset.median()),
            "iqr": float(onset.quantile(.75) - onset.quantile(.25)), "sd": float(onset.std()),
            "frac_within_10y_of_1950": float(((onset - 1950).abs() <= 10).mean()),
            "frac_before_1930": float((onset < 1930).mean()),
            "frac_after_1970": float((onset > 1970).mean()),
        },
    }
    with open(os.path.join(RESULTS_DIR, "changepoint_posterior_curve.json"), "w") as f:
        json.dump({int(y): float(p) for y, p in zip(CANDIDATE_YEARS, post)}, f)
    with open(os.path.join(RESULTS_DIR, "changepoint_uncertainty.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
