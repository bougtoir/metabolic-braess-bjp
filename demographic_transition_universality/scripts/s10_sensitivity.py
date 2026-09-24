"""Sensitivity of the two headline findings to the exploratory onset definition.

We vary the fertility-decline threshold (FERT_DROP) and the smoothing window (SMOOTH) and, for
each combination, recompute (i) the dispersion of the country onset distribution and (ii) the
event-time variance-reduction ratio (the collapse of between-country lambda dispersion when
countries are aligned at their own onset rather than at 1950). Robustness of both to these
choices guards against the criticism that the results are an artefact of one tuning.
"""
import json
import os

import numpy as np
import pandas as pd

from common import RESULTS_DIR, ensure_dirs, load_panel

CALENDAR_SPLIT = 1950
FERT_DROPS = [0.05, 0.10, 0.15, 0.20]
SMOOTHS = [3, 5, 7, 9]
WINDOW = 25
MIN_PLATEAU_YEARS = 10


def fertility_onset(g, fert_drop, smooth):
    g = g.sort_values("year")
    yrs = g["year"].values
    lam = g["lambda"].rolling(smooth, center=True, min_periods=1).mean().values
    if len(lam) < MIN_PLATEAU_YEARS:
        return np.nan
    threshold = (1 - fert_drop) * float(np.max(lam))
    above = np.where(lam >= threshold)[0]
    if len(above) == 0 or above[-1] == len(lam) - 1:
        return np.nan
    return int(yrs[above[-1] + 1])


def collapse_ratio(panel, onset):
    ev = panel.copy()
    ev["t"] = ev["country"].map(onset)
    ev = ev.dropna(subset=["t"])
    ev["tau"] = ev["year"] - ev["t"]
    ev_win = ev[(ev["tau"] >= -WINDOW) & (ev["tau"] <= WINDOW)]
    sd_event = ev_win.groupby("tau")["lambda"].std().mean()
    cal = panel[(panel["year"] >= CALENDAR_SPLIT - WINDOW) & (panel["year"] <= CALENDAR_SPLIT + WINDOW)]
    sd_cal = cal.groupby("year")["lambda"].std().mean()
    return float(sd_cal ** 2 / sd_event ** 2)


def main():
    ensure_dirs()
    panel = load_panel()
    grouped = list(panel.groupby("country"))
    rows = []
    for fd in FERT_DROPS:
        for sm in SMOOTHS:
            onset = {c: fertility_onset(g, fd, sm) for c, g in grouped}
            onset = {c: v for c, v in onset.items() if not np.isnan(v)}
            tf = pd.Series(list(onset.values()))
            rows.append({
                "fert_drop": fd, "smooth": sm, "n_onset": int(len(tf)),
                "iqr": float(tf.quantile(.75) - tf.quantile(.25)),
                "range": int(tf.max() - tf.min()),
                "median": float(tf.median()),
                "frac_within_10y_1950": float(((tf - 1950).abs() <= 10).mean()),
                "variance_reduction_ratio": collapse_ratio(panel, onset),
            })
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(RESULTS_DIR, "sensitivity.csv"), index=False)
    summary = {
        "n_settings": int(len(df)),
        "iqr_min": float(df["iqr"].min()), "iqr_max": float(df["iqr"].max()),
        "range_min": int(df["range"].min()), "range_max": int(df["range"].max()),
        "frac_within_10y_1950_min": float(df["frac_within_10y_1950"].min()),
        "frac_within_10y_1950_max": float(df["frac_within_10y_1950"].max()),
        "vrr_min": float(df["variance_reduction_ratio"].min()),
        "vrr_max": float(df["variance_reduction_ratio"].max()),
        "vrr_median": float(df["variance_reduction_ratio"].median()),
    }
    with open(os.path.join(RESULTS_DIR, "sensitivity_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(df.to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
