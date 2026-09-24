"""Compose GEB figure set (fig_geb1..4) from frozen results tables.
Fig1 conceptual schematic; Fig2 gamma+dominance; Fig3 2-D+decay;
Fig4 lumping+temporal. Fig5=sim06 heatmap, Fig6=attenuation (already
produced by 09_figures.py)."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
F = ROOT / "figures"

# ---- Fig 1: conceptual schematic ----
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.axis("off")
ax.text(0.06, 0.75, "True guild turnover\nΔβ_ecological", ha="center",
        fontsize=11, bbox=dict(boxstyle="round", fc="#dbeafe", ec="#1e40af"))
steps = ["regional pool\nsize", "dominance", "taxonomic\naggregation",
         "temporal\naggregation", "sampling\nasymmetry"]
xs = np.linspace(0.24, 0.76, len(steps))
for x, s in zip(xs, steps):
    ax.text(x, 0.75, s, ha="center", fontsize=9,
            bbox=dict(boxstyle="round", fc="#fef3c7", ec="#b45309"))
    ax.annotate("", xy=(x, 0.66), xytext=(x, 0.71),
                arrowprops=dict(arrowstyle="->", color="#b45309"))
ax.annotate("", xy=(0.20, 0.75), xytext=(0.13, 0.75),
            arrowprops=dict(arrowstyle="->"))
ax.add_patch(plt.Rectangle((0.17, 0.44), 0.66, 0.20, fc="#f3f4f6",
                           ec="#6b7280", ls="--"))
ax.text(0.5, 0.54, "assemblage structure (non-independent, interacting)",
        ha="center", fontsize=9, color="#374151")
ax.text(0.94, 0.54, "Δβ_observed", ha="center", fontsize=11,
        bbox=dict(boxstyle="round", fc="#fee2e2", ec="#b91c1c"))
ax.annotate("", xy=(0.86, 0.54), xytext=(0.83, 0.54),
            arrowprops=dict(arrowstyle="->", color="#b91c1c"))
ax.text(0.5, 0.30, "false differentiation:  Δβ_true = 0 → Δβ_obs ≠ 0\n"
                   "lost differentiation:  Δβ_true ≠ 0 → Δβ_obs → 0\n"
                   "Δβ_observed ≠ Δβ_ecological  whenever guilds differ "
                   "in structure", ha="center", fontsize=10)
ax.annotate("", xy=(0.5, 0.44), xytext=(0.5, 0.40),
            arrowprops=dict(arrowstyle="-"))
fig.tight_layout()
fig.savefig(F / "fig_geb1_conceptual.png", dpi=160)
plt.close(fig)

# ---- Fig 2: gamma + dominance ----
g = pd.read_csv(T / "sim01_gamma_bias.csv")
d = pd.read_csv(T / "sim02_dominance_bias.csv")
fig, ax = plt.subplots(1, 2, figsize=(9, 4))
ax[0].errorbar(g.n_pred_taxa, g.delta_beta_obs_mean,
               yerr=[g.delta_beta_obs_mean - g.lo95,
                     g.hi95 - g.delta_beta_obs_mean],
               marker="o", capsize=3)
ax[0].axhline(0, color="k", lw=0.8, ls=":")
ax[0].axvspan(3, 5, alpha=0.15, color="green")
ax[0].annotate("pool 4 (representative)", xy=(4, -0.17), fontsize=8,
               xytext=(8, -0.28), arrowprops=dict(arrowstyle="->"))
ax[0].annotate("pool 2 (extreme)", xy=(2, -0.41), fontsize=8,
               xytext=(6, -0.40), arrowprops=dict(arrowstyle="->"))
ax[0].set_xlabel("small-guild regional pool size (comparison = 26)")
ax[0].set_ylabel("Δβ_observed")
ax[0].set_title("(a) Gamma-diversity imbalance (Δβ_true = 0)")
ax[1].errorbar(d.p_dominant, d.delta_beta_obs_mean,
               yerr=[d.delta_beta_obs_mean - d.lo95,
                     d.hi95 - d.delta_beta_obs_mean],
               marker="s", capsize=3, color="#b45309")
ax[1].axhline(0, color="k", lw=0.8, ls=":")
ax[1].axvline(0.456, color="#7c3aed", ls="--", lw=1)
ax[1].text(0.48, ax[1].get_ylim()[0] + 0.01,
           "Allosaurus-like\noccupancy", fontsize=7, color="#7c3aed")
ax[1].set_xlabel("dominant-taxon prevalence p_D")
ax[1].set_ylabel("Δβ_observed")
ax[1].set_title("(b) Dominant-taxon effect")
fig.tight_layout()
fig.savefig(F / "fig_geb2_gamma_dominance.png", dpi=160)
plt.close(fig)

# ---- Fig 3: 2-D robustness + distance decay ----
g13 = pd.read_csv(T / "sim13_2d_gamma.csv")
dc = pd.read_csv(T / "sim13_2d_decay_curves.csv")
fig, ax = plt.subplots(1, 2, figsize=(9, 4))
ax[0].errorbar(g13.n_pred_taxa, g13.delta_beta_mean,
               yerr=[g13.delta_beta_mean - g13.lo95,
                     g13.hi95 - g13.delta_beta_mean],
               marker="o", capsize=3, color="#0369a1")
ax[0].axhline(0, color="k", lw=0.8, ls=":")
ax[0].set_xlabel("small-guild pool size (2-D lattice)")
ax[0].set_ylabel("Δβ_observed")
ax[0].set_title("(a) 2-D replication of gamma bias")
dcc = dc[dc.dist_bin_center <= 30]
ax[1].plot(dcc.dist_bin_center, dcc.dissim_smallpool, "o-",
           label="small pool (4)", color="#0369a1")
ax[1].plot(dcc.dist_bin_center, dcc.dissim_comparison, "s-",
           label="comparison (26)", color="#b45309")
for col, c, s in [("dissim_smallpool", "#0369a1", 0.028),
                  ("dissim_comparison", "#b45309", 0.006)]:
    ok = dcc[col].notna()
    b0 = dcc[col][ok].mean() - s * dcc.dist_bin_center[ok].mean()
    ax[1].plot(dcc.dist_bin_center[ok], b0 + s * dcc.dist_bin_center[ok],
               "--", color=c, lw=1)
ax[1].text(1, ax[1].get_ylim()[1] - 0.05,
           "slopes ≈ 0.028 vs 0.006", fontsize=8)
ax[1].set_xlim(0, 30)
ax[1].set_xlabel("pairwise distance (lattice units)")
ax[1].set_ylabel("mean Jaccard dissimilarity")
ax[1].set_title("(b) Distance-decay distortion (pool 4)")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(F / "fig_geb3_2d_decay.png", dpi=160)
plt.close(fig)

# ---- Fig 4: lumping + temporal ----
l = pd.read_csv(T / "sim03_taxonomic_lumping.csv")
t = pd.read_csv(T / "sim04_temporal_averaging.csv")
t13 = pd.read_csv(T / "sim13_2d_temporal.csv")
fig, ax = plt.subplots(1, 2, figsize=(9, 4))
ax[0].plot(l.n_lumped_species, l.B_lumping_mean, "o-", color="#15803d")
ax[0].axhline(0, color="k", lw=0.8, ls=":")
ax[0].set_xlabel("species pooled per genus (k)")
ax[0].set_ylabel("B_lumping = β_species − β_genus")
ax[0].set_title("(a) Taxonomic aggregation")
ax[1].plot(t.temporal_bins, t.delta_beta_obs_mean, "o-",
           label="1-D", color="#0369a1")
ax[1].plot(t13.temporal_bins, t13.delta_beta_mean, "s--",
           label="2-D", color="#b45309")
ax[1].axhline(0, color="k", lw=0.8, ls=":")
ax[1].set_xlabel("temporal bins (1 = fully pooled)")
ax[1].set_ylabel("Δβ_observed")
ax[1].set_title("(b) Temporal aggregation")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(F / "fig_geb4_lumping_temporal.png", dpi=160)
plt.close(fig)
# ---- Fig 6: Morrison sequential attenuation + Nemegt comparator ----
dec = pd.read_csv(T / "morrison_decomposition.csv")
nem = pd.read_csv(T / "nemegt_comparator_decomposition.csv")
fig, ax = plt.subplots(figsize=(7.5, 4))
sub = dec.iloc[:5]
y = np.arange(len(sub))[::-1]
xerr = np.clip(np.stack([sub["delta_beta"] - sub["lo95"],
                         sub["hi95"] - sub["delta_beta"]]), 0, None)
ax.errorbar(sub["delta_beta"], y, xerr=xerr, fmt="o",
            color="#b91c1c", capsize=3, label="Morrison")
ax.axvspan(sub.loc[1, "lo95"], sub.loc[1, "hi95"], color="#3498db",
           alpha=0.15, label="gamma-matched null")
ax.axvspan(sub.loc[2, "lo95"], sub.loc[2, "hi95"], color="#27ae60",
           alpha=0.15, label="frequency-matched null")
nrow = nem.iloc[0] if "delta_beta" in nem.columns else None
if nrow is not None:
    nlo = nrow.get("lo95", np.nan); nhi = nrow.get("hi95", np.nan)
    if pd.notna(nlo) and pd.notna(nhi):
        ax.errorbar([nrow["delta_beta"]], [len(y) + 0.5],
                    xerr=[[nrow["delta_beta"] - nlo],
                          [nhi - nrow["delta_beta"]]],
                    fmt="s", color="#0369a1", capsize=3,
                    label="Nemegt comparator")
    else:
        mv = pd.read_csv(ROOT / "results" / "manuscript_values.csv")
        r = mv[mv.value_id.str.contains("nem_db_full", case=False,
                                        na=False)].iloc[0]
        ax.errorbar([r["value"]], [len(y) + 0.5],
                    xerr=[[r["value"] - r["CI_lower"]],
                          [r["CI_upper"] - r["value"]]],
                    fmt="s", color="#0369a1", capsize=3,
                    label="Nemegt comparator")
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(list(y) + [len(y) + 0.5])
ax.set_yticklabels(list(sub["label"]) + ["Nemegt\n(comparator)"],
                   fontsize=8)
ax.set_xlabel("Δβ (predator − herbivore, Jaccard)")
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout()
fig.savefig(F / "fig_geb6_empirical.png", dpi=160)
plt.close(fig)
print("wrote fig_geb1..4 + fig_geb6")
