# Cenozoic mammals — strict replication of the dinosaur protocol

Tier-1 strict replication (see `protocols/cenozoic_mammals/`): Cenozoic
terrestrial mammals, North America, 23–5 Ma (Miocene–Pliocene), PBDB 1.2 API.

- lower trophic: herbivorous orders (Artiodactyla, Perissodactyla,
  Proboscidea, Lagomorpha, Rodentia, Xenarthra, Cingulata)
- higher trophic: Carnivora minus marine families (pinnipeds, Enaliarctidae,
  Desmatophocidae)
- primary estimand: Δβ = mean pairwise Simpson turnover(predator) −
  (herbivore); bootstrap 999; Mantel 9999 — identical to dinosaur
- identical five-correction sampling battery + aggregation ladder + genus-pool
  nulls (promoted to required negative controls)

## Reproduce

```bash
pip install -r requirements.txt
python3 src/fetch_pbdb_cenozoic.py   # or `make data`
make all                             # audit -> clean -> beta -> sampling -> aggregation -> null
```

Raw CSV is committed (`data/raw/pbdb_cenozoic/occurrences_NOA_23-5ma.csv`),
so `make all` runs offline. Deviations from the dinosaur reference are
enumerated in `protocols/cenozoic_mammals/PROTOCOL_DEVIATIONS.md`.
