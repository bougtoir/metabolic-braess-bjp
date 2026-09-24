#!/usr/bin/env python3
"""
Minimal distributed-lag non-linear model (DLNM) cross-basis utilities.

Implements the Gasparrini (2010) cross-basis: a tensor product of a predictor
(exposure) basis and a lag basis, built here on natural cubic regression
splines (patsy `cr`). Kept dependency-light (numpy + patsy) so the whole
pipeline is reproducible from a clean environment.

References:
  Gasparrini A, Armstrong B, Kenward MG. Distributed lag non-linear models.
  Stat Med 2010;29:2224-34.
  Gasparrini A, Leone M. Attributable risk from distributed lag models.
  BMC Med Res Methodol 2014;14:55.
"""
import numpy as np
import pandas as pd
from patsy import dmatrix, build_design_matrices


def _cr_basis(x, df):
    """Natural cubic regression spline basis (no intercept) with reusable knots."""
    di = dmatrix(f"cr(x, df={df}) - 1", {"x": np.asarray(x, float)},
                 return_type="dataframe")
    return np.asarray(di), di.design_info


def _cr_apply(design_info, x):
    return np.asarray(build_design_matrices([design_info], {"x": np.asarray(x, float)})[0])


def lag_matrix(df, group, date, value, maxlag):
    """Return array (n, maxlag+1) of lagged exposure, lag 0..maxlag, per group.
    Assumes daily continuous dates within each group."""
    d = df[[group, date, value]].copy().sort_values([group, date])
    out = np.full((len(d), maxlag + 1), np.nan)
    for l in range(maxlag + 1):
        out[:, l] = d.groupby(group)[value].shift(l).values
    return d.index.values, out


class DistLagBins:
    """Constrained distributed-lag model: the exposure is summarised over a small
    number of lag windows (moving averages), each entered through a nonlinear
    natural-spline basis. This avoids the rank deficiency / ill-conditioning of a
    full spline tensor cross-basis while keeping a nonlinear exposure-response and
    an interpretable acute-vs-delayed lag structure.

    bins: list of inclusive (lo, hi) lag ranges, e.g. [(0,0),(1,3),(4,10)].
    """

    def __init__(self, exposure_all, bins, var_df=4):
        self.bins = list(bins)
        self.maxlag = max(hi for _, hi in self.bins)
        B0, self.var_info = _cr_basis(exposure_all, var_df)
        # patsy `cr` spans the constant, so every lag window would share it and
        # the stacked basis is rank-deficient. Reduce to the constant-free
        # subspace once (SVD of the centred basis); the intercept carries level.
        self._mean = B0.mean(0)
        _, _, Vt = np.linalg.svd(B0 - self._mean, full_matrices=False)
        self._V = Vt[:var_df - 1].T                # (var_df, var_df-1)
        self.vx = var_df - 1

    def _reduced(self, x):
        return (_cr_apply(self.var_info, np.asarray(x, float)) - self._mean) @ self._V

    def _bin_mean(self, lagged, lo, hi):
        return np.nanmean(lagged[:, lo:hi + 1], axis=1)

    def transform(self, lagged):
        """lagged (n, L+1) -> (n, nbins*vx): reduced ns(mean exposure) per window.
        Rows with incomplete lag history (NaN) are filled here with 0 and must be
        excluded by the caller via a complete-history mask."""
        cols = [self._reduced(np.nan_to_num(self._bin_mean(lagged, lo, hi), nan=0.0))
                for lo, hi in self.bins]
        return np.hstack(cols)

    def cumulative_basis(self, xvals):
        """Basis for a sustained exposure xvals held across all lag windows."""
        return np.tile(self._reduced(xvals), (1, len(self.bins)))

    def bin_basis(self, xvals, which):
        """Basis isolating a single lag window (others zero)."""
        Bx = self._reduced(xvals)
        out = np.zeros((len(xvals), self.vx * len(self.bins)))
        out[:, which * self.vx:(which + 1) * self.vx] = Bx
        return out

    def colnames(self, prefix="dl"):
        return [f"{prefix}_b{bi}_v{v}" for bi in range(len(self.bins))
                for v in range(self.vx)]


class CrossBasis:
    def __init__(self, exposure_all, maxlag, var_df=4, lag_df=3):
        self.maxlag = maxlag
        self.var_df = var_df
        self.lag_df = lag_df
        # predictor basis defined on the pooled exposure distribution
        _, self.var_info = _cr_basis(exposure_all, var_df)
        self.vx = len(self.var_info.column_names)
        # lag basis over integer lags 0..maxlag
        lags = np.arange(maxlag + 1)
        self.lag_basis, self.lag_info = _cr_basis(lags, lag_df)  # (L+1, vl)
        self.vl = self.lag_basis.shape[1]
        self.lag_sum = self.lag_basis.sum(axis=0)  # for cumulative reduction

    def transform(self, lagged):
        """lagged: (n, L+1) exposure. Return cross-basis (n, vx*vl)."""
        n = lagged.shape[0]
        # B[l] = var-basis applied to exposure at lag l  -> (n, vx)
        cb = np.zeros((n, self.vx * self.vl))
        # accumulate over lags: CB[:, v, w] = sum_l Bl[:,v] * C[l,w]
        acc = np.zeros((n, self.vx, self.vl))
        for l in range(self.maxlag + 1):
            Bl = _cr_apply(self.var_info, np.nan_to_num(lagged[:, l], nan=np.nanmean(lagged)))
            acc += Bl[:, :, None] * self.lag_basis[l][None, None, :]
        return acc.reshape(n, self.vx * self.vl)

    def cumulative_basis(self, xvals):
        """Cumulative (lag-summed) basis for exposure values xvals -> (m, vx*vl).
        Used to draw the overall cumulative exposure-response curve."""
        B = _cr_apply(self.var_info, np.asarray(xvals, float))  # (m, vx)
        # cumulative over lag = B[:,v] * lag_sum[w]
        cb = B[:, :, None] * self.lag_sum[None, None, :]
        return cb.reshape(len(xvals), self.vx * self.vl)

    def colnames(self, prefix="cb"):
        return [f"{prefix}_v{v}_l{w}" for v in range(self.vx) for w in range(self.vl)]
