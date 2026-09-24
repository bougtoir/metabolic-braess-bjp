"""Robustness refit of the Allosaurus presence model.

The unpenalized statsmodels Logit showed separation (state coefficients
~17, MLE non-convergence). Refit with L2-penalized logistic regression
(sklearn) and report a McFadden-style pseudo-R2 computed from
predicted-probability log-likelihood. Exploratory robustness only.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]          # methodological_beta_bias
SIB = ROOT.parent                                  # dinosaur_migration_foodweb
ALLO = SIB / "allosaurus_spatial_ecology"
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss


def main() -> None:
    occ = pd.read_csv(SIB / "data" / "processed" / "occurrences_clean.csv")
    occ = occ[occ["guild"].isin(["herbivore", "predator"])]
    dino_colls = occ["collection_no"].unique()

    raw = pd.read_excel(
        SIB / "data" / "raw" / "maidment2024_dryad" /
        "Occurrence_data_with_STs_dinos.xlsx"
    )
    raw_dino = raw[raw["collection_no"].isin(dino_colls)]
    coll_env = raw_dino.groupby("collection_no").agg(
        environment=("environment", "first"),
        lithology1=("lithology1", "first"),
        member=("member", "first"),
        state=("state", "first"),
        systems_tract=("Systems_tract", "first"),
    )
    coll_rich = raw_dino.assign(
        g=raw_dino["genus"].fillna(raw_dino["accepted_name"])
    ).groupby("collection_no")["g"].nunique().rename("n_dino_taxa")
    coll_env = coll_env.join(coll_rich)

    y_allo = occ.loc[occ["taxon"] == "Allosaurus", "collection_no"].unique()
    coll_env["allo_present"] = coll_env.index.isin(y_allo).astype(int)

    env_dum = pd.get_dummies(
        coll_env[["environment", "lithology1", "member", "state", "systems_tract"]]
        .fillna("unknown").astype(str),
        drop_first=True,
    )
    X = pd.concat(
        [env_dum.astype(float), coll_env[["n_dino_taxa"]].fillna(0)], axis=1
    )
    y = coll_env["allo_present"].values

    rows = []
    for c in (10.0, 1.0, 0.1):
        m = LogisticRegression(C=c, penalty="l2", solver="lbfgs",
                               max_iter=5000)
        m.fit(X.values, y)
        p = np.clip(m.predict_proba(X.values)[:, 1], 1e-12, 1 - 1e-12)
        ll = -len(y) * log_loss(y, p, normalize=True)
        p0 = y.mean()
        ll0 = np.sum(y * np.log(p0) + (1 - y) * np.log(1 - p0))
        rows.append({
            "penalty_C": c,
            "converged": True,
            "pseudo_r2_penalized": 1 - ll / ll0,
            "mean_phat": float(p.mean()),
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "presence_model_robustness.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
