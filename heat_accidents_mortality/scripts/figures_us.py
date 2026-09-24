#!/usr/bin/env python3
"""Generate US figures (English) from processed result CSVs. One figure per file."""
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
C_HOT = "0.2" if BW else "tab:red"
C_COOL = "0.85" if BW else "tab:blue"
C_OFF = "0.55" if BW else "tab:grey"
plt.rcParams.update({"figure.dpi": 130, "font.size": 11, "axes.grid": True,
                     "grid.alpha": 0.3, "savefig.bbox": "tight"})


def save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(FIG, f"{name}.{ext}"))
    plt.close(fig)


def fig_abs():
    d = pd.read_csv(os.path.join(PROC, "us_exposure_response_abs.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(d.tmean, d.lo, d.hi, alpha=0.2, color=C_MAIN)
    ax.plot(d.tmean, d.rr, color=C_MAIN)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xlabel("Daily mean temperature (\u00b0C)")
    ax.set_ylabel("Rate ratio of crash deaths (vs MMT)")
    ax.set_title("A. Absolute-temperature exposure-response\n(confounded by seasonal driving envelope)")
    save(fig, "fig1_absolute_exposure_response")


def fig_anom():
    d = pd.read_csv(os.path.join(PROC, "us_anomaly_response.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.fill_between(d.anom, d.lo, d.hi, alpha=0.2, color=C_FILL)
    ax.plot(d.anom, d.rr, color=C_FILL)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.axvline(0, ls=":", color="grey", lw=0.8)
    ax.set_xlabel("Temperature anomaly vs local seasonal norm (\u00b0C)")
    ax.set_ylabel("Cumulative rate ratio (lag 0-10)")
    ax.set_title("B. Anomaly exposure-response (primary model)")
    save(fig, "fig2_anomaly_exposure_response")


def fig_lag():
    d = pd.read_csv(os.path.join(PROC, "us_lag_response.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(d))
    ax.errorbar(x, d.rr, yerr=[d.rr - d.lo, d.hi - d.rr], fmt="o", capsize=4,
                color=C_SEC)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(d.window)
    ax.set_xlabel("Lag window (days)")
    ax.set_ylabel("Rate ratio for +9\u00b0C anomaly")
    ax.set_title("C. Lag structure: acute spike then displacement")
    save(fig, "fig3_lag_response")


def fig_year():
    d = pd.read_csv(os.path.join(PROC, "us_attributable_by_year.csv"))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(d.year, d.heat_an, color=C_MAIN, alpha=0.8, edgecolor="0.15")
    ax.set_xlabel("Year")
    ax.set_ylabel("Heat-attributable crash deaths")
    ax.set_title("D. Net crash deaths attributable to\nhotter-than-normal days, by year")
    save(fig, "fig4_attributable_by_year")


def fig_compare():
    att = pd.read_csv(os.path.join(PROC, "us_attributable.csv")).iloc[0]
    cdc = pd.read_csv(os.path.join(PROC, "cdc_heat_deaths.csv"))
    off = cdc[cdc.year.between(2016, 2020)].heat_deaths_X30.mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    vals = [off, att.net_heat_attributable_per_year]
    labs = ["Official direct-heat\ndeaths (ICD-10 X30)", "Est. heat-attributable\ncrash deaths (this study)"]
    colors = [C_OFF, C_MAIN]
    hatch = ["", "//"] if BW else ["", ""]
    ax.bar(labs, vals, color=colors, alpha=0.85, edgecolor="0.15", hatch=hatch)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.0f}/yr", ha="center", va="bottom")
    ax.set_ylabel("Deaths per year (US)")
    ax.set_title("E. Hidden heat burden in crashes vs\nofficially recognised heat deaths")
    save(fig, "fig5_hidden_vs_official")


def fig_roaduser():
    d = pd.read_csv(os.path.join(PROC, "us_subgroup_response.csv"))
    d = d[d.dimension == "user"].copy()
    labels = {"vehicle_occupant": "Vehicle occupant\n(enclosed/AC)",
              "motorcyclist": "Motorcyclist", "pedestrian": "Pedestrian",
              "cyclist": "Cyclist"}
    d["lab"] = d.group.map(labels)
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(6.2, 4))
    ax.errorbar(d["sameday_RR_+9C"], y,
                xerr=[d["sameday_RR_+9C"] - d.sameday_lo, d.sameday_hi - d["sameday_RR_+9C"]],
                fmt="o", capsize=4, color=C_MAIN)
    ax.axvline(1, ls="--", color="k", lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(d.lab)
    ax.set_xlabel("Same-day rate ratio for +9\u00b0C anomaly")
    ax.set_title("Heat effect by road-user exposure:\nopen-air users hit hardest")
    save(fig, "fig_us_roaduser")


def fig_timeofday():
    d = pd.read_csv(os.path.join(PROC, "us_timeofday_response.csv"))
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(6, 4))
    if BW:
        fill = [C_COOL if h != "12-17" else C_HOT for h in d.hour_band]
        edge = ["0.15"] * len(d)
        ax.errorbar(x, d["sameday_RR_+9C"],
                    yerr=[d["sameday_RR_+9C"] - d.sameday_lo, d.sameday_hi - d["sameday_RR_+9C"]],
                    fmt="none", ecolor="0.35", capsize=4, zorder=3)
        ax.scatter(x, d["sameday_RR_+9C"], facecolors=fill, edgecolors=edge,
                   s=70, zorder=4, linewidths=1.2)
    else:
        colors = ["tab:blue" if h != "12-17" else "tab:red" for h in d.hour_band]
        ax.errorbar(x, d["sameday_RR_+9C"],
                    yerr=[d["sameday_RR_+9C"] - d.sameday_lo, d.sameday_hi - d["sameday_RR_+9C"]],
                    fmt="o", capsize=4, color="k", zorder=3)
        ax.scatter(x, d["sameday_RR_+9C"], c=colors, s=60, zorder=4)
    ax.axhline(1, ls="--", color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(d.hour_band)
    ax.set_xlabel("Crash hour of day (local, h)")
    ax.set_ylabel("Same-day rate ratio for +9\u00b0C anomaly")
    ax.set_title("Time-of-day of the heat excess\n(peak in the hottest hours, 12-17)")
    save(fig, "fig_us_timeofday")


def fig_projection():
    d = pd.read_csv(os.path.join(PROC, "us_projection.csv"))
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(x, d.extra_deaths_per_year, color=C_MAIN, alpha=0.85, edgecolor="0.15",
           yerr=[d.extra_deaths_per_year - d.extra_lo, d.extra_hi - d.extra_deaths_per_year],
           capsize=5)
    for i, v in enumerate(d.extra_deaths_per_year):
        ax.text(i, v, f"+{v:.0f}/yr", ha="center", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels([f"+{int(v)}\u00b0C" for v in d.delta_degC])
    ax.set_xlabel("Uniform warming of daily temperature")
    ax.set_ylabel("Additional crash deaths per year (US)")
    ax.set_title("Projected additional hidden crash deaths\nunder warming (activity held constant)")
    save(fig, "fig_us_projection")


def main():
    fig_abs(); fig_anom(); fig_lag(); fig_year(); fig_compare()
    fig_roaduser(); fig_timeofday(); fig_projection()
    print("figures written to", FIG)


if __name__ == "__main__":
    main()
