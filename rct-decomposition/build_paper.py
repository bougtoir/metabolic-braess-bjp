#!/usr/bin/env python3
"""
Build the KOTHA manuscript from the reproducible analysis pipeline.

Outputs:
- 04_paper_rsm.md (generated from paper_template.md + computed results)
- KOTHA_Framework_RSM.docx (via generate_rsm_docx_final.py)

Run this after `validation/run_validation.py` to ensure figures are current.
"""
import io
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

BASE = os.path.dirname(os.path.abspath(__file__))


def _run_validation():
    """Ensure figures and results_summary.txt are up to date."""
    subprocess.run(
        [sys.executable, os.path.join(BASE, 'validation', 'run_validation.py')],
        cwd=BASE,
        check=True,
    )


def _compute_values():
    """Import the validation module and compute all manuscript values."""
    sys.path.insert(0, os.path.join(BASE, 'validation'))
    import run_validation as rv

    # Compute all analysis results (suppress stdout to avoid duplicating prints)
    buf = io.StringIO()
    import contextlib
    with contextlib.redirect_stdout(buf):
        results = rv.compute_results()

    mk_mg = results['mk_mg']
    mk_st = results['mk_st']
    mt_mg = results['mt_mg']
    mt_st = results['mt_st']
    mh_mg = results['mh_mg']
    mh_st = results['mh_st']

    # MCMC convergence diagnostics ( conservative summary across cases and alphas )
    all_ess = []
    all_rhat = []
    for case in (mt_mg, mt_st):
        for alpha, r in case['power_prior'].items():
            all_ess.extend([r.get('ess_mu', np.nan), r.get('ess_log_tau', np.nan)])
            all_rhat.extend([r.get('rhat_mu', np.nan), r.get('rhat_log_tau', np.nan)])
    min_ess = int(round(min([e for e in all_ess if not np.isnan(e)])))
    max_rhat = max([r for r in all_rhat if not np.isnan(r)])

    # ------------------------------------------------------------------
    # Common helpers
    # ------------------------------------------------------------------
    def fmt_pct(x):
        return f"{x*100:.1f}%".replace("%", "\\%")

    def fmt_or(log_or, se):
        or_ = np.exp(log_or)
        lo = np.exp(log_or - 1.96 * se)
        hi = np.exp(log_or + 1.96 * se)
        return or_, lo, hi

    def fmt_hr(log_hr, se):
        return fmt_or(log_hr, se)

    # Magnesium Module K
    mg_pre_or, mg_pre_lo, mg_pre_hi = fmt_or(mk_mg['pooled_pre'], mk_mg['se_pre'])
    mg_all_or, mg_all_lo, mg_all_hi = fmt_or(mk_mg['pooled_all'], mk_mg['se_all'])

    s1_rate = mk_mg['s1_rate']
    s2_rate = mk_mg['s2_rate']
    s3_rate = mk_mg['s3_rate']

    # Power values at selected points
    pr_mg = pd.DataFrame(mk_mg['power_results'])
    def mg_power(or_val, scenario):
        idx = np.argmin(np.abs(pr_mg['OR'].values - or_val))
        return pr_mg.iloc[idx][scenario] * 100

    p1_true, e1_true = rv.power_analytical(s1_rate, mk_mg['true_OR'], mk_mg['N_isis4'])
    p2_true, e2_true = rv.power_analytical(s2_rate, mk_mg['true_OR'], mk_mg['N_isis4'])
    p3_true, e3_true = rv.power_analytical(s3_rate, mk_mg['true_OR'], mk_mg['N_isis4'])

    # Required N for 80% power at true_OR across scenarios
    def required_n(rate, or_true):
        for N in range(1000, 200000, 500):
            p, _ = rv.power_analytical(rate, or_true, N)
            if p >= 0.80:
                return N
        return None

    req_n_s1 = required_n(s1_rate, mk_mg['true_OR'])
    req_n_s2 = required_n(s2_rate, mk_mg['true_OR'])
    req_n_s3 = required_n(s3_rate, mk_mg['true_OR'])

    # Statins Module K
    st_obs_hr, st_obs_lo, st_obs_hi = fmt_hr(mk_st['pooled_obs'], mk_st['se_obs'])
    st_rct_hr, st_rct_lo, st_rct_hi = fmt_hr(mk_st['pooled_rct'], mk_st['se_rct'])

    pr_st = pd.DataFrame(mk_st['power_results'])
    def st_power(hr_val, scenario):
        idx = np.argmin(np.abs(pr_st['OR'].values - hr_val))
        return pr_st.iloc[idx][scenario] * 100

    # Power at the exact observational pooled HR (not on the grid) is computed directly
    p_st_s1_true, _ = rv.power_analytical(mk_st['obs_rate'], mk_st['true_HR'], mk_st['N_rct'])
    p_st_s2_true, _ = rv.power_analytical(mk_st['rct_rate'], mk_st['true_HR'], mk_st['N_rct'])

    # Module T tables
    def pp_rows(pp):
        rows = []
        for alpha in [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]:
            r = pp[alpha]
            rows.append({
                'alpha': alpha,
                'median': r['hr_median'],
                'lo': r['hr_lo'],
                'hi': r['hr_hi'],
                'p1': r['p_benefit'] * 100,
                'p09': r['p_lt_090'] * 100,
                'p08': r['p_lt_080'] * 100,
            })
        return rows

    mg_pp_rows = pp_rows(mt_mg['power_prior'])
    st_pp_rows = pp_rows(mt_st['power_prior'])

    # Module H boundaries
    z_alpha = stats.norm.ppf(0.975)
    # O'Brien-Fleming boundary at the final information fraction. Once the
    # optimal information size is reached, the OBF boundary equals the conventional
    # two-sided threshold; before that it is more conservative.
    if mh_mg['info_fraction'] < 1:
        mg_obf = z_alpha / np.sqrt(mh_mg['info_fraction'])
    else:
        mg_obf = z_alpha

    v = {
        # Magnesium case selection / Module K
        'mg_n_trials': len(rv.mg_data),
        'mg_year_min': int(rv.mg_data['year'].min()),
        'mg_year_max': int(rv.mg_data['year'].max()),
        's1_rate': s1_rate,
        's1_rate_pct': f"{s1_rate*100:.1f}",
        's2_rate': s2_rate,
        's2_rate_pct': f"{s2_rate*100:.1f}",
        's3_rate': s3_rate,
        's3_rate_pct': f"{s3_rate*100:.1f}",
        'mg_rate_ratio': s2_rate / s1_rate,
        'mg_rate_reduction_pct': (1 - s2_rate / s1_rate) * 100,
        'mg_pre_or': mg_pre_or,
        'mg_pre_lo': mg_pre_lo,
        'mg_pre_hi': mg_pre_hi,
        'mg_pre_i2': mk_mg['I2_pre'],
        'mg_all_or': mg_all_or,
        'mg_all_lo': mg_all_lo,
        'mg_all_hi': mg_all_hi,
        'mg_all_i2': mk_mg['I2_all'],
        'N_isis4': int(mk_mg['N_isis4']),
        'true_or': mk_mg['true_OR'],
        'mg_power_s1_true': p1_true * 100,
        'mg_power_s2_true': p2_true * 100,
        'mg_power_s3_true': p3_true * 100,
        'mg_events_s1_true': int(round(e1_true)),
        'mg_events_s2_true': int(round(e2_true)),
        'mg_events_s3_true': int(round(e3_true)),
        'mg_req_n_s1': req_n_s1,
        'mg_req_n_s2': req_n_s2,
        'mg_req_n_s3': req_n_s3,
        'mg_power_s1_or090': mg_power(0.90, 'S1'),
        'mg_power_s2_or090': mg_power(0.90, 'S2'),
        'mg_power_s3_or090': mg_power(0.90, 'S3'),

        # Statins
        'st_n_obs': len(rv.statin_obs),
        'st_n_rct': len(rv.statin_rct),
        'st_obs_hr': st_obs_hr,
        'st_obs_lo': st_obs_lo,
        'st_obs_hi': st_obs_hi,
        'st_obs_i2': mk_st['I2_obs'],
        'st_rct_hr': st_rct_hr,
        'st_rct_lo': st_rct_lo,
        'st_rct_hi': st_rct_hi,
        'st_rct_i2': mk_st['I2_rct'],
        'st_true_hr': mk_st['true_HR'],
        'N_statin_rct': int(mk_st['N_rct']),
        'obs_rate': mk_st['obs_rate'],
        'rct_rate': mk_st['rct_rate'],
        'st_s3_rate': mk_st.get('s3_rate', 0.12),
        'st_rate_ratio': mk_st['rct_rate'] / mk_st['obs_rate'],
        'st_rate_reduction_pct': (1 - mk_st['rct_rate'] / mk_st['obs_rate']) * 100,
        'st_power_s1_true': p_st_s1_true * 100,
        'st_power_s2_true': p_st_s2_true * 100,
        'st_power_s1_hr085': st_power(0.85, 'S1'),
        'st_power_s2_hr085': st_power(0.85, 'S2'),

        # Module T summaries
        'alpha_example': 0.3,
        'mg_pp_alpha0_or': mt_mg['power_prior'][0.0]['hr_median'],
        'mg_pp_alpha0_lo': mt_mg['power_prior'][0.0]['hr_lo'],
        'mg_pp_alpha0_hi': mt_mg['power_prior'][0.0]['hr_hi'],
        'mg_pp_alpha0_p1': mt_mg['power_prior'][0.0]['p_benefit'] * 100,
        'mg_pp_alpha0_p09': mt_mg['power_prior'][0.0]['p_lt_090'] * 100,
        'mg_pp_alpha3_or': mt_mg['power_prior'][0.3]['hr_median'],
        'mg_pp_alpha3_lo': mt_mg['power_prior'][0.3]['hr_lo'],
        'mg_pp_alpha3_hi': mt_mg['power_prior'][0.3]['hr_hi'],
        'mg_pp_alpha3_p1': mt_mg['power_prior'][0.3]['p_benefit'] * 100,
        'mg_pp_alpha1_or': mt_mg['power_prior'][1.0]['hr_median'],
        'mg_pp_alpha1_lo': mt_mg['power_prior'][1.0]['hr_lo'],
        'mg_pp_alpha1_hi': mt_mg['power_prior'][1.0]['hr_hi'],
        'mg_pp_alpha1_p1': mt_mg['power_prior'][1.0]['p_benefit'] * 100,
        'st_pp_alpha0_hr': mt_st['power_prior'][0.0]['hr_median'],
        'st_pp_alpha0_lo': mt_st['power_prior'][0.0]['hr_lo'],
        'st_pp_alpha0_hi': mt_st['power_prior'][0.0]['hr_hi'],
        'st_pp_alpha0_p1': mt_st['power_prior'][0.0]['p_benefit'] * 100,
        'st_pp_alpha0_p09': mt_st['power_prior'][0.0]['p_lt_090'] * 100,
        'st_pp_alpha3_hr': mt_st['power_prior'][0.3]['hr_median'],
        'st_pp_alpha3_lo': mt_st['power_prior'][0.3]['hr_lo'],
        'st_pp_alpha3_hi': mt_st['power_prior'][0.3]['hr_hi'],
        'st_pp_alpha3_p1': mt_st['power_prior'][0.3]['p_benefit'] * 100,
        'st_pp_alpha3_p09': mt_st['power_prior'][0.3]['p_lt_090'] * 100,

        # Module H
        'mg_ois': int(round(mh_mg['ois'])),
        'mg_total_events': int(round(mh_mg['total_events'])),
        'mg_info_frac': mh_mg['info_fraction'] * 100,
        'mg_z_fe': mh_mg['cum_z_fe'][-1],
        'mg_z_re': mh_mg['cum_z_re'][-1],
        'mg_z_alpha': stats.norm.ppf(0.975),
        'mg_obf': mg_obf,
        'mg_ois_075': int(round(rv.ois_calculation(0.75))),
        'st_ois': int(round(mh_st['ois'])),
        'st_total_events': int(round(mh_st['total_events'])),
        'st_info_frac': mh_st['info_fraction'] * 100,
        'st_z_fe': mh_st['cum_z_fe'][-1],
        'st_z_re': mh_st['cum_z_re'][-1],

        # Module H KOTHA-enhanced classifications (from run_validation.py)
        'mg_kotha_classification': mh_mg['kotha']['classification'],
        'mg_kotha_recommendation': mh_mg['kotha']['recommendation'],
        'mg_kotha_rationale': mh_mg['kotha']['rationale'],
        'mg_kotha_indirectness': mh_mg['kotha']['indirectness'],
        'mg_kotha_inconsistency': mh_mg['kotha']['inconsistency'],
        'st_kotha_classification': mh_st['kotha']['classification'],
        'st_kotha_recommendation': mh_st['kotha']['recommendation'],
        'st_kotha_rationale': mh_st['kotha']['rationale'],
        'st_kotha_indirectness': mh_st['kotha']['indirectness'],
        'st_kotha_inconsistency': mh_st['kotha']['inconsistency'],

        # MCMC convergence diagnostics
        'mc_min_ess': min_ess,
        'mc_max_rhat': max_rhat,

        # Data
        'mg_data': rv.mg_data,
        'statin_obs': rv.statin_obs,
        'statin_rct': rv.statin_rct,
        'mg_pp_rows': mg_pp_rows,
        'st_pp_rows': st_pp_rows,
    }

    # Simulation study values (Module K + T operating characteristics)
    sim = results['sim']
    metrics = sim['metrics']
    fixed_alpha = 0.3
    fixed_key = f'KOTHA alpha={fixed_alpha:.1f}'
    opt_key = f"KOTHA alpha={sim['optimal_alpha']:.1f}"
    enrolled = metrics['RCT enrolled only']
    kotha_fixed = metrics[fixed_key]
    kotha_opt = metrics[opt_key]

    def _reduction(new, base, absolute=False):
        if base == 0:
            return 0.0
        if absolute:
            return (1 - abs(new) / abs(base)) * 100
        return (1 - new / base) * 100

    sim.update({
        'sim_fixed_alpha': fixed_alpha,
        'sim_fixed_key': fixed_key,
        'sim_optimal_alpha': sim['optimal_alpha'],
        'sim_optimal_key': opt_key,
        'sim_target_bias': metrics['Target (all RCTs)']['bias'],
        'sim_target_rmse': metrics['Target (all RCTs)']['rmse'],
        'sim_target_coverage': metrics['Target (all RCTs)']['coverage'] * 100,
        'sim_target_power': metrics['Target (all RCTs)']['power'] * 100,
        'sim_enrolled_bias': enrolled['bias'],
        'sim_enrolled_rmse': enrolled['rmse'],
        'sim_enrolled_coverage': enrolled['coverage'] * 100,
        'sim_enrolled_power': enrolled['power'] * 100,
        'sim_obs_bias': metrics['Observational only']['bias'],
        'sim_obs_rmse': metrics['Observational only']['rmse'],
        'sim_obs_coverage': metrics['Observational only']['coverage'] * 100,
        'sim_obs_power': metrics['Observational only']['power'] * 100,
        'sim_kotha_fixed_bias': kotha_fixed['bias'],
        'sim_kotha_fixed_rmse': kotha_fixed['rmse'],
        'sim_kotha_fixed_coverage': kotha_fixed['coverage'] * 100,
        'sim_kotha_fixed_power': kotha_fixed['power'] * 100,
        'sim_kotha_opt_bias': kotha_opt['bias'],
        'sim_kotha_opt_rmse': kotha_opt['rmse'],
        'sim_kotha_opt_coverage': kotha_opt['coverage'] * 100,
        'sim_kotha_opt_power': kotha_opt['power'] * 100,
        'sim_rmse_reduction_fixed_pct': _reduction(kotha_fixed['rmse'], enrolled['rmse']),
        'sim_bias_reduction_fixed_pct': _reduction(kotha_fixed['bias'], enrolled['bias'], absolute=True),
        'sim_power_gain_fixed_pp': (kotha_fixed['power'] - enrolled['power']) * 100,
        'sim_rmse_reduction_opt_pct': _reduction(kotha_opt['rmse'], enrolled['rmse']),
        'sim_bias_reduction_opt_pct': _reduction(kotha_opt['bias'], enrolled['bias'], absolute=True),
        'sim_power_gain_opt_pp': (kotha_opt['power'] - enrolled['power']) * 100,
    })
    v.update(sim)
    return v


