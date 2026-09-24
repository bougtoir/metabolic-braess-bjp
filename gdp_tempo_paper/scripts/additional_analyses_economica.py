"""Additional analyses for the Economica (Wiley/LSE) submission.

Implements the six items listed in next_session_handoff.md (section A):
  A.1 Solow-residual historical-decomposition narrative (concrete episodes)
  A.2 Counterfactual-wealth narrative ("So what?" country-level implications)
  A.3 Future forecast simulation (2020-2040) under mu(t) continuation,
      stabilisation, AI/digital investment surge, and TFP-stagnation scenarios
  A.4 Cross-country cluster analysis by (mu, beta) and asset composition
  A.5 Time-varying depreciation robustness check
  A.6 Monte Carlo identification-sharpness simulation

Reads existing reproducible outputs:
  - data/fair_eval.csv
  - data/solow_decomposition.csv
  - data/counterfactual_wealth.csv
  - data/observable_mu.csv

Also re-uses the public PWT/WDI/OECD source data via run_paper_analyses.prepare_countries().

Writes new CSVs, figures (English + Japanese), and manuscript tables.
"""
from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster.vq import kmeans2
from sklearn.metrics import (
    silhouette_score,
    silhouette_samples,
    adjusted_rand_score,
)

# Japanese font registration (same as other figure scripts)
from matplotlib import font_manager
for path in ("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
             "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"):
    if os.path.exists(path):
        font_manager.fontManager.addfont(path)
        plt.rcParams["font.sans-serif"] = ["IPAGothic", "DejaVu Sans"]
        break

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
TAB = os.path.join(ROOT, "tables")
os.makedirs(DATA, exist_ok=True)
os.makedirs(FIG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)

import sys
sys.path.insert(0, HERE)
from run_paper_analyses import (
    prepare_countries, Country,
    pim_instant, pim_lagged, pim_lagged_tempo, build_intan_stock,
    fit_mu_const, fit_tempo, fit_joint,
    test_B_growth,
    DELTA_I,
)

# ---------------------------------------------------------------------------
# Utilities

LOG_BASE = 10


def pct(arr: np.ndarray) -> float:
    """Convert log difference to percentage points."""
    return float(arr * 100)


def safe_growth(series: np.ndarray) -> float:
    """Mean annual log growth, ignoring non-positive entries.

    If fewer than two valid observations are available (e.g. a country whose
    series is too short to estimate growth over 2010-2019), the function falls
    back to a conservative 2% per annum rate. This fallback is documented in
    Supplementary Section S.17.
    """
    s = np.asarray(series, dtype=float)
    s = s[np.isfinite(s) & (s > 0)]
    if len(s) < 2:
        return 0.02
    return float(np.mean(np.diff(np.log(s))))


def fill_series(x: np.ndarray) -> np.ndarray:
    """Forward/backward fill a 1-D array."""
    s = pd.Series(x)
    s = s.ffill().bfill()
    if s.isna().all():
        return np.full(len(x), np.nan)
    s = s.fillna(s.median())
    return s.to_numpy()


def compute_alpha_labsh(c: Country) -> float:
    return 1.0 - float(np.clip(np.mean(c.labsh), 0.40, 0.75))


# ---------------------------------------------------------------------------
# A.1  Solow-residual historical-decomposition narrative

NARRATIVE_EPISODES = [
    ("Japan", 1990, 1999, "Japan's 'lost decade'"),
    ("Japan", 2007, 2009, "Japan, global financial crisis"),
    ("United States", 1995, 2000, "United States, dot-com boom"),
    ("United States", 2007, 2009, "United States, global financial crisis"),
    ("Germany", 2007, 2009, "Germany, global financial crisis"),
    ("Republic of Korea", 1997, 1999, "Republic of Korea, Asian crisis"),
]


def run_solow_narrative(solow: pd.DataFrame) -> pd.DataFrame:
    """Create Table 7: concrete historical episodes from the decomposition.

    Episodes are selected from the largest OECD economies and Republic of Korea,
    covering well-documented macroeconomic episodes (asset-price collapse,
    technology boom, global financial crisis, and currency crisis) and requiring
    at least three years of data. This selection deliberately contrasts
    high- and low-investment-gestation regimes and is not driven by the
    magnitude of the estimated artifact.
    """
    rows = []
    for country, y0, y1, label in NARRATIVE_EPISODES:
        cdf = solow[(solow["country"] == country) &
                    (solow["year"] >= y0) & (solow["year"] <= y1)]
        if len(cdf) < 3:
            continue
        for mod in ("M0", "M2", "M4"):
            vals = cdf[f"tfp_{mod}"].to_numpy(dtype=float)
            if np.any(~np.isfinite(vals)):
                vals = vals[np.isfinite(vals)]
            if len(vals) < 2:
                continue
            dg = np.diff(vals)
            rows.append({
                "episode": label,
                "country": country,
                "period": f"{y0}-{y1}",
                "model": mod,
                "mean_TFP_growth_pp": round(float(np.mean(dg)) * 100, 2),
            })

    # Pivot to wide format
    if not rows:
        return pd.DataFrame()
    long = pd.DataFrame(rows)
    wide = long.pivot_table(
        index=["episode", "country", "period"],
        columns="model",
        values="mean_TFP_growth_pp",
    ).reset_index()
    wide.columns.name = None
    wide = wide.rename(columns={"M0": "M0_growth_pp",
                                "M2": "M2_growth_pp",
                                "M4": "M4_growth_pp"})
    for col in ["M0_growth_pp", "M2_growth_pp", "M4_growth_pp"]:
        if col not in wide.columns:
            wide[col] = np.nan
    wide["tempo_artifact_pp"] = wide["M0_growth_pp"] - wide["M2_growth_pp"]
    wide["joint_artifact_pp"] = wide["M0_growth_pp"] - wide["M4_growth_pp"]
    wide["artifact_share_pct"] = np.where(
        wide["M0_growth_pp"] != 0,
        (wide["tempo_artifact_pp"] / wide["M0_growth_pp"]) * 100,
        np.nan,
    )
    wide = wide.sort_values("tempo_artifact_pp", ascending=False, key=abs)
    return wide[["episode", "country", "period", "M0_growth_pp",
                 "M2_growth_pp", "M4_growth_pp", "tempo_artifact_pp",
                 "joint_artifact_pp", "artifact_share_pct"]]


