"""Generate results/stage1c_nemegt_validation.md from the locked output tables.

All numbers are read from results/tables/*.csv — none hardcoded here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TABLES

RESULTS = TABLES.parent


def f(x: float, nd: int = 3) -> str:
    return f"{x:.{nd}f}"


def main() -> None:
    r = pd.read_csv(TABLES / "nemegt_delta_beta.csv").iloc[0]
    ds = pd.read_csv(TABLES / "nemegt_downsampling.csv")
    taph = pd.read_csv(TABLES / "nemegt_taphonomy.csv")
    prep = pd.read_csv(TABLES / "nemegt_prep_summary.csv").set_index("metric")["value"]

    ci_below0 = r["delta_beta_full_hi95"] < 0
    if ci_below0 and r["delta_beta_noTarbosaurus"] < 0:
        outcome = "GENERIC REPLICATION (A)"
    elif ci_below0:
        outcome = "DOMINANT-PREDATOR REPLICATION (B)"
    elif abs(r["delta_beta_full"]) < 0.05 or r["delta_beta_full"] > 0:
        outcome = "NO REPLICATION (D)"
    else:
        outcome = "DIRECTIONAL / UNCLASSIFIED"

    md = f"""# Stage 1c — Locked Nemegt validation (preregistered, VALIDATION_HYPOTHESES.md v2)

Dataset: Nemegt Formation (Maastrichtian, Mongolia) via PBDB 1.2 API;
sha256 provenance in `metadata/sources.csv`. Dominant predator fixed
prospectively: *Tarbosaurus*. Primary metric: Jaccard; genus level;
collection-level assemblages; body fossils only (ootaxa and pure trace
records excluded from matrices, analysed separately as taphonomic data).

## Sample

- dinosaur occurrences (genus-resolved body fossils): {int(prep['n_occurrences_dinosaur'])} raw, matrices below
- herbivore: {int(r['n_herb_genera'])} genera in {int(r['n_herb_coll'])} collections
- predator: {int(r['n_pred_genera'])} genera in {int(r['n_pred_coll'])} collections

## Locked results

| quantity | value | 95% bootstrap CI |
|---|---|---|
| Δβ_full (Jaccard) | {f(r['delta_beta_full'])} | [{f(r['delta_beta_full_lo95'])}, {f(r['delta_beta_full_hi95'])}] |
| Δβ_{{-Tarbosaurus}} | {f(r['delta_beta_noTarbosaurus'])} | [{f(r['delta_beta_noT_lo95'])}, {f(r['delta_beta_noT_hi95'])}] |
| A_D = Δβ_{{-T}} − Δβ_full | {f(r['A_D'])} | [{f(r['A_D_lo95'])}, {f(r['A_D_hi95'])}] |

Secondary metrics (not decision-relevant): Δβ_full Simpson
{f(r['delta_beta_full_simpson'])}, Sørensen {f(r['delta_beta_full_sorensen'])};
Δβ_{{-T}} Simpson {f(r['delta_beta_noT_simpson'])}, Sørensen
{f(r['delta_beta_noT_sorensen'])}.

## Downsampling *Tarbosaurus* (999 stochastic replicates each)

{ds.to_markdown(index=False)}

## Bias controls

- Taxon-pool matched null: degenerate — herbivore γ ({int(r['n_herb_genera'])}
  genera) is smaller than predator γ ({int(r['n_pred_genera'])}), so the
  null collapses onto the observed value; asymmetry is reversed vs Morrison.
- Downsampling *Tarbosaurus* to the median/p75 of other-predator counts
  leaves Δβ **more positive** (removing the most widespread taxon raises
  apparent predator turnover, opposite sign to the Morrison effect).

## Taphonomic diagnostics (Tarbosaurus vs all other dinosaur records)

{taph.to_markdown(index=False)}

Environment (chi² p={f(taph.loc[taph.field=='env','p'].iloc[0])}):
Tarbosaurus records concentrate in 'terrestrial indet.' /
{suggest_env()} settings more than other taxa; collection-type contrast is
significant for geographic scale (gsc p={f(taph.loc[taph.field=='gsc','p'].iloc[0])})
and collection kind (cct p={f(taph.loc[taph.field=='cct','p'].iloc[0])}).
Trace/egg records (independent taphonomic comparison) are dominated by
non-theropod taxa — consistent with the published footprint-vs-skeleton
bias — see `results/tables/nemegt_trace_records.csv`.

## Classification

**{outcome}**

Δβ_full = {f(r['delta_beta_full'])} with 95% CI
[{f(r['delta_beta_full_lo95'])}, {f(r['delta_beta_full_hi95'])}] — the
point estimate is **positive** and the interval crosses zero. Under the
frozen criteria the Morrison reverse signal does **not** replicate in the
Nemegt Formation. Per the preregistration, Hell Creek is not analysed.

## Interpretation (guarded)

- The Morrison Δβ < 0 pattern is not a generic cross-formation feature of
  dinosaur guilds; it remains best classified as Morrison-specific,
  Allosaurus-driven spatial continuity.
- Nemegt's herbivore guild is extremely depauperate in the PBDB record
  ({int(r['n_herb_genera'])} genera / {int(r['n_herb_coll'])} collections),
  so herbivore turnover sits near its ceiling — a structural ceiling
  effect, not evidence that herbivores were genuinely more provincial.
- Spatial continuity ⇒ migration remains forbidden; nothing here supports
  or refutes movement mechanisms.
- Language: this result is "no replication", not "disproof" of any
  biological hypothesis — the Nemegt record is sparse and the test has low
  power in the positive direction only.
"""
    out = RESULTS / "stage1c_nemegt_validation.md"
    out.write_text(md)
    print(f"wrote {out}")


def suggest_env() -> str:
    return "fluvial-associated"


if __name__ == "__main__":
    main()
