#!/usr/bin/env python3
"""Generate Japan figures (English) from processed result CSVs. One figure per file."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROC = os.path.join(ROOT, "data", "processed")
BW = os.environ.get("FIGURES_BW") == "1"
FIG = os.path.join(ROOT, "output", "figures_bw" if BW else "figures")
os.makedirs(FIG, exist_ok=True)
C_MAIN = "0.25" if BW else "tab:red"
C_FILL = "0.55" if BW else "tab:orange"
C_SEC = "0.25" if BW else "tab:blue"
C_US = "0.35" if BW else "tab:red"
C_JP = "0.7" if BW else "tab:blue"
plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": 0.3, "savefig.bbox": "tight"})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"))
    plt.close(fig)


def fig_abs():
    d = pd.read_csv(os.path.join(PROC, "jp_exposure_response_abs.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(d.tmean, d.lo, d.hi, alpha=0.2, color=C_MAIN)
    ax.plot(d.tmean, d.rr, color=C_MAIN)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xlabel("Daily mean temperature (\u00b0C)")
    ax.set_ylabel("Rate ratio of crash deaths (vs MMT)")
    ax.set_title("Japan A. Absolute-temperature exposure-response")
    save(fig, "jp_fig1_absolute_exposure_response")


def fig_anom():
    d = pd.read_csv(os.path.join(PROC, "jp_anomaly_response.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(d.anom, d.lo, d.hi, alpha=0.2, color=C_FILL)
    ax.plot(d.anom, d.rr, color=C_FILL)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.axvline(0, ls=":", color="grey", lw=0.8)
    ax.set_xlabel("Temperature anomaly vs local seasonal norm (\u00b0C)")
    ax.set_ylabel("Cumulative rate ratio (lag 0-10)")
    ax.set_title("Japan B. Anomaly exposure-response (primary model)")
    save(fig, "jp_fig2_anomaly_exposure_response")


def fig_lag():
    d = pd.read_csv(os.path.join(PROC, "jp_lag_response.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(d))
    ax.errorbar(x, d.rr, yerr=[d.rr - d.lo, d.hi - d.rr], fmt="o", capsize=4, color=C_SEC)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(d.window)
    ax.set_xlabel("Lag window (days)")
    ax.set_ylabel("Rate ratio for +9\u00b0C anomaly")
    ax.set_title("Japan C. Lag structure (wide CIs: fewer deaths)")
    save(fig, "jp_fig3_lag_response")


def fig_compare():
    us = pd.read_csv(os.path.join(PROC, "us_lag_response.csv")).iloc[0]
    jp = pd.read_csv(os.path.join(PROC, "jp_lag_response.csv")).iloc[0]
    fig, ax = plt.subplots(figsize=(6, 4))
    labs = ["United States", "Japan"]
    rr = [us.rr, jp.rr]; lo = [us.lo, jp.lo]; hi = [us.hi, jp.hi]
    x = np.arange(2)
    if BW:
        markers = ["s", "o"]
        mcolors = [C_US, C_JP]
        for i, (lab, m, c, r, l, h) in enumerate(zip(labs, markers, mcolors, rr, lo, hi)):
            ax.errorbar([i], [r], yerr=[[r - l], [h - r]], fmt=m, capsize=5,
                        color=c, markersize=8, markeredgecolor="0.15")
    else:
        ax.errorbar(x, rr, yerr=[np.array(rr) - lo, np.array(hi) - rr], fmt="s",
                    capsize=5, color="tab:red")
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labs)
    ax.set_ylabel("Same-day rate ratio for +9\u00b0C anomaly")
    ax.set_title("D. Acute heat effect on crash deaths:\nUS vs Japan")
    save(fig, "cross_fig_us_vs_japan_sameday")


def main():
    fig_abs(); fig_anom(); fig_lag(); fig_compare()
    print("Japan figures written to", FIG)


if __name__ == "__main__":
    main()
