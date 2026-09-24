"""Robustness: leave-one-event-out, temporal placebo, negative control,
lag-response curve.

Primary response: deltaY_event = log1p(mean birds/bin in event window
0..+3d) - log1p(mean in pre window -14..-1d) relative to capelin spawn onset.
Pooled estimate = year-FE OLS coefficient on the event-window dummy with
year-clustered SEs.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRE, EVT = (-14, -1), (0, 3)

d = pd.read_csv(os.path.join(ROOT, "data/processed/surveys.csv"),
                parse_dates=["date"])
d["logbirds"] = np.log1p(d["birds_per_bin"])


def pooled_evt_effect(df, shift=0):
    """Year-FE OLS coefficient on event-window dummy; shift moves the
    event date in days (positive = event later)."""
    w = df.copy()
    w["tau_s"] = w["tau"] - shift
    w["evt"] = w["tau_s"].between(*EVT).astype(int)
    w = w[w["tau_s"].between(*PRE) | w["tau_s"].between(*EVT)]
    X = pd.concat([w["evt"], pd.get_dummies(w["year"], prefix="y",
                   drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X)
    m = sm.OLS(w["logbirds"], X).fit(cov_type="cluster",
                                   cov_kwds={"groups": w["year"]})
    return m.params["evt"], m.pvalues["evt"], len(w)


def per_event_delta(df, shift=0, exclude_year=None):
    """Per-year event response; returns dict year -> delta."""
    out = {}
    for y, g in df.groupby("year"):
        if exclude_year is not None and y == exclude_year:
            continue
        t = g["tau"] - shift
        pre = g.loc[t.between(*PRE), "birds_per_bin"]
        evt = g.loc[t.between(*EVT), "birds_per_bin"]
        out[y] = (np.log1p(evt.mean()) - np.log1p(pre.mean())
                  if len(pre) and len(evt) else np.nan)
    return out


full_coef, full_p, n_w = pooled_evt_effect(d)
deltas = per_event_delta(d)
print("full evt effect: %.3f (p=%.3f, n=%d)" % (full_coef, full_p, n_w))
print("per-year deltas:", {k: round(v, 2) for k, v in deltas.items()})

# ---------- leave-one-event-out ----------
loeo = []
for y in sorted(d["year"].unique()):
    sub = d[d["year"] != y]
    try:
        c, p, n = pooled_evt_effect(sub)
    except Exception:
        c, p, n = np.nan, np.nan, 0
    loeo.append({"dropped_event": y, "evt_coef": c, "p": p, "n": n})
lo = pd.DataFrame(loeo)
lo["sign_reversed"] = np.sign(lo["evt_coef"]) != np.sign(full_coef)
lo.to_csv(os.path.join(ROOT, "outputs/tables/leave_one_event_out_capelin.csv"),
          index=False)
print(lo)
print("sign reversals:", lo["sign_reversed"].sum())

# ---------- temporal placebo ----------
# placebo spawn dates: all doy within the year's surveyed seasonal window,
# excluding +/-7 days around the true spawn date
rng = np.random.default_rng(0)
plac = []
for y, g in d.groupby("year"):
    spawn = int(g["spawn_doy"].iloc[0])
    cand = [p for p in range(int(g["doy"].min()) + 14, int(g["doy"].max()) - 3)
            if abs(p - spawn) > 7]
    # cap candidates and sample deterministic subset
    for p in cand[::2]:
        gp = g.assign(tau=g["doy"] - p)
        pre = gp.loc[gp["tau"].between(*PRE), "birds_per_bin"]
        evt = gp.loc[gp["tau"].between(*EVT), "birds_per_bin"]
        plac.append({"year": y, "placebo_doy": p, "true_spawn": spawn,
                     "delta": (np.log1p(evt.mean()) - np.log1p(pre.mean())
                               if len(pre) and len(evt) else np.nan)})
pl = pd.DataFrame(plac).dropna(subset=["delta"])
pl.to_csv(os.path.join(ROOT, "outputs/tables/placebo_results_capelin.csv"),
          index=False)
obs_med = np.nanmedian(list(deltas.values()))
frac = (pl["delta"] >= obs_med).mean()
pval = 2 * min(frac, 1 - frac)
print("observed median delta %.3f | placebo median %.3f | frac>=obs %.2f | emp p=%.2f"
      % (obs_med, pl["delta"].median(), frac, pval))

# ---------- negative control: +/-30 day shifts ----------
neg = []
for shift in (-30, 30):
    dd = per_event_delta(d, shift=shift)
    neg.append({"shift_days": shift, "median_delta": np.nanmedian(list(dd.values())),
                "n_events": int(np.sum(np.isfinite(list(dd.values()))))})
pd.DataFrame(neg).to_csv(os.path.join(ROOT, "outputs/tables/negative_control_capelin.csv"),
                         index=False)
print(neg)

# ---------- lag response: shift event date by 0/1/3/7 days ----------
lags = [0, 1, 3, 7]
lagres = []
for l in lags:
    dd = per_event_delta(d, shift=-l)  # response lags event by l days
    lagres.append({"lag_days": l,
                   "median_delta": np.nanmedian(list(dd.values())),
                   "n_events": int(np.sum(np.isfinite(list(dd.values()))))})
lagdf = pd.DataFrame(lagres)
lagdf.to_csv(os.path.join(ROOT, "outputs/tables/lag_response_capelin.csv"),
             index=False)
print(lagdf)

# ---------- figures ----------
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(range(len(lo)), lo["evt_coef"])
ax.axhline(full_coef, color="r", ls="--")
ax.set_xticks(range(len(lo)))
ax.set_xticklabels(lo["dropped_event"], rotation=90, fontsize=7)
ax.set_ylabel("evt coef"); ax.set_title("Leave-one-event-out")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/leave_one_event_out_capelin.png"),
            dpi=150)

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(pl["delta"], bins=25)
ax.axvline(obs_med, color="r", lw=2)
ax.set_xlabel("placebo delta log1p(birds/bin)")
ax.set_title(f"Placebo distribution (frac>=obs {frac:.2f})")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/placebo_distribution_capelin.png"),
            dpi=150)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(lagdf["lag_days"], lagdf["median_delta"], "o-")
ax.axhline(0, color="grey", lw=0.6)
ax.set_xlabel("lag (days)"); ax.set_ylabel("median event delta")
ax.set_title("Lag-response (note: weekly survey resolution)")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/lag_response_capelin_seabird.png"),
            dpi=150)
print("done")
