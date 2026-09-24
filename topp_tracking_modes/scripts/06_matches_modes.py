# Event-animal matches, prey-field classification, matched-unit sensitivity,
# species_tracking_mode.csv, mode_predictor_results.csv.
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(ROOT, "outputs", "tables")
META = os.path.join(ROOT, "metadata")
os.makedirs(OUT, exist_ok=True)

ad = pd.read_parquet(os.path.join(PROC, "animal_day_model.parquet"))
ev = pd.read_csv(os.path.join(OUT, "independent_events.csv"),
                 parse_dates=["start_date", "end_date", "peak_date"])
for c in ["start_date", "end_date", "peak_date"]:
    ev[c] = pd.to_datetime(ev[c], utc=True).dt.tz_localize(None)
ev["in_window_end"] = ev["start_date"] + pd.Timedelta(days=21)

# ---- event_animal_matches: animals inside station-adjacent box in window ----
ad["date_naive"] = pd.to_datetime(ad["date"], utc=True).dt.tz_localize(None)
rows = []
for e in ev.itertuples():
    m = ad[(ad["date_naive"] >= e.start_date)
           & (ad["date_naive"] <= e.in_window_end)
           & (ad["lat"].between(e.station_lat - 2, e.station_lat + 2))]
    n_an = m["animal"].nunique()
    n_sp = m["species"].nunique()
    n_prey = m["chl"].notna().sum()
    n_env = m["uwi"].notna().sum()
    rows.append({"event_id": e.event_id, "station_lat": e.station_lat,
                 "start_date": e.start_date, "in_season": e.in_season,
                 "n_animals": n_an, "n_species": n_sp,
                 "animal_days": len(m),
                 "days_with_prey": n_prey, "days_with_env": n_env,
                 "with_predator": n_an > 0, "with_prey": n_prey > 0,
                 "with_both": (n_an > 0) & (n_prey > 0)})
em = pd.DataFrame(rows)
em.to_csv(os.path.join(OUT, "event_animal_matches.csv"), index=False)
print(em[["with_predator", "with_prey", "with_both"]].sum())

# ---- prey field classification ----
pf = pd.DataFrame([
    {"field": "SeaWiFS chl-a (8d, 4km)", "class": "INDIRECT",
     "role": "primary production / forage-fish proxy",
     "rationale": "No direct prey (krill/fish school) co-located measurements "
                  "in TOPP; chl-a is the standard productivity proxy used in "
                  "the TOPP literature (Block et al. 2011)."},
    {"field": "Bakun UWI (coastal stations)", "class": "ENVIRONMENTAL",
     "role": "upwelling forcing (not prey)",
     "rationale": "Wind-driven forcing index; enters E terms only."},
    {"field": "OISST daily SST", "class": "ENVIRONMENTAL",
     "role": "thermal habitat / niche control",
     "rationale": "Habitat-selection covariate per spec §17."},
    {"field": "AVISO geostrophic u/v", "class": "ENVIRONMENTAL",
     "role": "advection correction",
     "rationale": "Used to compute residual (active) displacement, §10."},
])
pf.to_csv(os.path.join(META, "topp_prey_field_classification.csv"),
          index=False)

# ---- matched-unit sensitivity: recompute n over threshold grid ----
sens = []
evb = ad[ad["event_id"].notna()].copy()
evb["t_in_ev"] = (evb["date_naive"]
                  - evb["event_id"].map(ev.set_index("event_id")
                                      ["start_date"])).dt.days
evb["dist_km"] = (evb["lat"] - evb["station"]).abs() * 111.0
for dh in [6, 12, 24, 48]:
    for dk in [5, 10, 20, 50]:
        m = evb[(evb["t_in_ev"] <= dh / 24.0) & (evb["dist_km"] <= dk)]
        sens.append({"max_hours_since_onset": dh, "max_km_from_station_lat": dk,
                     "matched_days": int(len(m)),
                     "events_hit": int(m["event_id"].nunique())})
pd.DataFrame(sens).to_csv(os.path.join(OUT, "matched_unit_sensitivity.csv"),
                          index=False)

# ---- species tracking mode ----
mc = pd.read_csv(os.path.join(OUT, "model_comparison.csv"))
ho = pd.read_csv(os.path.join(OUT, "event_holdout_results.csv"))
fp = pd.read_csv(os.path.join(OUT, "future_prey_prediction.csv"))
pk = pd.read_csv(os.path.join(OUT, "lag_peaks.csv"))

