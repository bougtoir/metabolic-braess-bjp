#!/usr/bin/env python3
"""
KOTHA Simulation Study
======================
Study-level simulation of enrollment-driven structural information loss.

Purpose
-------
Demonstrate that standard meta-analysis of RCTs that exclude high-risk
patients can yield attenuated treatment-effect estimates and reduced power,
and that the KOTHA framework (counterfactual power simulation + Bayesian
power-prior integration) identifies and partially corrects this loss.

Data-generating process
-----------------------
- 20 hypothetical studies, each with 1:1 randomization and n=1,000 per arm.
- Baseline risk distribution: logit(p_c) = mu + sigma * Z, Z ~ N(0,1).
- True study-specific log-OR = theta0 + gamma * Z.
  gamma < 0 means higher baseline risk is associated with larger treatment
  benefit (more negative log-OR). This is the effect-modification mechanism
  that produces structural information loss when high-risk patients are
  excluded.
- Enrollment: studies with Z > z_threshold are excluded (top 20% risk).
  The remaining "RCT-enrolled" studies have lower mean p_c and a less
  negative mean log-OR than the target population.
- Observational studies: all 20 studies, but each observed log-OR is
  shifted by a systematic confounding bias and inflated standard error.

All parameters are fixed and documented below; no patient-level data are
used. The simulation is fully reproducible from this script.
"""

import os
import json

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import expit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(OUTDIR, exist_ok=True)

# Color palette (Okabe-Ito, colorblind-friendly)
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
    'legend.fontsize': 9,
    'figure.dpi': 300,
    'savefig.dpi': 500,
    'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})


def compute_or(e_t, n_t, e_c, n_c, cc=0.5):
    """Compute log-OR and SE with continuity correction."""
    a = e_t + cc
    b = (n_t - e_t) + cc
    c = e_c + cc
    d = (n_c - e_c) + cc
    logOR = np.log(a * d / (b * c))
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return logOR, se


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


def power_analytical(p_control, OR, n_total, alpha=0.05):
    """Analytical power for a two-arm trial with binary outcome."""
    p_treat = (p_control * OR) / (1 - p_control + p_control * OR)
    n_arm = n_total // 2
    e_ctrl = n_arm * p_control
    e_treat = n_arm * p_treat
    total_events = e_ctrl + e_treat
    z_alpha = stats.norm.ppf(1 - alpha/2)
    logOR = np.log(OR)
    se_logOR = 2 / np.sqrt(total_events) if total_events > 0 else np.inf
    z_effect = abs(logOR) / se_logOR
    power = stats.norm.cdf(z_effect - z_alpha)
    return power, total_events


def _simulate_one_replication(rng, n_studies, n_per_arm,
                              mu_logit, sigma_logit, theta0, gamma,
                              enrollment_quantile, obs_bias,
                              obs_extra_tau, obs_se_factor):
    """Generate one hypothetical meta-analysis and return estimates."""
    Z = rng.normal(0, 1, n_studies)
    logit_pc = mu_logit + sigma_logit * Z
    p_c = expit(logit_pc)

    # True study-specific log-OR depends on baseline risk
    true_logOR = theta0 + gamma * Z
    OR = np.exp(true_logOR)
    p_t = (p_c * OR) / (1 - p_c + p_c * OR)

    n_arm = n_per_arm
    e_c = rng.binomial(n_arm, p_c)
    e_t = rng.binomial(n_arm, p_t)

    # RCT target (all studies)
    logORs, ses = [], []
    for i in range(n_studies):
        lo, se = compute_or(e_t[i], n_arm, e_c[i], n_arm)
        logORs.append(lo)
        ses.append(se)
    logORs = np.array(logORs)
    ses = np.array(ses)

    # Enrollment selection: exclude top (1 - enrollment_quantile) risk
    z_thresh = stats.norm.ppf(enrollment_quantile)
    enrolled = Z <= z_thresh

    # Observational estimates (all studies, biased + extra noise)
    obs_logOR = true_logOR + obs_bias + rng.normal(0, obs_extra_tau, n_studies)
    obs_se = ses * obs_se_factor

    return {
        'Z': Z,
        'p_c': p_c,
        'true_logOR': true_logOR,
        'logORs': logORs,
        'ses': ses,
        'enrolled': enrolled,
        'e_c': e_c,
        'e_t': e_t,
        'obs_logOR': obs_logOR,
        'obs_se': obs_se,
    }


