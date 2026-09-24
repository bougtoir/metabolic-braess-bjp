#!/usr/bin/env python3
"""
KOTHA Framework Validation with Real Published Data
=====================================================
Case 1: Intravenous Magnesium in Acute Myocardial Infarction
Case 2: Statins in Heart Failure

This script implements Modules K, T, and H using real study-level data
from published meta-analyses and generates all color figures.
"""

import os

import numpy as np
import pandas as pd
import emcee
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from scipy import stats
from scipy.special import expit, logit
import warnings
warnings.filterwarnings('ignore')

from simulation_study import (
    run_simulation_study,
    plot_simulation_results,
    save_simulation_summary,
)

# ============================================================
# Color palette (colorblind-friendly, Okabe-Ito)
# ============================================================
C_BLUE = '#0072B2'
C_ORANGE = '#E69F00'
C_GREEN = '#009E73'
C_RED = '#D55E00'
C_PURPLE = '#CC79A7'
C_CYAN = '#56B4E9'
C_YELLOW = '#F0E442'
C_GREY = '#999999'

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), 'data')
OUTDIR = os.path.join(BASE_DIR, 'figures')

os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# CASE 1: Intravenous Magnesium in Acute Myocardial Infarction
# ============================================================
# Data sources documented in data/SOURCES.md

mg_data = pd.read_csv(os.path.join(DATA_DIR, 'magnesium_ami.csv'))

# ============================================================
# CASE 2: Statins in Heart Failure
# ============================================================
# Observational data from published cohort studies
# RCT data from CORONA and GISSI-HF

def _load_statin_hr(path, design):
    df = pd.read_csv(path)
    df['logHR'] = np.log(df['HR'])
    df['logHR_lo'] = np.log(df['HR_lo'])
    df['logHR_hi'] = np.log(df['HR_hi'])
    df['se'] = (df['logHR_hi'] - df['logHR_lo']) / (2 * 1.96)
    df['design'] = design
    return df

statin_obs = _load_statin_hr(os.path.join(DATA_DIR, 'statins_hf_obs.csv'), 'OBS')
statin_rct = _load_statin_hr(os.path.join(DATA_DIR, 'statins_hf_rct.csv'), 'RCT')


# ============================================================
# Helper functions
# ============================================================

def compute_or(e_t, n_t, e_c, n_c, cc=0.5):
    """Compute log-OR and SE with continuity correction."""
    a = e_t + cc
    b = (n_t - e_t) + cc
    c = e_c + cc
    d = (n_c - e_c) + cc
    logOR = np.log(a * d / (b * c))
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return logOR, se


def fixed_effect_meta(logOR, se):
    """Inverse-variance fixed-effect meta-analysis."""
    w = 1 / se**2
    pooled = np.sum(w * logOR) / np.sum(w)
    se_pooled = 1 / np.sqrt(np.sum(w))
    return pooled, se_pooled


def random_effects_meta(logOR, se):
    """DerSimonian-Laird random-effects meta-analysis."""
    w = 1 / se**2
    Q = np.sum(w * (logOR - np.sum(w * logOR) / np.sum(w))**2)
    k = len(logOR)
    C = np.sum(w) - np.sum(w**2) / np.sum(w)
    tau2 = max(0, (Q - (k - 1)) / C)
    w_re = 1 / (se**2 + tau2)
    pooled = np.sum(w_re * logOR) / np.sum(w_re)
    se_pooled = 1 / np.sqrt(np.sum(w_re))
    I2 = max(0, (Q - (k - 1)) / Q * 100) if Q > 0 else 0
    return pooled, se_pooled, tau2, I2


def power_for_event_rate(p_control, OR, n_total, alpha=0.05, n_sim=10000):
    """
    Monte Carlo power simulation for a two-arm trial with binary outcome.
    p_control: control event rate
    OR: true odds ratio (treatment vs control)
    n_total: total sample size
    alpha: significance level (two-sided)
    """
    n_arm = n_total // 2
    p_treat = (p_control * OR) / (1 - p_control + p_control * OR)
    
    reject = 0
    for _ in range(n_sim):
        x_c = np.random.binomial(n_arm, p_control)
        x_t = np.random.binomial(n_arm, p_treat)
        # Fisher exact test approximation via chi-square
        table = np.array([[x_t, n_arm - x_t], [x_c, n_arm - x_c]])
        if table.min() >= 0:
            try:
                chi2, p_val, _, _ = stats.chi2_contingency(table, correction=True)
                if p_val < alpha:
                    reject += 1
            except:
                pass
    return reject / n_sim


def power_analytical(p_control, OR, n_total, alpha=0.05):
    """
    Analytical power calculation for log-rank/chi-square test.
    Uses the formula: power = Phi(|z_effect| - z_{alpha/2})
    where z_effect = log(OR) * sqrt(n_total * p_control * (1-p_control) / 4)
    """
    p_treat = (p_control * OR) / (1 - p_control + p_control * OR)
    # Number of events expected
    n_arm = n_total // 2
    e_ctrl = n_arm * p_control
    e_treat = n_arm * p_treat
    total_events = e_ctrl + e_treat
    
    # Schoenfeld formula for log-rank: power based on number of events
    z_alpha = stats.norm.ppf(1 - alpha/2)
    logOR = np.log(OR)
    # SE of log(OR) ~ 2/sqrt(D) where D is total events
    se_logOR = 2 / np.sqrt(total_events) if total_events > 0 else np.inf
    z_effect = abs(logOR) / se_logOR
    power = stats.norm.cdf(z_effect - z_alpha)
    return power, total_events


def ois_calculation(OR, alpha=0.05, power=0.80):
    """
    Calculate Optimal Information Size (required number of events).
    D = 4 * (z_{alpha/2} + z_{beta})^2 / (log(OR))^2
    """
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    logOR = np.log(OR)
    D = 4 * (z_alpha + z_beta)**2 / logOR**2
    return D


def kotha_assessment(info_fraction, final_z, ci_lo, ci_hi, rate_ratio, i2,
                     i2_threshold=50.0,
                     indirect_moderate_low=0.80, indirect_moderate_high=1.25,
                     indirect_serious_low=0.67, indirect_serious_high=1.50):
    """
    Derive a KOTHA-enhanced GRADE classification by integrating the five
    Module H assessments: information sufficiency, CI interpretation,
    representativeness (event-rate ratio), TSA boundary status, and
    inconsistency (I^2).

    Returns a dict with keys:
      - classification: short label for the result section
      - recommendation: short recommendation phrase
      - rationale: one-sentence justification
      - indirectness: 'low' / 'moderate' / 'serious'
      - inconsistency: bool (I^2 > i2_threshold)
    """
    z_alpha = stats.norm.ppf(0.975)
    # O'Brien-Fleming boundary at the current information fraction. When the
    # accumulated information is at or beyond the optimal information size, the
    # boundary has reached the conventional two-sided alpha threshold.
    if info_fraction <= 0:
        obf_boundary = np.inf
    elif info_fraction < 1:
        obf_boundary = z_alpha / np.sqrt(info_fraction)
    else:
        obf_boundary = z_alpha

    ci_crosses_null = (ci_lo < 1.0) and (ci_hi > 1.0)
    sig_benefit = (ci_hi < 1.0) or (final_z < -obf_boundary)
    sig_harm = (ci_lo > 1.0) or (final_z > obf_boundary)

    if rate_ratio < indirect_serious_low or rate_ratio > indirect_serious_high:
        indirectness = "serious"
    elif rate_ratio < indirect_moderate_low or rate_ratio > indirect_moderate_high:
        indirectness = "moderate"
    else:
        indirectness = "low"

    inconsistency = i2 > i2_threshold

    if info_fraction < 1.0:
        return {
            'classification': "No evidence of effect (informationally insufficient)",
            'recommendation': "No evidence of effect",
            'rationale': "OIS not reached; meta-analysis is analogous to an interim analysis",
            'indirectness': indirectness,
            'inconsistency': inconsistency,
        }

    if not sig_benefit and not sig_harm:
        if indirectness == "serious":
            classification = "Inconclusive with serious indirectness"
            recommendation = "Inconclusive; conditional recommendation"
            rationale = "OIS reached but no TSA/CI boundary crossed; serious indirectness from enrollment-driven event dilution"
        elif indirectness == "moderate":
            classification = "Inconclusive with moderate indirectness"
            recommendation = "Inconclusive; conditional recommendation"
            rationale = "OIS reached but no TSA/CI boundary crossed; moderate indirectness"
        else:
            classification = "Inconclusive"
            recommendation = "Inconclusive; conditional recommendation"
            rationale = "OIS reached but no TSA/CI boundary crossed"
        return {
            'classification': classification,
            'recommendation': recommendation,
            'rationale': rationale,
            'indirectness': indirectness,
            'inconsistency': inconsistency,
        }

    if sig_benefit:
        downgrade = []
        if inconsistency:
            downgrade.append("serious inconsistency (heterogeneity)")
        if indirectness == "serious":
            downgrade.append("serious indirectness")
        elif indirectness == "moderate":
            downgrade.append("moderate indirectness")
        if downgrade:
            classification = "Inconclusive with " + " and ".join(downgrade)
            recommendation = "Inconclusive; conditional recommendation"
            rationale = "TSA/CI indicate benefit but the signal is downgraded by " + " and ".join(downgrade)
        else:
            classification = "Evidence of effect"
            recommendation = "Evidence of effect; strong recommendation"
            rationale = "TSA/CI consistently indicate benefit with low risk of bias"
        return {
            'classification': classification,
            'recommendation': recommendation,
            'rationale': rationale,
            'indirectness': indirectness,
            'inconsistency': inconsistency,
        }

    if sig_harm:
        return {
            'classification': "Evidence of harm / no benefit",
            'recommendation': "Evidence of no benefit",
            'rationale': "TSA/CI indicate harm or no benefit",
            'indirectness': indirectness,
            'inconsistency': inconsistency,
        }

    # Fallback
    return {
        'classification': "Inconclusive",
        'recommendation': "Inconclusive; conditional recommendation",
        'rationale': "OIS reached but no clear TSA/CI signal",
        'indirectness': indirectness,
        'inconsistency': inconsistency,
    }


def cumulative_z(logOR_arr, se_arr):
    """Compute cumulative Z-statistic for TSA under a fixed-effect model."""
    z_values = []
    pooled_list = []
    info_list = []
    for k in range(1, len(logOR_arr) + 1):
        w = 1 / se_arr[:k]**2
        pooled = np.sum(w * logOR_arr[:k]) / np.sum(w)
        se_pooled = 1 / np.sqrt(np.sum(w))
        z = pooled / se_pooled
        z_values.append(z)
        pooled_list.append(pooled)
        info_list.append(np.sum(w))
    return np.array(z_values), np.array(pooled_list), np.array(info_list)


