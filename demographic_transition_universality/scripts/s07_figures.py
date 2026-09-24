"""Figures for the EHS commentary. Produces one composite four-panel figure (the single display
item permitted for a Commentary) plus the individual panels, in PNG and SVG, with English labels.
All inputs are recomputed from the panel and the results/*.json|csv produced by s02-s06.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import FIGS_DIR, RESULTS_DIR, TAU_E0, ensure_dirs, load_panel

plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})
CAL_SPLIT = 1950


def _load():
    panel = load_panel()
    onset = (pd.read_csv(os.path.join(RESULTS_DIR, "country_onset.csv"))
             .set_index("country")["t_fert"].dropna())
    cp = json.load(open(os.path.join(RESULTS_DIR, "changepoint_uncertainty.json")))
    ev = json.load(open(os.path.join(RESULTS_DIR, "event_alignment.json")))
    sub = pd.read_csv(os.path.join(RESULTS_DIR, "subnational_points.csv"))
    return panel, onset, cp, ev, sub


def _sd_by_offset(panel, onset, window=25):
    cal = panel[(panel.year >= CAL_SPLIT - window) & (panel.year <= CAL_SPLIT + window)].copy()
    cal["off"] = cal.year - CAL_SPLIT
    sd_cal = cal.groupby("off")["lambda"].std()
    ev = panel.copy()
    ev["t"] = ev.country.map(onset)
    ev = ev.dropna(subset=["t"])
    ev["off"] = ev.year - ev.t
    ev = ev[(ev.off >= -window) & (ev.off <= window)]
    sd_ev = ev.groupby("off")["lambda"].std()
    return sd_cal, sd_ev


def panel_A(ax, onset, cp):
    ax.hist(onset.values, bins=np.arange(1820, 2021, 10), color="#6b7fb0", edgecolor="white")
    b = cp["global_change_year_bootstrap"]
    ax.axvspan(b["ci95_lo"], b["ci95_hi"], color="#d9534f", alpha=0.25,
               label=f"Pooled change-point\n95% CI ({int(b['ci95_lo'])}-{int(b['ci95_hi'])})")
    ax.axvline(cp["global_change_year_point_estimate"], color="#d9534f", lw=1.5)
    ax.axvline(1950, color="k", ls=":", lw=1, label="Calendar split (1950)")
    ax.set_xlabel("Country fertility-transition onset year")
    ax.set_ylabel("Number of countries")
    ax.set_title("A  Onsets span ~185 years, not one date")
    ax.legend(fontsize=6.5, loc="upper left", frameon=False)


def panel_B(ax, panel, onset, ev):
    sd_cal, sd_ev = _sd_by_offset(panel, onset)
    ax.plot(sd_cal.index, sd_cal.values, color="k", marker="o", ms=2.5, lw=1,
            label="Calendar time (aligned at 1950)")
    ax.plot(sd_ev.index, sd_ev.values, color="#2a8", marker="s", ms=2.5, lw=1,
            label="Event time (aligned at onset)")
    vr = ev["collapse"]["variance_reduction_ratio"]
    ax.set_xlabel("Years from alignment point")
    ax.set_ylabel(r"Between-country SD of $\lambda$")
    ax.set_title(f"B  Event alignment collapses the spread ({vr:.1f}\u00d7)")
    ax.legend(fontsize=6.5, frameon=False)


def panel_C(ax, ev):
    cal = ev["conserved_cv_calendar"]
    evt = ev["conserved_cv_event"]
    labels = ["Phase I\n" + r"$\lambda\,e_0$", "Phase II\n" + r"$\lambda\,e^{e_0/17}$"]
    x = np.arange(2)
    w = 0.36
    ax.bar(x - w/2, [cal["cv_lambda_e0_phaseI"], cal["cv_lambda_exp_phaseII"]], w,
           color="k", alpha=0.7, label="Calendar split")
    ax.bar(x + w/2, [evt["cv_lambda_e0_phaseI"], evt["cv_lambda_exp_phaseII"]], w,
           color="#2a8", label="Event alignment")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("CV of conserved quantity")
    ax.set_title("C  Only Phase I tightens under alignment")
    ax.legend(fontsize=6.5, frameon=False)


def panel_D(ax, panel, sub):
    # global Phase II isocline lambda = C / exp(e0/17), fit on national high-e0 data
    hi = panel[panel.e0 > 60]
    x = 1.0 / np.exp(hi.e0.values / TAU_E0)
    C = float(np.dot(x, hi["lambda"].values) / np.dot(x, x))
    e0grid = np.linspace(72, 86, 50)
    ax.plot(e0grid, C / np.exp(e0grid / TAU_E0), color="k", lw=1.3,
            label=r"'Universal' Phase II isocline $\lambda=C/e^{e_0/17}$")
    cross = sub[sub.source.isin(["Eurostat NUTS2", "CDC/NCHS + US Census PEP"])]
    colors = {"Spain": "#d9534f", "Italy": "#f0ad4e", "Germany": "#5bc0de",
              "France": "#5cb85c", "United States": "#6b4fa0"}
    for c, g in cross.groupby("country"):
        ax.scatter(g.e0, g["lambda"], s=10, color=colors.get(c, "grey"), alpha=0.75, label=c)
    ax.set_xlim(72, 86)
    ax.set_xlabel(r"Life expectancy $e_0$ (years)")
    ax.set_ylabel(r"Crude birth rate $\lambda$")
    ax.set_title("D  Regions of one country scatter off the curve")
    ax.legend(fontsize=6, frameon=False, ncol=2)


def graphical_abstract(panel, onset, ev, sub):
    """A self-contained one-message graphical abstract: reading each country on its own clock
    sharpens the (first) regularity, yet within countries a single lambda-e0 curve does not hold."""
    fig = plt.figure(figsize=(10.5, 5.0))
    fig.suptitle("Two pathways, many clocks", fontsize=16, fontweight="bold", y=0.99)
    fig.text(0.5, 0.925,
             "Aligning countries on their own transition onset\u2014not the calendar\u2014sharpens "
             "the regularity, but no single curve holds within countries",
             ha="center", fontsize=9.5, style="italic")
    gs = fig.add_gridspec(1, 2, left=0.07, right=0.98, top=0.83, bottom=0.12, wspace=0.28)
    axL = fig.add_subplot(gs[0, 0])
    panel_B(axL, panel, onset, ev)
    vr = ev["collapse"]["variance_reduction_ratio"]
    axL.set_title(f"Own-clock alignment collapses the spread ({vr:.1f}\u00d7)", fontsize=10)
    axR = fig.add_subplot(gs[0, 1])
    panel_D(axR, panel, sub)
    axR.set_title("Yet regions of one country scatter off the curve", fontsize=10)
    fig.savefig(os.path.join(FIGS_DIR, "graphical_abstract.png"), dpi=200)
    fig.savefig(os.path.join(FIGS_DIR, "graphical_abstract.svg"))
    plt.close(fig)


def main():
    ensure_dirs()
    panel, onset, cp, ev, sub = _load()

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2))
    panel_A(axes[0, 0], onset, cp)
    panel_B(axes[0, 1], panel, onset, ev)
    panel_C(axes[1, 0], ev)
    panel_D(axes[1, 1], panel, sub)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGS_DIR, "fig_main.png"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGS_DIR, "fig_main.svg"), bbox_inches="tight")
    plt.close(fig)

    graphical_abstract(panel, onset, ev, sub)

    # individual panels (standalone figures for the manuscript / pptx): clean titles w/o A-D
    clean = {"A_onset": "Transition onsets span ~185 years",
             "B_collapse": "Event alignment collapses the between-country spread",
             "C_cv": "Only the first pathway tightens under alignment",
             "D_subnational": "Regions of one country scatter off the curve"}
    for name, fn in [("A_onset", panel_A), ("B_collapse", panel_B),
                     ("C_cv", panel_C), ("D_subnational", panel_D)]:
        f, a = plt.subplots(figsize=(4.8, 3.8))
        if name == "A_onset":
            fn(a, onset, cp)
        elif name == "B_collapse":
            fn(a, panel, onset, ev)
        elif name == "C_cv":
            fn(a, ev)
        else:
            fn(a, panel, sub)
        a.set_title(clean[name])
        f.tight_layout()
        f.savefig(os.path.join(FIGS_DIR, f"panel_{name}.png"), bbox_inches="tight")
        plt.close(f)
    print("figures written to", FIGS_DIR)


if __name__ == "__main__":
    main()
