# Analysis plan — Allosaurus spatial ecology (exploratory)

Execution order follows the inference hierarchy; earlier gates must be
cleared before mobility is even discussed.

1. `analysis/01_allosaurus_mechanisms.py` — produces all tables:
   - `allo_L_attenuation.csv` — Δβ_genus, Δβ_species, L = Δβ_genus − Δβ_species
     with collection-bootstrap CIs (Jaccard, genus↔species resolution).
   - `allo_occupancy.csv` + `figures/map_*.png` — occupancy and spatial
     extent for Allosaurus (genus), A. fragilis, A. jimmadseni, and the
     next best-sampled Morrison theropods.
   - `allo_duration_model_*.csv` — OLS: spatial extent ~ stratigraphic
     duration + occurrence count + guild; Allosaurus z-residual reported.
   - `allo_presence_logit.csv` — logistic model of Allosaurus presence per
     collection on environment/lithology/member/state/systems-tract/
     richness (exploratory; separable dummies noted).
   - `allo_predator_comparison.csv` — occupancy, extent, hull area,
     duration, environmental breadth for every Morrison theropod genus.
   - `allo_matched_taxa.csv` + `allo_matched_percentiles.csv` — nearest
     taxa matched on occurrence count and duration.
   - `allo_regional_generalism.csv` — Allosaurus share of collections per
     region vs regional herbivore turnover (indirect generalism evidence).
2. `analysis/02_allo_report.py` — renders `results/allosaurus_mechanism_report.md`
   from the tables and assigns the exploratory classification.

Not run (per protocol): Hell Creek, modern GPS analogues, any migration
claim.
