# Preregistered validation hypotheses (Stage 1c)

Frozen BEFORE analysing any independent validation dataset's guild-turnover
outcome. Do not modify after inspecting validation results.

## Discovery context (frozen Stage 1a/1b)

- Original confirmatory H1 (Δβ > 0): **falsified**, Δβ ≈ −0.54 to −0.65.
- Stage 1b (exploratory): reverse signal robust across strata, intervals,
  metrics, and scales, but **mostly Allosaurus-driven** (C2: Δβ ≈ 0 without
  it) and inside the taxon-pool-matched null interval.

## Primary validation hypothesis

H_new: Δβ < 0 — predator community spatial turnover is lower than
herbivore community turnover.

H0: Δβ ≥ 0 (one-sided confirmatory design, prospectively specified here).

## Frozen analysis specification

- **Primary effect**: Δβ = β_P − β_H, mean pairwise dissimilarity between
  collection-level assemblages.
- **Primary metric**: Jaccard presence/absence dissimilarity (as recommended;
  Simpson and Sorensen are secondary sensitivity metrics only).
- **Primary spatial unit**: collection (assemblage). Grid-pooling analyses
  are secondary sensitivity only.
- **Primary taxonomic resolution**: genus (accepted genus names; species-level
  is secondary sensitivity only).
- **Guild definitions**: predator = Theropoda occurrences; herbivore =
  non-theropod dinosaur occurrences (sauropodomorphs + ornithischians).
  Occurrences without genus resolution are excluded from matrices.
- **Primary statistical model**: bootstrap over collections (999 resamples)
  → 95% percentile CI for Δβ. Decision criterion: confirmatory replication
  requires the bootstrap 95% CI to lie entirely below 0
  (one-sided α = 0.025 boundary).
- **Required bias controls reported alongside**: taxon-pool-matched null
  (herbivore subsampled to predator gamma, B = 10,000) and dominant-taxon
  exclusion sensitivity (exclude the most abundant predator genus).

## v2 amendment (2026-09-20, pre-Nemegt)

Amended prospectively BEFORE viewing any Nemegt outcome. v1 preserved in
git history. Stage-1b interpretation is now classified as
**ALLOSAURUS-SPECIFIC SPATIAL CONTINUITY**, not a generic predator-guild
effect.

### Validation dataset selection (locked)

- **Primary validation dataset: Nemegt Formation** (Maastrichtian, Mongolia;
  independent of Maidment 2024 — separate continent, formation, and faunal
  pool; PBDB extraction).
- Estimated record overlap with Maidment 2024: **0%** (different formation
  and continent; overlap concept applies only to a Morrison re-extraction,
  which was rejected).
- Secondary dataset (only if Outcome A or B): **Hell Creek Formation**,
  dominant predator prospectively defined as *Tyrannosaurus*.
- Tendaguru: analogue context only.

### Hypothesis set (two distinct hypotheses)

**H1,guild (primary replication hypothesis)**

    Δβ = β_P − β_H < 0

Replication of the unexpected Morrison pattern at guild level.

**H2,dominant (mechanistic / dominant-predator hypothesis)**

Define a dominant large theropod taxon D, fixed prospectively:

- Nemegt: D = *Tarbosaurus* (chosen BEFORE inspecting Nemegt results).
- Hell Creek (if analysed): D = *Tyrannosaurus*.

Operational form:

    Δβ_full < 0   but   Δβ_{-D} → 0 or materially less negative

**Dominant-predator attribution quantity (defined before viewing results):**

    A_D = Δβ_{-D} − Δβ_full

Large positive A_D indicates the dominant predator accounts for much of the
guild-level continuity. A_D is reported with its bootstrap distribution
(same collection resamples applied to both Δβ terms, 999 replicates).

### Locked Nemegt analysis (order frozen)

1. **Full data**: Δβ_full (Jaccard, genus, collection-level) + bootstrap
   95% CI. Replication criterion: CI entirely below 0. Not modifiable.
2. **Tarbosaurus removed**: Δβ_{-Tarbosaurus} + bootstrap 95% CI.
3. **Tarbosaurus downsampled** (stochastic replication, R = 999 per level):
   to median predator occurrence count; to 75th-percentile predator
   occurrence count; to 50% of original count.
4. **Attribution**: A_D and its bootstrap distribution.
5. Required bias controls from v1 (taxon-pool-matched null B = 10,000).

### Mandatory taphonomic diagnostics (Nemegt)

Motivation: Tarbosaurus dominates skeletal collections while footprint
assemblages indicate herbivore dominance — possible preservational bias.
Assess, before biological interpretation: collection/occurrence counts of
Tarbosaurus by depositional environment and lithology; collection type;
sampling-intensity proxies (occurrences per collection); whether
Tarbosaurus occurs preferentially in particular preservational settings.
Any integrated footprint-locality data are treated as an independent
qualitative/quantitative taphonomic comparison.

### Replication classification (frozen, replaces v1 qualitative rules)

- **Outcome A — GENERIC REPLICATION**: Δβ < 0 (CI below 0) and remains
  negative after removing Tarbosaurus → predator-guild continuity
  replicates independently.
- **Outcome B — DOMINANT-PREDATOR REPLICATION**: Δβ_full < 0 but
  Δβ_{-Tarbosaurus} attenuates substantially toward zero → one spatially
  pervasive dominant theropod drives guild continuity (the most
  interesting replication scenario).
- **Outcome C — TAPHONOMIC REPLICATION**: Δβ < 0 but strongly attributable
  to preservational structure → fossil-record bias; weakens the movement
  hypothesis but remains a methodological result.
- **Outcome D — NO REPLICATION**: Δβ ≈ 0 or positive. Documented
  transparently.

Only on Outcome A or B does Hell Creek proceed under the identical locked
framework (Δβ_full, Δβ_{-Tyrannosaurus}, A_D). The cross-formation
synthesis ("dominant large theropods repeatedly generated spatial
continuity") is formulated only if Morrison + Nemegt (+ Hell Creek) share
the structure.

## Interpretation guardrails (extended)

- **Spatial continuity ⇒ migration is forbidden.** Candidate explanations
  include: high individual mobility, large home range, seasonal migration,
  dietary generalism, broad environmental tolerance, temporal persistence,
  taxonomic lumping, preservation bias. The validation question is spatial
  continuity only.
- Mobility (M) and dietary generalism (G) must be separated in any later
  factorial simulation.
- Evolutionary framing deferred: at most "deeper evolutionary antecedents
  of theropod spatial mobility" as a Discussion point, never bird-
  migration analogy as evidence.
- Bird migration is not evidence for Allosaurus migration.
- Language discipline: "consistent with", "supports"; never "confirmed"
  until independent replication plus mechanism support.

- Spatial continuity does not imply migration; mechanisms M1–M5 (predator
  mobility, dietary generalism, environmental tolerance, taxonomic/temporal
  persistence, combined) remain open until Stage-2 mechanism testing.
- Bird migration is not evidence for Allosaurus migration.
- Language discipline: "consistent with", "supports"; never "confirmed"
  until independent replication plus mechanism support.
