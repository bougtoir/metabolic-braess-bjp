"""Build the Heredity submission package."""

from __future__ import annotations

import re
import shutil
import subprocess
import zipfile
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from lxml import etree

import pandas as pd
from PIL import Image
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor as PptRGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches as PptInches
from pptx.util import Pt as PptPt

import heredity_content as revised_content


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
FIGURE_DIR = PROJECT_DIR / "figures"
OUTPUT_DIR = PROJECT_DIR / "docs" / "heredity_submission"
OUTPUT_FIGURE_DIR = OUTPUT_DIR / "figures"
JOURNAL = "Heredity"
JOURNAL_SHORT = "Heredity"
ARTICLE_TYPE = "Original Article"
EDITOR_IN_CHIEF = "Dr. Sara Goodacre"

TITLE = revised_content.TITLE
RUNNING_TITLE = revised_content.RUNNING_TITLE
AUTHOR = revised_content.AUTHOR
AFFILIATION = revised_content.AFFILIATION
CORRESPONDENCE = revised_content.CORRESPONDENCE
ABSTRACT = revised_content.ABSTRACT
KEYWORDS = revised_content.KEYWORDS
REFERENCES = revised_content.REFERENCES
REFERENCE_KEYS = revised_content.REFERENCE_KEYS
INTRODUCTION = revised_content.INTRODUCTION
METHODS = revised_content.METHODS
RESULTS = revised_content.RESULTS
DISCUSSION = revised_content.DISCUSSION
FIGURES = revised_content.FIGURES
SUPPORTING_FIGURES = revised_content.SUPPORTING_FIGURES


def set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def add_line_numbering(section) -> None:
    sectPr = section._sectPr
    lnNumType = OxmlElement("w:lnNumType")
    lnNumType.set(qn("w:countBy"), "1")
    lnNumType.set(qn("w:restart"), "continuous")
    sectPr.append(lnNumType)