def _table_3(v):
    lines = [
        "| Study | Year | Era | Events (Mg) | N (Mg) | Events (Ctrl) | N (Ctrl) | Control rate |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, row in v['mg_data'].iterrows():
        rate = row['e_ctrl'] / row['n_ctrl'] * 100
        lines.append(
            f"| {row['study']} | {int(row['year'])} | {row['era'].capitalize()} | "
            f"{int(row['e_treat'])} | {int(row['n_treat']):,} | "
            f"{int(row['e_ctrl'])} | {int(row['n_ctrl']):,} | {rate:.1f}% |"
        )
    return "\n".join(lines)


def _table_4(v):
    lines = [
        "| Study | Design | HR (95% CI) | N | Events |",
        "|---|---|---|---|---|",
    ]
    df = pd.concat([v['statin_obs'], v['statin_rct']], ignore_index=True)
    for _, row in df.iterrows():
        hr = row['HR']
        lo = row['HR_lo']
        hi = row['HR_hi']
        lines.append(
            f"| {row['study']} | {row['design']} | "
            f"{hr:.2f} ({lo:.2f}--{hi:.2f}) | {int(row['N']):,} | {int(row['events']):,} |"
        )
    return "\n".join(lines)


def _pp_table(rows, effect_label):
    lines = [
        f"| $\\alpha$ | {effect_label} (95% CrI) | P({effect_label} < 1) | P({effect_label} < 0.90) | P({effect_label} < 0.80) |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        alpha_label = f"{r['alpha']:.1f}"
        if r['alpha'] == 0.0:
            alpha_label += ' (RCTs only)' if effect_label == 'HR' else ' (ISIS-4 only)'
        elif r['alpha'] == 1.0:
            alpha_label += ' (full weight)'
        lines.append(
            f"| {alpha_label} | {r['median']:.2f} ({r['lo']:.2f}--{r['hi']:.2f}) | "
            f"{r['p1']:.1f}% | {r['p09']:.1f}% | {r['p08']:.1f}% |"
        )
    return "\n".join(lines)


def _pp_table_combined(v):
    """Combined Bayesian integration table for both cases."""
    lines = [
        "| Case | $\\alpha$ | OR/HR (95% CrI) | P(effect < 1) | P(effect < 0.90) | P(effect < 0.80) |",
        "|---|---|---|---|---|---|",
    ]
    for mg_r, st_r in zip(v['mg_pp_rows'], v['st_pp_rows']):
        alpha = mg_r['alpha']
        alpha_label = f"{alpha:.1f}"
        if alpha == 0.0:
            alpha_label += ' (ISIS-4 / RCTs only)'
        elif alpha == 1.0:
            alpha_label += ' (full weight)'
        lines.append(
            f"| Magnesium (OR) | {alpha_label} | OR {mg_r['median']:.2f} ({mg_r['lo']:.2f}--{mg_r['hi']:.2f}) | "
            f"{mg_r['p1']:.1f}% | {mg_r['p09']:.1f}% | {mg_r['p08']:.1f}% |"
        )
        lines.append(
            f"| Statins (HR) | {alpha_label} | HR {st_r['median']:.2f} ({st_r['lo']:.2f}--{st_r['hi']:.2f}) | "
            f"{st_r['p1']:.1f}% | {st_r['p09']:.1f}% | {st_r['p08']:.1f}% |"
        )
    return "\n".join(lines)


def _table_7(v):
    mg_i2 = int(round(v['mg_all_i2']))
    st_i2_obs = int(round(v['st_obs_i2']))
    st_i2_rct = int(round(v['st_rct_i2']))
    mg_reduction = int(round(v['mg_rate_reduction_pct']))
    st_reduction = int(round(v['st_rate_reduction_pct']))
    mg_rec = v.get('mg_kotha_recommendation', '"Inconclusive; conditional recommendation"')
    st_rec = v.get('st_kotha_recommendation', '"Inconclusive; conditional recommendation"')
    mg_indirect = v.get('mg_kotha_indirectness', 'moderate').capitalize()
    st_indirect = v.get('st_kotha_indirectness', 'serious').capitalize()
    lines = [
        "| GRADE domain | Standard (Mg in AMI) | KOTHA (Mg in AMI) | Standard (Statins HF) | KOTHA (Statins HF) |",
        "|---|---|---|---|---|",
        f"| Risk of bias | Low | Low | Low | Low |",
        f"| Inconsistency | High ($I^2$ = {mg_i2}%) | High ($I^2$ = {mg_i2}%) | Low ($I^2$ = {st_i2_rct}%) | Low ($I^2$ = {st_i2_rct}%) |",
        f"| Indirectness | Not assessed | {mg_indirect}: event rate decreased by {mg_reduction}% | Not assessed | {st_indirect}: event rate decreased by {st_reduction}% |",
        f"| Imprecision | Not serious (OIS met) | Not serious (OIS met, CI excludes null) | Not serious (OIS met, CI excludes clinically important benefit) | Not serious (OIS met, CI excludes clinically important benefit) |",
        f"| Overall certainty | Low | Low | High | Low |",
        f"| Recommendation | \"No benefit demonstrated\" | \"{mg_rec}\" | \"No benefit demonstrated\" | \"{st_rec}\" |",
    ]
    return "\n".join(lines)


def _simulation_table(v):
    def _row(label, bias, rmse, coverage, power):
        return (
            f"| {label} | {bias:+.3f} | {rmse:.3f} | "
            f"{coverage:.1f}% | {power:.1f}% |"
        )
    lines = [
        "| Estimator | Bias (log-OR) | RMSE (log-OR) | 95% coverage | Power |",
        "|---|---|---|---|---|",
        _row(
            "Target (all RCTs)",
            v['sim_target_bias'], v['sim_target_rmse'],
            v['sim_target_coverage'], v['sim_target_power'],
        ),
        _row(
            "RCT-enrolled only",
            v['sim_enrolled_bias'], v['sim_enrolled_rmse'],
            v['sim_enrolled_coverage'], v['sim_enrolled_power'],
        ),
        _row(
            "Observational only",
            v['sim_obs_bias'], v['sim_obs_rmse'],
            v['sim_obs_coverage'], v['sim_obs_power'],
        ),
        _row(
            f"KOTHA (fixed α = {v['sim_fixed_alpha']:.1f})",
            v['sim_kotha_fixed_bias'], v['sim_kotha_fixed_rmse'],
            v['sim_kotha_fixed_coverage'], v['sim_kotha_fixed_power'],
        ),
        _row(
            f"KOTHA (RMSE-optimal α = {v['sim_optimal_alpha']:.1f})",
            v['sim_kotha_opt_bias'], v['sim_kotha_opt_rmse'],
            v['sim_kotha_opt_coverage'], v['sim_kotha_opt_power'],
        ),
    ]
    return "\n".join(lines)


def _section_abstract_results(v):
    return (
        "**Results**: In the magnesium case, control event rates declined from "
        f"{v['s1_rate']*100:.1f}% (pre-thrombolysis era) to {v['s2_rate']*100:.1f}% (ISIS-4), "
        "reflecting temporal event dilution. The pre-ISIS-4 meta-analysis yielded "
        f"OR = {v['mg_pre_or']:.2f} (95% CI: {v['mg_pre_lo']:.2f}--{v['mg_pre_hi']:.2f}), "
        f"while the all-trials estimate was OR = {v['mg_all_or']:.2f} "
        f"({v['mg_all_lo']:.2f}--{v['mg_all_hi']:.2f}) with $I^2$ = {int(round(v['mg_all_i2']))}%. "
        "Bayesian integration with power prior discounting ($\\alpha$ = "
        f"{v['alpha_example']:.1f}) yielded OR = {v['mg_pp_alpha3_or']:.2f} "
        f"(95% CrI: {v['mg_pp_alpha3_lo']:.2f}--{v['mg_pp_alpha3_hi']:.2f}), "
        f"P(OR < 1) = {v['mg_pp_alpha3_p1']:.0f}%. In the statins case, observational studies showed "
        f"HR = {v['st_obs_hr']:.2f} ({v['st_obs_lo']:.2f}--{v['st_obs_hi']:.2f}) while RCTs showed "
        f"HR = {v['st_rct_hr']:.2f} ({v['st_rct_lo']:.2f}--{v['st_rct_hi']:.2f}), "
        f"with event rate ratio of {v['st_rate_ratio']:.2f} (RCT/observational). "
        "Module H classified magnesium as "
        f"{v['mg_kotha_classification'].lower()} and statins as {v['st_kotha_classification'].lower()}, "
        "whereas standard GRADE evaluation would be more likely to conclude \"no benefit demonstrated.\""
    )


def _section_empirical_illustration(v):
    parts = [
        "## Empirical illustration",
        "",
        "### Illustrative case selection",
        "",
        "To illustrate the KOTHA Framework, we applied all three modules to two well-documented cases "
        "where observational evidence and RCT evidence diverged, and where the reasons for divergence "
        "have been extensively discussed in the literature.",
        "",
        "**Case 1: Intravenous magnesium in acute myocardial infarction (AMI)**. Between "
        f"{v['mg_year_min']} and {v['mg_year_max']}, multiple small RCTs suggested that intravenous "
        "magnesium reduced mortality in AMI (pooled OR approximately "
        f"{v['mg_pre_or']:.2f}). The large ISIS-4 trial (N = {v['N_isis4']:,}) found no benefit "
        "(OR approximately 1.05). This discordance has been attributed to temporal changes in background "
        "therapy (introduction of thrombolysis), which reduced control-group event rates and potentially "
        "diluted the treatment effect [18, 19].",
        "",
        "**Case 2: Statins in heart failure (HF)**. Observational cohort studies consistently reported "
        f"reduced mortality with statin use (pooled HR approximately {v['st_obs_hr']:.2f}), whereas "
        "the two largest RCTs in this population---CORONA and GISSI-HF---found no significant benefit "
        f"(pooled HR approximately {v['st_rct_hr']:.2f}). This discrepancy has been attributed to "
        "differences between RCT-enrolled and real-world patient populations, with RCT participants having "
        "lower baseline risk [20, 21].",
        "",
        "### Data sources",
        "",
        "**Table 3: Study-level data for magnesium in AMI**",
        "",
        _table_3(v),
        "",
        "**Table 4: Study-level data for statins in heart failure**",
        "",
        _table_4(v),
        "",
        "### Module K results",
        "",
        "#### Magnesium in AMI",
        "",
        "Control-group event rates were computed for each era:",
        "",
        f"- Pre-thrombolysis era ({v['mg_year_min']}--1990): weighted mean = {v['s1_rate']*100:.1f}%",
        f"- ISIS-4 (1995): {v['s2_rate']*100:.1f}%",
        f"- LIMIT-2 (1992): {v['s3_rate']*100:.1f}%",
        "",
        f"The event rate ratio (ISIS-4 / pre-thrombolysis) was {v['mg_rate_ratio']:.2f}, indicating a "
        f"{v['mg_rate_reduction_pct']:.0f}% reduction in control event rates in the thrombolysis era (Fig. 2).",
        "",
        "Random-effects meta-analysis yielded:",
        "",
        f"- **Pre-ISIS-4 trials** (11 trials): OR = {v['mg_pre_or']:.2f} (95% CI: {v['mg_pre_lo']:.2f}--{v['mg_pre_hi']:.2f}), $I^2$ = {int(round(v['mg_pre_i2']))}%",
        f"- **All trials** (12 trials): OR = {v['mg_all_or']:.2f} (95% CI: {v['mg_all_lo']:.2f}--{v['mg_all_hi']:.2f}), $I^2$ = {int(round(v['mg_all_i2']))}%",
        "",
        f"Power analysis at the ISIS-4 sample size (N = {v['N_isis4']:,}) showed that for the pre-ISIS-4 "
        f"pooled effect (OR = {v['true_or']:.2f}), power exceeded 99% under all scenarios---the ISIS-4 trial "
        "was sufficiently large to detect an effect of this magnitude regardless of event rate. However, for "
        "more modest effects (OR = 0.85--0.95), the event rate reduction produced meaningful power differences "
        "between scenarios (Fig. 3A). At OR = 0.90, power was "
        f"{v['mg_power_s1_or090']:.1f}% under the pre-thrombolysis rate (S1) but "
        f"{v['mg_power_s2_or090']:.1f}% under the ISIS-4 rate (S2).",
        "",
        "#### Statins in heart failure",
        "",
        "Random-effects meta-analysis yielded:",
        "",
        f"- **Observational studies**: HR = {v['st_obs_hr']:.2f} (95% CI: {v['st_obs_lo']:.2f}--{v['st_obs_hi']:.2f}), $I^2$ = {int(round(v['st_obs_i2']))}%",
        f"- **RCTs**: HR = {v['st_rct_hr']:.2f} (95% CI: {v['st_rct_lo']:.2f}--{v['st_rct_hi']:.2f}), $I^2$ = {int(round(v['st_rct_i2']))}%",
        "",
        f"The event rate ratio (RCT / observational) was estimated at {v['st_rate_ratio']:.2f}, indicating that "
        "RCT populations had approximately half the event rate of observational cohorts.",
        "",
        f"Power analysis at the combined RCT sample size (N = {v['N_statin_rct']:,}) revealed substantial "
        "power differences (Fig. 3B). At the observational effect estimate (HR = {st_true_hr:.2f}), power was "
        f">99% under the observational event rate ({v['obs_rate']*100:.0f}%) but {v['st_power_s2_true']:.1f}% under "
        f"the RCT event rate ({v['rct_rate']*100:.0f}%). At more modest effects (HR = 0.85), power was "
        f"{v['st_power_s1_hr085']:.1f}% under the observational rate but only {v['st_power_s2_hr085']:.1f}% under "
        "the RCT rate---a {power_drop:.0f} percentage-point reduction attributable to event dilution.".format(
            st_true_hr=v['st_true_hr'],
            power_drop=v['st_power_s1_hr085'] - v['st_power_s2_hr085'],
        ),
        "",
        "### Module T results",
        "",
        "#### Bayesian integration --- Magnesium in AMI",
        "",
        "**Table 5: Bayesian integration --- Magnesium in AMI (power prior)**",
        "",
        _pp_table(v['mg_pp_rows'], 'OR'),
        "",
        f"At $\\alpha$ = 0 (ISIS-4 only), the posterior median OR was {v['mg_pp_alpha0_or']:.2f} with only "
        f"{v['mg_pp_alpha0_p1']:.1f}% probability of benefit. As $\\alpha$ increased, incorporating pre-ISIS-4 "
        "evidence progressively shifted the posterior toward benefit. At $\\alpha$ = 0.3 (moderate discounting), "
        f"the posterior OR was {v['mg_pp_alpha3_or']:.2f} with {v['mg_pp_alpha3_p1']:.0f}% probability of benefit. "
        "The sensitivity analysis demonstrates that conclusions about magnesium efficacy depend critically on the "
        "weight assigned to pre-ISIS-4 evidence (Fig. 5A).",
        "",
        "#### Bayesian integration --- Statins in HF",
        "",
        "**Table 6: Bayesian integration --- Statins in HF (power prior)**",
        "",
        _pp_table(v['st_pp_rows'], 'HR'),
        "",
        f"At $\\alpha$ = 0 (RCTs only), the posterior probability of any benefit was only "
        f"{v['st_pp_alpha0_p1']:.1f}%, and the probability of clinically meaningful benefit (HR < 0.90) was "
        f"{v['st_pp_alpha0_p09']:.1f}%. Even modest incorporation of observational evidence ($\\alpha$ = 0.3) "
        f"increased P(HR < 1) to {v['st_pp_alpha3_p1']:.1f}% and P(HR < 0.90) to {v['st_pp_alpha3_p09']:.1f}%. "
        "The sensitivity analysis (Fig. 5B) shows a monotonic increase in posterior probability of benefit with "
        "increasing $\\alpha$, but conclusions remain uncertain across the full range of discounting.",
        "",
        "### Module H results",
        "",
        "#### Magnesium in AMI",
        "",
        f"**Assessment 1 (Information sufficiency)**: The OIS for detecting OR = {v['true_or']:.2f} at $\\alpha$ = 0.05 "
        f"with 80% power was {v['mg_ois']} events. The total events across all 12 trials were {v['mg_total_events']:,} "
        f"(information fraction = {v['mg_info_frac']:.0f}%). By this criterion, the meta-analysis was informationally "
        "sufficient. However, this assessment assumes the pre-ISIS-4 effect estimate is the true effect; if the true "
        f"effect is more modest (e.g., OR = 0.75), the OIS would be {v['mg_ois_075']} events, still exceeded by the available evidence.",
        "",
        f"**Assessment 2 (CI assessment)**: The all-trials pooled OR = {v['mg_all_or']:.2f} (95% CI: "
        f"{v['mg_all_lo']:.2f}--{v['mg_all_hi']:.2f}) excluded 1.0, suggesting benefit. However, the high $I^2$ "
        f"({int(round(v['mg_all_i2']))}%) indicates substantial heterogeneity driven by the ISIS-4 result.",
        "",
        f"**Assessment 3 (Representativeness)**: The event rate ratio (ISIS-4 / pre-thrombolysis) was "
        f"{v['mg_rate_ratio']:.2f}. While this does not exceed the 1.5 threshold for serious indirectness, it reflects a "
        "temporal shift in background therapy rather than enrollment-driven event dilution per se.",
        "",
        "**Assessment 4 (TSA)**: We present the cumulative Z-curve using both fixed-effect and random-effects "
        "accumulation because the two models give different results in this case. Under a fixed-effect accumulation, "
        f"the Z-statistic reached significance after the early small trials but was pulled back to {v['mg_z_fe']:.2f} by "
        f"ISIS-4 (below the conventional boundary of {v['mg_z_alpha']:.2f}). Under a random-effects accumulation---the same "
        "model used for the pooled all-trials estimate---the final Z was "
        f"{v['mg_z_re']:.2f}, crossing the O'Brien-Fleming boundary, which because the cumulative information exceeded the optimal information size equals the conventional boundary ({v['mg_obf']:.2f}). This divergence "
        f"is a direct consequence of the high between-study heterogeneity ($I^2$ = {int(round(v['mg_all_i2']))}%) driven by "
        "the ISIS-4 result; it underscores that the magnesium evidence base contains a genuine shift in treatment effect "
        "across eras and should not be summarized by a single pooled estimate.",
        "",
        "#### Statins in heart failure",
        "",
        f"**Assessment 1 (Information sufficiency)**: The OIS for detecting HR = {v['st_true_hr']:.2f} at $\\alpha$ = 0.05 "
        f"with 80% power was {v['st_ois']} events. The total RCT events were {v['st_total_events']:,} "
        f"(information fraction = {v['st_info_frac']:.0f}%). The RCT evidence was informationally sufficient for the "
        "observational effect estimate.",
        "",
        f"**Assessment 2 (CI assessment)**: The RCT pooled HR = {v['st_rct_hr']:.2f} (95% CI: "
        f"{v['st_rct_lo']:.2f}--{v['st_rct_hi']:.2f}) included 1.0 but excluded 0.80, suggesting that a large benefit is "
        "unlikely based on RCT evidence alone.",
        "",
        f"**Assessment 3 (Representativeness)**: The event rate ratio (RCT / observational) was {v['st_rate_ratio']:.2f}, "
        "well below the 0.67 threshold. **Classification: serious indirectness.** The RCT populations had substantially "
        "lower event rates than the observational cohorts, consistent with selection of lower-risk patients.",
        "",
        f"**Assessment 4 (TSA)**: With an information fraction of {v['st_info_frac']:.0f}%, the RCT evidence reached the OIS. "
        f"The cumulative Z-statistic did not cross the efficacy boundary. Because the futility boundary was also not "
        "crossed, the appropriate TSA conclusion is **inconclusive** rather than evidence of no benefit at the "
        "RCT-enrolled risk level.",
        "",
        "#### Comparative GRADE assessment",
        "",
        "Fig. 8 presents the comparative GRADE assessment for both cases under standard and KOTHA-enhanced evaluation.",
        "",
        "**Table 7: Module H assessment --- Standard GRADE vs. KOTHA-enhanced**",
        "",
        _table_7(v),
        "",
        "The key difference is in the **indirectness** domain: standard GRADE assessment does not typically evaluate "
        "whether enrollment-driven event dilution has reduced the informativeness of the evidence. KOTHA-enhanced "
        "assessment explicitly quantifies this through the event rate ratio and adjusts the certainty rating accordingly.",
    ]
    return "\n".join(parts)


def _section_principal_findings(v):
    return (
        "### Principal findings\n\n"
        "The KOTHA Framework was illustrated using two canonical cases of observational-RCT divergence. "
        "In both cases, the framework identified structural features---temporal event dilution (magnesium) and "
        "population risk-profile differences (statins)---that contributed to the apparent discordance between "
        "observational and RCT evidence.\n\n"
        f"For the magnesium case, Module K demonstrated that the shift from pre-thrombolysis to thrombolysis-era "
        "background therapy reduced control event rates by "
        f"{v['mg_rate_reduction_pct']:.0f}%, though the ISIS-4 trial was sufficiently powered to detect the large effect "
        "suggested by earlier trials. The divergence in this case is more attributable to heterogeneity across eras "
        f"(reflected in $I^2$ = {int(round(v['mg_all_i2']))}%) than to simple underpowering. Module T showed that the "
        "posterior estimate depends critically on the weight assigned to pre-ISIS-4 evidence, with the discounting "
        "parameter $\\alpha$ serving as a transparent sensitivity parameter.\n\n"
        f"For the statins case, Module K revealed a more dramatic event dilution: RCT populations had approximately "
        f"half the event rate of observational cohorts (ratio = {v['st_rate_ratio']:.2f}). At the observational effect "
        f"estimate (HR = {v['st_obs_hr']:.2f}), the RCTs had adequate power, but at more modest effects (HR = 0.85), "
        f"power under the RCT event rate dropped to {v['st_power_s2_hr085']:.0f}% compared with {v['st_power_s1_hr085']:.0f}% "
        "under the observational rate. Module T demonstrated that even modest incorporation of observational evidence "
        f"($\\alpha$ = 0.3) shifted the posterior substantially toward benefit."
    )


def build():
    _run_validation()
    v = _compute_values()

    with open(os.path.join(BASE, 'paper_template.md'), 'r') as f:
        template = f.read()

    replacements = {
        '<!-- DYNAMIC: ABSTRACT_RESULTS -->': _section_abstract_results(v),
        '<!-- DYNAMIC: EMPIRICAL_ILLUSTRATION -->': _section_empirical_illustration(v),
        '<!-- DYNAMIC: PRINCIPAL_FINDINGS -->': _section_principal_findings(v),
    }

    for marker, content in replacements.items():
        if marker not in template:
            raise RuntimeError(f"Marker not found in paper_template.md: {marker}")
        template = template.replace(marker, content)

    # Replace any remaining sample-size placeholders in static figure captions / methods
    template = template.replace('<<N_ISIS4>>', f"{v['N_isis4']:,}")
    template = template.replace('<<N_STATIN_RCT>>', f"{v['N_statin_rct']:,}")
    template = template.replace('<<OIS_075>>', str(v['mg_ois_075']))
    template = template.replace('<<MG_N_TRIALS>>', str(v['mg_n_trials']))
    template = template.replace('<<MG_YEAR_MIN>>', str(v['mg_year_min']))
    template = template.replace('<<MG_YEAR_MAX>>', str(v['mg_year_max']))
    template = template.replace('<<ST_N_OBS>>', str(v['st_n_obs']))
    template = template.replace('<<ST_N_RCT>>', str(v['st_n_rct']))

    out_md = os.path.join(BASE, '04_paper_rsm.md')
    with open(out_md, 'w') as f:
        f.write(template)
    print(f"Wrote {out_md}")

    # Regenerate docx
    subprocess.run(
        [sys.executable, os.path.join(BASE, 'generate_rsm_docx_final.py')],
        cwd=BASE,
        check=True,
    )


if __name__ == '__main__':
    build()
