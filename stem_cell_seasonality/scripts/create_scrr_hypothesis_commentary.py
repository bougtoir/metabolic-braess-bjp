#!/usr/bin/env python3
"""
Generate Stem Cell Reviews and Reports (SCRR) Hypothesis and Commentary manuscript.

Target: Stem Cell Reviews and Reports (Springer Nature)
Form: Hypothesis and Commentary
Length: 3,000-5,000 words

Narrative shift from STEM CELLS reject:
- Central thesis: clonality reduces genetic variance but does not eliminate environmental variance
- GEO seasonality analysis is moved to a brief cautionary example, not a proof
- IoT statistical roadmap is added
- GMP vs research-lab gap is organized explicitly
"""

import re
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# Reference database (Vancouver, first-appearance order)
# ──────────────────────────────────────────────
REFERENCES = [
    # 1
    "Kirkeby A, Main H, Carpenter M. Pluripotent stem-cell-derived therapies in "
    "clinical trial: a 2025 update. Cell Stem Cell. 2025;32(1):10-37.",
    # 2
    "Yamanaka S. Pluripotent stem cell-based cell therapy-promise and challenges. "
    "Cell Stem Cell. 2020;27(4):523-531.",
    # 3
    "Volpato V, Smith J, Sandor C, et al. Reproducibility of molecular phenotypes "
    "after long-term differentiation to human iPSC-derived neurons: a multi-site "
    "omics study. Stem Cell Reports. 2018;11(4):897-911.",
    # 4
    "Volpato V, Webber C. Addressing variability in iPSC-derived models of human "
    "disease: guidelines to promote reproducibility. Dis Model Mech. "
    "2020;13(1):dmm042317.",
    # 5
    "Ortmann D, Vallier L. Variability of human pluripotent stem cell lines. Curr "
    "Opin Genet Dev. 2017;46:179-185.",
    # 6
    "Panina Y, Yamane J, Kobayashi K, Sone H, Fujibuchi W. Human ES and iPS cells "
    "display less drug resistance than differentiated cells, and naive-state "
    "induction further decreases drug resistance. J Toxicol Sci. 2021;46(3):131-142.",
    # 7
    "McCreery KP, Stubb A, Stephens R, et al. Mechano-osmotic signals control "
    "chromatin state and fate transitions in pluripotent stem cells. Nat Cell Biol. "
    "2025;27(10):1757-1770.",
    # 8
    "Chui JS-H, Izuel-Idoype T, Qualizza A, et al. Osmolar modulation drives "
    "reversible cell cycle exit and human pluripotent cell differentiation via "
    "NF-kappaB and WNT signaling. Adv Sci. 2024;11(7):2307554.",
    # 9
    "Sato S, Hishida T, Kinouchi K, et al. The circadian clock CRY1 regulates "
    "pluripotent stem cell identity and somatic cell reprogramming. Cell Rep. "
    "2023;42(6):112590.",
    # 10
    "Ameneiro C, Moreira T, Fuentes-Iglesias A, et al. BMAL1 coordinates energy "
    "metabolism and differentiation of pluripotent stem cells. Life Sci Alliance. "
    "2020;3(5):e201900534.",
    # 11
    "Bi S, Tang J, Zhang L, et al. Fine particulate matter reduces the pluripotency "
    "and proliferation of human embryonic stem cells through ROS induced AKT and ERK "
    "signaling pathway. Reprod Toxicol. 2020;96:231-240.",
    # 12
    "Cai J, Zhou L, Liu L, et al. Real-time monitoring reveals the effects of low "
    "concentrations of volatile organic compounds in the embryology laboratory. Hum "
    "Reprod. 2025;40(4):601-611.",
    # 13
    "Agarwal N, Chattopadhyay R, Ghosh S, et al. Volatile organic compounds and good "
    "laboratory practices in the in vitro fertilization laboratory: the important "
    "parameters for successful outcome in extended culture. J Assist Reprod Genet. "
    "2017;34(8):999-1006.",
    # 14
    "Czyz J, Nikolova T, Schuderer J, et al. Non-thermal effects of power-line "
    "magnetic fields (50 Hz) on gene expression levels of pluripotent embryonic stem "
    "cells. Mutat Res. 2004;557(1):63-74.",
    # 15
    "Diatroptova MA, Kosyreva AM, Diatroptov ME. About 4-day rhythm of proliferative "
    "activity of L-929 cells in culture correlates with the intensity of secondary "
    "cosmic radiation fluctuations. Bull Exp Biol Med. 2022;172(5):561-565.",
    # 16
    "Mizuno M, Endo K, Katano H, et al. The environmental risk assessment of "
    "cell-processing facilities for cell therapy in a Japanese academic institution. "
    "PLoS One. 2020;15(8):e0236600.",
    # 17
    "Klein SG, Steckbauer A, Alsolami SM, et al. Toward best practices for "
    "controlling mammalian cell culture environments. Front Cell Dev Biol. "
    "2022;10:788808.",
    # 18
    "Barrett T, Wilhite SE, Ledoux P, et al. NCBI GEO: archive for functional "
    "genomics data sets-update. Nucleic Acids Res. 2013;41(D):D991-D995.",
]


