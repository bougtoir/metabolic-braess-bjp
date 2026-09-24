# Handoff: Journal of Biopharmaceutical Statistics (JBS) submission

Date: 2026-08-28
Target journal: Journal of Biopharmaceutical Statistics (Taylor & Francis)
ISSN: 1054-3406 (print) / 1520-5711 (online)
Article type: Original Paper (preferred) or Review
Business model: Hybrid OA (subscription default, optional OA via APC / agreement)

## Why JBS?

- Scope explicitly includes "Real-World Evidence and Data Integration" and "external controls" in clinical development.
- Original Papers and Review Papers are accepted; rapid publication.
- The KOTHA framework (combining RCT evidence with discounted observational evidence via a power prior) maps naturally onto data integration / external information borrowing in biopharmaceutical development.

## Reframing needed for JBS

1. **Title**: Keep "KOTHA" but emphasize simulation-based methodology and data integration, e.g.:
   "The KOTHA Framework: A Simulation Study of Power-Prior Integration to Correct Structural Information Loss in RCT Meta-Analyses"
2. **Abstract**: Reframe the motivation as a biostatistical problem in clinical development (enrichment / enrollment risk shift), not as a general meta-analysis critique.
3. **Introduction**: Lead with why standard sample-size / meta-analysis methods can mislead when trial enrollment shifts the baseline risk; position KOTHA as a design-stage diagnostic.
4. **Methods**: Emphasize ADEMP simulation, power-prior formulation, operating characteristics (bias, RMSE, coverage, power) relative to RCT-only, observational-only, and naive meta-analysis.
5. **Results / Discussion**: Tie findings back to design decisions in Phase II/III or enrichment trials; avoid over-causal language; stress "operating characteristics" and "decision support".
6. **References**: Update Vancouver numbering to match the new Introduction order; remove any orphan/phantom citations.
7. **Declarations / COI / Funding**: Replace `[To be determined]` placeholders before submission.
8. **Word / figure limits**: JBS does not publish strict limits in the available search data; prepare a standard T&F manuscript (≈5,000–8,000 words, ≤8 figures/tables recommended) and verify against the current Instructions for Authors.

## Files already generated

- `05_paper_clinical_trials.md` / `KOTHA_Framework_ClinicalTrials_submission.docx` (Clinical Trials version; Clinical Trials desk-rejected 2026-08-28)
- `05_paper_cctc.md` / `KOTHA_Framework_CCTC.docx` (CCTC version)
- `critical_review_revised_KOTHA.md` (reviewer-perspective critique)
- `target_journal_options_sorted_by_APC.md` (candidate list)
- `validation/simulation_study.py`, `validation/run_validation.py`, `validation/simulation_summary.json`, `validation/figures/fig_simulation_operating_characteristics.png`

## Next steps

1. Read current JBS Instructions for Authors and APC details from Taylor & Francis.
2. Create `build_paper_jbs.py` (or adapt `build_paper_cct.py`) producing a JBS-formatted docx.
3. Reframe title/abstract/introduction for JBS scope.
4. Run clean-clone reproducibility check from `bougtoir/kotha-rct-decomposition`.
5. Push to `bougtoir/wip` and sync public mirror.

## Notes

- Keep English-only figure/table elements, font-based superscript citations, OMML equations, no CJK characters.
- All numbers must remain reproducible from code (no hard-coded estimates).
- Consider adding a sentence on regulatory relevance (e.g., FDA guidance on enrichment, external controls) if supported by real references.
