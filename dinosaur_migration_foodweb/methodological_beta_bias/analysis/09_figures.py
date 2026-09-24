"""Figures 1-5 for the methodological beta-bias project."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
F = ROOT / "figures"
F.mkdir(parents=True, exist_ok=True)


def main() -> None:
    dec = pd.read_csv(T / "morrison_decomposition.csv")

    # --- Figure 1: narrative emergence and disappearance ---
    fig, ax = plt.subplots(figsize=(7, 3.4))
    steps = ["H1\nprediction\n(Δβ>0)", "Morrison\nobserved", "exploratory\n(Allosaurus)",
             "Nemegt\nreplication", "decomposed\nresidual"]
    vals = [0.3, dec.loc[0, "delta_beta"], dec.loc[3, "delta_beta"],
            0.094, dec.loc[4, "delta_beta"]]
    cols = ["#999", "#c0392b", "#e67e22", "#2980b9", "#7f8c8d"]
    ax.bar(steps, vals, color=cols)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("Δβ (predator − herbivore, Jaccard)")
    ax.set_title("Fig.1 — A strong signal emerged and disappeared under correction")
    fig.tight_layout(); fig.savefig(F / "fig1_narrative.png", dpi=150); plt.close(fig)

    # --- Figure 2: sequential attenuation forest plot ---
    fig, ax = plt.subplots(figsize=(7, 3.6))
    sub = dec.iloc[:5]
    y = np.arange(len(sub))[::-1]
    xerr = np.clip(
        np.stack([sub["delta_beta"] - sub["lo95"],
                  sub["hi95"] - sub["delta_beta"]]), 0, None
    )
    ax.errorbar(sub["delta_beta"], y, xerr=xerr,
                fmt="o", color="#c0392b", capsize=3)
    # null intervals for steps 2-3 shown as shaded bands
    ax.axvspan(sub.loc[1, "lo95"], sub.loc[1, "hi95"], color="#3498db", alpha=0.15)
    ax.axvspan(sub.loc[2, "lo95"], sub.loc[2, "hi95"], color="#27ae60", alpha=0.15)
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(sub["label"], fontsize=8)
    ax.set_xlabel("Δβ"); ax.set_title("Fig.2 — Morrison sequential attenuation")
    fig.tight_layout(); fig.savefig(F / "fig2_attenuation.png", dpi=150); plt.close(fig)

    # --- Figure 3: factorial heatmap (bias) ---
    sim6 = pd.read_csv(T / "sim06_factorial.csv")
    ks = sorted(sim6["n_lumped"].unique())
    fig, axes = plt.subplots(1, len(ks), figsize=(11, 3.2), sharey=True)
    for ax, k in zip(axes, ks):
        sub = sim6[sim6["n_lumped"] == k]
        piv = sub.pivot(index="n_pred_taxa", columns="p_dominant", values="bias")
        im = ax.imshow(piv.values, cmap="RdBu_r", vmin=-0.5, vmax=0.5,
                       aspect="auto", origin="lower")
        ax.set_xticks(range(len(piv.columns))); ax.set_xticklabels(piv.columns)
        ax.set_yticks(range(len(piv.index))); ax.set_yticklabels(piv.index)
        ax.set_xlabel("p_dominant"); ax.set_title(f"k={k} lumped spp.")
    axes[0].set_ylabel("n predator taxa")
    fig.colorbar(im, ax=axes, label="Bias = Δβ_obs − 0")
    fig.suptitle("Fig.3 — False guild contrasts under structural bias")
    fig.tight_layout(); fig.savefig(F / "fig3_bias_heatmap.png", dpi=150); plt.close(fig)

    # --- Figure 4: lumping effect ---
    sim3 = pd.read_csv(T / "sim03_taxonomic_lumping.csv")
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.plot(sim3["n_lumped_species"], sim3["delta_beta_species"], "o-", label="species resolved")
    ax.plot(sim3["n_lumped_species"], sim3["delta_beta_genus"], "s-", label="genus pooled")
    ax.set_xlabel("sister species collapsed into one genus (k)")
    ax.set_ylabel("Δβ_obs"); ax.legend()
    ax.set_title("Fig.4 — Taxonomic lumping bias")
    fig.tight_layout(); fig.savefig(F / "fig4_lumping.png", dpi=150); plt.close(fig)

    # --- Figure 5: temporal averaging + dominance ---
    sim4 = pd.read_csv(T / "sim04_temporal_averaging.csv")
    sim2 = pd.read_csv(T / "sim02_dominance_bias.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    axes[0].errorbar(sim4["bin_width_slices"], sim4["delta_beta_obs_mean"],
                     yerr=[sim4["delta_beta_obs_mean"] - sim4["lo95"],
                           sim4["hi95"] - sim4["delta_beta_obs_mean"]],
                     fmt="o-", capsize=3)
    axes[0].set_xlabel("temporal bin width (slices merged)")
    axes[0].set_ylabel("Δβ_obs"); axes[0].axhline(0, color="k", lw=0.8)
    axes[0].set_title("Temporal averaging")
    axes[1].plot(sim2["p_dominant"], sim2["delta_beta_obs_mean"], "o-")
    axes[1].fill_between(sim2["p_dominant"], sim2["lo95"], sim2["hi95"], alpha=0.2)
    axes[1].set_xlabel("dominant-taxon prevalence p_D")
    axes[1].set_ylabel("Δβ_obs"); axes[1].axhline(0, color="k", lw=0.8)
    axes[1].axvline(0.46, color="grey", ls="--", lw=0.8)
    axes[1].annotate("Allosaurus ≈ 0.46", xy=(0.46, sim2["delta_beta_obs_mean"].min()),
                     fontsize=7, rotation=90, va="bottom")
    axes[1].set_title("Dominant-taxon effect")
    fig.suptitle("Fig.5 — Time averaging and dominance generate apparent guild contrasts")
    fig.tight_layout(); fig.savefig(F / "fig5_temporal_dominance.png", dpi=150)
    plt.close(fig)
    print("figures written")


if __name__ == "__main__":
    main()
