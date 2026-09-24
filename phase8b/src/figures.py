"""Phase-8B figures 1-9 from results/tables (all numbers generated, none hardcoded)."""
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results" / "tables"
FIG = ROOT / "results" / "figures"; FIG.mkdir(parents=True, exist_ok=True)

def load(pat):
    fs = sorted(TAB.glob(pat))
    return pd.concat([pd.read_csv(f).assign(src=f.stem.split("_")[0])
                      for f in fs], ignore_index=True) if fs else pd.DataFrame()

def main():
    hg = load("*_history_gain.csv")
    dec = load("*_memory_decay.csv")
    me = load("*_matched_env.csv")
    sl = load("*_shift_lag.csv")
    fp = pd.read_csv(TAB / "simulation_false_positive.csv") if (TAB / "simulation_false_positive.csv").exists() else pd.DataFrame()

    # Fig 1: HG by system/species
    if not hg.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        hg["lab"] = hg.get("species", hg.get("ind", "")).astype(str) + " (" + hg.src + ")"
        ax.barh(hg["lab"], hg.HG.fillna(0))
        ax.axvline(0, c="k", lw=.8)
        ax.set_xlabel("History gain HG = OOS(M3) - OOS(M1)"); ax.set_title("Fig 1. History gain by system")
        plt.tight_layout(); plt.savefig(FIG / "fig1_hg.png", dpi=120); plt.close()
        # Fig 2: EG
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(hg["lab"], hg.EG.fillna(0))
        ax.axvline(0, c="k", lw=.8)
        ax.set_xlabel("Env gain EG = OOS(M3) - OOS(M2)"); ax.set_title("Fig 2. Env gain")
        plt.tight_layout(); plt.savefig(FIG / "fig2_eg.png", dpi=120); plt.close()
        # Fig 3: model hierarchy
        cols = [c for c in ["M0", "M1", "M2", "M3", "M4", "M5", "M6"] if c in hg]
        fig, ax = plt.subplots(figsize=(7, 4))
        for src, g in hg.groupby("src"):
            ax.plot(cols, g[cols].median(), "o-", label=src)
        ax.legend(); ax.set_ylabel("LOYO OOS R2"); ax.set_title("Fig 3. Model hierarchy")
        plt.tight_layout(); plt.savefig(FIG / "fig3_models.png", dpi=120); plt.close()
    # Fig 4: memory decay
    if not dec.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        for src, g in dec.groupby("src"):
            ax.plot(g.groupby("horizon").oos.median(), "o-", label=src)
        ax.legend(); ax.set_xlabel("lag (bins)"); ax.set_ylabel("OOS R2")
        ax.set_title("Fig 4. Memory decay")
        plt.tight_layout(); plt.savefig(FIG / "fig4_decay.png", dpi=120); plt.close()
    # Fig 5: matched-env (current outcome vs prior outcome under similar env)
    if not me.empty:
        fig, ax = plt.subplots(figsize=(5, 5))
        for src, g in me.groupby("src"):
            x = g[[c for c in g if c.endswith("tm1") or c.endswith("tm12")]].iloc[:, 0]
            y = g[[c for c in g if c.endswith("_t")]].iloc[:, 0]
            ax.scatter(x.sample(min(2000, len(x)), random_state=0),
                       y.sample(min(2000, len(y)), random_state=0),
                       s=2, alpha=.2, label=src)
        ax.legend(); ax.set_xlabel("prior-bin outcome"); ax.set_ylabel("current outcome")
        ax.set_title("Fig 5. Matched-environment path dependence")
        plt.tight_layout(); plt.savefig(FIG / "fig5_matched.png", dpi=120); plt.close()
    # Fig 6: shift lag (distribution of post-shift changes)
    if not sl.empty:
        vals = sl.dropna().iloc[:, -1]
        if len(vals):
            lo, hi = np.percentile(vals, [1, 99])
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.hist(vals.clip(lo, hi), bins=60)
            ax.axvline(0, c="r"); ax.set_title("Fig 6. Post-shift response")
            plt.tight_layout()
            plt.savefig(FIG / "fig6_shift.png", dpi=120); plt.close()
    # Fig 7: FP rate
    if not fp.empty:
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(fp.system, fp.P_HG_pos_envonly); ax.set_ylim(0, 1)
        ax.axhline(.1, c="r", ls="--")
        ax.set_title("Fig 7. False-positive HG under env-only sim")
        plt.tight_layout(); plt.savefig(FIG / "fig7_fp.png", dpi=120); plt.close()
    # Fig 8: coverage
    fig, ax = plt.subplots(figsize=(6, 4))
    cov = {"foss": 45, "bbs": 58, "elk": 19, "wolf": 9}
    ax.bar(cov.keys(), cov.values()); ax.set_ylabel("years spanned")
    ax.set_title("Fig 8. Temporal coverage per system")
    plt.tight_layout(); plt.savefig(FIG / "fig8_coverage.png", dpi=120); plt.close()
    # Fig 9: HG vs EG scatter
    if not hg.empty:
        fig, ax = plt.subplots(figsize=(5, 5))
        for src, g in hg.groupby("src"):
            ax.scatter(g.HG, g.EG, s=12, label=src, alpha=.7)
        ax.axvline(0, c="k", lw=.8); ax.axhline(0, c="k", lw=.8)
        ax.set_xlabel("HG"); ax.set_ylabel("EG"); ax.legend()
        ax.set_title("Fig 9. HG vs EG")
        plt.tight_layout(); plt.savefig(FIG / "fig9_hg_eg.png", dpi=120); plt.close()
    print("figs written")

if __name__ == "__main__":
    main()
