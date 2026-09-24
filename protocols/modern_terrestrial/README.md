# Modern terrestrial adapter (Tier 2 — ecological translation)

Existing pipeline is preserved unchanged (`phase8b/`, `phase9/`, synthesis in
`geb/`). This adapter maps its outputs onto the Core Protocol export schema.
Do not redesign the study; only add the minimal analyses needed for
cross-system comparability (see VARIABLE_MAP.md "missing metrics" section).

- observation unit: BBS route-year (plus telemetry units in phase8b)
- spatial unit: survey route / site
- temporal unit: year (multi-decade panel)
- native metrics: History Gain decomposition, occupancy hysteresis,
  abundance state dependence, lag curves
