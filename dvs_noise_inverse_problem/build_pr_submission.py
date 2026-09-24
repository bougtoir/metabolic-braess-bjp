#!/usr/bin/env python3
"""Regenerate the Pattern Recognition submission package.

    python build_pr_submission.py            # figures + documents from results/*.json
    python build_pr_submission.py --full     # also rerun the EBSSA and DND21 analyses (hours)

--full downloads the labelled EBSSA split through tonic and the public DND21
AEDAT files (gdown) and rewrites results/sp_*.json, results/sparsity_cost.json,
results/partial_auc.json, results/self_calibration.json, results/zero_knowledge.json,
results/hybrid_screening.json, results/dnd21_*.json and results/comparator_feasibility.json.
results/pr_effect_sizes.json is derived from those files and is rebuilt on every run.
"""

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PR = HERE / 'pattern_recognition_submission'
PROVENANCE = HERE / 'results' / 'build_provenance.json'  # which analysis scripts ran in this build

ANALYSES = [
    (HERE, ['sp_evaluation.py']),
    (HERE, ['sparsity_cost.py']),
    (HERE, ['operating_points.py']),
    (HERE, ['zero_knowledge.py']),
    (HERE, ['hybrid_screening.py']),
    (HERE, ['qualitative_example.py']),
    (HERE, ['dnd21_evaluation.py']),
    (HERE, ['comparator_feasibility.py']),
    (HERE, ['aednet_transfer.py', '--dataset', 'ebssa']),
    (HERE, ['aednet_transfer.py', '--dataset', 'dnd21']),
    (HERE, ['aednet_transfer.py', '--summarise']),
]
DOCUMENTS = [
    (HERE, ['pr_effect_sizes.py']),  # derived statistics from results/*.json (deterministic, seed fixed)
    (PR, ['make_pr_figures.py']),
    (PR, ['create_pr_supporting.py']),  # builds the manuscript, then the supporting files
    (PR, ['check_pr_manuscript.py']),  # figure/table citation order and placement, abstract length
]

PACKAGE = ['manuscript_pattern_recognition.docx', 'supplementary_material.docx', 'highlights.docx',
           'title_page.docx', 'cover_letter.docx',
           'figure_legends.docx', 'tables_editable.docx', 'figures_tables_editable.pptx',
           'data_and_code_statement.md', 'REPRODUCIBILITY.md', 'comparator_feasibility.md',
           'package_manifest.json', 'graphical_abstract.png', 'graphical_abstract.tiff']


def run(cwd, args):
    print(f'>>> {" ".join(args)}', flush=True)
    subprocess.run([sys.executable, *args], cwd=cwd, check=True)


def make_zip():
    out = PR / 'pattern_recognition_submission.zip'
    files = [PR / f for f in PACKAGE] + sorted(PR.glob('fig*.png')) + sorted(PR.glob('fig*.tiff'))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.exists():
                z.write(f, f.name)
    print('zip written to', out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    analyses = ANALYSES if args.full else []
    for cwd, cmd in analyses:
        run(cwd, cmd)
    PROVENANCE.write_text(json.dumps({'rerun_scripts': [cmd[0] for _, cmd in analyses],
                                      'derived_scripts': ['pr_effect_sizes.py']}, indent=1) + '\n')
    for cwd, cmd in DOCUMENTS:
        run(cwd, cmd)
    make_zip()


if __name__ == '__main__':
    main()
