# Response to Reviewers — BMC Medical Research Methodology

**Manuscript**: The KOTHA Framework: a counterfactual simulation and Bayesian integration approach to diagnosing structural information loss in randomized controlled trial meta-analyses  
**Submission ID**: eb141294-29bb-4747-86a7-5c5bf45bd1e4  
**Decision**: Editorial rejection (uninvited for revision)

We thank the Editor and the Reviewers for their careful assessment. Although the manuscript was rejected, Reviewer 2 noted that the issues raised were addressable, and we believe the conceptual contribution is still valuable. We have therefore prepared the following point-by-point response and implemented the corresponding revisions in the manuscript (`04_paper_rsm.md`), validation pipeline (`run_validation.py`), figures, and supplementary files. The revised docx and editable figure pptx are also generated.

---

## Reviewer 1

### Main point 1 — Narrative style and overuse of lists
> The current presentation relies heavily on short subsections and lists. ... The author is encouraged to consolidate overlapping sections and develop a more streamlined narrative presentation, particularly in the Methods and Discussion.

**Response**: We agree. In the revised manuscript we will:
- Consolidate the Methods subsections for Modules K, T, and H into a clearer narrative flow, using tables only for the structured checklist (Module H) and the ADEMP reporting frame (Module K).
- Merge the "Theoretical foundations" section with the Methods section where possible, presenting the equations as part of the method description rather than as a separate section.
- Rewrite the Discussion to reduce bullet lists and develop a cohesive argument: (i) what problem KOTHA addresses, (ii) how the two empirical cases illustrate its use, (iii) how it relates to existing methods, and (iv) the conditions under which it is most useful.

### Main point 2 — RCTs do not always exclude high-risk patients
> It should be noted that not all RCTs exclude high-risk patients. ... The claim that it accounts for “a substantial proportion of observational-RCT discrepancies” should be either tempered or supported by systematic evidence.

**Response**: We will temper the claim throughout the manuscript. Specifically:
- The Abstract and Background will state that structural information loss is **one important source** of observational-RCT discordance, alongside confounding, selection bias, and publication bias in observational studies.
- We will note explicitly that some trials use enrichment designs and actively recruit high-risk patients, and that the KOTHA framework is intended for settings where enrollment criteria or practice patterns shift the risk profile downward.
- We will change language such as “a substantial proportion” to “a non-negligible and under-recognized proportion” and frame the hypothesis as requiring empirical calibration in each clinical domain.

### Main point 3 — Counterfactual simulation: idealized vs. realized
> The methods propose to simulate from the counterfactual population by employing a prognostic model fit to a real-world retrospective cohort. However, the data applications appear to conduct power calculations based on aggregate event rates from previously published studies. ... The applications may be more accurately described as sensitivity analyses of power under alternative assumed event rates.

**Response**: This is a fair and important distinction. We will revise the Methods and Discussion as follows:
- In the **Module K** methods, we will distinguish the **ideal workflow** (individual-level prognostic model fitted to a real-world cohort, with three enrollment scenarios) from the **realized application** in this manuscript (scenario-specific control event rates derived from published aggregate data, because patient-level retrospective cohorts were not available for the historical cases).
- We will relabel the current analyses as “scenario sensitivity analyses of statistical power under alternative assumed event rates” and make clear that they do not recover a true individual-level counterfactual.
- We will add a paragraph in **Strengths and limitations** noting that the framework’s full value depends on access to a representative retrospective cohort, and that the two cases serve as proof-of-concept illustrations.

### Main point 4 — HR and proportional hazards assumption
> For time-to-event endpoints, the proposed analysis is based on the hazard ratio (HR). ... The manuscript should surface the limitations of default reliance on HRs and note that alternative estimands with fewer assumptions, such as the RMST, are available.

**Response**: We will add a new subsection in **Module K / Theoretical foundations** titled “Choice of estimand for time-to-event outcomes”:
- We will state that the HR assumes proportional hazards and that its interpretation becomes ambiguous when this assumption is violated or censoring patterns differ across studies.
- We will note that the KOTHA power-calculation logic is not tied to the HR; it can be applied to any effect measure for which the expected number of events determines statistical information (e.g., log-OR, risk difference, RMST difference).
- We will add a limitation that the empirical applications use HRs because the published meta-analyses reported them, and that RMST-based sensitivity analyses would be a valuable extension.

### Main point 5 — Generic prior in Module T
> Module T currently relies on a generic prior for the overall treatment effect. ... The author is encouraged to comment on how an empirical cardiology prior, if available, could be used to contextualize the current RCT evidence before incorporating observational studies.