def add_superscript_refs(paragraph, text):
    """Parse text with {N} or {N-M} or {N,M} markers and create superscript runs."""
    parts = re.split(r'(\{[^}]+\})', text)
    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            run = paragraph.add_run(part[1:-1])
            run.font.superscript = True
            run.font.size = Pt(9)
        else:
            run = paragraph.add_run(part)
            run.font.size = Pt(11)
    return paragraph


def set_paragraph_format(para, space_after=Pt(6), space_before=Pt(0),
                         line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY):
    para.paragraph_format.space_after = space_after
    para.paragraph_format.space_before = space_before
    para.paragraph_format.line_spacing = line_spacing
    para.alignment = alignment
    return para


def add_heading(doc, text, level=1):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)
    return heading


def set_cell_text(cell, text, bold=False, size=Pt(10)):
    cell.paragraphs[0].clear()
    run = cell.paragraphs[0].add_run(text)
    run.font.size = size
    run.font.bold = bold
    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


def create_figure1():
    """Figure 1: Clonality reduces genetic variance, not environmental variance."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), dpi=150)

    # Panel A: distributions
    x = np.linspace(-3, 3, 300)
    genetic = np.exp(-x**2 / 0.3) / np.sqrt(0.3 * np.pi) / 2
    env_narrow = np.exp(-x**2 / 0.8) / np.sqrt(0.8 * np.pi) / 1.5
    env_wide = np.exp(-x**2 / 2.2) / np.sqrt(2.2 * np.pi)

    axes[0].plot(x, genetic, color='#2ca02c', linewidth=2.5, label='Genetic variance (clonal)')
    axes[0].plot(x, env_narrow, color='#d62728', linewidth=2.5, linestyle='--', label='Environmental variance (GMP)')
    axes[0].plot(x, env_wide, color='#ff7f0e', linewidth=2.5, linestyle=':', label='Environmental variance (research lab)')
    axes[0].set_xlabel('Differentiation outcome deviation', fontsize=11)
    axes[0].set_ylabel('Frequency', fontsize=11)
    axes[0].set_title('A  Variance components', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=8, loc='upper right')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Panel B: conceptual landscape
    t = np.linspace(0, 10, 100)
    base = np.sin(t) * 0.5
    env = np.sin(t * 0.7) * 0.8 + 0.3 * np.sin(t * 2.3)
    axes[1].fill_between(t, base - 0.2, base + 0.2, color='#2ca02c', alpha=0.3, label='Genetic range (clonal)')
    axes[1].fill_between(t, env - 0.4, env + 0.4, color='#ff7f0e', alpha=0.25, label='Environmental range (unmonitored)')
    axes[1].plot(t, base, color='#2ca02c', linewidth=2)
    axes[1].plot(t, env, color='#ff7f0e', linewidth=2)
    axes[1].set_xlabel('Time / experimental condition', fontsize=11)
    axes[1].set_ylabel('Differentiation efficiency', fontsize=11)
    axes[1].set_title('B  Clonality does not erase environmental drift', fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=8, loc='lower right')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "SCRR_Figure1_Clonal_Environmental_Variance.png")
    fig.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


def add_iot_table(doc):
    """Table 2: Proposed IoT-enabled statistical roadmap."""
    p = doc.add_paragraph()
    set_paragraph_format(p, space_before=Pt(12), space_after=Pt(6))
    run = p.add_run('Table 2. ')
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run('Proposed IoT-enabled statistical roadmap for environmental profiling of PSC facilities.')
    run.font.size = Pt(10)

    table = doc.add_table(rows=6, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ['Phase', ' Objective', ' Statistical design', ' Deliverable']
    for i, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], h, bold=True)

    data = [
        ['I. Passive monitoring', 'Establish baseline multi-parameter environmental variance', 'Longitudinal mixed-effects models; seasonality decomposition; control-chart anomaly detection', 'Facility-specific variance budget per environmental parameter'],
        ['II. Retrospective crosswalk', 'Identify candidate variables that correlate with historical batch outcomes', 'Time-lagged regression with cross-validation; false-discovery rate control; sensitivity analyses for reagent lot and operator', ' ranked list of candidate variables'],
        ['III. Controlled perturbation', 'Causally test high-priority variables', 'Blocked factorial or crossover designs; mixed models with random laboratory effect; equivalence testing for negative findings', 'Effect-size estimates and 95% confidence intervals'],
        ['IV. Standardization', 'Deploy validated monitoring protocol across sites', 'Multi-center measurement-system analysis; Bland-Altman agreement; generalized linear mixed models for outcomes', 'Standard operating procedure and quality-control thresholds'],
        ['V. Continuous audit', 'Maintain reproducibility over time', 'Automated control charts; change-point detection; periodic audit against reference standards', 'Annual reproducibility report and corrective-action log'],
    ]

    for r_idx, row in enumerate(data, 1):
        for c_idx, val in enumerate(row):
            set_cell_text(table.rows[r_idx].cells[c_idx], val)

    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                set_paragraph_format(paragraph, line_spacing=1.15)


def add_gmp_table(doc):
    """Table 1: Achieved vs unaddressed environmental controls in PSC facilities."""
    p = doc.add_paragraph()
    set_paragraph_format(p, space_before=Pt(12), space_after=Pt(6))
    run = p.add_run('Table 1. ')
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run('Environmental parameters in commercial GMP versus typical academic PSC research laboratories.')
    run.font.size = Pt(10)

    table = doc.add_table(rows=9, cols=3)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ['Parameter', 'Commercial GMP status', 'Academic research lab status']
    for i, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], h, bold=True)

    data = [
        ['Temperature', '37C +/- 0.1C; validated and alarmed', '37C +/- 0.5C; rarely logged continuously'],
        ['CO2', '5% +/- 0.1%; calibrated regularly', '5% setpoint; calibration ad hoc'],
        ['Humidity', 'Actively controlled and monitored', 'Seasonally coupled to outdoor air; rarely logged'],
        ['VOCs', 'Carbon filtration; real-time monitoring in some facilities', 'Typically unmonitored'],
        ['Ambient light', 'Controlled during processing', 'Variable by hood/incubator design'],
        ['ELF-EMF', 'Shielded or characterized during qualification', 'Uncharacterized'],
        ['Barometric pressure', 'Not typically controlled; logged in validated clean rooms', 'Not logged'],
        ['Vibration', 'Isolated or characterized', 'Uncharacterized'],
    ]

    for r_idx, row in enumerate(data, 1):
        for c_idx, val in enumerate(row):
            set_cell_text(table.rows[r_idx].cells[c_idx], val)

    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                set_paragraph_format(paragraph, line_spacing=1.15)


def count_words(doc):
    """Approximate word count from document paragraphs."""
    text = []
    for p in doc.paragraphs:
        text.append(p.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text.append(cell.text)
    full = ' '.join(text)
    return len(full.split())


def create_manuscript():
    doc = Document()

    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Title page
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run("Hypothesis and Commentary")
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 102, 153)

    p = doc.add_paragraph()
    set_paragraph_format(p, space_before=Pt(24), space_after=Pt(12))
    run = p.add_run(
        "The Invisible Variables: Why Clonal Systems Are Not Immune to Environmental Confounding"
    )
    run.bold = True
    run.font.size = Pt(16)

    p = doc.add_paragraph()
    set_paragraph_format(p, space_after=Pt(24))
    run = p.add_run("Tatsuki Onishi")
    run.font.size = Pt(11)
    run2 = p.add_run("1,*")
    run2.font.superscript = True
    run2.font.size = Pt(9)

    p = doc.add_paragraph()
    set_paragraph_format(p, space_after=Pt(3))
    run = p.add_run("1")
    run.font.superscript = True
    run.font.size = Pt(9)
    run2 = p.add_run("[Affiliation to be added]")
    run2.font.size = Pt(10)

    p = doc.add_paragraph()
    run = p.add_run("*Correspondence: bougtoir@gmail.com")
    run.font.size = Pt(10)
    run.italic = True
    set_paragraph_format(p, space_after=Pt(18))

    # Abstract
    add_heading(doc, "Abstract", level=2)
    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Pluripotent stem cell (PSC) differentiation remains variable even when genetically "
        "identical cell lines are used and protocols are nominally standardized. We propose that "
        "the field has fallen into a 'clonal complacency trap': the assumption that eliminating "
        "genetic variance removes the obligation to control environmental variance. Here we argue "
        "that clonality reduces genetic variance but does not eliminate environmental variance, and "
        "that most PSC research laboratories monitor only temperature and CO2 while leaving "
        "humidity, volatile organic compounds (VOCs), ambient light, electromagnetic fields (EMF), "
        "and barometric pressure largely unmonitored. We review evidence that PSCs are "
        "intrinsically sensitive to these variables, summarize the gap between commercial good "
        "manufacturing practice (GMP) facilities and academic research laboratories, and present an "
        "Internet-of-Things (IoT) statistical roadmap for quantifying environmental contributions to "
        "differentiation outcomes. We also explain why retrospective database mining, including an "
        "exploratory analysis of 6,101 NCBI Gene Expression Omnibus (GEO) submission dates, cannot "
        "resolve this question because submission timing is confounded by institutional calendars. "
        "The hypothesis is testable through prospective environmental monitoring paired with "
        "differentiation outcomes, and its verification would improve the reproducibility of both "
        "basic research and clinical-grade PSC manufacturing."
    )

    # Keywords
    p = doc.add_paragraph()
    set_paragraph_format(p, space_before=Pt(12))
    run = p.add_run("Keywords: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run(
        "pluripotent stem cells; clonality; environmental confounding; reproducibility; "
        "IoT monitoring; cell culture"
    )
    run.font.size = Pt(10)

    doc.add_page_break()

    # Section 1: Introduction
    add_heading(doc, "Introduction", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Pluripotent stem cell (PSC)-derived therapies are approaching clinical reality, with "
        "over a hundred active trials and more than a thousand patients treated as of 2024.{1} "
        "Yet differentiation protocols remain notoriously variable across laboratories and even "
        "between batches within a single group.{2-5} The field has invested heavily in controlling "
        "genetic and recipe variables-growth factors, small molecules, extracellular matrices, and "
        "timing-while largely ignoring the physical environment in which these variables are "
        "executed."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "A tacit assumption underlies this neglect: clonal or isogenic systems are, by virtue of "
        "their genetic uniformity, automatically controlled for confounding. If all cells share the "
        "same genome, the argument goes, then residual variation must be either stochastic or "
        "technical-and therefore not amenable to environmental adjustment. We call this the "
        "'clonal complacency trap.' It conflates the removal of genetic variance with the removal "
        "of all systematic variance, and it discourages the stratification, regression, and "
        "sensitivity analyses that observational scientists would consider mandatory. The central "
        "claim of this Commentary is that clonality reduces genetic variance but does not eliminate "
        "environmental variance (Figure 1)."
    )


    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The distinction matters because PSCs are not merely cells with the same DNA. They are "
        "cells in a metabolically active, chromatin-open, rapidly proliferating state whose fate "
        "decisions are gated by small changes in osmolarity, mechanical stress, and signaling "
        "molecules.{6-7} When a cell line is clonal, genetic heterogeneity is minimized. But the "
        "environmental exposure of that clone across days, seasons, and laboratories remains a "
        "random variable, not a constant. Treating it as zero is an assumption, not a fact, and the "
        "evidence is increasingly against it."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Multi-site reproducibility studies provide empirical support for this reframing. "
        "Volpato et al.{3} found that laboratory-of-origin was the dominant source of variance in "
        "iPSC-derived neuron transcriptomes, exceeding the effect of genetic background or "
        "differentiation batch. Current explanations invoke operator technique, reagent lots, and "
        "passage number, but these account for only a fraction of observed variance. We propose "
        "that unmeasured environmental differences between laboratories constitute a missing "
        "explanatory variable-and that the clonal paradigm has delayed its recognition."
    )

    # Section 2: Why PSCs are vulnerable
    add_heading(doc, "Why Pluripotent Stem Cells Are Uniquely Vulnerable", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Five lines of evidence justify the hypothesis that environmental perturbations matter "
        "more for PSCs than for differentiated cells. First, PSCs display markedly greater "
        "chemical sensitivity. Panina et al.{6} showed that human iPS cells are approximately "
        "1.5-fold more sensitive to drug exposure than embryonic stem cells, and both are several-"
        "fold less resistant than non-pluripotent cell types. Naive-state induction further "
        "heightened sensitivity, establishing a gradient: the more undifferentiated the cell, "
        "the more vulnerable it is to environmental perturbation."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Second, osmotic perturbations of small magnitude can gate cell-fate transitions. "
        "McCreery et al.{7} demonstrated that compaction-triggered changes in nuclear shape and "
        "volume in human iPSCs remodel chromatin architecture and prime cells for ectodermal "
        "differentiation. The implication for routine culture is direct: during biosafety cabinet "
        "work, medium evaporates at rates determined by ambient humidity, producing osmolarity "
        "shifts that could cross the thresholds identified in their work. Chui et al.{8} further "
        "showed that hyperosmotic culture drives reversible cell-cycle exit and maturation in "
        "iPSC-derived cells through NF-kappaB and WNT signaling."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Third, PSCs depend on circadian clock components in a non-canonical manner. CRY1 is "
        "upregulated in iPSCs and ESCs compared with somatic cells, and its deletion impairs self-"
        "renewal and disrupts reprogramming.{9} BMAL1 coordinates energy metabolism and "
        "differentiation independently of circadian oscillation, which is suppressed in "
        "pluripotent cells.{10} Because clock molecules are present without a fully buffered "
        "circadian oscillator, PSCs may be unusually sensitive to ambient light cycles leaking "
        "into incubators or biosafety cabinets."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Fourth, airborne pollutants affect PSCs at concentrations that leave somatic cells "
        "unharmed. Fine particulate matter (PM2.5) downregulates pluripotency markers NANOG and "
        "OCT4 in human ESCs through ROS-mediated AKT/ERK signaling.{11} In IVF laboratories, real-"
        "time VOC monitoring revealed that even low concentrations linearly predicted decreased "
        "blastocyst quality, and reducing VOCs increased blastocyst formation by 18% and live "
        "birth rates by 8%.{12-13} Importantly, the effect was specific to fresh embryos; frozen "
        "embryos were unaffected, indicating that early-stage cells are selectively vulnerable."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Fifth, ELF-EMF and other physical variables have documented effects on pluripotent cells. "
        "Czyz et al.{14} showed that 50 Hz power-line magnetic fields alter gene expression in "
        "mouse embryonic stem cells. Cosmic ray flux correlates with four-day rhythms of "
        "proliferative activity in cultured L-929 cells.{15} Barometric pressure fluctuations, "
        "building vibration, and water quality are rarely logged but plausibly modulate the same "
        "mechano-osmotic and pH-dependent pathways that govern PSC fate.{7-8}"
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Together, these findings point to a coherent picture: PSCs sit at an "
        "energetically shallow decision landscape where subtle environmental shifts can tip the "
        "balance between self-renewal and lineage commitment. What remains unknown is the real-world "
        "magnitude of these effects in working laboratories. The question is not whether PSCs can "
        "respond to environmental cues-they clearly can-but which cues matter, by how much, and "
        "whether current laboratories control them."
    )

    # Section 3: GMP gap
    add_heading(doc, "The GMP-Research Laboratory Gap", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Commercial cell-therapy manufacturing and academic research laboratories operate under "
        "different environmental control regimes. Good manufacturing practice (GMP) facilities "
        "validate temperature, CO2, humidity, particulate counts, microbial contamination, and "
        "operator flow, and maintain continuous monitoring records for regulatory audit.{17} This "
        "level of control is why commercial manufacturing has long treated environmental "
        "parameters as critical process variables, implementing dedicated sites, monitored "
        "airflow, temperature loggers, and sensors for metabolic activity of cells."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Academic research laboratories, by contrast, typically control only incubator "
        "temperature and CO2. Humidity is seasonally coupled to outdoor air; VOCs are introduced "
        "by building materials, disinfectants, and HVAC systems; ambient light varies by hood and "
        "incubator design; EMF is uncharacterized; and barometric pressure, vibration, and water "
        "quality are not logged.{16-17} Mizuno et al.{16} found that even in a Japanese academic "
        "cell-processing facility, humidity tracked outdoor seasonal patterns and bacterial or "
        "fungal contamination rates rose significantly above 55% relative humidity. The authors "
        "noted that humidity control equipment 'is expensive and usually not set up in academic "
        "institutions.' Klein et al.{17} similarly concluded that environmental control in "
        "mammalian cell culture is underdeveloped relative to other quality dimensions. "
        "Table 1 summarizes the contrast between commercial GMP and typical academic research "
        "laboratories."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The point is not that GMP facilities are perfect; rather, "
        "the variables they monitor are themselves evidence of which environmental parameters the "
        "field considers important once product quality is at stake. Academic research has not "
        "adopted the same monitoring discipline, not because the variables are irrelevant, but "
        "because there is no regulatory or funding incentive to do so. We argue that the same "
        "logic applies to reproducibility: without measuring environmental exposure, one cannot "
        "attribute variation to the correct source."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Cost-effectiveness arguments should also be reframed. A multi-parameter IoT sensor "
        "package for a standard PSC facility currently costs less than a few thousand dollars and "
        "requires minimal maintenance. By comparison, the cost of an unexplained failed "
        "differentiation batch-in reagents, time, and lost data-can exceed that amount many times "
        "over. When clinical translation is the goal, the cost of undetected environmental "
        "variation includes failed product lots, regulatory delays, and compromised patient safety. "
        "Environmental monitoring is therefore not an optional luxury but a prerequisite for "
        "reproducible stem-cell science."
    )

    # Section 4: IoT roadmap
    add_heading(doc, "An IoT Roadmap for Quantifying Invisible Variables", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "What is missing is not another culture medium or transcription factor, but a systematic "
        "environmental monitoring infrastructure paired with an appropriate statistical "
        "design. Modern Internet-of-Things (IoT) sensors can measure temperature, humidity, "
        "illuminance, VOCs, ELF-EMF, barometric pressure, and vibration at 1-minute resolution for "
        "modest cost. The challenge is not sensor availability but study design: how to separate "
        "environmental signal from batch, operator, reagent lot, and genetic effects."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "We propose a five-phase roadmap (Table 2). Phase I establishes a baseline by deploying "
        "multi-parameter sensors alongside routine differentiation outcomes for at least 12 "
        "months, covering one full seasonal cycle. Longitudinal mixed-effects models decompose "
        "variance into fixed seasonal components and random laboratory or batch effects, while "
        "control-chart methods flag anomalous environmental excursions. Phase II crosswalks these "
        "data with historical batch outcomes, using time-lagged regression and false-discovery-"
        "rate control to identify candidate variables. Phase III tests high-priority variables "
        "causally through blocked factorial or crossover experiments with mixed models and "
        "equivalence testing for negative findings. Phase IV translates validated monitoring into "
        "a multi-center standard operating procedure. Phase V maintains reproducibility through "
        "continuous automated auditing."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The five phases and their statistical requirements are summarized in Table 2. "
        "Several analytical choices are critical. Because differentiation outcomes are "
        "typically proportions or counts (differentiation efficiency, yield, marker purity), "
        "generalized linear mixed models with appropriate link functions are preferable to raw "
        "linear regression. Multiple comparison correction is essential when many environmental "
        "parameters are tested; we recommend false-discovery-rate control at the exploratory "
        "stage and family-wise error control for confirmatory contrasts. Seasonal components "
        "should be modeled with circular or harmonic terms rather than arbitrary month labels. "
        "Cross-validation and holdout laboratories should be used to assess external validity. "
        "Finally, null findings should be reported with equivalence bounds, so that absence of "
        "evidence is not mistaken for evidence of absence."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "In practice, Phase I should be treated as a variance-budgeting exercise rather than a "
        "formal hypothesis test. Its purpose is to estimate the baseline magnitude and "
        "autocorrelation of environmental fluctuations and to rank them by their association with "
        "routine batch outcomes. A pilot can begin with a single incubator or biosafety cabinet, "
        "one multi-parameter sensor, and the differentiation assays already in use. After 12 months, "
        "the variance components from Phase I directly inform the sample size and equivalence bounds "
        "for Phase III. This staged design prevents an underpowered causal experiment and keeps the "
        "initial implementation cost below that of a single failed batch."
    )

    # Section 5: Retrospective evidence and its limits
    add_heading(doc, "Retrospective Evidence and Its Limits", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "A tempting alternative to prospective monitoring is retrospective analysis of public "
        "databases. An exploratory analysis of 6,101 PSC differentiation-related datasets from "
        "NCBI GEO{18} shows why this approach is informative as a methodological caution, not as "
        "biological evidence. The overall dataset showed a March "
        "peak in submission dates. A natural experiment using academic-calendar groups found that "
        "the March signal was concentrated in Japan (n=200), while South Korea (n=50) did not "
        "show a comparable March peak. The larger September-start group peaked in January and "
        "showed no significant seasonality, and the small Southern Hemisphere group did not show "
        "a hemisphere-inverted peak. These mixed patterns show that GEO submission dates cannot "
        "separate institutional and biological seasonality."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "This result illustrates a general limitation: GEO submission dates are a convolution "
        "of experiment timing, analysis duration, manuscript writing, peer review, revision, and "
        "institutional reporting deadlines, with typical lags of 6-18 months from bench to "
        "deposition. Even if PSC differentiation were strongly seasonal, that signal would be "
        "obscured by institutional rhythms. Distinguishing biological seasonality from "
        "institutional artifacts requires either date-stamped experimental metadata (which GEO "
        "rarely provides) or direct prospective measurement. Database mining can therefore "
        "generate hypotheses, but it cannot test them."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Similarly, exploratory correlations between PSC dataset volume and solar activity "
        "indices were entirely explained by shared secular trends: after detrending, the "
        "correlation vanished. Co-trending time series are a well-known source of spurious "
        "associations, and the extreme Northern Hemisphere imbalance of GEO submissions (over "
        "95% of records with country data) precludes meaningful hemisphere-inversion tests. "
        "These findings do not rule out solar or seasonal effects; they simply show that public "
        "metadata are insufficient to detect them."
    )

    # Section 6: Discussion and implications
    add_heading(doc, "Discussion and Implications", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The clonal complacency trap-the equation of genetic uniformity with environmental "
        "invariance-has led the PSC field to neglect a correctable source of irreproducibility. "
        "Clonality reduces genetic variance but does not eliminate environmental variance. PSCs are "
        "biologically primed to respond to "
        "humidity, VOCs, light, EMF, osmotic stress, and barometric pressure; most academic "
        "laboratories do not monitor these variables; and public databases cannot substitute for "
        "direct measurement because their timestamps are confounded by institutional calendars. "
        "The path forward is prospective IoT-enabled environmental monitoring paired with a "
        "rigorous mixed-effects statistical framework."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Regulatory frameworks for advanced therapy medicinal products are increasingly "
        "emphasizing Quality by Design and process analytical technology. Environmental monitoring "
        "fits naturally into those frameworks: a control strategy that treats physical variables as "
        "potential critical process parameters, not background noise, would align academic research "
        "with the standards expected in clinical manufacturing and reduce downstream regulatory risk."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The IVF field provides a precedent. When embryology laboratories began monitoring and "
        "filtering air, many saw measurable improvements in outcomes.{12-13} The PSC field is at a "
        "similar inflection point, with the added advantage that modern sensors and cloud data "
        "infrastructure make comprehensive environmental logging far cheaper and more scalable "
        "than two decades ago. We do not claim that uncontrolled environments are the only or "
        "dominant source of PSC variability; rather, we claim that they remain unmeasured, that "
        "measurement is feasible, and that failing to measure them weakens the scientific basis "
        "for comparing protocols, lines, and laboratories. Testing the central hypothesis-that "
        "environmental variance explains a non-trivial fraction of residual PSC differentiation "
        "variability-is both urgent and tractable."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Several caveats are worth stating explicitly. This Commentary does not present new "
        "experimental measurements of PSC cultures under controlled environmental perturbations; "
        "its empirical contribution is a methodological demonstration that public GEO metadata are "
        "too noisy for this question. The proposed IoT roadmap is a design framework, not a "
        "validated protocol, and the optimal sensor suite, sampling frequency, and alert thresholds "
        "will vary by facility. Finally, environmental monitoring can identify associations, but it "
        "cannot, by itself, establish causality; only the factorial and crossover experiments in "
        "Phase III can do that. What the framework offers is a path from anecdotal reproducibility "
        "failures to quantifiable, auditable process control."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "A logical next step is a small consortium of laboratories that run an identical "
        "differentiation assay side-by-side with multi-parameter environmental sensors. "
        "Such a study could, within 12 to 18 months, produce the first facility-to-facility "
        "variance-partition estimates for temperature, humidity, VOCs, and light. Raw sensor logs, "
        "batch metadata, and analysis code should be shared under open licenses so that alert "
        "thresholds can be updated as evidence accumulates. Standardization bodies and funding "
        "agencies could accelerate adoption by defining minimum environmental metadata requirements "
        "for PSC publications. These pilots would also reveal whether existing laboratory quality-"
        "control practices already normalize environmental variation or merely mask it. Even "
        "negative findings would be valuable: a well-powered null result for a particular variable "
        "would tell the field that it can stop worrying about that parameter. Until such pilots are "
        "completed, the safest heuristic is to stop assuming that isogenic cells grown in different "
        "rooms, seasons, or buildings receive the same environmental exposure."
    )

    # Declarations
    add_heading(doc, "Declarations", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Ethics approval and consent to participate: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run("Not applicable. This Commentary does not report primary research involving human participants, human tissue, or animals.")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Consent for publication: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run("Not applicable.")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Availability of data and materials: ")
    run.bold = True
    run.font.size = Pt(10)
    add_superscript_refs(p,
        "All retrospective GEO dataset metadata analyzed in this Commentary were downloaded from "
        "NCBI GEO{18} using the Entrez E-utilities search interface with queries related to iPSC/ESC "
        "differentiation. Processed metadata and reproducibility code are archived in the public "
        "GitHub repository bougtoir/stem-cell-seasonality."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Code availability: ")
    run.bold = True
    run.font.size = Pt(10)
    add_superscript_refs(p,
        "Source code for downloading GEO metadata, performing the seasonal and solar analyses, "
        "generating figures and tables, and building this manuscript is available at "
        "https://github.com/bougtoir/stem-cell-seasonality."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Competing interests: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run("The author declares no competing interests.")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Funding: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run("This work received no specific funding.")
    run.font.size = Pt(10)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Authors' contributions: ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run("T.O. conceived the Commentary, designed the analyses, wrote the manuscript, and approved the final version.")
    run.font.size = Pt(10)

    # References
    add_heading(doc, "References", level=2)
    for i, ref in enumerate(REFERENCES, 1):
        p = doc.add_paragraph()
        set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
        run = p.add_run(f"{i}. {ref}")
        run.font.size = Pt(10)

    # Figure Legends
    doc.add_page_break()
    add_heading(doc, "Figure Legends", level=2)

    fig1_path = create_figure1()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_format(p, space_before=Pt(12), space_after=Pt(6))
    doc.add_picture(fig1_path, width=Inches(6.5))

    p = doc.add_paragraph()
    set_paragraph_format(p, space_before=Pt(6), space_after=Pt(12))
    run = p.add_run("Figure 1. ")
    run.bold = True
    run.font.size = Pt(10)
    run = p.add_run(
        "Conceptual model of the clonal complacency trap. (A) A clonal population has narrow "
        "genetic variance (green) but can still experience wide environmental variance (orange), "
        "especially in research laboratories that do not monitor environmental parameters. "
        "(B) Over time, unmonitored environmental drift can produce outcome variation comparable "
        "to-or larger than-genetic effects, even when all cells are isogenic."
    )
    run.font.size = Pt(10)

    # Tables
    doc.add_page_break()
    add_heading(doc, "Tables", level=2)

    add_gmp_table(doc)
    doc.add_page_break()
    add_iot_table(doc)

    out_path = os.path.join(OUTPUT_DIR, "StemCellReviewsAndReports_HypothesisCommentary_InvisibleVariables.docx")
    doc.save(out_path)
    print(f"Manuscript saved to: {out_path}")
    print(f"Approximate word count (main text + tables): {count_words(doc)}")
    return out_path


if __name__ == "__main__":
    create_manuscript()
