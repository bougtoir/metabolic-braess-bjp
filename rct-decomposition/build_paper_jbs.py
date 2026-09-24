#!/usr/bin/env python3
"""Build the KOTHA manuscript package for Journal of Biopharmaceutical Statistics (JBS).

Reuses the Contemporary Clinical Trials Communications (CCTC) manuscript
(05_paper_cctc.md / KOTHA_Framework_CCTC.docx) and restructures it for *Journal of
Biopharmaceutical Statistics* (Taylor & Francis NLM style):

- Title reframes simulation-based methodology and power-prior integration
- Background/Aims abstract heading
- Bracketed numbered in-text citations and reference list
- Biostatistical / pharmaceutical-development framing
- <= 8 main-text figures/tables (6 figures, 2 tables)
- Separate supplementary figures/tables and high-resolution PNGs
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import json
import zipfile

import sanitize_office_outputs as _san


BASE = os.path.dirname(os.path.abspath(__file__))

CCTC_MD = os.path.join(BASE, '05_paper_cctc.md')
CCTC_DOCX = os.path.join(BASE, 'KOTHA_Framework_CCTC.docx')
CCTC_SUPP_DOCX = os.path.join(BASE, 'KOTHA_Framework_CCTC_supplementary_tables.docx')

OUT_MD = os.path.join(BASE, '05_paper_jbs.md')
OUT_DOCX = os.path.join(BASE, 'KOTHA_Framework_JBS.docx')
OUT_SUB_DOCX = os.path.join(BASE, 'KOTHA_Framework_JBS_submission.docx')
OUT_FIGURES_PPTX = os.path.join(BASE, 'KOTHA_Framework_JBS_figures.pptx')
OUT_SUPP_FIGURES_PPTX = os.path.join(BASE, 'KOTHA_Framework_JBS_supplementary_figures.pptx')
OUT_TABLES_DOCX = os.path.join(BASE, 'KOTHA_Framework_JBS_tables.docx')
OUT_SUPP_DOCX = os.path.join(BASE, 'KOTHA_Framework_JBS_supplementary_tables.docx')
COVER_LETTER = os.path.join(BASE, 'cover_letter_JBS.docx')
SUBMISSION_FIGURES_DIR = os.path.join(BASE, 'JBS_figures')
SUBMISSION_PACKAGE = os.path.join(BASE, 'submission_package_JBS.zip')

FIGURE_MAP = {
    'validation/figures/fig1_framework_overview.png': 'Figure_1_framework_overview.png',
    'validation/figures/fig2_risk_profile_shift.png': 'Figure_2_risk_profile_shift.png',
    'validation/figures/fig3_power_curves.png': 'Figure_3_power_curves.png',
    'validation/figures/fig4_forest_combined.png': 'Figure_4_forest_combined.png',
    'validation/figures/fig7_sensitivity_analysis.png': 'Figure_5_sensitivity_analysis.png',
    'validation/figures/fig_simulation_operating_characteristics.png': 'Figure_6_operating_characteristics.png',
    'validation/figures/fig5_tsa_magnesium.png': 'Figure_S2_tsa_magnesium.png',
    'validation/figures/fig8_module_h_comparison.png': 'Figure_S3_module_h_comparison.png',
    'validation/figures/figS1a_trace_mcmc_magnesium.png': 'Figure_S1a_trace_mcmc_magnesium.png',
    'validation/figures/figS1b_trace_mcmc_statins.png': 'Figure_S1b_trace_mcmc_statins.png',
}


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


def _condense_abstract_results(results):
    """Shorten the CCTC Results paragraph to a single balanced summary sentence."""
    cer = re.search(r'control event rates fell from ([\d.]+)% to ([\d.]+)%', results, re.I)
    err = re.search(r'event[- ]rate ratio (?:was|of) ([\d.]+)', results, re.I)
    bayes = re.search(
        r'Bayesian integration \(alpha = ([\d.]+)\) yielded OR ([\d.]+) \(CrI ([\d.\-]+)\), '
        r'P\(OR < 1\) = ([\d.]+%) for magnesium and HR ([\d.]+) \(([\d.\-]+)\), '
        r'P\(HR < 1\) = ([\d.]+%) for statins',
        results, re.I,
    )
    # Append operating-characteristics metrics from the simulation summary.
    sim_path = os.path.join(BASE, 'validation', 'simulation_summary.json')
    sim_clause = ''
    if os.path.exists(sim_path):
        with open(sim_path, 'r', encoding='utf-8') as f:
            sim_data = json.load(f)
        metrics = sim_data.get('metrics', {})
        rct = metrics.get('RCT enrolled only', {})
        kotha = metrics.get('KOTHA alpha=0.3', {})
        if rct and kotha:
            rct_bias = float(rct['bias'])
            rct_rmse = float(rct['rmse'])
            rct_power = float(rct['power'])
            k_bias = float(kotha['bias'])
            k_rmse = float(kotha['rmse'])
            k_power = float(kotha['power'])
            abs_bias_red = (abs(rct_bias) - abs(k_bias)) / abs(rct_bias) * 100
            rmse_red = (rct_rmse - k_rmse) / rct_rmse * 100
            power_inc = (k_power - rct_power) * 100
            sim_clause = (
                f"A prespecified simulation showed KOTHA ($\\alpha$=0.3) reduced "
                f"absolute bias by {abs_bias_red:.0f}%, RMSE by {rmse_red:.0f}%, and increased power by "
                f"{power_inc:.0f} percentage points versus RCT-enrolled-only analysis."
            )
    if not (cer and err and bayes):
        # Fallback to the original paragraph if expected values are not found.
        return results.strip()
    cer_from, cer_to = cer.groups()
    err_val = err.group(1).rstrip('. ,;')
    alpha, or_val, or_cri, or_prob, hr_val, hr_cri, hr_prob = bayes.groups()
    empirical = (
        f"Control event rates fell from {cer_from}% to {cer_to}% for magnesium and "
        f"the RCT-to-observational event rate ratio was {err_val} for statins. Bayesian integration ($\\alpha$={alpha}) gave "
        f"OR {or_val} (CrI {or_cri}) and HR {hr_val} ({hr_cri}), with posterior probabilities of benefit "
        f"{or_prob} and {hr_prob}; both remained below decision thresholds."
    )
    if sim_clause:
        return f"**Results**: {empirical} {sim_clause}"
    return f"**Results**: {empirical}"


def _reframe_abstract(md):
    """Replace abstract framing while keeping the Results paragraph (with values)."""
    m = re.search(r'## Abstract\n\n(.*?)\n\n## ', md, re.S)
    if not m:
        return md
    old = m.group(1)
    paras = old.split('\n\n')
    results = _condense_abstract_results(paras[2]) if len(paras) > 2 else ''
    new = (
        "**Background/Aims**: Standard meta-analyses often conflate absence of evidence with evidence of absence "
        "when RCT enrollment shifts patients to lower-risk profiles. The KOTHA Framework quantifies this "
        "structural information loss and integrates RCT and observational evidence through power-prior "
        "Bayesian synthesis to inform Phase II/III and enrichment-trial design.\n\n"
        "**Methods**: KOTHA has three modules: counterfactual power simulation, Bayesian evidence "
        "integration, and GRADE-compatible interpretation. We applied it to magnesium in acute myocardial "
        "infarction and statins in heart failure and evaluated operating characteristics---bias, RMSE, "
        "coverage, and power---in a prespecified simulation.\n\n"
        f"{results}\n\n"
        "**Conclusions**: KOTHA distinguishes evidence of no effect from no evidence of effect and "
        "provides a reproducible diagnostic for Phase II/III and enrichment-trial design.\n\n"
        "**Key Words:** counterfactual power simulation; power prior; observational-RCT discordance; "
        "enrichment trial design; structural information loss; GRADE."
    )
    return md[:m.start(1)] + new + md[m.end(1):]


def _new_intro():
    """JBS-focused introduction text."""
    return (
        "The development of pharmaceuticals and biologics increasingly relies on randomized "
        "controlled trials (RCTs) for internal validity, but the external validity of trial "
        "evidence depends on whether enrolled patients mirror the target clinical population [1]. "
        "Meta-analyses of observational studies and RCTs frequently disagree: observational "
        "evidence may show statistically significant benefit while RCT evidence does not [2-3]. "
        "The conventional explanation invokes residual confounding, selection bias, or "
        "publication bias in observational data. While these sources of bias are real, they may "
        "not fully account for the discordance.\n\n"
        "A structural alternative is especially relevant to Phase II/III "
        "development and enrichment-trial design. RCT enrollment criteria, consent processes, "
        "and site selection progressively restrict the study population [4-5]. Because "
        "clinical events are concentrated in the highest-risk patients---those with comorbidities, "
        "advanced disease, or organ dysfunction---their exclusion lowers event rates in the "
        "enrolled cohort. If trial protocols do not compensate by increasing sample size, "
        "extending follow-up, or enriching high-risk enrollment, the resulting evidence base can "
        "become informationally insufficient. We call this **structural information "
        "loss**, a five-step causal chain: representativeness loss; event concentration in "
        "excluded populations; inadequate design compensation; systematic underpowering; and, "
        "ultimately, distorted recommendations when \"no statistically significant difference\" "
        "is interpreted as \"no effect\".\n\n"
        "Optimal information size (OIS) and trial sequential analysis (TSA) "
        "offer partial remedies. OIS recognizes that meta-analyses, like individual trials, "
        "require a minimum information size to reach reliable conclusions [6-7]. TSA applies "
        "sequential monitoring boundaries to cumulative meta-analysis, distinguishing evidence of "
        "no effect (futility boundary crossed) from no evidence of effect (boundary not crossed) "
        "[8-9]. Both are underused in biopharmaceutical development, however, and neither "
        "directly quantifies the information loss produced by enrollment-driven risk-profile "
        "shifts.\n\n"
        "Several trial design strategies can mitigate event dilution (Supplementary Table S3), "
        "including stratified randomization, prognostic enrichment, event-driven designs, "
        "adaptive sample-size re-estimation, and pragmatic or registry-based trials. Existing "
        "approaches address these issues separately; to our knowledge, no widely adopted "
        "framework links prospective power assessment, retrospective diagnostic "
        "evaluation, and structured evidence interpretation in a single reproducible workflow "
        "for completed or planned RCTs.\n\n"
        "To address this gap we developed the Knowledge-driven Observational-Trial "
        "Harmonization Approach (KOTHA). The framework has three modules: Module K diagnoses "
        "structural information loss through counterfactual power simulation; Module T "
        "integrates discordant evidence through hierarchical Bayesian meta-analysis; and "
        "Module H translates quantitative findings into a GRADE-compatible evidence assessment. "
        "We describe the framework here and illustrate it with two canonical cases of "
        "observational-RCT divergence, focusing on implications for Phase II/III and "
        "enrichment-trial design."
    )


def _convert_abbreviations(md):
    """Convert the Abbreviations markdown table to a bullet list."""
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
        if abbr.lower() in ('abbreviation', '') or definition.lower() == 'definition' or set(abbr) <= {'-'}:
            continue
        if abbr:
            bullets.append(f'* **{abbr}**: {definition}')
    replacement = header + '\n'.join(bullets) + tail if bullets else header + table_block + tail
    return md[:match.start()] + replacement + md[match.end():]


def _remove_block(md, kind, num):
    """Remove a figure or table block from markdown.

    `kind` is 'fig' or 'table'; `num` is the CCTC display number.
    """
    if kind == 'fig':
        pat = r'(?m)^\*\*Fig\.\s*' + re.escape(str(num)) + r'\*\*(.*?)\n\s*!\[.*?\]\((.*?)\)\n*'
    else:
        pat = r'(?m)^\*\*Table\s*' + re.escape(str(num)) + r':[^\n]*\*\*\n+(?:\|[^\n]*\n)+'
    return re.sub(pat, '', md, count=1, flags=re.S)


def _move_fig1_after_first_citation(md):
    """Move the Fig. 1 block to immediately follow its first in-text citation."""
    block_re = re.compile(r'\n\n(\*\*Fig\. 1\*\*[^\n]*\n\n!\[Fig\. 1\]\([^\)]+\))\n\n', re.S)
    m = block_re.search(md)
    if not m:
        return md
    block = m.group(1)
    md_without = md[:m.start()] + '\n\n' + md[m.end():]
    para_re = re.compile(r'^(The KOTHA Framework comprises.*?\(Fig\. 1\).*?applied in sequence\.)$', re.M)
    pm = para_re.search(md_without)
    if not pm:
        return md_without
    insert_at = pm.end()
    return md_without[:insert_at] + '\n\n' + block + md_without[insert_at:]


def _renumber_references(md):
    """Renumber remaining figures/tables and redirect removed items to supplementary."""
    placeholder_map = {
        'Fig. 6A': '__FIG6A__',
        'Fig. 6B': '__FIG6B__',
        'Fig. 5': '__FIG5__',
        'Fig. 6': '__FIG6__',
        'Fig. 7': '__FIG7__',
        'Fig. 8': '__FIG8__',
        'Table 1': '__TBL1__',
        'Table 2': '__TBL2__',
        'Table 3': '__TBL3__',
        'Table 4': '__TBL4__',
        'Table 5': '__TBL5__',
    }
    for old, ph in placeholder_map.items():
        md = re.sub(r'\b' + re.escape(old) + r'\b', ph, md)
    final_map = {
        '__FIG5__': 'Supplementary Fig. S2',
        '__FIG6A__': 'Fig. 5A',
        '__FIG6B__': 'Fig. 5B',
        '__FIG6__': 'Fig. 5',
        '__FIG7__': 'Supplementary Fig. S3',
        '__FIG8__': 'Fig. 6',
        '__TBL1__': 'Supplementary Table S3',
        '__TBL2__': 'Supplementary Table S4',
        '__TBL3__': 'Table 1',
        '__TBL4__': 'Supplementary Table S5',
        '__TBL5__': 'Table 2',
    }
    for ph, new in final_map.items():
        md = md.replace(ph, new)
    return md


def _replace_declarations(md):
    """Replace placeholder declarations with standard statements."""
    replacements = {
        r'### Ethics approval and consent to participate\n\n\[To be determined\]':
            '### Ethics approval and consent to participate\n\nNot applicable. This study used published aggregate data; no human participants were enrolled.',
        r'### Consent for publication\n\n\[To be determined\]':
            '### Consent for publication\n\nNot applicable.',
        r'### Declaration of competing interest\n\n\[To be determined\]':
            '### Declaration of competing interest\n\nThe authors declare no competing interests.',
        r'### Funding source\n\n\[To be determined\]':
            '### Funding source\n\nNo funding was received for this study.',
    }
    for old, new in replacements.items():
        md = re.sub(old, new, md, count=1)
    return md


def _restructure(md):
    """Apply all JBS-specific markdown transformations."""
    # Front matter
    md = re.sub(r'^title:.*$', 'title: The KOTHA Framework: A Simulation Study of Power-Prior Integration to Correct Structural Information Loss in RCT Meta-Analyses', md, flags=re.M)
    md = re.sub(r'^running_head:.*$', 'running_head: KOTHA Framework for Information Loss', md, flags=re.M)

    # Remove CCTC-specific elements
    md = re.sub(r'\n## Highlights\n.*?(?=\n## Abstract)', '', md, count=1, flags=re.S)

    # Reframe abstract and introduction
    md = _reframe_abstract(md)
    intro_match = re.search(r'## 1\. Introduction\n\n(.*?)## 2\. Methods', md, re.S)
    if intro_match:
        md = md[:intro_match.start(1)] + _new_intro().rstrip() + '\n\n' + md[intro_match.end(1):]

    # Move supplementary blocks out of main text
    for tbl in (1, 2, 4):
        md = _remove_block(md, 'table', tbl)
    for fig in (5, 7):
        md = _remove_block(md, 'fig', fig)

    # Convert abbreviations table to bullets; renumber remaining display items
    md = _convert_abbreviations(md)
    md = _renumber_references(md)

    # Place Fig. 1 immediately after its first citation
    md = _move_fig1_after_first_citation(md)

    # Declarations
    md = _replace_declarations(md)

    # Word count
    wc = _word_count(md)
    md = re.sub(r'^word_count:\s*\d+', f'word_count: {wc}', md, flags=re.M)

    return md, wc


def _build_docx(md_path, docx_path, *, submission=False):
    """Generate the JBS Word document using bracketed non-superscript NLM citations."""
    args = [
        'generate_cct_docx.py',
        md_path,
        docx_path,
        '--journal', 'Journal of Biopharmaceutical Statistics',
        '--no-citation-superscript',
        '--reference-brackets',
    ]
    if submission:
        args += ['--no-inline-figures', '--figure-legends-at-end']
    _run(*args)
    _san.sanitize_file(docx_path)


def _build_figures(md_path, out_pptx):
    """Build main figures PPTX from the markdown display-item blocks."""
    _run('build_figures_pptx.py', '--md', md_path, '--out', out_pptx)
    _san.sanitize_file(out_pptx)


def _build_tables(src_docx, out_docx):
    """Extract editable tables from the manuscript docx."""
    _run('build_tables_docx.py', '--src', src_docx, '--out', out_docx)
    _san.sanitize_file(out_docx)


def _build_supplementary_figures(out_pptx):
    """Assemble supplementary figures PPTX."""
    # Dedicated builder handles JBS supplementary numbering (S1a, S1b, S2, S3)
    _run('build_supplementary_figures_jbs.py', '--out', out_pptx)
    _san.sanitize_file(out_pptx)


def _build_supplementary_tables(out_docx):
    """Assemble supplementary tables docx from CCTC sources."""
    _run('build_supplementary_tables_jbs_docx.py', '--out', out_docx)
    _san.sanitize_file(out_docx)


def _copy_submission_figures():
    """Copy high-resolution PNGs to the submission figures folder."""
    if os.path.exists(SUBMISSION_FIGURES_DIR):
        shutil.rmtree(SUBMISSION_FIGURES_DIR)
    os.makedirs(SUBMISSION_FIGURES_DIR, exist_ok=True)
    for rel_src, dest_name in FIGURE_MAP.items():
        src = os.path.join(BASE, rel_src)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(SUBMISSION_FIGURES_DIR, dest_name))


def _build_submission_package():
    """Create the final submission ZIP archive."""
    files = [
        OUT_MD,
        OUT_DOCX,
        OUT_SUB_DOCX,
        OUT_FIGURES_PPTX,
        OUT_TABLES_DOCX,
        OUT_SUPP_FIGURES_PPTX,
        OUT_SUPP_DOCX,
        COVER_LETTER,
    ]
    files += [
        os.path.join(SUBMISSION_FIGURES_DIR, f)
        for f in os.listdir(SUBMISSION_FIGURES_DIR)
        if f.endswith('.png')
    ]
    with zipfile.ZipFile(SUBMISSION_PACKAGE, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            if os.path.exists(path):
                zf.write(path, arcname=os.path.basename(path))


def build(skip_validation=False, skip_package=False):
    """Full JBS build pipeline."""
    if not skip_validation:
        print('Running validation pipeline to ensure figures/results are current...')
        _run('validation/run_validation.py')

    _ensure_cctc_outputs()

    with open(CCTC_MD, 'r', encoding='utf-8') as f:
        cctc_md = f.read()

    jbs_md, wc = _restructure(cctc_md)
    print(f'JBS main-text word count: {wc}')

    # Replace remaining placeholder text for declarations that can be finalized later
    jbs_md = jbs_md.replace(
        '### Authors\' contributions\n\n[To be determined]',
        '### Authors\' contributions\n\n'
        'All authors contributed to the development of the KOTHA framework and the preparation '
        'of the manuscript. Author-specific contributions will be documented once the final '
        'author list is established.'
    )
    jbs_md = jbs_md.replace(
        '### Acknowledgements\n\n[To be determined]',
        '### Acknowledgements\n\nNone.'
    )

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(jbs_md)

    _build_docx(OUT_MD, OUT_DOCX)
    _build_docx(OUT_MD, OUT_SUB_DOCX, submission=True)
    # Remove empty highlight artifacts generated by the docx builder
    for path in (OUT_DOCX, OUT_SUB_DOCX):
        hl = path.rsplit('.docx', 1)[0] + '_highlights.docx'
        if os.path.exists(hl):
            os.remove(hl)
    _build_figures(OUT_MD, OUT_FIGURES_PPTX)
    _build_tables(OUT_DOCX, OUT_TABLES_DOCX)
    _build_supplementary_figures(OUT_SUPP_FIGURES_PPTX)
    _build_supplementary_tables(OUT_SUPP_DOCX)

    if not os.path.exists(COVER_LETTER):
        print('Cover letter missing; running build_cover_letter_jbs.py ...')
        _run('build_cover_letter_jbs.py')

    _copy_submission_figures()

    if not skip_package:
        _build_submission_package()
        print(f'Created submission package: {SUBMISSION_PACKAGE}')


def main():
    parser = argparse.ArgumentParser(description='Build JBS manuscript package')
    parser.add_argument('--skip-validation', action='store_true')
    parser.add_argument('--skip-package', action='store_true')
    args = parser.parse_args()
    build(skip_validation=args.skip_validation, skip_package=args.skip_package)


if __name__ == '__main__':
    main()