**Response**: We will add a paragraph to the **Module T prior specifications** and to the **Discussion**:
- We will acknowledge that the current weakly informative `Normal(0, 10²)` prior for μ is a placeholder and that domain-specific empirical priors (e.g., from previous cardiology trials or meta-epidemiological studies of observational-RCT discrepancies) could strengthen inference.
- We will cite recent work on empirical priors for phase III trials and note that such a prior would be applied to the RCT evidence first; the power-prior/discounting of observational evidence would then be used only after the empirical prior has been specified.
- We will add a sensitivity analysis showing how an informative empirical prior for μ changes the posterior, or state this as future work if an appropriate cardiology prior cannot be constructed from the available literature.

### Main point 6 — Bayesian integration at α = 0 (magnesium)
> At α=0, the magnesium analysis includes only ISIS-4, yet a random-effects model is apparently retained. ... The manuscript should also clarify that power-prior discounting reduces the influence of observational evidence but does not itself correct systematic bias due to confounding or lack of exchangeability.

**Response**: We will revise the **Module T** methods and results:
- We will report the fixed-effect (single-study) estimate for ISIS-4 alongside the Bayesian hierarchical estimate at α = 0, and explain that the latter is driven by the heterogeneity prior because τ is not identified with one study.
- We will clarify in the text that the α = 0 row represents the limiting case where the prior evidence receives zero weight, and that in practice a fixed-effect or single-study summary should be used when only one primary study is available.
- We will add an explicit statement that discounting (α < 1) attenuates the influence of observational or prior-era data but does **not** remove confounding or guarantee exchangeability; the bias-adjustment parameter δ is the mechanism for addressing systematic bias, and sensitivity to both α and δ is mandatory.

### Main point 7 — Reconcile magnesium TSA results
> The manuscript reports an all-trials random-effects pooled OR of 0.56 (95% CI: 0.38–0.83), yet the final cumulative TSA Z-statistic is 0.80. These results may reflect different meta-analytic models or weighting schemes, but the manuscript should state this explicitly and provide sufficient detail to reconcile the two analyses.

**Response**: This inconsistency arose because the pooled estimate used a random-effects model while the cumulative TSA used a fixed-effect inverse-variance accumulation. We will:
- Replace the fixed-effect cumulative TSA with a **random-effects cumulative TSA** (or a heterogeneity-adjusted information-size TSA) and present the cumulative Z-curve using the same model as the pooled meta-analysis.
- Report both the conventional and O’Brien-Fleming monitoring boundaries, and clearly state which model was used at each step.
- Add a paragraph explaining why the two models diverge in this case (ISIS-4 dominates the fixed-effect weights, while the random-effects model down-weights it because of high between-study heterogeneity, I² ≈ 62%).
- If the random-effects cumulative Z remains significant, we will not over-interpret it as evidence of benefit; instead, we will emphasize that the heterogeneity across eras makes the pooled effect ungeneralizable and that the case illustrates the need for Module T’s sensitivity analysis.

### Main point 8 — Statins TSA futility boundary
> Failure to cross an efficacy boundary, even after the required information size has been reached, does not establish evidence of no benefit. A conclusion of futility requires a separately defined futility boundary or other prespecified criterion demonstrating that clinically meaningful benefit can be excluded. The author should revise the Module H decision rules and the interpretation of the statin results accordingly.

**Response**: We will revise the **Module H decision rules** as follows:
- We will add a symmetric **futility boundary** to the TSA framework (e.g., an O’Brien-Fleming lower boundary) and require that this boundary be crossed before concluding “evidence of no effect.”
- We will change the statin case interpretation from “no benefit” to **“no evidence of effect: the efficacy boundary was not crossed and the futility boundary was not crossed; the RCT evidence is therefore inconclusive at the observed information size.”**
- We will update Table 2 (Module H checklist) and the decision flow to distinguish three outcomes: (1) efficacy boundary crossed → evidence of effect, (2) futility boundary crossed → evidence of no effect, (3) neither crossed → inconclusive.

### Main point 9 — Temper validation and clinical utility claims
> The discussion should temper the claims regarding validation and clinical utility. The two retrospective case studies provide useful illustrations, but they do not establish the operating characteristics of the full framework or show that it should alter clinical recommendations.

**Response**: We agree and will revise the **Discussion / Principal findings** and **Implications for clinical practice**:
- We will replace “validated” with “illustrated” or “proof-of-concept evaluated” where appropriate.
- We will state that the two cases are **retrospective illustrations** selected because they are well-documented examples of observational-RCT discordance, and that they do not establish the framework’s operating characteristics in a prospective or systematic sample of meta-analyses.
- We will add a limitation that the individual-level counterfactual simulation described in Module K was not implemented in the empirical cases (consistent with Main point 3) and that the Bayesian conclusions depend materially on the choice of α and δ.
- We will not claim that KOTHA should change any specific clinical recommendation until prospective validation is available.