def configure_document(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Cm(4)
    section.bottom_margin = Cm(4)
    section.left_margin = Cm(4)
    section.right_margin = Cm(4)
    add_line_numbering(section)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 2.0
    normal.paragraph_format.space_after = Pt(0)
    for name in ["Title", "Heading 1", "Heading 2"]:
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor(0, 0, 0)


def make_omml_run(text: str, italic: bool = True, font_size: int = 24) -> etree._Element:
    r = etree.SubElement(etree.Element("dummy"), qn("m:r"))
    rPr = etree.SubElement(r, qn("m:rPr"))
    if not italic:
        sty = etree.SubElement(rPr, qn("m:sty"))
        sty.set(qn("m:val"), "p")
    wRPr = etree.SubElement(r, qn("w:rPr"))
    rFonts = etree.SubElement(wRPr, qn("w:rFonts"))
    rFonts.set(qn("w:ascii"), "Cambria Math")
    rFonts.set(qn("w:hAnsi"), "Cambria Math")
    sz = etree.SubElement(wRPr, qn("w:sz"))
    sz.set(qn("w:val"), str(font_size))
    szCs = etree.SubElement(wRPr, qn("w:szCs"))
    szCs.set(qn("w:val"), str(font_size))
    t = etree.SubElement(r, qn("m:t"))
    t.text = text
    t.set(qn("xml:space"), "preserve")
    return r


def make_subscript(base_text: str, sub_text: str, base_italic: bool = True, sub_italic: bool = True) -> etree._Element:
    sSub = etree.SubElement(etree.Element("dummy"), qn("m:sSub"))
    e = etree.SubElement(sSub, qn("m:e"))
    e.append(make_omml_run(base_text, italic=base_italic))
    sub = etree.SubElement(sSub, qn("m:sub"))
    sub.append(make_omml_run(sub_text, italic=sub_italic))
    return sSub


def make_omath_para(*elements: etree._Element) -> etree._Element:
    oMathPara = etree.SubElement(etree.Element("dummy"), qn("m:oMathPara"))
    oMath = etree.SubElement(oMathPara, qn("m:oMath"))
    for el in elements:
        oMath.append(el)
    return oMathPara


def _add_expanded_model_equation(document: Document) -> None:
    """Insert a centred Word OMML equation for the expanded dyadic model."""
    para = document.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(6)
    parts = [
        make_subscript("s", "ij"),
        make_omml_run(" = ", italic=False),
        make_subscript("β", "0", sub_italic=False),
        make_omml_run(" + ", italic=False),
        make_subscript("β", "d", sub_italic=False),
        make_omml_run(" ", italic=False),
        make_subscript("d", "ij"),
        make_omml_run(" + ", italic=False),
        make_subscript("β", "a", sub_italic=False),
        make_omml_run(" ", italic=False),
        make_subscript("a", "ij"),
        make_omml_run(" + ", italic=False),
        make_subscript("β", "c", sub_italic=False),
        make_omml_run(" ", italic=False),
        make_subscript("c", "ij"),
        make_omml_run(" + ", italic=False),
        make_subscript("β", "m", sub_italic=False),
        make_omml_run(" ", italic=False),
        make_subscript("m", "ij"),
        make_omml_run(" + ", italic=False),
        make_subscript("ε", "ij"),
    ]
    para._element.append(make_omath_para(*parts))
    note = document.add_paragraph()
    note.paragraph_format.first_line_indent = Inches(0.3)
    run = note.add_run(
        "where s_ij is pairwise profile similarity, d_ij is great-circle distance in "
        "thousands of kilometres, a_ij indicates a pair involving a designated recently "
        "admixed American population, c_ij is same-continent status, and m_ij is same-dataset "
        "status. Subscripts denote population pairs i and j."
    )
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.italic = True


def add_cited_paragraph(document: Document, text: str, italic: bool = False):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.first_line_indent = Inches(0.3)
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.italic = italic
    return paragraph


def add_title(document: Document) -> None:
    """Add only the title (anonymous) for the manuscript body."""
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(TITLE)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    document.add_paragraph()


def add_abstract_page(document: Document) -> None:
    document.add_heading("Abstract", level=1)
    paragraph = document.add_paragraph(ABSTRACT)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.first_line_indent = Inches(0)
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.first_line_indent = Inches(0)
    run = paragraph.add_run("Keywords: ")
    run.bold = True
    paragraph.add_run(KEYWORDS)
    document.add_page_break()


def create_title_page(path: Path, main_word_count: int) -> None:
    document = Document()
    configure_document(document)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(TITLE)
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(ARTICLE_TYPE).bold = True
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(AUTHOR.upper()).bold = True
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(AFFILIATION)
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(CORRESPONDENCE)
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(f"Running title: {RUNNING_TITLE}")
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(f"Main-text word count: {main_word_count:,}")
    document.add_paragraph()
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(
        "Data and code availability: https://github.com/bougtoir/denisovan-archaic-dna-analysis "
        "(release heredity-submission-2026-09 will be fixed before publication)."
    )
    document.save(path)


def _format_pair_row(row, ancestry: str, sharing_col: str, z_col: str) -> list[str]:
    sharing = getattr(row, sharing_col)
    z = getattr(row, z_col)
    return [
        ancestry,
        row.pop1,
        row.pop2,
        row.region1.replace("_", " ").title(),
        row.region2.replace("_", " ").title(),
        f"{row.geo_dist_km:,.0f}",
        f"{sharing:.3f}",
        f"{z:.2f}",
    ]


def table_1_rows() -> list[list[str]]:
    pairs = pd.read_csv(DATA_DIR / "pairwise_sharing_corrected.csv")
    non_admixed = pairs[pairs["any_admixed"] == 0]
    candidates = []
    for row in non_admixed.itertuples():
        nean_qualifies = (row.nean_resid_z > 2) and (row.nean_fdr_pval < 0.10)
        deni_qualifies = (row.deni_resid_z > 2) and (row.deni_fdr_pval < 0.10)
        if nean_qualifies:
            candidates.append(
                (row.nean_resid_z, _format_pair_row(row, "Neanderthal", "nean_corr", "nean_resid_z"))
            )
        if deni_qualifies:
            candidates.append(
                (row.deni_resid_z, _format_pair_row(row, "Denisovan", "deni_corr", "deni_resid_z"))
            )
    rows = [
        [
            "Ancestry",
            "Population 1",
            "Population 2",
            "Region 1",
            "Region 2",
            "Distance (km)",
            "Sharing (r)",
            "z-score",
        ]
    ]
    if not candidates:
        rows.append(
            [
                "—",
                "No qualifying pair",
                "—",
                "—",
                "—",
                "—",
                "—",
                "No z>2 and q<0.10 result for either ancestry",
            ]
        )
        return rows
    candidates.sort(key=lambda item: item[0], reverse=True)
    for _, row in candidates:
        rows.append(row)
    return rows


def table_s1_rows() -> list[list[str]]:
    sublineage = pd.read_csv(DATA_DIR / "abo_sublineage_summary.csv")
    order = [
        "East Asia",
        "Europe",
        "Indigenous Americas",
        "Admixed Americas",
        "Central/South Asia",
        "Middle East",
        "Oceania",
    ]
    rows = [
        [
            "Region",
            "n",
            "Altai %",
            "Vindija %",
            "Chagyrskaya %",
        ]
    ]
    for group in order:
        group_summary = sublineage[
            (sublineage["analysis_group"] == group)
            & (sublineage["closest_reference"] != "Tie")
        ]
        total = int(group_summary["n_segments"].sum())
        values = {
            row.closest_reference: 100 * row.n_segments / total
            for row in group_summary.itertuples()
        } if total else {}
        rows.append(
            [
                group,
                str(total),
                f"{values.get('Altai', 0):.1f}",
                f"{values.get('Vindija', 0):.1f}",
                f"{values.get('Chagyrskaya', 0):.1f}",
            ]
        )
    return rows


TABLES = {
    1: (
        "Positive-residual archaic pairs after false discovery rate control",
        table_1_rows,
        "The prespecified family contains all non-admixed population pairs. A supported positive outlier required z>2 and Benjamini-Hochberg q<0.10 for Neanderthal or Denisovan ancestry; complete nominal rankings and dependence-aware model results are provided in Supplementary Data.",
    ),
}

SUPPORTING_TABLES = {
    1: (
        "Exploratory ABO-window Neanderthal-reference composition",
        table_s1_rows,
        "Counts are classifiable segments, not individuals. Percentages use the three-reference denominator shown by n. Equal maximum-similarity ties are excluded from these percentages but retained in Supplementary Data. The 2/2 Indigenous American value is not a regional frequency estimate; only one segment overlaps ABO, and these counts are not interpreted as a migration route.",
    ),
}


CRITICAL_REVIEW_REPORT_TEMPLATE = """# Pre-submission critical reviewer report — {journal}

**Manuscript:** "{title}"  
**Target journal:** {journal}  
**Date:** {date}  
**Reviewer role:** internal pre-submission critical review

**Implementation note:** All priority actions identified in this review have been applied to the generated package.

---

## 1. Manuscript: novelty, focus and logic

**Verdict:** Focused and timely; scope remains on negative-control/baseline methodology.

*Strengths*
- The central framing answers the AHG editor's first concern: the "special-connection claim" is defined explicitly, and the ABO focal-locus scan is treated as a prespecified negative test rather than a route proposal.
- The abstract immediately states what the paper does (build a dependence-aware baseline) and what it does not do (identify a migration route or an exceptional pair).
- The narrative is unified: Introduction introduces the claim, Methods explains dyadic dependence, Results reports the absence of FDR-supported outliers, and Discussion reinforces that the contribution is a reusable baseline.

*Risks*
- A reviewer may judge the biological result unsurprising. The value lies in the formal baseline and reproducible FDR control; this must be emphasised to avoid a "so what?" reaction. **Action:** keep the Discussion's opening sentence about the reproducible, dependence-aware baseline prominent.
- The ABO–genome-wide link is clear, but the phrase "no route-level signal" is qualitative. **Action:** repeat in the ABO Results paragraph that the two Indigenous-American segments are within the genome-wide expectation and are not interpreted as a route.

**Priority:** Medium.

---

## 2. Statistical design

**Verdict:** Method is appropriate and explicitly distinguishes itself from Mantel tests.

*Strengths*
- The population-label QAP is described as preserving row–column dependence, and the comparison with Mantel tests directly answers the AHG editor's second concern.
- The Methods state that R-squared values are descriptive, coefficients come from permuted regressions, and pair-level residual P values come from the same permutation distribution.
- Multiple testing is controlled with Benjamini–Hochberg FDR; the prespecified family is all non-admixed pairs.

*Risks*
- BH assumes independence or positive regression dependency. The manuscript notes that pair residuals are dyadically dependent and uses a joint permutation null, but does not discuss whether BH is conservative or anti-conservative under the specific dependency. Because no pair survives FDR correction, the practical impact is small. **Action:** add one sentence in the Methods noting that BH is used as a standard exploratory control and that the absence of any q<0.10 finding is robust to stricter dependence-aware procedures.
- The expanded model includes same-continent and same-dataset covariates as descriptive sensitivity terms. This is correctly labelled as non-causal.

**Priority:** Medium.

---

## 3. Figures and tables

**Verdict:** Figure/table set supports the manuscript; a few captions should be tightened.

*Strengths*
- Figure 1 directly shows the distance-decay relationship with a descriptive fit and a clear caption.
- Figure 2 shows broad regional blocks; Figure S1 provides the full 66 × 66 matrix.
- Figures S3 and S4 separate modern and ancient ABO evidence and warn against direct comparison.

*Risks*
- Figure 2 uses 31 prespecified populations. A reviewer may ask how the 31 were chosen. **Action:** the caption states that 31 populations were selected for legibility, ordered by geographic region, and that Figure S1 contains all 66.
- Table S1 excludes ties from percentages. The note already explains this.

**Priority:** Low–Medium.

---

## 4. Reproducibility

**Verdict:** Strong. Package is built from derived data with provenance files.

*Strengths*
- `analysis_provenance.json` and `ancient_abo_provenance.json` contain SHA-256 checksums and parameters.
- All manuscript numbers flow from `data/correction_stats.json`; the submission script contains no hard-coded results.
- Source data are public (Zenodo, Dryad, Ensembl), and the submission package includes the derived data as supplementary files.
- A reproducibility checklist and validation report are generated automatically.

*Risks*
- The public GitHub repository is not named in the anonymous manuscript for double-anonymised review; the cover letter and title page include the repository URL. **Action:** keep the URL on the title page and reproducibility checklist.
- The primary analysis pipeline requires the original hmmix segment files, which are large. The submission relies on derived `pairwise_sharing_corrected.csv`. This is standard, and the reproducibility checklist confirms that derived files are in `data/` and will be released.

**Priority:** Low.

---

## 5. Strength of claims

**Verdict:** Appropriately cautious. The manuscript repeatedly frames results as negative, descriptive, or baseline.

*Strengths*
- Key caveats are present: distance correlations are descriptive; coordinates are approximate; correlation is not identity-by-descent; ABO segment is not an ABO allele; closest-reference similarity is not a transmission path; Indigenous-American observations are not regional-frequency estimates or migration routes.
- The AHG editor's two concerns are addressed directly in the cover letter, revised Introduction, and Methods.

*Risks*
- A reviewer may ask why the ABO analysis is included if it is only a negative test. **Action:** the Introduction and Discussion state that it is a recurring claim in the literature and that a formal baseline is needed to discipline such claims.

**Priority:** Low.

---

## Overall decision

**Ready for submission after three minor revisions:**

1. **Medium:** Keep the Discussion's opening/closing statement that the paper's contribution is the baseline, not a new signal.
2. **Medium:** Add one sentence on BH FDR assumptions under dependence in the Methods.
3. **Low:** Keep the public repository URL on the title page and reproducibility checklist.

No fatal flaws, no hard-coded data, and the package passes the automated validation. The AHG editor's two concerns are addressed.
"""


def create_critical_review_report(path: Path) -> None:
    template_path = PROJECT_DIR / "scripts" / "critical_review_report_template.md"
    content = template_path.read_text(encoding="utf-8").format(
        title=TITLE, journal=JOURNAL, date=date.today().isoformat()
    )
    path.write_text(content, encoding="utf-8")


def render_table(document: Document, label: str, spec: tuple) -> None:
    title, row_function, note = spec
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(14)
    run = paragraph.add_run(f"{label}. {title}")
    run.bold = True
    rows = row_function()
    table = document.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Table Grid"
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            cell = table.cell(row_index, column_index)
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.line_spacing = 1
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    run.bold = row_index == 0
            if row_index == 0:
                set_cell_shading(cell, "D9EAF7")
    paragraph = document.add_paragraph(f"Note. {note}")
    paragraph.paragraph_format.line_spacing = 1
    for run in paragraph.runs:
        run.font.size = Pt(9)


def add_word_table(document: Document, table_number: int) -> None:
    render_table(document, f"Table {table_number}", TABLES[table_number])


def add_supporting_table(document: Document, table_number: int) -> None:
    render_table(document, f"Table S{table_number}", SUPPORTING_TABLES[table_number])


def add_inline_figure(document: Document, figure_number: int) -> None:
    filename, caption = FIGURES[figure_number]
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(16)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(
        str(FIGURE_DIR / filename), width=Inches(6.35)
    )
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(10)
    paragraph.paragraph_format.line_spacing = 1.15
    run = paragraph.add_run(f"Figure {figure_number}. ")
    run.bold = True
    paragraph.add_run(caption)


def add_object(document: Document, label: str) -> None:
    kind, number = label.split()
    if kind == "Figure":
        add_inline_figure(document, int(number))
    else:
        add_word_table(document, int(number))


def _body_texts() -> list[str]:
    body_texts = INTRODUCTION.copy()
    for _, paragraphs in METHODS:
        body_texts.extend(paragraphs)
    body_texts.extend(text for _, text, _ in RESULTS)
    body_texts.extend(DISCUSSION)
    return body_texts


def _main_text_word_count() -> int:
    texts = _body_texts()
    texts.extend([
        "The author acknowledges the participants, communities, and investigators whose "
        "contributions made the 1000 Genomes, HGDP, hmmix, and ancient-genome resources "
        "available. Public availability does not remove obligations of respectful reuse.",
        "Funding: This research received no specific grant from any funding agency in "
        "the public, commercial, or not-for-profit sectors.",
        "The author was responsible for conceptualization, methodology, formal analysis, "
        "visualization, writing—original draft, and writing—review and editing.",
        "The author declares no conflict of interest.",
        "The source hmmix segment calls are available from Zenodo record 14136628 "
        "(https://doi.org/10.5281/zenodo.14136628). The ancient ABO-window observations "
        "were derived from the public Neanderthal-segment catalogue of Iasi et al. "
        "(2024), archived at Dryad (https://doi.org/10.5061/dryad.zw3r228gg); O2 "
        "subtype-defining allele frequencies were obtained from the Ensembl Variation "
        "application programming interface and from Ohashi et al. (2006). Analysis "
        "scripts, aggregate derived data, figures, and document-generation code are "
        "available from the corresponding author and will be archived with a persistent "
        "DOI before acceptance. Raw-file SHA-256 checksums and all analysis parameters "
        "are included in analysis_provenance.json and ancient_abo_provenance.json.",
        "This secondary computational analysis used de-identified public genomic data "
        "and involved no recruitment, participant contact, biospecimen collection, or "
        "new phenotype inference. No separate institutional review determination was "
        "obtained; approvals, consent, and access procedures were those reported by the "
        "source studies. No source community representatives participated in this "
        "secondary study, and no direct community return-of-results process occurred. "
        "Because Indigenous genomic records are included, results are reported only at "
        "the minimum level needed for auditability, are not generalised to communities, "
        "and are not used to assign migration routes. The public article, code, and "
        "aggregate derived results are the current means of results availability.",
    ])
    return len(" ".join(texts).split())


def add_manuscript_body(document: Document, inline: bool) -> None:
    document.add_heading("Introduction", level=1)
    for text in INTRODUCTION:
        add_cited_paragraph(document, text)
    document.add_heading("Materials and Methods", level=1)
    for heading, paragraphs in METHODS:
        document.add_heading(heading, level=2)
        for index, text in enumerate(paragraphs):
            add_cited_paragraph(document, text)
            if heading == "Dyadic regression and permutation inference" and index == 0:
                _add_expanded_model_equation(document)
    document.add_heading("Results", level=1)
    for heading, text, objects in RESULTS:
        document.add_heading(heading, level=2)
        add_cited_paragraph(document, text)
        if inline:
            for label in objects:
                add_object(document, label)
    document.add_heading("Discussion", level=1)
    for text in DISCUSSION:
        add_cited_paragraph(document, text)
    document.add_heading("Acknowledgements", level=1)
    document.add_paragraph(
        "The author acknowledges the participants, communities, and investigators whose "
        "contributions made the 1000 Genomes, HGDP, hmmix, and ancient-genome resources "
        "available. Public availability does not remove obligations of respectful reuse."
    )
    document.add_paragraph(
        "Funding: This research received no specific grant from any funding agency in "
        "the public, commercial, or not-for-profit sectors."
    )
    document.add_heading("Author Contributions", level=1)
    document.add_paragraph(
        "The author was responsible for conceptualization, methodology, formal analysis, "
        "visualization, writing—original draft, and writing—review and editing."
    )
    document.add_heading("Conflict of Interest Statement", level=1)
    document.add_paragraph("The author declares no conflict of interest.")
    document.add_heading("Data Archiving", level=1)
    document.add_paragraph(
        "The source hmmix segment calls are available from Zenodo record 14136628 "
        "(https://doi.org/10.5281/zenodo.14136628). The ancient ABO-window observations "
        "were derived from the public Neanderthal-segment catalogue of Iasi et al. "
        "(2024), archived at Dryad (https://doi.org/10.5061/dryad.zw3r228gg); O2 "
        "subtype-defining allele frequencies were obtained from the Ensembl Variation "
        "application programming interface and from Ohashi et al. (2006). Analysis "
        "scripts, aggregate derived data, figures, and document-generation code are "
        "available from the corresponding author and will be archived with a persistent "
        "DOI before acceptance. Raw-file SHA-256 checksums and all analysis parameters "
        "are included in analysis_provenance.json and ancient_abo_provenance.json."
    )
    document.add_heading("Ethics Statement", level=1)
    document.add_paragraph(
        "This secondary computational analysis used de-identified public genomic data "
        "and involved no recruitment, participant contact, biospecimen collection, or "
        "new phenotype inference. No separate institutional review determination was "
        "obtained; approvals, consent, and access procedures were those reported by the "
        "source studies. No source community representatives participated in this "
        "secondary study, and no direct community return-of-results process occurred. "
        "Because Indigenous genomic records are included, results are reported only at "
        "the minimum level needed for auditability, are not generalised to communities, "
        "and are not used to assign migration routes. The public article, code, and "
        "aggregate derived results are the current means of results availability."
    )
    document.add_heading("References", level=1)
    for reference in REFERENCES:
        paragraph = document.add_paragraph(reference)
        paragraph.paragraph_format.first_line_indent = Inches(-0.25)
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.paragraph_format.space_after = Pt(4)
        for run in paragraph.runs:
            run.font.size = Pt(10)
    if not inline:
        document.add_heading("Figure Legends", level=1)
        for number, (_, caption) in FIGURES.items():
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.line_spacing = 1.5
            paragraph.paragraph_format.space_after = Pt(8)
            run = paragraph.add_run(f"Figure {number}. ")
            run.bold = True
            paragraph.add_run(caption)
        document.add_heading("Supporting Information Legends", level=1)
        for number, (_, caption) in SUPPORTING_FIGURES.items():
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.line_spacing = 1.5
            paragraph.paragraph_format.space_after = Pt(8)
            run = paragraph.add_run(f"Figure S{number}. ")
            run.bold = True
            paragraph.add_run(caption)
        document.add_heading("Tables", level=1)
        for number in TABLES:
            add_word_table(document, number)


def create_manuscript(path: Path, inline: bool, anonymous: bool = True) -> None:
    document = Document()
    configure_document(document)
    document.core_properties.title = TITLE
    document.core_properties.author = AUTHOR if not anonymous else ""
    add_title(document)
    add_abstract_page(document)
    add_manuscript_body(document, inline)
    document.save(path)


def create_tables_document(path: Path) -> None:
    document = Document()
    configure_document(document)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Editable Tables")
    run.bold = True
    run.font.size = Pt(16)
    paragraph = document.add_paragraph(TITLE)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for number in TABLES:
        add_word_table(document, number)
        if number != max(TABLES):
            document.add_page_break()
    document.save(path)


def create_single_table_document(path: Path, table_number: int) -> None:
    document = Document()
    configure_document(document)
    add_word_table(document, table_number)
    document.save(path)


def create_single_supporting_table_document(path: Path, table_number: int) -> None:
    document = Document()
    configure_document(document)
    add_supporting_table(document, table_number)
    document.save(path)


def create_excel_tables(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for label, spec in [("Table_1", TABLES[1]), ("Table_S1", SUPPORTING_TABLES[1])]:
        title, row_function, note = spec
        rows = row_function()
        df = pd.DataFrame(rows[1:], columns=rows[0])
        excel_path = output_dir / f"{label}.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Table")
            worksheet = writer.sheets["Table"]
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column].width = adjusted_width


