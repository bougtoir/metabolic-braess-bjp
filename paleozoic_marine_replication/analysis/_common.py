"""Shared constants and utilities for the Paleozoic marine replication.

Strict conceptual replication of
dinosaur_migration_foodweb/methodological_beta_bias: same Jaccard
mean-pairwise beta, same perturbation logic, same 2-D simulator
structure. Only parameter values differ (documented in
results/parameter_registry.csv).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROC = ROOT / "data" / "processed"
OUT = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"
for d in (DATA_RAW, DATA_PROC, OUT, FIG):
    d.mkdir(parents=True, exist_ok=True)

CLADES = ["Brachiopoda", "Trilobita", "Bivalvia", "Gastropoda",
          "Cephalopoda", "Crinoidea"]
# Cambrian base -> end-Permian (PBDB scale 1)
AGE_OLD, AGE_YOUNG = 538.8, 251.902

# Predefined minimum sampling thresholds (spec section 5)
MIN_SITES = 5
MIN_TAXA = 5
MIN_PAIRS_DECAY = 10

POOL_FRACTIONS = [1.0, 0.75, 0.5, 0.25]
SAMP_FRACTIONS = [1.0, 0.75, 0.5, 0.25]
RNG_SEED = 20260921
EARTH_R = 6371.0


def log_provenance(name: str, url: str, path: Path) -> None:
    rec = {"dataset": name, "url": url,
           "downloaded_utc": datetime.now(timezone.utc).isoformat(),
           "path": str(path.relative_to(ROOT))}
    prov = DATA_RAW / "provenance.jsonl"
    with prov.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def great_circle_km(lat1, lon1, lat2, lon2):
    """Vectorised haversine distance in km."""
    la1, lo1, la2, lo2 = map(np.radians, (lat1, lon1, lat2, lon2))
    h = (np.sin((la2 - la1) / 2) ** 2
         + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2)
    return 2 * EARTH_R * np.arcsin(np.sqrt(h))


def mean_beta_jaccard(mat: np.ndarray) -> float:
    """Identical to dinosaur methodological_beta_bias sim_core."""
    rich = mat.sum(axis=1).astype(float)
    shared = (mat @ mat.T).astype(float)
    union = rich[:, None] + rich[None, :] - shared
    diss = 1.0 - np.divide(shared, union, out=np.ones_like(shared),
                           where=union > 0)
    iu = np.triu_indices_from(diss, k=1)
    return float(diss[iu].mean())


def pairwise_dissimilarity(mat: np.ndarray):
    """Pairwise Jaccard, Sorensen, turnover (Simpson) and nestedness
    components (Baselga partition) on the upper triangle.

    Sorensen = 1 - 2a/(2a+b+c); Simpson turnover = 1 - a/(a+min(b,c));
    nestedness = Sorensen - Simpson. Jaccard = 1 - a/(a+b+c).
    """
    rich = mat.sum(axis=1).astype(float)
    a = (mat @ mat.T).astype(float)
    n = mat.shape[0]
    iu = np.triu_indices(n, k=1)
    i, j = iu
    aa = a[iu]
    b = rich[i] - aa
    c = rich[j] - aa
    jac = 1 - np.divide(aa, aa + b + c, out=np.ones_like(aa),
                        where=(aa + b + c) > 0)
    sor = 1 - np.divide(2 * aa, 2 * aa + b + c, out=np.ones_like(aa),
                        where=(2 * aa + b + c) > 0)
    sim = 1 - np.divide(aa, aa + np.minimum(b, c),
                        out=np.ones_like(aa),
                        where=(aa + np.minimum(b, c)) > 0)
    nes = np.clip(sor - sim, 0, None)
    return {"jaccard": jac, "sorensen": sor, "turnover": sim,
            "nestedness": nes, "i": i, "j": j}


def decay_slope(diss: np.ndarray, dist: np.ndarray):
    """OLS slope of dissimilarity ~ distance (same model family as the
    dinosaur analysis: linear fit on pairwise values)."""
    ok = dist > 0
    if ok.sum() < MIN_PAIRS_DECAY:
        return np.nan
    return float(np.polyfit(dist[ok], diss[ok], 1)[0])


def grid_cells(df: pd.DataFrame, res_deg: float) -> pd.Series:
    """Assign paleocoords to an equal-angle grid cell of res_deg."""
    return (np.round(df["plat"] / res_deg).astype(int).astype(str) + ":"
            + np.round(df["plng"] / res_deg).astype(int).astype(str))
