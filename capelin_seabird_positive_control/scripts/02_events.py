"""Capelin events (prey-defined only), published-result reproduction, and the
event-study response analysis.

Event = first day of capelin spawning in the study area (DateSpawn, ordinal),
taken verbatim from the published dataset. One pulse per year ->
n_independent_events == n_years.

Published result targeted for reproduction (Davoren et al. 2024, J Anim Ecol):
  (a) inshore capelin arrival produces 5-619x (mean 146 +/- 59) increase in
      coastal fish biomass;
  (b) seabird abundance within years peaks near the first day of spawning
      (DiffSpawn ~ 0), i.e. response to the seasonal influx, modelled as a
      quadratic in days-relative-to-spawning.

Event-study windows (prespecified): pre -14..-1, event 0..+3, post +4..+14
days relative to DateSpawn. Response Y = log1p(birds per 100-m bin).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRE, EVT, POST = (-14, -1), (0, 3), (4, 14)
BIRD_COLS = ["birds_total", "alcids", "larus", "gannets", "shearwaters"]

d = pd.read_csv(os.path.join(ROOT, "data/processed/surveys.csv"),
                parse_dates=["date"])

# ---------- events ----------
rows = []
for y, g in d.groupby("year"):
    spawn = int(g["spawn_doy"].iloc[0])
    pre = g[g["tau"].between(*PRE)]
    evt = g[g["tau"].between(*EVT)]
    post = g[g["tau"].between(*POST)]
    rows.append({
        "event_id": f"spawn_{y}", "year": y, "event_date_ordinal": spawn,
        "event_location": "10 km2 foraging area, coastal Newfoundland (capelin spawning-site cluster)",
        "pre_event_prey_level": pre["fish_g_m2"].mean(),
        "event_prey_level": evt["fish_g_m2"].mean(),
        "event_intensity": (evt["fish_g_m2"].mean() / pre["fish_g_m2"].mean()
                            if pre["fish_g_m2"].mean() > 0 else np.nan),
        # publication-style pulse magnitude: peak post-onset survey biomass
        # over pre-arrival baseline
        "peak_pulse_fold": (g.loc[g["tau"] >= 0, "fish_g_m2"].max()
                            / g.loc[g["tau"] < 0, "fish_g_m2"].mean()
                            if g.loc[g["tau"] < 0, "fish_g_m2"].mean() > 0
                            else np.nan),
        "event_duration": np.nan,  # single-date onset events
        "n_surveys_pre": len(pre), "n_surveys_evt": len(evt),
        "n_surveys_post": len(post),
        "data_source": "Dryad doi:10.5061/dryad.jq2bvq8k8 (hydroacoustic survey)"})
ev = pd.DataFrame(rows)
ev.to_csv(os.path.join(ROOT, "outputs/tables/capelin_events.csv"), index=False)
print(ev[["year", "event_date_ordinal", "event_intensity",
          "n_surveys_pre", "n_surveys_evt", "n_surveys_post"]])

# ---------- (a) reproduce fish biomass pulse ----------
# published: 5-619x, mean 146 +/- 59 across years
folds = ev["event_intensity"].dropna()
print("\npre->event fish biomass fold per year:", folds.round(1).tolist())
print("mean +/- SE:", folds.mean(), "+/-", folds.std() / np.sqrt(len(folds)))

# ---------- (b) reproduce within-year peak near DiffSpawn ~ 0 ----------
# fit log(birds+1) ~ tau + tau^2 pooled, and per-year vertex
d["logbirds"] = np.log1p(d["birds_per_bin"])
X = sm.add_constant(pd.DataFrame({"tau": d["tau"], "tau2": d["tau"] ** 2}))
m = sm.OLS(d["logbirds"], X).fit()
vertex = -m.params["tau"] / (2 * m.params["tau2"])
print("\npooled quadratic: beta_tau=%.4f beta_tau2=%.6f vertex=%.2f days"
      % (m.params["tau"], m.params["tau2"], vertex))

# ---------- event-level seabird response ----------
resp_rows = []
for y, g in d.groupby("year"):
    rec = {"year": y}
    for col in BIRD_COLS + ["birds_per_bin"]:
        pre = g.loc[g["tau"].between(*PRE), col]
        evt = g.loc[g["tau"].between(*EVT), col]
        post = g.loc[g["tau"].between(*POST), col]
        rec[f"d_{col}"] = (np.log1p(post.mean()) - np.log1p(pre.mean())
                           if len(pre) and len(post) else np.nan)
        rec[f"d_evt_{col}"] = (np.log1p(evt.mean()) - np.log1p(pre.mean())
                               if len(pre) and len(evt) else np.nan)
    resp_rows.append(rec)
resp = pd.DataFrame(resp_rows)
resp.to_csv(os.path.join(ROOT, "outputs/tables/event_level_seabird_response.csv"),
            index=False)
print("\n", resp[["year", "d_birds_per_bin", "d_evt_birds_per_bin"]])

# pooled event-study model: log(birds+1) ~ event dummy + year FE, cluster by year.
# Primary contrast: event window (0..+3) vs pre (-14..-1). The published result
# (birds peak AT spawn onset) predicts the event-window coefficient > 0; the
# post window (+4..+14) may already show post-peak decline.
dd = d.copy()
dd["evt"] = dd["tau"].between(*EVT).astype(int)
dd["post"] = dd["tau"].between(*POST).astype(int)
dd["inwindow"] = dd["tau"].between(*PRE) | dd["tau"].between(*EVT) | dd["tau"].between(*POST)
w = dd[dd["inwindow"]]
Xw = pd.concat([w[["evt", "post"]], pd.get_dummies(w["year"], prefix="y",
                drop_first=True, dtype=float)], axis=1)
Xw = sm.add_constant(Xw)
mod = sm.OLS(w["logbirds"], Xw).fit(
    cov_type="cluster", cov_kwds={"groups": w["year"]})
print("\nevent-window model evt coef=%.3f p=%.3f | post coef=%.3f p=%.3f" %
      (mod.params["evt"], mod.pvalues["evt"], mod.params["post"], mod.pvalues["post"]))
pd.DataFrame({"term": mod.params.index, "coef": mod.params.values,
              "p": mod.pvalues.values}).to_csv(
    os.path.join(ROOT, "outputs/tables/event_study_model.csv"), index=False)

# ---------- figures ----------
fig, axes = plt.subplots(2, 5, figsize=(15, 5), sharex=True)
for ax, (y, g) in zip(axes.flat, d.groupby("year")):
    ax2 = ax.twinx()
    ax.plot(g["tau"], g["fish_g_m2"], "o-", color="tab:blue", ms=3)
    ax2.plot(g["tau"], g["birds_per_bin"], "s-", color="tab:red", ms=3)
    ax.axvline(0, color="k", lw=0.7, ls="--")
    ax.set_title(str(y), fontsize=9)
fig.suptitle("Fish biomass (blue) and birds/100m-bin (red) vs days from spawn onset")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/capelin_event_timeseries.png"),
            dpi=150)

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(resp["year"], resp["d_birds_per_bin"])
ax.axhline(0, color="grey", lw=0.6)
ax.set_ylabel("delta log1p(birds/bin), post minus pre")
ax.set_title("Per-year seabird response to capelin spawn onset")
fig.tight_layout()
fig.savefig(os.path.join(ROOT, "outputs/figures/event_level_seabird_response.png"),
            dpi=150)
print("done")
