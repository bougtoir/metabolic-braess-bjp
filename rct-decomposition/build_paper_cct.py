#!/usr/bin/env python3
"""
Build the KOTHA manuscript for Contemporary Clinical Trials Communications (CCTC).

Outputs:
- 05_paper_cctc.md (generated from computed results)
- KOTHA_Framework_CCTC.docx (via generate_cct_docx.py)
"""
import io
import os
import re
import subprocess
import sys

import build_paper as bp

BASE = os.path.dirname(os.path.abspath(__file__))


def _run_validation():
    """Ensure figures and results_summary.txt are up to date."""
    subprocess.run(
        [sys.executable, os.path.join(BASE, 'validation', 'run_validation.py')],
        cwd=BASE,
        check=True,
    )


class RefManager:
    """Minimal Vancouver-style reference manager."""
    def __init__(self, refs):
        # refs: list of (key, citation_string) in planned order of first appearance
        self.refs = {key: (i + 1, text) for i, (key, text) in enumerate(refs)}
        self.used = set()

    def __call__(self, *keys):
        nums = []
        for k in keys:
            if k not in self.refs:
                raise KeyError(f"Unknown reference key: {k}")
            num, _ = self.refs[k]
            self.used.add(num)
            nums.append(num)
        return self._fmt(nums)

    def _fmt(self, nums):
        if not nums:
            return ''
        # collapse consecutive numbers to ranges
        nums = sorted(set(nums))
        parts = []
        start = prev = nums[0]
        for n in nums[1:] + [None]:
            if n == prev + 1:
                prev = n
                continue
            if start == prev:
                parts.append(str(start))
            else:
                parts.append(f"{start}-{prev}")
            if n is not None:
                start = prev = n
        return f"[{','.join(parts)}]"

    def group(self, *keys):
        # return bracket with numbers in the order requested (no collapse)
        nums = [self.refs[k][0] for k in keys]
        for k in keys:
            self.used.add(self.refs[k][0])
        return f"[{','.join(str(n) for n in nums)}]"

    def bibliography(self):
        out = []
        for key, (num, text) in sorted(self.refs.items(), key=lambda x: x[1][0]):
            out.append(f"{num}. {text}")
        return '\n'.join(out)


# Reference list in planned order of first appearance
REFS = [
    ('GRADE', 'Guyatt GH, Oxman AD, Vist GE, et al. GRADE: an emerging consensus on rating quality of evidence and strength of recommendations. BMJ 2008; 336(7650): 924-6.'),
    ('Concato', 'Concato J, Shah N and Horwitz RI. Randomized, controlled trials, observational studies, and the hierarchy of research designs. N Engl J Med 2000; 342(25): 1887-92.'),
    ('Anglemyer', 'Anglemyer A, Horvath HT and Bero L. Healthcare outcomes assessed with observational study designs compared with those assessed in randomized trials. Cochrane Database Syst Rev 2014; (4): MR000034.'),
    ('KennedyMartin', 'Kennedy-Martin T, Curtis S, Faries D, et al. A literature review on the representativeness of randomized controlled trial samples and implications for the external validity of trial results. Trials 2015; 16: 495.'),
    ('Rothwell', 'Rothwell PM. External validity of randomised controlled trials: "to whom do the results of this trial apply?" Lancet 2005; 365(9453): 82-93.'),
    ('Pogue', 'Pogue JM and Yusuf S. Cumulating evidence from randomized trials: utilizing sequential monitoring boundaries for cumulative meta-analysis. Control Clin Trials 1997; 18(6): 580-93.'),
    ('Wetterslev', 'Wetterslev J, Thorlund K, Brok J, et al. Estimating required information size by quantifying diversity in random-effects model meta-analyses. BMC Med Res Methodol 2009; 9: 86.'),
    ('Brok', 'Brok J, Thorlund K, Gluud C, et al. Trial sequential analysis reveals insufficient information size and potentially false positive results in many meta-analyses. J Clin Epidemiol 2008; 61(8): 763-9.'),
    ('TSAManual', 'Thorlund K, Engstrom J, Wetterslev J, et al. User manual for trial sequential analysis (TSA). Copenhagen Trial Unit, Centre for Clinical Intervention Research; 2011.'),
    ('ADEMP', 'Morris TP, White IR and Crowther MJ. Using simulation studies to evaluate statistical methods. Stat Med 2019; 38(11): 2074-102.'),
    ('Schoenfeld', 'Schoenfeld DA. Sample-size formula for the proportional-hazards regression model. Biometrics 1983; 39(2): 499-503.'),
    ('Ibrahim', 'Ibrahim JG and Chen MH. Power prior distributions for regression models. Stat Sci 2000; 15(1): 46-60.'),
    ('RMST', 'McCaw ZR, Yin G and Wei LJ. Using the restricted mean survival time difference as an alternative to the hazard ratio for analyzing clinical cardiovascular studies. Circulation 2019; 140(17): 1366-8. doi:10.1161/CIRCULATIONAHA.119.040680.'),
    ('Boyd', 'Boyd AP, Kittelson JM and Gillen DL. Estimation of treatment effect under non-proportional hazards and conditionally independent censoring. Stat Med 2012; 31(28): 3504-15. doi:10.1002/sim.5440.'),
    ('Sherry', 'Sherry AD, Msaouel P, Kupferman GS, et al. Evidence-based prior for estimating the treatment effect of phase III randomized trials in oncology. JCO Precis Oncol 2024; 8: e2400363. doi:10.1200/PO.24.00363.'),
    ('emcee', 'Foreman-Mackey D, Hogg DW, Lang D, et al. emcee: the MCMC hammer. Publ Astron Soc Pac 2013; 125(925): 306-12.'),
    ('Teo', 'Teo KK, Yusuf S, Collins R, et al. Effects of intravenous magnesium in suspected acute myocardial infarction: overview of randomised trials. BMJ 1991; 303(6816): 1499-503.'),
    ('Li', 'Li J, Zhang Q, Zhang M, et al. Intravenous magnesium for acute myocardial infarction. Cochrane Database Syst Rev 2007; (2): CD002755.'),
    ('Anker', 'Anker SD, Clark AL, Winkler R, et al. Statin use and survival in patients with chronic heart failure -- results from two observational studies with 5200 patients. Int J Cardiol 2006; 112(2): 234-42.'),
    ('Mozaffarian', 'Mozaffarian D, Nye R and Levy WC. Statin therapy is associated with lower mortality among patients with severe heart failure. Am J Cardiol 2004; 93(9): 1124-9.'),
    ('Horwich', 'Horwich TB, MacLellan WR and Fonarow GC. Statin therapy is associated with improved survival in ischemic and non-ischemic heart failure. J Am Coll Cardiol 2004; 43(4): 642-8.'),
    ('Go', 'Go AS, Lee WY, Yang J, et al. Statin therapy and risks for death and hospitalization in chronic heart failure. JAMA 2006; 296(17): 2105-11.'),
    ('Foody', 'Foody JM, Shah R, Galusha D, et al. Statins and mortality among elderly patients hospitalized with heart failure. Circulation 2006; 113(8): 1086-92.'),
    ('CORONA', 'Kjekshus J, Apetrei E, Barrios V, et al. Rosuvastatin in older patients with systolic heart failure. N Engl J Med 2007; 357(22): 2248-61.'),
    ('GISSI', 'GISSI-HF Investigators. Effect of rosuvastatin in patients with chronic heart failure (the GISSI-HF trial): a randomised, double-blind, placebo-controlled trial. Lancet 2008; 372(9645): 1231-9.'),
    ('DerSimonianLaird', 'DerSimonian R and Laird N. Meta-analysis in clinical trials. Control Clin Trials 1986; 7(3): 177-88.'),
    ('HernanTTE1', 'Hernan MA and Robins JM. Using big data to emulate a target trial when a randomized trial is not available. Am J Epidemiol 2016; 183(8): 758-64.'),
    ('HernanTTE2', 'Hernan MA, Wang W and Leaf DE. Target trial emulation: a framework for causal inference from observational data. JAMA 2022; 328(24): 2446-7.'),
    ('Schmidli', 'Schmidli H, Gsteiger S, Roychoudhury S, et al. Robust meta-analytic-predictive priors in clinical trials with historical control information. Biometrics 2014; 70(4): 1023-32.'),
    ('Verde', 'Verde PE and Ohmann C. Combining randomized and non-randomized evidence in clinical research: a review of methods and applications. Res Synth Methods 2015; 6(1): 45-62.'),
    ('Efthimiou', 'Efthimiou O, Mavridis D, Debray TPA, et al. Combining randomized and non-randomized evidence in network meta-analysis. Stat Med 2017; 36(8): 1210-26.'),
]


