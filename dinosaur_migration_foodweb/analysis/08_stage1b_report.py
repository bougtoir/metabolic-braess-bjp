"""Generate results/stage1b_exploratory_reverse_signal.md from output tables.

Exploratory / hypothesis-generating only — no confirmatory claims for the
reverse biological hypothesis.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ROOT, TABLES


def fmt(x):
    return f"{x:.3f}" if pd.notna(x) else "NA"


def main() -> None:
    null = pd.read_csv(TABLES / "stage1b_null_summary.csv")
    A = null[null["analysis"] == "A_taxon_pool_null"].iloc[0]
    B = null[null["analysis"] == "B_freq_matched_null"].iloc[0]
    C = pd.read_csv(TABLES / "stage1b_C_allosaurus.csv")
    D = pd.read_csv(TABLES / "stage1b_D_systems_tract.csv")
    E = pd.read_csv(TABLES / "stage1b_E_intervals.csv")
    F = pd.read_csv(TABLES / "stage1b_F_resolution.csv")
    G = pd.read_csv(TABLES / "stage1b_G_metric_scale.csv")

    c = {r["scenario"]: r for _, r in C.iterrows()}

    md = f"""# Stage 1b — Exploratory reverse-signal characterization

**Status: exploratory, post hoc, hypothesis-generating.** The original
confirmatory hypothesis (Δβ > 0) was falsified and frozen in
`results/stage1_original_hypothesis_report.md`. Nothing here is confirmatory
evidence for the reverse biological hypothesis.

## Observed reverse effect

Δβ (Simpson, genus level, collection scale) = **{fmt(A['observed'])}**
(bootstrap 95% CI excludes 0; see Stage-1a report).

## A. Taxon-pool matched null (B=10,000)

Herbivore guilds subsampled to predator gamma diversity (12 genera):

- null mean {fmt(A['null_mean'])}, median {fmt(A['null_median'])},
  95% null interval [{fmt(A['null_lo95'])}, {fmt(A['null_hi95'])}]
- observed {fmt(A['observed'])}; fraction of nulls ≤ observed:
  {fmt(A['prop_null_le_obs'])}

→ The observed Δβ falls **inside** the size-matched null interval: regional
gamma-pool asymmetry alone can produce effects of this sign and magnitude.

## B. Frequency-matched null (B=10,000)

Herbivore genera caliper-matched to predator occupancy frequencies:

- null mean {fmt(B['null_mean'])}, 95% null interval
  [{fmt(B['null_lo95'])}, {fmt(B['null_hi95'])}]
- observed {fmt(B['observed'])}; fraction of nulls ≤ observed:
  {fmt(B['prop_null_le_obs'])}

→ Even after matching occupancy/dominance structure, the observed Δβ is
**more negative than every matched realisation** — the reverse signal is not
reproduced by dominance structure alone.

## C. Allosaurus dependence

| Scenario | Δβ | Notes |
|---|---|---|
| C1 full | {fmt(c['C1_full']['delta_beta'])} | — |
| C2 exclude Allosaurus | {fmt(c['C2_no_allosaurus']['delta_beta'])} | signal collapses to ~0 |
| C3 downsample to median | {fmt(c['C3_downsample_median']['delta_beta'])} | [{fmt(c['C3_downsample_median']['lo95'])}, {fmt(c['C3_downsample_median']['hi95'])}] |
| C3 downsample to p75 | {fmt(c['C3_downsample_p75']['delta_beta'])} | [{fmt(c['C3_downsample_p75']['lo95'])}, {fmt(c['C3_downsample_p75']['hi95'])}] |
| C3 downsample to p90 | {fmt(c['C3_downsample_p90']['delta_beta'])} | [{fmt(c['C3_downsample_p90']['lo95'])}, {fmt(c['C3_downsample_p90']['hi95'])}] |
| C3 downsample 50% | {fmt(c['C3_downsample_half']['delta_beta'])} | [{fmt(c['C3_downsample_half']['lo95'])}, {fmt(c['C3_downsample_half']['hi95'])}] |
| C4 species split | {fmt(c['C4_allosaurus_species_split']['delta_beta'])} | n_taxa={int(c['C4_allosaurus_species_split']['n_taxa_used'])} |
| C5 Allosaurus only | — | {int(c['C5_allosaurus_only']['n_collections'])} collections ({fmt(c['C5_allosaurus_only']['share_of_predator_collections'])} of predator collections), lat range {fmt(c['C5_allosaurus_only']['lat_range'])}°, lng range {fmt(c['C5_allosaurus_only']['lng_range'])}° |

→ The reverse signal is **mostly Allosaurus-driven**: removing it leaves
Δβ ≈ 0, and downsampling it to typical predator counts flips the sign
slightly positive. Splitting Allosaurus to species retains a moderate
negative value.

## D. Systems-tract stratification

{D.to_markdown(index=False)}

→ Δβ < 0 within every sufficiently sampled systems tract (3–6), with
bootstrap CIs entirely negative — the signal is not confined to one
depositional window.

## E. Stratigraphic control (interval bins)

{E.to_markdown(index=False)}

→ Persists within the Kimmeridgian and Tithonian bins; Oxfordian and
undated bins are too sparse.

## F. Taxonomic-resolution symmetry

{F.to_markdown(index=False)}

→ Genus-level Δβ = {fmt(float(F[(F.level=='genus_level')&(F.guild=='DELTA')]['beta_simpson'].iloc[0]))};
species-level Δβ = {fmt(float(F[(F.level=='species_level')&(F.guild=='DELTA')]['beta_simpson'].iloc[0]))}
(still negative, attenuated — consistent with Allosaurus splitting raising
predator turnover).

## G. Metric and spatial-scale robustness

{G.to_markdown(index=False)}

→ Δβ < 0 for Simpson/Sorensen/Jaccard at collection scale and at 50/100/150 km
grid pooling; magnitude attenuates with aggregation (−0.55 → −0.28).

## Exploratory interpretation

**Classification: ALLOSAURUS-SPECIFIC** (with a residual artifact
contribution from gamma-pool asymmetry).

- The signal is real in the statistical sense (robust across tracts,
  intervals, metrics, scales, and frequency-matched nulls), but it is
  carried overwhelmingly by one ubiquitous predator genus rather than being
  a guild-wide predator property (C2: Δβ ≈ 0 without Allosaurus).
- Movement cannot be inferred from continuity alone. Candidate mechanisms
  for Allosaurus ubiquity include mobility, dietary generalism, taxonomic
  lumping, and preservational structure.

## Implication for Stage 1c

A defensible confirmatory question is the narrower one: **is predator
community spatial turnover lower than herbivore turnover in an independent
formation, at a preregistered metric/scale, with per-taxon occupancy or
gamma-pool matching controls?** See `VALIDATION_HYPOTHESES.md`.
"""
    out = ROOT / "results" / "stage1b_exploratory_reverse_signal.md"
    out.write_text(md)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
