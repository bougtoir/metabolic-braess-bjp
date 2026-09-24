"""Shared beta-diversity machinery for analyses 05 and 06."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import haversine_km

DIST_BIN_KM = 100.0


def incidence_matrix(occ: pd.DataFrame) -> pd.DataFrame:
    return pd.crosstab(occ["collection_no"], occ["taxon"]).clip(upper=1)


def pairwise_simpson(mat: np.ndarray) -> np.ndarray:
    """Pairwise Simpson turnover dissimilarity for a 0/1 incidence matrix.

    Vectorised; numerically identical to the per-pair loop.
    """
    mat = mat.astype(float)
    rich = mat.sum(axis=1)
    shared = mat @ mat.T
    denom = np.minimum(rich[:, None], rich[None, :])
    out = 1.0 - np.divide(shared, denom, out=np.ones_like(shared), where=denom > 0)
    np.fill_diagonal(out, 0.0)
    return out


def pairwise_sorensen(mat: np.ndarray) -> np.ndarray:
    mat = mat.astype(float)
    rich = mat.sum(axis=1)
    shared = mat @ mat.T
    denom = rich[:, None] + rich[None, :]
    out = 1.0 - np.divide(2 * shared, denom, out=np.ones_like(shared), where=denom > 0)
    np.fill_diagonal(out, 0.0)
    return out


def beta_by_distance(dist: np.ndarray, diss: np.ndarray, bin_km: float = DIST_BIN_KM) -> pd.Series:
    iu = np.triu_indices_from(dist, k=1)
    d = dist[iu]
    b = diss[iu]
    bins = np.floor(d / bin_km).astype(int) * bin_km
    s = pd.Series(b).groupby(pd.Series(bins)).mean()
    s.index = s.index + bin_km / 2
    return s


def mean_beta(diss: np.ndarray) -> float:
    iu = np.triu_indices_from(diss, k=1)
    return float(diss[iu].mean())


def bootstrap_rows(mat: np.ndarray, rng) -> np.ndarray:
    """Resample rows (assemblages) of an incidence matrix WITH replacement.

    Rows must be duplicated by index, not filtered by ID -- the same
    collection drawn twice contributes two resampled assemblages.
    """
    idx = rng.integers(0, mat.shape[0], size=mat.shape[0])
    return mat[idx]


def mantel(dist: np.ndarray, diss: np.ndarray, n_perm: int, rng) -> tuple[float, float]:
    """Mantel test (Spearman), same statistic as the loop version but with a
    flat-index gather instead of a per-permutation matrix rebuild."""
    n = dist.shape[0]
    iu = np.triu_indices_from(dist, k=1)
    d, b = dist[iu], diss[iu]
    r_obs = spearmanr(d, b).statistic
    d_rank = rankdata(d)
    d_rank = (d_rank - d_rank.mean()) / d_rank.std()
    flat = diss.reshape(-1)
    perm = np.empty(n_perm)
    for k in range(n_perm):
        p = rng.permutation(n)
        bp = flat[p[iu[0]] * n + p[iu[1]]]
        b_rank = rankdata(bp)
        b_rank = (b_rank - b_rank.mean()) / b_rank.std()
        perm[k] = float((d_rank * b_rank).mean())
    p_val = (1 + np.sum(np.abs(perm) >= abs(r_obs))) / (n_perm + 1)
    return float(r_obs), float(p_val)


def guild_pieces(occ: pd.DataFrame, guild: str):
    sub = occ[occ["guild"] == guild]
    mat = incidence_matrix(sub)
    coll = sub.groupby("collection_no")[["lng", "lat"]].median().loc[mat.index]
    dist = haversine_km(
            coll["lng"].to_numpy()[:, None],
            coll["lat"].to_numpy()[:, None],
            coll["lng"].to_numpy()[None, :],
            coll["lat"].to_numpy()[None, :],
        )
    return mat, dist


def bootstrap_delta_beta(
    occ: pd.DataFrame,
    fn,
    n_boot: int,
    rng,
    guild_col: str = "guild",
) -> np.ndarray:
    """Collection bootstrap of Delta-beta = mean_beta(predator) - mean_beta(herbivore).

    Resamples rows of each guild's incidence matrix (proper bootstrap).
    """
    mats = {}
    for guild in ("herbivore", "predator"):
        sub = occ[occ[guild_col] == guild]
        mats[guild] = incidence_matrix(sub).to_numpy()
    out = np.empty(n_boot)
    for i in range(n_boot):
        vals = []
        for guild in ("herbivore", "predator"):
            mb = bootstrap_rows(mats[guild], rng)
            vals.append(mean_beta(fn(mb)))
        out[i] = vals[1] - vals[0]
    return out


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


def load_clean_genus_occurrences() -> pd.DataFrame:
    from _common import PROCESSED

    occ = pd.read_csv(PROCESSED / "occurrences_clean.csv")
    occ = occ[occ["resolution"] == "genus"].copy()
    return occ[occ["guild"].isin(["herbivore", "predator"])]
