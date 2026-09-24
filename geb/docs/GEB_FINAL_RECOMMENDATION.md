# GEB final recommendation

## Verdict: GEB AFTER ONE ESSENTIAL ANALYSIS

**The one analysis**: an observer-persistence control for the abundance
prior-state effect — re-estimate the matched-environment abundance contrast
on consecutive route-year pairs where the observer changed (or with
observer identity included in the match). Rationale (GAP_AUDIT §10): the
abundance result (+0.63 log-count, 40/41 CI > 0) is the paper's headline
positive finding and its most attackable flank is the observation process,
not the biology. The check is feasible with existing data (observer IDs are
already in the panel), answers one specific reviewer objection, and either
strengthens the result or materially changes it — either outcome must be
known before drafting.

## Everything else is ready

- Decomposition design, falsification discipline, leakage-free
  forward-chaining, survey semantics, common evaluation samples, and
  simulation validation are all verified and regression-tested.
- Novelty: no prior study found that directly separates static spatial
  persistence from temporal history dependence in lagged-state predictors
  across many species *and* contrasts occupancy vs abundance under one
  design. Closest precedent (autocovariate vs static random effects in
  spatial SDMs; space-for-time climate decomposition) is complementary and
  citable — repositioning note in NOVELTY_MATRIX.csv.

## Items to fix in drafting (no analysis needed)

- Scope wording: "116 widespread, regularly detected breeding-bird species",
  not birds generally (inclusion rule selects for prevalence).
- Bounded environmental claim: "at matched modelled environment".
- Pre-fix numbers appear only in a supplementary reproducibility note,
  never in the main text.
- Do not rescue memory/hysteresis/delayed-redistribution/regional
  persistence as positive claims — the falsification is the paper.

## If the observer-control analysis removes the abundance effect

The paper remains viable but the headline changes: it becomes a pure
"lagged-state predictability is mostly spatial persistence" paper with a
null contrast. Still publishable at GEB-level conceptual interest, but the
occupancy/abundance divergence is the stronger paper — hence the analysis
is worth running before the draft, not after review.
