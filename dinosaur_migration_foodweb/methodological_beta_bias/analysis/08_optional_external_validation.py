"""08: external comparator — apply the SAME bias-diagnostic workflow to the
Nemegt PBDB pull. Comparator, not a confirmatory replication.

Steps: naive Δβ -> gamma-null -> −Tarbosaurus -> species resolution ->
duration/sampling adjustment (extent residual of Tarbosaurus).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
sys.path.insert(0, str(PROJ / "analysis"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from beta_utils import bootstrap_rows, haversine_km  # noqa: E402
from sim_core import mean_beta_jaccard  # noqa: E402
import statsmodels.api as sm  # noqa: E402

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
RNG_SEED = 20260925
N_BOOT = 999
B_NULL = 10_000
DOMINANT = "Tarbosaurus"


def mat(occ: pd.DataFrame, col: str) -> np.ndarray:
    return pd.crosstab(occ["collection_no"], occ[col]).clip(upper=1).to_numpy()


def delta(occ: pd.DataFrame, col: str = "taxon") -> float:
    mh = mat(occ[occ["guild"] == "herbivore"], col)
    mp = mat(occ[occ["guild"] == "predator"], col)
    return mean_beta_jaccard(mp) - mean_beta_jaccard(mh)


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = pd.read_csv(PROJ / "data" / "processed" / "nemegt_occurrences.csv")
    m = occ["body_fossil"].fillna(False).astype(bool)
    m &= ~occ["is_ootaxon"].fillna(False).astype(bool)
    occ = occ[m & occ["genus"].notna()].copy()
    occ["taxon"] = occ["genus"]
    # species-level where accepted name carries a species
    occ["taxon_species"] = np.where(
        occ["tna"].str.contains(" ", na=False), occ["tna"], occ["taxon"]
    )

    rows = []

    def add(step, label, d, note=""):
        rows.append({"step": step, "label": label, "delta_beta": d, "note": note})

    add(1, "naive genus-level guild contrast", delta(occ))

    h = occ[occ["guild"] == "herbivore"]
    p = occ[occ["guild"] == "predator"]
    n_pg = p["taxon"].nunique()
    n_hg = h["taxon"].nunique()
    if n_hg >= n_pg:
        nulls = np.empty(B_NULL)
        h_colls = np.sort(h["collection_no"].unique())
        cidx = {c: i for i, c in enumerate(h_colls)}
        h_vecs = {}
        for t, g in h.groupby("taxon"):
            v = np.zeros(len(h_colls))
            v[[cidx[c] for c in g["collection_no"].unique()]] = 1
            h_vecs[t] = v
        h_taxa = np.array(sorted(h_vecs))
        beta_p = mean_beta_jaccard(mat(p, "taxon"))
        for b in range(B_NULL):
            pick = rng.choice(h_taxa, size=n_pg, replace=False)
            mm = np.stack([h_vecs[t] for t in pick], axis=1)
            keep = mm.sum(axis=1) > 0
            nulls[b] = np.nan if keep.sum() < 5 else beta_p - mean_beta_jaccard(mm[keep])
        nulls = nulls[~np.isnan(nulls)]
        add(2, "gamma-matched null 95% interval",
            float(nulls.mean()),
            note=f"[{np.quantile(nulls,0.025):.3f}, {np.quantile(nulls,0.975):.3f}]")
    else:
        add(2, "gamma-matched null", np.nan,
            note="degenerate: herbivore gamma < predator gamma")

    add(3, f"exclude {DOMINANT}", delta(occ[occ["taxon"] != DOMINANT]))
    add(4, "species-level resolution", delta(occ, "taxon_species"))

    # duration/sampling adjustment: extent residual of Tarbosaurus
    taxa_stats = (
        occ.groupby("taxon")
        .agg(guild=("guild", "first"), n_occ=("collection_no", "size"))
        .reset_index()
    )
    def extent(t):
        g = occ[occ["taxon"] == t]
        pts = g.groupby("collection_no")[["lng", "lat"]].median().to_numpy()
        if len(pts) < 2:
            return 0.0
        return float(haversine_km(pts[:, 0][:, None], pts[:, 1][:, None],
                                  pts[:, 0][None, :], pts[:, 1][None, :]).max())
    taxa_stats["extent_km"] = taxa_stats["taxon"].map(extent)
    taxa_stats["pred"] = (taxa_stats["guild"] == "predator").astype(int)
    X = sm.add_constant(taxa_stats[["n_occ", "pred"]].astype(float))
    fit = sm.OLS(taxa_stats["extent_km"], X).fit()
    resid = taxa_stats["extent_km"] - fit.predict(X)
    tarb_z = resid[taxa_stats["taxon"] == DOMINANT].iloc[0] / resid.std()
    add(5, f"{DOMINANT} extent residual z (sampling-adjusted)",
        float(tarb_z), note="|z|<2 = not exceptional")
    taxa_stats.to_csv(OUT / "nemegt_taxa_extent.csv", index=False)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "nemegt_comparator_decomposition.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
