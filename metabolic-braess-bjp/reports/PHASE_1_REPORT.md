# Phase 1 Report — Model acquisition, freezing, QC

## Models (frozen; sha256 recorded)
| model | file | version/commit | rxns | mets | genes | sha256 (prefix) |
|-------|------|----------------|------|------|-------|-----|
| Human-GEM | models/human2/Human-GEM.xml | v2.0.1 (93e8d29) | 12,877 | 8,460 | 2,848 | 6ce49b62 |
| Recon3DModel | models/recon3d/Recon3DModel_301.xml | v301 (967ff51) | 10,600 | 5,835 | 2,248 | 6f965381 |

## QC results (results/qc/)
- Human2: 1,660 boundary rxns, 1,293 blocked, 2,288 dead-end mets; ATP task
  (ATPM hydrolysis demand) under curated minimal medium: optimal, 120.0.
- Recon3D: 1,806 boundary rxns, 0 blocked, 1,010 dead-end mets; ATP task:
  optimal, 121.5.

## Environment (config/config.yaml `medium`)
- Boundary convention (both models): −v = uptake, +v = secretion.
- Uptakes: glucose (10), O2 (20), NH3/ammonia, phosphate, H2O, H+ (cap 100).
- Secretions: canonical wastes only — H2O, CO2, l-/d-lactate, urea, NH3,
  Pi, H+, HCO3−, sulfate, acetate, formate, pyruvate, bilirubin, ROS
  (O2−/H2O2). All other exchanges closed.
- Conditions: aerobic (glc 10/O2 20), glucose_limited (glc 2/O2 20),
  oxygen_limited (glc 10/O2 2).

## Validated behaviour (no cheats)
- Both models: glucose −10, O2 −20, CO2 +20, ATP ≈ 120 (≈12 ATP/glc),
  canonical lactate/acetate excretion only, ZERO non-canonical fuel imports
  and ZERO disproportionation cycles under curated medium.
- Extended audit trail: open/native exchanges permit ATP/ADP import and
  polyol-fuel disproportionation (ATPM → 1000, glucose unused); the curated
  closed medium with correct sign convention is the environment that forces
  canonical metabolism. Documented, not model-edited.
- Known limitation: Human-GEM does not enforce a physiological P/O ratio on
  ATP synthase (atp_per_o2 = 6 at baseline); reported as-is.
