# Phase-9 GO/NO-GO — BBS hysteresis and delayed redistribution

Included species: 116

- HG>0: 0.77; median HG 0.006
- CI entirely >0: 0.34
- HG survives lagged env (HG_lagenv>0): 0.73, median 0.006
- matched-env effect median 0.000; frac sig (p<0.05): 0.00
- anomaly: obs_redist median 0.000, env-pred 0.308, hist-pred 0.264
- speed bias: env 0.308 vs hist 0.264
- sim FP: P(hyst>0 | env-only)=0.400, P(hyst>0 | static-route)=1.000
- observer-controlled HG: median 0.009; occurrence HG NA; regional HG -0.043
- migratory vs resident HG: migrant:0.007; resident:0.004; short_dist:0.005
- HG(h): h1=0.009, h2=0.003, h3=0.001, h5=0.001

## 13-question memo

**1. How many species have HG>0?** 89/116 under forward-chaining + route demean.

**2. How many exceed the simulation null?** See simulation_false_positive.csv; species counts vs p95 in table.

**3. Retain history after static route effects?** Median HG_D (demeaned) 0.006; frac>0 0.77.

**4. Retain history after lagged environment?** Median incremental HG 0.006.

**5. Pass matched-environment path dependence?** Median prior-state effect 0.000 (P(occ|prior) - P(occ|no prior) at matched env).

**6. Genuine hysteresis supported?** See matched_environment_hysteresis + trajectory tables.

**7. Do climate anomalies produce delayed redistribution?** See disequilibrium_decay (D by lag) and anomaly tables.

**8. Do env-only models predict redistribution too quickly?** speed_bias_env median 0.308.

**9. Do history-aware models improve timing?** speed_bias_hist median 0.264 vs env 0.308.

**10. Which strategies show strongest history?** See observer_occurrence_scale_moderators.csv mig groups.

**11. Sufficient for Nature submission?** See verdict rationale below.

**12. Strongest result against preferred interpretation?** 2x2 diagnostic: HG collapses to ~0 once route means are removed; LOYO HG largely reflects route-level static persistence.

**13. Single analysis that would most change conclusion?** Occupancy-model (nonlinear) matched-env test or individual-marked data (route fidelity).

## VERDICT: WEAK GO (no Nature escalation — stop rule engaged)

After train-only route demeaning, the prospective forward-chaining HG collapses to a median of 0.006 (77% of species >0, 34% with 95% CI entirely >0). The 2x2 diagnostic assigns the Phase-8B LOYO signal primarily to Pattern 2: route-level static persistence, not to LOYO future-year information (CV effect C-A median 0.009).

What survives static geography: a small positive lag-1 history contribution (median HG 0.006) that persists after lagged-env controls (M6-M5 median 0.006) and is stable across minimum-history 5/10/15-yr screens and expanding/10-yr/20-yr windows. At matched environment, the occupancy contrast degenerates (median 0.000; defined for 41/116 species) because focal species are near-ubiquitous, but the abundance contrast is positive (median 0.629, CI>0 in 40/41 defined species) - prior-year occupancy predicts next-year abundance at fixed environment.

Regional (state-level) aggregation HG median -0.043 where defined (does NOT retain the route-level signal), while observer covariates do not change the picture (observer-controlled HG 0.009). Climate-anomaly events show history-aware forecasts slower than env-only (speed bias 0.264 vs 0.308), consistent with inertia, but the same simulations show the demeaned-FC pipeline cannot distinguish true history from static structure at route level (scenario E HG negative; occupancy hysteresis metric has P(FP|static-route)=1.000).

Interpretation: the Phase-8B BBS signal is dominated by retrospective route-level persistence; a genuine but small prospective lag-1 component and a robust abundance-level prior-state effect remain. Under the prespecified scale this is WEAK GO (only lag-1 persistence). Per the stop rule, matched-env occupancy history effects disappeared at route level and Nature escalation stops; hysteresis/delayed-redistribution claims are not supported for the Nature-track target.