def cumulative_random_effects_z(logOR_arr, se_arr):
    """Compute cumulative Z-statistic for TSA under a random-effects model."""
    z_values = []
    pooled_list = []
    info_list = []
    for k in range(1, len(logOR_arr) + 1):
        if k == 1:
            pooled = logOR_arr[0]
            se_pooled = se_arr[0]
        else:
            pooled, se_pooled, _, _ = random_effects_meta(logOR_arr[:k], se_arr[:k])
        z = pooled / se_pooled
        z_values.append(z)
        pooled_list.append(pooled)
        info_list.append(1 / se_pooled**2)
    return np.array(z_values), np.array(pooled_list), np.array(info_list)


# ============================================================
# MODULE K: Counterfactual Power Simulation
# ============================================================

def run_module_k_magnesium(mg_data):
    """Apply Module K to the magnesium in AMI data."""
    print("=" * 60)
    print("MODULE K: Counterfactual Power Simulation (Magnesium in AMI)")
    print("=" * 60)
    
    # Compute OR and SE for each study
    logORs, SEs, ctrl_rates = [], [], []
    for _, row in mg_data.iterrows():
        lo, se = compute_or(row['e_treat'], row['n_treat'], row['e_ctrl'], row['n_ctrl'])
        logORs.append(lo)
        SEs.append(se)
        ctrl_rates.append(row['e_ctrl'] / row['n_ctrl'])
    
    mg_data['logOR'] = logORs
    mg_data['se'] = SEs
    mg_data['ctrl_rate'] = ctrl_rates
    mg_data['OR'] = np.exp(mg_data['logOR'])
    
    # Scenario definitions based on control-group event rates
    # S1: Pre-thrombolysis era (high event rate, ~10-25%)
    pre_thrombolysis = mg_data[mg_data['era'] == 'pre-thrombolysis']
    # S2: Thrombolysis era (low event rate, ~7-10%)
    thrombolysis_era = mg_data[mg_data['era'].isin(['thrombolysis'])]
    
    # Weighted mean control rates
    pre_n = pre_thrombolysis['n_ctrl'].sum()
    pre_events = pre_thrombolysis['e_ctrl'].sum()
    s1_rate = pre_events / pre_n  # high-risk scenario
    
    isis4 = mg_data[mg_data['study'] == 'ISIS-4 1995'].iloc[0]
    s2_rate = isis4['e_ctrl'] / isis4['n_ctrl']  # ISIS-4 rate
    
    # LIMIT-2 era rate
    limit2 = mg_data[mg_data['study'] == 'LIMIT-2 1992'].iloc[0]
    s3_rate = limit2['e_ctrl'] / limit2['n_ctrl']  # moderate enrichment
    
    print(f"\nScenario S1 (pre-thrombolysis population): control event rate = {s1_rate:.3f}")
    print(f"Scenario S2 (ISIS-4 / thrombolysis era):    control event rate = {s2_rate:.3f}")
    print(f"Scenario S3 (LIMIT-2 / moderate):           control event rate = {s3_rate:.3f}")
    print(f"Event rate ratio S2/S1 = {s2_rate/s1_rate:.2f}")
    
    # Meta-analysis of pre-ISIS-4 trials
    pre_isis = mg_data[mg_data['study'] != 'ISIS-4 1995']
    pooled_pre, se_pre, tau2_pre, I2_pre = random_effects_meta(
        pre_isis['logOR'].values, pre_isis['se'].values
    )
    print(f"\nPre-ISIS-4 meta-analysis (RE): OR = {np.exp(pooled_pre):.2f} "
          f"(95% CI: {np.exp(pooled_pre - 1.96*se_pre):.2f}-{np.exp(pooled_pre + 1.96*se_pre):.2f}), I^2={I2_pre:.0f}%")
    
    # All-trials meta-analysis
    pooled_all, se_all, tau2_all, I2_all = random_effects_meta(
        mg_data['logOR'].values, mg_data['se'].values
    )
    print(f"All-trials meta-analysis (RE):   OR = {np.exp(pooled_all):.2f} "
          f"(95% CI: {np.exp(pooled_all - 1.96*se_all):.2f}-{np.exp(pooled_all + 1.96*se_all):.2f}), I^2={I2_all:.0f}%")
    
    # Power analysis across scenarios
    # True effect: use pre-ISIS-4 pooled OR as the "real" effect
    true_OR = np.exp(pooled_pre)
    N_isis4 = isis4['n_treat'] + isis4['n_ctrl']
    
    OR_grid = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
    
    print(f"\n{'True OR':<10} {'S1 Power':>10} {'S2 Power':>10} {'S3 Power':>10}")
    print("-" * 45)
    
    power_results = {'OR': [], 'S1': [], 'S2': [], 'S3': []}
    for OR in OR_grid:
        p1, e1 = power_analytical(s1_rate, OR, N_isis4)
        p2, e2 = power_analytical(s2_rate, OR, N_isis4)
        p3, e3 = power_analytical(s3_rate, OR, N_isis4)
        power_results['OR'].append(OR)
        power_results['S1'].append(p1)
        power_results['S2'].append(p2)
        power_results['S3'].append(p3)
        print(f"{OR:<10.2f} {p1:>10.1%} {p2:>10.1%} {p3:>10.1%}")
    
    # At the pre-ISIS4 pooled effect
    p1_true, e1_true = power_analytical(s1_rate, true_OR, N_isis4)
    p2_true, e2_true = power_analytical(s2_rate, true_OR, N_isis4)
    p3_true, e3_true = power_analytical(s3_rate, true_OR, N_isis4)
    
    print(f"\nAt pre-ISIS-4 pooled OR = {true_OR:.2f}:")
    print(f"  S1 (pre-thrombolysis rate {s1_rate:.1%}): power = {p1_true:.1%}, expected events = {e1_true:.0f}")
    print(f"  S2 (ISIS-4 rate {s2_rate:.1%}):           power = {p2_true:.1%}, expected events = {e2_true:.0f}")
    print(f"  S3 (LIMIT-2 rate {s3_rate:.1%}):          power = {p3_true:.1%}, expected events = {e3_true:.0f}")
    
    # Required N for 80% power
    for target_power in [0.80]:
        for label, rate in [('S1', s1_rate), ('S2', s2_rate), ('S3', s3_rate)]:
            for N in range(1000, 200000, 500):
                p, _ = power_analytical(rate, true_OR, N)
                if p >= target_power:
                    print(f"  Required N for {target_power:.0%} power at OR={true_OR:.2f}, {label}: N = {N:,}")
                    break
    
    return {
        'mg_data': mg_data,
        's1_rate': s1_rate, 's2_rate': s2_rate, 's3_rate': s3_rate,
        'true_OR': true_OR, 'N_isis4': N_isis4,
        'power_results': power_results,
        'pooled_pre': pooled_pre, 'se_pre': se_pre,
        'pooled_all': pooled_all, 'se_all': se_all,
        'I2_pre': I2_pre, 'I2_all': I2_all,
    }


def run_module_k_statins(statin_obs, statin_rct):
    """Apply Module K to statins in HF data."""
    print("\n" + "=" * 60)
    print("MODULE K: Counterfactual Power Simulation (Statins in HF)")
    print("=" * 60)
    
    # Observational pooled effect
    pooled_obs, se_obs, tau2_obs, I2_obs = random_effects_meta(
        statin_obs['logHR'].values, statin_obs['se'].values
    )
    print(f"Observational meta-analysis (RE): HR = {np.exp(pooled_obs):.2f} "
          f"(95% CI: {np.exp(pooled_obs - 1.96*se_obs):.2f}-{np.exp(pooled_obs + 1.96*se_obs):.2f}), I^2={I2_obs:.0f}%")
    
    # RCT pooled effect
    pooled_rct, se_rct, tau2_rct, I2_rct = random_effects_meta(
        statin_rct['logHR'].values, statin_rct['se'].values
    )
    print(f"RCT meta-analysis (RE):           HR = {np.exp(pooled_rct):.2f} "
          f"(95% CI: {np.exp(pooled_rct - 1.96*se_rct):.2f}-{np.exp(pooled_rct + 1.96*se_rct):.2f}), I^2={I2_rct:.0f}%")
    
    # Event rates
    # Control-group event probabilities are derived directly from the aggregate
    # event counts and sample sizes in the public data files. Because person-time
    # is not available from published aggregate reports, these are crude event
    # proportions (not annual mortality rates) and are used as approximate
    # event probabilities for the power illustration.
    obs_rate = statin_obs['events'].sum() / statin_obs['N'].sum()
    rct_rate = statin_rct['events'].sum() / statin_rct['N'].sum()
    # S3 is a hypothetical enrichment target set at the midpoint between the
    # observed observational and RCT crude proportions. It represents a design
    # that halves the risk-profile gap between the enrolled RCT population and
    # the real-world population.
    enriched_rate = (obs_rate + rct_rate) / 2.0

    print(f"\nEvent rate comparison:")
    print(f"  S1 (observational cohorts): ~{obs_rate:.1%} (crude event proportion)")
    print(f"  S2 (RCT-enrolled):          ~{rct_rate:.1%} (crude event proportion)")
    print(f"  S3 (enriched):              ~{enriched_rate:.1%} (midpoint of S1 and S2)")
    print(f"  Event rate ratio S2/S1 = {rct_rate/obs_rate:.2f}")
    
    # Combined RCT N
    N_rct = statin_rct['N'].sum()
    true_HR = np.exp(pooled_obs)
    
    # Power analysis (using OR approximation for low event rates)
    OR_grid = np.arange(0.50, 1.01, 0.05)
    power_results = {'OR': [], 'S1': [], 'S2': [], 'S3': []}
    
    print(f"\n{'True HR':<10} {'S1 Power':>10} {'S2 Power':>10} {'S3 Power':>10}")
    print("-" * 45)
    
    for OR in OR_grid:
        p1, _ = power_analytical(obs_rate, OR, N_rct)
        p2, _ = power_analytical(rct_rate, OR, N_rct)
        p3, _ = power_analytical(enriched_rate, OR, N_rct)
        power_results['OR'].append(OR)
        power_results['S1'].append(p1)
        power_results['S2'].append(p2)
        power_results['S3'].append(p3)
        print(f"{OR:<10.2f} {p1:>10.1%} {p2:>10.1%} {p3:>10.1%}")

    p1_true, _ = power_analytical(obs_rate, true_HR, N_rct)
    p2_true, _ = power_analytical(rct_rate, true_HR, N_rct)
    p3_true, _ = power_analytical(enriched_rate, true_HR, N_rct)

    print(f"\nAt observational pooled HR = {true_HR:.2f}:")
    print(f"  S1 (obs rate {obs_rate:.0%}): power = {p1_true:.1%}")
    print(f"  S2 (RCT rate {rct_rate:.0%}): power = {p2_true:.1%}")
    print(f"  S3 (enriched rate {enriched_rate:.0%}): power = {p3_true:.1%}")

    return {
        'pooled_obs': pooled_obs, 'se_obs': se_obs, 'I2_obs': I2_obs,
        'pooled_rct': pooled_rct, 'se_rct': se_rct, 'I2_rct': I2_rct,
        'power_results': power_results,
        'true_HR': true_HR, 'N_rct': N_rct,
        'obs_rate': obs_rate, 'rct_rate': rct_rate, 's3_rate': enriched_rate,
    }