def _kotha_power_prior_estimate(logORs_rct, ses_rct, logORs_obs, ses_obs, alpha):
    """Normal-approximation power-prior meta-analysis.

    The observational likelihood is discounted by alpha in [0,1].
    Effective weights: RCT = 1/se^2, OBS = alpha/se^2.
    """
    if alpha == 0:
        return random_effects_meta(logORs_rct, ses_rct)[:2]
    w_rct = 1 / ses_rct**2
    w_obs = alpha / ses_obs**2
    all_y = np.concatenate([logORs_rct, logORs_obs])
    all_w = np.concatenate([w_rct, w_obs])
    all_se = 1 / np.sqrt(all_w)
    pooled, se_pooled, _, _ = random_effects_meta(all_y, all_se)
    return pooled, se_pooled


def _compute_metrics(pooled, se, theta0):
    """Operating-characteristic metrics across replications."""
    bias = float(np.mean(pooled - theta0))
    rmse = float(np.sqrt(np.mean((pooled - theta0)**2)))
    ci_lo = np.exp(pooled - 1.96 * se)
    ci_hi = np.exp(pooled + 1.96 * se)
    true_or = np.exp(theta0)
    coverage = float(np.mean((ci_lo <= true_or) & (ci_hi >= true_or)))
    power = float(np.mean(ci_hi < 1.0))  # true effect < 1, two-sided benefit
    return {'bias': bias, 'rmse': rmse, 'coverage': coverage, 'power': power}


