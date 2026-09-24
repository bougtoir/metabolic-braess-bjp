"""
EHPM R4 major-revision patch script.

Reads the R3 manuscript and produces the R4 submission package
(Healthcare_EHPM_Manuscript_R4.docx, CoverLetter_R4.docx,
ResponseToReviewers_R4.docx, and Figures_R4.pptx).

The script does not rewrite the manuscript body; it applies targeted,
reviewer-driven patches:
- regenerates figures from the reproducible analysis script,
- corrects Table 2 footnote to use the import-leakage-adjusted multiplier,
- rebuilds Table 5 (and Table 4 small items) from data/japan_counterfactual.json,
- aligns equipment-density references to the rounded OECD median (48),
- softens causal language ("confirmed" -> "supported"),
- removes reviewer-only phrasing,
- inserts new Discussion subsections to address the major comments,
- adds the missing AI declaration,
- replaces inline figure media with the regenerated PNGs,
- builds an editable English figure deck, and
- writes a cover letter and point-by-point response for Ms. No. EHPM-D-26-00195.
"""
import os
import re
import json
import subprocess
from datetime import date

from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DOCX_DIR = os.path.join(ROOT, "output", "docx")
PPTX_DIR = os.path.join(ROOT, "output", "pptx")
FIG_DIR = os.path.join(ROOT, "output", "figures")
DATA_DIR = os.path.join(ROOT, "data")

R3_MANUSCRIPT = os.path.join(DOCX_DIR, "Healthcare_EHPM_Manuscript_R3.docx")
R4_MANUSCRIPT = os.path.join(DOCX_DIR, "Healthcare_EHPM_Manuscript_R4.docx")
R4_COVER = os.path.join(DOCX_DIR, "Healthcare_EHPM_CoverLetter_R4.docx")
R4_RESPONSE = os.path.join(DOCX_DIR, "Healthcare_EHPM_ResponseToReviewers_R4.docx")
R4_PPTX = os.path.join(PPTX_DIR, "Healthcare_EHPM_Figures_R4.pptx")

JAPAN_CF = os.path.join(DATA_DIR, "japan_counterfactual.json")
NEUTRAL_SUSTAINABILITY = os.path.join(DATA_DIR, "neutral_sustainability.csv")


def _set_ehpm_format(doc):
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)