# ============================================================
# MODULE T: Bayesian Hierarchical Meta-Analysis (MCMC)
# ============================================================

# bayesian_meta_analysis removed - too slow with per-study random effects.
# Use power_prior_meta (fast 2-parameter MCMC) and bias_adjusted_normal instead.

def bias_adjusted_normal(logY_rct, se_rct, logY_obs, se_obs, delta_grid):
    """Analytical normal approximation for bias-adjusted integration."""
    results = {}
    for delta in delta_grid:
        logY_adj = logY_obs + delta
        logY_all = np.concatenate([logY_rct, logY_adj])
        se_all = np.concatenate([se_rct, se_obs])
        pooled, se_p, tau2, I2 = random_effects_meta(logY_all, se_all)
        hr = np.exp(pooled)
        ci_lo = np.exp(pooled - 1.96 * se_p)
        ci_hi = np.exp(pooled + 1.96 * se_p)
        p_benefit = float(stats.norm.cdf(0, loc=pooled, scale=se_p))
        results[delta] = {'hr': hr, 'ci_lo': ci_lo, 'ci_hi': ci_hi,
                          'p_benefit': p_benefit, 'pooled': pooled, 'se': se_p}
    return results


def _split_rhat(chains):
    """Split-R-hat (Gelman-Rubin) for chains of shape (n_chains, n_draws, n_vars)."""
    chains = np.asarray(chains)
    if chains.ndim == 2:
        chains = chains[..., None]
    n, L, d = chains.shape
    half = L // 2
    if half == 0:
        return np.full(d, np.nan)
    split = np.concatenate([chains[:, :half], chains[:, half:2*half]], axis=0)
    theta_mean = split.mean(axis=1)
    theta_var = split.var(axis=1, ddof=1)
    B = half * theta_mean.var(axis=0, ddof=1)
    W = theta_var.mean(axis=0)
    V = (half - 1) / half * W + B / half
    rhat = np.sqrt(V / W)
    return rhat


def _ess_ise(x, max_lag=None):
    """Geyer initial sequence estimator for one chain."""
    x = np.asarray(x)
    n = len(x)
    if n < 4:
        return float(n)
    x = x - x.mean()
    # autocovariances via FFT
    f = np.fft.fft(x, n=2*n)
    ac = np.fft.ifft(f * f.conjugate()).real[:n]
    ac = ac / (np.arange(n, 0, -1) * np.var(x, ddof=1) + 1e-12)
    G = 0.0
    for t in range(0, n - 1, 2):
        if t + 1 >= n:
            break
        g = ac[t] + ac[t + 1]
        if g < 0:
            break
        G += g
    ess = n / (1.0 + 2.0 * G)
    return max(1.0, ess)


def _ess_mcmc(chains):
    """Sum ESS across independent chains."""
    chains = np.asarray(chains)
    if chains.ndim == 2:
        chains = chains[..., None]
    n, L, d = chains.shape
    ess = np.zeros(d)
    for i in range(n):
        for j in range(d):
            ess[j] += _ess_ise(chains[i, :, j])
    return ess


def power_prior_meta(logY_rct, se_rct, logY_obs, se_obs, alpha_grid, n_iter=4000, n_warmup=1000, n_walkers=16, seed=42):
    """
    Power prior meta-analysis: discount observational likelihood by alpha.
    Uses an ensemble affine-invariant MCMC sampler for robust convergence.
    """
    results = {}
    rng = np.random.default_rng(seed)

    for i, alpha in enumerate(alpha_grid):
        def log_prob(theta):
            mu, log_tau = theta
            if not np.isfinite(log_tau):
                return -np.inf
            tau = np.exp(log_tau)
            if tau <= 1e-9 or tau > 100.0:
                return -np.inf
            var_rct = se_rct**2 + tau**2
            ll_rct = np.sum(stats.norm.logpdf(logY_rct, loc=mu, scale=np.sqrt(var_rct)))
            var_obs = se_obs**2 + tau**2
            ll_obs = alpha * np.sum(stats.norm.logpdf(logY_obs, loc=mu, scale=np.sqrt(var_obs)))
            lp_mu = stats.norm.logpdf(mu, 0, 10)
            # Jacobian for tau = exp(log_tau)
            lp_tau = stats.halfcauchy.logpdf(tau, scale=0.5) + log_tau
            return ll_rct + ll_obs + lp_mu + lp_tau

        # initial walkers around a small ball near tau ~ 0.1
        p0 = rng.normal([0.0, -2.3], 0.15, size=(n_walkers, 2))
        sampler = emcee.EnsembleSampler(n_walkers, 2, log_prob)
        # seed emcee's internal RandomState for reproducibility
        sampler.random_state = np.random.RandomState(seed + i).get_state()
        sampler.run_mcmc(p0, n_warmup + n_iter, progress=False)
        chain = sampler.get_chain(discard=n_warmup, thin=1)  # (n_iter, n_walkers, 2)
        chain = chain.transpose(1, 0, 2)  # (n_walkers, n_iter, 2)

        mu_samples = chain[:, :, 0].reshape(-1)
        hr_arr = np.exp(mu_samples)

        rhat = _split_rhat(chain)
        ess = _ess_mcmc(chain)

        results[alpha] = {
            'hr_median': float(np.median(hr_arr)),
            'hr_lo': float(np.percentile(hr_arr, 2.5)),
            'hr_hi': float(np.percentile(hr_arr, 97.5)),
            'p_benefit': float(np.mean(hr_arr < 1.0)),
            'p_lt_090': float(np.mean(hr_arr < 0.90)),
            'p_lt_080': float(np.mean(hr_arr < 0.80)),
            'samples': mu_samples,
            'rhat_mu': float(rhat[0]),
            'rhat_log_tau': float(rhat[1]),
            'ess_mu': float(ess[0]),
            'ess_log_tau': float(ess[1]),
            'chain': chain,
        }

    return results


def run_module_t_magnesium(mg_data):
    """Apply Module T to the magnesium data."""
    print("\n" + "=" * 60)
    print("MODULE T: Bayesian Evidence Integration (Magnesium in AMI)")
    print("=" * 60)
    
    # For magnesium: all studies are RCTs, but we can treat
    # pre-thrombolysis vs thrombolysis-era as different "designs"
    # OR: treat pre-ISIS-4 as "informative prior" and ISIS-4 as "new RCT"
    
    # Approach: Power prior - discount the small trials by alpha
    # and see how much weight the pre-ISIS-4 evidence should get
    
    pre_isis = mg_data[mg_data['study'] != 'ISIS-4 1995']
    isis4 = mg_data[mg_data['study'] == 'ISIS-4 1995']
    
    alpha_grid = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    
    results = power_prior_meta(
        isis4['logOR'].values, isis4['se'].values,
        pre_isis['logOR'].values, pre_isis['se'].values,
        alpha_grid
    )
    
    print(f"\n{'Alpha':<8} {'OR (95% CrI)':<25} {'P(OR<1)':>10} {'P(OR<0.90)':>12}")
    print("-" * 60)
    for alpha in alpha_grid:
        r = results[alpha]
        print(f"{alpha:<8.1f} {r['hr_median']:.2f} ({r['hr_lo']:.2f}-{r['hr_hi']:.2f})"
              f"{'':>5} {r['p_benefit']:>10.1%} {r['p_lt_090']:>12.1%}")
    
    # Bias-adjusted normal approximation
    ba = bias_adjusted_normal(
        isis4['logOR'].values, isis4['se'].values,
        pre_isis['logOR'].values, pre_isis['se'].values,
        [0.0, 0.1, 0.2, 0.3]
    )
    print("\nBias-adjusted (normal approx):")
    for d, r in ba.items():
        print(f"  delta={d:.1f}: HR={r['hr']:.2f} ({r['ci_lo']:.2f}-{r['ci_hi']:.2f}), P(HR<1)={r['p_benefit']:.1%}")
    
    return {'power_prior': results, 'bias_adj': ba}


def run_module_t_statins(statin_obs, statin_rct):
    """Apply Module T to statins in HF data."""
    print("\n" + "=" * 60)
    print("MODULE T: Bayesian Evidence Integration (Statins in HF)")
    print("=" * 60)
    
    alpha_grid = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    
    results = power_prior_meta(
        statin_rct['logHR'].values, statin_rct['se'].values,
        statin_obs['logHR'].values, statin_obs['se'].values,
        alpha_grid
    )
    
    print(f"\n{'Alpha':<8} {'HR (95% CrI)':<25} {'P(HR<1)':>10} {'P(HR<0.90)':>12}")
    print("-" * 60)
    for alpha in alpha_grid:
        r = results[alpha]
        print(f"{alpha:<8.1f} {r['hr_median']:.2f} ({r['hr_lo']:.2f}-{r['hr_hi']:.2f})"
              f"{'':>5} {r['p_benefit']:>10.1%} {r['p_lt_090']:>12.1%}")
    
    # Bias-adjusted normal approximation
    ba = bias_adjusted_normal(
        statin_rct['logHR'].values, statin_rct['se'].values,
        statin_obs['logHR'].values, statin_obs['se'].values,
        [0.0, 0.1, 0.2, 0.3]
    )
    print("\nBias-adjusted (normal approx):")
    for d, r in ba.items():
        print(f"  delta={d:.1f}: HR={r['hr']:.2f} ({r['ci_lo']:.2f}-{r['ci_hi']:.2f}), P(HR<1)={r['p_benefit']:.1%}")
    
    return {'power_prior': results, 'bias_adj': ba}


# ============================================================
# MODULE H: OIS / TSA Assessment
# ============================================================

