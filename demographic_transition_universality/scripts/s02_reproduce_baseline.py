"""Reproduce the paper's core calendar-year result as a baseline.

Two things are reproduced from Itao (arXiv:2402.15697; EHS 2026):
  (1) A single calendar-year change point maximises the two-segment fit, and it falls near
      1950; adding further segments barely improves the fit (their Fig. 1A/1B).
  (2) The two segments are well described by the conserved quantities lambda*e0 (Phase I)
      and lambda*exp(e0/TAU_E0) (Phase II).

All numbers are written to results/ for the manuscript to read; nothing is hard-coded.
"""
import json
import os

import numpy as np

from common import RESULTS_DIR, TAU_E0, ensure_dirs, load_panel

# Candidate functional forms for a segment: lambda = C * basis(e0).
# "power" p  -> lambda = C / e0**p ;  "exp" c -> lambda = C / exp(e0/c)
POWER_EXPONENTS = [0.5, 1, 2, 3, 4, 5]
EXP_CONSTANTS = list(range(15, 26))


def _basis(e0, form, param):
    if form == "power":
        return 1.0 / (e0 ** param)
    return 1.0 / np.exp(e0 / param)


def _best_segment_fit(e0, y):
    """Fit the best single-parameter (through-origin) form to one segment; return SSE, form."""
    best = None
    for form, param in ([("power", p) for p in POWER_EXPONENTS]
                        + [("exp", c) for c in EXP_CONSTANTS]):
        x = _basis(e0, form, param)
        denom = float(np.dot(x, x))
        if denom <= 0:
            continue
        coef = float(np.dot(x, y) / denom)
        resid = y - coef * x
        sse = float(np.dot(resid, resid))
        if best is None or sse < best["sse"]:
            best = {"sse": sse, "form": form, "param": param, "coef": coef}
    return best


_SEG_CACHE = {}


def _segment_fit_cached(panel, lo, hi):
    """Cached best-form fit for the calendar segment [lo, hi); returns (sse, info) or None."""
    key = (lo, hi)
    if key in _SEG_CACHE:
        return _SEG_CACHE[key]
    seg = panel[(panel["year"] >= lo) & (panel["year"] < hi)]
    seg = seg[seg["e0"] > 30]
    if len(seg) < 20:
        _SEG_CACHE[key] = None
        return None
    fit = _best_segment_fit(seg["e0"].values, seg["lambda"].values)
    _SEG_CACHE[key] = fit
    return fit


def _segmentation_r2(panel, cut_years, tss):
    edges = [-10 ** 9] + sorted(cut_years) + [10 ** 9]
    sse = 0.0
    seg_info = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        fit = _segment_fit_cached(panel, lo, hi)
        if fit is None:
            return None
        sse += fit["sse"]
        seg_info.append({"lo": None if lo < -10 ** 8 else int(lo),
                         "hi": None if hi > 10 ** 8 else int(hi),
                         **{k: fit[k] for k in ("form", "param", "coef")}})
    return {"r2": 1.0 - sse / tss, "segments": seg_info}


def best_partition(panel, k, year_lo=1850, year_hi=2000, step=1):
    """Exhaustive search of the best (k-1) interior calendar cut years maximising total R^2."""
    from itertools import combinations
    y_all = panel["lambda"].values
    tss = float(np.sum((y_all - y_all.mean()) ** 2))
    candidate_years = list(range(year_lo, year_hi + 1, step))
    best = None
    if k == 1:
        res = _segmentation_r2(panel, [], tss)
        return {"k": 1, "cuts": [], **res}
    for cuts in combinations(candidate_years, k - 1):
        allc = [year_lo - 1] + list(cuts) + [year_hi + 1]
        if any(b - a < 15 for a, b in zip(allc[:-1], allc[1:])):
            continue
        res = _segmentation_r2(panel, list(cuts), tss)
        if res is None:
            continue
        if best is None or res["r2"] > best["r2"]:
            best = {"k": k, "cuts": list(cuts), **res}
    return best


def main():
    ensure_dirs()
    panel = load_panel()

    # R^2 as a function of the number of segments (their Fig. 1B). k=3,4 use a coarser
    # search grid to stay tractable.
    r2_by_k = {}
    partitions = {}
    for k in (1, 2):
        part = best_partition(panel, k)
        r2_by_k[k] = part["r2"]
        partitions[k] = part
    for k in (3, 4):
        part = best_partition(panel, k, year_lo=1870, year_hi=1990, step=2)
        r2_by_k[k] = part["r2"]
        partitions[k] = part

    best_cut = partitions[2]["cuts"][0]

    # Headline Phase I / Phase II conserved-quantity fits at the discovered split.
    pre = panel[(panel["year"] < best_cut) & (panel["e0"] > 40)]
    post = panel[(panel["year"] >= best_cut) & (panel["e0"] > 60)]
    # Phase I: lambda * e0 = C1  ->  regress lambda on 1/e0
    x1 = 1.0 / pre["e0"].values
    c1 = float(np.dot(x1, pre["lambda"].values) / np.dot(x1, x1))
    # Phase II: lambda * exp(e0/tau) = C2 -> regress lambda on 1/exp(e0/tau)
    x2 = 1.0 / np.exp(post["e0"].values / TAU_E0)
    c2 = float(np.dot(x2, post["lambda"].values) / np.dot(x2, x2))

    out = {
        "n_countries": int(panel["country"].nunique()),
        "n_obs": int(len(panel)),
        "year_min": int(panel["year"].min()),
        "year_max": int(panel["year"].max()),
        "r2_by_k": {str(k): v for k, v in r2_by_k.items()},
        "r2_gain_1_to_2": r2_by_k[2] - r2_by_k[1],
        "r2_gain_2_to_3": r2_by_k[3] - r2_by_k[2],
        "best_single_change_year": int(best_cut),
        "tau_e0": TAU_E0,
        "phaseI_const_lambda_e0": c1,
        "phaseII_const_lambda_exp": c2,
        "partitions": partitions,
    }
    with open(os.path.join(RESULTS_DIR, "baseline_calendar.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("n_countries", "n_obs", "r2_by_k", "best_single_change_year",
                       "phaseI_const_lambda_e0", "phaseII_const_lambda_exp")}, indent=2))


if __name__ == "__main__":
    main()