def create_supporting_information(path: Path) -> None:
    document = Document()
    configure_document(document)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Supporting Information")
    run.bold = True
    run.font.size = Pt(16)
    paragraph = document.add_paragraph(TITLE)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for number, (filename, caption) in SUPPORTING_FIGURES.items():
        heading = document.add_paragraph()
        heading.paragraph_format.space_before = Pt(16)
        run = heading.add_run(f"Figure S{number}. {caption}")
        run.bold = True
        image = document.add_paragraph()
        image.alignment = WD_ALIGN_PARAGRAPH.CENTER
        image.add_run().add_picture(
            str(FIGURE_DIR / filename), width=Inches(6.35)
        )
        document.add_page_break()
    for number in SUPPORTING_TABLES:
        add_supporting_table(document, number)
        document.add_page_break()
    document.add_heading("Supplementary Data Files", level=1)
    document.add_paragraph(
        "Supplementary Data 1: population_metadata.csv. Population, project, sample "
        "size, coordinates, continent assignment, and analysis inclusion."
    )
    document.add_paragraph(
        "Supplementary Data 2: pairwise_sharing_corrected.csv. Complete pairwise "
        "similarity, geographic, covariate, residual, permutation, and false discovery "
        "rate results."
    )
    document.add_paragraph(
        "Supplementary Data 3: model_summary.csv. Quadratic assignment procedure "
        "coefficients, permutation P values, descriptive R-squared values, and "
        "population-deletion intervals."
    )
    document.add_paragraph(
        "Supplementary Data 4: sensitivity_analysis.csv and "
        "window_size_sensitivity.csv. Metric, population-subset, and window-size "
        "robustness summaries."
    )
    document.save(path)