def run_module_h_magnesium(mg_data, mk_results):
    """Apply Module H to the magnesium data."""
    print("\n" + "=" * 60)
    print("MODULE H: Guideline Interpretation (Magnesium in AMI)")
    print("=" * 60)
    
    # Assessment 1: Information sufficiency
    true_OR = mk_results['true_OR']
    ois = ois_calculation(true_OR)
    total_events = mg_data['e_treat'].sum() + mg_data['e_ctrl'].sum()
    total_events_pre = mg_data[mg_data['study'] != 'ISIS-4 1995']['e_treat'].sum() + \
                       mg_data[mg_data['study'] != 'ISIS-4 1995']['e_ctrl'].sum()
    info_fraction = total_events / ois
    info_fraction_pre = total_events_pre / ois
    
    print(f"\nAssessment 1: Information Sufficiency")
    print(f"  OIS (for OR = {true_OR:.2f}, alpha=0.05, power=80%) = {ois:.0f} events")
    print(f"  Total events (all trials): {total_events:.0f}")
    print(f"  Total events (pre-ISIS-4): {total_events_pre:.0f}")
    print(f"  Information fraction (all): {info_fraction:.0%}")
    print(f"  Information fraction (pre-ISIS-4): {info_fraction_pre:.0%}")
    
    # Assessment 2: CI assessment
    pooled_all = mk_results['pooled_all']
    se_all = mk_results['se_all']
    ci_lo = np.exp(pooled_all - 1.96 * se_all)
    ci_hi = np.exp(pooled_all + 1.96 * se_all)
    print(f"\nAssessment 2: CI Assessment")
    print(f"  Pooled OR (all trials) = {np.exp(pooled_all):.2f} (95% CI: {ci_lo:.2f}-{ci_hi:.2f})")
    crosses_null = ci_lo < 1.0 < ci_hi
    print(f"  CI crosses null: {'Yes' if crosses_null else 'No'}")
    
    # Assessment 3: Representativeness
    rate_ratio = mk_results['s2_rate'] / mk_results['s1_rate']
    if rate_ratio < 0.67 or rate_ratio > 1.50:
        indirect_label = "Serious indirectness"
    elif rate_ratio < 0.80 or rate_ratio > 1.25:
        indirect_label = "Moderate indirectness"
    else:
        indirect_label = "Low indirectness"
    print(f"\nAssessment 3: Representativeness")
    print(f"  Event rate ratio (ISIS-4 / pre-thrombolysis) = {rate_ratio:.2f}")
    print(f"  Classification: {indirect_label}")
    
    # Assessment 4: TSA
    # Sort by year for cumulative analysis
    mg_sorted = mg_data.sort_values('year')
    cum_z_fe, cum_pooled_fe, cum_info_fe = cumulative_z(mg_sorted['logOR'].values, mg_sorted['se'].values)
    cum_z_re, cum_pooled_re, cum_info_re = cumulative_random_effects_z(mg_sorted['logOR'].values, mg_sorted['se'].values)
    
    print(f"\nAssessment 4: Trial Sequential Analysis")
    print(f"  Required information size: {ois:.0f} events")
    print(f"  Final cumulative Z (fixed-effect):   {cum_z_fe[-1]:.2f}")
    print(f"  Final cumulative Z (random-effects): {cum_z_re[-1]:.2f}")
    
    z_alpha = stats.norm.ppf(0.975)
    # O'Brien-Fleming boundary at information fraction; when info_fraction >= 1
    # the boundary has reached the conventional two-sided threshold.
    if info_fraction <= 0:
        obf_boundary = np.inf
    elif info_fraction < 1:
        obf_boundary = z_alpha / np.sqrt(info_fraction)
    else:
        obf_boundary = z_alpha
    print(f"  O'Brien-Fleming boundary at {info_fraction:.0%} information: Z = {obf_boundary:.2f}")
    print(f"  Conventional boundary: Z = {z_alpha:.2f}")
    
    # Assessment 5: Recommendation
    print(f"\nAssessment 5: Recommendation Language")
    kotha = kotha_assessment(
        info_fraction, cum_z_re[-1], ci_lo, ci_hi, rate_ratio, mk_results['I2_all']
    )
    print(f"  -> {kotha['classification']}: {kotha['rationale']}")
    
    return {
        'ois': ois, 'total_events': total_events, 'total_events_pre': total_events_pre,
        'info_fraction': info_fraction, 'info_fraction_pre': info_fraction_pre,
        'cum_z_fe': cum_z_fe, 'cum_pooled_fe': cum_pooled_fe, 'cum_info_fe': cum_info_fe,
        'cum_z_re': cum_z_re, 'cum_pooled_re': cum_pooled_re, 'cum_info_re': cum_info_re,
        'mg_sorted': mg_sorted,
        'kotha': kotha,
        'rate_ratio': rate_ratio,
        'ci_lo': ci_lo,
        'ci_hi': ci_hi,
    }


def run_module_h_statins(statin_obs, statin_rct, mk_results):
    """Apply Module H to statins in HF data."""
    print("\n" + "=" * 60)
    print("MODULE H: Guideline Interpretation (Statins in HF)")
    print("=" * 60)
    
    true_HR = mk_results['true_HR']
    ois = ois_calculation(true_HR)
    total_events = statin_rct['events'].sum()
    info_fraction = total_events / ois
    
    print(f"\nAssessment 1: Information Sufficiency")
    print(f"  OIS (for HR = {true_HR:.2f}) = {ois:.0f} events")
    print(f"  Total RCT events: {total_events}")
    print(f"  Information fraction: {info_fraction:.0%}")
    
    pooled_rct = mk_results['pooled_rct']
    se_rct = mk_results['se_rct']
    ci_lo = np.exp(pooled_rct - 1.96 * se_rct)
    ci_hi = np.exp(pooled_rct + 1.96 * se_rct)
    print(f"\nAssessment 2: CI Assessment")
    print(f"  Pooled HR = {np.exp(pooled_rct):.2f} (95% CI: {ci_lo:.2f}-{ci_hi:.2f})")
    
    rate_ratio = mk_results['rct_rate'] / mk_results['obs_rate']
    if rate_ratio < 0.67 or rate_ratio > 1.50:
        indirect_label = "Serious indirectness"
    elif rate_ratio < 0.80 or rate_ratio > 1.25:
        indirect_label = "Moderate indirectness"
    else:
        indirect_label = "Low indirectness"
    print(f"\nAssessment 3: Representativeness")
    print(f"  Event rate ratio (RCT / observational) = {rate_ratio:.2f}")
    print(f"  Classification: {indirect_label}")
    
    # Assessment 4: TSA
    st_sorted = statin_rct.sort_values('N')
    cum_z_fe, _, _ = cumulative_z(st_sorted['logHR'].values, st_sorted['se'].values)
    cum_z_re, _, _ = cumulative_random_effects_z(st_sorted['logHR'].values, st_sorted['se'].values)
    final_z_re = cum_z_re[-1]
    
    print(f"\nAssessment 4: Trial Sequential Analysis")
    print(f"  Information fraction = {info_fraction:.0%}")
    print(f"  Final cumulative Z (fixed-effect):   {cum_z_fe[-1]:.2f}")
    print(f"  Final cumulative Z (random-effects): {final_z_re:.2f}")
    
    z_alpha = stats.norm.ppf(0.975)
    print(f"  Conventional efficacy boundary: Z = {z_alpha:.2f}")
    print(f"  Conventional futility boundary: Z = {-z_alpha:.2f}")
    
    # Assessment 5: Recommendation
    print(f"\nAssessment 5: Recommendation Language")
    kotha = kotha_assessment(
        info_fraction, final_z_re, ci_lo, ci_hi, rate_ratio, mk_results['I2_rct']
    )
    print(f"  -> {kotha['classification']}: {kotha['rationale']}")
    
    return {
        'ois': ois, 'total_events': total_events, 'info_fraction': info_fraction,
        'cum_z_fe': cum_z_fe, 'cum_z_re': cum_z_re,
        'kotha': kotha,
        'rate_ratio': rate_ratio,
        'ci_lo': ci_lo,
        'ci_hi': ci_hi,
    }


# ============================================================
# FIGURE GENERATION (ALL COLOR)
# ============================================================

