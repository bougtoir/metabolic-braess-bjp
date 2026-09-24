"""Generate manuscript figures F1-F6 from phase9 post-fix result tables.

All values read from phase9/results/tables/*.csv - nothing hardcoded.
Output: geb/results/figures/F{1..6}.png
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "phase9" / "results" / "tables"
FIGDIR = Path(__file__).resolve().parents[1] / "results" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9})


def med(s):
    return float(pd.to_numeric(s, errors="coerce").median())


def f1_conceptual():
    fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.0))
    labels = ["A  Apparent memory\n(naive reading)",
              "B  Persistent spatial\nheterogeneity",
              "C  True state dependence\n(after spatial control)"]
    for ax, lab in zip(axes, labels):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.set_title(lab, fontsize=9)
    # A: X_t-1 -> X_t
    ax = axes[0]
    ax.text(0.2, 0.75, "$X_{t-1}$", fontsize=13, ha="center")
    ax.text(0.8, 0.75, "$X_t$", fontsize=13, ha="center")
    ax.add_patch(FancyArrowPatch((0.32, 0.75), (0.68, 0.75), arrowstyle="-|>",
                                 mutation_scale=16, lw=2, color="C0"))
    ax.text(0.5, 0.82, "predictive", fontsize=8, ha="center", color="C0")
    # B: static suitability drives both
    ax = axes[1]
    ax.text(0.5, 0.25, "persistent route\nsuitability", fontsize=10,
            ha="center", color="C3")
    ax.text(0.18, 0.78, "$X_{t-1}$", fontsize=13, ha="center")
    ax.text(0.82, 0.78, "$X_t$", fontsize=13, ha="center")
    for x in (0.18, 0.82):
        ax.add_patch(FancyArrowPatch((0.5, 0.35), (x, 0.68), arrowstyle="-|>",
                                     mutation_scale=14, lw=1.8, color="C3"))
    ax.add_patch(FancyArrowPatch((0.30, 0.78), (0.70, 0.78), arrowstyle="-|>",
                                 mutation_scale=14, lw=1.4, color="0.6",
                                 linestyle="--"))
    ax.text(0.5, 0.85, "apparent lag\ncorrelation", fontsize=7, ha="center",
            color="0.4")
    # C: residual after removing static
    ax = axes[2]
    ax.text(0.2, 0.75, "$X_{t-1}$", fontsize=13, ha="center")
    ax.text(0.8, 0.75, "$X_t$", fontsize=13, ha="center")
    ax.add_patch(FancyArrowPatch((0.32, 0.75), (0.68, 0.75), arrowstyle="-|>",
                                 mutation_scale=14, lw=2, color="C2"))
    ax.text(0.5, 0.82, "residual (small)", fontsize=8, ha="center",
            color="C2")
    ax.text(0.5, 0.25, "static component\nremoved (demeaned)",
            fontsize=9, ha="center", color="0.5")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F1_conceptual.png", dpi=300)
    plt.close(fig)


def f2_2x2(diag):
    cols = ["HG_A", "HG_B", "HG_C", "HG_D"]
    labs = ["A\nLOYO,\nno demean", "B\nLOYO,\ndemean",
            "C\nforward,\nno demean", "D\nforward,\ndemean"]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    data = [diag[c].dropna() for c in cols]
    for i, c in enumerate(cols):
        ax.plot([i - 0.06, i + 0.06], [0, 0], lw=0)
        ax.scatter(np.full(len(diag), i) + np.linspace(-0.12, 0.12, len(diag)),
                   diag[c], s=4, alpha=0.25, color="C0", zorder=1)
        # paired lines to next condition
        if i < 3:
            for _, r in diag.iterrows():
                ax.plot([i + 0.12, i + 1 - 0.12], [r[c], r[cols[i + 1]]],
                        color="0.7", lw=0.3, alpha=0.4, zorder=0)
    bp = ax.boxplot(data, positions=range(4), widths=0.35, showfliers=False,
                    patch_artist=True,
                    medianprops=dict(color="black", lw=1.5))
    for b in bp["boxes"]:
        b.set_facecolor("none"); b.set_edgecolor("black")
    ax.axhline(0, color="C3", ls="--", lw=1)
    ax.set_xticks(range(4)); ax.set_xticklabels(labs)
    ax.set_ylabel("History Gain (OOS $R^2$ difference)")
    ax.set_title("Static route persistence explains most apparent history dependence")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F2_2x2.png", dpi=300)
    plt.close(fig)


def f3_species_hg(summ):
    d = summ[["species", "HG_D", "HG_lo", "HG_hi"]].dropna().sort_values("HG_D")
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.fill_between(x, d.HG_lo, d.HG_hi, color="C0", alpha=0.25, lw=0)
    ax.plot(x, d.HG_D, color="C0", lw=1.2)
    ax.axhline(0, color="C3", ls="--", lw=1)
    ax.set_xlabel("Species (ranked by prospective History Gain)")
    ax.set_ylabel("HG$_D$ (forward + route-demeaned)")
    ax.set_title(f"Prospective lag-1 signal across {len(d)} species")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F3_species_hgd.png", dpi=300)
    plt.close(fig)


def f4_occ_vs_abund(hys):
    d = hys.dropna(subset=["eff_abundance"]).copy()
    d = d.sort_values("eff_abundance")
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.8))
    ax = axes[0]
    occ = hys.dropna(subset=["effect_of_prior_state"])
    xo = np.arange(len(occ))
    ax.fill_between(xo, occ.sort_values("effect_of_prior_state").ci_lo,
                    occ.sort_values("effect_of_prior_state").ci_hi,
                    color="C1", alpha=0.25, lw=0)
    ax.plot(xo, occ.sort_values("effect_of_prior_state").effect_of_prior_state,
            color="C1", lw=1.2)
    ax.axhline(0, color="C3", ls="--", lw=1)
    ax.set_xlabel(f"Species (n={len(occ)} definable)")
    ax.set_ylabel("Occupancy prior-state effect")
    ax.set_title("A  Occupancy: no hysteresis")
    ax = axes[1]
    x = np.arange(len(d))
    ax.fill_between(x, d.ci_ab_lo, d.ci_ab_hi, color="C2", alpha=0.3, lw=0)
    ax.plot(x, d.eff_abundance, color="C2", lw=1.2)
    ax.axhline(0, color="C3", ls="--", lw=1)
    ax.set_xlabel(f"Species (n={len(d)} definable)")
    ax.set_ylabel("Abundance prior-state effect (log-count)")
    ax.set_title("B  Abundance: strong state dependence")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F4_occ_vs_abund.png", dpi=300)
    plt.close(fig)


def f5_robustness(summ, lagenv, trn, win):
    specs, meds, los, his = [], [], [], []
    def add(name, s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        specs.append(name); meds.append(s.median())
        los.append(s.quantile(0.25)); his.append(s.quantile(0.75))
    add("primary\n(fwd+demean)", summ.HG_D)
    add("after lagged env\n(M6-M5)", lagenv.HG_lagenv)
    add("after lag-2 env\n(M6b-M5b)", lagenv.HG_lagenv2)
    for mh, g in trn.dropna(subset=["min_hist"]).groupby("min_hist"):
        add(f"min history\n{int(mh)}y", g.HG)
    worder = {"expand": "expanding", "10y": "rolling 10y", "20y": "rolling 20y"}
    for w, g in win.groupby("window"):
        add(f"{worder.get(w, w)}\nwindow", g.HG)
    x = np.arange(len(specs))
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.errorbar(x, meds, yerr=[np.array(meds) - np.array(los),
                             np.array(his) - np.array(meds)],
                fmt="o", color="C0", capsize=3, ms=5)
    ax.axhline(0, color="C3", ls="--", lw=1)
    ax.set_xticks(x); ax.set_xticklabels(specs)
    ax.set_ylabel("Median species HG (IQR)")
    ax.set_title("Prospective signal is small and stable across specifications")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F5_robustness.png", dpi=300)
    plt.close(fig)


def f6_interpretation(diag, hys):
    comp = [("Naive apparent\nhistory gain\n(LOYO, no demean)",
             med(diag.HG_A)),
            ("After static\nroute control\n(forward, demean)",
             med(diag.HG_D)),
            ("Abundance\nstate dependence\n(matched env)",
             med(hys.eff_abundance))]
    fig, ax = plt.subplots(figsize=(6.0, 3.8))
    colors = ["C0", "C0", "C2"]
    xs = range(3)
    ax.bar(xs, [c[1] for c in comp], color=colors, alpha=0.75)
    ax.axhline(0, color="0.3", lw=1)
    for i, (lab, v) in enumerate(comp):
        ax.text(i, v + 0.008 * np.sign(v if v else 1), f"{v:+.3f}",
                ha="center", fontsize=9)
    ax.set_xticks(list(xs)); ax.set_xticklabels([c[0] for c in comp],
                                              fontsize=8)
    ax.set_ylabel("Effect size (median)")
    ax.set_title("Apparent distribution memory is spatial persistence;\n"
                 "abundance retains genuine state dependence")
    fig.tight_layout()
    fig.savefig(FIGDIR / "F6_interpretation.png", dpi=300)
    plt.close(fig)


def main():
    diag = pd.read_csv(T / "cv_demean_2x2_diagnostic.csv")
    summ = pd.read_csv(T / "final_116_species_summary.csv")
    hys = pd.read_csv(T / "matched_environment_hysteresis.csv")
    lag = pd.read_csv(T / "history_after_lagged_env.csv")
    trn = pd.read_csv(T / "forward_training_size_sensitivity.csv")
    win = pd.read_csv(T / "window_sensitivity.csv")
    f1_conceptual()
    f2_2x2(diag)
    f3_species_hg(summ)
    f4_occ_vs_abund(hys)
    f5_robustness(summ, lag, trn, win)
    f6_interpretation(diag, hys)
    print("figures written to", FIGDIR)


if __name__ == "__main__":
    main()
