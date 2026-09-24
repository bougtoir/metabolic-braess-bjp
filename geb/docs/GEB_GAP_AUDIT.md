# GEB gap audit

Answers to the 10 audit questions, against the Phase-9 post-fix pipeline.
"Gap" = something a competent GEB reviewer could reasonably press on.

## 1. Is 116 species sufficient for general macroecological framing?

Adequate but not unlimited. 116 widespread, regularly-surveyed passerine and
non-passerine species is a credible continental sample and the per-species
distribution over HG/effects is the right scale for the claim. Two cautions:
(a) the inclusion rule (nz_frac ≥ 0.30 on surveyed route-years) selects for
widespread species — statements must be about "widespread, regularly
detected breeding birds", not all birds; (b) near-ubiquity is exactly why
the occupancy contrast degenerates for 75 species, so the occupancy null is
bounded by design. Not a blocking gap; wording-level fix.

## 2. Are migration-status contrasts useful or distracting?

Distracting as a main result. The migratory/resident moderator analysis is
weakly powered at n=116 and the 8B-style contrast adds little once static
persistence dominates. Recommend: one supplementary table, zero main-text
claims. Do not build a section on it.

## 3. Is the abundance prior-state effect fully adjusted for long-run route abundance?

Not fully — this is the largest remaining interpretive gap. The abundance
contrast is computed on route-demeaned abundance within matched
environment, so stable mean differences are removed, but a route's
long-run *level* can still correlate with persistence if demeaning is
imperfect under trends. Mitigation already present: train-only demeaning +
common matched sets. Recommendation: one supplementary check regressing the
prior-state effect on route mean abundance — cheap, answerable with
existing outputs. If it survives, the result strengthens.

## 4. Any remaining risk that observer persistence creates the abundance effect?

Low but not zero. Observer covariates were controlled (observer-controlled
HG ≈ 0.009, no material change), and the matched-environment design fixes
environment, not observer. A repeated-observer confound (same observer for
years on one route) could in principle produce serially correlated counts.
Residual risk acknowledged as a limitation; a dedicated observer-persistence
control is the single most defensible optional addition — see §10.

## 5. Are environment variables rich enough to support claims about environmental adjustment?

Bounded claim only. The matched-environment and lagged-env controls use the
final covariate set; we cannot claim exhaustive environmental adjustment.
Wording must be "at matched modelled environment", not "at identical
environment". Residual habitat heterogeneity (land use, fine-scale
vegetation) is a stated limitation. No additional data are required for the
current claims.

## 6. Is the forward-chaining implementation fully leakage-free?

Yes, verified: route-demeaning means and predictor column centring are
estimated from train ≤ t only (no SD scaling is applied; evaluation is
complete-case — no imputation); target-year information cannot enter
features; common evaluation samples are asserted per species
(`final_common_eval_assert.csv`); the regression test suite
(`phase9/tests/test_phase9.py`) includes a no-future-in-forward test.
This is a strength to advertise in Methods.

## 7. Is the static route control biologically interpretable?

Yes — route demeaning absorbs any time-invariant route property
(persistent habitat quality, local geography, long-run observer identity
averaged over the panel). Interpretation must stay at that level of
abstraction: it removes "persistent route-level heterogeneity", not
"habitat" specifically. Overclaiming what the fixed effect *is* is a
reviewer trap.

## 8. Is simulation null construction adequate?

Adequate for the falsification purpose: scenarios cover environment-only,
static-route-only, observation persistence, true history, and true
hysteresis; survey coverage mask is applied to simulated frames; truth
labels are regression-tested. Honest limitation already documented: the
demeaned forward-chaining design has limited power — even true-history
simulations are hard to detect after demeaning. This must be stated openly;
it bounds how strongly we can claim "no" history rather than weakening the
static-persistence result.

## 9. Is there any claim that should be removed before GEB submission?

Yes, three:
- (a) any residual language implying positive regional persistence
  (post-fix regional HG ≈ −0.04) — report as null;
- (b) any claim of occupancy hysteresis — matched-env contrast is 0.000 in
  all definable species;
- (c) any delayed-redistribution/history-aware-forecast-speed claim as a
  positive result — speed bias (env 0.31 vs hist 0.26) shows history-aware
  forecasts are if anything slower, not better trackers.

## 10. What additional analysis, if any, would materially change acceptance probability?

Exactly one candidate clears the §16 threshold:

**Observer-persistence control for the abundance prior-state effect.**
The single headline positive result (abundance state dependence, +0.63
log-count) is the one reviewers will attack via observation process.
A matched-set re-estimation restricted to consecutive route-years with
different observers (or with observer identity added to the match) directly
tests whether demographic continuity survives once observer persistence is
removed. Feasible with current data (route-year observer IDs already
loaded in `observers_mod`); answers a specific gap; could change the
effect size, not just its wording.

Everything else (finer covariates, more species, individual-level data) is
either infeasible with current data or non-essential.
