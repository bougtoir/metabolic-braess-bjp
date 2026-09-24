"""Stage 1b — exploratory characterization of the unexpected reverse signal.

ALL results in this script are exploratory / hypothesis-generating. The
original confirmatory hypothesis (Delta-beta > 0) was falsified and frozen in
results/stage1_original_hypothesis_report.md. Nothing here is confirmatory
evidence for the reverse biological hypothesis.

Analyses:
A. Taxon-pool matched null   — herbivore guilds subsampled to predator gamma
B. Frequency-matched null    — herbivore genera matched to predator occupancy
C. Allosaurus dependence     — exclusion / downsampling / species split
D. Systems-tract stratification
E. Stratigraphic (interval) control
F. Taxonomic-resolution symmetry (species level)
G. Metric and spatial-scale robustness
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PROCESSED, TABLES, write_table
from beta_utils import (
    guild_pieces,
    load_clean_genus_occurrences,
    mean_beta,
    pairwise_simpson,
    pairwise_sorensen,
)

RNG_SEED = 20240922
B_POOL = 10_000
B_FREQ = 10_000
N_DOWNSAMPLE = 1_000
N_STRAT_BOOT = 499


def pairwise_jaccard(mat: np.ndarray) -> np.ndarray:
    n = mat.shape[0]
    out = np.zeros((n, n))
    for i in range(n):
        a = mat[i]
        for j in range(i + 1, n):
            b = mat[j]
            inter = np.minimum(a, b).sum()
            union = np.maximum(a, b).sum()
            out[i, j] = out[j, i] = 1.0 - inter / union if union else 0.0
    return out


METRICS = {
    "simpson": pairwise_simpson,
    "sorensen": pairwise_sorensen,
    "jaccard": pairwise_jaccard,
}


def fast_mean_beta(mat: np.ndarray, metric: str = "simpson") -> float:
    """Vectorised mean pairwise dissimilarity over the upper triangle."""
    rich = mat.sum(axis=1).astype(float)
    shared = (mat @ mat.T).astype(float)
    if metric == "simpson":
        denom = np.minimum(rich[:, None], rich[None, :])
        diss = 1.0 - np.divide(shared, denom, out=np.ones_like(shared), where=denom > 0)
    elif metric == "sorensen":
        denom = rich[:, None] + rich[None, :]
        diss = 1.0 - np.divide(2 * shared, denom, out=np.ones_like(shared), where=denom > 0)
    else:  # jaccard
        union = rich[:, None] + rich[None, :] - shared
        diss = 1.0 - np.divide(shared, union, out=np.ones_like(shared), where=union > 0)
    iu = np.triu_indices_from(diss, k=1)
    return float(diss[iu].mean())


def guild_incidence(occ: pd.DataFrame, guild: str, taxa: list[str] | None = None):
    sub = occ[occ["guild"] == guild]
    if taxa is not None:
        sub = sub[sub["taxon"].isin(taxa)]
    mat = pd.crosstab(sub["collection_no"], sub["taxon"]).clip(upper=1)
    return mat


def genus_collection_vectors(occ: pd.DataFrame, guild: str):
    """Per-genus boolean incidence vector over the guild's collection list."""
    sub = occ[occ["guild"] == guild]
    colls = np.sort(sub["collection_no"].unique())
    coll_idx = {c: i for i, c in enumerate(colls)}
    vecs = {}
    for taxon, g in sub.groupby("taxon"):
        v = np.zeros(len(colls))
        v[[coll_idx[c] for c in g["collection_no"].unique()]] = 1
        vecs[taxon] = v
    return vecs, colls


