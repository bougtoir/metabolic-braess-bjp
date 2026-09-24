# Outcome of the original project — frozen

Project: *Migration-sustained dinosaur food webs* — test whether Late
Jurassic (Morrison) predator communities show higher spatial turnover than
herbivore communities because large herbivores coupled the basin through
seasonal movement (Bakker-style migratory-prey hypothesis).

## 1. Original hypothesis

H1: Δβ = β_predator − β_herbivore > 0 (predator communities turn over
faster in space because mobile herbivores homogenise prey communities).

## 2. Morrison result (opposite direction)

Δβ_Simpson = −0.543 (95% collection-bootstrap CI [−0.623, −0.452]),
Δβ_Sørensen = −0.549. Predator assemblages are spatially **more**
continuous than herbivore assemblages. Robust across systems tracts,
Kimmeridgian/Tithonian bins, all three dissimilarity metrics, and all
spatial scales (collection, 50/100/150 km grids).

## 3. Exploratory attribution (Stage 1b)

The reverse signal is **Allosaurus-dependent**: removing Allosaurus
reduces Δβ to ≈ 0; downsampling attenuates or reverses it; splitting to
species level attenuates it. The signal lies inside the taxon-pool-matched
null interval but below all frequency-matched nulls. Classified
exploratorily as **ALLOSAURUS-SPECIFIC SPATIAL CONTINUITY** — never
treated as confirmation of generic predator mobility.

## 4. Prospective Nemegt validation

Preregistered (VALIDATION_HYPOTHESES.md v2, commit e9acfdad): H1,guild
Δβ < 0; dominant predator fixed as Tarbosaurus; Jaccard, genus level,
collection assemblages; replication requires the bootstrap 95% CI entirely
below 0.

## 5. Failure to replicate

Nemegt: Δβ_full = +0.094 (95% CI [−0.079, +0.300]); Δβ_{−Tarbosaurus} =
+0.134; A_D = +0.040. Classification per the locked rules:
**NO REPLICATION (Outcome D)**.

> The unexpected Morrison predator-continuity signal did not replicate in
> an independently specified Late Cretaceous dinosaur assemblage. The
> Morrison effect was therefore not treated as evidence for a general
> theropod or predator-guild spatial-continuity phenomenon.

## 6. Decision

The confirmatory inferential chain is frozen and closed. No additional
post hoc formations were or will be searched for a desired sign. Hell
Creek is not analysed as a confirmatory replication attempt; the
originally planned Stage-2 modern-GPS validation is not part of this
project any more. See `NATURE_GO_NO_GO.md` (classification: **NO-GO**).

## Commit trail (preserved)

| commit | content |
|---|---|
| f8684e1b | Stage 1 pipeline + Morrison beta-diversity test |
| 4f4b6372 | Freeze of H1 falsification (stage1a) |
| d1fdcacf | Stage 1b exploratory analyses A–G |
| 4a67c8c4 | Preregistration v1 (reverse hypothesis) |
| 7cbff000 | Bootstrap/estimand bugfixes (verdict unchanged) |
| e9acfdad | Preregistration v2 (Tarbosaurus, A_D, locked Nemegt) |
| 9ff5e093 | Locked Nemegt validation — NO REPLICATION |