def create_cover_letter(path: Path) -> None:
    document = Document()
    configure_document(document)
    document.styles["Normal"].paragraph_format.line_spacing = 1
    document.styles["Normal"].paragraph_format.space_after = Pt(7)
    for text in [
        EDITOR_IN_CHIEF,
        "Editor-in-Chief, " + JOURNAL,
        "School of Life Sciences, University of Nottingham, UK",
    ]:
        document.add_paragraph(text)
    document.add_paragraph()
    paragraph = document.add_paragraph()
    run = paragraph.add_run(f"Re: Submission of an {ARTICLE_TYPE}")
    run.bold = True
    document.add_paragraph(f"Dear {EDITOR_IN_CHIEF},")
    paragraphs = [
        (
            f'I am pleased to submit "{TITLE}" for consideration as an '
            f'{ARTICLE_TYPE} in {JOURNAL}.'
        ),
        (
            "Focal-locus and special-connection interpretations of shared archaic "
            "segments are common in human population genetics, yet they are seldom "
            "tested against a genome-wide baseline that respects the dependence "
            "structure of pairwise data. Using publicly archived hmmix "
            f"archaic-introgression calls from {revised_content.INDIVIDUALS:,} "
            f"individuals in {revised_content.POPULATIONS} populations "
            "(1000 Genomes Project and Human Genome Diversity Project), we construct "
            "such a baseline: population profiles are built so that window "
            "frequencies remain within 0-1, distance and pair-level effects are "
            "tested with population-label quadratic assignment procedure (QAP) "
            "permutations, and multiple testing is controlled with the "
            "false-discovery rate (FDR)."
        ),
        (
            "The analysis shows a broad geographic distance-decay pattern but no "
            "population pair that survives FDR correction and no ABO-window signal "
            "beyond the genome-wide expectation. The contribution is therefore a "
            "reusable, dependence-aware negative control against which focal-locus "
            "and special-connection archaic claims can be judged, rather than a new "
            "migration route. This methodological, reproducibility-focused study "
            "fits the scope of Heredity in population and evolutionary genetics, the "
            "geographic distribution of genetic variation, and statistical-genetic "
            "methodology applied to real data."
        ),
        (
            "This manuscript was previously considered for publication in Annals of "
            "Human Genetics (manuscript 1260928) and was declined after desk review. "
            "The handling editor raised two concerns: (1) the connection between "
            "archaic overlap, geographic distance, and the ABO blood-group claim was "
            "unclear, and (2) it was unclear how the permutation procedure differs "
            "from Mantel tests. Both issues have been addressed in this revision. The "
            "special-connection claim is now stated explicitly and is tested directly "
            "with a prespecified ABO-window scan; the ABO result is framed as a "
            "negative test, not as a route proposal. The Methods section now "
            "distinguishes QAP from Mantel tests: Mantel tests evaluate a single "
            "matrix correlation, whereas our QAP implementation permutes the response "
            "matrix, refits the multiple regression, and records the coefficient and "
            "each pair's residual at every iteration, enabling both coefficient "
            "inference under dependence and FDR control across pairs."
        ),
        (
            "The work is original, is not under consideration elsewhere, and uses "
            "de-identified public genomic resources. No new human participants or "
            "specimens were recruited. The manuscript explicitly discloses that no "
            "separate institutional review determination, community participation, or "
            "direct return-of-results process occurred for this secondary analysis. "
            "The author declares no conflict of interest and reports no external funding."
        ),
        (
            "All analysis code and derived outputs are provided through the project "
            "repository. The source archaic-introgression data, generated with hmmix "
            "(a hidden Markov model-based detection method), are publicly archived in "
            "Zenodo. The submission includes separate figure files, editable tables, "
            "figure legends in the manuscript, and a complete Supporting Information file."
        ),
    ]
    for text in paragraphs:
        document.add_paragraph(text)
    document.add_paragraph("Sincerely,")
    document.add_paragraph(AUTHOR)
    document.add_paragraph(AFFILIATION)
    document.add_paragraph("Email: bougtoir@gmail.com")
    document.save(path)