def run_solow_narrative_loo(solow: pd.DataFrame) -> pd.DataFrame:
    """Leave-one-episode-out robustness for Table 7.

    For each episode, drop it from the sample and recompute the mean
    joint-artifact across the remaining episodes. A small deviation shows the
    narrative conclusion is not driven by a single episode.
    """
    base = run_solow_narrative(solow)
    if base.empty:
        return pd.DataFrame()
    full_mean = base["joint_artifact_pp"].mean()
    rows = []
    for episode in base["episode"].unique():
        sub = base[base["episode"] != episode]
        rows.append({
            "excluded": episode,
            "n_remaining": len(sub),
            "mean_joint_artifact_pp": round(float(sub["joint_artifact_pp"].mean()), 2),
            "full_mean_joint_artifact_pp": round(float(full_mean), 2),
            "delta_pp": round(float(sub["joint_artifact_pp"].mean() - full_mean), 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# A.2  Counterfactual-wealth narrative

def run_counterfactual_narrative(cf: pd.DataFrame) -> pd.DataFrame:
    """Create Table 8: top country-level counterfactual wealth adjustments."""
    if cf.empty:
        return pd.DataFrame()
    cols = ["country", "iso3", "beta_j", "cwon_pca_official",
            "cwon_pca_adjusted", "pca_gap_pct",
            "pca_gap_pct_1_5x", "pca_gap_pct_2_0x", "pca_gap_pct_3_0x",
            "cwon_tow_official", "cwon_tow_adjusted", "tow_gap_pct",
            "tow_gap_pct_1_5x", "tow_gap_pct_2_0x", "tow_gap_pct_3_0x",
            "intan_ratio"]
    cols = [c for c in cols if c in cf.columns]
    out = cf[cols].copy()
    out = out.sort_values("pca_gap_pct", ascending=False)
    for col in ["cwon_pca_official", "cwon_pca_adjusted",
                "cwon_tow_official", "cwon_tow_adjusted"]:
        if col in out.columns:
            out[col] = out[col].round(2)
    for col in ["pca_gap_pct", "tow_gap_pct",
                "pca_gap_pct_1_5x", "tow_gap_pct_1_5x",
                "pca_gap_pct_2_0x", "tow_gap_pct_2_0x",
                "pca_gap_pct_3_0x", "tow_gap_pct_3_0x",
                "beta_j", "intan_ratio"]:
        if col in out.columns:
            out[col] = out[col].round(2)
    return out


# ---------------------------------------------------------------------------
# A.3  Future forecast simulation (2020-2040)

FUTURE_HIGHLIGHT = ["United States", "Japan", "Germany",
                    "Republic of Korea", "China", "Colombia"]
FUTURE_YEARS = np.arange(2020, 2041)
FISCAL_GDP_SHARE = 0.02  # illustrative public-investment scenario


def project_investment(I_obs: np.ndarray, years_obs: np.ndarray,
                      start_year: int = 2010, end_year: int = 2019) -> np.ndarray:
    """Project constant-log-growth investment path for 2020-2040."""
    mask = (years_obs >= start_year) & (years_obs <= end_year)
    g = safe_growth(I_obs[mask])
    I_2019 = float(I_obs[-1])
    n = len(FUTURE_YEARS)
    # I[2020], I[2021], ..., I[2040]
    return I_2019 * np.exp(g * np.arange(1, n + 1))


def project_intangible_investment(Y_obs: np.ndarray, rnd_share: np.ndarray,
                                  years_obs: np.ndarray,
                                  extra_growth: float = 0.0) -> np.ndarray:
    """Project R&D-driven intangible investment, optionally boosted for AI surge."""
    s = fill_series(rnd_share)
    I_R_obs = Y_obs * s / 100.0
    mask = (years_obs >= 2010) & (years_obs <= 2019)
    g = safe_growth(I_R_obs[mask]) + extra_growth
    I_2019 = float(I_R_obs[-1])
    n = len(FUTURE_YEARS)
    return I_2019 * np.exp(g * np.arange(1, n + 1))


def project_labor(emp: np.ndarray, avh: np.ndarray, hc: np.ndarray,
                  years_obs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project raw labour (L) and human-capital-augmented labour (LH)."""
    L = emp * avh
    LH = L * hc
    mask = (years_obs >= 2010) & (years_obs <= 2019)
    g_L = safe_growth(L[mask])
    g_LH = safe_growth(LH[mask])
    L_2019 = float(L[-1])
    LH_2019 = float(LH[-1])
    n = len(FUTURE_YEARS)
    L_proj = L_2019 * np.exp(g_L * np.arange(1, n + 1))
    LH_proj = LH_2019 * np.exp(g_LH * np.arange(1, n + 1))
    return L_proj, LH_proj


def project_tfp(tfp_obs: np.ndarray, years_obs: np.ndarray,
                level_only: bool = False) -> np.ndarray:
    """Project TFP: 2010-2019 linear trend, or flat at the 2019 level."""
    tfp_obs = np.asarray(tfp_obs, dtype=float)
    mask = (years_obs >= 2010) & (years_obs <= 2019)
    y = years_obs[mask]
    t = y - y[0]
    x = np.column_stack([np.ones_like(t), t])
    intercept, slope = np.linalg.lstsq(x, tfp_obs[mask], rcond=None)[0][:2]
    n = len(FUTURE_YEARS)
    t_proj = FUTURE_YEARS - y[0]
    if level_only:
        # Hold fixed at the trend-implied 2019 level (stops extrapolation)
        return np.full(n, float(intercept + slope * t[-1]))
    return intercept + slope * t_proj


def project_public_investment(Y_2019: float,
                              logY_M4: np.ndarray,
                              idx_2020: int,
                              share: float = FISCAL_GDP_SHARE) -> np.ndarray:
    """Illustrative public-investment path tied to M4-corrected GDP growth.

    Public investment is set to `share` of 2019 GDP in 2020 and then grows at the
    same rate as the M4 baseline output path.  This is a stylised fiscal-policy
    scenario and is documented as such in Supplementary Section S.17.
    """
    n = len(FUTURE_YEARS)
    I_public = np.empty(n)
    I_public[0] = share * Y_2019
    Y_path = np.exp(logY_M4)
    for i in range(1, n):
        I_public[i] = I_public[i - 1] * (Y_path[idx_2020 + i] /
                                          Y_path[idx_2020 + i - 1])
    return I_public


def run_future_scenarios(countries: list[Country],
                         solow: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create Table 9 and Figure 15: 2020-2040 GDP-level scenarios.

    Baseline M4 extrapolates the 2010-2019 TFP trend.  Additional scenarios:
    - M2_trend and M2_stabilize: tempo-only effects.
    - M4_TFP_level_only: 2019 TFP level held fixed (no future trend).
    - M4_AI_surge: R&D-driven intangible investment grows 1.5 pp faster.
    - M4_fiscal_stimulus: public investment equal to 2% of 2019 GDP,
      growing with M4-corrected output, illustrating a policy link to
      fiscal capacity.
    """
    by_country = {c.country: c for c in countries}
    params = solow.groupby("country").first()[["alpha", "mu0", "mu1",
                                                  "mu_j", "beta_j"]]
    summary_rows = []
    detail_rows = []

    for country, row in params.iterrows():
        if country not in by_country:
            continue
        c = by_country[country]
        alpha = float(row["alpha"])
        mu0 = float(row["mu0"])
        mu1 = float(row["mu1"])
        mu_j = float(row["mu_j"])
        beta_j = float(row["beta_j"])

        # Observed series
        I_obs = c.I
        delta_obs = c.delta
        years_obs = c.years

        # Project investment and labour
        I_proj = project_investment(I_obs, years_obs)
        I_R_proj = project_intangible_investment(c.Y, c.rnd_share, years_obs)
        I_R_ai_proj = project_intangible_investment(
            c.Y, c.rnd_share, years_obs, extra_growth=0.015)
        L_proj, LH_proj = project_labor(c.emp, c.avh, c.hc, years_obs)

        # Full arrays 1970-2040
        I_full = np.concatenate([I_obs, I_proj])
        I_R_full = np.concatenate([c.Y * fill_series(c.rnd_share) / 100.0, I_R_proj])
        I_R_ai_full = np.concatenate([c.Y * fill_series(c.rnd_share) / 100.0, I_R_ai_proj])
        delta_full = np.concatenate([delta_obs,
                                     np.full(len(FUTURE_YEARS), delta_obs[-1])])
        years_full = np.concatenate([years_obs, FUTURE_YEARS])
        L_full = np.concatenate([c.emp * c.avh, L_proj])
        LH_full = np.concatenate([c.emp * c.avh * c.hc, LH_proj])

        # TFP series from solow decomposition
        cdf = solow[solow["country"] == country].sort_values("year")
        tfp_M0 = cdf["tfp_M0"].to_numpy(dtype=float)
        tfp_M2 = cdf["tfp_M2"].to_numpy(dtype=float)
        tfp_M4 = cdf["tfp_M4"].to_numpy(dtype=float)

        # Extend TFP arrays to full length (only 2020-2040 used)
        tfp_M0_full = np.concatenate([tfp_M0, project_tfp(tfp_M0, years_obs)])
        tfp_M2_full = np.concatenate([tfp_M2, project_tfp(tfp_M2, years_obs)])
        tfp_M4_full = np.concatenate([tfp_M4, project_tfp(tfp_M4, years_obs)])
        tfp_M4_level_full = np.concatenate([tfp_M4, project_tfp(tfp_M4, years_obs, level_only=True)])

        # Capital stocks
        K_M0_full = pim_instant(I_full, delta_full, float(c.K0))
        K_M2_trend_full = pim_lagged_tempo(I_full, delta_full, float(c.K0),
                                           mu0, mu1, years_full)
        mu_2019 = mu0 + mu1 * (2019 - years_obs[0])
        K_M2_stab_full = pim_lagged_tempo(I_full, delta_full, float(c.K0),
                                          mu_2019, 0.0, years_full)
        K_M4_full = pim_lagged(I_full, delta_full, float(c.K0), mu_j)

        # Intangible capital stocks (baseline + AI surge)
        # Project R&D-driven intangible investment and apply PIM
        I_R_obs = c.Y * fill_series(c.rnd_share) / 100.0
        K0_intan = float(I_R_obs[0] / (DELTA_I + 0.03))
        I_R_full = np.concatenate([I_R_obs, I_R_proj])
        I_R_ai_full = np.concatenate([I_R_obs, I_R_ai_proj])
        delta_intan_full = np.full(len(I_R_full), DELTA_I)
        K_intan_base_full = pim_instant(I_R_full, delta_intan_full, K0_intan)
        K_intan_ai_full = pim_instant(I_R_ai_full, delta_intan_full, K0_intan)

        # Ensure positivity
        K_M0_full = np.where(K_M0_full > 0, K_M0_full, 1e-6)
        K_M2_trend_full = np.where(K_M2_trend_full > 0, K_M2_trend_full, 1e-6)
        K_M2_stab_full = np.where(K_M2_stab_full > 0, K_M2_stab_full, 1e-6)
        K_M4_full = np.where(K_M4_full > 0, K_M4_full, 1e-6)
        K_intan_base_full = np.where(K_intan_base_full > 0, K_intan_base_full, 1e-6)
        K_intan_ai_full = np.where(K_intan_ai_full > 0, K_intan_ai_full, 1e-6)

        # GDP scenarios
        logY_M0 = alpha * np.log(K_M0_full) + (1 - alpha) * np.log(LH_full) + tfp_M0_full
        logY_M2_trend = alpha * np.log(K_M2_trend_full) + (1 - alpha) * np.log(LH_full) + tfp_M2_full
        logY_M2_stab = alpha * np.log(K_M2_stab_full) + (1 - alpha) * np.log(LH_full) + tfp_M2_full
        w_L = max(1e-6, 1 - alpha - beta_j)
        # M4 tfp_M4 was computed with human-capital-adjusted labour when beta_j == 0
        # and with raw labour when beta_j > 0; keep the same input for consistency.
        L_M4 = LH_full if beta_j == 0.0 else L_full
        logY_M4_base = (alpha * np.log(K_M4_full) +
                        beta_j * np.log(K_intan_base_full) +
                        w_L * np.log(L_M4) + tfp_M4_full)
        logY_M4_ai = (alpha * np.log(K_M4_full) +
                      beta_j * np.log(K_intan_ai_full) +
                      w_L * np.log(L_M4) + tfp_M4_full)
        logY_M4_level = (alpha * np.log(K_M4_full) +
                         beta_j * np.log(K_intan_base_full) +
                         w_L * np.log(L_M4) + tfp_M4_level_full)

        # Fiscal policy scenario: add public investment equal to 2% of 2019 GDP,
        # growing with the M4-corrected output path.
        idx_2020 = len(years_obs)
        y_2019 = float(c.Y[-1])
        I_public = project_public_investment(y_2019, logY_M4_base, idx_2020)
        I_fiscal_full = I_full.astype(float).copy()
        I_fiscal_full[idx_2020:idx_2020 + len(FUTURE_YEARS)] += I_public
        K_M4_fiscal_full = pim_lagged(I_fiscal_full, delta_full, float(c.K0), mu_j)
        K_M4_fiscal_full = np.where(K_M4_fiscal_full > 0, K_M4_fiscal_full, 1e-6)
        logY_M4_fiscal = (alpha * np.log(K_M4_fiscal_full) +
                          beta_j * np.log(K_intan_base_full) +
                          w_L * np.log(L_M4) + tfp_M4_full)

        idx_2019 = len(years_obs) - 1
        scenarios = {
            "M0_baseline": logY_M0,
            "M2_trend": logY_M2_trend,
            "M2_stabilize": logY_M2_stab,
            "M4_baseline": logY_M4_base,
            "M4_TFP_level_only": logY_M4_level,
            "M4_AI_surge": logY_M4_ai,
            "M4_fiscal_stimulus": logY_M4_fiscal,
        }

        # Save 2040 summary
        idx_2040 = np.where(years_full == 2040)[0][0]
        summary = {"country": country, "iso3": c.iso}
        for name, ly in scenarios.items():
            summary[f"{name}_2040_index"] = round(
                float(np.exp(ly[idx_2040]) / y_2019 * 100), 1)
            summary[f"{name}_2030_index"] = round(
                float(np.exp(ly[idx_2019 + 10]) / y_2019 * 100), 1)
        summary_rows.append(summary)

        # Save detail for plotting
        for yi, yr in enumerate(years_full):
            if yr < 2019:
                continue
            detail = {"country": country, "iso3": c.iso, "year": int(yr),
                      "actual": float(c.Y[yi]) if yi < len(c.Y) else np.nan}
            for name, ly in scenarios.items():
                detail[name] = float(np.exp(ly[yi]) / y_2019 * 100)
            detail_rows.append(detail)

    summary_df = pd.DataFrame(summary_rows)
    detail_df = pd.DataFrame(detail_rows)
    return summary_df, detail_df


def make_fig15_future(detail: pd.DataFrame, lang: str = "en"):
    """Figure 15: future GDP-index scenarios for selected countries."""
    labels = {
        "en": {
            "title": "2020-2040 GDP-level scenarios (2019=100)",
            "ylabel": "GDP index (2019=100)",
            "xlabel": "Year",
            "M0_baseline": "M0 baseline",
            "M2_trend": "M2 trend continuation",
            "M2_stabilize": "M2 stabilisation",
            "M4_baseline": "M4 baseline",
            "M4_TFP_level_only": "M4 TFP level only",
            "M4_AI_surge": "M4 AI/digital surge",
            "M4_fiscal_stimulus": "M4 public investment (2% GDP)",
        },
        "ja": {
            "title": "2020-2040年GDP水準シナリオ（2019年=100）",
            "ylabel": "GDP指数（2019年=100）",
            "xlabel": "年",
            "M0_baseline": "M0 基準",
            "M2_trend": "M2 トレンド継続",
            "M2_stabilize": "M2 安定化",
            "M4_baseline": "M4 基準",
            "M4_TFP_level_only": "M4 TFP水準固定",
            "M4_AI_surge": "M4 AI/デジタル投資急増",
            "M4_fiscal_stimulus": "M4 公共投資（GDPの2%）",
        },
    }[lang]

    scenario_cols = ["M0_baseline", "M2_trend", "M2_stabilize",
                     "M4_baseline", "M4_TFP_level_only", "M4_AI_surge",
                     "M4_fiscal_stimulus"]
    colors = ["#888888", "#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b2", "#ccb974"]
    styles = ["-", "-", "--", "-", ":", "-", "--"]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9), sharex=True, sharey=True)
    for ax, country in zip(axes.flat, FUTURE_HIGHLIGHT):
        cdf = detail[detail["country"] == country]
        if cdf.empty:
            ax.set_visible(False)
            continue
        years = cdf["year"].to_numpy()
        for col, color, style in zip(scenario_cols, colors, styles):
            ax.plot(years, cdf[col].to_numpy(), style, color=color,
                    label=labels[col], linewidth=1.5)
        ax.set_title(country, fontsize=10)
        ax.grid(alpha=0.3)
        ax.axhline(100, color="black", linewidth=0.5, linestyle="-")
    for ax in axes[-1]:
        ax.set_xlabel(labels["xlabel"])
    for ax in axes[:, 0]:
        ax.set_ylabel(labels["ylabel"], fontsize=9)
    handles, lbls = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, lbls, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.02), fontsize=9)
    fig.suptitle(labels["title"], y=0.99, fontsize=12)
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    out = os.path.join(FIG, f"fig15_future_scenarios_{lang}.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("wrote", out)


# ---------------------------------------------------------------------------
# A.4  Cross-country cluster analysis


def load_cluster_features(countries: list[Country],
                          fair: pd.DataFrame,
                          mu_df: pd.DataFrame) -> pd.DataFrame:
    """Build country-level feature set for clustering."""
    by_iso = {c.iso: c for c in countries}
    mu_recent = (mu_df[mu_df["year"] >= 2010]
                 .groupby("iso3")
                 .agg({"share_N111G": "mean",
                       "share_N112G": "mean",
                       "share_N1131G": "mean",
                       "share_N1132G": "mean",
                       "share_N117G": "mean",
                       "share_N11MG": "mean"}))
    mu_recent = mu_recent.reset_index()

    # Compute robust equipment/ICT share avoiding double counting
    def equipment_share(row):
        if pd.notna(row["share_N1132G"]):
            return (row.get("share_N1131G", 0) or 0) + (row["share_N1132G"] or 0)
        return row.get("share_N11MG", 0) or 0

    mu_recent["share_equipment"] = mu_recent.apply(equipment_share, axis=1)
    mu_recent["share_structures"] = (mu_recent["share_N111G"].fillna(0) +
                                     mu_recent["share_N112G"].fillna(0))
    mu_recent["share_ipp"] = mu_recent["share_N117G"].fillna(0)

    merged = fair[["country", "iso3", "mu_M4", "beta_M4", "mu_M2_1"]].copy()
    merged = merged.merge(mu_recent[["iso3", "share_equipment",
                                     "share_structures", "share_ipp"]],
                          on="iso3", how="left")

    rnd_intensity = []
    for _, row in merged.iterrows():
        c = by_iso.get(row["iso3"])
        if c is not None and np.isfinite(c.rnd_share).any():
            vals = c.rnd_share[(c.years >= 2010) & (c.years <= 2019)]
            rnd_intensity.append(float(np.nanmean(vals)))
        else:
            rnd_intensity.append(np.nan)
    merged["rnd_intensity"] = rnd_intensity

    # Drop rows with missing key features
    feature_cols = ["mu_M4", "beta_M4", "mu_M2_1", "rnd_intensity",
                    "share_equipment", "share_ipp"]
    merged = merged.dropna(subset=feature_cols)
    return merged


def _cluster_inertia(Xs: np.ndarray, labels: np.ndarray,
                      centroids: np.ndarray) -> float:
    return float(np.sum((Xs - centroids[labels]) ** 2))


def _bootstrap_stability(Xs: np.ndarray, labels: np.ndarray,
                          n_boot: int = 100, seed: int = 99) -> float:
    """Mean adjusted Rand index between original labels and bootstrapped fits."""
    rng = np.random.default_rng(seed)
    n = len(Xs)
    scores = []
    for b in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        _, lab_boot = kmeans2(Xs[idx], 3, seed=seed + b, minit="++")
        scores.append(adjusted_rand_score(labels[idx], lab_boot))
    return float(np.nanmean(scores))


def run_cluster_analysis(countries: list[Country],
                         fair: pd.DataFrame,
                         mu_df: pd.DataFrame) -> tuple:
    """Create Table 10 and Figure 16: k-means clusters by (mu, beta) + composition.

    Returns (df, centers, metrics, diagnostics).  Metrics and diagnostics
    contain silhouette and bootstrap stability scores used to validate the
    k=3 choice.
    """
    df = load_cluster_features(countries, fair, mu_df)
    if df.empty:
        warnings.warn("Cluster analysis skipped: insufficient feature coverage")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    feature_cols = ["mu_M4", "beta_M4", "mu_M2_1", "rnd_intensity",
                    "share_equipment", "share_ipp"]
    X = df[feature_cols].to_numpy(dtype=float)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)

    # Elbow / silhouette across candidate k (2-6)
    diag = []
    best_sil = -1.0
    chosen_k = 3
    for k in range(2, 7):
        cent, lab = kmeans2(Xs, k, seed=42, minit="++")
        n_unique = len(np.unique(lab))
        sil = silhouette_score(Xs, lab) if n_unique >= 2 and n_unique < len(Xs) else -1.0
        inertia = _cluster_inertia(Xs, lab, cent)
        diag.append({
            "k": k,
            "silhouette": round(float(sil), 3),
            "inertia": round(inertia, 3),
        })
        if sil > best_sil:
            best_sil = sil
            chosen_k = k
    diag_df = pd.DataFrame(diag)

    # Final k=3 fit
    centroids, labels = kmeans2(Xs, 3, seed=42, minit="++")
    df["cluster"] = labels
    sil_overall = silhouette_score(Xs, labels)
    sil_samples = silhouette_samples(Xs, labels)
    df["silhouette_sample"] = np.round(sil_samples, 3)
    boot_arand = _bootstrap_stability(Xs, labels)

    # Cluster centers in original units
    centers = df.groupby("cluster")[feature_cols + ["country"]].agg({
        **{c: "mean" for c in feature_cols},
        "country": lambda x: ", ".join(sorted(x)),
    }).reset_index()
    centers = centers.rename(columns={"country": "members"})
    centers["mean_silhouette"] = (
        df.groupby("cluster")["silhouette_sample"].mean().round(3).values
    )

    final_k = 3  # chosen for interpretability; sweep reported in table10c
    metrics = pd.DataFrame([{
        "k": int(final_k),
        "silhouette_overall": round(float(sil_overall), 3),
        "bootstrap_adjusted_rand": round(float(boot_arand), 3),
    }])

    for lang in ("en", "ja"):
        make_fig16_clusters(df, lang, sil_overall, boot_arand)

    return df, centers, metrics, diag_df


