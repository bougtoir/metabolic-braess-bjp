# GEB journal-fit check

## Scope mapping

| GEB scope element | manuscript element |
|---|---|
| Macroecology | 116-species continental-scale comparative analysis |
| Species distributions | route-level occupancy/distribution dynamics, 1966–2024 BBS |
| Spatial and temporal dynamics | explicit decomposition of spatial persistence vs temporal history |
| Modelling | SDM-family models with lagged-state predictors, forward validation |
| Conceptual inference from broad-scale data | occupancy vs abundance state-dependence contrast; falsification design |

GEB regularly publishes BBS-based macroecology and distribution-dynamics
papers with strong conceptual framing; the occupancy/abundance distinction
and the persistence-vs-memory decomposition fit the journal's taste for
"pattern + mechanism discipline" papers. The paper should be written as
biogeography with a methodological spine — the statistics serve the
question, not vice versa.

## Likely editor concerns

| concern | manuscript response |
|---|---|
| "Is this a methods paper?" | Framing leads with the biological distinction (distribution persistence vs abundance state dependence); Methods push implementation detail; figures are ecological. |
| "Scope too narrow?" (one survey, one continent, birds) | Continental scale, 116 species, 58 years; limitation acknowledged; generality argued conceptually not empirically. |
| "Negative result framing?" | Falsification is explicit and is the paper's contribution — the journal publishes null-consistent macroecology when the decomposition is novel. |
| "Is the abundance result just trivial autocorrelation?" | Addressed via matched-environment design + observer controls + framing as demographic state dependence (see REVIEWER_RISK). |

## Likely reviewer objections — coverage map

See `GEB_REVIEWER_RISK.md` for the full 10-objection table. Summary of
which existing analyses already answer each:

- already covered: forward-chaining leakage (regression-tested), lagged
  env control, observer-covariate control, common eval samples, simulation
  falsification, survey-semantics correction.
- partially covered: observer *persistence* (covariates yes, matched
  observer-turnover no — one optional analysis, see GAP_AUDIT §10).
- wording/discipline needed: bounded environmental adjustment claim,
  "widespread species" scope, route-demean interpretation.

## Fit verdict

Fit is real. The main risk is presentation: if the paper reads as a
statistical debunking it will be seen as narrow; if it reads as a
redefinition of what lagged distributions mean biogeographically, it fits
GEB's core readership.
