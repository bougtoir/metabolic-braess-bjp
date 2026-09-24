# NATURE_PAPER_SKELETON (Phase-8B scaffold only — not a manuscript)

Title (working): Spatial memory and distributional inertia across independent animal survey systems

## Abstract skeleton
- Question: does past space use predict current distribution beyond environment?
- Systems: individual GPS (elk), fishery trawl (FOSS), bird survey (BBS), [NEON small mammal].
- Result scaffold: history-gain sign + magnitude per system; FP-screen caveats.
- Implication: population-level persistence vs individual route fidelity are separable.

## Figures (map to results/figures)
- Fig 1: HG by system/species (evidence strength)
- Fig 2: EG (env gain over history) — shows env adds little once history included
- Fig 3: model hierarchy M0–M6 per system
- Fig 4: memory decay curves
- Fig 5: matched-environment path dependence scatter
- Fig 6: post-shift response distribution
- Fig 7: false-positive HG rates under env-only + observation-persistence sims
- Fig 8: temporal coverage per system
- Fig 9: HG vs EG scatter

## Key tables
- results/tables/{foss,bbs,elk,wolf,neon}_history_gain.csv
- *_memory_decay.csv, *_matched_env.csv, *_shift_lag.csv
- simulation_false_positive.csv

## Interpretation boundaries (to hold in manuscript)
- BBS/FOSS HG>0 is common under observation-persistence nulls → population-level claims must rest on magnitude above simulated nulls and matched-env evidence, not HG sign.
- Elk provides individual-level evidence (per-animal HG distribution).
- Wolf excluded for sparse coverage; Bathurst caribou unavailable (Movebank-gated).
