#!/usr/bin/env python3
"""Generate corrected RSM markdown with proper numbering."""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, '03_paper_draft.md'), 'r') as f:
    text = f.read()

# Reference remapping: old -> new (in order of first appearance)
ref_map = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9,
    10: 10, 11: 11, 12: 12, 13: 13,
    20: 14, 21: 15, 22: 16, 23: 17, 24: 18, 25: 19,
    26: 20, 27: 21, 28: 22, 29: 23,
    14: 24, 15: 25, 16: 26, 17: 27, 18: 28,
}

# Split into sections
sections = {}
section_order = []
cur = '_preamble_'
cur_lines = []
for line in text.split('\n'):
    if line.startswith('## '):
        if cur_lines:
            sections[cur] = '\n'.join(cur_lines)
            section_order.append(cur)
        cur = line.strip()
        cur_lines = [line]
    else:
        cur_lines.append(line)
if cur_lines:
    sections[cur] = '\n'.join(cur_lines)
    section_order.append(cur)

print("Sections:", section_order)

# Renumber citations
def renumber_citations(block):
    def repl(m):
        inner = m.group(1)
        nums = [s.strip() for s in inner.split(',')]
        try:
            ints = [int(n) for n in nums]
        except ValueError:
            return m.group(0)
        if all(1 <= n <= 29 for n in ints):
            return '[' + ', '.join(str(ref_map.get(n, n)) for n in ints) + ']'
        return m.group(0)
    return re.sub(r'\[(\d+(?:,\s*\d+)*)\]', repl, block)

skip = {'## References', '## Tables', '## Figures', '## Additional files'}
for s in section_order:
    if s not in skip:
        sections[s] = renumber_citations(sections[s])

# Figure remapping: old -> new
fig_map = {1: 1, 2: 2, 3: 3, 4: 4, 7: 5, 6: 6, 5: 7, 8: 8}

def renumber_figs(block):
    def repl(m):
        num = int(m.group(1))
        suffix = m.group(2) or ''
        new = fig_map.get(num, num)
        return 'Fig. <<F' + str(new) + '>>' + suffix
    r = re.sub(r'Fig\.\s*(\d+)([AB]?)', repl, block)
    r = re.sub(r'<<F(\d+)>>', r'\1', r)
    return r

for s in section_order:
    if s not in skip:
        sections[s] = renumber_figs(sections[s])

# Add missing figure citations
ek = '## Empirical validation'
if ek in sections:
    sections[ek] = sections[ek].replace(
        'Table 5 presents results across the discounting grid.',
        'Table 5 presents results across the discounting grid, with the full forest plot in Fig. 4.'
    )
    sections[ek] = sections[ek].replace(
        'Table 6 presents results.',
        'Table 6 presents results, with the full forest plot in Fig. 6.'
    )

# Rebuild references
ref_text = sections.get('## References', '')
refs = {}
for line in ref_text.split('\n'):
    m = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
    if m:
        refs[int(m.group(1))] = m.group(2)

new_refs = ['## References', '']
for new_num in range(1, 29):
    old_nums = [k for k, v in ref_map.items() if v == new_num]
    if old_nums and old_nums[0] in refs:
        new_refs.append(f'{new_num}. {refs[old_nums[0]]}')
    else:
        print(f'WARNING: missing ref {new_num}')
sections['## References'] = '\n'.join(new_refs)

