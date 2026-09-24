# Dinosaur observation model

**Biological process**: Late Jurassic herbivore ranges / migration vs predator
assemblage turnover.

**Observation process**: PBDB-curated fossil collections (Maidment 2024
package). Collection ≠ locality-day — collections aggregate quarries over
variable temporal windows; monodominant bone beds inflate herbivore counts;
gamma-pool asymmetry (12 predator vs 26 herbivore genera, ~70% Allosaurus)
depresses observed predator turnover independent of ecology.

**Preservation**: taphonomic filter — small/juvenile taxa underrepresented;
quarry sampling concentrated in Morrison bone beds.

**Corrections applied**: dominant-quarry exclusion, singleton exclusion,
collection-count equalization, 1° thinning; Nemegt taphonomic diagnostics
(`nemegt_taph_*.csv`).

**Known residual biases**: guild pool asymmetry (addressed by 1b nulls, not
eliminated); formation-level time averaging hides seasonal migration.
