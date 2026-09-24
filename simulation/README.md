# Simulation architecture (spec §17-18)

`simulation/core/` holds the shared ecological generating process:
species ranges → trophic structure → dispersal → environmental forcing.

Adapters pass the SAME ecological signal through different observation
models:

| Adapter | Observation process |
|---|---|
| `terrestrial_fossil/` | fossil preservation, locality sampling, time aggregation, spatial pooling |
| `marine_fossil/` | depositional/facies filtering, stratigraphic condensation, collection intensity |
| `modern_observation/` | observer detection, survey effort, route structure, imperfect detection |

Purpose: estimate, per system, `Observed Effect − True Effect` (observation
distortion), linking fossil incompleteness, modern detectability,
sampling-pool restriction, and time aggregation under one framework.

Baseline: the dinosaur 2-D simulation machinery migrates into
`simulation/core/` in a follow-up refactor (this branch sets the layout;
dinosaur's in-repo simulations — `phase9/src/sim9.py`, `phase8b/src/sim_fp.py`
for the modern side — remain in place until their outputs are regression-pinned).