def summarize_null(obs: float, null: np.ndarray) -> dict:
    return {
        "observed": obs,
        "null_mean": float(null.mean()),
        "null_median": float(np.median(null)),
        "null_lo95": float(np.quantile(null, 0.025)),
        "null_hi95": float(np.quantile(null, 0.975)),
        "empirical_tail_p": float((np.abs(null) >= abs(obs)).mean()),
        "prop_null_le_obs": float((null <= obs).mean()),
    }


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = load_clean_genus_occurrences()
    out_dir = TABLES

    # ---- baseline observed delta-beta (Simpson) ----
    beta = {}
    for g in ("herbivore", "predator"):
        mat, _ = guild_pieces(occ[occ["guild"] == g], g)
        beta[g] = mean_beta(pairwise_simpson(mat.to_numpy()))
    delta_obs = beta["predator"] - beta["herbivore"]

    n_pred_genera = occ[occ["guild"] == "predator"]["taxon"].nunique()

    # ================= Analysis A: taxon-pool matched null =================
    h_vecs, h_colls = genus_collection_vectors(occ, "herbivore")
    h_taxa = np.array(sorted(h_vecs))
    pred_mat = guild_incidence(occ, "predator")
    beta_P = fast_mean_beta(pred_mat.to_numpy())

    nulls = np.empty(B_POOL)
    for b in range(B_POOL):
        pick = rng.choice(h_taxa, size=n_pred_genera, replace=False)
        m = np.stack([h_vecs[t] for t in pick], axis=1)
        keep = m.sum(axis=1) > 0
        if keep.sum() < 5:
            nulls[b] = np.nan
            continue
        nulls[b] = beta_P - fast_mean_beta(m[keep])
    nulls = nulls[~np.isnan(nulls)]
    resA = summarize_null(delta_obs, nulls)
    write_table(
        pd.DataFrame({"delta_beta_b": nulls}), "stage1b_A_taxon_pool_null.csv"
    )

    # ================= Analysis B: frequency-matched null =================
    occ_freq = (
        occ.groupby(["guild", "taxon"])["collection_no"]
        .nunique()
        .rename("n_coll")
        .reset_index()
    )
    pred_freq = occ_freq[occ_freq["guild"] == "predator"].set_index("taxon")["n_coll"]
    herb_freq = occ_freq[occ_freq["guild"] == "herbivore"].set_index("taxon")["n_coll"]

    nullsB = np.empty(B_FREQ)
    for b in range(B_FREQ):
        avail = dict(herb_freq)
        matched = []
        for f in pred_freq.sample(frac=1, random_state=rng.integers(1e9)):
            # caliper match: nearest occupancy frequency, randomised
            diffs = {t: abs(v - f) for t, v in avail.items()}
            if not diffs:
                break
            dmin = min(diffs.values())
            cands = [t for t, d in diffs.items() if d == dmin]
            pick = rng.choice(cands)
            matched.append(pick)
            avail.pop(pick)
        if len(matched) < 5:
            nullsB[b] = np.nan
            continue
        m = np.stack([h_vecs[t] for t in matched], axis=1)
        keep = m.sum(axis=1) > 0
        if keep.sum() < 5:
            nullsB[b] = np.nan
            continue
        nullsB[b] = beta_P - fast_mean_beta(m[keep])
    nullsB = nullsB[~np.isnan(nullsB)]
    resB = summarize_null(delta_obs, nullsB)
    write_table(
        pd.DataFrame({"delta_beta_b": nullsB}), "stage1b_B_freq_matched_null.csv"
    )

    # ================= Analysis C: Allosaurus dependence =================
    c_rows = []

    def delta_with_pred(pred_occ: pd.DataFrame) -> float:
        mat, _ = guild_pieces(pred_occ, "predator")
        return mean_beta(pairwise_simpson(mat.to_numpy())) - beta["herbivore"]

    pred_full = occ[occ["guild"] == "predator"]
    c_rows.append({"scenario": "C1_full", "delta_beta": delta_with_pred(pred_full)})

    c_rows.append(
        {
            "scenario": "C2_no_allosaurus",
            "delta_beta": delta_with_pred(pred_full[pred_full["taxon"] != "Allosaurus"]),
        }
    )

    other_counts = (
        pred_full[pred_full["taxon"] != "Allosaurus"]
        .groupby("taxon")
        .size()
    )
    allo = pred_full[pred_full["taxon"] == "Allosaurus"]
    non_allo = pred_full[pred_full["taxon"] != "Allosaurus"]
    for label, k in (
        ("median", int(other_counts.median())),
        ("p75", int(other_counts.quantile(0.75))),
        ("p90", int(other_counts.quantile(0.90))),
        ("half", int(len(allo) * 0.5)),
    ):
        vals = []
        for _ in range(N_DOWNSAMPLE):
            sub = allo.sample(n=min(k, len(allo)), replace=False, random_state=rng)
            vals.append(delta_with_pred(pd.concat([non_allo, sub])))
        vals = np.asarray(vals)
        c_rows.append(
            {
                "scenario": f"C3_downsample_{label}",
                "delta_beta": float(vals.mean()),
                "lo95": float(np.quantile(vals, 0.025)),
                "hi95": float(np.quantile(vals, 0.975)),
            }
        )

    # C4: species-level split of Allosaurus (accepted_name where rank=species)
    pred_species = pred_full.copy()
    mask = (pred_species["genus"] == "Allosaurus") & (
        pred_species["accepted_rank"] == "species"
    )
    pred_species.loc[mask, "taxon"] = pred_species.loc[mask, "accepted_name"]
    c_rows.append(
        {
            "scenario": "C4_allosaurus_species_split",
            "delta_beta": delta_with_pred(pred_species),
            "n_taxa_used": int(pred_species["taxon"].nunique()),
        }
    )

    # C5: Allosaurus-only occupancy summary
    allo_colls = allo["collection_no"].nunique()
    allo_pts = allo.groupby("collection_no")[["lng", "lat"]].median()
    c_rows.append(
        {
            "scenario": "C5_allosaurus_only",
            "n_collections": allo_colls,
            "lat_range": float(allo_pts["lat"].max() - allo_pts["lat"].min()),
            "lng_range": float(allo_pts["lng"].max() - allo_pts["lng"].min()),
            "share_of_predator_collections": float(
                allo_colls / pred_full["collection_no"].nunique()
            ),
        }
    )
    c_df = pd.DataFrame(c_rows)
    write_table(c_df, "stage1b_C_allosaurus.csv")

    # ======== Analysis D: systems-tract stratification ========
    d_rows = []
    for st, g0 in occ.dropna(subset=["Systems_tract"]).groupby("Systems_tract"):
        row = {"systems_tract": st}
        ok = True
        betas = {}
        for guild in ("herbivore", "predator"):
            mat, _ = guild_pieces(g0[g0["guild"] == guild], guild)
            row[f"n_{guild}_collections"] = int(mat.shape[0])
            row[f"n_{guild}_taxa"] = int(mat.shape[1])
            if mat.shape[0] < 5:
                ok = False
            else:
                betas[guild] = mean_beta(pairwise_simpson(mat.to_numpy()))
        if not ok:
            row["note"] = "insufficient collections"
            d_rows.append(row)
            continue
        row["beta_H"] = betas["herbivore"]
        row["beta_P"] = betas["predator"]
        row["delta_beta"] = betas["predator"] - betas["herbivore"]
        # bootstrap CI over collections
        ds = []
        hc = g0[g0["guild"] == "herbivore"]["collection_no"].unique()
        pc = g0[g0["guild"] == "predator"]["collection_no"].unique()
        for _ in range(N_STRAT_BOOT):
            vals = []
            for guild, cc in (("herbivore", hc), ("predator", pc)):
                pick = rng.choice(cc, size=len(cc), replace=True)
                sub = g0[(g0["guild"] == guild) & (g0["collection_no"].isin(pick))]
                m, _ = guild_pieces(sub, guild)
                if m.shape[0] < 5:
                    vals.append(np.nan)
                    continue
                vals.append(mean_beta(pairwise_simpson(m.to_numpy())))
            ds.append(vals[1] - vals[0])
        ds = np.asarray(ds, dtype=float)
        ds = ds[~np.isnan(ds)]
        row["lo95"] = np.quantile(ds, 0.025)
        row["hi95"] = np.quantile(ds, 0.975)
        d_rows.append(row)
    d_df = pd.DataFrame(d_rows)
    write_table(d_df, "stage1b_D_systems_tract.csv")

    # ======== Analysis E: stratigraphic (interval) control ========
    def coarse_interval(s: str) -> str:
        s = str(s)
        if "Oxfordian" in s:
            return "Oxfordian"
        if "Kimmeridgian" in s:
            return "Kimmeridgian"
        if "Tithonian" in s:
            return "Tithonian"
        return "Other/undated"

    e_rows = []
    occ_iv = occ.assign(interval=occ["early_interval"].map(coarse_interval))
    for iv, g0 in occ_iv.groupby("interval"):
        row = {"interval": iv}
        betas = {}
        ok = True
        for guild in ("herbivore", "predator"):
            mat, _ = guild_pieces(g0[g0["guild"] == guild], guild)
            row[f"n_{guild}_collections"] = int(mat.shape[0])
            if mat.shape[0] < 5:
                ok = False
            else:
                betas[guild] = mean_beta(pairwise_simpson(mat.to_numpy()))
        if ok:
            row["beta_H"] = betas["herbivore"]
            row["beta_P"] = betas["predator"]
            row["delta_beta"] = betas["predator"] - betas["herbivore"]
        else:
            row["note"] = "insufficient collections"
        e_rows.append(row)
    write_table(pd.DataFrame(e_rows), "stage1b_E_intervals.csv")

    # ======== Analysis F: taxonomic resolution ========
    raw_spec = pd.read_csv(PROCESSED / "occurrences_clean.csv")
    spec = raw_spec.copy()
    spec["taxon"] = np.where(
        spec["accepted_rank"] == "species",
        spec["accepted_name"],
        spec["genus"],
    )
    spec = spec.dropna(subset=["taxon"])
    f_rows = []
    for level, frame in (("genus_level", occ), ("species_level", spec)):
        vals = {}
        for guild in ("herbivore", "predator"):
            sub = frame[frame["guild"] == guild]
            mat = pd.crosstab(sub["collection_no"], sub["taxon"]).clip(upper=1)
            vals[guild] = fast_mean_beta(mat.to_numpy())
            f_rows.append(
                {
                    "level": level,
                    "guild": guild,
                    "n_collections": int(mat.shape[0]),
                    "n_taxa": int(mat.shape[1]),
                    "beta_simpson": vals[guild],
                }
            )
        f_rows.append(
            {"level": level, "guild": "DELTA", "beta_simpson": vals["predator"] - vals["herbivore"]}
        )
    write_table(pd.DataFrame(f_rows), "stage1b_F_resolution.csv")

    # ======== Analysis G: metric and spatial-scale robustness ========
    g_rows = []
    km_per_deg = 111.0
    for cell_km in (None, 50, 100, 150):
        frame = occ.copy()
        unit = "collection"
        if cell_km:
            deg = cell_km / km_per_deg
            coll_xy = frame.groupby("collection_no")[["lng", "lat"]].median()
            cell = (
                (coll_xy["lng"] // deg).astype(int).astype(str)
                + "_"
                + (coll_xy["lat"] // deg).astype(int).astype(str)
            )
            frame["collection_no"] = frame["collection_no"].map(cell)
            unit = f"grid_{cell_km}km"
        for metric_name, fn in METRICS.items():
            vals = {}
            for guild in ("herbivore", "predator"):
                mat = pd.crosstab(
                    frame[frame["guild"] == guild]["collection_no"],
                    frame[frame["guild"] == guild]["taxon"],
                ).clip(upper=1)
                vals[guild] = fast_mean_beta(mat.to_numpy(), metric_name)
            g_rows.append(
                {
                    "unit": unit,
                    "metric": metric_name,
                    "beta_H": vals["herbivore"],
                    "beta_P": vals["predator"],
                    "delta_beta": vals["predator"] - vals["herbivore"],
                }
            )
    write_table(pd.DataFrame(g_rows), "stage1b_G_metric_scale.csv")

    # summary row per analysis
    summary = pd.DataFrame(
        [
            {"analysis": "A_taxon_pool_null", **resA},
            {"analysis": "B_freq_matched_null", **resB},
        ]
    )
    write_table(summary, "stage1b_null_summary.csv")
    print(summary.to_string(index=False))
    print(c_df.to_string(index=False))
    print(d_df.to_string(index=False))
    print(pd.DataFrame(e_rows).to_string(index=False))
    print(pd.DataFrame(f_rows).to_string(index=False))
    print(pd.DataFrame(g_rows).to_string(index=False))


if __name__ == "__main__":
    main()
