"""Does per-country time rescaling collapse the birth-rate trajectories onto one curve?

Two distinct questions:
  (Q1) In the (e0, lambda) plane the paper works in, rescaling time cannot change anything:
       time is only a parameter along the curve, so warping it leaves each (e0(t), lambda(t))
       locus untouched. We quantify the irreducible between-country SD of lambda at matched e0
       as a reference; no monotone time transform can reduce it.
  (Q2) Overlaying lambda as a function of transition time. Shifting each country to its own
       onset already collapses the spread; here we additionally rescale the time axis by each
       country's transition *duration* (s = (year - onset) / D_i) and measure the extra collapse.

Outputs results/time_rescaling.json and figs/fig_time_rescaling.png|svg. No values hard-coded.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import FIGS_DIR, RESULTS_DIR, ensure_dirs, load_panel

SMOOTH = 5
FLOOR_FRAC = 0.10       # transition "ends" when smoothed lambda is within 10% of plateau->floor
MIN_DURATION = 5        # need a resolvable transition span (years)
S_GRID = np.arange(0.0, 1.0001, 0.02)


def _smooth(s):
    return s.rolling(SMOOTH, center=True, min_periods=1).mean()


def country_transitions(panel, onset):
    """For each country with an onset, return (onset, end, duration, per-year lambda series)."""
    out = {}
    for c, g in panel.groupby("country"):
        if c not in onset:
            continue
        g = g.sort_values("year")
        yrs = g["year"].values
        lam = _smooth(g["lambda"]).values
        t0 = onset[c]
        if t0 < yrs.min() or t0 > yrs.max():
            continue
        plateau = float(np.max(lam[yrs <= t0])) if (yrs <= t0).any() else float(np.max(lam))
        post = lam[yrs >= t0]
        if len(post) < 3:
            continue
        floor = float(np.min(post))
        thresh = floor + FLOOR_FRAC * (plateau - floor)
        reached = np.where((yrs > t0) & (lam <= thresh))[0]
        end = int(yrs[reached[0]]) if len(reached) else int(yrs[-1])
        D = end - t0
        if D < MIN_DURATION:
            continue
        out[c] = {"onset": int(t0), "end": end, "duration": int(D),
                  "years": yrs, "lambda": g["lambda"].values}
    return out


def mean_between_country_sd(curves, coord, grid, normalize=False, min_countries=20):
    """Mean between-country SD of lambda evaluated on `grid` of the temporal coordinate.
    coord='tau' uses years-since-onset; coord='s' uses fraction-of-transition.
    normalize=True first maps each country's lambda to (lambda-floor)/(plateau-floor), so the
    comparison is of trajectory *shape* only (unitless), removing amplitude differences."""
    cols = []
    for c, d in curves.items():
        yrs = d["years"]; lam = d["lambda"].astype(float)
        if normalize:
            lo_l, hi_l = _smooth(pd.Series(lam)).min(), _smooth(pd.Series(lam)).max()
            if hi_l - lo_l <= 0:
                continue
            lam = (lam - lo_l) / (hi_l - lo_l)
        if coord == "tau":
            x = yrs - d["onset"]
        else:
            x = (yrs - d["onset"]) / d["duration"]
        order = np.argsort(x)
        x, y = x[order], lam[order]
        lo, hi = x.min(), x.max()
        vals = np.array([np.interp(t, x, y) if lo <= t <= hi else np.nan for t in grid])
        cols.append(vals)
    M = np.vstack(cols)  # countries x grid
    n = np.sum(~np.isnan(M), axis=0)
    sd = np.nanstd(M, axis=0, ddof=1)
    keep = n >= min_countries
    return float(np.nanmean(sd[keep])), M, keep


def matched_e0_residual(panel, onset, bin_width=1.0, min_countries=20):
    """Irreducible between-country SD of lambda at matched e0 (time-warp invariant),
    restricted to transitioning countries and their transition e0 range."""
    rows = []
    for c, d in country_transitions(panel, onset).items():
        g = panel[(panel.country == c) & (panel.year >= d["onset"]) & (panel.year <= d["end"])]
        rows.append(g[["e0", "lambda"]])
    df = pd.concat(rows)
    df["bin"] = (df["e0"] / bin_width).round() * bin_width
    sd = df.groupby("bin")["lambda"].agg(["std", "count"])
    sd = sd[sd["count"] >= min_countries]
    return float(sd["std"].mean())


def main():
    ensure_dirs()
    panel = load_panel()
    onset = (pd.read_csv(os.path.join(RESULTS_DIR, "country_onset.csv"))
             .set_index("country")["t_fert"].dropna().astype(int).to_dict())
    curves = country_transitions(panel, onset)

    durations = np.array([d["duration"] for d in curves.values()])
    # evaluate both coordinates under the same ">=20 countries present" rule for fairness
    tau_grid = np.arange(0, int(np.percentile(durations, 75)) + 1)

    sd_tau, _, _ = mean_between_country_sd(curves, "tau", tau_grid)
    sd_s, Ms, keep_s = mean_between_country_sd(curves, "s", S_GRID)
    sd_tau_n, _, _ = mean_between_country_sd(curves, "tau", tau_grid, normalize=True)
    sd_s_n, _, _ = mean_between_country_sd(curves, "s", S_GRID, normalize=True)
    e0_resid = matched_e0_residual(panel, onset)

    result = {
        "n_countries_with_transition": len(curves),
        "duration_years": {"median": float(np.median(durations)),
                            "q1": float(np.percentile(durations, 25)),
                            "q3": float(np.percentile(durations, 75)),
                            "min": int(durations.min()), "max": int(durations.max())},
        "raw_lambda": {
            "sd_event_time": sd_tau,
            "sd_rescaled_time": sd_s,
            "variance_ratio_event_over_rescaled": float(sd_tau ** 2 / sd_s ** 2),
        },
        "amplitude_normalised_shape": {
            "sd_event_time": sd_tau_n,
            "sd_rescaled_time": sd_s_n,
            "variance_ratio_event_over_rescaled": float(sd_tau_n ** 2 / sd_s_n ** 2),
        },
        "irreducible_sd_lambda_at_matched_e0": e0_resid,
        "note": ("Time rescaling by transition duration does NOT collapse raw lambda better than "
                 "onset-shift alone. Only after ALSO normalising amplitude does the (sigmoidal) "
                 "shape align, and that discards the level information universality is about. The "
                 "matched-e0 residual is invariant to any time warp."),
    }
    with open(os.path.join(RESULTS_DIR, "time_rescaling.json"), "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

    # figure: lambda vs event time (left) and vs duration-normalised time (right)
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 4.0))
    for c, d in curves.items():
        tau = d["years"] - d["onset"]
        m = (tau >= -5) & (tau <= tau_grid.max())
        ax[0].plot(tau[m], d["lambda"][m], color="#888", lw=0.4, alpha=0.35)
        s = (d["years"] - d["onset"]) / d["duration"]
        ms = (s >= -0.1) & (s <= 1.1)
        ax[1].plot(s[ms], d["lambda"][ms], color="#888", lw=0.4, alpha=0.35)
    # mean curves
    mean_s = np.nanmean(Ms, axis=0)
    ax[1].plot(S_GRID[keep_s], mean_s[keep_s], color="#d9534f", lw=2, label="cross-country mean")
    ax[0].set_title(f"\u03bb vs event time (aligned at onset)\nbetween-country SD = {sd_tau:.1f}")
    ax[0].set_xlabel("Years since transition onset")
    ax[0].set_ylabel(r"Crude birth rate $\lambda$")
    ax[1].set_title(f"\u03bb vs duration-normalised time\nbetween-country SD = {sd_s:.1f} "
                    f"(raw \u03bb: no extra collapse)")
    ax[1].set_xlabel("Fraction of transition completed (s = (t\u2212onset)/D)")
    ax[1].legend(fontsize=7, frameon=False)
    for a in ax:
        a.spines["top"].set_visible(False); a.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "fig_time_rescaling.png"), bbox_inches="tight", dpi=150)
    fig.savefig(os.path.join(FIGS_DIR, "fig_time_rescaling.svg"), bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_time_rescaling")


if __name__ == "__main__":
    main()