def run_simulation_study(n_reps=500, seed=20260821,
                         n_studies=20, n_per_arm=1000,
                         mu_logit=-2.2, sigma_logit=1.0,
                         theta0=None, gamma=-0.5,
                         enrollment_quantile=0.80,
                         obs_bias=-0.15, obs_extra_tau=0.15,
                         obs_se_factor=1.5):
    """Run the KOTHA operating-characteristics simulation.

    Returns a dict with raw replications and summary metrics that can be
    inserted directly into the manuscript build pipeline.
    """
    if theta0 is None:
        theta0 = np.log(0.80)

    rng = np.random.default_rng(seed)
    alpha_grid = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

    target_est, target_se = [], []
    enrolled_est, enrolled_se = [], []
    obs_est, obs_se = [], []
    kotha_est = {a: [] for a in alpha_grid}
    kotha_se = {a: [] for a in alpha_grid}

    rate_target_all = []
    rate_enrolled_all = []

    replications = []
    for rep in range(n_reps):
        rep_data = _simulate_one_replication(
            rng, n_studies, n_per_arm, mu_logit, sigma_logit,
            theta0, gamma, enrollment_quantile, obs_bias,
            obs_extra_tau, obs_se_factor
        )

        Z = rep_data['Z']
        p_c = rep_data['p_c']
        logORs = rep_data['logORs']
        ses = rep_data['ses']
        enrolled = rep_data['enrolled']
        e_c = rep_data['e_c']
        e_t = rep_data['e_t']
        obs_logOR_rep = rep_data['obs_logOR']
        obs_se_rep = rep_data['obs_se']

        # Target (all studies)
        p_t, s_t, _, _ = random_effects_meta(logORs, ses)
        target_est.append(p_t)
        target_se.append(s_t)

        # RCT enrolled
        p_e, s_e, _, _ = random_effects_meta(logORs[enrolled], ses[enrolled])
        enrolled_est.append(p_e)
        enrolled_se.append(s_e)

        # Observational
        p_o, s_o, _, _ = random_effects_meta(obs_logOR_rep, obs_se_rep)
        obs_est.append(p_o)
        obs_se.append(s_o)

        # KOTHA power prior
        for alpha in alpha_grid:
            p_k, s_k = _kotha_power_prior_estimate(
                logORs[enrolled], ses[enrolled], obs_logOR_rep, obs_se_rep, alpha
            )
            kotha_est[alpha].append(p_k)
            kotha_se[alpha].append(s_k)

        # Event rates for Module K counterfactual power
        rate_target = (e_c.sum() + e_t.sum()) / (2 * n_per_arm * n_studies)
        rate_enrolled = (e_c[enrolled].sum() + e_t[enrolled].sum()) / (
            2 * n_per_arm * enrolled.sum()
        ) if enrolled.sum() > 0 else np.nan
        rate_target_all.append(rate_target)
        rate_enrolled_all.append(rate_enrolled)

        if rep == 0:
            # Save one example for the scatter plot
            example = rep_data

    target_est = np.array(target_est)
    target_se = np.array(target_se)
    enrolled_est = np.array(enrolled_est)
    enrolled_se = np.array(enrolled_se)
    obs_est = np.array(obs_est)
    obs_se = np.array(obs_se)
    rate_target_all = np.array(rate_target_all)
    rate_enrolled_all = np.array(rate_enrolled_all)

    # Overall summary metrics
    methods = {
        'Target (all RCTs)': (target_est, target_se),
        'RCT enrolled only': (enrolled_est, enrolled_se),
        'Observational only': (obs_est, obs_se),
    }
    for alpha in alpha_grid:
        methods[f'KOTHA alpha={alpha:.1f}'] = (
            np.array(kotha_est[alpha]), np.array(kotha_se[alpha])
        )

    metrics = {}
    for name, (est, se) in methods.items():
        metrics[name] = _compute_metrics(est, se, theta0)

    # Find alpha that minimizes RMSE among KOTHA estimates
    rmse_by_alpha = {alpha: _compute_metrics(np.array(kotha_est[alpha]),
                                             np.array(kotha_se[alpha]),
                                             theta0)['rmse']
                     for alpha in alpha_grid}
    optimal_alpha = min(rmse_by_alpha, key=rmse_by_alpha.get)

    # Event-rate ratio
    mean_rate_target = float(np.nanmean(rate_target_all))
    mean_rate_enrolled = float(np.nanmean(rate_enrolled_all))
    event_rate_ratio = float(mean_rate_enrolled / mean_rate_target)

    # Counterfactual power at true OR under target and enrolled rates
    n_total_target = int(n_studies * 2 * n_per_arm)
    n_enrolled_expected = int(round(n_studies * enrollment_quantile))
    n_total_enrolled = n_enrolled_expected * 2 * n_per_arm
    power_target_true, _ = power_analytical(mean_rate_target, np.exp(theta0), n_total_target)
    power_enrolled_true, _ = power_analytical(mean_rate_enrolled, np.exp(theta0), n_total_enrolled)

    summary = {
        'n_reps': n_reps,
        'n_studies': n_studies,
        'n_per_arm': n_per_arm,
        'mu_logit': mu_logit,
        'sigma_logit': sigma_logit,
        'theta0': float(theta0),
        'gamma': gamma,
        'enrollment_quantile': enrollment_quantile,
        'obs_bias': obs_bias,
        'obs_extra_tau': obs_extra_tau,
        'obs_se_factor': obs_se_factor,
        'true_OR': float(np.exp(theta0)),
        'mean_rate_target': mean_rate_target,
        'mean_rate_enrolled': mean_rate_enrolled,
        'event_rate_ratio': event_rate_ratio,
        'power_target_true': power_target_true,
        'power_enrolled_true': power_enrolled_true,
        'optimal_alpha': float(optimal_alpha),
        'rmse_by_alpha': {str(k): v for k, v in rmse_by_alpha.items()},
        'metrics': metrics,
        'example': example,
    }
    return summary


def _sim_table_rows(summary):
    """Build markdown table rows from summary metrics."""
    order = [
        'Target (all RCTs)',
        'RCT enrolled only',
        'Observational only',
        'KOTHA alpha=0.3',
        f"KOTHA alpha={summary['optimal_alpha']:.1f}",
    ]
    rows = []
    for name in order:
        m = summary['metrics'][name]
        rows.append({
            'method': name,
            'bias': m['bias'],
            'rmse': m['rmse'],
            'coverage': m['coverage'] * 100,
            'power': m['power'] * 100,
        })
    return rows


def _get_optimal_label(summary):
    return f"KOTHA alpha={summary['optimal_alpha']:.1f}"