def fig1_framework_overview():
    """Fig 1: KOTHA Framework overview diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(5, 7.5, 'KOTHA Framework', fontsize=18, fontweight='bold',
            ha='center', va='center', color=C_BLUE)
    ax.text(5, 7.1, 'Knowledge-driven Observational-Trial Harmonization Approach',
            fontsize=11, ha='center', va='center', color=C_GREY, style='italic')
    
    # Input data boxes
    for i, (label, color) in enumerate([
        ('Retrospective\nCohort Data', C_CYAN),
        ('RCT\nMeta-analysis', C_ORANGE),
        ('Observational\nMeta-analysis', C_GREEN)
    ]):
        x = 1.5 + i * 3.5
        rect = mpatches.FancyBboxPatch((x-1.2, 5.8), 2.4, 0.9,
                                        boxstyle='round,pad=0.1',
                                        facecolor=color, alpha=0.3, edgecolor=color, lw=2)
        ax.add_patch(rect)
        ax.text(x, 6.25, label, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Arrows down
    for x in [1.5, 5.0, 8.5]:
        ax.annotate('', xy=(x, 5.0), xytext=(x, 5.7),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.5))
    
    # Module boxes
    modules = [
        ('Module K', 'Counterfactual\nPower Simulation', C_BLUE, 1.5),
        ('Module T', 'Trial-Observational\nBayesian Integration', C_ORANGE, 5.0),
        ('Module H', 'Hermeneutic\nGuideline Interpreter', C_GREEN, 8.5),
    ]
    
    for name, desc, color, x in modules:
        rect = mpatches.FancyBboxPatch((x-1.4, 3.5), 2.8, 1.5,
                                        boxstyle='round,pad=0.15',
                                        facecolor=color, alpha=0.15,
                                        edgecolor=color, lw=2.5)
        ax.add_patch(rect)
        ax.text(x, 4.6, name, ha='center', va='center', fontsize=12, fontweight='bold', color=color)
        ax.text(x, 3.95, desc, ha='center', va='center', fontsize=8, color='#333333')
    
    # Inter-module arrows
    ax.annotate('', xy=(3.4, 4.25), xytext=(2.9, 4.25),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2))
    ax.annotate('', xy=(6.8, 4.25), xytext=(6.3, 4.25),
                arrowprops=dict(arrowstyle='->', color=C_RED, lw=2))
    
    # Labels on arrows
    ax.text(3.15, 4.55, 'Risk\ndist.', fontsize=7, ha='center', color=C_RED)
    ax.text(6.55, 4.55, 'Posterior\nestimates', fontsize=7, ha='center', color=C_RED)
    
    # Output box
    rect = mpatches.FancyBboxPatch((2.5, 1.2), 5.0, 1.2,
                                    boxstyle='round,pad=0.15',
                                    facecolor=C_PURPLE, alpha=0.15,
                                    edgecolor=C_PURPLE, lw=2.5)
    ax.add_patch(rect)
    ax.text(5, 2.1, 'Integrated Evidence Assessment', ha='center', va='center',
            fontsize=13, fontweight='bold', color=C_PURPLE)
    ax.text(5, 1.6, 'GRADE-compatible recommendation with quantified uncertainty',
            ha='center', va='center', fontsize=9, color='#555555')
    
    # Arrows to output
    for x in [1.5, 5.0, 8.5]:
        ax.annotate('', xy=(max(min(x, 7.3), 2.7), 2.5), xytext=(x, 3.4),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.5))
    
    fig.savefig(f'{OUTDIR}/fig1_framework_overview.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig1_framework_overview.png")


def fig2_risk_profile_shift(mg_data):
    """Fig 2: Risk-profile shift - control event rates across trials."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Panel A: Control event rates by year
    colors_era = {'pre-thrombolysis': C_BLUE, 'transition': C_ORANGE, 'thrombolysis': C_RED}
    sizes = np.sqrt(mg_data['n_ctrl'].values) * 2
    sizes = np.clip(sizes, 20, 500)
    
    for era, color in colors_era.items():
        mask = mg_data['era'] == era
        ax1.scatter(mg_data.loc[mask, 'year'], mg_data.loc[mask, 'ctrl_rate'] * 100,
                   s=sizes[mask], c=color, alpha=0.7, edgecolor='white', lw=1, label=era.capitalize(), zorder=3)
    
    ax1.set_xlabel('Year of publication')
    ax1.set_ylabel('Control group mortality (%)')
    ax1.set_title('A. Control Event Rates Over Time', fontweight='bold')
    ax1.legend(title='Era')
    ax1.axhline(y=7.24, color=C_RED, linestyle='--', alpha=0.5, label='ISIS-4 rate')
    ax1.text(1996, 7.8, 'ISIS-4 rate (7.2%)', fontsize=8, color=C_RED)
    ax1.set_ylim(0, 30)
    ax1.grid(True, alpha=0.3)
    
    # Panel B: Distribution of event rates
    pre_rates = mg_data[mg_data['era'] == 'pre-thrombolysis']['ctrl_rate'] * 100
    post_rates = mg_data[mg_data['era'].isin(['thrombolysis'])]['ctrl_rate'] * 100
    
    bins = np.arange(0, 32, 3)
    ax2.hist(pre_rates, bins=bins, alpha=0.6, color=C_BLUE, edgecolor='white',
             label=f'Pre-thrombolysis (mean={pre_rates.mean():.1f}%)', density=True)
    ax2.axvline(pre_rates.mean(), color=C_BLUE, linestyle='--', lw=2)
    ax2.axvline(7.24, color=C_RED, linestyle='--', lw=2)
    ax2.text(7.24 + 0.5, ax2.get_ylim()[1]*0.9, 'ISIS-4\n7.2%', fontsize=9, color=C_RED)
    ax2.text(pre_rates.mean() + 0.5, ax2.get_ylim()[1]*0.7, f'Pre-thrombolysis\nmean {pre_rates.mean():.1f}%',
             fontsize=9, color=C_BLUE)
    
    ax2.set_xlabel('Control group mortality (%)')
    ax2.set_ylabel('Density')
    ax2.set_title('B. Event Rate Distribution by Era', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig2_risk_profile_shift.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig2_risk_profile_shift.png")


def fig3_power_curves(mk_results_mg, mk_results_st):
    """Fig 3: Power curves by enrollment scenario."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    
    # Panel A: Magnesium
    pr = mk_results_mg['power_results']
    ax1.plot(pr['OR'], [p*100 for p in pr['S1']], '-o', color=C_BLUE, lw=2.5, ms=6,
             label=f"S1: Pre-thrombolysis ({mk_results_mg['s1_rate']:.1%})")
    ax1.plot(pr['OR'], [p*100 for p in pr['S2']], '-s', color=C_RED, lw=2.5, ms=6,
             label=f"S2: ISIS-4 era ({mk_results_mg['s2_rate']:.1%})")
    ax1.plot(pr['OR'], [p*100 for p in pr['S3']], '-^', color=C_GREEN, lw=2.5, ms=6,
             label=f"S3: LIMIT-2 era ({mk_results_mg['s3_rate']:.1%})")
    
    ax1.axhline(80, color=C_GREY, linestyle='--', alpha=0.5)
    ax1.text(0.51, 82, '80% power', fontsize=9, color=C_GREY)
    ax1.axvline(mk_results_mg['true_OR'], color=C_PURPLE, linestyle=':', alpha=0.7)
    ax1.text(mk_results_mg['true_OR'] + 0.01, 15,
             f"Pre-ISIS-4\npooled OR\n= {mk_results_mg['true_OR']:.2f}",
             fontsize=8, color=C_PURPLE)
    
    ax1.set_xlabel('True Odds Ratio')
    ax1.set_ylabel('Statistical Power (%)')
    ax1.set_title(f"A. Magnesium in AMI (N = {mk_results_mg['N_isis4']:,})", fontweight='bold')
    ax1.legend(loc='upper right', fontsize=9)
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)
    
    # Panel B: Statins
    pr2 = mk_results_st['power_results']
    ax2.plot(pr2['OR'], [p*100 for p in pr2['S1']], '-o', color=C_BLUE, lw=2.5, ms=6,
             label=f"S1: Observational cohorts ({mk_results_st['obs_rate']:.0%})")
    ax2.plot(pr2['OR'], [p*100 for p in pr2['S2']], '-s', color=C_RED, lw=2.5, ms=6,
             label=f"S2: RCT-enrolled ({mk_results_st['rct_rate']:.0%})")
    
    ax2.axhline(80, color=C_GREY, linestyle='--', alpha=0.5)
    ax2.text(0.51, 82, '80% power', fontsize=9, color=C_GREY)
    ax2.axvline(mk_results_st['true_HR'], color=C_PURPLE, linestyle=':', alpha=0.7)
    ax2.text(mk_results_st['true_HR'] + 0.01, 15,
             f"Obs pooled\nHR = {mk_results_st['true_HR']:.2f}",
             fontsize=8, color=C_PURPLE)
    
    ax2.set_xlabel('True Hazard Ratio')
    ax2.set_ylabel('Statistical Power (%)')
    ax2.set_title(f"B. Statins in Heart Failure (N = {mk_results_st['N_rct']:,})", fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig3_power_curves.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig3_power_curves.png")


def fig4_forest_plot(mg_data, mt_results_mg):
    """Fig 4: Forest plot - individual studies and integrated estimates."""
    mg = mg_data.copy()
    
    # Compute OR and CI for each study
    studies = []
    for _, row in mg.iterrows():
        lo, se = compute_or(row['e_treat'], row['n_treat'], row['e_ctrl'], row['n_ctrl'])
        OR = np.exp(lo)
        ci_lo = np.exp(lo - 1.96 * se)
        ci_hi = np.exp(lo + 1.96 * se)
        studies.append({
            'name': row['study'],
            'OR': OR, 'ci_lo': ci_lo, 'ci_hi': ci_hi,
            'era': row['era'],
            'weight': 1/se**2,
        })
    
    # Add pooled estimates
    pp_results = mt_results_mg['power_prior']
    
    pooled_entries = [
        {'name': 'Pre-ISIS-4 (frequentist)', 'OR': None, 'ci_lo': None, 'ci_hi': None, 'era': 'pooled'},
        {'name': 'All trials (frequentist)', 'OR': None, 'ci_lo': None, 'ci_hi': None, 'era': 'pooled'},
    ]
    
    # Compute frequentist pooled
    pre_isis = mg[mg['study'] != 'ISIS-4 1995']
    lo_pre, se_pre, _, _ = random_effects_meta(pre_isis['logOR'].values, pre_isis['se'].values)
    pooled_entries[0]['OR'] = np.exp(lo_pre)
    pooled_entries[0]['ci_lo'] = np.exp(lo_pre - 1.96*se_pre)
    pooled_entries[0]['ci_hi'] = np.exp(lo_pre + 1.96*se_pre)
    
    lo_all, se_all, _, _ = random_effects_meta(mg['logOR'].values, mg['se'].values)
    pooled_entries[1]['OR'] = np.exp(lo_all)
    pooled_entries[1]['ci_lo'] = np.exp(lo_all - 1.96*se_all)
    pooled_entries[1]['ci_hi'] = np.exp(lo_all + 1.96*se_all)
    
    # Add Bayesian integrated
    for alpha in [0.3, 0.5, 1.0]:
        r = pp_results[alpha]
        pooled_entries.append({
            'name': f'Bayesian integrated (alpha={alpha})',
            'OR': r['hr_median'], 'ci_lo': r['hr_lo'], 'ci_hi': r['hr_hi'],
            'era': 'bayesian'
        })
    
    # Plot
    n_studies = len(studies)
    n_pooled = len(pooled_entries)
    total = n_studies + n_pooled + 2  # +2 for gaps
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 0.45 * total + 2))
    
    y_pos = total
    era_colors = {
        'pre-thrombolysis': C_BLUE,
        'transition': C_ORANGE,
        'thrombolysis': C_RED,
        'pooled': C_PURPLE,
        'bayesian': C_GREEN,
    }
    
    for s in studies:
        y_pos -= 1
        color = era_colors.get(s['era'], C_GREY)
        ax.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax.plot(s['OR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax.text(0.12, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax.text(4.5, y_pos, f"{s['OR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
    
    y_pos -= 1.5  # gap
    ax.axhline(y_pos + 0.5, color=C_GREY, linestyle='-', alpha=0.3)
    
    for p in pooled_entries:
        y_pos -= 1
        color = era_colors.get(p['era'], C_GREY)
        ax.plot([p['ci_lo'], p['ci_hi']], [y_pos, y_pos], '-', color=color, lw=2.5)
        ax.plot(p['OR'], y_pos, 'D', color=color, ms=9, zorder=5)
        ax.text(0.12, y_pos, p['name'], ha='right', va='center', fontsize=9, fontweight='bold')
        ax.text(4.5, y_pos, f"{p['OR']:.2f} ({p['ci_lo']:.2f}-{p['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color, fontweight='bold')
    
    ax.axvline(1.0, color='black', linestyle='-', lw=0.8)
    ax.set_xlabel('Odds Ratio (95% CI/CrI)', fontsize=12)
    ax.set_title('Magnesium in AMI: Forest Plot with Bayesian Integration', fontweight='bold', fontsize=13)
    ax.set_xlim(0.1, 5.0)
    ax.set_xscale('log')
    ax.set_xticks([0.2, 0.5, 1.0, 2.0, 4.0])
    ax.set_xticklabels(['0.2', '0.5', '1.0', '2.0', '4.0'])
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.3)
    
    # Legend
    handles = [
        mpatches.Patch(color=C_BLUE, label='Pre-thrombolysis era'),
        mpatches.Patch(color=C_ORANGE, label='Transition era'),
        mpatches.Patch(color=C_RED, label='Thrombolysis era'),
        mpatches.Patch(color=C_PURPLE, label='Frequentist pooled'),
        mpatches.Patch(color=C_GREEN, label='Bayesian integrated'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=9)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig4_forest_plot_mg.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig4_forest_plot_mg.png")


def fig5_tsa_plot(mh_results_mg):
    """Fig 5: Trial Sequential Analysis plot."""
    mg_sorted = mh_results_mg['mg_sorted']
    cum_z_fe = mh_results_mg['cum_z_fe']
    cum_z_re = mh_results_mg['cum_z_re']
    ois = mh_results_mg['ois']
    
    # Cumulative events
    cum_events = np.cumsum(mg_sorted['e_treat'].values + mg_sorted['e_ctrl'].values)
    info_fractions = cum_events / ois
    
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Z-curves
    ax.plot(cum_events, cum_z_fe, '-o', color=C_BLUE, lw=2.5, ms=6, zorder=5, label='Cumulative Z (fixed-effect)')
    ax.plot(cum_events, cum_z_re, '-s', color=C_PURPLE, lw=2.5, ms=6, zorder=5, label='Cumulative Z (random-effects)')
    
    # Label key studies
    studies_to_label = ['LIMIT-2 1992', 'ISIS-4 1995']
    for i, (_, row) in enumerate(mg_sorted.iterrows()):
        if row['study'] in studies_to_label:
            ax.annotate(row['study'],
                       xy=(cum_events[i], cum_z_fe[i]),
                       xytext=(cum_events[i] + 200, cum_z_fe[i] + 0.5),
                       fontsize=9, color=C_BLUE,
                       arrowprops=dict(arrowstyle='->', color=C_BLUE, lw=1))
    
    # Conventional boundaries
    z_alpha = stats.norm.ppf(0.975)
    ax.axhline(z_alpha, color=C_GREY, linestyle='--', lw=1, label=f'Conventional alpha=0.05 (Z={z_alpha:.2f})')
    ax.axhline(-z_alpha, color=C_GREY, linestyle='--', lw=1)
    
    # OIS line
    ax.axvline(ois, color=C_RED, linestyle='--', lw=2, alpha=0.7, label=f'Required information size ({ois:.0f} events)')
    
    # O'Brien-Fleming-like monitoring boundaries (approximate)
    info_points = np.linspace(0.1, 1.2, 50) * ois
    obf_upper = z_alpha / np.sqrt(np.clip(info_points / ois, 0.01, 1.0))
    obf_lower = -obf_upper
    ax.plot(info_points, obf_upper, '-', color=C_ORANGE, lw=2, alpha=0.7, label="O'Brien-Fleming boundary")
    ax.plot(info_points, obf_lower, '-', color=C_ORANGE, lw=2, alpha=0.7)
    
    # Futility boundary (simplified)
    fut_upper = np.where(info_points / ois < 1.0,
                         z_alpha * np.sqrt(info_points / ois) - z_alpha * np.sqrt(1 - info_points / ois),
                         0)
    ax.plot(info_points[info_points < ois], fut_upper[info_points < ois],
            '--', color=C_GREEN, lw=1.5, alpha=0.7, label='Futility boundary')
    
    # Fill zones
    ax.fill_between(info_points, obf_upper, 6, alpha=0.05, color=C_ORANGE)
    ax.fill_between(info_points, -6, obf_lower, alpha=0.05, color=C_ORANGE)
    
    ax.set_xlabel('Cumulative number of events', fontsize=12)
    ax.set_ylabel('Cumulative Z-statistic', fontsize=12)
    ax.set_title('Trial Sequential Analysis: Magnesium in AMI', fontweight='bold', fontsize=13)
    ax.legend(loc='upper left', fontsize=9)
    ax.set_ylim(-4, 6)
    ax.set_xlim(0, max(cum_events[-1], ois) * 1.1)
    ax.grid(True, alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig5_tsa_magnesium.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig5_tsa_magnesium.png")


def fig6_forest_statins(statin_obs, statin_rct, mt_results_st):
    """Fig 6: Forest plot - statins in HF with Bayesian integration."""
    pp_results = mt_results_st['power_prior']
    
    all_studies = []
    for _, row in statin_rct.iterrows():
        all_studies.append({
            'name': row['study'], 'HR': np.exp(row['logHR']),
            'ci_lo': np.exp(row['logHR'] - 1.96*row['se']),
            'ci_hi': np.exp(row['logHR'] + 1.96*row['se']),
            'type': 'RCT'
        })
    for _, row in statin_obs.iterrows():
        all_studies.append({
            'name': row['study'], 'HR': np.exp(row['logHR']),
            'ci_lo': np.exp(row['logHR'] - 1.96*row['se']),
            'ci_hi': np.exp(row['logHR'] + 1.96*row['se']),
            'type': 'OBS'
        })
    
    # Pooled estimates
    pooled_entries = []
    # RCT-only
    lo_rct, se_rct, _, _ = random_effects_meta(statin_rct['logHR'].values, statin_rct['se'].values)
    pooled_entries.append({
        'name': 'RCT pooled', 'HR': np.exp(lo_rct),
        'ci_lo': np.exp(lo_rct - 1.96*se_rct), 'ci_hi': np.exp(lo_rct + 1.96*se_rct),
        'type': 'pooled_rct'
    })
    # OBS-only
    lo_obs, se_obs, _, _ = random_effects_meta(statin_obs['logHR'].values, statin_obs['se'].values)
    pooled_entries.append({
        'name': 'Observational pooled', 'HR': np.exp(lo_obs),
        'ci_lo': np.exp(lo_obs - 1.96*se_obs), 'ci_hi': np.exp(lo_obs + 1.96*se_obs),
        'type': 'pooled_obs'
    })
    # Bayesian
    for alpha in [0.1, 0.3, 0.5]:
        r = pp_results[alpha]
        pooled_entries.append({
            'name': f'KOTHA integrated (alpha={alpha})',
            'HR': r['hr_median'], 'ci_lo': r['hr_lo'], 'ci_hi': r['hr_hi'],
            'type': 'bayesian'
        })
    
    total = len(all_studies) + len(pooled_entries) + 3
    fig, ax = plt.subplots(1, 1, figsize=(10, 0.45 * total + 2))
    
    type_colors = {
        'RCT': C_RED, 'OBS': C_BLUE,
        'pooled_rct': C_RED, 'pooled_obs': C_BLUE, 'bayesian': C_GREEN,
    }
    
    y_pos = total
    
    # RCT section
    ax.text(0.35, y_pos, 'Randomized Controlled Trials', fontsize=10, fontweight='bold', va='center')
    y_pos -= 1
    for s in [s for s in all_studies if s['type'] == 'RCT']:
        color = type_colors[s['type']]
        ax.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax.plot(s['HR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax.text(0.35, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax.text(1.6, y_pos, f"{s['HR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
        y_pos -= 1
    
    y_pos -= 0.5
    ax.text(0.35, y_pos, 'Observational Studies', fontsize=10, fontweight='bold', va='center')
    y_pos -= 1
    for s in [s for s in all_studies if s['type'] == 'OBS']:
        color = type_colors[s['type']]
        ax.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax.plot(s['HR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax.text(0.35, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax.text(1.6, y_pos, f"{s['HR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
        y_pos -= 1
    
    y_pos -= 0.5
    ax.axhline(y_pos + 0.3, color=C_GREY, linestyle='-', alpha=0.3)
    
    for p in pooled_entries:
        color = type_colors[p['type']]
        ax.plot([p['ci_lo'], p['ci_hi']], [y_pos, y_pos], '-', color=color, lw=2.5)
        ax.plot(p['HR'], y_pos, 'D', color=color, ms=9, zorder=5)
        ax.text(0.35, y_pos, p['name'], ha='right', va='center', fontsize=9, fontweight='bold')
        ax.text(1.6, y_pos, f"{p['HR']:.2f} ({p['ci_lo']:.2f}-{p['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color, fontweight='bold')
        y_pos -= 1
    
    ax.axvline(1.0, color='black', linestyle='-', lw=0.8)
    ax.set_xlabel('Hazard Ratio (95% CI/CrI)', fontsize=12)
    ax.set_title('Statins in Heart Failure: Forest Plot with KOTHA Integration', fontweight='bold', fontsize=13)
    ax.set_xlim(0.3, 1.5)
    ax.set_xscale('log')
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
    ax.set_xticklabels(['0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3'])
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.3)
    
    handles = [
        mpatches.Patch(color=C_RED, label='RCT'),
        mpatches.Patch(color=C_BLUE, label='Observational'),
        mpatches.Patch(color=C_GREEN, label='KOTHA integrated'),
    ]
    ax.legend(handles=handles, loc='lower right', fontsize=9)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig6_forest_statins.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig6_forest_statins.png")


def fig4_forest_combined(mg_data, mt_results_mg, statin_obs, statin_rct, mt_results_st):
    """Fig 4: Combined forest plots for magnesium and statins."""
    # -------- Magnesium panel --------
    mg = mg_data.copy()
    mg_studies = []
    for _, row in mg.iterrows():
        lo, se = compute_or(row['e_treat'], row['n_treat'], row['e_ctrl'], row['n_ctrl'])
        OR = np.exp(lo)
        ci_lo = np.exp(lo - 1.96 * se)
        ci_hi = np.exp(lo + 1.96 * se)
        mg_studies.append({
            'name': row['study'], 'OR': OR, 'ci_lo': ci_lo, 'ci_hi': ci_hi,
            'era': row['era'],
        })

    pp_mg = mt_results_mg['power_prior']
    pre_isis = mg[mg['study'] != 'ISIS-4 1995']
    lo_pre, se_pre, _, _ = random_effects_meta(pre_isis['logOR'].values, pre_isis['se'].values)
    lo_all, se_all, _, _ = random_effects_meta(mg['logOR'].values, mg['se'].values)
    mg_pooled = [
        {'name': 'Pre-ISIS-4 (frequentist)', 'OR': np.exp(lo_pre),
         'ci_lo': np.exp(lo_pre - 1.96*se_pre), 'ci_hi': np.exp(lo_pre + 1.96*se_pre), 'era': 'pooled'},
        {'name': 'All trials (frequentist)', 'OR': np.exp(lo_all),
         'ci_lo': np.exp(lo_all - 1.96*se_all), 'ci_hi': np.exp(lo_all + 1.96*se_all), 'era': 'pooled'},
    ]
    for alpha in [0.3, 0.5, 1.0]:
        r = pp_mg[alpha]
        mg_pooled.append({
            'name': f'Bayesian integrated (alpha={alpha})',
            'OR': r['hr_median'], 'ci_lo': r['hr_lo'], 'ci_hi': r['hr_hi'], 'era': 'bayesian'
        })

    n_mg_studies = len(mg_studies)
    n_mg_pooled = len(mg_pooled)
    total_mg = n_mg_studies + n_mg_pooled + 2

    # -------- Statins panel --------
    st_all_studies = []
    for _, row in statin_rct.iterrows():
        st_all_studies.append({
            'name': row['study'], 'HR': np.exp(row['logHR']),
            'ci_lo': np.exp(row['logHR'] - 1.96*row['se']),
            'ci_hi': np.exp(row['logHR'] + 1.96*row['se']), 'type': 'RCT'
        })
    for _, row in statin_obs.iterrows():
        st_all_studies.append({
            'name': row['study'], 'HR': np.exp(row['logHR']),
            'ci_lo': np.exp(row['logHR'] - 1.96*row['se']),
            'ci_hi': np.exp(row['logHR'] + 1.96*row['se']), 'type': 'OBS'
        })

    lo_rct, se_rct, _, _ = random_effects_meta(statin_rct['logHR'].values, statin_rct['se'].values)
    lo_obs, se_obs, _, _ = random_effects_meta(statin_obs['logHR'].values, statin_obs['se'].values)
    pp_st = mt_results_st['power_prior']
    st_pooled = [
        {'name': 'RCT pooled', 'HR': np.exp(lo_rct),
         'ci_lo': np.exp(lo_rct - 1.96*se_rct), 'ci_hi': np.exp(lo_rct + 1.96*se_rct), 'type': 'pooled_rct'},
        {'name': 'Observational pooled', 'HR': np.exp(lo_obs),
         'ci_lo': np.exp(lo_obs - 1.96*se_obs), 'ci_hi': np.exp(lo_obs + 1.96*se_obs), 'type': 'pooled_obs'},
    ]
    for alpha in [0.1, 0.3, 0.5]:
        r = pp_st[alpha]
        st_pooled.append({
            'name': f'KOTHA integrated (alpha={alpha})',
            'HR': r['hr_median'], 'ci_lo': r['hr_lo'], 'ci_hi': r['hr_hi'], 'type': 'bayesian'
        })

    total_st = len(st_all_studies) + len(st_pooled) + 3
    max_total = max(total_mg, total_st)

    # -------- Plot --------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 0.45 * max_total + 2),
                                   gridspec_kw={'wspace': 0.22})

    # Left: Magnesium
    era_colors_mg = {
        'pre-thrombolysis': C_BLUE, 'transition': C_ORANGE,
        'thrombolysis': C_RED, 'pooled': C_PURPLE, 'bayesian': C_GREEN,
    }
    y_pos = total_mg
    for s in mg_studies:
        color = era_colors_mg.get(s['era'], C_GREY)
        ax1.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax1.plot(s['OR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax1.text(0.12, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax1.text(4.5, y_pos, f"{s['OR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
        y_pos -= 1

    y_pos -= 1.5
    ax1.axhline(y_pos + 0.5, color=C_GREY, linestyle='-', alpha=0.3)
    for p in mg_pooled:
        y_pos -= 1
        color = era_colors_mg.get(p['era'], C_GREY)
        ax1.plot([p['ci_lo'], p['ci_hi']], [y_pos, y_pos], '-', color=color, lw=2.5)
        ax1.plot(p['OR'], y_pos, 'D', color=color, ms=9, zorder=5)
        ax1.text(0.12, y_pos, p['name'], ha='right', va='center', fontsize=9, fontweight='bold')
        ax1.text(4.5, y_pos, f"{p['OR']:.2f} ({p['ci_lo']:.2f}-{p['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color, fontweight='bold')

    ax1.axvline(1.0, color='black', linestyle='-', lw=0.8)
    ax1.set_xlabel('Odds Ratio (95% CI/CrI)', fontsize=12)
    ax1.set_title('A. Magnesium in AMI', fontweight='bold', fontsize=13)
    ax1.set_xlim(0.1, 5.0)
    ax1.set_xscale('log')
    ax1.set_xticks([0.2, 0.5, 1.0, 2.0, 4.0])
    ax1.set_xticklabels(['0.2', '0.5', '1.0', '2.0', '4.0'])
    ax1.set_yticks([])
    ax1.grid(True, axis='x', alpha=0.3)
    handles_mg = [
        mpatches.Patch(color=C_BLUE, label='Pre-thrombolysis era'),
        mpatches.Patch(color=C_ORANGE, label='Transition era'),
        mpatches.Patch(color=C_RED, label='Thrombolysis era'),
        mpatches.Patch(color=C_PURPLE, label='Frequentist pooled'),
        mpatches.Patch(color=C_GREEN, label='Bayesian integrated'),
    ]
    ax1.legend(handles=handles_mg, loc='lower right', fontsize=9)

    # Right: Statins
    type_colors = {
        'RCT': C_RED, 'OBS': C_BLUE,
        'pooled_rct': C_RED, 'pooled_obs': C_BLUE, 'bayesian': C_GREEN,
    }
    y_pos = total_st
    y_pos -= 1
    ax2.text(0.35, y_pos, 'Randomized Controlled Trials', fontsize=10, fontweight='bold', va='center')
    y_pos -= 1
    for s in [s for s in st_all_studies if s['type'] == 'RCT']:
        color = type_colors[s['type']]
        ax2.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax2.plot(s['HR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax2.text(0.35, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax2.text(1.6, y_pos, f"{s['HR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
        y_pos -= 1

    y_pos -= 0.5
    ax2.text(0.35, y_pos, 'Observational Studies', fontsize=10, fontweight='bold', va='center')
    y_pos -= 1
    for s in [s for s in st_all_studies if s['type'] == 'OBS']:
        color = type_colors[s['type']]
        ax2.plot([s['ci_lo'], s['ci_hi']], [y_pos, y_pos], '-', color=color, lw=1.5)
        ax2.plot(s['HR'], y_pos, 'o', color=color, ms=7, zorder=5)
        ax2.text(0.35, y_pos, s['name'], ha='right', va='center', fontsize=9)
        ax2.text(1.6, y_pos, f"{s['HR']:.2f} ({s['ci_lo']:.2f}-{s['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color)
        y_pos -= 1

    y_pos -= 0.5
    ax2.axhline(y_pos + 0.3, color=C_GREY, linestyle='-', alpha=0.3)
    for p in st_pooled:
        y_pos -= 1
        color = type_colors[p['type']]
        ax2.plot([p['ci_lo'], p['ci_hi']], [y_pos, y_pos], '-', color=color, lw=2.5)
        ax2.plot(p['HR'], y_pos, 'D', color=color, ms=9, zorder=5)
        ax2.text(0.35, y_pos, p['name'], ha='right', va='center', fontsize=9, fontweight='bold')
        ax2.text(1.6, y_pos, f"{p['HR']:.2f} ({p['ci_lo']:.2f}-{p['ci_hi']:.2f})",
                ha='left', va='center', fontsize=8, color=color, fontweight='bold')

    ax2.axvline(1.0, color='black', linestyle='-', lw=0.8)
    ax2.set_xlabel('Hazard Ratio (95% CI/CrI)', fontsize=12)
    ax2.set_title('B. Statins in heart failure', fontweight='bold', fontsize=13)
    ax2.set_xlim(0.3, 1.5)
    ax2.set_xscale('log')
    ax2.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
    ax2.set_xticklabels(['0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3'])
    ax2.set_yticks([])
    ax2.grid(True, axis='x', alpha=0.3)
    handles_st = [
        mpatches.Patch(color=C_RED, label='RCT'),
        mpatches.Patch(color=C_BLUE, label='Observational'),
        mpatches.Patch(color=C_GREEN, label='KOTHA integrated'),
    ]
    ax2.legend(handles=handles_st, loc='lower right', fontsize=9)

    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig4_forest_combined.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig4_forest_combined.png")


def fig7_sensitivity_heatmap(mt_results_mg, mt_results_st):
    """Fig 7: Sensitivity analysis heatmap - P(benefit) by alpha and case."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    alphas = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    
    # Magnesium
    pp_mg = mt_results_mg['power_prior']
    metrics_mg = np.array([[pp_mg[a]['p_benefit'] * 100,
                            pp_mg[a]['p_lt_090'] * 100,
                            pp_mg[a]['p_lt_080'] * 100] for a in alphas])
    
    for i, (label, color, marker) in enumerate([
        ('P(OR < 1.0)', C_BLUE, 'o'),
        ('P(OR < 0.90)', C_ORANGE, 's'),
        ('P(OR < 0.80)', C_RED, '^'),
    ]):
        ax1.plot(alphas, metrics_mg[:, i], f'-{marker}', color=color, lw=2, ms=8, label=label)
    
    ax1.set_xlabel('Discounting parameter alpha')
    ax1.set_ylabel('Posterior probability (%)')
    ax1.set_title('A. Magnesium in AMI', fontweight='bold')
    ax1.legend()
    ax1.set_ylim(0, 105)
    ax1.grid(True, alpha=0.3)
    ax1.axhline(95, color=C_GREY, linestyle=':', alpha=0.5)
    ax1.text(0.01, 96, '95%', fontsize=8, color=C_GREY)
    
    # Statins
    pp_st = mt_results_st['power_prior']
    metrics_st = np.array([[pp_st[a]['p_benefit'] * 100,
                            pp_st[a]['p_lt_090'] * 100,
                            pp_st[a]['p_lt_080'] * 100] for a in alphas])
    
    for i, (label, color, marker) in enumerate([
        ('P(HR < 1.0)', C_BLUE, 'o'),
        ('P(HR < 0.90)', C_ORANGE, 's'),
        ('P(HR < 0.80)', C_RED, '^'),
    ]):
        ax2.plot(alphas, metrics_st[:, i], f'-{marker}', color=color, lw=2, ms=8, label=label)
    
    ax2.set_xlabel('Discounting parameter alpha')
    ax2.set_ylabel('Posterior probability (%)')
    ax2.set_title('B. Statins in Heart Failure', fontweight='bold')
    ax2.legend()
    ax2.set_ylim(0, 105)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(95, color=C_GREY, linestyle=':', alpha=0.5)
    ax2.text(0.01, 96, '95%', fontsize=8, color=C_GREY)
    
    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig7_sensitivity_analysis.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig7_sensitivity_analysis.png")


def _severity_color(cell, domain):
    """Return a GRADE-style color for a summary table cell."""
    t = cell.lower()
    if domain == 'Risk of bias':
        if 'low' in t: return '#ccffcc'
        if 'moderate' in t: return '#fff3cc'
        if 'serious' in t: return '#ffcccc'
        return '#e0e0e0'
    if domain == 'Inconsistency':
        if 'low' in t: return '#ccffcc'
        if 'high' in t or 'substantial' in t: return '#fff3cc'
        return '#e0e0e0'
    if domain == 'Indirectness':
        if 'not assessed' in t: return '#e0e0e0'
        if 'low' in t: return '#ccffcc'
        if 'moderate' in t: return '#fff3cc'
        if 'serious' in t: return '#ffcccc'
        return '#e0e0e0'
    if domain == 'Imprecision':
        if 'not serious' in t: return '#ccffcc'
        if 'serious' in t: return '#fff3cc'
        return '#e0e0e0'
    if domain == 'Overall certainty':
        if 'high' in t and 'very' not in t: return '#ccffcc'
        if 'moderate' in t: return '#e6f5c9'
        if 'very low' in t: return '#ffcccc'
        if 'low' in t: return '#fff3cc'
        return '#e0e0e0'
    if domain == 'Recommendation':
        if 'no benefit' in t: return '#ffcccc'
        if 'inconclusive' in t or 'conditional' in t: return '#cce5ff'
        return '#ccffcc'
    return '#e0e0e0'


def _imprecision_cell(info_fraction, ci_lo, ci_hi, effect='OR'):
    """Build the imprecision label from OIS and CI."""
    if info_fraction < 1.0:
        return 'Serious\n(OIS not met)'
    if ci_hi < 1.0:
        return 'Not serious\n(OIS met, CI excludes null)'
    if effect == 'HR' and ci_lo >= 0.90:
        return 'Not serious\n(OIS met, CI excludes clinically important benefit)'
    return 'Serious\n(OIS met but CI crosses null)'


def fig8_module_h_summary(mh_mg, mh_st, mk_mg, mk_st):
    """Fig 8: Module H assessment comparison - standard vs KOTHA-enhanced.

    Uses the same KOTHA outputs that populate Table 7 so the figure and
    manuscript table remain consistent.
    """
    mg_i2 = int(round(mk_mg['I2_all']))
    st_i2 = int(round(mk_st['I2_rct']))

    mg_indirect = mh_mg['kotha']['indirectness'].capitalize()
    st_indirect = mh_st['kotha']['indirectness'].capitalize()
    mg_reduction = int(round((1 - mh_mg['rate_ratio']) * 100))
    st_reduction = int(round((1 - mh_st['rate_ratio']) * 100))

    mg_imprec = _imprecision_cell(mh_mg['info_fraction'], mh_mg['ci_lo'], mh_mg['ci_hi'], effect='OR')
    st_imprec = _imprecision_cell(mh_st['info_fraction'], mh_st['ci_lo'], mh_st['ci_hi'], effect='HR')

    # Overall certainty: standard Mg is low because of high inconsistency;
    # standard St is high because the RCT evidence has no serious concerns;
    # KOTHA certainty is driven by the dominant domain (inconsistency for Mg,
    # indirectness for St) and is therefore low for both.
    standard_mg_certainty = 'Low'
    standard_st_certainty = 'High'
    kotha_mg_certainty = 'Low'
    kotha_st_certainty = 'Low'

    mg_rec = mh_mg['kotha']['recommendation']
    st_rec = mh_st['kotha']['recommendation']

    headers = ['GRADE Domain', 'Standard\n(Mg in AMI)', 'KOTHA-enhanced\n(Mg in AMI)',
               'Standard\n(Statins in HF)', 'KOTHA-enhanced\n(Statins in HF)']

    rows = [
        ['Risk of bias', 'Low', 'Low', 'Low', 'Low'],
        ['Inconsistency', f'High ($I^2$ = {mg_i2}%)', f'High ($I^2$ = {mg_i2}%)',
         f'Low ($I^2$ = {st_i2}%)', f'Low ($I^2$ = {st_i2}%)'],
        ['Indirectness', 'Not assessed',
         f'{mg_indirect}:\nEvent rate\ndecreased by {mg_reduction}%',
         'Not assessed',
         f'{st_indirect}:\nEvent rate\ndecreased by {st_reduction}%'],
        ['Imprecision', mg_imprec, mg_imprec, st_imprec, st_imprec],
        ['Overall certainty', standard_mg_certainty, kotha_mg_certainty,
         standard_st_certainty, kotha_st_certainty],
        ['Recommendation', '"No benefit\ndemonstrated"',
         f'"{mg_rec}"', '"No benefit\ndemonstrated"', f'"{st_rec}"'],
    ]

    colors_cell = []
    for row in rows:
        domain = row[0]
        row_colors = ['#f0f0f0']
        for j in range(1, 5):
            row_colors.append(_severity_color(row[j], domain))
        colors_cell.append(row_colors)

    fig, ax = plt.subplots(1, 1, figsize=(16, 7))
    ax.axis('off')

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellColours=colors_cell,
        colColours=[C_CYAN]*5,
        loc='center',
        cellLoc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.auto_set_column_width(col=np.arange(5))
    table.scale(1.0, 2.0)

    # Style header
    for j in range(5):
        table[0, j].set_text_props(fontweight='bold', color='white')
        table[0, j].set_facecolor(C_BLUE)

    ax.set_title('Module H Assessment: Standard GRADE vs. KOTHA-Enhanced',
                 fontweight='bold', fontsize=14, pad=20)

    fig.tight_layout()
    fig.savefig(f'{OUTDIR}/fig8_module_h_comparison.png', dpi=500)
    plt.close()
    print(f"Saved: {OUTDIR}/fig8_module_h_comparison.png")


def figS1_trace_mcmc(mt_mg, mt_st):
    """Supplementary Figures S1a and S1b: MCMC trace plots for selected discounting factors."""
    selected_alphas = [0.0, 0.3, 1.0]
    cases = [
        ('magnesium', 'Mg AMI, log OR', 'log effect', mt_mg['power_prior'], 'figS1a_trace_mcmc_magnesium.png', 'Supplementary Figure S1a'),
        ('statins', 'Statins HF, log HR', 'log effect', mt_st['power_prior'], 'figS1b_trace_mcmc_statins.png', 'Supplementary Figure S1b'),
    ]
    param_names = ['log effect', 'log tau']

    for case_key, case_label, _, pp, filename, sup_fig_label in cases:
        n_rows = len(param_names)
        n_cols = len(selected_alphas)
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 2.2 * n_rows), sharex='col')
        if n_rows == 1:
            axes = axes.reshape(1, -1)

        for p, p_name in enumerate(param_names):
            for col, alpha in enumerate(selected_alphas):
                ax = axes[p, col]
                chain = pp[alpha]['chain']  # (n_walkers, n_iter, n_params)
                for w in range(chain.shape[0]):
                    ax.plot(chain[w, :, p], alpha=0.25, linewidth=0.7)
                ax.set_title(f'{case_label} - {p_name}, alpha = {alpha}', fontsize=9)
                ax.set_ylabel(p_name, fontsize=8)
                if p == n_rows - 1:
                    ax.set_xlabel('Iteration (post-warmup)', fontsize=8)
                ax.tick_params(labelsize=7)
                ax.set_xlim(0, chain.shape[1])

        fig.suptitle(f'{sup_fig_label}: MCMC trace plots for {case_key} case by parameter and discounting factor',
                     fontweight='bold', fontsize=12)
        fig.tight_layout(h_pad=2.0, w_pad=1.0)
        save_path = f'{OUTDIR}/{filename}'
        fig.savefig(save_path, dpi=500)
        plt.close()
        print(f"Saved: {save_path}")


