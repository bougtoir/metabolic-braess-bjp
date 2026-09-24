"""07: Morrison empirical sequential decomposition (worked example).

Recomputes every step on the SAME primary specification (Jaccard, genus
level unless the step changes resolution, collection scale) so the
attenuation cascade is internally consistent:

step 1 naive Δβ -> 2 gamma-null position -> 3 frequency-null position ->
4 -Allosaurus -> 5 species resolution -> 6 duration/sampling-adjusted
Allosaurus exceptionalism -> 7 preservation-model contribution.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT.parent  # dinosaur_migration_foodweb
sys.path.insert(0, str(PROJ / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from beta_utils import bootstrap_rows  # noqa: E402
from sim_core import mean_beta_jaccard  # noqa: E402

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
RNG_SEED = 20260924
N_BOOT = 999
B_NULL = 10_000


def mat(occ: pd.DataFrame, taxon_col: str) -> np.ndarray:
    return (
        pd.crosstab(occ["collection_no"], occ[taxon_col]).clip(upper=1).to_numpy()
    )


def delta(occ: pd.DataFrame, taxon_col: str = "taxon") -> float:
    mh = mat(occ[occ["guild"] == "herbivore"], taxon_col)
    mp = mat(occ[occ["guild"] == "predator"], taxon_col)
    return mean_beta_jaccard(mp) - mean_beta_jaccard(mh)


def boot_delta(occ: pd.DataFrame, rng, taxon_col: str = "taxon",
               pred_taxa=None) -> np.ndarray:
    mh = mat(occ[occ["guild"] == "herbivore"], taxon_col)
    p = occ[occ["guild"] == "predator"]
    if pred_taxa is not None:
        p = p[p[taxon_col].isin(pred_taxa)]
    mp = mat(p, taxon_col)
    out = np.empty(N_BOOT)
    for i in range(N_BOOT):
        out[i] = mean_beta_jaccard(bootstrap_rows(mp, rng)) - mean_beta_jaccard(
            bootstrap_rows(mh, rng)
        )
    return out


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = pd.read_csv(PROJ / "data" / "processed" / "occurrences_clean.csv")
    occ = occ[occ["guild"].isin(["herbivore", "predator"])].copy()
    occ["taxon_species"] = np.where(
        occ["accepted_rank"] == "species", occ["accepted_name"], occ["taxon"]
    )

    rows = []

    def add(step, label, d, ci=None, note=""):
        rows.append(
            {
                "step": step,
                "label": label,
                "delta_beta": d,
                "lo95": ci[0] if ci is not None else np.nan,
                "hi95": ci[1] if ci is not None else np.nan,
                "note": note,
            }
        )

    # step 1: naive
    d1 = delta(occ)
    b1 = boot_delta(occ, rng)
    add(1, "naive genus-level guild contrast", d1,
        (np.quantile(b1, 0.025), np.quantile(b1, 0.975)))

    # step 2: gamma-matched null position
    h = occ[occ["guild"] == "herbivore"]
    p = occ[occ["guild"] == "predator"]
    n_pg = p["taxon"].nunique()
    h_colls = np.sort(h["collection_no"].unique())
    cidx = {c: i for i, c in enumerate(h_colls)}
    h_vecs = {}
    for t, g in h.groupby("taxon"):
        v = np.zeros(len(h_colls))
        v[[cidx[c] for c in g["collection_no"].unique()]] = 1
        h_vecs[t] = v
    h_taxa = np.array(sorted(h_vecs))
    beta_p = mean_beta_jaccard(mat(p, "taxon"))
    nulls = np.empty(B_NULL)
    for b in range(B_NULL):
        pick = rng.choice(h_taxa, size=min(n_pg, len(h_taxa)), replace=False)
        m = np.stack([h_vecs[t] for t in pick], axis=1)
        keep = m.sum(axis=1) > 0
        nulls[b] = np.nan if keep.sum() < 5 else beta_p - mean_beta_jaccard(m[keep])
    nulls = nulls[~np.isnan(nulls)]
    add(2, "observed vs gamma-matched null",
        d1, (np.quantile(nulls, 0.025), np.quantile(nulls, 0.975)),
        note="CI shown is the null 95% interval")

    # step 3: frequency-matched null
    occ_freq = (
        occ.groupby(["guild", "taxon"])["collection_no"].nunique().rename("n")
        .reset_index()
    )
    pf = occ_freq[occ_freq["guild"] == "predator"].set_index("taxon")["n"]
    hf = occ_freq[occ_freq["guild"] == "herbivore"].set_index("taxon")["n"]
    nB = np.empty(B_NULL)
    for b in range(B_NULL):
        avail = dict(hf)
        matched = []
        for f0 in pf.sample(frac=1, random_state=rng.integers(1e9)):
            diffs = {t: abs(v - f0) for t, v in avail.items()}
            if not diffs:
                break
            dmin = min(diffs.values())
            cands = [t for t, d0 in diffs.items() if d0 == dmin]
            pick_t = rng.choice(cands)
            matched.append(pick_t)
            avail.pop(pick_t)
        if len(matched) < 5:
            nB[b] = np.nan
            continue
        m = np.stack([h_vecs[t] for t in matched], axis=1)
        keep = m.sum(axis=1) > 0
        nB[b] = np.nan if keep.sum() < 5 else beta_p - mean_beta_jaccard(m[keep])
    nB = nB[~np.isnan(nB)]
    add(3, "observed vs frequency-matched null",
        d1, (np.quantile(nB, 0.025), np.quantile(nB, 0.975)),
        note="CI shown is the null 95% interval")

    # step 4: remove Allosaurus
    occ_noallo = occ[occ["taxon"] != "Allosaurus"]
    d4 = delta(occ_noallo)
    b4 = boot_delta(occ_noallo, rng)
    add(4, "exclude Allosaurus", d4,
        (np.quantile(b4, 0.025), np.quantile(b4, 0.975)))

    # step 5: species resolution
    d5 = delta(occ, "taxon_species")
    b5 = boot_delta(occ, rng, "taxon_species")
    add(5, "species-level resolution", d5,
        (np.quantile(b5, 0.025), np.quantile(b5, 0.975)))

    # steps 6-7: pull structural-adjustment results produced by the
    # allosaurus_spatial_ecology run (extent residual, logit pseudo-R2)
    taxa = pd.read_csv(
        PROJ / "allosaurus_spatial_ecology" / "results" / "tables"
        / "allo_duration_model_taxa.csv"
    )
    allo_z = taxa.loc[taxa["taxon"] == "Allosaurus", "extent_resid_z"].iloc[0]
    pres = pd.read_csv(
        PROJ / "allosaurus_spatial_ecology" / "results" / "tables"
        / "allo_presence_summary.csv"
    ).set_index("metric")["value"]
    add(6, "duration+sampling adjusted Allosaurus extent z",
        allo_z, note="extent residual z-score; |z|<2 = not exceptional")
    add(7, "sampling/preservation model pseudo-R2",
        float(pres["logit_pseudo_r2"]),
        note="share of presence structure explained by collection covariates")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "morrison_decomposition.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
