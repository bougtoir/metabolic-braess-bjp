"""Estimate each country's demographic-transition onset year (the "event").

We use the canonical fertility-transition marker (Coale 1973; Casterline 2001): the onset is
the first year in which the (smoothed) crude birth rate has fallen and remained at least
FERT_DROP below the country's own pre-transition plateau, with the decline being sustained.
We also record the mortality-transition onset (first sustained rise of e0) for context.

Outputs results/country_onset.csv with one row per country. No values are hard-coded.
"""
import os

import numpy as np
import pandas as pd

from common import RESULTS_DIR, ensure_dirs, load_panel

FERT_DROP = 0.10          # 10% irreversible decline below the plateau defines fertility onset
SMOOTH = 5                # centred rolling-mean window (years)
SUSTAIN = 15              # decline must persist over this horizon (years)
MIN_PLATEAU_YEARS = 10    # require some observations to establish the plateau


def _smooth(series, window=SMOOTH):
    return series.rolling(window, center=True, min_periods=1).mean()


def fertility_onset(g):
    """Onset = first year of the *irreversible* fertility decline (Coale 1973): the year
    after which the smoothed crude birth rate stays permanently at least FERT_DROP below the
    country's pre-transition plateau (the maximum smoothed CBR over the series). This avoids
    labelling transient 19th-century dips (later reversed) as the transition."""
    g = g.sort_values("year")
    yrs = g["year"].values
    lam = _smooth(g["lambda"]).values
    if len(lam) < MIN_PLATEAU_YEARS:
        return np.nan
    plateau = float(np.max(lam))
    threshold = (1 - FERT_DROP) * plateau
    # last year the series is at/above the threshold; the transition is irreversible afterwards
    above = np.where(lam >= threshold)[0]
    if len(above) == 0 or above[-1] == len(lam) - 1:
        return np.nan  # never plateaued, or never dropped below threshold within the window
    onset_idx = above[-1] + 1
    return int(yrs[onset_idx])


def mortality_onset(g, e0_rise=5.0):
    """First year e0 has risen e0_rise years above its early plateau and keeps rising."""
    g = g.sort_values("year")
    yrs = g["year"].values
    e0 = _smooth(g["e0"]).values
    if len(e0) < MIN_PLATEAU_YEARS:
        return np.nan
    running_min = np.minimum.accumulate(e0)
    for i in range(len(e0)):
        if e0[i] >= running_min[i] + e0_rise:
            horizon = e0[i:i + SUSTAIN]
            if np.mean(horizon) >= running_min[i] + e0_rise:
                return int(yrs[i])
    return np.nan


def main():
    ensure_dirs()
    panel = load_panel()
    rows = []
    for country, g in panel.groupby("country"):
        t_fert = fertility_onset(g)
        t_mort = mortality_onset(g)
        rows.append({
            "country": country,
            "t_fert": t_fert,
            "t_mort": t_mort,
            "lambda_plateau": float(_smooth(g["lambda"]).iloc[:MIN_PLATEAU_YEARS].max()),
            "e0_start": float(g.sort_values("year")["e0"].iloc[0]),
            "e0_end": float(g.sort_values("year")["e0"].iloc[-1]),
            "n_years": int(len(g)),
        })
    out = pd.DataFrame(rows).sort_values("t_fert")
    out.to_csv(os.path.join(RESULTS_DIR, "country_onset.csv"), index=False)

    tf = out["t_fert"].dropna()
    summary = {
        "n_countries": int(len(out)),
        "n_with_fertility_onset": int(tf.notna().sum()),
        "t_fert_min": int(tf.min()),
        "t_fert_p05": float(tf.quantile(0.05)),
        "t_fert_q1": float(tf.quantile(0.25)),
        "t_fert_median": float(tf.median()),
        "t_fert_q3": float(tf.quantile(0.75)),
        "t_fert_p95": float(tf.quantile(0.95)),
        "t_fert_max": int(tf.max()),
        "t_fert_iqr": float(tf.quantile(0.75) - tf.quantile(0.25)),
        "t_fert_range": int(tf.max() - tf.min()),
    }
    import json
    with open(os.path.join(RESULTS_DIR, "onset_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))
    print("\nEarliest transitions:\n", out.head(8)[["country", "t_fert"]].to_string(index=False))
    print("\nLatest transitions:\n", out.dropna(subset=["t_fert"]).tail(8)[["country", "t_fert"]].to_string(index=False))


if __name__ == "__main__":
    main()
