"""Competing models, mediation, Type A vs B comparison, event-holdout CV.

Unit: matched trophic unit (zoop tow + predator sightings within 24h/10km).
Outcome: log1p predator density (bird_km2 primary; krillbird_km2, whale_km alt).
Exposures: uwi (7-day upwelling index), sst_anom. Prey: log1p krill_m3.
Controls: year, month dummies, depth_max, lat. SE: cluster by cruise.

Outputs:
  outputs/tables/model_estimates.csv
  outputs/tables/mediation_results.csv
  outputs/tables/typeA_typeB_model_comparison.csv
  outputs/tables/event_holdout_results.csv
"""
import os

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "outputs/tables")

u = pd.read_parquet(os.path.join(ROOT, "data/processed/units_with_env.parquet"))
d = u.dropna(subset=["krill_m3", "bird_km2", "uwi", "sst_anom"]).copy()
d["P"] = np.log1p(d["bird_km2"])
d["K"] = np.log1p(d["krill_m3"])
d["Z"] = np.log1p(d["zoop_m3"])
d["E"] = d["uwi"]
d["month"] = d["time"].dt.month
d["year"] = d["time"].dt.year
d["cruise"] = d["cruise"].astype(str)

def fit(form, data=d):
    m = smf.ols(form, data=data).fit(cov_type="cluster",
                                   cov_kwds={"groups": data["cruise"]})
    return m

rows = []
specs = {
    "M0_env_only": "P ~ E + sst_anom + C(month) + C(year)",
    "M1_prey_only": "P ~ K + C(month) + C(year)",
    "M2_env_plus_prey": "P ~ E + sst_anom + K + C(month) + C(year)",
    "M2b_two_prey": "P ~ E + sst_anom + K + Z + C(month) + C(year)",
}
for name, f in specs.items():
    m = fit(f)
    rows.append({"model": name, "n": int(m.nobs), "r2": m.rsquared,
                 "aic": m.aic, "bic": m.bic,
                 "E_coef": m.params.get("E", np.nan),
                 "E_p": m.pvalues.get("E", np.nan),
                 "K_coef": m.params.get("K", np.nan),
                 "K_p": m.pvalues.get("K", np.nan)})

# env->prey link
mk = fit("K ~ E + sst_anom + C(month) + C(year)")
rows.append({"model": "env_to_prey", "n": int(mk.nobs), "r2": mk.rsquared,
             "aic": mk.aic, "bic": mk.bic, "E_coef": mk.params.get("E"),
             "E_p": mk.pvalues.get("E"), "K_coef": np.nan, "K_p": np.nan})
est = pd.DataFrame(rows)
est.to_csv(os.path.join(OUT, "model_estimates.csv"), index=False)

# ------- mediation: indirect E->K->P, bootstrap by cruise cluster ------
m0 = fit(specs["M0_env_only"]); m2 = fit(specs["M2_env_plus_prey"])
a = mk.params["E"]            # E->K
b = m2.params["K"]            # K->P | E
direct = m2.params["E"]       # E->P | K
total = m0.params["E"]        # E->P
indirect = a * b
cruises = d["cruise"].unique()
rng = np.random.default_rng(0)
boot = []
for _ in range(500):
    cs = rng.choice(cruises, len(cruises), replace=True)
    db = pd.concat([d[d["cruise"] == c] for c in cs], ignore_index=True)
    try:
        ba = smf.ols("K ~ E + sst_anom + C(month) + C(year)", data=db).fit().params["E"]
        bm2 = smf.ols(specs["M2_env_plus_prey"], data=db).fit()
        bm0 = smf.ols(specs["M0_env_only"], data=db).fit()
        boot.append({"a": ba, "b": bm2.params["K"], "ind": ba * bm2.params["K"],
                     "direct": bm2.params["E"], "total": bm0.params["E"]})
    except Exception:
        pass