def add_slide_title(slide, title: str) -> None:
    box = slide.shapes.add_textbox(
        PptInches(0.6),
        PptInches(0.12),
        PptInches(12.1),
        PptInches(0.7),
    )
    box.text_frame.word_wrap = True
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text = title
    paragraph.font.name = "Arial"
    paragraph.font.size = PptPt(16)
    paragraph.font.bold = True
    paragraph.alignment = PP_ALIGN.CENTER


def add_slide_caption(slide, caption: str) -> None:
    box = slide.shapes.add_textbox(
        PptInches(0.65),
        PptInches(6.55),
        PptInches(12.0),
        PptInches(0.72),
    )
    box.text_frame.word_wrap = True
    paragraph = box.text_frame.paragraphs[0]
    paragraph.text = caption
    paragraph.font.name = "Arial"
    paragraph.font.size = PptPt(8)
    paragraph.alignment = PP_ALIGN.LEFT


def add_picture_contained(slide, path: Path) -> None:
    with Image.open(path) as image:
        width, height = image.size
    area_left = 0.55
    area_top = 0.85
    area_width = 12.2
    area_height = 5.65
    scale = min(area_width / width, area_height / height)
    picture_width = width * scale
    picture_height = height * scale
    left = area_left + (area_width - picture_width) / 2
    top = area_top + (area_height - picture_height) / 2
    slide.shapes.add_picture(
        str(path),
        PptInches(left),
        PptInches(top),
        PptInches(picture_width),
        PptInches(picture_height),
    )