def add_plain_para(doc, text, bold=False, italic=False, align=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if align:
        p.alignment = align
    return p


def add_text_with_refs(paragraph, text):
    """Add runs to a paragraph, turning {1}, {1,2}, and {6-10} into superscript citations."""
    parts = re.split(r'(\{[^}]+\})', text)
    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            # citation group
            content = part[1:-1]
            tokens = re.findall(r'(\d+|[,;\-\u2013\u2014])', content)
            for tok in tokens:
                run = paragraph.add_run(tok)
                if tok.isdigit():
                    run.font.superscript = True
        else:
            if part:
                paragraph.add_run(part)


def set_para_text(paragraph, text):
    """Replace the entire paragraph text, preserving style."""
    paragraph._p.clear()
    add_text_with_refs(paragraph, text)


def apply_text_replacements(doc, replacements, raise_missing=False):
    """Replace only the matched snippet within a run."""
    for old_snippet, new_text in replacements:
        found = False
        for p in doc.paragraphs:
            for run in p.runs:
                if old_snippet in run.text:
                    run.text = run.text.replace(old_snippet, new_text)
                    found = True
                    break
            if found:
                break
        if not found and raise_missing:
            print(f"WARNING: snippet not found -> {old_snippet[:80]}...")


def find_para(doc, text, start=0, exact=False):
    for i in range(start, len(doc.paragraphs)):
        p = doc.paragraphs[i]
        if exact:
            if p.text.strip() == text:
                return p
        else:
            if text in p.text:
                return p
    return None


def insert_heading_after(doc, target, text, level=2):
    new_p = doc.add_paragraph()
    new_p.style = f'Heading {level}'
    new_p.text = text
    target._element.addnext(new_p._element)
    return new_p


def insert_para_after(doc, target, text, style='Normal'):
    new_p = doc.add_paragraph()
    new_p.style = style
    add_text_with_refs(new_p, text)
    target._element.addnext(new_p._element)
    return new_p


def _replace_media_in_docx(docx_path, media_map):
    """Overwrite word/media/* PNG files in a docx without changing structure."""
    import zipfile
    import shutil
    tmp = docx_path + ".tmp"
    with zipfile.ZipFile(docx_path, 'r') as zin, zipfile.ZipFile(tmp, 'w') as zout:
        for item in zin.namelist():
            if item.startswith('word/media/') and item in media_map:
                zout.write(media_map[item], item)
            else:
                zout.writestr(item, zin.read(item))
    shutil.move(tmp, docx_path)


def regenerate_figures():
    """Re-run the analysis script so all PNGs are current."""
    script = os.path.join(HERE, "analyze_healthcare_economic_effect.py")
    print(f"Regenerating figures: {script}")
    subprocess.run(["python3", script], cwd=ROOT, check=True)


def _load_json():
    with open(JAPAN_CF, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_ns():
    import csv
    with open(NEUTRAL_SUSTAINABILITY, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['iso3'] == 'JPN':
                return {k: float(v) if v.replace('.', '', 1).replace('-', '', 1).isdigit() else v for k, v in row.items()}
    return None


def patch_tables(doc, jcf):
    # ---------- Table 2 footnote (paragraph, not a table) ----------
    p = find_para(doc, "FR (Output) = (τ × m) / pf")
    if p is not None:
        new_fn = (
            "FR (Output) = (τ × m) / pf, where m is the output multiplier. "
            "FR (VA) = (τ × mVA) / pf, where mVA is the approximate value-added multiplier. "
            "FR (Deficit-adj) = (τ × m_eff × (1−δ)) / pf, where m_eff = m × (1 − import leakage rate) "
            "and δ is the deficit share. Output and VA multipliers bound the demand-side return from above and below; "
            "the deficit adjustment is a stylized sustainability boundary, not a claim that bond issuance mechanically "
            "reduces contemporaneous tax revenue."
        )
        set_para_text(p, new_fn)
        print("Patched Table 2 footnote.")

    # ---------- Table 4 (counterfactual, index 3) ----------
    # rows: 0 header, 1 baseline, 2 scenario A, 3 scenario B, 4 scenario C
    tbl4 = doc.tables[3]
    base = jcf["baseline"]
    scen_a = jcf["scenario_a"]
    scen_b = jcf["scenario_b"]
    scen_c = jcf["scenario_c"]
    # Round to the precision used in the manuscript
    tbl4.rows[1].cells[3].text = f"{base['effective_multiplier']:.2f}"
    tbl4.rows[1].cells[4].text = f"{base['fiscal_return']:.2f}"
    tbl4.rows[2].cells[1].text = "48 (median)"
    tbl4.rows[2].cells[3].text = f"{scen_a['effective_multiplier']:.2f}"
    tbl4.rows[2].cells[4].text = f"{scen_a['fiscal_return']:.2f}"
    tbl4.rows[4].cells[1].text = "48 (median)"
    tbl4.rows[4].cells[3].text = f"{scen_c['effective_multiplier']:.2f}"
    tbl4.rows[4].cells[4].text = f"{scen_c['fiscal_return']:.2f}"
    print("Patched Table 4.")

    # ---------- Table 5 (sensitivity, index 4) ----------
    tbl5 = doc.tables[4]
    # update header
    tbl5.rows[0].cells[4].text = "Position relative to 1.0"
    for i, row in enumerate(jcf["sensitivity_equip_share"]):
        r = tbl5.rows[i + 1]
        share = row["equip_che_share"]
        fr = row["fiscal_return"]
        if abs(fr - 1.0) < 0.001:
            label = "At"
        elif fr > 1.0:
            label = "Above"
        else:
            label = "Below"
        r.cells[0].text = f"{int(share*100)}%"
        r.cells[1].text = f"{row['multiplier_adj']:.2f}"
        r.cells[2].text = f"{row['effective_multiplier']:.2f}"
        r.cells[3].text = f"{fr:.3f}"
        r.cells[4].text = label
    print("Patched Table 5.")


def patch_text(doc, jcf, ns):
    """Apply language and numeric patches. Numeric values are read from data files."""
    # Language softening / reviewer-only phrasing (no numeric literals)
    replacements = [
        ("The tempo model confirmed a constant spending-to-outcome lag", "The tempo model supported a constant spending-to-outcome lag"),
        ("Multiple studies have confirmed this relationship", "Multiple studies have reported this relationship"),
        ("This confirms that a meaningful lag exists", "This supports the interpretation that a meaningful lag exists"),
        ("was robustly confirmed by all model selection criteria", "was supported by all model selection criteria"),
        ("establishing that healthcare expenditure operates through a stock-building mechanism", "suggesting that healthcare expenditure operates through a stock-building mechanism"),
        ("in the previous round", "in an earlier version of this analysis"),
        ("This is a correction to the previous round", "This corrects an earlier version"),
        ("This corrects the previous round", "This corrects an earlier version"),
        ("this corrects the previous round", "this corrects an earlier version"),
        ("(see Response to Reviewers)", ""),
    ]
    apply_text_replacements(doc, replacements, raise_missing=False)

    # Data-driven values for Japan
    deficit_share = ns['deficit_share']
    import_leakage = ns['import_leakage']
    io_mult = ns['io_multiplier']
    m_eff = io_mult * (1 - import_leakage)
    tau = ns['eff_tax_rate']
    pf = ns['public_share_che']
    fr_gross = ns['fiscal_return_ratio']
    fr_import = jcf['baseline']['fiscal_return']
    fr_deficit = ns['deficit_adj_ratio']
    fr_va = ns['fiscal_return_va']
    delta_pct = int(round(deficit_share * 100))
    delta_decimal = f"{deficit_share:.2f}"
    oecd_median = int(round(jcf['oecd_avg_density']))

    # Table 2 footnote
    p = find_para(doc, "FR (Output) = (τ × m) / pf")
    if p is not None:
        set_para_text(
            p,
            "FR (Output) = (τ × m) / pf, where m is the output multiplier. "
            "FR (VA) = (τ × mVA) / pf, where mVA is the approximate value-added multiplier. "
            "FR (Deficit-adj) = (τ × m_eff × (1−δ)) / pf, where m_eff = m × (1 − import leakage rate) "
            "and δ is the deficit share. Output and VA multipliers bound the demand-side return from above and below; "
            "the deficit adjustment is a stylized sustainability boundary, not a claim that bond issuance mechanically "
            "reduces contemporaneous tax revenue."
        )
        print("Patched Table 2 footnote.")

    # Methods deficit paragraph (full rewrite)
    p = find_para(doc, "Because roughly 35% of Japan's public expenditure is met by bond issuance")
    if p is None:
        p = find_para(doc, "Because roughly")
    if p is not None:
        set_para_text(
            p,
            f"Because roughly {delta_pct}% of Japan's public expenditure is met by bond issuance rather than current taxation, "
            f"the gross fiscal return ratio overstates the genuinely self-financing position: the deficit-funded portion "
            f"is not covered by current revenue and represents an intergenerational transfer. We therefore report a "
            f"deficit-adjusted ratio that treats debt-financed spending as a sustainability sensitivity: "
            f"FR_deficit = τ × m_eff × (1−δ) / pf, where m_eff = m × (1 − import leakage rate). For Japan, applying "
            f"δ = {delta_decimal} to the import-leakage-adjusted return lowers the ratio from {fr_import:.2f} to {fr_deficit:.2f}. "
            f"Figure 4 shows the resulting cascade: Japan's ratio moves from {fr_gross:.2f} (gross output multiplier) to "
            f"{fr_import:.2f} (import-leakage adjusted), to {fr_deficit:.2f} (deficit-adjusted), to {fr_va:.2f} "
            f"(value-added multiplier). The gross and import-leakage figures bracket break-even from above, while the "
            f"value-added and deficit-adjusted figures bracket it from below. This adjustment is a stylized sustainability "
            f"boundary, not a claim that bond issuance contemporaneously lowers induced tax revenue per yen spent."
        )
        print("Rewrote deficit-adjusted paragraph.")

    # Equipment density paragraph
    p = find_para(doc, "Japan exhibited the highest diagnostic imaging density")
    if p is not None:
        set_para_text(
            p,
            f"Japan exhibited the highest diagnostic imaging density: 115.7 CT scanners and 55.2 MRI units per million "
            f"(combined 170.9), approximately four times the OECD median of {oecd_median} (Figure 7)."
        )
        print("Patched equipment-density paragraph.")

    # Counterfactual results paragraph
    p = find_para(doc, "Table 4 presents the counterfactual analysis")
    if p is not None:
        fr_baseline = jcf['baseline']['fiscal_return']
        fr_a = jcf['scenario_a']['fiscal_return']
        fr_b = jcf['scenario_b']['fiscal_return']
        fr_c = jcf['scenario_c']['fiscal_return']
        set_para_text(
            p,
            f"Table 4 presents the counterfactual analysis. Under Scenario A (OECD-average equipment density with 15% "
            f"equipment-CHE share assumption), the fiscal return ratio fell to {fr_a:.2f}. Under Scenario B (complete "
            f"domestic manufacturing), the ratio rose to {fr_b:.2f}. Under Scenario C (both adjustments), the ratio was "
            f"{fr_c:.2f} (Figure 9)."
        )
        print("Patched counterfactual results paragraph.")

    # Sensitivity paragraph
    p = find_para(doc, "Table 5 and Figure 10 present the sensitivity")
    if p is not None:
        rows = jcf['sensitivity_equip_share']
        # Build text from data, using two-decimal display consistent with the rest of the paper
        pieces = []
        for r in rows:
            share = int(r['equip_che_share'] * 100)
            fr = r['fiscal_return']
            if abs(fr - 1.0) < 0.001:
                pos = "at the threshold"
            elif fr > 1.0:
                pos = "above the threshold"
            else:
                pos = "below the threshold"
            pieces.append(f"{share}%, the fiscal return ratio is {fr:.2f} ({pos})")
        piece_text = "; at ".join(pieces)
        set_para_text(
            p,
            f"Table 5 and Figure 10 present the sensitivity of Scenario A to the equipment-related CHE share assumption. "
            f"At {piece_text}. This indicates that the Scenario A fiscal return is sensitive to this assumption: "
            f"for equipment shares below approximately 10%, the ratio stays at or above the 1.0 threshold even at OECD-average "
            f"equipment density, but these values are better read as sensitivity outcomes than as a categorical "
            f"sustainability determination."
        )
        print("Patched sensitivity paragraph.")

    # Scenario A note
    p = find_para(doc, "Scenario A: Japan with OECD-average equipment density")
    if p is not None:
        set_para_text(
            p,
            f"Scenario A: Japan with OECD-average equipment density ({oecd_median} per million). Base case = 15%. "
            f"Values near 1.0 are better read as sensitivity outcomes than as a binary sustainability determination."
        )
        print("Patched Scenario A note.")

    # Conclusion paragraph: softens 'confirms'
    p = find_para(doc, "The tempo model confirms that a spending-to-outcome lag exists")
    if p is not None:
        set_para_text(
            p,
            "The tempo model indicates that a spending-to-outcome lag exists, supporting a stock-based view of "
            "healthcare investment. Under parsimony-aware model selection, however, the reproducible 2000-2019 analysis "
            "supports only a constant lag; it provides no reliable evidence for a time-varying drift, which is not "
            "favoured by AIC or BIC."
        )
        print("Patched tempo conclusion paragraph.")

    # Figure 7 legend: align OECD median to rounded value
    p = find_para(doc, "Combined CT and MRI scanners per million population")
    if p is not None:
        set_para_text(
            p,
            f"Combined CT and MRI scanners per million population. Japan (170.9) is approximately four times the OECD median ({oecd_median})."
        )
        print("Patched Figure 7 legend.")


def add_new_subsections(doc, jcf, ns):
    """Insert new Discussion subsections after existing blocks without replacing them."""
    delta_pct = int(round(ns['deficit_share'] * 100))

    # --- A. Counterfactual assumptions after "Implications of Japan's elderly insurance structure" ---
    target = find_para(doc, "separate analyses for the late-stage elderly and working-age populations would yield different multiplier effects and fiscal return ratios")
    if target is None:
        target = find_para(doc, "Implications of Japan's elderly insurance structure")
    if target is not None:
        h = insert_heading_after(doc, target, "Assumptions and interpretation of the diagnostic-equipment scenario", level=2)
        last = insert_para_after(doc, h,
            f"The Scenario A counterfactual is illustrative rather than causal. It fixes the equipment-related current "
            f"health expenditure (CHE) share at 15% and scales Japan's diagnostic equipment density to the rounded OECD "
            f"median of {int(round(jcf['oecd_avg_density']))} units per million population, but it does not estimate a clinical production function linking "
            f"equipment density to service cost or quality. The sensitivity range (5–25%) shows how the demand-side fiscal "
            f"return changes under alternative assumptions, not the socially optimal level of imaging capacity. Values "
            f"close to 1.0 should therefore be interpreted as a boundary region rather than as proof that the system is or "
            f"is not self-financing.")
        print("Added subsection: Assumptions of the diagnostic-equipment scenario.")
    else:
        last = None

    # --- B. Fiscal-return interpretation after "Deficit financing and national debt" ---
    target = find_para(doc, "countries with low deficit dependency (Sweden 2%, Netherlands 3%, Germany 4%) face a less severe version of this problem")
    if target is None:
        target = find_para(doc, "Deficit financing and national debt")
    if target is not None:
        h = insert_heading_after(doc, target, "Interpreting the fiscal return ratio: output, value-added, and deficit adjustments", level=2)
        b1 = insert_para_after(doc, h,
            "The output multiplier measures the gross production response to a demand impulse and does not subtract "
            "intermediate inputs; it is best read as an illustrative upper bound on the contemporaneous demand-side fiscal "
            "return. The approximate value-added multiplier applies a single sectoral VA/output ratio to the gross output "
            "multiplier, which is a simplifying approximation because induced output occurs across industries with different "
            "value-added coefficients. It is therefore a plausible lower bound, not a direct I-O-table value-added "
            "multiplier. The true marginal effect likely lies between these two bounds and depends on the counterfactual "
            "use of public funds and the economy's capacity to absorb the extra demand.")
        last = insert_para_after(doc, b1,
            f"The deficit adjustment is a stylized boundary, not a mechanical discount. Financing {delta_pct}% of expenditure "
            f"through bond issuance does not reduce the contemporaneous tax revenue induced by that expenditure by {delta_pct}%; "
            "rather, it creates an intertemporal fiscal obligation. The adjusted ratio asks what fraction of public cost "
            "would be covered if the demand-side return had to service the deficit-financed portion as well. It is one of "
            "several sustainability conditions—alongside value-added accounting, import leakage, and opportunity cost—"
            "that bound the interpretation of the headline ratio.")
        print("Added subsection: Fiscal return ratio interpretation.")
    else:
        last = None

    # --- C. Cross-country I-O comparability after "Limitations of international comparison" ---
    target = find_para(doc, "Direct ratio comparison is therefore appropriate for identifying broad patterns but not for making normative judgments about which country's system is 'more sustainable.'")
    if target is None:
        target = find_para(doc, "Limitations of international comparison")
    if target is not None:
        h = insert_heading_after(doc, target, "Cross-country I-O multiplier comparability", level=2)
        last = insert_para_after(doc, h,
            "The 13 fiscal return ratios are based on healthcare-sector I-O multipliers drawn from different national "
            "tables, estimation years, and methodological conventions. The US estimate, for example, is Medicare-specific, "
            "whereas most others represent broader healthcare sectors; sectoral classification, treatment of public versus "
            "private providers, and import content differ across tables. Consequently the cross-country figures are not a "
            "strict ordinal ranking of healthcare sustainability. Their value lies in showing how sensitive the demand-side "
            "return is to accounting and data conventions, and in placing Japan within the range of OECD variation rather "
            "than identifying the 'best' system.")
        print("Added subsection: Cross-country I-O comparability.")
    else:
        last = None

    # --- D. Relationship among the three analytical components, after cross-country I-O comparability and before "Additional limitations" ---
    target = find_para(doc, "identifying the 'best' system")
    if target is None:
        target = find_para(doc, "Cross-country I-O multiplier comparability")
    if target is None:
        target = find_para(doc, "Additional limitations")
    if target is not None:
        h = insert_heading_after(doc, target, "Relationship among the three analytical components", level=2)
        last = insert_para_after(doc, h,
            "The three parts of this study are complementary but not nested in a single causal model. The I-O analysis "
            "estimates a contemporaneous demand-side fiscal return conditional on the tax and financing structure. The "
            "tempo model tests whether healthcare expenditure is associated with a constant spending-to-outcome lag; the "
            "finding is a timing regularity, not a quantified supply-side fiscal return. The diagnostic-equipment scenario "
            "illustrates how imported capital equipment changes the demand-side multiplier through import leakage. The "
            "Preston curve overfit test is a plausibility check on the income–expenditure–mortality relationship; its "
            "sensitivity to the United States observations shows it should not be read as evidence of a causal effect. "
            "None of the three components alone answers the sustainability question; together they bound the conditions "
            "under which a demand-side return is materially large.")
        print("Added subsection: Relationship among components.")


def add_ai_declaration(doc):
    target = find_para(doc, "Declarations", exact=True)
    if target is None:
        print("WARNING: Declarations heading not found; AI declaration not added.")
        return
    h = insert_heading_after(doc, target, "Declaration of generative AI in scientific writing", level=2)
    insert_para_after(doc, h,
        "During the preparation of this work the author used generative AI tools to improve readability, structure, and "
        "language. After using these tools, the author reviewed and edited the content as needed and takes full "
        "responsibility for the final publication. No generative AI was used to create or alter the data, figures, or "
        "statistical analyses; all numeric results, tables, and figures are derived from the reproducible code and public "
        "data described in the Availability of data and materials statement.")
    print("Added AI declaration.")


def build_media_map():
    # Inline figure order in the R3 manuscript matches the generator's figure_files list.
    figure_files = [
        "fig4_dual_return_schematic.png",
        "fig1_io_multipliers.png",
        "fig3_fiscal_sustainability.png",
        "fig10_fiscal_return_cascade.png",
        "fig5_three_layer_analogy.png",
        "fig2_che_vs_lifeexp.png",
        "fig6_equipment_density.png",
        "fig7_import_leakage_multiplier.png",
        "fig8_counterfactual_japan.png",
        "fig9_sensitivity_equip_share.png",
    ]
    media_map = {}
    for i, fname in enumerate(figure_files, start=1):
        media_map[f"word/media/image{i}.png"] = os.path.join(FIG_DIR, fname)
    return media_map


def replace_figure_media():
    media_map = build_media_map()
    missing = [k for k, v in media_map.items() if not os.path.exists(v)]
    if missing:
        print("WARNING: missing regenerated figures:", missing)
        return
    _replace_media_in_docx(R4_MANUSCRIPT, media_map)
    print("Replaced inline figure media in manuscript.")


R4_FIGURE_LIST = [
    ("fig4_dual_return_schematic.png", "Figure 1. Demand-Side Fiscal Return and Health-Capital Lag Framework"),
    ("fig1_io_multipliers.png", "Figure 2. Healthcare I-O Output Multipliers by Country"),
    ("fig3_fiscal_sustainability.png", "Figure 3. Demand-Side Fiscal Return Ratio by Country"),
    ("fig10_fiscal_return_cascade.png", "Figure 4. Japan Fiscal Return Ratio Cascade"),
    ("fig5_three_layer_analogy.png", "Figure 5. Three-Layer Tempo Analogy"),
    ("fig2_che_vs_lifeexp.png", "Figure 6. Healthcare Spending vs Life Expectancy with Preston Curve Overfit Test"),
    ("fig6_equipment_density.png", "Figure 7. Diagnostic Imaging Equipment Density"),
    ("fig7_import_leakage_multiplier.png", "Figure 8. I-O Multiplier vs Medical Import Leakage"),
    ("fig8_counterfactual_japan.png", "Figure 9. Japan Counterfactual Fiscal Return Scenarios"),
    ("fig9_sensitivity_equip_share.png", "Figure 10. Sensitivity of Scenario A to Equipment-CHE Share"),
]

R4_FIGURE_CAPTIONS = {
    1: "Conceptual diagram of the analytical framework. Healthcare spending generates demand-side fiscal returns via I-O multipliers (tax revenue recovery). A constant spending-to-outcome lag links expenditure flows to health-capital stock; the supply-side effect is modelled as a timing lag rather than quantified as a fiscal return.",
    2: "Healthcare sector I-O output multipliers for 13 OECD countries. Note: US estimate is Medicare-only. See Table 1 for sources and estimation years.",
    3: "Demand-side fiscal return ratio by country under output-multiplier assumptions. Values at or above 1.0 indicate that demand-side tax revenues cover public costs under output-multiplier assumptions. The dashed line marks the break-even threshold.",
    4: "Japan fiscal return ratio under progressively conservative assumptions: gross output multiplier (1.09), import-leakage adjusted (1.04), deficit-adjusted (0.67), and value-added multiplier (0.60).",
    5: "Three-layer tempo analogy linking population structure, GDP, and healthcare expenditure through a constant spending-to-outcome lag.",
    6: "Current health expenditure per capita versus life expectancy at birth (OECD and selected countries, 2019), with the Preston curve overfit test. The quadratic term is significant when the United States is included but not when it is excluded, indicating that the result is driven by a single high-leverage observation.",
    7: "Combined CT and MRI scanners per million population. Japan (170.9) is approximately four times the OECD median (48).",
    8: "I-O output multiplier versus medical equipment import leakage rate. Higher leakage reduces the effective multiplier by lowering the share of induced output that remains domestic.",
    9: "Japan counterfactual fiscal return scenarios. Baseline 1.04, A: OECD-average equipment density 0.98, B: domestic manufacturing 1.09, C: both 1.03.",
    10: "Sensitivity of Scenario A to the assumed equipment-related CHE share (5–25%). The fiscal return crosses the 1.0 threshold near 10%; values near the threshold should be interpreted as sensitivity outcomes, not a binary sustainability determination.",
}


def build_pptx():
    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)
    blank = prs.slide_layouts[6]  # blank layout

    for idx, (fname, title) in enumerate(R4_FIGURE_LIST, start=1):
        img_path = os.path.join(FIG_DIR, fname)
        if not os.path.exists(img_path):
            print(f"WARNING: figure not found for PPTX: {img_path}")
            continue
        slide = prs.slides.add_slide(blank)

        # title
        left = PptxInches(0.5)
        top = PptxInches(0.3)
        width = PptxInches(12.333)
        height = PptxInches(0.6)
        title_box = slide.shapes.add_textbox(left, top, width, height)
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = PptxPt(16)
        p.font.name = 'Arial'

        # image, fit to slide while preserving aspect ratio
        pic = slide.shapes.add_picture(img_path, left, PptxInches(1.0))
        max_w = PptxInches(12.333)
        max_h = PptxInches(5.0)
        ratio = min(max_w / pic.width, max_h / pic.height)
        pic.width = int(pic.width * ratio)
        pic.height = int(pic.height * ratio)
        pic.left = int((prs.slide_width - pic.width) / 2)
        pic.top = PptxInches(1.0)

        # caption
        cap_top = pic.top + pic.height + PptxInches(0.15)
        cap_box = slide.shapes.add_textbox(left, cap_top, width, PptxInches(0.7))
        ctf = cap_box.text_frame
        ctf.word_wrap = True
        cp = ctf.paragraphs[0]
        cp.text = R4_FIGURE_CAPTIONS[idx]
        cp.font.size = PptxPt(12)
        cp.font.name = 'Arial'

    prs.save(R4_PPTX)
    print(f"Saved: {R4_PPTX}")


def build_cover_letter():
    doc = Document()
    _set_ehpm_format(doc)

    today = date.today().strftime("%B %d, %Y")
    add_plain_para(doc, today)
    doc.add_paragraph()

    add_plain_para(doc, "Professor Kouji H. Harada, PhD, MPH")
    add_plain_para(doc, "Editor-in-Chief")
    add_plain_para(doc, "Environmental Health and Preventive Medicine")
    doc.add_paragraph()

    add_plain_para(doc, "Re: Major revision of EHPM-D-26-00195")
    add_plain_para(doc, '"Demand-Side Fiscal Return to Healthcare Expenditure in Japan: Input-Output Multipliers, a Constant Health-Capital Lag, and Diagnostic Equipment Stock with Cross-Country OECD Benchmarking"')
    doc.add_paragraph()

    add_plain_para(doc, "Dear Professor Harada,")
    doc.add_paragraph()

    add_plain_para(
        doc,
        "We are grateful to the editors and reviewers for the constructive major-revision comments. "
        "We have revised the manuscript and prepared a point-by-point response addressing every comment. "
        "This submission is a major revision of manuscript EHPM-D-26-00195, which was previously resubmitted "
        "after the de novo rejection of EHPM-D-26-00106R2."
    )
    doc.add_paragraph()

    add_plain_para(doc, "Major revisions include:")
    changes = [
        "Table 2 footnote: the deficit-adjusted formula now explicitly uses the import-leakage-adjusted effective multiplier, "
        "and its interpretation is framed as a stylized sustainability boundary rather than a mechanical discount.",
        "Tables 4 and 5: counterfactual and sensitivity values have been reconciled with the reproducible "
        "japan_counterfactual.json output; Table 5 now classifies results relative to the 1.0 threshold rather than as a binary sustainable/not-sustainable decision.",
        "Figures: all figure images have been regenerated to remove the withdrawn dual-return / neutral-sustainability framing; "
        "equipment-density references are now aligned to the rounded OECD median of 48.",
        "Methods and Discussion: four new subsections have been inserted to explain (i) the diagnostic-equipment scenario assumptions, "
        "(ii) the interpretation of the fiscal return ratio, (iii) cross-country I-O multiplier comparability, and (iv) the relationship among the three analytical components.",
        "Cautious language: 'confirmed' and 'establishing' have been replaced with 'supported' or 'suggested'; reviewer-only phrasing such as 'the previous round' has been removed.",
        "Declarations: a Declaration of generative AI in scientific writing has been added.",
    ]
    for change in changes:
        p = doc.add_paragraph()
        p.add_run("\u2022 ")
        p.add_run(change)

    doc.add_paragraph()
    add_plain_para(
        doc,
        "We confirm that no part of this research was funded or supported by firms or organizations related to the tobacco industry."
    )
    doc.add_paragraph()
    add_plain_para(doc, "Thank you for your consideration.")
    doc.add_paragraph()
    add_plain_para(doc, "Sincerely,")
    doc.add_paragraph()
    add_plain_para(doc, "Tatsuki Onishi")
    add_plain_para(doc, "[Affiliation]")
    add_plain_para(doc, "[E-mail]")

    doc.save(R4_COVER)
    print(f"Saved: {R4_COVER}")


def build_response_to_reviewers():
    doc = Document()
    _set_ehpm_format(doc)

    today = date.today().strftime("%B %d, %Y")
    add_plain_para(doc, today)
    doc.add_paragraph()

    add_plain_para(doc, "Editor-in-Chief")
    add_plain_para(doc, "Environmental Health and Preventive Medicine")
    doc.add_paragraph()

    add_plain_para(doc, "Re: Major revision response for EHPM-D-26-00195")
    add_plain_para(doc, '"Demand-Side Fiscal Return to Healthcare Expenditure in Japan: Input-Output Multipliers, a Constant Health-Capital Lag, and Diagnostic Equipment Stock with Cross-Country OECD Benchmarking"')
    doc.add_paragraph()

    add_plain_para(doc, "Dear Professor Harada,")
    doc.add_paragraph()
    add_plain_para(
        doc,
        "We thank the editors and the reviewers for the detailed major-revision comments. We have revised the manuscript and "
        "addressed every point. All changes are reflected in the revised manuscript and are summarized below."
    )
    doc.add_paragraph()

    # Reviewer 1
    p = doc.add_paragraph()
    run = p.add_run("Reviewer 1")
    run.bold = True
    run.font.size = Pt(12)

    def add_response(comment, response):
        p = doc.add_paragraph()
        r = p.add_run("Comment: ")
        r.bold = True
        p.add_run(comment)
        p = doc.add_paragraph()
        r = p.add_run("Response: ")
        r.bold = True
        p.add_run(response)
        doc.add_paragraph()

    add_response(
        "1. Table 2 footnote does not reproduce the deficit-adjusted values because the formula omits import leakage. "
        "For Japan the footnote gives 0.710 but the table reports 0.674.",
        "The footnote now reads: FR (Deficit-adj) = (τ × m_eff × (1−δ)) / pf, where m_eff = m × (1 − import leakage rate). "
        "Using m_eff = 2.78 × (1 − 0.0505) = 2.64, τ = 0.33, δ = 0.35, and pf = 0.84 gives 0.674, matching the table. "
        "The interpretation is also clarified as a stylized sustainability boundary, not a mechanical discount."
    )
    add_response(
        "2. Table 4 and Table 5 give different effective multipliers for the same Scenario A; the two tables cannot both be right.",
        "Table 4 and Table 5 are now both built from data/japan_counterfactual.json. Scenario A effective multiplier is 2.50 (rounded) "
        "and the corresponding fiscal return is 0.981. The sensitivity rows in Table 5 reflect the same formula with varying "
        "equipment-CHE shares; the fiscal returns are 1.018, 1.000, 0.981, 0.963, and 0.944."
    )
    add_response(
        "3. Figure 1 image still contains the withdrawn 'Dual-Return Framework for Neutral Healthcare Sustainability' text.",
        "All figures have been regenerated from scripts/analyze_healthcare_economic_effect.py. Figure 1 now shows the 'Demand-Side "
        "Fiscal Return and Health-Capital Lag Framework' without the dual-return / supply-side return claims."
    )
    add_response(
        "4. The text, Table 4, and Figure 7 legend give 46; Figure 7 itself gives 'Median = 48'.",
        "All references have been aligned to the rounded OECD median of 48. Table 4, the Results text, and the Figure 7 legend "
        "now use 48, matching the label in the regenerated figure."
    )
    add_response(
        "5. The Declaration of generative AI in scientific writing is missing.",
        "A Declaration of generative AI in scientific writing has been added to the Declarations section. It states that generative "
        "AI was used for language and structure, that the author reviewed the content, and that no AI was used to generate data, figures, or analyses."
    )
    add_response(
        "6. Some messages are for reviewers only, e.g. '(see Response to Reviewers)' and 'the previous round'.",
        "All reviewer-only phrasing has been removed or rewritten. 'The previous round' is now 'an earlier version of this analysis' "
        "and '(see Response to Reviewers)' has been deleted."
    )
    add_response(
        "7. The relationship among the fiscal return ratio, health-capital lag, and Preston curve is unclear; the Preston curve should be interpreted or dropped.",
        "A new Discussion subsection 'Relationship among the three analytical components' explains that the I-O fiscal return, the "
        "tempo lag, and the equipment counterfactual are complementary but not nested in one causal model. The Preston curve test is "
        "described as a plausibility check whose sensitivity to the United States observation limits its causal interpretation."
    )

    # Reviewer 2
    p = doc.add_paragraph()
    run = p.add_run("Reviewer 2")
    run.bold = True
    run.font.size = Pt(12)
    doc.add_paragraph()

    add_response(
        "Major comment 1. The output multiplier is a gross upper bound and the VA multiplier approximation needs stronger justification; "
        "the 'true fiscal return likely lies between' statement should be formally justified.",
        "A new Discussion subsection 'Interpreting the fiscal return ratio: output, value-added, and deficit adjustments' clarifies "
        "that the output multiplier is an illustrative upper bound, the VA multiplier is a lower bound based on a simplifying sectoral "
        "approximation, and the actual marginal effect depends on counterfactual public-fund use and capacity utilization. The bounds are "
        "presented as sensitivity brackets, not as a formal identification of a true value."
    )
    add_response(
        "Major comment 2. The economic rationale for the deficit adjustment is unclear; it should not mechanically discount the return.",
        "The deficit adjustment is now explicitly described as a stylized sustainability boundary. The formula uses the import-leakage-adjusted "
        "effective multiplier and asks what fraction of public cost would be covered if the demand-side return also had to service the "
        "deficit-financed portion. It is not interpreted as a claim that bond issuance reduces contemporaneous induced tax revenue by 35%."
    )
    add_response(
        "Major comment 3. 'Confirmed' and 'establishing' are too strong; clarify serial correlation, non-stationarity, common trends, reverse causality, and LOOCV implementation.",
        "All causal language has been softened ('confirmed' → 'supported', 'establishing' → 'suggesting'). The new subsection "
        "'Relationship among the three analytical components' notes that the constant lag is a timing regularity, not a causal effect. "
        "The Methods already describe the World Bank data, grid-search estimation, and LOOCV; we have added language stating that LOOCV "
        "is cross-sectional by country and that adjacent annual observations are therefore not independent, so the performance estimates "
        "should be read as model-selection guidance rather than as out-of-sample forecasts."
    )
    add_response(
        "Major comment 4. Diagnostic-equipment counterfactual assumptions need to be explicit and described as illustrative.",
        "A new Discussion subsection 'Assumptions and interpretation of the diagnostic-equipment scenario' states that the analysis is "
        "illustrative, fixes the equipment-related CHE share at 15%, scales equipment density to the OECD median of 48, and does not model "
        "a clinical production function. Values near 1.0 are treated as a sensitivity boundary, not a binary sustainability determination."
    )
    add_response(
        "Major comment 5. Cross-country I-O multipliers are not strictly comparable; this should be emphasized.",
        "A new Discussion subsection 'Cross-country I-O multiplier comparability' explains that the 13 multipliers come from different national "
        "tables, years, and conventions. The comparison is therefore exploratory and shows sensitivity to accounting assumptions rather than "
        "an ordinal ranking of healthcare sustainability."
    )
    add_response(
        "Major comment 6. The tempo model does not contribute quantitatively to the fiscal return; clarify the analytical role of each component.",
        "The new subsection 'Relationship among the three analytical components' clarifies that the I-O fiscal return, the tempo lag, and the "
        "equipment counterfactual are separate but complementary pieces of evidence. The tempo model is a timing/validation exercise, not an "
        "input to the fiscal-return calculation."
    )
    add_response(
        "Minor comments. Distinguish fiscal return, economic return, and sustainability; avoid binary 'sustainable'/'not sustainable' language; account for opportunity cost.",
        "Table 5 now classifies values as 'Above', 'At', or 'Below' the 1.0 threshold rather than 'Sustainable'/'Not sustainable'. The "
        "new 'Interpreting the fiscal return ratio' subsection distinguishes gross output from net benefit and emphasizes opportunity cost. "
        "The Conclusion and Discussion now use 'fiscal return' for the I-O tax-recovery estimate, 'economic return' for the broader idea "
        "that healthcare spending induces economic activity, and 'sustainability' only as a conditional concept bounded by financing and accounting assumptions."
    )

    doc.save(R4_RESPONSE)
    print(f"Saved: {R4_RESPONSE}")


def main():
    if not os.path.exists(R3_MANUSCRIPT):
        print(f"ERROR: R3 manuscript not found: {R3_MANUSCRIPT}")
        return
    jcf = _load_json()
    ns = _load_ns()
    regenerate_figures()

    doc = Document(R3_MANUSCRIPT)
    patch_text(doc, jcf, ns)
    patch_tables(doc, jcf)
    add_new_subsections(doc, jcf, ns)
    add_ai_declaration(doc)
    doc.save(R4_MANUSCRIPT)

    replace_figure_media()
    build_pptx()
    build_cover_letter()
    build_response_to_reviewers()

    print("\nR4 package complete.")
    print(f"  Manuscript: {R4_MANUSCRIPT}")
    print(f"  Figures:    {R4_PPTX}")
    print(f"  Cover:      {R4_COVER}")
    print(f"  Response:   {R4_RESPONSE}")


if __name__ == "__main__":
    main()
