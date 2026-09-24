# Phase 10 (prep) — Reviewer-style pre-submission critique

Anticipated referee objections and where the manuscript must address them:

1. **Artefact risk — pFBA degeneracy.** NOPM in efficiency metrics may reflect
   which alternate optimum pFBA selects, not physiology. Mitigation: (a) all
   hits reproduced in a SECOND independent model (recon3d); (b) L1-MOMA
   (a different selection rule, not alternate-optimum-sensitive in the same
   way) must reproduce interior optima on the Type-II hits; (c) state
   explicitly that results are conditional on the selection rule.
2. **Yield vs rate conflation.** atp_per_glc improving while ATP RATE falls
   could be dismissed as trivial. Manuscript must present BOTH raw endpoints
   (rate and yield) and the Pareto view, and avoid implying partial
   inhibition "improves" cells — it improves a stoichiometric yield metric.
3. **Medium dependence.** Curated minimal medium is artificial. Assessed
   over aerobic/glucose-limited/oxygen-limited; open mediums admit cheat
   cycles (documented). Acknowledge limited condition coverage.
4. **Clinical overreach.** No dose translation claimed; drug_mapping is
   target-level only. Devimistat/metformin examples must be framed as
   mechanistic analogies.
5. **Model artefacts.** Human-GEM P/O not locked (atp_per_o2=6 baseline);
   reported as model property. Recon3D name typos handled by aliases.
   No silent model edits — all changes in code/config.
6. **ATPM objective artificiality.** Objective is ATP maintenance demand;
   results are stated as conditional on this system objective.
7. **Kinetics absent.** Stoichiometric-only; no enzyme kinetics, regulation,
   or dynamics. Interior optima are constraint-based predictions to be
   tested, not measured effects.
8. **Tissue specificity.** Single generic cell context; tissue
   contextualization via condition proxies only; flagged as future work.
9. **Statistical framing.** No replicates exist (deterministic LP); effects
   reported as magnitudes over a grid, not significance — avoid p-values.
10. **Total_flux minima interpretation.** Parsimony minima may be
    considered definition-bound to pFBA (min |v| is pFBA's own criterion).
    Response: kept as a secondary class; efficiency optima are the headline.
