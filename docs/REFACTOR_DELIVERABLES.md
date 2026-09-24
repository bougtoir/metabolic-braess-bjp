# Refactor deliverables & status (spec §27)

## Delivered in this branch

1. `docs/EXISTING_PROTOCOL_AUDIT.md` — audit of dinosaur / modern terrestrial /
   modern-marine candidate portfolio (Phase 1, no code altered).
2. `docs/CORE_PROTOCOL_V1.md` — fixed vs variable items, nine core metrics
   (M1–M9) with implementation/alternative/normalization/export definitions;
   reconciled with the frozen program-level `CORE_PROTOCOL_v1.docx`
   (`docs/reference/`).
3. `protocols/{dinosaur,cenozoic_mammals,quaternary,ancient_marine,
   modern_terrestrial,modern_marine}/` — README, config.yaml, VARIABLE_MAP,
   OBSERVATION_MODEL, PROTOCOL_DEVIATIONS (+ MARINE_TRANSLATION_MAP for
   ancient marine).
4. `docs/DINOSAUR_PROTOCOL_CANONICAL.md` — extracted reference protocol.
5. `results/common_metrics/schema.yaml` + `src/common/export_common_metrics.py`
   — common result schema and exporters.
6. `results/observation_model_matrix.csv` — six-system bias matrix.
7. `results/common_metrics/common_metrics_{dinosaur,cenozoic,
   modern_terrestrial,modern_marine}.csv` — exports for available systems.
8. `results/cross_system_comparison.csv` — cross-system table (native +
   standardized, direction, robustness, bias sensitivity; NA where a system
   has not exported yet).
9. `docs/MODERN_PROTOCOL_COMPATIBILITY_AUDIT.md` — modern-system mapping and
   minimal additions.
10. `tests/regression/` + `tests/regression/baselines.json` — dinosaur and
    phase9 key-value regression tests (11 tests, passing).
11. `cenozoic_mammals/` — Tier-1 strict replication implemented end-to-end
    (PBDB NOA mammals, 23–5 Ma): fetch, clean, Δβ bootstrap/Mantel, five
    sampling corrections, aggregation ladder, genus-pool nulls, report.
12. `simulation/` skeleton — core + three observation-model adapters
    (spec §17 layout; dinosaur/modern simulators migrate next refactor).
13. Root `Makefile` — `make dinosaur|cenozoic|...|common_metrics|synthesis`.

## Cenozoic strict-replication result (new)

North American mammals, 23–5 Ma, 12 248 terrestrial occurrences / 2 102
collections (378 herbivore / 131 predator genera):

- Δβ_Simpson = **−0.028** [−0.040, −0.018], P(Δ>0)=0 — same sign as dinosaur
  (predator turnover *lower* than herbivore).
- Mantel distance decay: herbivore r=0.088, predator r=0.103, both p<0.001
  (weak but nonzero decay — unlike Morrison's r≈0).
- All five sampling corrections preserve the sign.
- Aggregation ladder: Δβ strengthens to ≈ −0.08 at epoch/5 Ma/1 Ma bins
  (fine binning does not weaken the contrast).
- Genus-pool nulls: observed Δβ sits at quantile ≈ 0.33 of size-matched and
  label-shuffle nulls — the small negative contrast is **null-consistent**:
  the direction replicates, the magnitude does not exceed guild-pool
  asymmetry expectations → **Class B (partial replication)**, not A.

## System status

SYSTEMS FULLY COMPATIBLE:
dinosaur (reference), cenozoic (strict replication, all core metrics exported)

SYSTEMS PARTIALLY COMPATIBLE:
modern_terrestrial (M2–M9 mapped; M1 guild Δβ missing — minimal add or
documented NA), modern_marine (M4/M6/M7 direct; M1/M3 translated via path
coefficients and centroid displacement)

SYSTEMS REQUIRING ADDITIONAL ANALYSIS:
quaternary, ancient_marine — adapter specs written; pipelines are being
built in parallel sessions (第四期回遊, 古生代海洋回遊) and export into this
schema when they land.

MAIN CROSS-SYSTEM COMPARABILITY RISK:
guild-pool asymmetry drives Δβ magnitude independent of ecology — the
size-matched null is the essential discriminator; naive comparison of raw
Δβ across systems would conflate sampling structure with signal.

ONE ESSENTIAL HARMONIZATION STEP:
every Tier-1/2 system must export its size-matched genus-pool null alongside
Δβ (already mandatory via M7; make `null_pool_quantile` a required schema
metric in v1.1).
