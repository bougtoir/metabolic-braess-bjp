# KOTHA Framework — Session Handoff to Contemporary Clinical Trials

## Decision

- **Next target journal**: *Contemporary Clinical Trials* (Elsevier)
- **IF**: ~1.9–2.2
- **APC**: ~$3,450 USD (hybrid OA; non-OA publication under CTA also possible)
- **Scope**: clinical trial design, conduct, analysis, regulation, ethics; perspectives/commentaries; systematic reviews of clinical trials and methodologies.
- **Word limit**: full-length papers **≤ 4,000 words** (short communications ≤ 1,500). The current `04_paper_rsm.md` is ~7,600 words, so substantial condensation and reframing are required.

## What was completed in the previous session

- Reviewed BMC Medical Research Methodology rejection and Reviewer 1 / Reviewer 2 comments.
- Created `response_to_reviewers_BMC_MRM.md` with point-by-point responses.
- Updated `04_paper_rsm.md`:
  - Tempered claims; acknowledged other sources of observational-RCT discordance.
  - Distinguished ideal vs. realized counterfactual simulation.
  - Added HR/PH assumption and RMST alternative discussion.
  - Added empirical prior discussion for Module T.
  - Clarified α = 0 as a single-study/fixed-effect limiting case.
  - Added TSA futility boundary and reconciled fixed-effect vs. random-effects cumulative Z.
  - Changed statin TSA interpretation to “inconclusive.”
  - Added Table 1 comparison and module prerequisites discussion.
  - Replaced “validated” with “illustrated.”
  - Renumbered references in Vancouver order (31 refs).
- Updated `validation/run_validation.py` and regenerated all figures + `results_summary.txt`.
- Generated `KOTHA_Framework_RSM.docx` and `KOTHA_Framework_RSM_figures.pptx`.
- Created `journal_recommendation.md` with a full IF/APC/publisher comparison of candidate journals.
- Pushed to `bougtoir/wip` branch `devin/1774274321-rct-decomposition-paper` (PR #9).

## Key numerical results (verified)

- Magnesium pre-ISIS-4 random-effects OR = 0.54 (95% CI 0.40–0.75), I² = 6%.
- Magnesium all-trials random-effects OR = 0.56 (95% CI 0.38–0.83), I² = 62%.
- Fixed-effect cumulative TSA final Z = 0.80; random-effects cumulative TSA final Z = -2.90.
- Statin observational random-effects HR = 0.72 (95% CI 0.64–0.80), I² = 82%.
- Statin RCT random-effects HR = 0.97 (95% CI 0.90–1.05), I² = 0%.
- Statin final TSA Z = -0.74 → interpreted as inconclusive.

## Files that matter for the CCT submission

- `rct-decomposition/04_paper_rsm.md` — source manuscript (needs major rewrite for CCT)
- `rct-decomposition/generate_rsm_docx_final.py` — docx generator (will need word-count/format adjustments)
- `rct-decomposition/KOTHA_Framework_RSM.docx` — current formatted manuscript
- `rct-decomposition/KOTHA_Framework_RSM_figures.pptx` — editable figures
- `rct-decomposition/validation/run_validation.py` — reproducible analysis code
- `rct-decomposition/validation/figures/*.png` — figure files
- `rct-decomposition/validation/results_summary.txt` — numerical summary
- `rct-decomposition/journal_recommendation.md` — full candidate comparison
- `rct-decomposition/response_to_reviewers_BMC_MRM.md` — prior rejection response for record

## Required rewrite strategy for Contemporary Clinical Trials

1. **Refocus from meta-analysis methodology to trial-design implications**:
   - Frame KOTHA as a diagnostic framework that evaluates how **trial enrollment and event-rate design choices** propagate into evidence synthesis.
   - Emphasize the connection to Table 1 design strategies (enrichment, pragmatic/registry trials, event-driven designs) and show how KOTHA can audit their consequences in meta-analysis.
   - Position the manuscript as a methodology for improving the design and interpretation of future clinical trials, not only for retrospective meta-analysis.

2. **Cut to ≤ 4,000 words**:
   - Reduce the theoretical/philosophical sections.
   - Move detailed equations and Bayesian derivations to an Appendix or supplementary material.
   - Keep only one illustrative case or condense both cases into a single high-level example.
   - Merge Methods subsections and remove redundant bullet lists.

3. **Adjust tone and terminology**:
   - Use “clinical trial design and evidence synthesis” rather than “meta-analysis methodology.”
   - Stress translational value: KOTHA helps trialists understand whether their trial population will be informative when pooled with others.
   - Avoid strong clinical-recommendation language; CCT is not a clinical-guideline journal.

4. **Verify CCT Author Guidelines** at https://www.sciencedirect.com/journal/contemporary-clinical-trials:
   - Confirm article types (Full-length paper, Short communication, Perspective, Commentary, Systematic review of methodologies).
   - Check abstract structure, word count, figure/table limits, reference style (Vancouver), and file formats.

5. **Cover letter for CCT**:
   - Highlight that the manuscript addresses trial design and evidence synthesis.
   - Explain how KOTHA complements enrichment, event-driven, and registry-based design strategies.
   - Mention the two cardiovascular examples (Mg/AMI, statins/HF) as real-world illustrations of trial-population shift.

## Remaining work for the new session

1. Read CCT Author Guidelines and decide article type.
2. Rewrite `04_paper_rsm.md` to ≤ 4,000 words with a trial-design framing.
3. Update `generate_rsm_docx_final.py` if needed for CCT formatting (or keep generic).
4. Regenerate `KOTHA_Framework_CCT.docx` and `KOTHA_Framework_CCT_figures.pptx`.
5. Draft CCT-specific cover letter.
6. Run `run_validation.py` and confirm reproducibility.
7. Push to `devin/1774274321-rct-decomposition-paper` or create a new branch if the rewrite is substantial.

## Important constraints from user knowledge notes

- Results must be reproducible from the public repo and real data mentioned in the paper.
- Do not hard-code numbers in the manuscript generator.
- Maintain Vancouver citation order; renumber if references are added/removed.
- Figures/tables inline in docx and also as editable pptx.
- Do not resubmit to BMC Medical Research Methodology, Journal of Clinical Epidemiology, or Research Synthesis Methods.

## Branch / PR status

- Working branch: `devin/1774274321-rct-decomposition-paper` in `bougtoir/wip`
- PR: `bougtoir/wip#9`
- Public mirror sync: `sync-to-repos.yml` maps this branch → `bougtoir/kotha-rct-decomposition`.

## Note on previous SMMR handoff

- `session_handoff_to_SMMR.md` was prepared for *Statistical Methods in Medical Research*; this CCT handoff supersedes it unless the user decides to pursue SMMR later.
