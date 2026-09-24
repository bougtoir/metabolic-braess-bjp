"""Build results/cross_system_comparison.csv from exported common metrics.

Rows = core metric; columns = systems. Includes native estimate,
standardized estimate, direction, robustness class, bias sensitivity.
Never meta-analyzes incompatible native metrics — standardized columns only.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CM = ROOT / "results" / "common_metrics"
SYSTEMS = ["dinosaur", "cenozoic", "quaternary", "ancient_marine",
           "modern_terrestrial", "modern_marine"]


def main() -> None:
    frames = []
    for s in SYSTEMS:
        p = CM / f"common_metrics_{s}.csv"
        if p.exists():
            df = pd.read_csv(p, dtype=str, keep_default_na=False)
            df["_sys"] = s
            frames.append(df)
        else:
            print(f"{s}: no export yet (NA columns in comparison)")
    if not frames:
        print("no exports; nothing to compare")
        return
    allm = pd.concat(frames, ignore_index=True)

    rows = []
    metrics = allm["metric"].unique()
    for m in metrics:
        row = {"metric": m}
        for s in SYSTEMS:
            sub = allm[(allm.metric == m) & (allm._sys == s)]
            if sub.empty:
                row[s] = "NA"
                continue
            r = sub.iloc[0]
            row[s] = (
                f"native={r['effect_estimate']} ({r['effect_scale']}); "
                f"std={r['standardized_effect']}; dir={r['effect_direction']}; "
                f"robust={r['robustness_class']}; bias_sens={r['sampling_pool_sensitivity']}"
            )
        rows.append(row)
    out = pd.DataFrame(rows)
    dest = ROOT / "results" / "cross_system_comparison.csv"
    out.to_csv(dest, index=False)
    print(f"wrote {dest.relative_to(ROOT)} ({len(out)} metrics x {len(SYSTEMS)} systems)")


if __name__ == "__main__":
    main()