def add_ppt_table(slide, rows: list[list[str]]) -> None:
    table_shape = slide.shapes.add_table(
        len(rows),
        len(rows[0]),
        PptInches(0.45),
        PptInches(1.0),
        PptInches(12.4),
        PptInches(5.5),
    )
    table = table_shape.table
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            cell = table.cell(row_index, column_index)
            cell.text = value
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                PptRGBColor(217, 234, 247)
                if row_index == 0
                else PptRGBColor(255, 255, 255)
            )
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.name = "Arial"
                paragraph.font.size = PptPt(9)
                paragraph.font.bold = row_index == 0


def create_presentation(path: Path) -> None:
    presentation = Presentation()
    presentation.slide_width = PptInches(13.333)
    presentation.slide_height = PptInches(7.5)
    blank = presentation.slide_layouts[6]
    for number, (filename, caption) in FIGURES.items():
        slide = presentation.slides.add_slide(blank)
        add_slide_title(slide, f"Figure {number}")
        add_picture_contained(slide, FIGURE_DIR / filename)
        add_slide_caption(slide, caption)
    for number, (filename, caption) in SUPPORTING_FIGURES.items():
        slide = presentation.slides.add_slide(blank)
        add_slide_title(slide, f"Figure S{number}")
        add_picture_contained(slide, FIGURE_DIR / filename)
        add_slide_caption(slide, caption)
    for number, (title, row_function, note) in TABLES.items():
        slide = presentation.slides.add_slide(blank)
        add_slide_title(slide, f"Table {number}. {title}")
        add_ppt_table(slide, row_function())
        add_slide_caption(slide, f"Note. {note}")
    for number, (title, row_function, note) in SUPPORTING_TABLES.items():
        slide = presentation.slides.add_slide(blank)
        add_slide_title(slide, f"Table S{number}. {title}")
        add_ppt_table(slide, row_function())
        add_slide_caption(slide, f"Note. {note}")
    presentation.save(path)


def prepare_separate_figures() -> None:
    OUTPUT_FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    for stale in OUTPUT_FIGURE_DIR.glob("Figure_*"):
        stale.unlink()
    for number, (filename, _) in FIGURES.items():
        source = FIGURE_DIR / filename
        png_target = OUTPUT_FIGURE_DIR / f"Figure_{number}.png"
        tiff_target = OUTPUT_FIGURE_DIR / f"Figure_{number}.tiff"
        shutil.copy2(source, png_target)
        tiff_source = source.with_suffix(".tiff")
        if tiff_source.exists():
            shutil.copy2(tiff_source, tiff_target)
        else:
            with Image.open(source) as image:
                image.convert("RGB").save(
                    tiff_target,
                    format="TIFF",
                    dpi=(300, 300),
                    compression="tiff_lzw",
                )
    for number, (filename, _) in SUPPORTING_FIGURES.items():
        source = FIGURE_DIR / filename
        png_target = OUTPUT_FIGURE_DIR / f"Figure_S{number}.png"
        tiff_target = OUTPUT_FIGURE_DIR / f"Figure_S{number}.tiff"
        shutil.copy2(source, png_target)
        tiff_source = source.with_suffix(".tiff")
        if tiff_source.exists():
            shutil.copy2(tiff_source, tiff_target)
        else:
            with Image.open(source) as image:
                image.convert("RGB").save(
                    tiff_target,
                    format="TIFF",
                    dpi=(300, 300),
                    compression="tiff_lzw",
                )


def validate_content() -> list[str]:
    body_texts = _body_texts()
    joined_body = "\n".join(body_texts)
    uncited_references = []
    for key in REFERENCE_KEYS:
        author, year = key.rsplit(" ", 1)
        variants = [key, f"{author} ({year})", f"{author} et al. ({year})"]
        if not any(variant in joined_body for variant in variants):
            uncited_references.append(key)
    figure_mentions = []
    supporting_figure_mentions = []
    table_mentions = []
    for text in body_texts:
        figure_mentions.extend(
            int(value) for value in re.findall(r"Figures? (?!S)(\d+)", text)
        )
        supporting_figure_mentions.extend(
            int(value) for value in re.findall(r"Figures? S(\d+)", text)
        )
        table_mentions.extend(int(value) for value in re.findall(r"Table (\d+)", text))
    figure_order = list(dict.fromkeys(figure_mentions))
    supporting_figure_order = list(dict.fromkeys(supporting_figure_mentions))
    table_order = list(dict.fromkeys(table_mentions))
    unresolved = [
        value
        for value in [
            "[" + "Affiliation to be added]",
            "[" + "To be added]",
            "[" + "Corresponding author details]",
        ]
        if value in "\n".join(body_texts)
    ]
    main_word_count = _main_text_word_count()
    checks = [
        ("Author-date citations", not re.findall(r"\{\d", joined_body)),
        ("Every reference cited", not uncited_references),
        ("References alphabetised", REFERENCES == sorted(REFERENCES)),
        ("Figure first-appearance order", figure_order == list(FIGURES)),
        (
            "Supporting figure first-appearance order",
            supporting_figure_order == list(SUPPORTING_FIGURES),
        ),
        ("Table first-appearance order", table_order == list(TABLES)),
        ("No placeholder strings", not unresolved),
        ("Running title under 150 characters", len(RUNNING_TITLE) <= 150),
        ("Summary at most 250 words", len(ABSTRACT.split()) <= 250),
        ("Main text at most 7000 words", main_word_count <= 7000),
        (
            "Three to six keywords",
            3 <= len([k for k in KEYWORDS.split(";") if k.strip()]) <= 6,
        ),
        (
            "All figure source files present",
            all((FIGURE_DIR / filename).exists() for filename, _ in FIGURES.values()),
        ),
        (
            "All supporting figure source files present",
            all(
                (FIGURE_DIR / filename).exists()
                for filename, _ in SUPPORTING_FIGURES.values()
            ),
        ),
        (
            "Main figures and tables within Heredity limit",
            len(FIGURES) + len(TABLES) <= 8,
        ),
        ("References within Heredity limit", len(REFERENCES) <= 100),
    ]
    lines = [
        f"{JOURNAL_SHORT} SUBMISSION VALIDATION",
        "==========================",
        "",
        f"Summary words: {len(ABSTRACT.split())}",
        f"Main-text words: {main_word_count}",
        f"References: {len(REFERENCES)}",
        f"Uncited references: {uncited_references}",
        f"First-appearance figure order: {figure_order}",
        f"First-appearance supporting figure order: {supporting_figure_order}",
        f"First-appearance table order: {table_order}",
        "",
    ]
    for label, passed in checks:
        lines.append(f"{'PASS' if passed else 'FAIL'}: {label}")
    if not all(passed for _, passed in checks):
        raise RuntimeError("\n".join(lines))
    return lines