def _front_matter(v, word_count):
    return f"""---
running_head: KOTHA Framework for Information Loss
title: The KOTHA Framework: A Simulation-Based Approach to Quantifying and Correcting Structural Information Loss in Randomized Controlled Trial Meta-Analyses
authors: [To be determined]
affiliations: [To be determined]
word_count: {word_count}
corresponding_author: [To be determined]
corresponding_author_address: [To be determined]
---
"""


def _build_markdown():
    _run_validation()
    v = bp._compute_values()
    r = RefManager(REFS)

    # Abstract numbers
    mg_pre_or = v['mg_pre_or']
    mg_pre_lo = v['mg_pre_lo']
    mg_pre_hi = v['mg_pre_hi']
    mg_all_or = v['mg_all_or']
    mg_all_lo = v['mg_all_lo']
    mg_all_hi = v['mg_all_hi']
    mg_all_i2 = int(round(v['mg_all_i2']))
    st_obs_hr = v['st_obs_hr']
    st_obs_lo = v['st_obs_lo']
    st_obs_hi = v['st_obs_hi']
    st_rct_hr = v['st_rct_hr']
    st_rct_lo = v['st_rct_lo']
    st_rct_hi = v['st_rct_hi']

    abstract = f"""**Background/Aims**: Evidence-based medicine places RCTs and meta-analyses at the top of the evidence hierarchy, yet when observational and RCT evidence disagree the usual explanation is residual confounding. We highlight a structural explanation: trial enrollment progressively excludes higher-risk patients, diluting event rates and statistical information. The Knowledge-driven Observational-Trial Harmonization Approach (KOTHA) Framework diagnoses this structural information loss. We aimed to develop and illustrate KOTHA so that trialists can distinguish structural information loss from residual confounding and inform sample size, eligibility, enrichment, and endpoint decisions in prospective trial design.

**Methods**: KOTHA comprises three modules: Module K quantifies risk-profile shifts and power loss, Module T combines RCT and observational evidence with power-prior discounting, and Module H translates outputs into a GRADE-compatible assessment. We applied it to magnesium in acute myocardial infarction and statins in heart failure.

**Results**: In the magnesium case, control event rates fell from {v['s1_rate']*100:.1f}% to {v['s2_rate']*100:.1f}%; the pre-ISIS-4 pooled odds ratio (OR) was {mg_pre_or:.2f} (95% CI: {mg_pre_lo:.2f}-{mg_pre_hi:.2f}) and the all-trials estimate {mg_all_or:.2f} ({mg_all_lo:.2f}-{mg_all_hi:.2f}) with $I^2$ = {mg_all_i2}%. In the statins case, observational hazard ratio (HR) was {st_obs_hr:.2f} ({st_obs_lo:.2f}-{st_obs_hi:.2f}) versus RCT HR {st_rct_hr:.2f} ({st_rct_lo:.2f}-{st_rct_hi:.2f}), with an event-rate ratio of {v['st_rate_ratio']:.2f}. Bayesian integration (alpha = {v['alpha_example']:.1f}) yielded OR {v['mg_pp_alpha3_or']:.2f} (CrI {v['mg_pp_alpha3_lo']:.2f}-{v['mg_pp_alpha3_hi']:.2f}), P(OR < 1) = {v['mg_pp_alpha3_p1']:.1f}% for magnesium and HR {v['st_pp_alpha3_hr']:.2f} ({v['st_pp_alpha3_lo']:.2f}-{v['st_pp_alpha3_hi']:.2f}), P(HR < 1) = {v['st_pp_alpha3_p1']:.1f}% for statins; both probabilities remained below conventional decision thresholds, leaving conclusions uncertain.

**Conclusions**: KOTHA distinguishes "evidence of no effect" from "no evidence of effect". Module H classified magnesium as {v['mg_kotha_classification'].lower()}, and statins as {v['st_kotha_classification'].lower()}."""
    intro = f"""Evidence-based medicine places RCTs and their meta-analyses at the apex of the evidence hierarchy because randomization minimizes confounding and provides internally valid estimates of treatment effects {r('GRADE')}. Nevertheless, meta-analyses of observational studies and RCTs frequently disagree: observational evidence may show statistically significant benefit while RCT evidence does not {r('Concato', 'Anglemyer')}. The conventional explanation invokes residual confounding, selection bias, or publication bias in observational data. While these sources of bias are real, they may not fully account for the discordance.

An alternative structural explanation deserves systematic attention. RCT enrollment criteria, consent processes, and site selection progressively restrict the study population {r('KennedyMartin', 'Rothwell')}. Because clinical events are concentrated in the highest-risk patients---those with comorbidities, advanced disease, or organ dysfunction---their exclusion lowers event rates in the enrolled cohort. If trial protocols do not compensate by increasing sample size, extending follow-up, or enriching high-risk enrollment, the resulting evidence base can become informationally insufficient. We call this phenomenon **structural information loss**, a five-step causal chain: representativeness loss; event concentration in excluded populations; inadequate design compensation; systematic underpowering; and, ultimately, distorted recommendations when "no statistically significant difference" is interpreted as "no effect".

The concepts of optimal information size (OIS) and trial sequential analysis (TSA) provide partial remedies. OIS recognizes that meta-analyses, like individual trials, require a minimum information size to reach reliable conclusions {r('Pogue', 'Wetterslev')}. TSA applies sequential monitoring boundaries to cumulative meta-analysis, distinguishing evidence of no effect (futility boundary crossed) from no evidence of effect (boundary not crossed) {r('Brok', 'TSAManual')}. Both are underused in guideline development, however, and neither directly quantifies the information loss produced by enrollment-driven risk-profile shifts.

Several trial design strategies can mitigate event dilution (Table 1), including stratified randomization, prognostic enrichment, event-driven designs, adaptive sample-size re-estimation, and pragmatic or registry-based trials. Existing approaches address these issues separately; to our knowledge, no widely adopted framework tightly links prospective power assessment, retrospective diagnostic evaluation, and structured evidence interpretation in a single reproducible workflow for completed or planned RCTs.

To address this gap we developed the Knowledge-driven Observational-Trial Harmonization Approach (KOTHA). The framework has three modules: Module K diagnoses structural information loss through counterfactual power simulation; Module T integrates discordant evidence through hierarchical Bayesian meta-analysis; and Module H translates quantitative findings into a GRADE-compatible evidence assessment. We describe the framework here and illustrate it with two canonical cases of observational-RCT divergence, focusing on implications for clinical trial design."""

    methods = f"""### Overview

The KOTHA Framework comprises three interconnected modules (Fig. 1). Module K (Counterfactual Power Simulation) quantifies how enrollment-driven risk-profile shifts reduce statistical power. Module T (Trial-Observational Bayesian Integration) combines RCT and observational evidence with explicit discounting for design-related bias. Module H (Guideline Interpreter) translates module outputs into a structured GRADE assessment. Each module can be used independently, but the framework is most informative when applied in sequence.

### Module K: Counterfactual power simulation

Module K asks: if the RCTs in a meta-analysis had enrolled patients with the risk profile of the real-world target population, would the combined evidence have been sufficient to detect the effect suggested by observational studies? The simulation component follows the ADEMP reporting structure {r('ADEMP')}: aims (quantify information loss from enrollment-driven risk-profile shifts), data-generating process (published aggregate event counts and sample sizes), estimands (counterfactual power under S1-S3), methods (Schoenfeld approximation with proportional-hazards data handled via the log-HR/log-OR equivalence under rare events), and performance measures (power across a grid of true effects and required sample size).

We define three enrollment scenarios: S1 (real-world target population, approximated by a representative retrospective cohort or published aggregate event rates); S2 (RCT-enrolled equivalent, defined by applying published eligibility criteria to the retrospective cohort or using observed RCT event rates); and S3 (design-optimized, incorporating prognostic enrichment).

For each scenario, we compute the expected control event rate $p_c$ and treatment event rate $p_t = (p_c \\cdot \\text{{OR}}) / (1 - p_c + p_c \\cdot \\text{{OR}})$. The total expected number of events is $D = N(p_c + p_t)/2$ for a trial of $N$ patients randomized 1:1. Under the Schoenfeld approximation {r('Schoenfeld')}, the standard error of the log relative effect (log-OR or log-HR under proportional hazards) is approximately $2/\\sqrt{{D}}$, yielding the power function

$$\\text{{Power}} = \\Phi\\left( |\\log(\\text{{OR or HR}})| \\cdot \\sqrt{{D}} / 2 - z_{{\\alpha/2}} \\right)$$

where $\\Phi$ is the standard normal cumulative distribution function. The ratio $\\rho = p_c^{{(S2)}} / p_c^{{(S1)}}$ quantifies event dilution. Module K reports power across a grid of assumed true effects and computes the sample size required to reach 80% power under each scenario. For the statins case, which reports hazard ratios, the hazard ratio is approximated by an odds ratio under the rare-event assumption and crude control event proportions derived from the aggregate data are used as approximate event probabilities; this comparison is intended to illustrate the relative power loss across enrollment scenarios rather than to provide exact sample-size estimates for a specific follow-up duration.

### Module T: Hierarchical Bayesian evidence integration

When Module K indicates that RCT evidence is informationally insufficient, Module T combines RCT and observational evidence while discounting the observational likelihood for potential design-specific bias. Let $y_i$ denote the reported log effect size from study $i$ with standard error $s_i$. The RCT evidence contributes its full likelihood; the observational evidence contributes a power-prior-discounted likelihood with factor $\\alpha \\in [0, 1]$ {r('Ibrahim')}, so that $\\alpha = 0$ retains only RCTs and $\\alpha = 1$ gives observational data full weight. Between-study heterogeneity is modeled with a random-effects distribution $u_i \\sim \\text{{Normal}}(0, \\tau^2)$. We used weakly informative priors $\\mu \\sim N(0, 10^2)$ on the population mean log effect and $\\tau \\sim \\text{{Half-Cauchy}}(0, 0.5)$ on the between-study standard deviation, with $\\tau$ bounded between $10^{{-9}}$ and $100$ for numerical stability. Alternative effect measures such as restricted mean survival time can be substituted when proportional-hazards assumptions are questionable {r('RMST', 'Boyd')}. Evidence-based priors have been proposed to anchor historical expectations while limiting prior-data conflict {r('Sherry')}. We also present bias-adjusted normal-approximation analyses as a sensitivity check. Posterior distributions are sampled with an affine-invariant ensemble MCMC {r('emcee')} using 16 walkers, 1,000 warmup and 4,000 post-warmup iterations per walker, for each $\\alpha$ in $(0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0)$. Convergence was assessed with split-R-hat and effective sample size (ESS) for the population mean log effect and the between-study heterogeneity, using accepted thresholds (split-R-hat < 1.05; ESS per parameter > 400). Trace plots for selected chains are provided as Supplementary Figures S1a (magnesium) and S1b (statins) and showed no obvious non-stationarity. Across all discounting factors the minimum ESS was {v['mc_min_ess']:.0f} and the maximum split-R-hat was {v['mc_max_rhat']:.3f}, both satisfying the convergence criteria. We report the full grid to show sensitivity and use $\\alpha$ = 0.3 as an illustrative moderate-discounting value without claiming it is universally optimal.

### Module H: Guideline interpretation

Module H maps the outputs of Modules K and T onto the GRADE framework {r('GRADE')}. It includes five assessments (Table 2): information sufficiency (OIS vs observed events), confidence interval interpretation, representativeness (event rate ratio), TSA boundary status, and recommended language. For CI interpretation, we used relative effect boundaries of 0.80 and 1.25 to define clinically important benefit and harm. For representativeness, event-rate ratios below 0.67 or above 1.50 (a relative shift of 50% or more) are classified as serious indirectness, and ratios below 0.80 or above 1.25 (a relative shift of 25% or more) as moderate indirectness. These thresholds correspond to conventional boundaries for clinically important relative effects. The result is a KOTHA-enhanced certainty rating and recommendation that explicitly distinguishes "evidence of effect," "evidence of no effect," and "no evidence of effect (inconsistent or indirect)."

""" + rf"""### Formal causal model and operating-characteristics simulation

To quantify the operating characteristics of the KOTHA evidence combination rule, we specified a transparent data-generating process that mimics the two empirical cases. Let $Z_i \sim \text{{Logit-Normal}}(\mu_Z, \sigma_Z^2)$ denote the baseline risk of trial $i$ on the log-odds scale. The true treatment effect in that population is $\text{{log OR}}_i = \theta_0 + \gamma Z_i$, with $\gamma < 0$ meaning that baseline risk modifies the treatment effect (higher-risk patients experience larger absolute or relative benefit). The target population is all hypothetical RCTs; the enrolled population is a lower-risk subset selected by a quantile threshold on $Z_i$. This is the formal mechanism for structural information loss: the RCT-enrolled meta-analysis estimates the treatment effect in a selected, lower-risk subpopulation rather than the target estimand $\mathbb{{E}}[\text{{log OR}}]$ over all RCTs.

An observational source is generated from the same target population but with systematic design-related bias toward spurious benefit, $\text{{E}}[\hat\theta_{{\text{{obs}}}}] = \theta_{{\text{{true}}}} + \beta_{{\text{{obs}}}}$ with inflated standard errors. The KOTHA combination uses a normal-approximation power-prior, $\text{{log-posterior}} \propto \alpha \cdot \text{{log-likelihood}}_{{\text{{obs}}}} + \text{{log-likelihood}}_{{\text{{rct}}}} + \text{{log-prior}}(\theta, \tau^2)$, and returns the posterior mean as the point estimate. Performance was evaluated by bias, RMSE, 95% credible-interval coverage, and statistical power (posterior probability that OR < 1 exceeds 97.5%) relative to the target estimand. The simulation was run with {v.get('n_reps', 500)} replications under pre-specified parameters; results are reported using the ADEMP checklist {r('ADEMP')}."""

    data_sources = f"""### Data sources and statistical analysis

For magnesium in AMI we used study-level event counts extracted from published overviews {r('Teo', 'Li')}. For statins in heart failure we used aggregate data from five observational cohorts {r('Anker', 'Mozaffarian', 'Horwich', 'Go', 'Foody')} and two RCTs {r('CORONA', 'GISSI')}. We used DerSimonian-Laird random-effects meta-analysis {r('DerSimonianLaird')} and computed 95% confidence intervals. OIS and TSA were calculated using standard formulas {r('Pogue', 'Wetterslev', 'Brok', 'TSAManual')}. All analyses were performed with the Python code in the public repository."""

    results = f"""### Study-level data and risk-profile shift

Study-level data are provided in Supplementary Table S1 (magnesium in AMI) and Supplementary Table S2 (statins in HF). In the magnesium case, control-group mortality fell from a pre-thrombolysis weighted mean of {v['s1_rate']*100:.1f}% to {v['s2_rate']*100:.1f}% in ISIS-4, an event rate ratio of {v['mg_rate_ratio']:.2f} (Fig. 2). In the statins case, the RCT-to-observational event rate ratio was {v['st_rate_ratio']:.2f}, indicating that the RCT populations had roughly half the mortality event rate of the observational cohorts.

**Fig. 2** Risk-profile shift in the magnesium-in-AMI case. (A) Control-group mortality rates over time, with bubble size proportional to study sample size and colors indicating era. (B) Weighted mean control mortality by era.

![Fig. 2](validation/figures/fig2_risk_profile_shift.png)

### Counterfactual power simulation

At the ISIS-4 sample size (N = {v['N_isis4']:,}) and the pre-ISIS-4 pooled effect (OR = {v['true_or']:.2f}), power exceeded 99% under all three event-rate scenarios. For a more modest effect (OR = 0.90), however, power was {v['mg_power_s1_or090']:.1f}% under the pre-thrombolysis rate and {v['mg_power_s2_or090']:.1f}% under the ISIS-4 rate (Fig. 3A). For statins, power to detect the observational effect (HR = {v['st_true_hr']:.2f}) was {v['st_power_s1_true']:.1f}% under the observational event rate and {v['st_power_s2_true']:.1f}% under the RCT event rate; for a more modest effect (HR = 0.85), power fell from {v['st_power_s1_hr085']:.1f}% to {v['st_power_s2_hr085']:.1f}%---a {v['st_power_s1_hr085'] - v['st_power_s2_hr085']:.0f} percentage-point reduction consistent with event dilution (Fig. 3B).

**Fig. 3** Estimated power by enrollment scenario and true effect size. (A) Magnesium in AMI at the ISIS-4 sample size (N = {v['N_isis4']:,}). (B) Statins in HF at the combined RCT sample size (N = {v['N_statin_rct']:,}). S1 = real-world/observational event rate; S2 = RCT event rate; S3 = intermediate/enriched rate. Horizontal dashed lines indicate 80% power.

![Fig. 3](validation/figures/fig3_power_curves.png)

### Frequentist meta-analysis and trial sequential analysis

Fig. 4 shows forest plots for magnesium and statins. Random-effects meta-analysis of the 11 pre-ISIS-4 magnesium trials yielded OR = {mg_pre_or:.2f} (95% CI: {mg_pre_lo:.2f}-{mg_pre_hi:.2f}) with $I^2$ = {int(round(v['mg_pre_i2']))}%. Adding ISIS-4 changed the pooled estimate to OR = {mg_all_or:.2f} ({mg_all_lo:.2f}-{mg_all_hi:.2f}), but heterogeneity increased to $I^2$ = {mg_all_i2}% (Fig. 4A). Under fixed-effect accumulation the final cumulative $Z$ was {v['mg_z_fe']:.2f}, which did not cross the conventional two-sided boundary for benefit or harm ($|Z|$ = {v['mg_z_alpha']:.2f}); under random-effects accumulation the final $Z$ was {v['mg_z_re']:.2f}, crossing the lower O'Brien-Fleming boundary of -{v['mg_obf']:.2f}. Because cumulative information exceeded the optimal information size, this boundary equals the conventional two-sided boundary (Fig. 5). This divergence is consistent with era-dependent treatment-effect heterogeneity, with the ISIS-4 result contributing substantially to that heterogeneity.

For statins, observational studies showed a pooled HR of {st_obs_hr:.2f} (95% CI: {st_obs_lo:.2f}-{st_obs_hi:.2f}) with $I^2$ = {int(round(v['st_obs_i2']))}%, whereas the two RCTs (CORONA and GISSI-HF) yielded HR = {st_rct_hr:.2f} ({st_rct_lo:.2f}-{st_rct_hi:.2f}) with $I^2$ = {int(round(v['st_rct_i2']))}% (Fig. 4B).

**Fig. 4** Forest plots for (A) magnesium in AMI and (B) statins in heart failure. Individual study effect estimates are shown with 95% confidence intervals. Pooled estimates include frequentist random-effects and Bayesian integrated estimates at selected discounting levels ($\\alpha$ = 0.3, 0.5, 1.0 for magnesium; 0.1, 0.3, 0.5 for statins).

![Fig. 4](validation/figures/fig4_forest_combined.png)

**Fig. 5** Trial sequential analysis for magnesium in AMI. The cumulative Z-curve is plotted against cumulative events. Vertical dashed line indicates the optimal information size (OIS). Curved lines show O'Brien-Fleming monitoring boundaries.

![Fig. 5](validation/figures/fig5_tsa_magnesium.png)

### Bayesian integration

Bayesian integration (Table 3) showed that for magnesium, with $\\alpha$ = 0 (ISIS-4 only), the posterior median OR was {v['mg_pp_alpha0_or']:.2f} with {v['mg_pp_alpha0_p1']:.1f}% probability of benefit. With $\\alpha$ = {v['alpha_example']:.1f} the posterior shifted to OR = {v['mg_pp_alpha3_or']:.2f} (95% CrI: {v['mg_pp_alpha3_lo']:.2f}-{v['mg_pp_alpha3_hi']:.2f}), with {v['mg_pp_alpha3_p1']:.1f}% probability of benefit (Fig. 6A). For statins, with $\\alpha$ = 0 (RCTs only) the posterior probability of benefit was {v['st_pp_alpha0_p1']:.1f}% and the probability of a clinically meaningful benefit (HR < 0.90) was {v['st_pp_alpha0_p09']:.1f}%. With $\\alpha$ = {v['alpha_example']:.1f} these probabilities rose to {v['st_pp_alpha3_p1']:.1f}% and {v['st_pp_alpha3_p09']:.1f}%, respectively (Fig. 6B). Even with moderate borrowing from observational evidence, conclusions remained uncertain.

**Table 3: Bayesian integration results by case and discounting factor (power prior)**

{bp._pp_table_combined(v)}

**Fig. 6** Sensitivity analysis of Bayesian integration to the discounting parameter $\\alpha$. (A) Magnesium in AMI. (B) Statins in HF. Three posterior probability thresholds are shown: P(effect < 1.0), P(effect < 0.90), and P(effect < 0.80). Horizontal dashed line indicates 95% probability.

![Fig. 6](validation/figures/fig7_sensitivity_analysis.png)

### Module H assessment

Module H results are summarized in Table 4 and Fig. 7. For magnesium, the OIS for the pre-ISIS-4 effect was {v['mg_ois']} events and the observed total was {v['mg_total_events']:,} (information fraction {v['mg_info_frac']:.0f}%). The TSA efficacy boundary was crossed under random-effects accumulation, but the pooled estimate was dominated by high between-study heterogeneity ($I^2$ = {mg_all_i2}%). The appropriate KOTHA classification is **{v['mg_kotha_classification']}** ({v['mg_kotha_rationale']}). For statins, if the observational effect (HR {v['st_obs_hr']:.2f}) represented the true effect in the target population, the required information size would be {v['st_ois']} events; the RCTs contributed {v['st_total_events']:,} events (information fraction {v['st_info_frac']:.0f}%). The cumulative $Z$ was {v['st_z_re']:.2f}, the efficacy boundary was not crossed, and the event rate ratio was {v['st_rate_ratio']:.2f}; the appropriate classification is **{v['st_kotha_classification']}** ({v['st_kotha_rationale']}). In both cases, standard GRADE would be more likely to conclude "no benefit demonstrated," whereas KOTHA explicitly labels the evidence as informationally insufficient.

**Table 4: Module H assessment --- Standard GRADE vs. KOTHA-enhanced**

{bp._table_7(v)}

**Fig. 7** Module H assessment comparison: standard GRADE vs. KOTHA-enhanced evaluation for both illustrative cases. Color coding indicates severity of concern (green = no concern, yellow = moderate, red = serious).

![Fig. 7](validation/figures/fig8_module_h_comparison.png)

### Simulation study of operating characteristics

The formal causal model produced a controlled setting in which structural information loss could be quantified. Across {v['n_reps']} replications, the target meta-analysis that used all RCTs showed negligible bias ({v['sim_target_bias']:+.3f} log-OR) and the lowest RMSE ({v['sim_target_rmse']:.3f}) (Table 5 and Fig. 8). The RCT-enrolled-only analysis was biased toward the null ({v['sim_enrolled_bias']:+.3f}), had inflated RMSE ({v['sim_enrolled_rmse']:.3f}), and low power ({v['sim_enrolled_power']:.1f}%), because low-risk enrollment diluted event rates and shifted the estimand. The observational-only estimate was biased in the opposite direction ({v['sim_obs_bias']:+.3f}) and also had poor coverage.

KOTHA with a fixed power-prior discount of $\\alpha$ = {v['sim_fixed_alpha']:.1f} reduced the absolute bias by {v['sim_bias_reduction_fixed_pct']:.0f}% and the RMSE by {v['sim_rmse_reduction_fixed_pct']:.0f}% compared with RCT-enrolled only, and increased power by {v['sim_power_gain_fixed_pp']:.0f} percentage points. The RMSE-optimal discount was $\\alpha$ = {v['sim_optimal_alpha']:.1f}; at that value the RMSE reduction was {v['sim_rmse_reduction_opt_pct']:.0f}% and the power gain was {v['sim_power_gain_opt_pp']:.0f} percentage points relative to RCT-enrolled only. These gains came from combining a small amount of observational information while down-weighting its design-related bias.

**Table 5: Operating characteristics of the KOTHA power-prior combination relative to alternative estimators.**

{bp._simulation_table(v)}

**Fig. 8** Operating characteristics of the simulation study. (A) Bias and RMSE for the target, RCT-enrolled-only, observational-only, fixed KOTHA (α = 0.3), and RMSE-optimal KOTHA estimators. (B) Coverage and power. Error bars in A show RMSE around the bias estimate; coverage and power are empirical proportions across replications.

![Fig. 8](validation/figures/fig_simulation_operating_characteristics.png)"""


    discussion = f"""### Principal findings

The KOTHA Framework integrates counterfactual power simulation, Bayesian evidence synthesis, and structured GRADE interpretation to diagnose structural information loss in RCT meta-analyses. In the magnesium case, Module K identified an {v['mg_rate_reduction_pct']:.0f}% relative decline in control event rates from the pre-thrombolysis era to ISIS-4. The divergence between pre-ISIS-4 and all-trials estimates is more consistent with era-dependent treatment effect heterogeneity ($I^2$ = {mg_all_i2}%) than with underpowering alone. In the statins case, Module K showed that RCT populations had roughly half the event rate of observational cohorts, and that power for a modest effect (HR = 0.85) dropped from {v['st_power_s1_hr085']:.0f}% to {v['st_power_s2_hr085']:.0f}%. Module T showed that even modest borrowing from observational evidence materially raised the posterior probability of benefit, yet the evidence remained uncertain. Module H classified magnesium as {v['mg_kotha_classification'].lower()}, and statins as {v['st_kotha_classification'].lower()}, rather than "evidence of no effect."

The simulation study formalizes the mechanism behind these empirical patterns. Under a transparent generative model with risk-dependent treatment effects and selective low-risk enrollment, the RCT-enrolled-only meta-analysis was biased toward the null and underpowered, while the observational-only estimate was biased toward spurious benefit. KOTHA with a fixed discount of $\\alpha$ = {v['sim_fixed_alpha']:.1f} reduced RMSE by {v['sim_rmse_reduction_fixed_pct']:.0f}% and increased power by {v['sim_power_gain_fixed_pp']:.0f} percentage points compared with RCT-enrolled-only analysis. These gains show that, in this stylized setting, the power-prior combination rule can improve operating characteristics when observational data contain relevant information that RCT enrollment discards and are appropriately down-weighted.

### Implications for clinical trial design

Module K can also be used prospectively. Before a trial is conducted, investigators can use published or registry-derived event rates for the target population (S1), for the population expected to enroll under current eligibility criteria (S2), and for an enriched design (S3). This comparison can inform four design decisions:

- **Sample size**: required N can be calculated under S2 and S3 rather than under an assumed event rate that may not materialize.
- **Eligibility criteria**: the information cost of excluding high-risk subgroups can be quantified and balanced against safety considerations.
- **Enrichment thresholds**: a minimum proportion of high-risk patients can be prespecified and powered.
- **Endpoints and follow-up**: when the primary event rate is diluted, composite endpoints or longer follow-up can be evaluated.

This reframes the design question: sample size should be based on the event rate the enrolled population will actually show, not only on a hypothesized effect.

### Comparison with existing methods

Target trial emulation uses observational data to mimic a specific RCT in order to estimate a causal effect {r('HernanTTE1', 'HernanTTE2')}. Module K is complementary: it does not estimate effects but quantifies the information lost due to enrollment decisions. Existing methods for combining RCT and observational evidence include hierarchical models, power priors, and meta-analytic-predictive priors {r('Schmidli', 'Verde', 'Efthimiou')}. Module T builds on these but embeds them in a broader workflow that first diagnoses the need for integration and then interprets the result through Module H. TSA and OIS are well established {r('Pogue', 'Wetterslev', 'Brok', 'TSAManual')}, but are not routinely used to quantify risk-profile shifts. GRADE provides domains for assessment {r('GRADE')}; KOTHA provides quantitative inputs to the imprecision and indirectness domains without changing GRADE's structure.

### Strengths and limitations

The framework is reproducible from published aggregate data, follows the ADEMP reporting structure {r('ADEMP')}, and is illustrated with real, well-documented cases. The operating-characteristics simulation is transparent: parameters, generative process, and metrics are reported explicitly. It shows that the power-prior combination rule can improve estimation and power under the specified structural information loss. The modular design allows each component to be used independently.

Limitations:

- The cases are retrospective applications of the framework to published aggregate data; individual patient data would strengthen risk-profile stratification and adjustment for confounders, and ecological bias may affect the representativeness assessment.
- For statins, the observational and RCT crude event proportions are aggregate study-level values, so the comparison is ecological and may not reflect within-individual risk differences.
- The hazard-ratio-to-odds-ratio approximation and the use of a crude event proportion (rather than an event rate per person-time) mean Module K estimates relative power loss across enrollment scenarios, not a definitive sample size for a specific follow-up.
- For statins, the S3 enrichment target is set at the midpoint between the observational and RCT crude proportions as an illustration; other thresholds would yield different power curves.
- The magnesium case spans the pre-thrombolysis and thrombolysis eras, so temporal changes in standard care, case mix, and outcome ascertainment create treatment-era confounding that cannot be fully controlled with aggregate data.
- Prospective validation against trials whose results are not yet known would be stronger.
- The operating-characteristics simulation is intentionally stylized: it uses a single data-generating model with risk-dependent effects, one selection mechanism, and normal-approximation power priors. It demonstrates that KOTHA can improve operating characteristics under transparent assumptions, but it does not establish general optimality of any fixed discounting factor.
- Module T treats the discounting parameter $\\alpha$ as a fixed sensitivity parameter and is therefore sensitive to assumptions about residual confounding; we present the full grid of values but do not claim a single preferred $\\alpha$.
- The magnesium case involves genuine treatment-effect heterogeneity across thrombolysis eras, which Module K identifies but cannot fully explain.
- Finally, adoption by guideline groups will require institutional change beyond the method itself."""

    declarations = f"""### Ethics approval and consent to participate

Not applicable. This study proposes a methodological framework and uses only published aggregate data.

### Consent for publication

Not applicable.

### Availability of data and materials

All data are from published sources and are included in the repository (https://github.com/bougtoir/kotha-rct-decomposition). Python code that reproduces all results, tables, and figures is available in the same repository.

### Trial registration

Not applicable. This manuscript presents a methodological framework and retrospective case illustrations; no prospective clinical trial was conducted.

### Declaration of competing interest

[To be determined]

### Funding source

[To be determined]

### Authors' contributions

[To be determined]

### Acknowledgements

[To be determined]"""

    highlights = """* KOTHA separates structural information loss from residual confounding.
* Counterfactual power simulation quantifies enrollment-driven event dilution.
* Power-prior Bayesian synthesis transparently discounts observational evidence.
* GRADE-compatible output labels evidence as sufficient or insufficient."""

    body_md = f"""## Highlights

{highlights}

## Abstract

{abstract}

**Keywords**: randomized controlled trials, meta-analysis, observational studies, trial design, Bayesian evidence synthesis, GRADE

## Abbreviations

| Abbreviation | Definition |
|---|---|
| ADEMP | Aims, Data-generating mechanisms, Estimands, Methods, Performance measures |
| AMI | Acute myocardial infarction |
| CrI | Credible interval |
| CI | Confidence interval |
| GRADE | Grading of Recommendations Assessment, Development and Evaluation |
| HF | Heart failure |
| HR | Hazard ratio |
| KOTHA | Knowledge-driven Observational-Trial Harmonization Approach |
| MCMC | Markov chain Monte Carlo |
| OIS | Optimal information size |
| OR | Odds ratio |
| RCT | Randomized controlled trial |
| TSA | Trial sequential analysis |

## 1. Introduction

{intro}

**Table 1: Existing approaches to mitigate event dilution in RCTs**

| Approach | Mechanism | Adoption level |
|---|---|---|
| Stratified randomization | Risk-based stratification of randomization and analysis | Common for basic strata; rare for event-rate-driven strata |
| Prognostic enrichment | Intentional enrollment of high-risk patients to increase event rates | Endorsed by FDA and EMA guidance; limited in non-drug trials |
| Event-driven design | Continue enrollment/follow-up until target event count is reached | Common in cardiology and oncology; rare in other specialties |
| Adaptive sample size re-estimation | Mid-trial re-estimation of required sample size based on observed event rates | Statistically powerful; regulatory complexity limits adoption |
| External data-informed design | Use retrospective data to quantify expected event loss and adjust design | Ideal but very rare in practice |
| Pragmatic / registry-based trials | Broad eligibility, minimal exclusions, real-world enrollment | Growing (e.g., REMAP-CAP, RECOVERY) but not yet standard |

## 2. Methods

{methods}

**Fig. 1** Overview of the KOTHA Framework. Module K (Counterfactual Power Simulation) quantifies risk-profile shift and estimates power under counterfactual enrollment scenarios. Module T (Bayesian Evidence Integration) combines RCT and observational evidence using power-prior discounting. Module H (Guideline Interpreter) synthesizes outputs into a structured GRADE-compatible assessment.

![Fig. 1](validation/figures/fig1_framework_overview.png)

**Table 2: Module H assessment checklist mapped to GRADE domains**

| Module H assessment | GRADE domain | Analytical tool | Decision criterion |
|---|---|---|---|
| Information sufficiency | Imprecision | OIS calculation | Total events < OIS: informationally insufficient |
| CI assessment | Imprecision | CI inspection | CI spans benefit through null: inconclusive |
| Representativeness | Indirectness | Module K event rate ratio | < 0.67 or > 1.50: serious; < 0.80 or > 1.25: moderate |
| TSA | Imprecision | Sequential monitoring boundaries | Boundaries not crossed: interim analysis equivalent |
| Recommendation language | Overall assessment | Standardized templates | Tailored to information sufficiency classification |

{data_sources}

## 3. Results

{results}

## 4. Discussion

{discussion}

## 5. Conclusions

The KOTHA Framework (Knowledge-driven Observational-Trial Harmonization Approach) diagnoses structural information loss in RCT meta-analyses through counterfactual power simulation, hierarchical Bayesian evidence integration, and structured GRADE-compatible interpretation. Empirical application to magnesium in AMI and statins in heart failure shows that the framework can identify enrollment-driven event dilution, quantify its impact on statistical power, and produce more nuanced evidence assessments than standard approaches. By informing sample size, eligibility, enrichment, and endpoint decisions, KOTHA offers a reproducible design aid for future clinical trials.

## Declarations

{declarations}

## References

{r.bibliography()}
"""

    # Compute word count for the main text (exclude abstract/declarations/tables/references)
    word_count_text = body_md
    # Strip front matter sections not counted
    # For CCT, word count typically excludes title page, abstract, references, tables, figures.
    # We will count Introduction through Conclusions.
    wc_match = re.search(r'## 1\. Introduction(.*?)## Declarations', body_md, re.S)
    if wc_match:
        wc_text = wc_match.group(1)
    else:
        wc_text = body_md
    # remove markdown syntax, math, figures, and tables from word count
    wc_text = re.sub(r'!\[.*?\]\(.*?\)', '', wc_text)
    wc_text = re.sub(r'\*\*Fig\.\s*\d+\*\*.*', '', wc_text)
    wc_text = re.sub(r'\*\*Table[^*]+\*\*', '', wc_text)
    wc_text = re.sub(r'(?:\|.*\n)+', '', wc_text)
    wc_text = re.sub(r'[#*_`$\\]', ' ', wc_text)
    wc_text = re.sub(r'\[.*?\]', '', wc_text)
    word_count = len(wc_text.split())

    md = _front_matter(v, word_count) + body_md

    md_path = os.path.join(BASE, '05_paper_cctc.md')
    with open(md_path, 'w') as f:
        f.write(md)
    print(f"Wrote {md_path} (main text word count: {word_count})")

    # Generate docx
    docx_path = os.path.join(BASE, 'KOTHA_Framework_CCTC.docx')
    subprocess.run(
        [sys.executable, os.path.join(BASE, 'generate_cct_docx.py'), md_path, docx_path],
        cwd=BASE,
        check=True,
    )

    return md_path


if __name__ == '__main__':
    _build_markdown()
