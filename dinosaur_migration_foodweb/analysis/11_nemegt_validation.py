"""Locked Nemegt validation analysis (VALIDATION_HYPOTHESES.md v2).

Frozen order — do not reorder or extend after viewing results:
1. Full data      : Delta-beta_full  (Jaccard, genus, collection level) + boot CI
2. -Tarbosaurus   : Delta-beta_{-T}  + boot CI
3. Downsample     : Tarbosaurus occs -> median / p75 other-predator counts / 50%
4. Attribution    : A_D = Delta-beta_{-T} - Delta-beta_full + boot distribution
5. Bias control   : taxon-pool matched null (B=10,000)
6. Taphonomy      : Tarbosaurus vs non-Tarbosaurus across env/lithology/
                    collection type + trace-record comparison
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESSED, TABLES, write_table
from beta_utils import bootstrap_rows, fast_mean_beta, incidence_matrix

RNG_SEED = 20260920
N_BOOT = 999
N_DOWNSAMPLE = 999
B_POOL = 10_000
DOMINANT = "Tarbosaurus"
METRIC = "jaccard"


def load() -> pd.DataFrame:
    occ = pd.read_csv(PROCESSED / "nemegt_occurrences.csv")
    m = occ["body_fossil"].fillna(False).astype(bool)
    m &= ~occ["is_ootaxon"].fillna(False).astype(bool)
    occ = occ[m & occ["genus"].notna()].copy()
    return occ.rename(columns={"genus": "taxon"})


def mats(occ: pd.DataFrame, pred_taxa=None):
    out = {}
    for guild in ("herbivore", "predator"):
        sub = occ[occ["guild"] == guild]
        if pred_taxa is not None and guild == "predator":
            sub = sub[sub["taxon"].isin(pred_taxa)]
        out[guild] = incidence_matrix(sub).to_numpy()
    return out


def delta_beta(mat_h, mat_p, metric=METRIC) -> float:
    return fast_mean_beta(mat_p, metric) - fast_mean_beta(mat_h, metric)


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = load()

    m0 = mats(occ)
    mat_h, mat_p = m0["herbivore"], m0["predator"]
    delta_full = delta_beta(mat_h, mat_p)

    # --- locked bootstrap: same collection resamples for all quantities ---
    pred_taxa_full = sorted(occ.loc[occ["guild"] == "predator", "taxon"].unique())
    pred_taxa_noT = [t for t in pred_taxa_full if t != DOMINANT]
    mat_p_noT = mats(occ, pred_taxa_noT)["predator"]

    boot = np.empty((N_BOOT, 2))
    for i in range(N_BOOT):
        mb_h = bootstrap_rows(mat_h, rng)
        mb_f = bootstrap_rows(mat_p, rng)
        mb_n = bootstrap_rows(mat_p_noT, rng)
        boot[i, 0] = delta_beta(mb_h, mb_f)
        boot[i, 1] = delta_beta(mb_h, mb_n)
    a_d = boot[:, 1] - boot[:, 0]

    delta_noT = delta_beta(mat_h, mat_p_noT)
    res = {
        "delta_beta_full": delta_full,
        "delta_beta_full_lo95": np.quantile(boot[:, 0], 0.025),
        "delta_beta_full_hi95": np.quantile(boot[:, 0], 0.975),
        "delta_beta_noTarbosaurus": delta_noT,
        "delta_beta_noT_lo95": np.quantile(boot[:, 1], 0.025),
        "delta_beta_noT_hi95": np.quantile(boot[:, 1], 0.975),
        "A_D": delta_noT - delta_full,
        "A_D_lo95": np.quantile(a_d, 0.025),
        "A_D_hi95": np.quantile(a_d, 0.975),
        "n_herb_coll": mat_h.shape[0],
        "n_pred_coll": mat_p.shape[0],
        "n_pred_coll_noT": mat_p_noT.shape[0],
        "n_pred_genera": mat_p.shape[1],
        "n_herb_genera": mat_h.shape[1],
    }

    # --- secondary metrics (sensitivity, not decision) ---
    for metric in ("simpson", "sorensen"):
        res[f"delta_beta_full_{metric}"] = delta_beta(mat_h, mat_p, metric)
        res[f"delta_beta_noT_{metric}"] = delta_beta(mat_h, mat_p_noT, metric)

    # --- downsampling (stochastic replication) ---
    pred_occ = occ[occ["guild"] == "predator"]
    tarb = pred_occ[pred_occ["taxon"] == DOMINANT]
    other = pred_occ[pred_occ["taxon"] != DOMINANT]
    other_counts = other.groupby("taxon").size()
    ds_rows = []
    for label, k in (
        ("median_other_predator", int(other_counts.median())),
        ("p75_other_predator", int(other_counts.quantile(0.75))),
        ("half_original", int(len(tarb) * 0.5)),
    ):
        k = max(1, min(k, len(tarb)))
        vals = np.empty(N_DOWNSAMPLE)
        for r in range(N_DOWNSAMPLE):
            sub = tarb.sample(n=k, replace=False, random_state=rng)
            m = incidence_matrix(pd.concat([other, sub])).to_numpy()
            vals[r] = fast_mean_beta(m, METRIC) - fast_mean_beta(mat_h, METRIC)
        ds_rows.append(
            {
                "target": label,
                "k": k,
                "delta_beta_mean": vals.mean(),
                "lo95": np.quantile(vals, 0.025),
                "hi95": np.quantile(vals, 0.975),
            }
        )
    write_table(pd.DataFrame(ds_rows), "nemegt_downsampling.csv")

    # --- taxon-pool matched null (B=10,000): herbivore subsampled to
    #     predator gamma richness ---
    h_sub = occ[occ["guild"] == "herbivore"]
    h_taxa = np.array(sorted(h_sub["taxon"].unique()))
    h_vecs = {}
    h_colls = np.sort(h_sub["collection_no"].unique())
    cidx = {c: i for i, c in enumerate(h_colls)}
    for t, g in h_sub.groupby("taxon"):
        v = np.zeros(len(h_colls))
        v[[cidx[c] for c in g["collection_no"].unique()]] = 1
        h_vecs[t] = v
    n_pred_g = len(pred_taxa_full)
    beta_P = fast_mean_beta(mat_p, METRIC)
    nulls = np.empty(B_POOL)
    for b in range(B_POOL):
        pick = rng.choice(h_taxa, size=min(n_pred_g, len(h_taxa)), replace=False)
        m = np.stack([h_vecs[t] for t in pick], axis=1)
        keep = m.sum(axis=1) > 0
        nulls[b] = np.nan if keep.sum() < 5 else beta_P - fast_mean_beta(m[keep], METRIC)
    nulls = nulls[~np.isnan(nulls)]
    write_table(pd.DataFrame({"delta_beta_b": nulls}), "nemegt_pool_null.csv")
    res.update(
        {
            "null_mean": nulls.mean(),
            "null_lo95": np.quantile(nulls, 0.025),
            "null_hi95": np.quantile(nulls, 0.975),
            "prop_null_le_obs": float((nulls <= delta_full).mean()),
        }
    )

    # --- taphonomic diagnostics ---
    allocc = pd.read_csv(PROCESSED / "nemegt_occurrences.csv")
    tarb_mask = (allocc["genus"] == DOMINANT) | (allocc["tna"].str.contains(
        DOMINANT, na=False
    ))
    diag = []
    for field in ("env", "lt1", "gsc", "cct"):
        ct = pd.crosstab(
            tarb_mask.map({True: DOMINANT, False: "other"}),
            allocc[field].fillna("unknown"),
        )
        if ct.shape[1] > 1:
            chi2, p, *_ = chi2_contingency(ct)
        else:
            chi2, p = np.nan, np.nan
        diag.append(
            {
                "field": field,
                "chi2": chi2,
                "p": p,
                "tarbosaurus_top": ct.loc[DOMINANT].idxmax(),
                "tarb_share_top_cat": float(
                    ct.loc[DOMINANT].max() / ct.loc[DOMINANT].sum()
                ),
                "other_top": ct.loc["other"].idxmax(),
                "other_share_top_cat": float(
                    ct.loc["other"].max() / ct.loc["other"].sum()
                ),
            }
        )
        write_table(ct, f"nemegt_taph_{field}.csv")
    write_table(pd.DataFrame(diag), "nemegt_taphonomy.csv")

    occ_per_coll = (
        allocc.assign(tarb=tarb_mask)
        .groupby(["collection_no", "tarb"])
        .size()
        .rename("n")
        .reset_index()
    )
    occ_per_coll.to_csv(TABLES / "nemegt_occ_per_collection.csv", index=False)
    traces = allocc[~allocc["body_fossil"].fillna(False).astype(bool)]
    write_table(
        traces.groupby(["tna"]).size().rename("n_trace_records").reset_index(),
        "nemegt_trace_records.csv",
    )

    write_table(pd.DataFrame([res]), "nemegt_delta_beta.csv")
    for k, v in res.items():
        print(f"{k:32s} {v}")
    print(pd.DataFrame(ds_rows).to_string(index=False))
    print(pd.DataFrame(diag).to_string(index=False))


if __name__ == "__main__":
    main()
