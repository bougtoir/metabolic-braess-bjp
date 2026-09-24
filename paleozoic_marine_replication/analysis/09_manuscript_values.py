"""09: manuscript_values.csv + stop-rule report (spec s.22, 24).

Every manuscript number traces to a machine-generated table.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from _common import CLADES, OUT


def main() -> None:
    inv = pd.read_csv(OUT / "data_inventory.csv")
    pool = pd.read_csv(OUT / "pool_perturbation_replicates.csv",
                       low_memory=False)
    cs = pd.read_csv(OUT / "cross_clade_summary.csv")
    ta = pd.read_csv(OUT / "temporal_aggregation.csv")
    fac = pd.read_csv(OUT / "sampling_factorial_replicates.csv",
                      low_memory=False)

    v = {}
    v["n_occurrences_total"] = int(inv["n_occurrences"].sum())
    # unique collections across all clades (clade rows overlap)
    from _common import DATA_PROC
    harm = pd.read_csv(DATA_PROC / "harmonized_occurrences.csv",
                       low_memory=False, usecols=["collection_id"])
    v["n_collections_total"] = int(harm["collection_id"].nunique())
    v["n_clades"] = int(inv.shape[0])
    for sch in ("stage", "10myr"):
        v[f"n_eligible_datasets_pool_{sch}"] = int(
            pool[pool["temporal_aggregation"] == sch]
            [["clade", "time_bin"]].drop_duplicates().shape[0])
    for c in CLADES:
        sub = inv[inv["clade"] == c]
        v[f"n_occ_{c.lower()}"] = int(sub["n_occurrences"].iloc[0])
        v[f"n_genera_{c.lower()}"] = int(sub["n_genera"].iloc[0])

    p50 = pool[pool["pool_fraction"] == 0.5]
    v["bias_beta_pool50_mean"] = round(float(p50["bias_beta"].mean()), 4)
    v["bias_beta_pool50_prop_positive"] = round(
        float((p50["bias_beta"] > 0).mean()), 3)
    bd = p50["bias_decay"].dropna()
    v["bias_decay_pool50_mean"] = round(float(bd.mean()), 6)
    v["bias_decay_pool50_prop_positive"] = round(
        float((bd > 0).mean()), 3)

    # per-clade sign consistency at f=0.5
    cs50 = cs[cs["pool_fraction"] == 0.5].set_index("clade")
    v["n_clades_bias_beta_negative_50"] = int(
        (cs50["bias_beta_mean"] < 0).sum())
    v["n_clades_bias_decay_positive_50"] = int(
        (cs50["bias_decay_mean"] > 0).sum())

    tagg = ta[ta["metric"] == "beta_jaccard"]
    v["bias_time_stage_to_stage2_mean"] = round(float(
        tagg[tagg["coarse_scheme"] == "stage2"]["bias_time"].mean()), 4)
    v["bias_time_5_to_10myr_mean"] = round(float(
        tagg[tagg["coarse_scheme"] == "10myr"]["bias_time"].mean()), 4)

    piv = fac.groupby(["pool_fraction", "sampling_fraction"])[
        "beta_value"].mean().unstack()
    v["beta_full_grid_min"] = round(float(piv.min().min()), 4)
    v["beta_full_grid_max"] = round(float(piv.max().max()), 4)

    mv = pd.DataFrame([{"name": k, "value": vv} for k, vv in v.items()])
    mv.to_csv(OUT.parent / "manuscript_values.csv", index=False)
    print(mv.to_string(index=False))

    # stop-rule report
    rep = []
    rep.append("# Paleozoic marine replication - stop-rule report\n")
    rep.append("## A. Did the dinosaur effect replicate?\n")
    direction = ("Pool contraction systematically "
                 + ("LOWERED" if v["bias_beta_pool50_mean"] < 0
                    else "RAISED")
                 + " mean pairwise Jaccard beta "
                 f"(mean bias {v['bias_beta_pool50_mean']}) and "
                 + ("steepened" if v["bias_decay_pool50_mean"] > 0
                    else "flattened")
                 + " the distance-decay slope "
                 f"(mean bias {v['bias_decay_pool50_mean']}).\n")
    rep.append(direction)
    rep.append("## B/C. Components replicated vs not\n")
    rep.append(cs50.round(4).to_string(index=False) + "\n")
    rep.append("## D. Robustness across clades\n")
    rep.append(f"Bias_beta negative in "
               f"{v['n_clades_bias_beta_negative_50']}/"
               f"{len(cs50)} clades at pool_fraction=0.5.\n")
    rep.append("## E. Harmonisation for cross-system synthesis\n")
    rep.append("cross_system_export.csv contains only the shared "
               "schema columns; Paleozoic-only metadata are in "
               "paleozoic_extended.csv.\n")
    (OUT.parent / "stop_rule_report.md").write_text("\n".join(rep))


if __name__ == "__main__":
    main()
