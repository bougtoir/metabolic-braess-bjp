# Modern marine adapter (Tier 2 — ecological translation)

Existing pipelines are preserved (`marine_dataset_screen/`,
`palmyra_trophic_mobility/`, `ecomega_trophic_propagation/`,
`topp_tracking_modes/`, `capelin_seabird_positive_control/`). The sibling
"海洋生物回遊" session is still running; this adapter maps current outputs
and will be updated when that session's final system settles.

- observation unit: matched survey unit (tow-anchored) / telemetry track-day
- spatial unit: survey grid / CCS window / archipelago network
- temporal unit: event-based + daily
- native metrics: Type-A/Type-B discrimination, mediation, event-holdout CV,
  lag curves, centroid displacement