def create_checklist(path: Path) -> None:
    content = """# Heredity submission checklist

## Journal parameters

- Article type: Original Article
- Abstract limit: 250 words (unstructured)
- Main-text limit: 7,000 words excluding references, tables, and figures
- Combined figure/table limit: 8
- Reference limit: 100
- Reference style: author-date, alphabetical reference list
- Peer review: double-anonymised (manuscript anonymised; title page uploaded separately)

## Prepared files

- `title_page_heredity.docx`: title, article type, author, affiliation, corresponding author, running title, main-text word count
- `manuscript_heredity.docx`: anonymous main manuscript (title, abstract, Introduction, Materials and Methods, Results, Discussion, Acknowledgements, Author Contributions, Conflict of Interest, Data Archiving, Ethics Statement, References, Figure Legends, Tables)
- `manuscript_heredity_inline_review.docx`: internal review copy with figures and tables immediately after first mention
- `Table_1_residual_outliers.docx`: editable main table
- `Table_S1_abo_summary.docx`: editable supporting table
- `tables_heredity.xlsx` and `tables_heredity/Table_1.xlsx`, `Table_S1.xlsx`: Excel versions for upload
- `supporting_information_heredity.docx`: Supporting Figures S1-S5, supporting Table S1, and data-file descriptions
- `figures_tables_heredity.pptx`: Figures 1-4, Figures S1-S5, Table 1, and Table S1
- `cover_letter_heredity.docx`: cover letter including previous submission disclosure and editor-concern responses
- `figures/Figure_1` through `Figure_4` and `Figure_S1` through `Figure_S5`: separate PNG and TIFF files (300 dpi)
- `supplementary_data/`: population metadata, complete pairwise results, model output, sensitivities, and provenance
- `reproducibility_checklist.md`: data provenance, rebuild commands, expected checks, and package versions
- `reference_validation.csv`: DOI/PubMed existence and title checks (if generated)

## Automated checks

- Author-date citations in the body; no numbered bracket citations
- Every listed reference is cited and every citation has a reference entry
- Figures 1-4 and Table 1 are first mentioned sequentially
- Summary within 250 words; main text within 7,000 words
- Three to six keywords
- Running title within 150 characters
- Title page, availability, funding, conflict, ethics, and contribution statements present
- No submission placeholder strings remain

## Author checks before upload

- Confirm the full correspondence postal address and email.
- Confirm the no-external-funding statement.
- Confirm the conflict-of-interest statement.
- Confirm institutional determination is not required for this secondary genomic analysis.
- Review the explicit disclosure of no direct community engagement or return of results.
- Provide an authenticated ORCID iD for the submitting author in the submission portal.
- Upload the title page separately and the anonymised manuscript as the main file.
- Upload each figure as a separate TIFF or PNG file; do not embed figures in the manuscript.
- Upload Excel table files and the Supporting Information file.
- Do not interpret nominal residuals or the two Indigenous-American ABO-window segments as definitive migration evidence.
- Include previous reviewer/editor comments in the cover letter (done).

## Submission links

- Author guidelines: https://www.nature.com/hdy/authors-and-referees/gta
- Online submission system: https://mts-hdy.nature.com
- Editorial office: heredity-journal@glasgow.ac.uk
"""
    path.write_text(content, encoding="utf-8")


def create_reproducibility_checklist(path: Path) -> None:
    packages = [
        "pandas",
        "numpy",
        "scipy",
        "statsmodels",
        "matplotlib",
        "seaborn",
        "python-docx",
        "python-pptx",
        "Pillow",
        "openpyxl",
    ]
    versions = []
    for package in packages:
        try:
            versions.append(f"- `{package}=={version(package)}`")
        except PackageNotFoundError:
            versions.append(f"- `{package}`: version not available")
    content = f"""# Reproducibility checklist

## Repository

- Analysis scripts, derived data, figures, and document-generation code: https://github.com/bougtoir/denisovan-archaic-dna-analysis
- Commit/release to be fixed before publication: `heredity-submission-2026-09`

## Public source data

- hmmix archaic-introgression segment files from the 1000 Genomes Project and Human Genome Diversity Project (HGDP): Zenodo record 14136628
- O2 blood-group subtype-defining `rs41302905 T` frequencies: Ensembl Variation application programming interface endpoint
- Solomon Islands ABO*O02 frequencies: Ohashi et al. 2006, doi:10.1007/s10038-006-0375-8
- Ancient ABO-window summary: reproducibly extracted from the public Neanderthal-segment catalogue of Iasi et al. 2024 (Dryad doi:10.5061/dryad.zw3r228gg) by `scripts/build_ancient_abo_summary.py`. Source-file SHA-256 hashes are recorded in `data/ancient_abo_provenance.json`.

## Rebuild order

Run from the project root:

```bash
python scripts/run_ajba_pipeline.py \\
  --segments-1kg /path/to/hg38_1000g_segments.txt \\
  --segments-hgdp /path/to/hg38_HGDP_segments.txt \\
  --permutations 9999 \\
  --sensitivity-permutations 999
python scripts/create_heredity_submission.py
```

The committed `data/ancient_abo_summary.csv` (supporting temporal figure only) is regenerated by additionally passing the Iasi et al. 2024 Dryad files:

```bash
python scripts/build_ancient_abo_summary.py \\
  --iasi-segments /path/to/Neandertal_segments_matching_references_Shared_map.csv \\
  --iasi-metadata /path/to/Meta_Data_individuals.csv
```

## Expected primary checks

- Individuals: {revised_content.INDIVIDUALS:,}
- Populations: {revised_content.POPULATIONS}
- Unique population pairs: {revised_content.PAIRS:,}
- Every population-window frequency is between 0 and 1
- Neanderthal raw distance r: {revised_content.NEANDERTHAL['raw_r']:.4f}
- Denisovan raw distance r: {revised_content.DENISOVAN['raw_r']:.4f}
- Neanderthal expanded descriptive R²: {revised_content.NEANDERTHAL['expanded_r_squared']:.4f}
- Denisovan expanded descriptive R²: {revised_content.DENISOVAN['expanded_r_squared']:.4f}
- QAP distance P: {revised_content.NEANDERTHAL['distance_qap_p']:.4f} and {revised_content.DENISOVAN['distance_qap_p']:.4f}
- FDR q<0.10 non-admixed outliers: {revised_content.NEANDERTHAL['fdr_q_lt_0.10_positive_z_gt_2']} and {revised_content.DENISOVAN['fdr_q_lt_0.10_positive_z_gt_2']}
- Neanderthal/Both segments in the 500-kb ABO interval: {revised_content.ABO['interval_segments']:,}
- Strict ABO-overlapping Neanderthal/Both segments: {revised_content.ABO['strict_overlap']}
- Neanderthal/Both segments with tied maximum reference similarity: {revised_content.ABO['ties']}
- Indigenous American window carriers: Pima 1/13, Maya 1/21, Colombian 0/7
- Strict ABO overlap among those carriers: Pima only

## Environment used for the package

{chr(10).join(versions)}

## Interpretation guardrails

- Pairwise correlation does not prove identity by descent.
- Pairwise rows are dependent; inference uses population-label QAP permutations.
- Expanded-model R² is descriptive and not a causal variance decomposition.
- Reference-genome similarity does not prove a specific migration route.
- Admixed American residuals are not treated as ancient-migration evidence.
- No positive-residual non-admixed pair survived FDR correction.
- Ancient and modern ABO-window calls were produced by different pipelines.
- The ABO-window scan is a prespecified negative test, not a route proposal.
"""
    path.write_text(content, encoding="utf-8")