def make_fig16_clusters(df: pd.DataFrame, lang: str = "en",
                        sil_overall: float = np.nan,
                        boot_arand: float = np.nan):
    labels = {
        "en": {
            "title": "Country clusters by joint-identified (mu, beta) and asset composition",
            "xlabel": r"$\hat{\mu}_{\mathrm{joint}}$ (years)",
            "ylabel": r"$\hat{\beta}_{\mathrm{joint}}$",
            "size": "R&D intensity (% GDP)",
            "annotation": f"Silhouette = {sil_overall:.2f}; bootstrap ARAND = {boot_arand:.2f}",
        },
        "ja": {
            "title": "(μ, β) と資産構成による国クラスター",
            "xlabel": r"$\hat{\mu}_{\mathrm{joint}}$（年）",
            "ylabel": r"$\hat{\beta}_{\mathrm{joint}}$",
            "size": "R&D強度（GDP比%）",
            "annotation": f"シルエット = {sil_overall:.2f}; ブートストラップARAND = {boot_arand:.2f}",
        },
    }[lang]

    palette = ["#4c72b0", "#c44e52", "#55a868"]
    fig, ax = plt.subplots(figsize=(9, 7))
    for cl in sorted(df["cluster"].unique()):
        cdf = df[df["cluster"] == cl]
        ax.scatter(cdf["mu_M4"], cdf["beta_M4"],
                   s=np.clip(cdf["rnd_intensity"], 5, 50) * 8,
                   c=palette[cl % len(palette)],
                   label=f"Cluster {cl + 1}", alpha=0.7, edgecolors="black")
        for _, row in cdf.iterrows():
            ax.annotate(row["iso3"], (row["mu_M4"], row["beta_M4"]),
                        fontsize=7, alpha=0.8)
    ax.set_xlabel(labels["xlabel"])
    ax.set_ylabel(labels["ylabel"])
    ax.set_title(labels["title"], fontsize=11)
    ax.legend(title=labels["size"])
    ax.grid(alpha=0.3)
    ax.text(0.02, 0.98, labels["annotation"],
            transform=ax.transAxes, fontsize=8,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))
    plt.tight_layout()
    out = os.path.join(FIG, f"fig16_country_clusters_{lang}.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("wrote", out)


# ---------------------------------------------------------------------------
# A.5  Time-varying depreciation robustness check

DELTA_SCENARIOS = {
    "baseline": lambda c, t, y: c.delta[t],
    "trend_up": lambda c, t, y: c.delta[t] * (1 + 0.10 * (y - c.years[0]) / max(1, c.years[-1] - c.years[0])),
    "trend_down": lambda c, t, y: c.delta[t] * (1 - 0.10 * (y - c.years[0]) / max(1, c.years[-1] - c.years[0])),
    "post2000_high": lambda c, t, y: c.delta[t] * (1.15 if y >= 2000 else 1.0),
    "post2000_low": lambda c, t, y: c.delta[t] * (0.85 if y >= 2000 else 1.0),
    "cyclical": lambda c, t, y: c.delta[t] * (1 + 0.05 * np.sin(2 * np.pi * (y - c.years[0]) / 15.0)),
}


def run_delta_timevarying(countries: list[Country]) -> pd.DataFrame:
    """Create Table 11 and Figure 17: delta(t) robustness."""
    rows = []
    for c in countries:
        alpha = compute_alpha_labsh(c)
        L = c.emp * c.avh
        LH = L * c.hc
        logY = np.log(c.Y)
        logLH = np.log(LH)

        for scen_name, func in DELTA_SCENARIOS.items():
            delta_t = np.array([func(c, t, y) for t, y in enumerate(c.years)],
                               dtype=float)
            delta_t = np.clip(delta_t, 0.01, 0.99)

            mu_m1 = fit_mu_const(c.I, delta_t, c.K0, logY, logLH, alpha)
            mu0_m2, mu1_m2 = fit_tempo(c.I, delta_t, c.K0, logY,
                                       logLH, alpha, c.years)
            K_m2 = pim_lagged_tempo(c.I, delta_t, c.K0, mu0_m2, mu1_m2, c.years)
            K_m2 = np.where(K_m2 > 0, K_m2, 1e-6)
            rmse = test_B_growth(logY, np.log(K_m2), logLH, alpha)

            rows.append({
                "country": c.country,
                "iso3": c.iso,
                "scenario": scen_name,
                "mu_M1": mu_m1,
                "mu0_M2": mu0_m2,
                "mu1_M2": mu1_m2,
                "TestB_M2_rmse_pp": rmse,
            })

    df = pd.DataFrame(rows)
    # Aggregate summary
    summary = (df.groupby("scenario")
               .agg(n_countries=("country", "count"),
                    median_mu_M1=("mu_M1", "median"),
                    mean_mu_M1=("mu_M1", "mean"),
                    median_mu0_M2=("mu0_M2", "median"),
                    median_mu1_M2=("mu1_M2", "median"),
                    median_TestB_M2=("TestB_M2_rmse_pp", "median"))
               .reset_index())
    for col in ["median_mu_M1", "mean_mu_M1", "median_mu0_M2",
                "median_mu1_M2", "median_TestB_M2"]:
        summary[col] = summary[col].round(3)
    return df, summary


def make_fig17_delta(summary: pd.DataFrame, lang: str = "en"):
    labels = {
        "en": {
            "title": "Time-varying depreciation robustness: median estimated lag",
            "ylabel_mu": r"Median $\hat{\mu}$ (M1, years)",
            "ylabel_mu1": r"Median $\hat{\mu}_1$ (M2 drift, years/year)",
            "xlabel": "Depreciation scenario",
        },
        "ja": {
            "title": "時変減価償却率の頑健性：推定ラグの中央値",
            "ylabel_mu": r"中央値 $\hat{\mu}$（M1, 年）",
            "ylabel_mu1": r"中央値 $\hat{\mu}_1$（M2ドリフト, 年/年）",
            "xlabel": "減価償却シナリオ",
        },
    }[lang]

    x = np.arange(len(summary))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(x, summary["median_mu_M1"], color="#4c72b0")
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary["scenario"], rotation=45, ha="right")
    ax1.set_ylabel(labels["ylabel_mu"])
    ax1.set_xlabel(labels["xlabel"])
    ax1.grid(axis="y", alpha=0.3)

    ax2.bar(x, summary["median_mu1_M2"], color="#c44e52")
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary["scenario"], rotation=45, ha="right")
    ax2.set_ylabel(labels["ylabel_mu1"])
    ax2.set_xlabel(labels["xlabel"])
    ax2.grid(axis="y", alpha=0.3)

    fig.suptitle(labels["title"], fontsize=12)
    plt.tight_layout()
    out = os.path.join(FIG, f"fig17_delta_timevarying_{lang}.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("wrote", out)


# ---------------------------------------------------------------------------
# A.6  Monte Carlo identification sharpness


MONTE_CARLO_COUNTRIES = [
    "United States", "Republic of Korea", "France", "Colombia",
]


def fit_joint_fast(I: np.ndarray,
                   delta: np.ndarray,
                   K0: float,
                   K_intan: np.ndarray,
                   logY: np.ndarray,
                   logL: np.ndarray,
                   alpha: float,
                   ki: list,
                   pca: np.ndarray,
                   lambda_w: float = 0.3) -> tuple:
    """Vectorised fit_joint over the beta grid for a fixed (I, delta, K0).

    Mirrors the loss function of run_paper_analyses.fit_joint but computes
    the loss for all beta values simultaneously, which is ~20x faster in the
    Monte Carlo loop.
    """
    mu_grid = np.linspace(0.01, 6.0, 25)
    beta_grid = np.linspace(0.0, 0.34, 18)

    dY = np.diff(logY)
    dL = np.diff(logL)
    K_intan_p = np.where(K_intan > 0, K_intan, 1e-6)
    dI = np.diff(np.log(K_intan_p))

    pca_arr = np.asarray(pca, dtype=float)
    mask_pca = np.isfinite(pca_arr) & (pca_arr > 0)
    log_pca = np.full_like(pca_arr, np.nan, dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        log_pca[mask_pca] = np.log(pca_arr[mask_pca])

    K_intan_aligned = np.array(
        [K_intan_p[ii] if ii is not None else np.nan for ii in ki])
    log_pca_b = log_pca[:, None]
    mask_pca_b = mask_pca[:, None]

    best_score = np.inf
    best = (np.nan, np.nan, np.nan, np.nan)
    for mu in mu_grid:
        K_m = pim_lagged(I, delta, K0, mu)
        K_m_p = np.where(K_m > 0, K_m, 1e-6)
        logK = np.log(K_m_p)
        dK = np.diff(logK)

        pred = (alpha * dK[:, None] +
                beta_grid[None, :] * dI[:, None] +
                (1.0 - alpha - beta_grid[None, :]) * dL[:, None])
        g = np.mean(dY[:, None] - pred, axis=0)
        resid = dY[:, None] - g[None, :] - pred
        L_p = np.mean(resid ** 2, axis=0)

        aligned_m = np.array(
            [K_m_p[ii] if ii is not None else np.nan for ii in ki])
        aligned = aligned_m[:, None] + beta_grid[None, :] * K_intan_aligned[:, None]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lhat = np.log(aligned)

        mask = mask_pca_b & np.isfinite(lhat)
        n_valid = mask.sum(axis=0)
        lhat_mean = np.where(mask, lhat, np.nan)
        lhat_mean = np.nanmean(lhat_mean, axis=0)
        pca_mean = np.where(mask, log_pca_b, np.nan)
        pca_mean = np.nanmean(pca_mean, axis=0)

        d = lhat - lhat_mean - (log_pca_b - pca_mean)
        d = np.where(mask, d, 0.0)
        L_w = np.sum(d ** 2, axis=0) / np.maximum(n_valid, 1)

        invalid = (alpha + beta_grid) >= 0.95
        L_p = np.where(~invalid, L_p, np.inf)
        L_w = np.where((n_valid >= 6) & (~invalid), L_w, np.inf)

        score = L_p + lambda_w * L_w
        idx = int(np.argmin(score))
        if score[idx] < best_score:
            best_score = score[idx]
            best = (float(mu), float(beta_grid[idx]),
                    float(L_p[idx]), float(L_w[idx]))

    return best


def _monte_carlo_country(c: Country, params_row: pd.Series,
                         solow: pd.DataFrame, n_rep: int,
                         rng: np.random.Generator) -> list[dict]:
    """Run the Monte Carlo experiment for one country calibration."""
    alpha = float(params_row["alpha"])

    K_intan_full = build_intan_stock(c.Y, fill_series(c.rnd_share))
    if K_intan_full is None:
        K_intan_full = np.full(len(c.Y), 1e-6)
    K_intan_full = np.where(K_intan_full > 0, K_intan_full, 1e-6)
    logK_intan_full = np.log(K_intan_full)
    logL_full = np.log(c.emp * c.avh)

    cdf = solow[solow["country"] == c.country].sort_values("year")
    tfp_df = cdf.set_index("year")["tfp_M4"]
    tfp_arr = np.array([tfp_df.get(int(y), np.nan) for y in c.years])
    valid = np.isfinite(tfp_arr)
    if valid.sum() >= 2:
        t = c.years[valid] - c.years[valid][0]
        x = np.column_stack([np.ones_like(t), t])
        a_tfp, b_tfp = np.linalg.lstsq(x, tfp_arr[valid], rcond=None)[0][:2]
    else:
        a_tfp, b_tfp = 0.0, 0.0

    mu_truths = [0.5, 1.5, 3.0]
    beta_truths = [0.05, 0.15, 0.30]
    sigmas = [0.01, 0.02, 0.04]
    sample_lengths = [30, 40, 50]

    rows = []
    for T in sample_lengths:
        if T > len(c.years):
            continue
        i0 = len(c.years) - T
        years_slice = c.years[i0:]
        I = c.I[i0:]
        delta = c.delta[i0:]
        logK_intan = logK_intan_full[i0:]
        logL = logL_full[i0:]
        idx_map_slice = {int(y): i for i, y in enumerate(years_slice)}

        for sigma in sigmas:
            for mu_true in mu_truths:
                K_tang_true_full_mu = pim_lagged(c.I, c.delta, c.K0, mu_true)
                K_tang_true = K_tang_true_full_mu[i0:]
                K_tang_true = np.where(K_tang_true > 0, K_tang_true, 1e-6)
                logK_true = np.log(K_tang_true)

                for beta_true in beta_truths:
                    mu_hats = []
                    beta_hats = []
                    w_L = max(1e-6, 1 - alpha - beta_true)

                    for _ in range(n_rep):
                        t_sub = years_slice - years_slice[0]
                        tfp_sim = a_tfp + b_tfp * t_sub + rng.normal(0, sigma, size=T)

                        logY_sim = (alpha * logK_true +
                                    beta_true * logK_intan +
                                    w_L * logL + tfp_sim)

                        mask = ((c.cwon_years >= years_slice[0]) &
                                (c.cwon_years <= years_slice[-1]))
                        cwon_years_sample = c.cwon_years[mask]
                        pca_sim = []
                        ki = []
                        for cy in cwon_years_sample:
                            j = idx_map_slice.get(int(cy))
                            if (j is not None and
                                    K_tang_true[j] > 0 and
                                    K_intan_full[i0 + j] > 0):
                                pca_sim.append(
                                    (K_tang_true[j] +
                                     beta_true * K_intan_full[i0 + j]) *
                                    np.exp(rng.normal(0, 0.02)))
                                ki.append(j)
                            else:
                                pca_sim.append(np.nan)
                                ki.append(None)
                        pca_sim = np.array(pca_sim)

                        if np.isfinite(pca_sim).sum() < 6:
                            continue

                        try:
                            mu_hat, beta_hat, _, _ = fit_joint_fast(
                                I, delta, K_tang_true[0], K_intan_full[i0:],
                                logY_sim, logL, alpha, ki, pca_sim,
                                lambda_w=0.3)
                        except Exception:
                            continue
                        if np.isfinite(mu_hat) and np.isfinite(beta_hat):
                            mu_hats.append(mu_hat)
                            beta_hats.append(beta_hat)

                    if mu_hats:
                        mu_hats = np.array(mu_hats)
                        beta_hats = np.array(beta_hats)
                        n_valid = len(mu_hats)
                        mu_se = float(np.std(mu_hats, ddof=1) / np.sqrt(n_valid)) if n_valid > 1 else np.nan
                        beta_se = float(np.std(beta_hats, ddof=1) / np.sqrt(n_valid)) if n_valid > 1 else np.nan
                        mu_lo, mu_hi = np.nanpercentile(mu_hats, [2.5, 97.5]) if n_valid > 1 else (np.nan, np.nan)
                        beta_lo, beta_hi = np.nanpercentile(beta_hats, [2.5, 97.5]) if n_valid > 1 else (np.nan, np.nan)
                        rows.append({
                            "country": c.country,
                            "T": T,
                            "sigma": sigma,
                            "mu_true": mu_true,
                            "beta_true": beta_true,
                            "n_rep_valid": n_valid,
                            "mu_bias": round(float(np.mean(mu_hats) - mu_true), 3),
                            "mu_se": round(mu_se, 3),
                            "mu_rmse": round(float(np.sqrt(np.mean((mu_hats - mu_true) ** 2))), 3),
                            "mu_ci_lo": round(mu_lo, 3),
                            "mu_ci_hi": round(mu_hi, 3),
                            "beta_bias": round(float(np.mean(beta_hats) - beta_true), 3),
                            "beta_se": round(beta_se, 3),
                            "beta_rmse": round(float(np.sqrt(np.mean((beta_hats - beta_true) ** 2))), 3),
                            "beta_ci_lo": round(beta_lo, 3),
                            "beta_ci_hi": round(beta_hi, 3),
                        })
    return rows


def run_monte_carlo(countries: list[Country],
                    solow: pd.DataFrame,
                    n_rep: int = 100,
                    seed: int = 123) -> pd.DataFrame:
    """Create Table 12 and Figure 18: Monte Carlo joint-identification sharpness.

    Calibrated to four economies (United States, Republic of Korea, France,
    Colombia) to show robustness across parameter regions.
    """
    rng = np.random.default_rng(seed)
    by_country = {c.country: c for c in countries}
    params = solow.groupby("country").first()[["alpha", "mu_j", "beta_j"]]

    all_rows = []
    for country in MONTE_CARLO_COUNTRIES:
        if country not in by_country or country not in params.index:
            continue
        print(f"  Monte Carlo calibration: {country} ...")
        country_rows = _monte_carlo_country(
            by_country[country], params.loc[country], solow, n_rep, rng)
        all_rows.extend(country_rows)

    return pd.DataFrame(all_rows)


def make_fig18_monte_carlo(df: pd.DataFrame, lang: str = "en"):
    labels = {
        "en": {
            "title": ("Monte Carlo identification sharpness "
                      "(United States, Korea, France, Colombia)"),
            "ylabel_mu": r"RMSE of $\hat{\mu}$ (years)",
            "ylabel_beta": r"RMSE of $\hat{\beta}$",
            "xlabel": r"Output noise $\sigma$",
            "note": "No simulation results available.",
            "legend": "T={T}",
        },
        "ja": {
            "title": ("モンテカルロ同定鋭度 "
                      "（米国・韓国・フランス・コロンビア）"),
            "ylabel_mu": r"$\hat{\mu}$ のRMSE（年）",
            "ylabel_beta": r"$\hat{\beta}$ のRMSE",
            "xlabel": r"出力ショックの標準偏差 $\sigma$",
            "note": "シミュレーション結果がありません。",
            "legend": "T={T}",
        },
    }[lang]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), sharex=True)
    if df.empty or "mu_rmse" not in df.columns:
        for ax in (ax1, ax2):
            ax.text(0.5, 0.5, labels["note"], transform=ax.transAxes,
                    ha="center", va="center")
            ax.axis("off")
    else:
        agg = (df.groupby(["T", "sigma"], as_index=False)
                 .agg(mu_rmse=("mu_rmse", "mean"),
                      mu_sd=("mu_rmse", "std"),
                      beta_rmse=("beta_rmse", "mean"),
                      beta_sd=("beta_rmse", "std"),
                      n=("mu_rmse", "count")))
        agg["mu_se"] = 1.96 * agg["mu_sd"] / np.sqrt(agg["n"])
        agg["beta_se"] = 1.96 * agg["beta_sd"] / np.sqrt(agg["n"])

        colors = {30: "#4c72b0", 40: "#c44e52", 50: "#55a868"}
        for T in sorted(agg["T"].unique()):
            sub = agg[agg["T"] == T]
            color = colors.get(T, "black")
            ax1.errorbar(sub["sigma"], sub["mu_rmse"], yerr=sub["mu_se"],
                         fmt="o-", capsize=4, capthick=1.2,
                         label=labels["legend"].format(T=T), color=color)
            ax2.errorbar(sub["sigma"], sub["beta_rmse"], yerr=sub["beta_se"],
                         fmt="o-", capsize=4, capthick=1.2,
                         label=labels["legend"].format(T=T), color=color)
        ax1.set_ylabel(labels["ylabel_mu"])
        ax1.set_xlabel(labels["xlabel"])
        ax1.legend()
        ax1.grid(alpha=0.3)
        ax2.set_ylabel(labels["ylabel_beta"])
        ax2.set_xlabel(labels["xlabel"])
        ax2.legend()
        ax2.grid(alpha=0.3)
    fig.suptitle(labels["title"], fontsize=12)
    plt.tight_layout()
    out = os.path.join(FIG, f"fig18_monte_carlo_{lang}.png")
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print("wrote", out)


