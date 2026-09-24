# LOYO vs forward-chaining diagnostic

Same species inclusion, predictors (env + lag-1 vs env-only), response, and R2 metric in all four cells.

## 2x2 table (median over species)

| cell | CV | route demean | median HG | IQR | P(HG>0) |
|---|---|---|---|---|---|
| A | LOYO | no | 0.299 | [0.194,0.390] | 0.99 |
| B | LOYO | yes | 0.024 | [0.014,0.042] | 0.97 |
| C | forward | no | 0.315 | [0.204,0.407] | 0.98 |
| D | forward | yes | 0.006 | [0.000,0.014] | 0.77 |

Phase-8B-style year-demean LOYO HG_A_8Bstyle median: 0.598

## Effect decomposition

- CV effect (C-A): median 0.009, IQR [0.004,0.020], P(>0) 0.84, boot95 [0.007,0.047]
- demean effect, LOYO (B-A): median -0.262, IQR [-0.336,-0.171], P(>0) 0.01, boot95 [-0.280,-0.236]
- demean effect, forward (D-C): median -0.297, IQR [-0.403,-0.199], P(>0) 0.03, boot95 [-0.339,-0.272]
- residual forward HG (D): median 0.006, IQR [0.000,0.014], P(>0) 0.77, boot95 [0.005,0.011]

## Future-information

Delta_future_information median 0.013, HG_past_only median 0.006, HG_past_future median 0.020.

## Forward-chaining validity

- demeaning route means: train-only (fixed)
- env anomalies: fixed baseline <=2005, no future stats
- predictor centring in _fit: train-only column means (no SD scaling; complete-case rows, no imputation)
- inclusion rule: coverage counts only, no outcome info

## Training-size / window sensitivity

- min_hist 5: median HG 0.007, P(>0) 0.82
- min_hist 10: median HG 0.009, P(>0) 0.78
- min_hist 15: median HG 0.012, P(>0) 0.80
- window 10: median HG 0.002
- window 20: median HG 0.006
- window expand: median HG 0.006

## Pattern: Pattern 2 (static route persistence dominates)
