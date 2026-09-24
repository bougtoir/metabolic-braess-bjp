# Dinosaur adapter (Tier 1 — reference implementation)

Reference implementation of the Core Protocol. Canonical description:
`docs/DINOSAUR_PROTOCOL_CANONICAL.md`. Code: `dinosaur_migration_foodweb/`.

- lower trophic: Sauropoda + Ornithischia genera
- higher trophic: Theropoda genera
- spatial unit: collection (centroid = median coords)
- temporal unit: Morrison pooled assemblage; validation: Nemegt
- primary metric: Δβ Simpson, collection bootstrap (999), Mantel (9999)

Export: `src/common/export_common_metrics.py --system dinosaur`.
