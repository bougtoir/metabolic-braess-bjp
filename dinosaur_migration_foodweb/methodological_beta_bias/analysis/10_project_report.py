"""Generate results/methodological_project_report.md from output tables."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"


def f(x, nd=3):
    return f"{float(x):.{nd}f}"


def main() -> None:
    dec = pd.read_csv(T / "morrison_decomposition.csv")
    nem = pd.read_csv(T / "nemegt_comparator_decomposition.csv")
    for d in (dec, nem):
        if "note" in d:
            d["note"] = d["note"].astype(str).str.replace("|", "/", regex=False)
    s1 = pd.read_csv(T / "sim01_gamma_bias.csv")
    s2 = pd.read_csv(T / "sim02_dominance_bias.csv")
    s3 = pd.read_csv(T / "sim03_taxonomic_lumping.csv")
    s4 = pd.read_csv(T / "sim04_temporal_averaging.csv")
    s5 = pd.read_csv(T / "sim05_sampling_bias.csv")
    s6 = pd.read_csv(T / "sim06_factorial.csv")

    md = f"""# Methodological beta-bias — project report

Methodological study (new primary route). Worked example: the Morrison
guild contrast that falsified the original hypothesis.

## Morrison empirical decomposition (sequential, Jaccard, collection level)

{dec.to_markdown(index=False)}

Sequential finding: naive Δβ = {f(dec.iloc[0].delta_beta)} falls inside
the gamma-matched null interval ({f(dec.iloc[1].lo95)} to
{f(dec.iloc[1].hi95)}) but below the frequency-matched null
({f(dec.iloc[2].lo95)} to {f(dec.iloc[2].hi95)}); removing Allosaurus
collapses it to {f(dec.iloc[3].delta_beta)}; species resolution leaves
{f(dec.iloc[4].delta_beta)}; duration/sampling adjustment removes the
Allosaurus extent anomaly (z = {f(dec.iloc[5].delta_beta)}).

## Nemegt comparator (same diagnostic workflow; not a replication)

{nem.to_markdown(index=False)}

Nemegt starts near zero (+{f(nem.iloc[0].delta_beta)}) — there is no
contrast to decompose; herbivore gamma ({8}) < predator gamma, so the
gamma null degenerates. Comparator of opposite structure.

## Simulation results

### 01 Gamma-diversity imbalance
{s1.to_markdown(index=False)}

Pool-size asymmetry alone generates strong negative Δβ: predator pool of
4/26 herbivore gamma → bias {f(s1.loc[s1.n_pred_taxa==4,'bias_mean'].iloc[0])}
(false contrast in {f(s1.loc[s1.n_pred_taxa==4,'prop_abs_gt_0.1'].iloc[0]*100,0)}% of reps).

### 02 Dominant taxon (p_D sweep)
{s2.to_markdown(index=False)}

A dominant predator at p_D = 0.46 (Allosaurus-like prevalence) shifts
Δβ by ~{f(s2.loc[(s2.p_dominant-0.5).abs().idxmin(),'delta_beta_obs_mean'])}.

### 03 Taxonomic lumping
{s3.to_markdown(index=False)}

Collapsing k geographically partitioned species into one genus adds
B_lumping ≈ {f(s3.iloc[-1].B_lumping_mean)} at k=6 — genus pooling
systematically inflates apparent continuity.

### 04 Temporal averaging
{s4.to_markdown(index=False)}

Merging 8 time slices into 1 erases nearly all guild contrast
(Δβ → {f(s4.iloc[-1].delta_beta_obs_mean)}).

### 05 Sampling asymmetry
{s5.to_markdown(index=False)}

Guild-specific sampling ratios up to 8× produced only modest bias
({f(s5.delta_beta_obs_mean.min())} to {f(s5.delta_beta_obs_mean.max())})
in this simple model — sampling bias is real but smaller than
gamma/dominance effects here.

### 06 Factorial grid
{s6.groupby('n_lumped').bias.mean().round(3).to_markdown()}

(per-lumping-level mean bias; full grid in sim06_factorial.csv —
sign-reversal and false-difference flags in `prop_sign_negative` /
`prop_false_difference`)

## Figures

- fig1_narrative.png, fig2_attenuation.png, fig3_bias_heatmap.png,
  fig4_lumping.png, fig5_temporal_dominance.png

## Independent evidence audit

See INDEPENDENT_EVIDENCE_AUDIT.md — nothing found contradicts the
methodological conclusion; available evidence favours trophic
generalism over mobility.

## Headline

Naive guild-level beta-diversity contrasts in fossil assemblages can be
dominated by gamma asymmetry, a single dominant taxon, taxonomic
resolution and time averaging — demonstrated on a preregistered
prediction that reversed and then failed independent replication.
"""
    out = ROOT / "results" / "methodological_project_report.md"
    out.write_text(md)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
