"""Cenozoic step 1: raw-data audit (env distribution, orders, temporal span)."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import DIAG, load_raw


def main() -> None:
    df = load_raw()
    DIAG.mkdir(parents=True, exist_ok=True)

    lines = [
        f"raw occurrences: {len(df)}",
        f"collections: {df['cid'].nunique()}",
        f"genera (gnl): {df['gnl'].nunique()}",
        "",
        "== env value counts ==",
        df["env"].value_counts(dropna=False).to_string(),
        "",
        "== order value counts ==",
        df["odl"].value_counts(dropna=False).to_string(),
        "",
        f"age range: eag {df['eag'].min()}-{df['eag'].max()}, "
        f"lag {df['lag'].min()}-{df['lag'].max()}",
        "",
        "== early interval (oei) counts ==",
        df["oei"].value_counts(dropna=False).to_string(),
    ]
    (DIAG / "audit.txt").write_text("\n".join(str(x) for x in lines))
    print("\n".join(str(x) for x in lines[:6]))


if __name__ == "__main__":
    main()
