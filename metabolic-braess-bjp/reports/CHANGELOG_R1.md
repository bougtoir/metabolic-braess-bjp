# Revision R1 change log (BJP metabolic NOPM)

## Claims corrected
- Abstract "recur under pFBA in all media" → "in multiple (but not
  all) media" — Human-GEM glucose-limited pFBA has zero hits for both
  modulation methods (robustness matrix).
- Abstract converted to BJP structured format (Background and Purpose /
  Experimental Approach / Key Results / Conclusion and Implications;
  204 words).
- Title: "Maximum local effect does not imply optimal system effect:
  selection-rule-dependent interior modulation optima in human
  metabolic networks".
- "feedback-free stoichiometric coupling" → "constraint-based metabolic
  models represent stoichiometric coupling and rerouting without
  explicit kinetic feedback regulation".
- pFBA≠chronic / MOMA≠acute: reframed as parsimonious/adapted vs
  minimal-deviation state-selection abstractions; acute-vs-chronic
  demoted to explicit testable hypothesis (4.7).
- Rate–yield trade-off made explicit: "ATP yield per glucose rises as
  ATP throughput falls" (Results 3.2, Discussion 4.3, Fig 4 caption).
- ATP/O2 downgraded to diagnostic endpoint (Methods + Limitation iii);
  headline claims use ATP/glucose, carbon efficiency, flux economy.
- Discussion restructured to A–G skeleton: existence / cross-model
  replication / rate–yield / state-selection / pharmacological
  interpretation / limitations / adaptation-state hypothesis.

## Additions
- Supplementary Table S1: Human-GEM→Recon3D reaction crosswalk with
  family-level replication status and PDH discordance notes
  (manuscript/tableS1_crosswalk.csv).
- Ref [21] Facchetti & Altafini 2013 (continuous partial inhibition in
  bilevel FBA) added; prior-art audit extended (PHASE_0 R1 section).
- Cover letter updated (new title; state-selection framing).

## Unchanged (verified, not altered)
- 12 Human-GEM / 8 Recon3D Type II hits; all u*, J(0)/J(u*)/J(1)
  verified against results/scans/class_*_full.csv.
- Robustness matrix (24 cells) verified incl. Human-GEM
  glucose-limited pFBA zeros.
- Figures regenerated from results CSVs (fig1–5); manuscript_values.csv
  regenerated (18 keys).
- Tests: 12/12 pass.
