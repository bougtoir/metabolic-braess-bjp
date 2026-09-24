# Statistical issues register (post-audit)

| # | issue | status | action_taken | residual_risk | manuscript_location |
|---|---|---|---|---|---|
| 1 | Protocol cited pool4→−0.41; actual −0.41@pool2, −0.17@pool4 | RESOLVED | both values reported; pool4 = main example, pool2 = labelled extreme; GAMMA_VALUE_AUDIT confirms no stale statement | none | Results 1 |
| 2 | Presence-model MLE non-convergence (separation: state coefs ≈17) | RESOLVED WITH LIMITATION | L2-penalized refit converges; pseudo-R² = 0.34 (C=1) vs 0.46 unpenalized — same qualitative conclusion; both flagged exploratory | penalized fit still in-sample | Results 5, Methods |
| 3 | Bias-term non-independence | RESOLVED | additive form explicitly labelled conceptual scaffold; factorial grid is the interaction evidence | readers may still over-read additivity | Methods, Results 3 |
| 4 | Nemegt gamma-null degeneracy | RESOLVED WITH LIMITATION | Nemegt framed as structural comparator only; no powered replication claim | none material | Results 6 |
| 5 | Bootstrap/null interval semantics | RESOLVED | captions distinguish observed bootstrap CI vs null simulation interval | none | Fig.5 caption |
| 6 | Species-level sensitivity to ambiguous IDs | OPEN BUT NON-CRITICAL | not quantified; flagged | moderate | Results 5 |
| 7 | 1-D simulator | RESOLVED WITH LIMITATION | stated explicitly; magnitudes are demonstration not calibration | transportability limited | Methods, (Discussion) |
| 8 | Sampling-asymmetry parameter range | RESOLVED WITH LIMITATION | wording limited to "within the parameter range examined" | stronger coupling untested | Results 2 |

No item remains OPEN AND MANUSCRIPT-CRITICAL.