# ---------------------------------------------------------------------------
# Main entry point

def run_gamma_price_summary() -> pd.DataFrame | None:
    """Create Table 13: cross-country summary of gamma that closes PIM/CWON gap.

    Uses the wide-format gamma_price.csv output from run_paper_analyses.py.
    For each country, the table reports (i) the gamma at which the fitted
    log(PIM/CWON) line crosses zero, and (ii) whether that crossing lies inside
    the explored [-0.04, 0.04] interval.  If no crossing occurs inside the
    interval, the root is obtained by linear extrapolation and flagged as
    out-of-range.
    """
    path = os.path.join(DATA, "gamma_price.csv")
    if not os.path.exists(path):
        warnings.warn("gamma_price.csv not found; skipping gamma summary")
        return None
    df = pd.read_csv(path)
    gamma_cols = [c for c in df.columns if c.startswith("logratio_g")]
    if not gamma_cols:
        return None
    gammas = sorted([float(c.replace("logratio_g", "").replace("+", "")) for c in gamma_cols])

    rows = []
    for _, row in df.iterrows():
        country = row["country"]
        iso3 = row.get("iso3", "")
        ratios = np.array([float(row[c]) for c in gamma_cols], dtype=float)
        # interpolate/extrapolate zero crossing
        in_range = False
        gamma_zero = np.nan
        if not np.all(np.isfinite(ratios)):
            pass
        elif np.any(np.sign(ratios[:-1]) != np.sign(ratios[1:])):
            idx = np.where(np.sign(ratios[:-1]) != np.sign(ratios[1:]))[0][0]
            x0, x1 = gammas[idx], gammas[idx + 1]
            y0, y1 = ratios[idx], ratios[idx + 1]
            gamma_zero = x0 - y0 * (x1 - x0) / (y1 - y0)
            in_range = -0.04 <= gamma_zero <= 0.04
        else:
            # linear extrapolation through the two extreme explored points
            x = np.array(gammas)
            y = ratios
            coeffs = np.polyfit(x, y, 1)
            if abs(coeffs[0]) > 1e-12:
                gamma_zero = -coeffs[1] / coeffs[0]
            in_range = False

        rows.append({
            "country": country,
            "iso3": iso3,
            "gamma_zero": round(float(gamma_zero), 4) if np.isfinite(gamma_zero) else np.nan,
            "in_range": in_range,
            "min_log_ratio": round(float(np.nanmin(ratios)), 4),
            "max_log_ratio": round(float(np.nanmax(ratios)), 4),
        })
    return pd.DataFrame(rows)


