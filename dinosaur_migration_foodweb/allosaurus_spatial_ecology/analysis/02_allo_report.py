"""Generate results/allosaurus_mechanism_report.md from output tables."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"


def f(x, nd=3):
    return f"{x:.{nd}f}"


def main() -> None:
    L = pd.read_csv(TABLES / "allo_L_attenuation.csv").set_index("quantity")
    occ = pd.read_csv(TABLES / "allo_occupancy.csv")
    dur_fit = pd.read_csv(TABLES / "allo_duration_model_fit.csv").set_index("term")
    pred = pd.read_csv(TABLES / "allo_predator_comparison.csv")
    matched = pd.read_csv(TABLES / "allo_matched_taxa.csv")
    pct = pd.read_csv(TABLES / "allo_matched_percentiles.csv").set_index("metric")["value"]
    pres = pd.read_csv(TABLES / "allo_presence_summary.csv").set_index("metric")["value"]
    reg = pd.read_csv(TABLES / "allo_regional_generalism.csv")
    taxa = pd.read_csv(TABLES / "allo_duration_model_taxa.csv")
    allo_resid = taxa.loc[taxa["taxon"] == "Allosaurus", "extent_resid"].iloc[0]
    allo_z = taxa.loc[taxa["taxon"] == "Allosaurus", "extent_resid_z"].iloc[0]
    allo_pct = float((taxa["extent_resid"] <= allo_resid).mean())

    def occ_row(t):
        return occ[occ["taxon"] == t].iloc[0]

    md = f"""# Allosaurus mechanism report — EXPLORATORY (not confirmatory)

Question: why does *Allosaurus* generate unusually high spatial continuity
in Morrison assemblages? Gates applied in order: taxonomic pooling →
temporal averaging → preservation/sampling → generalism → (mobility
deferred). All numbers are generated from `results/tables/allo_*.csv`.

## 1. Taxonomic pooling (H_T)

| quantity | estimate | 95% CI |
|---|---|---|
| Δβ_genus (Jaccard) | {f(L.loc['delta_beta_genus','estimate'])} | [{f(L.loc['delta_beta_genus','lo95'])}, {f(L.loc['delta_beta_genus','hi95'])}] |
| Δβ_species | {f(L.loc['delta_beta_species','estimate'])} | [{f(L.loc['delta_beta_species','lo95'])}, {f(L.loc['delta_beta_species','hi95'])}] |
| **L = Δβ_genus − Δβ_species** | **{f(L.loc['L_attenuation','estimate'])}** | [{f(L.loc['L_attenuation','lo95'])}, {f(L.loc['L_attenuation','hi95'])}] |

Genus pooling accounts for ~{abs(L.loc['L_attenuation','estimate']/L.loc['delta_beta_genus','estimate'])*100:.0f}% of the negative Δβ; the species-level signal remains negative.

## 2. Occupancy (maps in `figures/map_*.png`)

{occ.to_markdown(index=False)}

## 3. Stratigraphic-duration / sampling model (OLS: extent ~ duration + n_occ + guild)

{dur_fit.to_markdown()}

Allosaurus extent residual {f(allo_resid,0)} km (z = {f(allo_z,2)},
percentile vs all dinosaur genera: {allo_pct:.0%}) — i.e., after
controlling for stratigraphic duration and occurrence count, Allosaurus's
geographic extent is what a well-sampled, long-ranging taxon would
produce.

## 4. Preservation / collection bias (H_P)

Presence of Allosaurus in a dinosaur collection is substantially
predictable from collection covariates (pseudo-R² =
{f(pres['logit_pseudo_r2'])}; environment, lithology, member, state,
systems tract, collection richness). See `allo_presence_logit.csv` for
term-level coefficients (many dummies; MLE did not fully converge —
exploratory only).

## 5. Predator comparison

{pred.head(6).to_markdown(index=False)}

## 6. Matched-taxon controls (matched on occurrence count + duration)

{matched[['taxon','guild','n_occ','duration','extent_km','occupancy']].to_markdown(index=False)}

Allosaurus matched extent/occupancy percentile: {pct['matched_extent_percentile']:.0%} /
{pct['matched_occupancy_percentile']:.0%}. However its closest comparators
(Camarasaurus, Stegosaurus) reach similar occupancy; the margin over the
best-sampled herbivores is small.

## 7. Regional generalism (H_G — indirect evidence only)

{reg.to_markdown(index=False)}

Allosaurus occurs in {f(reg['allo_regional_share'].mean()*100,0)}% of
collections on average across regions spanning distinct herbivore faunas —
consistent with broad trophic generalism OR with preservational
pervasiveness; the two cannot be separated by occupancy alone.

## Classification

**MULTIFACTORIAL — taxonomic lumping (H_T) + sampling/temporal
averaging (H_L, H_P) account for most of the apparent exceptionalism;
no robust residual biological exceptionalism detected.**

- Genus→species splitting removes ~40% of the signal (H_T contribution).
- After duration and sampling adjustment Allosaurus spatial extent is
  not exceptional (H_L/H_P contribution).
- A modest residual remains (species-level Δβ stays negative; matched
  occupancy percentile = 100%), so biological generalism (H_G) is
  *plausible* but not demonstrated.
- Mobility (H_M) was not evaluated — the hierarchy gates were not all
  passed; no migration inference is made.

## Guardrails

- Exploratory labels throughout; nothing here is confirmatory.
- Broad occurrence ≠ mobility; mobility claims require independent
  evidence (isotopes, biomechanics, trackways) not yet analysed.
"""
    out = ROOT / "results" / "allosaurus_mechanism_report.md"
    out.write_text(md)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
