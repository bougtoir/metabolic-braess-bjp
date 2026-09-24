"""Cenozoic step 7: regenerate STATUS-style report from committed tables —
no hard-coded numbers (mirrors dinosaur 99_stage1_report.py convention).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import TABLES


def main() -> None:
    s = pd.read_csv(TABLES / "beta_summary.csv", index_col=0).iloc[:, 0]
    sens = pd.read_csv(TABLES / "sampling_sensitivity.csv")
    agg = pd.read_csv(TABLES / "aggregation_sensitivity.csv")
    null = pd.read_csv(TABLES / "pool_null.csv")

    lines = [
        "# Cenozoic mammals — strict replication report",
        "",
        "## Primary contrast (Delta-beta, predator - herbivore)",
        f"- Simpson: {s['delta_beta_simpson_overall']:.3f} "
        f"[{s['delta_beta_simpson_boot_lo']:.3f}, {s['delta_beta_simpson_boot_hi']:.3f}], "
        f"P(delta>0)={s['delta_beta_simpson_boot_p_gt0']:.3f}",
        f"- Sorensen: {s['delta_beta_sorensen_overall']:.3f} "
        f"[{s['delta_beta_sorensen_boot_lo']:.3f}, {s['delta_beta_sorensen_boot_hi']:.3f}]",
        f"- n collections: herbivore {int(s['herbivore_simpson_n_collections'])}, "
        f"predator {int(s['predator_simpson_n_collections'])}",
        "",
        "## Distance decay (Mantel Spearman r)",
        f"- herbivore: r={s['herbivore_simpson_mantel_r']:.4f} (p={s['herbivore_simpson_mantel_p']:.4f})",
        f"- predator: r={s['predator_simpson_mantel_r']:.4f} (p={s['predator_simpson_mantel_p']:.4f})",
        "",
        "## Sampling-pool sensitivity (delta_beta under each correction)",
        sens.to_string(index=False),
        "",
        "## Temporal aggregation sensitivity",
        agg.to_string(index=False),
        "",
        "## Genus-pool null models",
        null.to_string(index=False),
        "",
        "## Comparison to dinosaur reference",
        "- dinosaur Morrison: Delta-beta_Simpson = -0.543 [-0.623, -0.452], "
        "P(>0)=0; Mantel r~0 both guilds (see docs/DINOSAUR_PROTOCOL_CANONICAL.md)",
        "- Robustness class assignment: see protocols/cenozoic_mammals/ "
        "and results/common_metrics/common_metrics_cenozoic.csv",
    ]
    out = TABLES.parent.parent / "results" / "cenozoic_report.md"
    out.write_text("\n".join(str(x) for x in lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
