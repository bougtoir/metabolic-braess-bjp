# Project plan — Migration sustained dinosaur food webs

Target journal: Nature. See `ANALYSIS_PLAN.md` for the analysis design and
stage gates, `DATA_SOURCES.md` for data provenance.

## Concept

Traditional: local herbivore abundance -> local predator abundance.

Proposed: seasonal vegetation -> mobile herbivore biomass -> spatial prey
subsidy -> multiple predator populations. Fossil predator/prey ratios are
time-integrated projections of moving populations, so R_fossil may differ
systematically from R_instantaneous.

## Questions

1. Could dinosaur food webs have been sustained by repeated spatial reuse of
   the same mobile herbivore biomass?
2. Does seasonal herbivore movement make fossil predator/prey ratios differ
   systematically from instantaneous ratios?

## Guilds and study system

Morrison Formation (Late Jurassic, ~163–145 Ma window in this dataset),
western USA. Herbivores: sauropods + ornithischians (Camarasaurus, Diplodocus,
Apatosaurus, Stegosaurus, Camptosaurus, ...). Predators: large theropods
(Allosaurus, Ceratosaurus, Torvosaurus, ...). Genus- and species-level where
resolution permits.

## Deliverables (ordered)

1. PROJECT_PLAN.md / DATA_SOURCES.md / ANALYSIS_PLAN.md (done)
2. Reproducible data acquisition (done; `src/download/fetch_data.py`)
3. Morrison data audit (done; `analysis/01_data_audit.py`)
4. Taxonomy reconciliation (done; `metadata/taxonomy_reconciliation.csv`)
5. Spatial occupancy (done; `analysis/04_spatial_occupancy.py`)
6. Herbivore vs predator beta diversity (done; `analysis/05_beta_diversity.py`)
7. Sampling-bias sensitivity (done; `analysis/06_sampling_bias.py`)
8. Modern GPS dataset acquisition + artificial fossilization (Stage 2)
9. SRF estimator + fossil ratio correction (Stage 3)
10. Energetics / movement / food-web persistence models (Stage 4)
11. Remote-collapse network analysis (Stage 5)
12. Figures, manuscript, cover letter, reproducibility checklist

## Manuscript discipline

Prefer "consistent with", "supports", "increases the plausibility of" over
"proves". Distinguish observed fossil pattern, model-derived inference,
modern validation, and speculation. Document negative findings; do not
rescue the hypothesis post hoc.