def main():
    print("Loading country panel...")
    countries = prepare_countries()
    print(f"  {len(countries)} countries")

    print("\n--- A.1 Solow-residual historical episodes ---")
    solow = pd.read_csv(os.path.join(DATA, "solow_decomposition.csv"))
    table7 = run_solow_narrative(solow)
    table7.to_csv(os.path.join(TAB, "table7_solow_episodes.csv"), index=False)
    table7_loo = run_solow_narrative_loo(solow)
    table7_loo.to_csv(os.path.join(TAB, "table7b_narrative_loo.csv"), index=False)
    print(f"  wrote table7 ({len(table7)} episodes) and table7b ({len(table7_loo)} leave-one-out)")

    print("\n--- A.2 Counterfactual-wealth narrative ---")
    cf = pd.read_csv(os.path.join(DATA, "counterfactual_wealth.csv"))
    table8 = run_counterfactual_narrative(cf)
    table8.to_csv(os.path.join(TAB, "table8_counterfactual_narrative.csv"), index=False)
    print(f"  wrote table8 ({len(table8)} countries)")

    print("\n--- A.3 Future forecast simulation ---")
    table9, detail = run_future_scenarios(countries, solow)
    table9.to_csv(os.path.join(TAB, "table9_future_scenarios.csv"), index=False)
    detail.to_csv(os.path.join(DATA, "future_scenarios_detail.csv"), index=False)
    for lang in ("en", "ja"):
        make_fig15_future(detail, lang)
    print(f"  wrote table9 and fig15 ({len(table9)} countries)")

    print("\n--- A.4 Cross-country cluster analysis ---")
    fair = pd.read_csv(os.path.join(DATA, "fair_eval.csv"))
    mu_df = pd.read_csv(os.path.join(DATA, "observable_mu.csv"))
    cluster_df, table10, table10_metrics, table10_diag = run_cluster_analysis(countries, fair, mu_df)
    if not cluster_df.empty:
        cluster_df.to_csv(os.path.join(DATA, "cluster_analysis.csv"), index=False)
        table10.to_csv(os.path.join(TAB, "table10_cluster_analysis.csv"), index=False)
        table10_metrics.to_csv(os.path.join(TAB, "table10b_cluster_metrics.csv"), index=False)
        table10_diag.to_csv(os.path.join(TAB, "table10c_cluster_diagnostics.csv"), index=False)
        print(f"  wrote table10/10b/10c and fig16 ({len(cluster_df)} countries, 3 clusters)")
    else:
        print("  skipped (missing features)")

    print("\n--- A.5 Time-varying depreciation robustness ---")
    delta_detail, table11 = run_delta_timevarying(countries)
    delta_detail.to_csv(os.path.join(DATA, "delta_timevarying_detail.csv"), index=False)
    table11.to_csv(os.path.join(TAB, "table11_delta_timevarying.csv"), index=False)
    for lang in ("en", "ja"):
        make_fig17_delta(table11, lang)
    print(f"  wrote table11 and fig17 ({len(table11)} scenarios)")

    print("\n--- A.6 Monte Carlo identification sharpness ---")
    table12 = run_monte_carlo(countries, solow, n_rep=100)
    table12.to_csv(os.path.join(TAB, "table12_monte_carlo.csv"), index=False)
    for lang in ("en", "ja"):
        make_fig18_monte_carlo(table12, lang)
    print(f"  wrote table12 and fig18 ({len(table12)} cells)")

    print("\n--- A.7 Gamma-price cross-country summary ---")
    table14 = run_gamma_price_summary()
    if table14 is not None:
        table14.to_csv(os.path.join(TAB, "table14_gamma_price_summary.csv"), index=False)
        print(f"  wrote table14 ({len(table14)} countries)")
    else:
        print("  skipped (gamma_price.csv missing)")

    print("\nDone.")


if __name__ == "__main__":
    main()
