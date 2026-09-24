"""Minimal 2-D robustness check (GEB requirement).

Square lattice L x L; each taxon occupies a disc of radius r
(fraction of lattice width) centred uniformly; recorded w.p. occ_p
inside its disc. Reproduces:
  (a) gamma-imbalance false contrast (n_p=4 vs n_h=26, Δβ_true=0)
  (b) temporal-aggregation attenuation (8 slices -> 1 pooled bin)
  (c) distance-decay slope bias: does pool asymmetry change the
      estimated distance-decay slope per guild, not just mean beta?
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"

RNG_SEED = 20260924
L = 40          # 40x40 lattice
N_H = 26
OCC_P = 0.35
R_FRAC = 0.225  # disc radius as fraction of L
REPS = 100


def gen_taxon_2d(L, r_frac, occ_p, rng):
    c = rng.uniform(0, 1, 2) * L
    xx, yy = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
    d = np.sqrt((xx - c[0]) ** 2 + (yy - c[1]) ** 2)
    inside = d <= r_frac * L
    return (inside & (rng.random((L, L)) < occ_p)).astype(float).ravel()


def guild_2d(L, n, r_frac, occ_p, rng, drop_empty=True):
    m = np.stack([gen_taxon_2d(L, r_frac, occ_p, rng) for _ in range(n)],
                 axis=1)
    if drop_empty:
        m = m[m.sum(axis=1) > 0]
    return m


def mean_beta(mat):
    rich = mat.sum(1)
    shared = mat @ mat.T
    union = rich[:, None] + rich[None, :] - shared
    diss = 1 - np.divide(shared, union, out=np.ones_like(shared),
                         where=union > 0)
    iu = np.triu_indices_from(diss, 1)
    return float(diss[iu].mean())


def decay_slope(mat, coords):
    """OLS slope of pairwise Jaccard dissimilarity ~ distance."""
    dist, d = _pairwise(mat, coords)
    ok = dist > 0
    return float(np.polyfit(dist[ok], d[ok], 1)[0])


def _pairwise(mat, coords):
    rich = mat.sum(1)
    shared = mat @ mat.T
    union = rich[:, None] + rich[None, :] - shared
    diss = 1 - np.divide(shared, union, out=np.ones_like(shared),
                         where=union > 0)
    iu = np.triu_indices_from(diss, 1)
    dist = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2)
                   .sum(-1))[iu]
    return dist, diss[iu]


def decay_curve(mat, coords, bins):
    """Mean Jaccard dissimilarity per distance bin."""
    dist, d = _pairwise(mat, coords)
    idx = np.digitize(dist, bins)
    out = np.full(len(bins) - 1, np.nan)
    for b in range(1, len(bins)):
        sel = idx == b
        if sel.any():
            out[b - 1] = d[sel].mean()
    return out


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    xx, yy = np.meshgrid(np.arange(L), np.arange(L), indexing="ij")
    coords = np.stack([xx.ravel(), yy.ravel()], axis=1)

    # (a) gamma imbalance
    rows = []
    for n_p in (2, 4, 12, 26):
        vals, sp, sh = [], [], []
        for _ in range(REPS):
            mh = guild_2d(L, N_H, R_FRAC, OCC_P, rng, drop_empty=False)
            mp = guild_2d(L, n_p, R_FRAC, OCC_P, rng, drop_empty=False)
            kh, kp = mh.sum(1) > 0, mp.sum(1) > 0
            mh_f, mp_f = mh[kh], mp[kp]
            vals.append(mean_beta(mp_f) - mean_beta(mh_f))
            sp.append(decay_slope(mp_f, coords[kp]))
            sh.append(decay_slope(mh_f, coords[kh]))
        rows.append(dict(n_pred_taxa=n_p,
                         delta_beta_mean=np.mean(vals),
                         lo95=np.quantile(vals, .025),
                         hi95=np.quantile(vals, .975),
                         decay_slope_pred=np.mean(sp),
                         decay_slope_herb=np.mean(sh),
                         decay_slope_diff=np.mean(np.array(sp) - np.array(sh))))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim13_2d_gamma.csv", index=False)
    print(df.round(4).to_string(index=False))

    # (c) distance-decay curves for the pool-4 case (Fig. 3b)
    bins = np.arange(0, 60, 4.0)
    curves_p, curves_h = [], []
    for _ in range(REPS):
        mh = guild_2d(L, N_H, R_FRAC, OCC_P, rng, drop_empty=False)
        mp = guild_2d(L, 4, R_FRAC, OCC_P, rng, drop_empty=False)
        kh, kp = mh.sum(1) > 0, mp.sum(1) > 0
        curves_p.append(decay_curve(mp[kp], coords[kp], bins))
        curves_h.append(decay_curve(mh[kh], coords[kh], bins))
    pd.DataFrame({
        "dist_bin_center": (bins[:-1] + bins[1:]) / 2,
        "dissim_smallpool": np.nanmean(curves_p, 0),
        "dissim_comparison": np.nanmean(curves_h, 0),
    }).to_csv(OUT / "sim13_2d_decay_curves.csv", index=False)

    # (b) temporal aggregation in 2-D
    rows = []
    for n_bins in (8, 4, 1):
        group = 8 // n_bins
        vals = []
        for _ in range(30):
            dbins = []
            for b in range(n_bins):
                mh = np.zeros((L * L, N_H))
                mp = np.zeros((L * L, 12))
                for s in range(group):
                    mh = np.maximum(mh, guild_2d(L, N_H, R_FRAC * .75,
                                                 OCC_P, rng,
                                                 drop_empty=False))
                    mp = np.maximum(mp, guild_2d(L, 12, R_FRAC * .75,
                                                 OCC_P, rng,
                                                 drop_empty=False))
                dbins.append(mean_beta(mp[mp.sum(1) > 0])
                             - mean_beta(mh[mh.sum(1) > 0]))
            vals.append(np.mean(dbins))
        rows.append(dict(temporal_bins=n_bins,
                         delta_beta_mean=np.mean(vals)))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sim13_2d_temporal.csv", index=False)
    print(df.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