def plot_simulation_results(summary, outpath=None):
    """Generate a 2x2 figure summarizing the operating-characteristics study."""
    if outpath is None:
        outpath = os.path.join(OUTDIR, 'fig_simulation_operating_characteristics.png')

    example = summary['example']
    Z = example['Z']
    p_c = example['p_c']
    true_logOR = example['true_logOR']
    enrolled = example['enrolled']
    z_thresh = stats.norm.ppf(summary['enrollment_quantile'])

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # Panel A: baseline risk vs true log-OR, with enrollment threshold
    ax = axes[0, 0]
    scatter = ax.scatter(p_c[enrolled] * 100, true_logOR[enrolled],
                        c=C_BLUE, alpha=0.7, s=80, edgecolor='white', label='Enrolled (S=1)')
    ax.scatter(p_c[~enrolled] * 100, true_logOR[~enrolled],
              c=C_RED, alpha=0.7, marker='x', s=80, label='Excluded')
    # Risk threshold line
    p_thresh = expit(summary['mu_logit'] + summary['sigma_logit'] * z_thresh)
    ax.axvline(p_thresh * 100, color=C_ORANGE, linestyle='--', lw=2,
              label=f'Eligibility threshold (Z={z_thresh:.2f})')
    # True target log-OR
    ax.axhline(summary['theta0'], color=C_GREY, linestyle=':', lw=1.5,
              label=f'Target log-OR = {summary["theta0"]:.2f}')
    ax.set_xlabel('Control event rate (%)')
    ax.set_ylabel('True study log-OR')
    ax.set_title('A. Risk-dependent treatment effects and enrollment selection',
                fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel B: Bias across methods
    ax = axes[0, 1]
    methods = ['Target (all RCTs)', 'RCT enrolled only', 'Observational only',
               'KOTHA alpha=0.3', _get_optimal_label(summary)]
    biases = [summary['metrics'][m]['bias'] for m in methods]
    colors = [C_GREEN, C_RED, C_ORANGE, C_BLUE, C_PURPLE]
    bars = ax.barh(methods, biases, color=colors, alpha=0.8, edgecolor='black')
    ax.axvline(0, color='black', linestyle='-', lw=0.8)
    ax.set_xlabel('Bias in log-OR (mean estimate - true)')
    ax.set_title('B. Bias relative to target population estimand',
                fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    # annotate values
    for bar, val in zip(bars, biases):
        ax.text(val + (0.01 if val >= 0 else -0.01), bar.get_y() + bar.get_height()/2,
               f'{val:.3f}', ha='left' if val >= 0 else 'right', va='center', fontsize=8)

    # Panel C: RMSE
    ax = axes[1, 0]
    rmses = [summary['metrics'][m]['rmse'] for m in methods]
    bars = ax.barh(methods, rmses, color=colors, alpha=0.8, edgecolor='black')
    ax.set_xlabel('RMSE (log-OR)')
    ax.set_title('C. Root mean squared error', fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    for bar, val in zip(bars, rmses):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
               f'{val:.3f}', ha='left', va='center', fontsize=8)

    # Panel D: Coverage and power
    ax = axes[1, 1]
    coverage = [summary['metrics'][m]['coverage'] * 100 for m in methods]
    power = [summary['metrics'][m]['power'] * 100 for m in methods]
    x = np.arange(len(methods))
    width = 0.35
    bars1 = ax.bar(x - width/2, coverage, width, label='Coverage of true OR (%)',
                  color=C_CYAN, alpha=0.8, edgecolor='black')
    bars2 = ax.bar(x + width/2, power, width, label='Power to detect benefit (%)',
                  color=C_YELLOW, alpha=0.8, edgecolor='black')
    ax.axhline(95, color=C_GREY, linestyle='--', alpha=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace(' (', '\n(') for m in methods], fontsize=8, rotation=0)
    ax.set_ylabel('Percentage (%)')
    ax.set_title('D. Coverage and statistical power', fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)
    ax.set_ylim(0, 105)
    ax.grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    fig.savefig(outpath, dpi=500)
    plt.close()
    print(f'Saved: {outpath}')
    return outpath


def save_simulation_summary(summary, outpath=None):
    """Save a JSON summary and a CSV table for reproducibility."""
    if outpath is None:
        outpath = os.path.join(BASE_DIR, 'simulation_summary.json')

    # Remove non-JSON-serializable objects
    serializable = {k: v for k, v in summary.items() if k != 'example'}
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2)
    print(f'Saved: {outpath}')

    # Save metrics CSV
    rows = _sim_table_rows(summary)
    df = pd.DataFrame(rows)
    csv_path = os.path.join(BASE_DIR, 'simulation_metrics.csv')
    df.to_csv(csv_path, index=False, float_format='%.3f')
    print(f'Saved: {csv_path}')
    return outpath, csv_path


if __name__ == '__main__':
    summary = run_simulation_study()
    plot_simulation_results(summary)
    save_simulation_summary(summary)
    print(json.dumps(summary.get('metrics', {}), indent=2))
