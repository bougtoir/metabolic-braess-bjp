#!/usr/bin/env python3
"""Package the IEEE TIM submission files into a single ZIP archive.

Layout:
    manuscript/            main manuscript docx (template-formatted if present)
    tables/                editable tables docx
    figures/               editable figure deck plus individual TIFFs
    cover_letter/          cover letter docx
    supplementary_material/replication_code/   full reproducible code + data

Usage:
    python3 scripts/make_submission_zip.py [--out /path/TIM_submission.zip]
"""
from __future__ import annotations

import argparse
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CODE_DIRS = ["src", "scripts", "data", "results", "figures", "manuscripts",
             "cover_letter"]
CODE_FILES = ["README.md", "Makefile", "requirements.txt", ".gitignore"]
SKIP_DIR_PARTS = {"__pycache__", ".git", ".ipynb_checkpoints"}


def add_file(z: zipfile.ZipFile, path: str, arcname: str) -> None:
    if os.path.exists(path):
        z.write(path, arcname)


def add_tree(z: zipfile.ZipFile, root: str, arc_root: str) -> None:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            z.write(full, os.path.join(arc_root, rel))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "TIM_submission.zip"))
    args = ap.parse_args()

    man_dir = os.path.join(ROOT, "manuscripts")
    formatted = os.path.join(man_dir, "TIM_ZeroFree_Manuscript_EN_formatted.docx")
    plain = os.path.join(man_dir, "TIM_ZeroFree_Manuscript_EN.docx")

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        add_file(z, plain, "manuscript/TIM_ZeroFree_Manuscript_EN.docx")
        add_file(z, formatted,
                 "manuscript/TIM_ZeroFree_Manuscript_EN_formatted.docx")
        add_file(z, os.path.join(man_dir, "TIM_Tables_EN.docx"),
                 "tables/TIM_Tables_EN.docx")
        add_file(z, os.path.join(man_dir, "TIM_Figures_EN.pptx"),
                 "figures/TIM_Figures_EN.pptx")
        for i in range(1, 8):
            add_file(z, os.path.join(ROOT, "figures", "submission",
                                     f"Figure{i}.tif"),
                     f"figures/individual_tif/Figure{i}.tif")
        add_file(z, os.path.join(ROOT, "cover_letter",
                                 "TIM_Cover_Letter_EN.docx"),
                 "cover_letter/TIM_Cover_Letter_EN.docx")

        arc_root = "supplementary_material/replication_code"
        for name in CODE_FILES:
            add_file(z, os.path.join(ROOT, name),
                     os.path.join(arc_root, name))
        for d in CODE_DIRS:
            path = os.path.join(ROOT, d)
            if os.path.isdir(path):
                add_tree(z, path, os.path.join(arc_root, d))

    print("Submission archive written:", args.out)


if __name__ == "__main__":
    main()
