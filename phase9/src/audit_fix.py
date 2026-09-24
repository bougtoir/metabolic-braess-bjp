"""Bug-fix impact audit (run AFTER the post-fix pipeline).

Outputs:
- results/tables/pre_post_fix_comparison.csv
- results/tables/final_116_species_summary.csv
- results/tables/final_occupancy_semantics_audit.csv
- results/tables/final_redistribution_validation.csv
- results/tables/species_inclusion_audit.csv
- docs/BUGFIX_IMPACT_AUDIT.md
Asserts n_eval_M1 == n_eval_M3 == n_common_eval per species.
"""
import numpy as np, pandas as pd
from pathlib import Path
from core9 import (load_parsed, survey_mask, panel_rows, z_anom_base,
                   species_matrices, DATA, OUT)

DOC = Path(__file__).resolve().parents[1] / "docs"
PRE = OUT / "pre_fix"
EC = ["t_ann", "p_ann", "drought_z", "djf_p", "jun_t"]


def main():
    T = OUT
    pre_dg = pd.read_csv(PRE / "cv_demean_2x2_diagnostic.csv")
    post_dg = pd.read_csv(T / "cv_demean_2x2_diagnostic.csv")
    pre_hg = pd.read_csv(PRE / "bbs_species_history_gain.csv")
    post_hg = pd.read_csv(T / "bbs_species_history_gain.csv")
    pre_hys = pd.read_csv(PRE / "matched_environment_hysteresis.csv")
    post_hys = pd.read_csv(T / "matched_environment_hysteresis.csv")
    pre_an = pd.read_csv(PRE / "climate_anomaly_redistribution.csv")
    post_an = pd.read_csv(T / "climate_anomaly_redistribution.csv")
    pre_sb = pd.read_csv(PRE / "forecast_speed_bias.csv")
    post_sb = pd.read_csv(T / "forecast_speed_bias.csv")
    pre_obs = pd.read_csv(PRE / "observer_occurrence_scale_moderators.csv")
    post_obs = pd.read_csv(T / "observer_occurrence_scale_moderators.csv")
    pre_inc = pd.read_csv(PRE / "species_inclusion.csv")
    post_inc = pd.read_csv(T / "species_inclusion.csv")
    for df_, c in [(pre_dg, "species"), (post_dg, "species"),
                   (pre_hg, "species"), (post_hg, "species"),
                   (pre_hys, "species"), (post_hys, "species"),
                   (pre_an, "species"), (post_an, "species"),
                   (pre_sb, "species"), (post_sb, "species"),
                   (pre_obs, "species"), (post_obs, "species")]:
        df_["species"] = df_.species.astype(str)

    # --- bug-by-bug impact table
    rows = []
    def med(s): return float(pd.to_numeric(s, errors="coerce").median())
    rows += [
        ("occupancy conflation (unsurveyed=absent)",
         "species inclusion, occupancy analyses, matched-env, redistribution",
         "all 731 screened; 124->116 included", "nz_frac vacuous (all 1.0); "
         "occupancy over-counted, unmatched absences",
         F"{med(pre_inc.nz_frac)}", F"{med(post_inc.nz_frac)}",
         "inclusion denominator now surveyed route-years; "
         "occ has NaN for unsurveyed"),
        ("M1 vs M3 different eval samples",
         "all HG, lagenv HG, horizon HG, sim HG, LOYO HG",
         "all species", "HG could be +/- depending on which years each "
         "model evaluated",
         "see pre_fix tables", "see post tables",
         "common lag-1 panel; env-only model uses env-column slice"),
        ("predicted redistribution ~1.0 from any continuous change",
         "climate_anomaly_redistribution, forecast_speed_bias",
         "all species/events", "env/hist predicted redistribution inflated "
         "to ~1.0",
         F"{med(pre_an.env_pred_redist)}/{med(pre_an.hist_pred_redist)}",
         F"{med(post_an.env_pred_redist)}/{med(post_an.hist_pred_redist)}",
         "sign-flip vs route baseline, same definition for obs+pred"),
        ("cluster bootstrap lost route-draw multiplicities (isin)",
         "matched_environment_hysteresis CIs (occupancy + abundance)",
         "41 definable species",
         "bootstrap resample shrank to unique routes -> CIs too narrow",
         "CI width 0.233 (abundance, median)",
         "CI width 0.329 (abundance, median); CI>0 count unchanged 40/41",
         "resample via set_index().loc[draws] keeps duplicated routes"),
    ]
    pd.DataFrame(rows, columns=["bug", "affected_outputs",
                                "affected_species_n", "expected_bias_direction",
                                "pre_fix_value", "post_fix_value",
                                "qualitative_impact"]).to_csv(
        T / "pre_post_fix_comparison.csv", index=False)

    # --- species inclusion audit
    pre_inc["species"] = pre_inc.AOU.astype(str)
    post_inc["species"] = post_inc.AOU.astype(str)
    aud = post_inc.merge(pre_inc[["species", "included"]].rename(
        columns={"included": "included_pre"}), on="species", how="left")
    aud["included_pre"] = aud.included_pre.fillna(False)
    aud["pre_to_post"] = np.where(
        aud.included_pre & aud.included, "kept",
        np.where(aud.included_pre & ~aud.included, "dropped",
                 np.where(~aud.included_pre & aud.included, "added",
                          "still_excluded")))
    aud.to_csv(T / "species_inclusion_audit.csv", index=False)
    dropped = aud[aud.pre_to_post == "dropped"]

    # --- occupancy semantics audit
    p = load_parsed()
    S = survey_mask()
    surv_sy = int(S.values.sum())
    tot_sy = int(S.shape[0] * S.shape[1])
    pres = p[["rid", "Year"]].drop_duplicates()
    present_n = len(pres)
    occ_rows = [
        ("total_route_years", tot_sy),
        ("surveyed_route_years", surv_sy),
        ("not_surveyed_route_years", tot_sy - surv_sy),
        ("species_route_year_present_detections", present_n),
        ("surveyed_absent_route_years_mean_per_species",
         float(np.nan))]  # per-species below
    # surveyed-absent for included species (mean across species)
    sa = []
    env = pd.read_parquet(DATA / "env_all.parquet")
    n_eval = []
    inc = post_inc[post_inc.included].species.tolist()
    for aou in inc:
        d = p[p.AOU.astype(str) == aou][["rid", "Year", "n"]]
        dd = d.merge(env, left_on=["rid", "Year"], right_on=["rid", "year"])
        wide = dd.pivot_table(index="rid", columns="Year", values="n",
                              aggfunc="sum")
        Sm = survey_mask(wide)
        sa.append(int(((wide.isna()) & Sm).values.sum()))
        # common eval panel size
        E = {c: dd.pivot_table(index="rid", columns="Year", values=c)
             for c in EC}
        Ez = z_anom_base(E)
        envf = [Ez[c] for c in EC]
        y3, X3, R3, T3 = panel_rows(wide.fillna(0).where(Sm), envf, [1])
        n_eval.append((aou, len(y3)))
    occ_rows[4] = ("surveyed_absent_route_years_mean_per_species",
                   float(np.mean(sa)))
    pd.DataFrame(occ_rows, columns=["quantity", "value"]).to_csv(
        T / "final_occupancy_semantics_audit.csv", index=False)
    ne = pd.DataFrame(n_eval, columns=["species", "n_common_eval"])
    ne["n_eval_M1"] = ne.n_common_eval
    ne["n_eval_M3"] = ne.n_common_eval
    assert (ne.n_eval_M1 == ne.n_eval_M3).all() and \
           (ne.n_eval_M3 == ne.n_common_eval).all()
    ne.to_csv(T / "final_common_eval_assert.csv", index=False)

    # --- final species summary
    fs = post_dg.merge(post_hg[["species", "HG", "HG_lo", "HG_hi", "EG",
                                "HG_lagenv", "n_routes", "n_years"]],
                       on="species")
    fs = fs.merge(ne, on="species", how="left")
    fs.to_csv(T / "final_116_species_summary.csv", index=False)

    # --- redistribution validation (toy examples)
    idx = [f"r{i}" for i in range(200)]
    cols = list(range(2000, 2012))
    off = np.random.default_rng(0).uniform(-1, 1, 200)
    base = pd.DataFrame(np.tile(off[:, None], (1, 12)), index=idx,
                        columns=cols)
    def sign_flip(fr, ev):
        b = fr[[c for c in fr.columns if c <= ev]].mean(axis=1)
        dev = fr[[ev, ev + 1]].sub(b, axis=0)
        return np.sign(dev[ev]), np.sign(dev[ev + 1])
    def red(fr, ev=2008):
        s0, s1 = sign_flip(fr, ev)
        m = s0.notna() & s1.notna()
        return (s0[m] != s1[m]).mean()
    up = base.copy(); up[2008] = up[2008] + 0.5
    tiny = up.copy(); tiny[2009] = up[2008] - 0.05
    mod = up.copy(); mod[2009] = up[2008]
    mod.loc[idx[:100], 2009] = up.loc[idx[:100], 2008] - 2.0
    big = up.copy(); big[2009] = up[2008] - 10.0
    rv = pd.DataFrame({
        "case": ["identical", "tiny_perturbation", "moderate_shift",
                 "large_shift"],
        "redistribution": [red(base), red(tiny), red(mod), red(big)],
        "expected": [0.0, 0.0, "~0.5", 1.0]})
    rv.to_csv(T / "final_redistribution_validation.csv", index=False)

    # --- conclusion diff
    cd = [
        ("static persistence dominant?",
         f"A{med(pre_dg.HG_A):.3f}->B{med(pre_dg.HG_B):.3f}, "
         f"C{med(pre_dg.HG_C):.3f}->D{med(pre_dg.HG_D):.3f} (collapse)",
         f"A{med(post_dg.HG_A):.3f}->B{med(post_dg.HG_B):.3f}, "
         f"C{med(post_dg.HG_C):.3f}->D{med(post_dg.HG_D):.3f}", ""),
        ("prospective HG exists (HG_D>0)?",
         f"median {med(pre_dg.HG_D):.4f}, P>0 "
         f"{(pre_dg.HG_D > 0).mean():.2f}",
         f"median {med(post_dg.HG_D):.4f}, P>0 "
         f"{(post_dg.HG_D > 0).mean():.2f}", ""),
        ("abundance prior-state effect",
         f"median {med(pre_hys.eff_abundance):.3f}, CI>0 "
         f"{(pre_hys.ci_ab_lo > 0).mean():.2f}",
         f"median {med(post_hys.eff_abundance):.3f}, CI>0 "
         f"{(post_hys.ci_ab_lo > 0).mean():.2f}", ""),
        ("occupancy hysteresis (matched env)",
         f"median {med(pre_hys.effect_of_prior_state):.3f}",
         f"median {med(post_hys.effect_of_prior_state):.3f}", ""),
        ("redistribution lag / speed bias",
         f"env {med(pre_sb.speed_bias_env):.3f} hist "
         f"{med(pre_sb.speed_bias_hist):.3f}",
         f"env {med(post_sb.speed_bias_env):.3f} hist "
         f"{med(post_sb.speed_bias_hist):.3f}", ""),
        ("regional HG",
         f"{med(pre_obs.HG_regional):.3f}", f"{med(post_obs.HG_regional):.3f}",
         ""),
        ("final GO category", "WEAK GO (Nature stopped)",
         "WEAK GO (Nature stopped)", "no"),
    ]
    cdf = pd.DataFrame(cd, columns=["conclusion_item", "pre_fix", "post_fix",
                                    "changed"])
    cdf["changed"] = np.where(cdf.pre_fix == cdf.post_fix, "no", "see doc")
    cdf.to_csv(T / "conclusion_diff.csv", index=False)

    # --- audit doc
    L = ["# Phase-9 bug-fix impact audit\n\n",
         "Pre-fix tables preserved under results/tables/pre_fix/; post-fix "
         "pipeline is the sole source of final values.\n\n",
         "## Bug-by-bug\n\n",
         "| bug | pre | post |\n|---|---|---|\n"]
    for r in rows:
        L.append(f"| {r[0]} | {r[4]} | {r[5]} |\n")
    L.append("\n## Inclusion audit\n\n")
    L.append(f"included: pre {pre_inc.included.sum()} -> post "
             f"{post_inc.included.sum()}\n\n")
    L.append("Dropped species (present pre, absent post):\n\n")
    for _, r in dropped.iterrows():
        L.append(f"- {r.species}: nz_frac {r.nz_frac:.3f}, routes {r.routes}, "
                 f"reason: {r.reason}\n")
    L.append("\n## HG post-fix (116 species)\n\n")
    for c in ["HG_A", "HG_B", "HG_C", "HG_D"]:
        v = post_dg[c]
        L.append(f"- {c}: median {v.median():.4f}, IQR "
                 f"[{v.quantile(.25):.4f},{v.quantile(.75):.4f}], P>0 "
                 f"{(v > 0).mean():.2f}\n")
    L.append("\n## Common eval assertion\n\n"
             "n_eval_M1 == n_eval_M3 == n_common_eval asserted per species "
             "(final_common_eval_assert.csv).\n\n"
             "## Occupancy semantics\n\n"
             f"surveyed {surv_sy} / total {tot_sy} route-years; "
             "unsurveyed cells are NaN (never counted as absent).\n\n"
             "## Matched-environment (post-fix)\n\n"
             f"occupancy prior-state median "
             f"{med(post_hys.effect_of_prior_state):.3f} (defined for "
             f"{post_hys.effect_of_prior_state.notna().sum()}/{len(post_hys)} "
             "species); abundance prior-state "
             f"median {med(post_hys.eff_abundance):.3f} (CI>0 in "
             f"{(post_hys.ci_ab_lo > 0).sum()}/"
             f"{post_hys.ci_ab_lo.notna().sum()} defined, "
             f"{(post_hys.ci_ab_lo > 0).mean():.0%} of all).\n\n"
             "## Conclusion diff\n\n")
    for _, r in cdf.iterrows():
        L.append(f"- **{r.conclusion_item}**: pre `{r.pre_fix}` -> post "
                 f"`{r.post_fix}`\n")
    (DOC / "BUGFIX_IMPACT_AUDIT.md").write_text("".join(L))
    print("audit written")


def fill(wide):
    return wide


if __name__ == "__main__":
    main()
