"""Exploratory Allosaurus mechanisms — analyses 1-8 of the new project.

ALL exploratory; nothing here is confirmatory. Implements the locked
hierarchy: taxonomic pooling (L), temporal duration, preservation/sampling,
predator comparison, matched-taxon controls, generalism (niche overlap).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.spatial import ConvexHull
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SIB = ROOT.parent
sys.path.insert(0, str(SIB / "analysis"))
from beta_utils import bootstrap_rows, fast_mean_beta, haversine_km  # noqa: E402

RAW_XLSX = SIB / "data" / "raw" / "maidment2024_dryad" / "Occurrence_data_with_STs_dinos.xlsx"
TABLES = ROOT / "results" / "tables"
FIGS = ROOT / "figures"
for d in (TABLES, FIGS):
    d.mkdir(parents=True, exist_ok=True)

RNG_SEED = 20260921
N_BOOT = 999
N_MATCH = 500


def write(df: pd.DataFrame, name: str) -> None:
    df.to_csv(TABLES / name, index=False)
    print(f"wrote {TABLES/name}")


def occ_collections(occ: pd.DataFrame, taxon_col: str = "taxon"):
    return pd.crosstab(occ["collection_no"], occ[taxon_col]).clip(upper=1)


def extent_metrics(pts: pd.DataFrame) -> dict:
    """pts: lng/lat per collection occupied."""
    xy = pts[["lng", "lat"]].to_numpy()
    if len(xy) < 2:
        return {"max_dist_km": 0.0, "hull_area_deg2": 0.0, "lat_range": float(xy[:, 1].max() - xy[:, 1].min()) if len(xy) else 0.0}
    dist = haversine_km(xy[:, 0][:, None], xy[:, 1][:, None], xy[:, 0][None, :], xy[:, 1][None, :])
    hull = ConvexHull(xy).volume if len(xy) >= 3 else 0.0
    return {
        "max_dist_km": float(dist.max()),
        "hull_area_deg2": float(hull),
        "lat_range": float(xy[:, 1].max() - xy[:, 1].min()),
    }


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    occ = pd.read_csv(SIB / "data" / "processed" / "occurrences_clean.csv")
    occ = occ[occ["guild"].isin(["herbivore", "predator"])].copy()
    dino_colls = occ["collection_no"].unique()
    n_all_colls = len(dino_colls)

    raw = pd.read_excel(RAW_XLSX)
    raw_dino = raw[raw["collection_no"].isin(dino_colls)]
    coll_env = (
        raw_dino.groupby("collection_no")
        .agg(
            environment=("environment", "first"),
            lithology1=("lithology1", "first"),
            member=("member", "first"),
            state=("state", "first"),
            systems_tract=("Systems_tract", "first"),
            lat=("lat", "median"),
            lng=("lng", "median"),
        )
    )
    coll_rich = raw_dino.assign(
        g=raw_dino["genus"].fillna(raw_dino["accepted_name"])
    ).groupby("collection_no")["g"].nunique().rename("n_dino_taxa")
    coll_env = coll_env.join(coll_rich)

    # ---------- 1. Taxonomic pooling: L = Δβ_genus − Δβ_species ----------
    occ["taxon_species"] = np.where(
        occ["accepted_rank"] == "species", occ["accepted_name"], occ["taxon"]
    )
    betas = {}
    for level, col in (("genus", "taxon"), ("species", "taxon_species")):
        mats = {}
        for guild in ("herbivore", "predator"):
            mats[guild] = occ_collections(occ[occ["guild"] == guild], col).to_numpy()
        betas[level] = {
            "h": fast_mean_beta(mats["herbivore"], "jaccard"),
            "p": fast_mean_beta(mats["predator"], "jaccard"),
            "delta": fast_mean_beta(mats["predator"], "jaccard")
            - fast_mean_beta(mats["herbivore"], "jaccard"),
            "mats": mats,
        }
    L = betas["genus"]["delta"] - betas["species"]["delta"]

    Ls = np.empty(N_BOOT)
    dg, dsp = [], []
    for b in range(N_BOOT):
        for level, out in (("genus", dg), ("species", dsp)):
            mm = betas[level]["mats"]
            out.append(
                fast_mean_beta(bootstrap_rows(mm["predator"], rng), "jaccard")
                - fast_mean_beta(bootstrap_rows(mm["herbivore"], rng), "jaccard")
            )
        Ls[b] = dg[-1] - dsp[-1]
    write(
        pd.DataFrame(
            {
                "quantity": ["delta_beta_genus", "delta_beta_species", "L_attenuation"],
                "estimate": [betas["genus"]["delta"], betas["species"]["delta"], L],
                "lo95": [
                    np.quantile(dg, 0.025),
                    np.quantile(dsp, 0.025),
                    np.quantile(Ls, 0.025),
                ],
                "hi95": [
                    np.quantile(dg, 0.975),
                    np.quantile(dsp, 0.975),
                    np.quantile(Ls, 0.975),
                ],
            }
        ),
        "allo_L_attenuation.csv",
    )

    # ---------- 2. Occupancy + maps ----------
    occ_rows = []
    targets = ["Allosaurus", "Allosaurus fragilis", "Allosaurus jimmadseni",
               "Ceratosaurus", "Torvosaurus"]
    for t in targets:
        sub = occ[(occ["taxon_species"] == t) | (occ["taxon"] == t)]
        pts = sub.groupby("collection_no")[["lng", "lat"]].median()
        m = extent_metrics(pts)
        occ_rows.append(
            {
                "taxon": t,
                "n_occurrences": len(sub),
                "n_collections": pts.shape[0],
                "occupancy_share": pts.shape[0] / n_all_colls,
                **m,
            }
        )
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.scatter(coll_env["lng"], coll_env["lat"], c="0.8", s=10, label="dinosaur coll.")
        ax.scatter(pts["lng"], pts["lat"], c="crimson", s=15, label=t)
        ax.set_title(f"{t} occupancy ({pts.shape[0]} collections)")
        ax.set_xlabel("lng"); ax.set_ylabel("lat"); ax.legend(markerscale=1.5, fontsize=7)
        fig.tight_layout()
        fig.savefig(FIGS / f"map_{t.replace(' ', '_')}.png", dpi=150)
        plt.close(fig)
    write(pd.DataFrame(occ_rows), "allo_occupancy.csv")

    # ---------- 3. Stratigraphic duration model ----------
    taxa_stats = (
        occ.groupby("taxon")
        .agg(
            guild=("guild", "first"),
            n_occ=("collection_no", "size"),
            n_coll=("collection_no", "nunique"),
            max_ma=("max_ma", "max"),
            min_ma=("min_ma", "min"),
        )
        .assign(duration=lambda d: d["max_ma"] - d["min_ma"])
        .reset_index()
    )
    # spatial extent per genus
    ext = {}
    for t, g in occ.groupby("taxon"):
        pts = g.groupby("collection_no")[["lng", "lat"]].median()
        ext[t] = extent_metrics(pts)["max_dist_km"]
    taxa_stats["extent_km"] = taxa_stats["taxon"].map(ext)
    taxa_stats["occupancy"] = taxa_stats["n_coll"] / n_all_colls
    taxa_stats["is_allo"] = taxa_stats["taxon"] == "Allosaurus"

    X = taxa_stats.assign(
        pred=(taxa_stats["guild"] == "predator").astype(int)
    )[["duration", "n_occ", "pred"]]
    X = sm.add_constant(X)
    y = taxa_stats["extent_km"]
    fit = sm.OLS(y, X).fit()
    resid = taxa_stats["extent_km"] - fit.predict(X)
    taxa_stats["extent_resid"] = resid
    taxa_stats["extent_resid_z"] = resid / resid.std()
    write(taxa_stats, "allo_duration_model_taxa.csv")
    write(
        pd.DataFrame(
            {
                "term": fit.params.index,
                "coef": fit.params.values,
                "p": fit.pvalues.values,
            }
        ),
        "allo_duration_model_fit.csv",
    )

    # ---------- 4. Preservation / collection-bias model ----------
    y_allo = pd.Series(
        occ[occ["taxon"] == "Allosaurus"]["collection_no"].unique(), name="c"
    )
    coll_env["allo_present"] = coll_env.index.isin(y_allo).astype(int)
    env_dum = pd.get_dummies(
        coll_env[["environment", "lithology1", "member", "state", "systems_tract"]]
        .fillna("unknown")
        .astype(str),
        drop_first=True,
    )
    Xp = sm.add_constant(
        pd.concat([env_dum.astype(float), coll_env[["n_dino_taxa"]].fillna(0)], axis=1)
    )
    logit = sm.Logit(coll_env["allo_present"], Xp).fit(disp=0)
    write(
        pd.DataFrame(
            {"term": logit.params.index, "coef": logit.params.values,
             "p": logit.pvalues.values}
        ).sort_values("p"),
        "allo_presence_logit.csv",
    )
    phat = logit.predict(Xp)
    write(
        pd.DataFrame(
            {
                "metric": [
                    "allo_observed_occupancy",
                    "allo_expected_occupancy_mean_phat",
                    "logit_pseudo_r2",
                ],
                "value": [
                    coll_env["allo_present"].mean(),
                    float(phat.mean()),
                    float(logit.prsquared),
                ],
            }
        ),
        "allo_presence_summary.csv",
    )

    # ---------- 5. Predator comparison ----------
    prow = []
    for t, g in occ[occ["guild"] == "predator"].groupby("taxon"):
        pts = g.groupby("collection_no")[["lng", "lat"]].median()
        env_breadth = coll_env.loc[
            coll_env.index.isin(pts.index), "environment"
        ].nunique()
        m = extent_metrics(pts)
        dur = g["max_ma"].max() - g["min_ma"].min()
        prow.append(
            {
                "taxon": t,
                "n_occurrences": len(g),
                "n_collections": pts.shape[0],
                "occupancy_share": pts.shape[0] / n_all_colls,
                "duration_ma": dur,
                "env_breadth": env_breadth,
                **m,
            }
        )
    write(pd.DataFrame(prow).sort_values("occupancy_share", ascending=False),
          "allo_predator_comparison.csv")

    # ---------- 6. Matched-taxon controls ----------
    pool = taxa_stats[taxa_stats["taxon"] != "Allosaurus"].reset_index(drop=True)
    allo = taxa_stats[taxa_stats["taxon"] == "Allosaurus"].iloc[0]
    all_ranks_nocc = taxa_stats["n_occ"].rank()
    all_ranks_dur = taxa_stats["duration"].rank()
    pool_r_nocc = all_ranks_nocc[taxa_stats["taxon"] != "Allosaurus"].reset_index(drop=True)
    pool_r_dur = all_ranks_dur[taxa_stats["taxon"] != "Allosaurus"].reset_index(drop=True)
    allo_r_nocc = all_ranks_nocc[taxa_stats["taxon"] == "Allosaurus"].iloc[0]
    allo_r_dur = all_ranks_dur[taxa_stats["taxon"] == "Allosaurus"].iloc[0]
    dist = np.sqrt(
        ((pool_r_nocc - allo_r_nocc) / len(taxa_stats)) ** 2
        + ((pool_r_dur - allo_r_dur) / len(taxa_stats)) ** 2
    )
    pool["match_dist"] = dist.values
    matched = pool.nsmallest(min(10, len(pool)), "match_dist")
    write(matched, "allo_matched_taxa.csv")
    pct = float((matched["extent_km"] <= allo["extent_km"]).mean())
    occ_pct = float((matched["occupancy"] <= allo["occupancy"]).mean())
    write(
        pd.DataFrame(
            {
                "metric": ["matched_extent_percentile", "matched_occupancy_percentile"],
                "value": [pct, occ_pct],
            }
        ),
        "allo_matched_percentiles.csv",
    )

    # ---------- 7. Generalism: Allosaurus occupancy vs regional prey turnover
    regs = coll_env["state"].fillna("unknown")
    occ2 = occ.copy()
    occ2["region"] = occ2["collection_no"].map(regs)
    reg_rows = []
    for reg, g in occ2.groupby("region"):
        h = g[g["guild"] == "herbivore"]
        if h["collection_no"].nunique() < 3:
            continue
        allo_c = g[g["taxon"] == "Allosaurus"]["collection_no"].nunique()
        reg_rows.append(
            {
                "region": reg,
                "n_dino_colls": g["collection_no"].nunique(),
                "n_herb_genera": h["taxon"].nunique(),
                "allo_collections": allo_c,
                "allo_regional_share": allo_c / g["collection_no"].nunique(),
            }
        )
    write(pd.DataFrame(reg_rows), "allo_regional_generalism.csv")

    print("done")


if __name__ == "__main__":
    main()