def mode_row(sp):
    g = mc[mc["species"] == sp]
    gg = g.set_index("model")
    h = ho[ho["species"] == sp]
    hm = h.groupby("model")["corr"].mean()
    f = fp[fp["species"] == sp]
    pred_corr = float(f["corr"].iloc[0]) if len(f) else np.nan
    # in-sample anchors
    r2 = gg["r2"]
    best_in = r2.idxmax() if len(r2) else None
    # CV anchors
    best_cv = hm.idxmax() if len(hm.dropna()) else None
    # CueAdvantage: env-driven future-prey predictive performance vs
    # current-prey model performance (in-sample r2 proxy)
    cue_adv = np.nan
    if len(f) and "M_K" in gg.index:
        cue_adv = pred_corr - np.sqrt(max(gg.loc["M_K", "r2"], 0))
    # classification logic (not p-value only): use CV + in-sample + lags
    ev_cv = {k: hm.get(k, np.nan) for k in hm.index}
    if len(hm.dropna()) == 0:
        best, second, strength = "INCONCLUSIVE", "INCONCLUSIVE", "none"
        lim = "no usable event-held-out folds"
        metric = "n/a"
    else:
        e_cv = ev_cv.get("M_E", np.nan); ek = ev_cv.get("M_EK", np.nan)
        k_cv = ev_cv.get("M_K", np.nan); mp = ev_cv.get("M_PREDICTIVE", np.nan)
        metric = f"eventCV corr E={e_cv:.2f} EK={ek:.2f} K={k_cv:.2f} PRED={mp:.2f}"
        if all(np.nanmean(list(ev_cv.values())) < 0 for _ in [0]):
            best, second = "MIXED-WEAK", "INCONCLUSIVE"
            strength = "weak (negative transfer across events)"
            lim = "models do not generalize to held-out events"
        elif mp == np.nanmax(list(ev_cv.values())) and pred_corr > 0:
            best, second = "ENVIRONMENTAL-CUE DOMINATED", "MIXED-WEAK"
            strength = "moderate"; lim = "chl-a is indirect prey proxy"
        elif e_cv >= ek and e_cv >= k_cv:
            best, second = "ENVIRONMENTAL-CUE DOMINATED", "MIXED-WEAK"
            strength = "weak"; lim = "chl-a is indirect prey proxy"
        elif k_cv > e_cv and ek > e_cv:
            best, second = "PREY-MEDIATED DOMINATED", "ENVIRONMENTAL-CUE DOMINATED"
            strength = "weak"; lim = "chl-a is indirect prey proxy"
        else:
            best, second = "MIXED-WEAK", "ENVIRONMENTAL-CUE DOMINATED"
            strength = "weak"; lim = "limited event coverage"
    return {"species": sp, "best_supported_mode": best,
            "second_best_mode": second, "evidence_strength": strength,
            "main_supporting_metric": metric,
            "predictability_futureprey_from_env": pred_corr,
            "cue_advantage": cue_adv,
            "main_limitation": lim}

sm = pd.DataFrame([mode_row(s) for s in sorted(mc["species"].unique())])
sm.to_csv(os.path.join(OUT, "species_tracking_mode.csv"), index=False)

# ---- mode predictors: mobility/trophic/predictability vs mode signal ----
mob = pd.read_csv(os.path.join(META, "topp_species_mobility.csv"))
mr = sm.merge(mob, on="species", how="left")
pr = []
for _, r in mr.iterrows():
    pr.append({"species": r["species"],
               "predictability": r["predictability_futureprey_from_env"],
               "cue_advantage": r["cue_advantage"],
               "median_daily_disp_km": r.get("median_daily_disp_km", np.nan)})
prd = pd.DataFrame(pr)
res = {"n": len(prd.dropna(subset=["predictability"]))}
if res["n"] >= 3:
    res["corr_pred_vs_mobility"] = float(prd["predictability"].corr(
        prd["median_daily_disp_km"], method="spearman"))
    res["corr_cueadv_vs_mobility"] = float(prd["cue_advantage"].corr(
        prd["median_daily_disp_km"], method="spearman"))
pd.DataFrame([res]).to_csv(os.path.join(OUT, "mode_predictor_results.csv"),
                           index=False)
print(sm.to_string())
print(res)