boot = pd.DataFrame(boot)
ci = boot.quantile([0.025, 0.5, 0.975])
med = pd.DataFrame([
    {"path": "E->K", "coef": a, "ci_lo": ci.loc[0.025, "a"], "ci_hi": ci.loc[0.975, "a"]},
    {"path": "K->P|E", "coef": b, "ci_lo": ci.loc[0.025, "b"], "ci_hi": ci.loc[0.975, "b"]},
    {"path": "indirect E->K->P", "coef": indirect, "ci_lo": ci.loc[0.025, "ind"], "ci_hi": ci.loc[0.975, "ind"]},
    {"path": "direct E->P|K", "coef": direct, "ci_lo": ci.loc[0.025, "direct"], "ci_hi": ci.loc[0.975, "direct"]},
    {"path": "total E->P", "coef": total, "ci_lo": ci.loc[0.025, "total"], "ci_hi": ci.loc[0.975, "total"]},
    {"path": "attenuation (total-direct)/total", "coef": (total - direct) / total if total else np.nan,
     "ci_lo": np.nan, "ci_hi": np.nan},
])
med.to_csv(os.path.join(OUT, "mediation_results.csv"), index=False)

# ------- Type A vs Type B: in-sample + event-holdout CV by cruise -------
cmp_rows = []
pred_fun = {
    "A_env": specs["M0_env_only"],
    "B_env_prey": specs["M2_env_plus_prey"],
}
# CV variants without year FE: unseen year levels in held-out folds are
# unpredictable and would silently drop folds
pred_fun_cv = {
    "A_env": "P ~ E + sst_anom + C(month)",
    "B_env_prey": "P ~ E + sst_anom + K + C(month)",
}
for name, f in pred_fun.items():
    m = fit(f)
    cmp_rows.append({"model": name, "n": int(m.nobs), "r2": m.rsquared,
                     "aic": m.aic, "bic": m.bic})

# event-holdout: hold out each in-season environmental event; also each cruise
def holdout(split_on):
    res = []
    failed = []
    groups = d.dropna(subset=[split_on])[split_on].unique()
    for g in groups:
        te = d[d[split_on] == g]
        tr = d[d[split_on] != g]
        if len(te) < 5 or len(tr) < 50:
            continue
        for name, f in pred_fun_cv.items():
            try:
                m = smf.ols(f, data=tr).fit()
                pr = m.predict(te)
                y = te["P"]
                res.append({"split": split_on, "held_out": g, "model": name,
                            "rmse": float(np.sqrt(np.mean((y - pr) ** 2))),
                            "mae": float(np.mean(np.abs(y - pr))),
                            "corr": float(np.corrcoef(y, pr)[0, 1]),
                            "n": len(te)})
            except Exception as ex:
                failed.append({"split": split_on, "held_out": g,
                               "model": name, "error": str(ex)})
    pd.DataFrame(failed).to_csv(
        os.path.join(OUT, f"holdout_failed_folds_{split_on}.csv"), index=False)
    print(f"holdout {split_on}: {len(failed)} failed folds logged")
    return pd.DataFrame(res)

ho_ev = holdout("event_id")
ho_cr = holdout("cruise")
ho = pd.concat([ho_ev, ho_cr])
ho.to_csv(os.path.join(OUT, "event_holdout_results.csv"), index=False)

agg = ho.groupby(["split", "model"]).agg(
    rmse=("rmse", "mean"), mae=("mae", "mean"), corr=("corr", "mean"),
    folds=("held_out", "nunique")).reset_index()
for _, r in agg.iterrows():
    cmp_rows.append({"model": r["model"], "n": np.nan,
                     "r2": np.nan, "aic": np.nan, "bic": np.nan,
                     "holdout": f"{r['split']}", "cv_rmse": r["rmse"],
                     "cv_corr": r["corr"], "cv_folds": r["folds"]})
cmpd = pd.DataFrame(cmp_rows)
cmpd.to_csv(os.path.join(OUT, "typeA_typeB_model_comparison.csv"), index=False)
print(est.to_string(index=False))
print(med.to_string(index=False))
print(agg.to_string(index=False))
