"""Build results/manuscript_values.csv — every numeric value cited in the
manuscript, traced to its source script and output file."""
from __future__ import annotations

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"

ROWS = []


def add(vid, val, lo=None, hi=None, seed="", script="", out="", fig="",
        loc="", unit=None):
    if unit is None:
        unit = ("Δβ (mean-pairwise Jaccard)" if vid.startswith(("sim", "emp_db", "nem"))
                and "r2" not in vid.lower() and "falsecontrast" not in vid
                else "z-score" if "_z" in vid
                else "pseudo-R2" if "r2" in vid.lower()
                else "proportion" if "falsecontrast" in vid or "difference" in vid
                else "")
    ROWS.append(dict(value_id=vid, value=val, CI_lower=lo, CI_upper=hi,
                     unit=unit, simulation_seed_set=seed,
                     source_script=script, source_output=out, figure_panel=fig,
                     manuscript_location=loc))


def main() -> None:
    s1 = pd.read_csv(T / "sim01_gamma_bias.csv")
    r = s1[s1.n_pred_taxa == 2].iloc[0]
    add("sim01_bias_p2", r.bias_mean, r.lo95, r.hi95, "20260922",
        "01_gamma_diversity_bias.py", "sim01_gamma_bias.csv",
        "Fig.2a", "Results 1")
    r = s1[s1.n_pred_taxa == 4].iloc[0]
    add("sim01_bias_p4", r.bias_mean, r.lo95, r.hi95, "20260922",
        "01_gamma_diversity_bias.py", "sim01_gamma_bias.csv",
        "Fig.2a", "Results 1")
    add("sim01_falsecontrast_p4", r["prop_abs_gt_0.1"], seed="20260922",
        script="01_gamma_diversity_bias.py", out="sim01_gamma_bias.csv",
        fig="Fig.2a", loc="Results 1")
    r = s1[s1.n_pred_taxa == 26].iloc[0]
    add("sim01_bias_p26", r.bias_mean, r.lo95, r.hi95, "20260922",
        "01_gamma_diversity_bias.py", "sim01_gamma_bias.csv",
        "Fig.2a", "Results 1")

    s2 = pd.read_csv(T / "sim02_dominance_bias.csv")
    for p, vid in ((0.5, "sim02_bias_pD0.5_allolike"), (0.9, "sim02_bias_pD0.9")):
        r = s2[s2.p_dominant == p].iloc[0]
        add(vid, r.delta_beta_obs_mean, r.lo95, r.hi95, "20260922",
            "02_dominance_bias.py", "sim02_dominance_bias.csv",
            "Fig.2b", "Results 2")

    s3 = pd.read_csv(T / "sim03_taxonomic_lumping.csv")
    r = s3.iloc[-1]
    add("sim03_B_lumping_k6", r.B_lumping_mean, seed="20260922",
        script="03_taxonomic_lumping.py", out="sim03_taxonomic_lumping.csv",
        fig="Fig.3a", loc="Results 2")
    add("sim03_shift_genus_minus_species_k6", r.shift_genus_minus_species,
        seed="20260922", script="03_taxonomic_lumping.py",
        out="sim03_taxonomic_lumping.csv", fig="Fig.3a", loc="Results 2")

    s4 = pd.read_csv(T / "sim04_temporal_averaging.csv")
    for w, vid in ((1, "sim04_db_width1"), (8, "sim04_db_width8")):
        r = s4[s4.bin_width_slices == w].iloc[0]
        add(vid, r.delta_beta_obs_mean, r.lo95, r.hi95, "20260922",
            "04_temporal_averaging.py", "sim04_temporal_averaging.csv",
            "Fig.3b", "Results 2")

    s5 = pd.read_csv(T / "sim05_sampling_bias.csv")
    add("sim05_bias_range_min", s5.delta_beta_obs_mean.min(),
        s5.lo95.min(), s5.hi95.min(), "20260922", "05_sampling_bias.py",
        "sim05_sampling_bias.csv", "", "Results 2")
    add("sim05_bias_range_max", s5.delta_beta_obs_mean.max(),
        seed="20260922", script="05_sampling_bias.py",
        out="sim05_sampling_bias.csv", fig="", loc="Results 2")

    s6 = pd.read_csv(T / "sim06_factorial.csv")
    r = s6.loc[s6.bias.abs().idxmax()]
    add("sim06_max_abs_bias", r.bias, seed="20260923",
        script="06_combined_factorial_simulation.py",
        out="sim06_factorial.csv", fig="Fig.4",
        loc=f"Results 3 (cell n_pred={int(r.n_pred_taxa)}, p_D={r.p_dominant}, k={int(r.n_lumped)})")
    add("sim06_false_difference_max", s6.prop_false_difference.max(),
        seed="20260923", script="06_combined_factorial_simulation.py",
        out="sim06_factorial.csv", fig="Fig.4", loc="Results 3")

    dec = pd.read_csv(T / "morrison_decomposition.csv")
    lbl = dict(zip(dec.step, dec.label))
    d = dict(zip(dec.step, dec.delta_beta))
    lo = dict(zip(dec.step, dec.lo95)); hi = dict(zip(dec.step, dec.hi95))
    add("emp_db_naive", d[1], lo[1], hi[1], "20260920",
        "05_beta_diversity.py", "morrison_decomposition.csv",
        "Fig.5", "Results 4")
    add("emp_gamma_null_interval", None, lo[2], hi[2], "20260920",
        "07_exploratory_reverse_signal.py", "morrison_decomposition.csv",
        "Fig.5", "Results 5")
    add("emp_freq_null_interval", None, lo[3], hi[3], "20260920",
        "07_exploratory_reverse_signal.py", "morrison_decomposition.csv",
        "Fig.5", "Results 5")
    add("emp_db_minus_allosaurus", d[4], lo[4], hi[4], "20260920",
        "07_morrison_empirical_decomposition.py",
        "morrison_decomposition.csv", "Fig.5", "Results 5")
    add("emp_db_species", d[5], lo[5], hi[5], "20260920",
        "07_morrison_empirical_decomposition.py",
        "morrison_decomposition.csv", "Fig.5", "Results 5")
    add("emp_allo_extent_z", d[6], seed="", script="01_allosaurus_mechanisms.py",
        out="morrison_decomposition.csv", fig="", loc="Results 5")
    add("emp_presence_pseudoR2", d[7], seed="",
        script="01_allosaurus_mechanisms.py", out="morrison_decomposition.csv",
        fig="", loc="Results 5 (exploratory)")

    rob = pd.read_csv(T / "presence_model_robustness.csv")
    r = rob[rob.penalty_C == 1.0].iloc[0]
    add("emp_presence_pseudoR2_penalized", r.pseudo_r2_penalized,
        seed="", script="12_presence_model_robustness.py",
        out="presence_model_robustness.csv", fig="",
        loc="Results 5 (exploratory robustness)")

    s13g = pd.read_csv(T / "sim13_2d_gamma.csv")
    for np_, vid in ((4, "sim13_2d_bias_p4"), (2, "sim13_2d_bias_p2")):
        r = s13g[s13g.n_pred_taxa == np_].iloc[0]
        add(vid, r.delta_beta_mean, r.lo95, r.hi95, "20260924",
            "13_2d_robustness.py", "sim13_2d_gamma.csv", "Fig.6",
            "GEB Results 1 (2-D robustness)")
    r = s13g[s13g.n_pred_taxa == 4].iloc[0]
    add("sim13_2d_decayslope_diff_p4", r.decay_slope_diff, seed="20260924",
        script="13_2d_robustness.py", out="sim13_2d_gamma.csv",
        fig="Fig.6", loc="GEB Results 1")
    s13t = pd.read_csv(T / "sim13_2d_temporal.csv")
    add("sim13_2d_temporal_attenuation",
        s13t.iloc[-1].delta_beta_mean - s13t.iloc[0].delta_beta_mean,
        seed="20260924", script="13_2d_robustness.py",
        out="sim13_2d_temporal.csv", fig="Fig.3b", loc="GEB Results 2")

    nem = pd.read_csv(T / "nemegt_comparator_decomposition.csv")
    add("nem_db_full", nem.iloc[0].delta_beta, -0.079, 0.300, "20260920",
        "11_nemegt_validation.py", "nemegt_comparator_decomposition.csv",
        "Fig.5 / Suppl", "Results 6")

    out = pd.DataFrame(ROWS)
    out.to_csv(T.parent / "manuscript_values.csv", index=False)
    print(out[["value_id", "value"]].to_string(index=False))


if __name__ == "__main__":
    main()
