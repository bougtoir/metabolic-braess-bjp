import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax.axis("off")
boxes = [
    (0.02, "Modulation\nu ∈ [0,1]\ncapacity restriction\nof feasible span", "#fde2e2"),
    (0.28, "A  Feasibility\nF(u) ⊆ F(0)\nset membership only", "#e2ecfd"),
    (0.52, "B  State selection\nv(u) = pFBA (L1-MOMA)\nindependent of J", "#e2f7e2"),
    (0.76, "C  Evaluation\nJ(v(u)): ATP rate,\nyield, |flux|, lactate", "#fdf6e2"),
]
for x, txt, c in boxes:
    ax.add_patch(mp.FancyBboxPatch((x, 0.25), 0.20, 0.5, boxstyle="round,pad=0.01",
                 fc=c, ec="#555", transform=ax.transAxes))
    ax.text(x + 0.10, 0.5, txt, ha="center", va="center", fontsize=8)
for x0, x1 in [(0.22, 0.28), (0.48, 0.52), (0.72, 0.76)]:
    ax.annotate("", xy=(x1, 0.5), xytext=(x0, 0.5), xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", color="#333"))
ax.text(0.5, 0.05, "Type II / NOPM:  J(u*) > J(0)  and  J(u*) > J(1)  for interior u*",
        ha="center", fontsize=9, style="italic")
fig.tight_layout(); fig.savefig("figures/fig1_pipeline.png", dpi=200)
