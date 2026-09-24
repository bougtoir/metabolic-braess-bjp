# Cenozoic mammals — deviations from the dinosaur reference

| # | Deviation | Reason |
|---|---|---|
| 1 | Guild defined by order list (herbivores) + Carnivora, not a single clade field | PBDB mammals have no single `class` guild flag; orders encode trophic role |
| 2 | Pinnipeds (Phocidae/Otariidae/Odobenidae) excluded from Carnivora | marine predators; terrestrial-comparable only |
| 3 | Temporal aggregation ladder added (epoch/subepoch/1 Ma) | Cenozoic collections carry finer chronostratigraphy; pooled window alone would discard a strength of this system (per spec §8-adjacent rationale) |
| 4 | Region = continental North America (cc=NOA), not a single formation | no single Cenozoic formation spans 23–5 Ma; continental pool is the smallest unit giving a usable pair count per guild |
| 5 | Null models = genus-pool size-matched + frequency-matched (1b-style) run as primary nulls | guild pool asymmetry (Carnivora << herbivore orders) is known a priori; nulls promoted from exploratory to required |

All five dinosaur sampling corrections are implemented unchanged
(`analysis/04_sampling_bias.py`).
