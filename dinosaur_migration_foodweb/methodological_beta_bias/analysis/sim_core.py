"""Shared simulator for methodological_beta_bias.

Generates artificial fossil guild assemblages on a 1-D spatial axis so
that the *true* guild turnover contrast is known and the *observed*
contrast can be decomposed into bias terms.

Everything is incidence-based and uses the same Jaccard mean-pairwise
beta as the empirical pipeline.
"""
from __future__ import annotations

import numpy as np


def mean_beta_jaccard(mat: np.ndarray) -> float:
    rich = mat.sum(axis=1).astype(float)
    shared = (mat @ mat.T).astype(float)
    union = rich[:, None] + rich[None, :] - shared
    diss = 1.0 - np.divide(shared, union, out=np.ones_like(shared), where=union > 0)
    iu = np.triu_indices_from(diss, k=1)
    return float(diss[iu].mean())


def gen_taxon(n_loc: int, breadth: float, occ_p: float, rng) -> np.ndarray:
    """Contiguous range centred randomly; occupancy w.p. occ_p in range."""
    m = np.zeros(n_loc)
    c = rng.uniform(0, 1)
    half = breadth / 2
    lo, hi = (c - half) % 1.0, (c + half) % 1.0
    x = np.arange(n_loc) / n_loc
    inside = (x >= lo) & (x <= hi) if lo <= hi else (x >= lo) | (x <= hi)
    m[inside] = rng.random(inside.sum()) < occ_p
    return m


def gen_guild(n_loc: int, n_taxa: int, breadth: float, occ_p: float, rng,
              dominant_p: float = 0.0, keep_empty: bool = False) -> np.ndarray:
    """Return incidence matrix (localities x taxa). If dominant_p>0 the
    first taxon is a dominant: it occupies dominant_p of all localities
    range-wide."""
    taxa = [
        gen_taxon(n_loc, breadth, occ_p, rng) for _ in range(n_taxa)
    ]
    if dominant_p > 0 and n_taxa > 0:
        taxa[0] = (rng.random(n_loc) < dominant_p).astype(float)
    mat = np.stack(taxa, axis=1)
    if keep_empty:
        return mat
    keep = mat.sum(axis=1) > 0
    return mat[keep]


def delta_beta(mat_h: np.ndarray, mat_p: np.ndarray) -> float:
    return mean_beta_jaccard(mat_p) - mean_beta_jaccard(mat_h)


def sign_class(bias: float, delta_obs: float, delta_true: float) -> str:
    if abs(delta_true) < 1e-9:
        return "false_difference" if abs(delta_obs) > 0.05 else "ok"
    if np.sign(delta_obs) != np.sign(delta_true):
        return "sign_reversed"
    return "attenuated" if abs(delta_obs) < abs(delta_true) * 0.9 else "preserved"