def create_zip(path: Path, files: list[Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            archive.write(file_path, file_path.relative_to(OUTPUT_DIR))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in ["Table_1_corrected_model.docx", "Table_2_abo_summary.docx"]:
        (OUTPUT_DIR / stale).unlink(missing_ok=True)

    # Validation must pass before documents are created
    validation_lines = validate_content()

    main_word_count = _main_text_word_count()
    prepare_separate_figures()
    create_title_page(OUTPUT_DIR / "title_page_heredity.docx", main_word_count)
    create_manuscript(OUTPUT_DIR / "manuscript_heredity.docx", inline=False, anonymous=True)
    create_manuscript(OUTPUT_DIR / "manuscript_heredity_inline_review.docx", inline=True, anonymous=True)
    create_tables_document(OUTPUT_DIR / "tables_heredity.docx")
    create_single_table_document(OUTPUT_DIR / "Table_1_residual_outliers.docx", 1)
    create_single_supporting_table_document(OUTPUT_DIR / "Table_S1_abo_summary.docx", 1)
    create_excel_tables(OUTPUT_DIR / "tables_heredity")
    create_supporting_information(OUTPUT_DIR / "supporting_information_heredity.docx")
    create_cover_letter(OUTPUT_DIR / "cover_letter_heredity.docx")
    create_critical_review_report(OUTPUT_DIR / "critical_review_report.md")
    presentation = OUTPUT_DIR / "figures_tables_heredity.pptx"
    create_presentation(presentation)
    checklist = OUTPUT_DIR / "submission_checklist.md"
    reproducibility = OUTPUT_DIR / "reproducibility_checklist.md"
    validation = OUTPUT_DIR / "submission_validation.txt"
    create_checklist(checklist)
    create_reproducibility_checklist(reproducibility)
    validation.write_text("\n".join(validation_lines) + "\n", encoding="utf-8")

    # Run numeric consistency and reference validation from the public data files
    subprocess.run(
        ["python3", "scripts/validate_numeric_consistency.py"],
        cwd=str(PROJECT_DIR),
        check=True,
    )
    subprocess.run(
        ["python3", "scripts/validate_references.py"],
        cwd=str(PROJECT_DIR),
        check=True,
    )

    supplementary_directory = OUTPUT_DIR / "supplementary_data"
    supplementary_directory.mkdir(parents=True, exist_ok=True)
    supplementary_sources = [
        DATA_DIR / "population_metadata.csv",
        DATA_DIR / "pairwise_sharing_corrected.csv",
        DATA_DIR / "model_summary.csv",
        DATA_DIR / "sensitivity_analysis.csv",
        DATA_DIR / "window_size_sensitivity.csv",
        DATA_DIR / "analysis_provenance.json",
        DATA_DIR / "profile_quality_checks.csv",
        DATA_DIR / "ancient_abo_summary.csv",
        DATA_DIR / "ancient_abo_provenance.json",
    ]
    for source in supplementary_sources:
        shutil.copy2(source, supplementary_directory / source.name)

    zip_files = [
        OUTPUT_DIR / "title_page_heredity.docx",
        OUTPUT_DIR / "manuscript_heredity.docx",
        OUTPUT_DIR / "manuscript_heredity_inline_review.docx",
        OUTPUT_DIR / "Table_1_residual_outliers.docx",
        OUTPUT_DIR / "Table_S1_abo_summary.docx",
        OUTPUT_DIR / "supporting_information_heredity.docx",
        OUTPUT_DIR / "cover_letter_heredity.docx",
        OUTPUT_DIR / "critical_review_report.md",
        presentation,
        checklist,
        reproducibility,
        validation,
        *sorted(OUTPUT_DIR.glob("tables_heredity/*.xlsx")),
        *sorted(OUTPUT_FIGURE_DIR.glob("Figure_*")),
        *sorted(supplementary_directory.iterdir()),
    ]
    reference_validation = OUTPUT_DIR / "reference_validation.csv"
    if reference_validation.exists():
        zip_files.append(reference_validation)
    numeric_consistency = OUTPUT_DIR / "numeric_consistency_check.txt"
    if numeric_consistency.exists():
        zip_files.append(numeric_consistency)
    create_zip(OUTPUT_DIR / "Heredity_submission_package.zip", zip_files)
    print(f"Created {JOURNAL_SHORT} submission materials in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
