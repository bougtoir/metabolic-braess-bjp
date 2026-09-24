#!/usr/bin/env python3
"""Spot-check numeric consistency between the generated manuscript and data files."""

import json
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parent.parent
DOCX = ROOT / "docs" / "heredity_submission" / "manuscript_heredity.docx"
DATA_DIR = ROOT / "data"
OUT = ROOT / "docs" / "heredity_submission" / "numeric_consistency_check.txt"


def main():
    doc = Document(DOCX)
    text = "\n".join(p.text for p in doc.paragraphs)
    text = text.replace(",", "")  # remove thousand separators for number matching

    with (DATA_DIR / "correction_stats.json").open(encoding="utf-8") as f:
        stats = json.load(f)
    with (DATA_DIR / "analysis_provenance.json").open(encoding="utf-8") as f:
        prov = json.load(f)

    expected = {
        "individuals": str(prov["individuals"]),
        "populations": str(prov["included_populations"]),
        "pairs": str(prov["population_pairs"]),
        "window_kb": str(int(prov["bin_size"] / 1000)),
        "neanderthal_raw_r": f"{stats['nean']['raw_r']:.3f}",
        "neanderthal_partial_r": f"{stats['nean']['partial_r']:.3f}",
        "neanderthal_beta": f"{stats['nean']['distance_qap_beta']:.5f}",
        "neanderthal_p": f"{stats['nean']['distance_qap_p']:.4f}",
        "denisovan_raw_r": f"{stats['deni']['raw_r']:.3f}",
        "denisovan_partial_r": f"{stats['deni']['partial_r']:.3f}",
        "denisovan_beta": f"{stats['deni']['distance_qap_beta']:.5f}",
        "denisovan_p": f"{stats['deni']['distance_qap_p']:.4f}",
        "permutations": str(stats["permutations"]),
        "sensitivity_permutations": str(stats["sensitivity_permutations"]),
    }

    failures = []
    for label, value in expected.items():
        if value.replace("-", "") not in text.replace("-", ""):
            failures.append(f"Missing {label}: {value}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if failures:
        OUT.write_text("FAIL\n" + "\n".join(failures), encoding="utf-8")
        print("Numeric consistency check FAILED")
        for f in failures:
            print(" ", f)
        raise SystemExit(1)
    else:
        OUT.write_text(
            "PASS: All checked numeric values from correction_stats.json and "
            "analysis_provenance.json are present in manuscript_heredity.docx.\n",
            encoding="utf-8",
        )
        print("Numeric consistency check PASSED")


if __name__ == "__main__":
    main()
