# Phase-8B GO/NO-GO — history dependence across ecosystems

All values regenerated from results/tables at report time.

## HG / EG by system

| system | n | median HG | median EG | sim p95 HG (rho=0.3) |
|---|---|---|---|---|
| bbs | 10 | 0.664 | -0.000 | 0.272 |
| elk | 54 | 0.022 | 0.000 | NA |
| foss | 6 | 0.033 | 0.013 | 0.372 |
| neon | 6 | 0.354 | -0.021 | NA |
| wolf | 2 | -0.050 | 0.000 | NA |

## False-positive screen

| system | rho_obs | P(HG>0) | P(HG>0.05) | median sim HG | p95 sim HG |
|---|---|---|---|---|---|
| foss | 0.0 | 1.00 | 0.80 | 0.235 | 0.362 |
| foss | 0.3 | 0.95 | 0.85 | 0.245 | 0.372 |
| bbs | 0.0 | 1.00 | 0.85 | 0.090 | 0.281 |
| bbs | 0.3 | 0.95 | 0.70 | 0.117 | 0.272 |
| elk_mask | 0.0 | 0.35 | 0.00 | -0.001 | 0.002 |
| elk_mask | 0.3 | 0.95 | 0.10 | 0.008 | 0.056 |

## Verdict vs criteria

- BBS (population): median HG 0.664 vs simulated-null p95 0.272 — exceeds obs-persistence null.
- FOSS (population): median HG 0.033 vs p95 0.372 — within null.
- Elk (GPS individual): median HG 0.022 vs p95 0.056 — within null.

## 12-question memo

**1. Is HG>0 in >=2 systems incl. one GPS + one population?** BBS HG=0.664 (yes, exceeds sim null), elk HG=0.022 (positive but within obs-persistence null), FOSS HG=0.033 (below sim median). Only BBS cleanly passes.

**2. Does history survive static-geography control?** Outcomes are unit-demeaned (indiv x cell / route / station), so HG is measured net of static site means; M0 R2 ~0 by construction.

**3. Does history survive lagged-env control (M5 vs M6)?** BBS: M6-M5 median = 0.061; elk: 0.050; FOSS: NA.

**4. Memory decay?** bbs: h1=0.661, h2=0.633, h3=0.601, h5=0.514; elk: h1=0.022, h2=-0.004, h3=-0.003, h5=0.006, h12=0.054; foss: h1=0.033, h2=0.023, h3=0.011, h5=0.008; neon: h1=0.301, h2=NA, h3=NA, h6=NA, h12=-0.085; wolf: h1=-0.050, h2=-0.068, h3=-0.023, h5=-0.000, h12=-0.172; 

**5. Matched-environment path dependence?** FOSS: P(occ|occupied prior yr)=0.889 vs 0.396 without prior. BBS matched-env rows n=33449.

**6. Redistribution lag after env shifts?** foss_shift_lag.csv: post-shift CPUE changes at |BT anomaly|>1sd years; see D_shift vs D_post3 columns.

**7. Observation-persistence ruled out?** Partially: env-only + AR(1) sampling noise yields P(HG>0.05)=0.70-0.85 for FOSS/BBS-sized panels and median sim HG 0.09-0.24. BBS observed HG exceeds p95; FOSS and elk medians do not.

**8. Subgroup mining?** None performed: prespecified species lists only.

**9. Serengeti retuned?** No — locked discovery dataset untouched.

**10. Systems actually replicated?** GPS-individual (elk), marine trawl (FOSS), terrestrial bird survey (BBS), NEON small mammal (partial). Bathurst caribou unavailable (Movebank-gated).

**11. Honest limits?** Elk env is cell-invariant (climate monthly); wolf too sparse; NEON partial coverage; FOSS HG consistent with autocorrelation null.

**12. Final call?** See verdict below.

## VERDICT: WEAK GO

BBS shows distributional inertia far above the observation-persistence null (population-level history dependence). Elk gives positive individual-level HG but within the sampling-null envelope — consistent with, not proof of, individual spatial memory. FOSS HG is below the simulated null median. STRONG GO requires both a GPS-individual and a population system to clear the null; only the population side does.