# Rebuild figures section
fc = {
    1: ('Overview of the KOTHA Framework. Module K (Counterfactual Power Simulation) uses retrospective cohort data to quantify risk-profile shift and estimate power under counterfactual enrollment scenarios. Module T (Bayesian Evidence Integration) combines RCT and observational evidence using hierarchical models with power-prior discounting. Module H (Guideline Interpreter) synthesizes outputs from Modules K and T into a structured GRADE-compatible assessment for guideline committees. Arrows indicate data flow between modules.', 'fig1_framework_overview.png'),
    2: ('Risk-profile shift in the magnesium-in-AMI case. (A) Control-group mortality rates over time, with bubble size proportional to study sample size. Colors indicate era classification. (B) Weighted mean control mortality by era, showing the decline from pre-thrombolysis to thrombolysis era.', 'fig2_risk_profile_shift.png'),
    3: ('Estimated power by enrollment scenario and true effect size. (A) Magnesium in AMI at the ISIS-4 sample size (N = 58,050). (B) Statins in HF at the combined RCT sample size (N = 9,585). Horizontal dashed lines indicate 80% power threshold. S1 = real-world/observational event rate; S2 = RCT event rate; S3 = intermediate/enriched rate.', 'fig3_power_curves.png'),
    4: ('Forest plot for magnesium in AMI. Individual study odds ratios are shown with 95% confidence intervals, color-coded by era. Pooled estimates include frequentist random-effects (pre-ISIS-4 and all trials) and Bayesian integrated estimates at selected discounting levels (alpha = 0.3, 0.5, 1.0).', 'fig4_forest_plot_mg.png'),
    5: ('Sensitivity analysis of Bayesian integration to the discounting parameter alpha. (A) Magnesium in AMI. (B) Statins in HF. Three posterior probability thresholds are shown: P(effect < 1.0), P(effect < 0.90), and P(effect < 0.80). Horizontal dashed line indicates 95% probability threshold.', 'fig7_sensitivity_analysis.png'),
    6: ('Forest plot for statins in heart failure. Individual study hazard ratios are shown with 95% confidence intervals, grouped by design (RCT vs. observational). Pooled estimates include design-specific frequentist pooling and KOTHA-integrated estimates at selected discounting levels (alpha = 0.1, 0.3, 0.5).', 'fig6_forest_statins.png'),
    7: ("Trial sequential analysis for magnesium in AMI. The cumulative Z-curve is plotted against cumulative events. Vertical dashed line indicates the optimal information size (OIS). Curved lines show O'Brien-Fleming monitoring boundaries. Key studies (LIMIT-2, ISIS-4) are annotated.", 'fig5_tsa_magnesium.png'),
    8: ('Module H assessment comparison: standard GRADE vs. KOTHA-enhanced evaluation for both validation cases. Color coding indicates severity of concern (green = no concern, yellow = moderate, red = serious).', 'fig8_module_h_comparison.png'),
}

flines = ['## Figures', '']
for n in sorted(fc):
    cap, fn = fc[n]
    flines.append(f'**Fig. {n}** {cap}')
    flines.append('')
    flines.append(f'![Fig. {n}](validation/figures/{fn})')
    flines.append('')
sections['## Figures'] = '\n'.join(flines)

# Update Additional files
sections['## Additional files'] = (
    '## Additional files\n\n'
    '**Additional file 1**: Study-level data tables for both validation cases (Tables S1--S2), including trial characteristics, event counts, and era classification.\n\n'
    '**Additional file 2**: Python validation code implementing all three modules with figure generation.\n\n'
    '**Additional file 3**: Complete Bayesian integration results across all alpha and delta grid values.\n\n'
    '**Additional file 4**: ADEMP reporting checklist for Module K simulation component.\n\n'
    '**Additional file 5**: Module H checklist template for guideline committees, with worked examples and decision flowchart.\n'
)

# Assemble
full = '\n'.join(sections[s] for s in section_order) + '\n'
out = os.path.join(BASE, '04_paper_rsm.md')
with open(out, 'w') as f:
    f.write(full)
print(f'\nSaved to {out}')

# Verification
body = full[:full.index('## References')]
co = []
for m in re.finditer(r'\[(\d+(?:,\s*\d+)*)\]', body):
    for ns in re.split(r',\s*', m.group(1)):
        try:
            n = int(ns.strip())
            if 1 <= n <= 28 and n not in co:
                co.append(n)
        except:
            pass
print(f'\nCitation order: {co}')
exp = list(range(1, len(co)+1))
print('Citations PASS' if co == exp else f'Citations FAIL: {co} vs {exp}')

fo = []
for m in re.finditer(r'Fig\.\s*(\d+)', body):
    n = int(m.group(1))
    if n not in fo:
        fo.append(n)
print(f'Figure order: {fo}')
ef = list(range(1, len(fo)+1))
print('Figures PASS' if fo == ef else f'Figures FAIL: {fo} vs {ef}')

to = []
for m in re.finditer(r'Table\s+(\d+)', body):
    n = int(m.group(1))
    if n not in to:
        to.append(n)
print(f'Table order: {to}')
et = list(range(1, len(to)+1))
print('Tables PASS' if to == et else f'Tables FAIL: {to} vs {et}')

rr = full[full.index('## References'):]
rn = [int(m.group(1)) for m in re.finditer(r'^(\d+)\.\s+', rr, re.MULTILINE)]
print(f'Refs in list: {len(rn)}, cited: {len(co)}')
print('Uncited:', sorted(set(rn)-set(co)) or 'none')
print('Missing entries:', sorted(set(co)-set(rn)) or 'none')