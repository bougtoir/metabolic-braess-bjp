#!/usr/bin/env python3
"""Build the KOTHA manuscript for Clinical Trials: Journal of the Society for Clinical Trials.

This script reuses the Contemporary Clinical Trials Communications (CCTC) manuscript
(05_paper_cctc.md / KOTHA_Framework_CCTC.docx) and restructures it for *Clinical Trials*:
- <= 6 main-text tables/figures
- Sage Vancouver superscript citations without brackets
- Background/Aims abstract heading
- First-three-authors + et al. reference list
- Separate supplementary tables and high-resolution figure files
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile

import sanitize_office_outputs as _san

BASE = os.path.dirname(os.path.abspath(__file__))

CCTC_MD = os.path.join(BASE, '05_paper_cctc.md')
CCTC_DOCX = os.path.join(BASE, 'KOTHA_Framework_CCTC.docx')
CCTC_SUPP_DOCX = os.path.join(BASE, 'KOTHA_Framework_CCTC_supplementary_tables.docx')

OUT_MD = os.path.join(BASE, '05_paper_clinical_trials.md')
OUT_DOCX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials.docx')
OUT_SUB_DOCX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials_submission.docx')
OUT_FIGURES_PPTX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials_figures.pptx')
OUT_SUPP_FIGURES_PPTX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials_supplementary_figures.pptx')
OUT_TABLES_DOCX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials_tables.docx')
OUT_SUPP_DOCX = os.path.join(BASE, 'KOTHA_Framework_ClinicalTrials_supplementary_tables.docx')
SUBMISSION_FIGURES_DIR = os.path.join(BASE, 'ClinicalTrials_figures')

HIGHLIGHTS_BLOCK = r"""## Highlights

* KOTHA separates structural information loss from residual confounding.
* Counterfactual power simulation quantifies enrollment-driven event dilution.
* Power-prior Bayesian synthesis transparently discounts observational evidence.
* GRADE-compatible output labels evidence as sufficient or insufficient.

