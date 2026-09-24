"""Event-time (transition-onset) alignment vs calendar-time alignment.

Two quantitative claims of the commentary are computed here:

Result 2 (collapse): the between-country dispersion of the crude birth rate lambda around
the transition is far smaller when trajectories are aligned by each country's own onset year
(event time tau = year - t_fert) than when they are stacked by calendar year. We report the
variance-reduction ratio in a common window around the transition.

Result 3 (phase indexing): the two conserved-quantity "pathways" (Phase I: lambda*e0 = const;
Phase II: lambda*exp(e0/TAU_E0) = const) are separated at least as well when each observation
is labelled pre/post that country's own onset as when it is labelled pre/post the single
calendar year 1950. We report the two-isocline R^2 under each labelling, and the between-
country coefficient of variation (CV) of each conserved quantity.
"""
import json
import os

import numpy as np
import pandas as pd

from common import RESULTS_DIR, TAU_E0, ensure_dirs, load_panel

CALENDAR_SPLIT = 1950
E0_PLATEAU = 43.6   # below this e0 the paper places a high-fertility plateau (its constant3)


def _fit_two_isocline_r2(df, phase):
    """Fit lambda=C1/e0 on Phase-I rows and lambda=C2/exp(e0/tau) on Phase-II rows;
    a constant lambda on plateau rows. Return overall R^2 and the fitted constants."""
    phase = np.asarray(phase)
    y = df["lambda"].values
    e0 = df["e0"].values
    tss = float(np.sum((y - y.mean()) ** 2))
    pred = np.full(len(df), np.nan)

    m1 = phase == 1
    if m1.sum() > 2:
        x1 = 1.0 / e0[m1]
        c1 = float(np.dot(x1, y[m1]) / np.dot(x1, x1))
        pred[m1] = c1 * x1
    else:
        c1 = np.nan

    m2 = phase == 2
    if m2.sum() > 2:
        x2 = 1.0 / np.exp(e0[m2] / TAU_E0)
        c2 = float(np.dot(x2, y[m2]) / np.dot(x2, x2))
        pred[m2] = c2 * x2
    else:
        c2 = np.nan

    m3 = phase == 3
    if m3.sum() > 0:
        c3 = float(np.mean(y[m3]))
        pred[m3] = c3
    else:
        c3 = np.nan

    ok = ~np.isnan(pred)
    sse = float(np.sum((y[ok] - pred[ok]) ** 2))
    r2 = 1.0 - sse / tss
    return {"r2": r2, "c1": c1, "c2": c2, "c3": c3, "n_fit": int(ok.sum())}


def _label_calendar(df):
    """Phase from calendar year: plateau if e0<E0_PLATEAU; else Phase I before 1950, II after."""
    phase = np.where(df["e0"].values < E0_PLATEAU, 3,
                     np.where(df["year"].values < CALENDAR_SPLIT, 1, 2))
    return pd.Series(phase, index=df.index)


def _label_event(df, onset):
    """Phase from each country's own onset year: plateau if e0<E0_PLATEAU; else Phase I before
    onset, Phase II from onset onward."""
    t = df["country"].map(onset)
    phase = np.where(df["e0"].values < E0_PLATEAU, 3,
                     np.where(df["year"].values < t.values, 1, 2))
    return pd.Series(phase, index=df.index)


def collapse_ratio(panel, onset, window=25):
    """Between-country SD of lambda within a +/- window around the transition, computed in
    calendar time (stacked at CALENDAR_SPLIT) vs event time (stacked at each onset)."""
    # event time
    ev = panel.copy()
    ev["t"] = ev["country"].map(onset)
    ev = ev.dropna(subset=["t"])
    ev["tau"] = ev["year"] - ev["t"]
    ev_win = ev[(ev["tau"] >= -window) & (ev["tau"] <= window)]
    sd_event = ev_win.groupby("tau")["lambda"].std().mean()

    # calendar time
    cal = panel[(panel["year"] >= CALENDAR_SPLIT - window)
                & (panel["year"] <= CALENDAR_SPLIT + window)]
    sd_calendar = cal.groupby("year")["lambda"].std().mean()

    return {"sd_lambda_calendar": float(sd_calendar),
            "sd_lambda_event": float(sd_event),
            "variance_reduction_ratio": float((sd_calendar ** 2) / (sd_event ** 2)),
            "window": window}


def conserved_cv(panel, phase, e0_min_I=40.0, e0_min_II=60.0):
    """Coefficient of variation of each conserved quantity within its assigned phase, computed
    inside the same e0 windows the paper uses to fit the two constants (Phase I: e0>40;
    Phase II: e0>60), so the calendar vs event comparison is apples-to-apples."""
    d = panel.copy()
    d["phase"] = np.asarray(phase)
    s1 = d[(d.phase == 1) & (d.e0 > e0_min_I)]
    s2 = d[(d.phase == 2) & (d.e0 > e0_min_II)]
    q1 = s1["lambda"] * s1["e0"]
    q2 = s2["lambda"] * np.exp(s2["e0"] / TAU_E0)
    def cv(s):
        return float(s.std() / s.mean()) if len(s) > 2 and s.mean() != 0 else np.nan
    return {"cv_lambda_e0_phaseI": cv(q1), "cv_lambda_exp_phaseII": cv(q2),
            "n_phaseI": int(len(s1)), "n_phaseII": int(len(s2))}


def main():
    ensure_dirs()
    panel = load_panel()
    onset = (pd.read_csv(os.path.join(RESULTS_DIR, "country_onset.csv"))
             .set_index("country")["t_fert"].dropna().to_dict())

    # restrict to countries with an estimated onset so calendar and event labellings are
    # compared on exactly the same observations
    panel = panel[panel["country"].isin(onset)].reset_index(drop=True)

    ph_cal = _label_calendar(panel)
    ph_ev = _label_event(panel, onset)

    res_cal = _fit_two_isocline_r2(panel, ph_cal.values)
    res_ev = _fit_two_isocline_r2(panel, ph_ev.values)

    out = {
        "calendar_split_year": CALENDAR_SPLIT,
        "two_isocline_R2_calendar": res_cal["r2"],
        "two_isocline_R2_event": res_ev["r2"],
        "R2_gain_event_over_calendar": res_ev["r2"] - res_cal["r2"],
        "fit_calendar": res_cal,
        "fit_event": res_ev,
        "collapse": collapse_ratio(panel, onset),
        "conserved_cv_calendar": conserved_cv(panel, ph_cal),
        "conserved_cv_event": conserved_cv(panel, ph_ev),
    }
    with open(os.path.join(RESULTS_DIR, "event_alignment.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if k != "fit_calendar" and k != "fit_event"},
                     indent=2))


if __name__ == "__main__":
    main()
