# Core Protocol adapter

The Core Protocol is defined in `docs/CORE_PROTOCOL_V1.md` (normative) and
`results/common_metrics/schema.yaml` (the export contract). This directory
holds only the shared vocabulary — it contains no data.

## Adapter contract

Every system directory under `protocols/` must contain:

| File | Contents |
|---|---|
| `README.md` | system summary + how to run |
| `config.yaml` | tier, interval, region, seeds, guild definitions |
| `VARIABLE_MAP.md` | core metric → system variable/table mapping |
| `OBSERVATION_MODEL.md` | observation process vs biological process |
| `PROTOCOL_DEVIATIONS.md` | every deviation from the dinosaur reference, with justification |

Plus system-specific extras:
- `protocols/ancient_marine/MARINE_TRANSLATION_MAP.md`
- `protocols/modern_terrestrial/VARIABLE_MAP.md` (maps phase8b/phase9 metrics)
- `protocols/modern_marine/VARIABLE_MAP.md`

Each system exports `results/common_metrics/common_metrics_<system>.csv`
conforming to `results/common_metrics/schema.yaml`. The exporter lives at
`src/common/export_common_metrics.py` and reads each system's own committed
result tables — it never re-runs raw analysis.