---

## Reviewer 2

### Major point 1 — Complexity and prerequisites of the approach
> One of the main weaknesses of the approach is that it is relatively complicated to apply and requires many assumptions/prerequisites. ... It would be good, if the authors could discuss more deeply how often the requirements for the different Modules are met in practice and maybe also what to do, if the requirements are not fully met, similar as done for other approaches in Table 1.

**Response**: We will add a new subsection in the **Discussion** titled **“Prerequisites and practical applicability of the KOTHA modules”**:
- For each module we will list the minimum data requirements (e.g., for Module K: a representative retrospective cohort or reliable aggregate event-rate data; for Module T: study-level effect estimates from RCT and observational sources; for Module H: an OIS/TSA calculation and a GRADE assessment).
- We will discuss how often each requirement is likely to be met in practice (Module H almost always; Module T often; Module K only when suitable retrospective data are available).
- We will provide guidance on what to do when a requirement is not met (e.g., skip Module K and rely on Module T/H with explicit sensitivity analyses; use bias-adjusted normal approximation instead of full Bayesian integration; downgrade certainty due to inability to quantify indirectness).

### Major point 2 — Table 1 approaches are not discussed
> The approaches named in Table 1 are just mentioned once and never discussed or embedded again, but it would be helpful to discuss the new framework with respect to the approaches in table 1 (pros and cons, what is solves, what is open).

**Response**: We will expand the **Comparison with existing methods** subsection in the Discussion:
- We will explicitly compare KOTHA to each approach in Table 1 (stratified randomization, prognostic enrichment, event-driven design, adaptive sample-size re-estimation, external-data-informed design, pragmatic/registry-based trials).
- For each, we will state: (i) the problem it solves, (ii) when it is most useful, (iii) its limitation, and (iv) how KOTHA complements it (e.g., KOTHA provides a retrospective diagnostic tool, whereas Table 1 approaches are primarily prospective design strategies).
- We will add a paragraph explaining that KOTHA is not a replacement for good trial design but a diagnostic and integrative layer that can be applied when the Table 1 strategies have not been or cannot be implemented.

### Minor point 1 — German expression in Figure 1 / Page 8
> Figure 1 and Page 8: there are Germen expressions “kontrafaktische power”, please translate.

**Response**: We will replace “Kontrafaktische Power Simulation” with “Counterfactual Power Simulation” in all text and figure labels, and regenerate Figure 1.

### Minor point 2 — Table 7 wording
> Table 7: “Serious: event rate down 18%/47%”. I suppose you mean “Event rate decreased by 18%/47%”.

**Response**: We will update Table 7 to read “Event rate decreased by 18% (magnesium) / 47% (statins)” and make the same change in the figure-generating code for Figure 8.

---

## Summary of planned manuscript changes

| Section | Change | Status |
|---|---|---|
| Abstract & Background | Temper claims; acknowledge other causes of observational-RCT discordance. | Done |
| Methods / Module K | Distinguish ideal individual-level workflow from realized aggregate-rate sensitivity analysis. Add RMST/HR discussion. | Done |
| Methods / Module T | Clarify α = 0 as single-study/fixed-effect limiting case; discuss empirical priors; clarify discounting does not remove confounding. | Done |
| Methods / Module H | Add futility boundary; define three TSA outcomes (efficacy / futility / inconclusive). | Done |
| Results / Module H | Reconcile magnesium TSA using fixed-effect and random-effects cumulative models; revise statin interpretation to “inconclusive.” | Done |
| Discussion | Consolidate narrative; add Table 1 comparison; add prerequisites/applicability subsection; temper validation claims. | Done |
| Figures & Tables | Translate “Kontrafaktische Power Simulation”; update Table 7/Figure 8 wording. | Done |
| Validation code | Update `run_validation.py` to compute fixed-effect and random-effects cumulative TSA; regenerate figures and `results_summary.txt`. | Done |

---

## Files updated in this revision

- `rct-decomposition/04_paper_rsm.md` — revised manuscript
- `rct-decomposition/response_to_reviewers_BMC_MRM.md` — this document
- `rct-decomposition/journal_recommendation.md` — next-journal strategy
- `rct-decomposition/validation/run_validation.py` — corrected TSA and Module T outputs
- `rct-decomposition/validation/figures/*` — regenerated figures
- `rct-decomposition/validation/results_summary.txt` — regenerated numerical summary
- `rct-decomposition/KOTHA_Framework_RSM.docx` — formatted manuscript
- `rct-decomposition/KOTHA_Framework_RSM_figures.pptx` — editable figures
