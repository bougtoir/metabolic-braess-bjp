"""Phase 8: figures + manuscript_values.csv from scan outputs.

All numbers come from results/scans/*.csv — nothing hardcoded.
Outputs: figures/fig*.png, manuscript/manuscript_values.csv
"""
import sys, os, json
sys.path.insert(0, 'src')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SC = "results/scans"
FIG = "figures"
os.makedirs(FIG, exist_ok=True)
os.makedirs("manuscript", exist_ok=True)
values = []  # (key, value, source_file)


def rec(key, val, src):
    values.append(dict(key=key, value=val, source=src))


plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 200})

# ---- load stage3 grids
gH = pd.read_csv(f"{SC}/full_human2_aerobic_pfba_fva_informed_stage3_grid.csv")
gR = pd.read_csv(f"{SC}/full_recon3d_aerobic_pfba_fva_informed_stage3_grid.csv")
fine = pd.read_csv(f"{SC}/fine_human2_aerobic_pfba_fva_informed.csv")

# ---- Fig 2: efficiency NOPM response curves (both models)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=False)
for ax, rid, lab, col in [(axes[0], "MAR04373", "GAPDH (MAR04373)", "tab:red"),
                          (axes[0], "MAR04368", "PGK (MAR04368)", "tab:blue")]:
    sub = gH[gH.reaction_id == rid].sort_values("modulation_fraction")
    ax.plot(sub.modulation_fraction, sub.atp_per_glc, "o-", label=lab, color=col, ms=3)
    fsub = fine[fine.reaction_id == rid].sort_values("modulation_fraction")
    if len(fsub):
        ax.plot(fsub.modulation_fraction, fsub.atp_per_glc, "-", color=col, lw=0.7, alpha=0.6)
ax = axes[1]
for rid, lab, col in [("ENO", "ENO", "tab:green"), ("PGM", "PGM", "tab:orange"), ("GAPD", "GAPD", "tab:red")]:
    sub = gR[gR.reaction_id == rid].sort_values("modulation_fraction")
    ax.plot(sub.modulation_fraction, sub.atp_per_glc, "s-", label=lab, color=col, ms=3)
axes[0].set_xlabel("restriction fraction u"); axes[1].set_xlabel("restriction fraction u")
axes[0].set_ylabel("ATP yield per glucose (J)")
axes[0].set_title("A  Human-GEM v2.0.1"); axes[1].set_title("B  Recon3D v301")
for ax in axes:
    ax.axvspan(0, 1, color="none")
    ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(f"{FIG}/fig2_efficiency_nopm.png"); plt.close(fig)

# ---- Fig 3: parsimony NOPM (total_flux interior minima)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9))
hitsH = ["MAR04391", "MAR04896", "MAR06412", "MAR06921", "MAR08746", "MAR20069", "MAR06409", "MAR06916"]
for rid in hitsH:
    sub = gH[gH.reaction_id == rid].sort_values("modulation_fraction")
    if len(sub):
        axes[0].plot(sub.modulation_fraction, sub.total_flux / sub.total_flux.max() * -1, "o-", ms=2.5, lw=0.9, label=rid)
hitsR = ["O2t", "CYOR_u10mi", "TPI", "ENO", "PGM"]
for rid in hitsR:
    sub = gR[gR.reaction_id == rid].sort_values("modulation_fraction")
    if len(sub):
        axes[1].plot(sub.modulation_fraction, sub.total_flux / abs(sub.total_flux.iloc[0]) * -1, "s-", ms=2.5, lw=0.9, label=rid)
axes[0].set_ylabel("total |flux| (normalized, sign-flipped)")
for ax in axes:
    ax.set_xlabel("restriction fraction u"); ax.legend(frameon=False, fontsize=6)
axes[0].set_title("A  Human-GEM"); axes[1].set_title("B  Recon3D")
fig.tight_layout(); fig.savefig(f"{FIG}/fig3_parsimony_nopm.png"); plt.close(fig)

# ---- Fig 4: Pareto view — ATP rate vs ATP/glucose, GAPDH both models
fig, ax = plt.subplots(figsize=(3.4, 3.0))
for d, rid, lab, col, m in [(gH, "MAR04373", "Human-GEM GAPDH", "tab:red", "o"),
                            (gR, "GAPD", "Recon3D GAPD", "tab:blue", "s")]:
    sub = d[d.reaction_id == rid].sort_values("modulation_fraction")
    ax.plot(sub.atp_demand, sub.atp_per_glc, m + "-", label=lab, color=col, ms=3)
    for _, r in sub.iterrows():
        if r.modulation_fraction in (0, 0.5, 1.0):
            ax.annotate(f"u={r.modulation_fraction}", (r.atp_demand, r.atp_per_glc), fontsize=6)
ax.set_xlabel("ATP production rate (J_atp)"); ax.set_ylabel("ATP per glucose")
ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(f"{FIG}/fig4_pareto_gapdh.png"); plt.close(fig)

# ---- manuscript_values.csv — headline numbers from files
def J(d, rid, metric, u):
    r = d[(d.reaction_id == rid) & (np.isclose(d.modulation_fraction, u))]
    return float(r[metric].iloc[0]) if len(r) else np.nan

srcH = "full_human2_aerobic_pfba_fva_informed_stage3_grid.csv"
srcR = "full_recon3d_aerobic_pfba_fva_informed_stage3_grid.csv"
for key, d, rid, u in [
    ("human2_GAPDH_J0", gH, "MAR04373", 0), ("human2_GAPDH_Jstar", gH, "MAR04373", 0.9), ("human2_GAPDH_J1", gH, "MAR04373", 1.0),
    ("human2_PGK_J0", gH, "MAR04368", 0), ("human2_PGK_Jstar", gH, "MAR04368", 0.75), ("human2_PGK_J1", gH, "MAR04368", 1.0),
]:
    rec(key, J(d, rid, "atp_per_glc", u), srcH)
for key, d, rid, u in [
    ("recon3d_ENO_J0", gR, "ENO", 0), ("recon3d_ENO_Jstar", gR, "ENO", 0.75), ("recon3d_ENO_J1", gR, "ENO", 1.0),
    ("recon3d_PGM_J0", gR, "PGM", 0), ("recon3d_PGM_Jstar", gR, "PGM", 0.75), ("recon3d_PGM_J1", gR, "PGM", 1.0),
]:
    rec(key, J(d, rid, "atp_per_glc", u), srcR)

for tag, path in [("human2_full", "class_human2_full.csv"), ("recon3d_full", "class_recon3d_full.csv"),
                  ("human2_fine_pilot", "class_fine_pilot.csv")]:
    c = pd.read_csv(f"{SC}/{path}")
    rec(f"nopm_combos_{tag}", int((c.type == "II").sum()), path)
    rec(f"classified_combos_{tag}", int(len(c)), path)

pd.DataFrame(values).to_csv("manuscript/manuscript_values.csv", index=False)
print("figures:", sorted(os.listdir(FIG)))
print("values:", len(values))