# ============================================================
# MAIN
# ============================================================

def compute_results():
    """Run all analyses and return a dictionary of computed results."""
    mk_mg = run_module_k_magnesium(mg_data)
    mk_st = run_module_k_statins(statin_obs, statin_rct)
    mt_mg = run_module_t_magnesium(mk_mg['mg_data'])
    mt_st = run_module_t_statins(statin_obs, statin_rct)
    mh_mg = run_module_h_magnesium(mk_mg['mg_data'], mk_mg)
    mh_st = run_module_h_statins(statin_obs, statin_rct, mk_st)
    sim = run_simulation_study()
    return {
        'mk_mg': mk_mg, 'mk_st': mk_st,
        'mt_mg': mt_mg, 'mt_st': mt_st,
        'mh_mg': mh_mg, 'mh_st': mh_st,
        'sim': sim,
    }


def main():
    print("KOTHA Framework - Empirical Validation")
    print("=" * 60)
    
    results = compute_results()
    mk_mg = results['mk_mg']
    mk_st = results['mk_st']
    mt_mg = results['mt_mg']
    mt_st = results['mt_st']
    mh_mg = results['mh_mg']
    mh_st = results['mh_st']
    
    # --- Generate Figures ---
    print("\n" + "=" * 60)
    print("GENERATING FIGURES")
    print("=" * 60)
    
    fig1_framework_overview()
    fig2_risk_profile_shift(mk_mg['mg_data'])
    fig3_power_curves(mk_mg, mk_st)
    fig4_forest_combined(mk_mg['mg_data'], mt_mg, statin_obs, statin_rct, mt_st)
    fig5_tsa_plot(mh_mg)
    fig7_sensitivity_heatmap(mt_mg, mt_st)
    fig8_module_h_summary(mh_mg, mh_st, mk_mg, mk_st)
    figS1_trace_mcmc(mt_mg, mt_st)

    print("\n" + "=" * 60)
    print("SIMULATION STUDY")
    print("=" * 60)
    sim = results['sim']
    plot_simulation_results(sim)
    save_simulation_summary(sim)
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    
    # Save numerical results summary
    with open(os.path.join(OUTDIR, '..', 'results_summary.txt'), 'w') as f:
        f.write("KOTHA Framework Validation - Numerical Results Summary\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("CASE 1: Intravenous Magnesium in AMI\n")
        f.write("-" * 40 + "\n")
        f.write(f"Pre-thrombolysis control event rate: {mk_mg['s1_rate']:.3f}\n")
        f.write(f"ISIS-4 control event rate: {mk_mg['s2_rate']:.3f}\n")
        f.write(f"Event rate ratio (S2/S1): {mk_mg['s2_rate']/mk_mg['s1_rate']:.2f}\n")
        f.write(f"Pre-ISIS-4 pooled OR: {np.exp(mk_mg['pooled_pre']):.2f}\n")
        f.write(f"All-trials pooled OR: {np.exp(mk_mg['pooled_all']):.2f}\n")
        
        p2, e2 = power_analytical(mk_mg['s2_rate'], mk_mg['true_OR'], mk_mg['N_isis4'])
        p1, e1 = power_analytical(mk_mg['s1_rate'], mk_mg['true_OR'], mk_mg['N_isis4'])
        f.write(f"Power at ISIS-4 N with pre-ISIS-4 effect:\n")
        f.write(f"  S1 (high-risk): {p1:.1%}\n")
        f.write(f"  S2 (ISIS-4 rate): {p2:.1%}\n")
        
        f.write(f"OIS: {mh_mg['ois']:.0f} events\n")
        f.write(f"Total events: {mh_mg['total_events']:.0f}\n")
        f.write(f"Information fraction: {mh_mg['info_fraction']:.0%}\n\n")
        
        f.write("Bayesian integration (power prior):\n")
        for alpha in [0.0, 0.3, 0.5, 1.0]:
            r = mt_mg['power_prior'][alpha]
            f.write(f"  alpha={alpha}: OR={r['hr_median']:.2f} ({r['hr_lo']:.2f}-{r['hr_hi']:.2f}), "
                    f"P(OR<1)={r['p_benefit']:.1%}\n")
        
        f.write(f"\nCASE 2: Statins in Heart Failure\n")
        f.write("-" * 40 + "\n")
        f.write(f"Observational pooled HR: {mk_st['true_HR']:.2f}\n")
        f.write(f"RCT pooled HR: {np.exp(mk_st['pooled_rct']):.2f}\n")
        f.write(f"Event rate ratio (RCT/obs): {mk_st['rct_rate']/mk_st['obs_rate']:.2f}\n")
        
        f.write(f"OIS: {mh_st['ois']:.0f} events\n")
        f.write(f"Total RCT events: {mh_st['total_events']}\n")
        f.write(f"Information fraction: {mh_st['info_fraction']:.0%}\n\n")
        
        f.write("Bayesian integration (power prior):\n")
        for alpha in [0.0, 0.3, 0.5, 1.0]:
            r = mt_st['power_prior'][alpha]
            f.write(f"  alpha={alpha}: HR={r['hr_median']:.2f} ({r['hr_lo']:.2f}-{r['hr_hi']:.2f}), "
                    f"P(HR<1)={r['p_benefit']:.1%}\n")
    
    print(f"\nResults saved to: {OUTDIR}/../results_summary.txt")


if __name__ == '__main__':
    main()
