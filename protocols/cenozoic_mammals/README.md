# Cenozoic mammals adapter (Tier 1 — strict replication)

Strict replication of the dinosaur protocol on Cenozoic terrestrial mammals,
primary interval **23–5 Ma** (Miocene–Pliocene, configurable), default region
North America (PBDB `cc=NOA`). Code: `cenozoic_mammals/`.

- lower trophic: herbivorous terrestrial mammals (ungulates + herbivorous
  small mammals; see `config.yaml` `guilds.herbivore_orders`)
- higher trophic: order Carnivora (terrestrial families only)
- spatial unit: PBDB collection, centroid = median coords
- temporal unit: coarse primary bin (single pooled 23–5 Ma window);
  sensitivity ladder stage/subepoch/1 Ma for metric M6
- primary metric: Δβ Simpson, identical estimand & corrections as dinosaur

Reproduce:

```bash
cd cenozoic_mammals
python3 src/fetch_pbdb_cenozoic.py   # PBDB 1.2 API, no auth
make all                             # audit -> clean -> beta -> sampling -> aggregation -> report
```