"""

FIGURE_MAP = {
    'validation/figures/fig1_framework_overview.png': 'Figure_1_framework_overview.png',
    'validation/figures/fig2_risk_profile_shift.png': 'Figure_2_risk_profile_shift.png',
    'validation/figures/fig3_power_curves.png': 'Figure_3_power_curves.png',
    'validation/figures/fig4_forest_combined.png': 'Figure_4_forest_combined.png',
    'validation/figures/fig5_tsa_magnesium.png': 'Figure_S2_tsa_magnesium.png',
    'validation/figures/fig7_sensitivity_analysis.png': 'Figure_S3_sensitivity_analysis.png',
    'validation/figures/fig8_module_h_comparison.png': 'Figure_S4_module_h_comparison.png',
    'validation/figures/figS1a_trace_mcmc_magnesium.png': 'Figure_S1a_trace_mcmc_magnesium.png',
    'validation/figures/figS1b_trace_mcmc_statins.png': 'Figure_S1b_trace_mcmc_statins.png',
}


def _remove_supplementary_blocks(md):
    """Remove CCTC blocks that become supplementary material in Clinical Trials.

    Using regex patterns means the build script does not have to hard-code
    CCTC markdown content (especially data-dependent tables).
    """
    patterns = [
        (r'\n## Highlights\n', r'(?=\n## Abstract)'),
        (r'\n\*\*Table 1:.*', r'(?=\n## 2\. Methods)'),
        (r'\n\*\*Fig\. 5\*\*.*', r'(?=\n### Bayesian integration)'),
        (r'\n\*\*Table 3:.*', r'(?=\n### Module H assessment)'),
        (r'\n\*\*Fig\. 7\*\*.*', r'(?=\n## 4\. Discussion)'),
    ]
    for start, end in patterns:
        md = re.sub(start + r'.*?' + end, '', md, count=1, flags=re.S)
    return md


def _run(script, *args):
    """Run a Python script in the repository root."""
    subprocess.run([sys.executable, script, *args], cwd=BASE, check=True)


def _ensure_cctc_outputs():
    """Generate CCTC outputs if they are not already present."""
    if not os.path.exists(CCTC_MD) or not os.path.exists(CCTC_DOCX):
        print('CCTC outputs missing; running build_paper_cct.py ...')
        _run('build_paper_cct.py')
    if not os.path.exists(CCTC_SUPP_DOCX):
        print('CCTC supplementary tables missing; running build_supplementary_tables_docx.py ...')
        _run('build_supplementary_tables_docx.py')


def _word_count(md):
    """Count main-text words excluding abstract, declarations, tables, figures, references."""
    wc_match = re.search(r'## 1\. Introduction(.*?)## Declarations', md, re.S)
    wc_text = wc_match.group(1) if wc_match else md
    wc_text = re.sub(r'!\[.*?\]\(.*?\)', '', wc_text)
    wc_text = re.sub(r'\*\*Fig\.\s*\d+\*\*.*', '', wc_text)
    wc_text = re.sub(r'\*\*Table[^*]+\*\*', '', wc_text)
    wc_text = re.sub(r'(?:\|.*\n)+', '', wc_text)
    wc_text = re.sub(r'[#*_`$\\]', ' ', wc_text)
    wc_text = re.sub(r'\[.*?\]', '', wc_text)
    return len(wc_text.split())


def _abbreviate_reference_line(line):
    """Reduce a Vancouver reference to first three authors + et al."""
    m = re.match(r'^(\d+\.\s+)(.+?)\.\s+(.*)$', line)
    if not m:
        return line
    prefix, authors, rest = m.groups()
    parts = [p.strip() for p in authors.split(',') if p.strip()]
    parts = [p for p in parts if p.lower() != 'et al.']
    if len(parts) > 3:
        parts = parts[:3] + ['et al']
    return f'{prefix}{", ".join(parts)}. {rest}'


def _abbreviate_references(md):
    """Abbreviate author lists in the References section to Sage Vancouver style."""
    ref_start = md.find('## References')
    if ref_start == -1:
        return md
    before = md[:ref_start]
    ref_section = md[ref_start:]
    lines = ref_section.splitlines()
    new_lines = [lines[0]]
    for line in lines[1:]:
        if re.match(r'^\d+\.', line):
            new_lines.append(_abbreviate_reference_line(line))
        else:
            new_lines.append(line)
    return before + '\n'.join(new_lines)


def _convert_abbreviations(md):
    """Convert the Abbreviations markdown table to a bullet list.

    Clinical Trials limits original research to 6 tables/figures total.
    An unnumbered abbreviations table would still count as a table in Word,
    so we render it as a definition list instead.
    """
    match = re.search(r'(## Abbreviations\n\n)(.*?)(\n\n## 1\. Introduction)', md, re.S)
    if not match:
        return md
    header, table_block, tail = match.group(1), match.group(2), match.group(3)
    bullets = []
    for line in table_block.strip().splitlines():
        line = line.strip()
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if not cells or len(cells) < 2:
            continue
        abbr, definition = cells[0], cells[1]
        # Skip header and separator rows
        if abbr.lower() in ('abbreviation', '') or definition.lower() == 'definition' or set(abbr) <= {'-'}:
            continue
        if abbr:
            bullets.append(f'* **{abbr}**: {definition}')
    replacement = header + '\n'.join(bullets) + tail if bullets else header + table_block + tail
    return md[:match.start()] + replacement + md[match.end():]


def _move_fig1_after_first_citation(md):
    """Move the Figure 1 block to immediately after its first in-text citation.

    The first citation is in the Methods/Overview paragraph; the figure block
    is therefore placed right after that paragraph and before Module K.
    """
    # Extract the Fig. 1 block (caption line + image line)
    block_re = re.compile(r'\n\n(\*\*Fig\. 1\*\*[^\n]*\n\n!\[Fig\. 1\]\([^\)]+\))\n\n', re.S)
    m = block_re.search(md)
    if not m:
        return md
    block = m.group(1)
    md_without = md[:m.start()] + '\n\n' + md[m.end():]

    # Find the first paragraph that cites Fig. 1
    para_re = re.compile(r'^(The KOTHA Framework comprises.*?\(Fig\. 1\).*?applied in sequence\.)$', re.M)
    pm = para_re.search(md_without)
    if not pm:
        return md_without
    insert_at = pm.end()
    return md_without[:insert_at] + '\n\n' + block + md_without[insert_at:]


def _restructure(md):
    """Restructure CCTC markdown for Clinical Trials."""
    md = _remove_supplementary_blocks(md)

    # Update in-text references to supplementary items
    md = md.replace('(Table 1)', '(Supplementary Table S1)')
    md = md.replace('(Fig. 5)', '(Supplementary Fig. S2)')
    md = md.replace('(Table 3)', '(Supplementary Table S4)')
    md = md.replace('(Fig. 6A)', '(Supplementary Fig. S3A)')
    md = md.replace('(Fig. 6B)', '(Supplementary Fig. S3B)')
    md = md.replace('(Table 2)', '(Table 1)')
    md = md.replace('(Table 4)', '(Table 2)')
    md = md.replace('Table 4 and Fig. 7', 'Table 4 and Supplementary Fig. S4')

    # CCTC supplementary table numbering differs from Clinical Trials numbering:
    # in Clinical Trials the existing-approaches table becomes Supplementary Table S1,
    # so study-level data tables move from S1/S2 to S2/S3.
    md = md.replace(
        'Study-level data are provided in Supplementary Table S1 (magnesium in AMI) and Supplementary Table S2 (statins in HF).',
        'Study-level data are provided in Supplementary Table S2 (magnesium in AMI) and Supplementary Table S3 (statins in HF).'
    )

    # Renumber remaining main-text tables sequentially (Table 2 -> 1, Table 4 -> 2)
    md = re.sub(r'\bTable 2\b', 'Table 1', md)
    md = re.sub(r'\bTable 4\b', 'Table 2', md)

    md = _convert_abbreviations(md)
    md = _move_fig1_after_first_citation(md)
    md = _abbreviate_references(md)

    # Update main-text word count
    wc = _word_count(md)
    md = re.sub(r'^word_count:\s*\d+', f'word_count: {wc}', md, flags=re.MULTILINE)
    return md, wc


def _copy_submission_figures():
    """Copy high-resolution figure files into a submission-ready folder."""
    if os.path.exists(SUBMISSION_FIGURES_DIR):
        shutil.rmtree(SUBMISSION_FIGURES_DIR)
    os.makedirs(SUBMISSION_FIGURES_DIR)
    for src, dst in FIGURE_MAP.items():
        src_path = os.path.join(BASE, src)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(SUBMISSION_FIGURES_DIR, dst))
        else:
            print(f'  WARNING: figure not found: {src_path}')


def _build_submission_package():
    """Zip all Clinical Trials deliverables."""
    zip_path = os.path.join(BASE, 'submission_package_ClinicalTrials.zip')
    files_to_zip = [
        OUT_MD,
        OUT_DOCX,
        OUT_SUB_DOCX,
        OUT_TABLES_DOCX,
        OUT_FIGURES_PPTX,
        OUT_SUPP_FIGURES_PPTX,
        OUT_SUPP_DOCX,
        os.path.join(BASE, 'cover_letter_ClinicalTrials.docx'),
    ]
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in files_to_zip:
            if os.path.exists(f):
                zf.write(f, os.path.basename(f))
        for root, _, files in os.walk(SUBMISSION_FIGURES_DIR):
            for file in files:
                full = os.path.join(root, file)
                arc = os.path.relpath(full, BASE)
                zf.write(full, arc)
    print(f'Created {zip_path}')


def main():
    parser = argparse.ArgumentParser(description='Build Clinical Trials manuscript package')
    parser.add_argument('--no-cctc', action='store_true', help='Skip CCTC build even if outputs are missing')
    args = parser.parse_args()

    if not args.no_cctc:
        _ensure_cctc_outputs()

    print(f'Reading {CCTC_MD} ...')
    with open(CCTC_MD, 'r', encoding='utf-8') as f:
        md = f.read()

    md, wc = _restructure(md)
    print(f'Restructured main-text word count: {wc}')

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(md)
    print(f'Wrote {OUT_MD}')

    # Generate main manuscript docx with Sage-style unbracketed superscript citations
    # (inline figures/tables for editing/reference)
    _run(
        'generate_cct_docx.py',
        OUT_MD,
        OUT_DOCX,
        '--journal', 'Clinical Trials: Journal of the Society for Clinical Trials',
        '--strip-citation-brackets',
    )

    # Generate a submission docx with placeholders in the text and figure legends at the end,
    # per Sage/Clinical Trials artwork guidelines (external figures uploaded separately).
    _run(
        'generate_cct_docx.py',
        OUT_MD,
        OUT_SUB_DOCX,
        '--journal', 'Clinical Trials: Journal of the Society for Clinical Trials',
        '--strip-citation-brackets',
        '--no-inline-figures',
        '--figure-legends-at-end',
    )

    # Editable figures PPTX
    _run('build_figures_pptx.py', '--md', OUT_MD, '--out', OUT_FIGURES_PPTX)

    # Editable tables docx extracted from the main manuscript
    _run('build_tables_docx.py', '--src', OUT_DOCX, '--out', OUT_TABLES_DOCX)

    # Supplementary tables docx (S1-S4) extracted from CCTC outputs
    _run('build_supplementary_tables_clinical_trials_docx.py')

    # Supplementary figures PPTX (editable, one slide per supplementary figure)
    _run(
        'build_supplementary_figures_pptx.py',
        '--cctc-md', CCTC_MD,
        '--out', OUT_SUPP_FIGURES_PPTX,
        '--base-dir', BASE,
    )

    # Cover letter (regenerated after the manuscript so word/figure counts are available)
    _run('build_cover_letter_clinical_trials.py')

    # Remove non-ASCII (especially CJK/full-width) characters from Office XML metadata.
    # Equation symbols in OMML are preserved; only font/theme/numbering metadata are cleaned.
    for _path in [OUT_DOCX, OUT_SUB_DOCX, OUT_TABLES_DOCX, OUT_SUPP_DOCX,
                  OUT_FIGURES_PPTX, OUT_SUPP_FIGURES_PPTX,
                  os.path.join(BASE, 'cover_letter_ClinicalTrials.docx')]:
        if os.path.exists(_path):
            _san.sanitize_file(_path)

    # Copy high-resolution figure files for upload
    _copy_submission_figures()

    # Build zip package
    _build_submission_package()

    print('\nClinical Trials deliverables ready:')
    for p in [OUT_MD, OUT_DOCX, OUT_SUB_DOCX, OUT_TABLES_DOCX, OUT_FIGURES_PPTX, OUT_SUPP_FIGURES_PPTX,
              OUT_SUPP_DOCX, os.path.join(BASE, 'submission_package_ClinicalTrials.zip')]:
        print(' -', os.path.basename(p))


if __name__ == '__main__':
    main()
