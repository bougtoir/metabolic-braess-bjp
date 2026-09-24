#!/usr/bin/env python3
"""
Generate Stem Cell Reviews and Reports (SCRR) Comment manuscript.

Target: Stem Cell Reviews and Reports (Springer Nature)
Form: Comment
Length: <= 1500 words, 1 figure, <= 5 references, no abstract
"""

import re
import os
import json
import math
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# Reference database (Vancouver, first-appearance order)
# ──────────────────────────────────────────────
REFERENCES = [
    # 1
    "Volpato V, Smith J, Sandor C, et al. Reproducibility of molecular phenotypes "
    "after long-term differentiation to human iPSC-derived neurons: a multi-site "
    "omics study. Stem Cell Reports. 2018;11(4):897-911.",
    # 2
    "McCreery KP, Stubb A, Stephens R, et al. Mechano-osmotic signals control "
    "chromatin state and fate transitions in pluripotent stem cells. Nat Cell Biol. "
    "2025;27(10):1757-1770.",
    # 3
    "Bi S, Tang J, Zhang L, et al. Fine particulate matter reduces the pluripotency "
    "and proliferation of human embryonic stem cells through ROS induced AKT and ERK "
    "signaling pathway. Reprod Toxicol. 2020;96:231-240.",
    # 4
    "Cai J, Zhou L, Liu L, et al. Real-time monitoring reveals the effects of low "
    "concentrations of volatile organic compounds in the embryology laboratory. Hum "
    "Reprod. 2025;40(4):601-611.",
    # 5
    "Barrett T, Wilhite SE, Ledoux P, et al. NCBI GEO: archive for functional "
    "genomics data sets-update. Nucleic Acids Res. 2013;41(D):D991-D995.",
]


def add_superscript_refs(paragraph, text, base_size=Pt(11), ref_size=Pt(9)):
    """Parse text with {N} or {N-M} or {N,M} markers and create superscript runs."""
    parts = re.split(r'(\{[^}]+\})', text)
    for part in parts:
        if part.startswith('{') and part.endswith('}'):
            run = paragraph.add_run(part[1:-1])
            run.font.superscript = True
            run.font.size = ref_size
        else:
            run = paragraph.add_run(part)
            run.font.size = base_size
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


def count_words(doc, include_fig_legend=True, include_refs=True, include_declarations=True):
    """Approximate word count from document paragraphs."""
    text = []
    ref_block = False
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("References"):
            ref_block = True
        if not include_refs and ref_block and re.match(r'^\d+\.\s', t):
            continue
        if not include_fig_legend and t.startswith("Figure 1."):
            continue
        if not include_declarations and t.startswith(("Ethics approval", "Availability of data",
                                                      "Competing interests", "Funding",
                                                      "Consent for publication",
                                                      "Authors' contributions")):
            continue
        text.append(t)
    full = ' '.join(text)
    return len(full.split())


def create_figure1(summary=None):
    """Figure 1: Clonality does not eliminate environmental variance."""
    if summary is None:
        summary = compute_geo_summary()

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2), dpi=150)

    # Panel A: variance components
    x = np.linspace(-3, 3, 300)
    genetic = np.exp(-x**2 / 0.3) / np.sqrt(0.3 * np.pi) / 2
    env_narrow = np.exp(-x**2 / 0.8) / np.sqrt(0.8 * np.pi) / 1.5
    env_wide = np.exp(-x**2 / 2.2) / np.sqrt(2.2 * np.pi)

    axes[0].plot(x, genetic, color='#2ca02c', linewidth=2.5, label='Genetic variance (clonal)')
    axes[0].plot(x, env_narrow, color='#d62728', linewidth=2.5, linestyle='--',
                 label='Environmental variance (GMP)')
    axes[0].plot(x, env_wide, color='#ff7f0e', linewidth=2.5, linestyle=':',
                 label='Environmental variance (research lab)')
    axes[0].set_xlabel('Differentiation outcome deviation', fontsize=11)
    axes[0].set_ylabel('Frequency', fontsize=11)
    axes[0].set_title('A  Variance components', fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=7, loc='upper right')
    axes[0].spines['top'].set_visible(False)
    axes[0].spines['right'].set_visible(False)

    # Panel B: GEO natural-experiment mini
    geo_path = os.path.join(OUTPUT_DIR, "geo_psc_metadata.csv")
    country_path = os.path.join(OUTPUT_DIR, "geo_country_full.csv")
    geo = pd.read_csv(geo_path)
    geo['date'] = pd.to_datetime(geo['date'])
    countries = pd.read_csv(country_path)
    country_map = dict(zip(countries["accession"], countries["country"]))
    geo['country'] = geo['accession'].map(country_map)

    march_april_start = {"Japan", "South Korea"}
    sept_oct_start_nh = {
        "USA", "United Kingdom", "Germany", "China", "France", "Italy", "Spain",
        "Canada", "Netherlands", "Belgium", "Switzerland", "Sweden", "Denmark",
        "Austria", "Finland", "Norway", "Ireland", "Israel", "Singapore", "Taiwan",
        "Poland", "Czech Republic", "Portugal", "Hong Kong"
    }
    jan_feb_start_sh = {
        "Australia", "New Zealand", "Brazil", "South Africa", "Argentina", "Chile"
    }

    def assign_group(c):
        if not isinstance(c, str):
            return None
        c = c.strip()
        if c in march_april_start:
            return "Mar/Apr-start (JP/KR)"
        if c in sept_oct_start_nh:
            return "Sep/Oct-start (US/EU/CN)"
        if c in jan_feb_start_sh:
            return "Jan/Feb-start (AU/NZ/BR, SH)"
        return None

    geo['group'] = geo['country'].apply(assign_group)
    filtered = geo[geo['group'].notna()]

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    colors = {
        "Jan/Feb-start (AU/NZ/BR, SH)": '#1f77b4',
        "Mar/Apr-start (JP/KR)": '#2ca02c',
        "Sep/Oct-start (US/EU/CN)": '#ff7f0e',
    }

    for group, gdf in filtered.groupby('group'):
        counts = gdf.groupby(gdf['date'].dt.month).size().reindex(range(1, 13), fill_value=0)
        props = counts / counts.sum()
        axes[1].plot(range(1, 13), props, marker='o', linewidth=2,
                     label=group, color=colors[group])

    axes[1].axhline(1 / 12, color='gray', linestyle='--', linewidth=1, label='Uniform')
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xticklabels(month_names, fontsize=9)
    axes[1].set_xlabel('Month of GEO release', fontsize=11)
    axes[1].set_ylabel('Proportion of datasets', fontsize=11)
    axes[1].set_title('B  GEO seasonality by academic-year group', fontsize=12,
                      fontweight='bold')
    axes[1].legend(fontsize=6.5, loc='upper right')
    axes[1].spines['top'].set_visible(False)
    axes[1].spines['right'].set_visible(False)

    # Panel C: temporal drift
    t = np.linspace(0, 10, 100)
    base = np.sin(t) * 0.5
    env = np.sin(t * 0.7) * 0.8 + 0.3 * np.sin(t * 2.3)
    axes[2].fill_between(t, base - 0.2, base + 0.2, color='#2ca02c', alpha=0.3,
                         label='Genetic range (clonal)')
    axes[2].fill_between(t, env - 0.4, env + 0.4, color='#ff7f0e', alpha=0.25,
                         label='Environmental range (unmonitored)')
    axes[2].plot(t, base, color='#2ca02c', linewidth=2)
    axes[2].plot(t, env, color='#ff7f0e', linewidth=2)
    axes[2].set_xlabel('Time / experimental condition', fontsize=11)
    axes[2].set_ylabel('Outcome deviation', fontsize=11)
    axes[2].set_title('C  Unmonitored environmental drift', fontsize=12,
                      fontweight='bold')
    axes[2].legend(fontsize=7, loc='lower right')
    axes[2].spines['top'].set_visible(False)
    axes[2].spines['right'].set_visible(False)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "SCRR_Comment_Figure1_Clonal_Environmental_Variance.png")
    fig.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


def compute_geo_summary():
    """Compute summary statistics from public GEO data for the Comment text."""
    geo_path = os.path.join(OUTPUT_DIR, "geo_psc_metadata.csv")
    country_path = os.path.join(OUTPUT_DIR, "geo_country_full.csv")

    geo = pd.read_csv(geo_path)
    geo['date'] = pd.to_datetime(geo['date'])
    countries = pd.read_csv(country_path)
    country_map = dict(zip(countries["accession"], countries["country"]))
    geo['country'] = geo['accession'].map(country_map)

    n_total = len(geo)
    month_counts = geo.groupby(geo['date'].dt.month).size().sort_index()
    peak_month = int(month_counts.idxmax())
    peak_count = int(month_counts.max())
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    peak_month_name = month_names[peak_month - 1]

    n_country = int(geo['country'].notna().sum())

    southern = {"australia", "new zealand", "brazil", "argentina", "south africa",
                "chile", "peru", "colombia", "indonesia", "madagascar"}
    hemisphere = geo['country'].apply(
        lambda c: "Southern" if isinstance(c, str) and c.lower().strip() in southern
        else ("Northern" if isinstance(c, str) else None)
    )
    n_nh = int((hemisphere == "Northern").sum())
    n_sh = int((hemisphere == "Southern").sum())
    n_known_hemi = n_nh + n_sh
    pct_nh = round(100 * n_nh / n_known_hemi) if n_known_hemi > 0 else 0

    march_april_start = {"Japan", "South Korea"}
    sept_oct_start_nh = {"USA", "United Kingdom", "Germany", "China", "France",
                         "Italy", "Spain", "Canada", "Netherlands", "Belgium",
                         "Switzerland", "Sweden", "Denmark", "Austria", "Finland",
                         "Norway", "Ireland", "Israel", "Singapore", "Taiwan",
                         "Poland", "Czech Republic", "Portugal", "Hong Kong"}
    jan_feb_start_sh = {"Australia", "New Zealand", "Brazil", "South Africa",
                        "Argentina", "Chile"}

    def assign_group(c):
        if not isinstance(c, str):
            return None
        c = c.strip()
        if c in march_april_start:
            return "Mar/Apr-start (JP/KR)"
        if c in sept_oct_start_nh:
            return "Sep/Oct-start (US/EU/CN)"
        if c in jan_feb_start_sh:
            return "Jan/Feb-start (AU/NZ/BR, SH)"
        return None

    geo['acad_group'] = geo['country'].apply(assign_group)

    def rayleigh_test(months):
        arr = np.array(months)
        theta = 2 * math.pi * (arr - 1) / 12
        n = len(theta)
        C = np.sum(np.cos(theta))
        S = np.sum(np.sin(theta))
        R = math.sqrt(C**2 + S**2) / n
        Z = n * R**2
        p = math.exp(-Z)
        return R, Z, p

    def chi2_uniformity(counts_12):
        observed = np.array([counts_12.get(m, 0) for m in range(1, 13)])
        expected = np.full(12, observed.sum() / 12)
        return stats.chisquare(observed, expected)

    group_stats = {}
    for gname, gdf in geo[geo['acad_group'].notna()].groupby('acad_group'):
        counts = gdf.groupby(gdf['date'].dt.month).size()
        chi2, p_chi2 = chi2_uniformity(counts)
        R, Z, p_ray = rayleigh_test(gdf['date'].dt.month.values)
        peak_m = int(counts.idxmax())
        group_stats[gname] = {
            "n": int(len(gdf)),
            "peak_month": month_names[peak_m - 1],
            "chi2": float(chi2),
            "p_chi2": float(p_chi2),
            "R": float(R),
            "p_ray": float(p_ray),
        }

    summary = {
        "n_total": n_total,
        "n_country": n_country,
        "n_nh": n_nh,
        "n_sh": n_sh,
        "pct_nh": pct_nh,
        "peak_month": peak_month,
        "peak_month_name": peak_month_name,
        "peak_count": peak_count,
        "group_stats": group_stats,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    json_path = os.path.join(OUTPUT_DIR, "comment_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Comment summary saved to: {json_path}")
    return summary


def create_manuscript():
    summary = compute_geo_summary()
    n_total = summary["n_total"]
    peak_month_name = summary["peak_month_name"]
    peak_count = summary["peak_count"]
    gs = summary["group_stats"]
    jpkr_n = gs["Mar/Apr-start (JP/KR)"]["n"]
    jpkr_p = gs["Mar/Apr-start (JP/KR)"]["p_chi2"]
    sepoct_n = gs["Sep/Oct-start (US/EU/CN)"]["n"]
    sepoct_p = gs["Sep/Oct-start (US/EU/CN)"]["p_chi2"]
    sepoct_peak = gs["Sep/Oct-start (US/EU/CN)"]["peak_month"]
    sh_n = gs["Jan/Feb-start (AU/NZ/BR, SH)"]["n"]
    sh_p = gs["Jan/Feb-start (AU/NZ/BR, SH)"]["p_chi2"]
    sh_peak = gs["Jan/Feb-start (AU/NZ/BR, SH)"]["peak_month"]

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
    run = p.add_run("Comment")
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

    # Section 1
    add_heading(doc, "The clonal complacency trap", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Genetically identical pluripotent stem cell (PSC) lines are often treated as if they "
        "cancel out all systematic variance. The reasoning is intuitive: if every cell carries the "
        "same genome, then residual differences must be stochastic or technical. We argue that this "
        "'clonal complacency trap' conflates removing genetic variance with removing "
        "environmental variance. Clonality reduces the first, but not the second."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The problem is empirical, not philosophical. Volpato and colleagues showed that "
        "laboratory-of-origin explains more transcriptomic variance in iPSC-derived neurons than "
        "genetic background or differentiation batch.{1} Operator technique, reagent lots, and "
        "passage number account for part of that variance, yet a large residual remains unexplained. "
        "We propose that unmeasured environmental exposure is a missing explanatory variable."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "The crucial distinction is between genetic identity and environmental identity. Two "
        "aliquots of the same clone grown in different rooms, seasons, or buildings do not receive "
        "the same environmental input unless that input is measured and controlled. Treating "
        "unmeasured environmental exposure as a constant is an assumption, not a fact, and it "
        "weakens the scientific basis for comparing protocols, lines, and laboratories."
    )

    # Section 2
    add_heading(doc, "Why PSCs are environmentally exposed", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Pluripotent cells are unusually sensitive to physical parameters. Mechano-osmotic "
        "perturbations alter nuclear morphology, chromatin state, and fate transitions in human "
        "iPSCs, with implications for routine biosafety-cabinet work where evaporation changes "
        "medium osmolarity.{2} Ambient fine particulate matter reduces pluripotency and proliferation "
        "in human embryonic stem cells through ROS-mediated signalling, showing that ordinary air "
        "quality directly affects pluripotency.{3} In embryology laboratories, continuous "
        "monitoring has demonstrated that low concentrations of volatile organic compounds correlate "
        "with compromised embryo quality, yet comparable monitoring is rarely reported in PSC "
        "studies.{4} Together, these observations are consistent with a shallow energetic "
        "landscape in which small environmental shifts can tip the balance between self-renewal and "
        "lineage commitment. Although many published protocols still assume environmental homogeneity, "
        "the evidence above suggests that assumption is frequently violated."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Good Manufacturing Practice (GMP) facilities already treat temperature, humidity, "
        "particulate counts, microbial contamination, and operator flow as critical process "
        "variables, logging them continuously for regulatory audit. Most academic research "
        "laboratories control only incubator temperature and CO2. Humidity, ambient light, "
        "electromagnetic fields, barometric pressure, and vibration are typically unlogged. This "
        "disparity in monitoring discipline creates a reproducibility gap between clinical-grade "
        "manufacturing and discovery research."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "This gap is no longer only academic. As PSC-derived products move toward clinical "
        "translation, manufacturing guidelines increasingly treat environmental parameters as "
        "process variables that should be logged continuously. Recording the same variables in "
        "discovery research would narrow the reproducibility gap between clinical-grade "
        "manufacturing and academic laboratories."
    )

    # Section 3
    add_heading(doc, "Why public databases cannot settle the question", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Figure 1A and 1C schematize the conceptual distinction between narrow genetic variance "
        "and broad environmental variance; Figure 1B tests the same idea with public data. "
        f"An exploratory analysis of {n_total:,} PSC differentiation-related GEO Series shows why "
        f"retrospective metadata are more cautionary than probative. Overall submissions peaked in "
        f"{peak_month_name} ({peak_count:,} datasets). Grouping submissions by academic-year "
        f"start shows that the {peak_month_name} signal was concentrated in the Japan/"
        f"Korea group (n={jpkr_n}, p={jpkr_p:.4f}), while the larger September-start group "
        f"(n={sepoct_n}) had its highest count in {sepoct_peak} and showed no significant "
        f"seasonality (p={sepoct_p:.4f}). The small Southern Hemisphere group (n={sh_n}) "
        f"also peaked in {sh_peak}, consistent with institutional rather than hemisphere-inverted "
        f"biological timing, although the deviation from uniformity was not significant "
        f"(p={sh_p:.4f}). These mixed patterns suggest that GEO submission dates cannot "
        f"separate institutional and biological seasonality.{{5}}"
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "This limitation is structural. GEO submission dates are a convolution of experiment "
        "timing, analysis duration, manuscript preparation, peer review, revision, and institutional "
        "reporting deadlines, with typical lags of six to eighteen months from bench to deposition. "
        "Even if PSC differentiation were strongly seasonal, that signal would be obscured. "
        "Retrospective database mining can generate hypotheses, but it cannot test them."
    )

    # Inline Figure 1 (after Section 3)
    fig1_path = create_figure1(summary)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_paragraph_format(p, space_before=Pt(12), space_after=Pt(6))
    doc.add_picture(fig1_path, width=Inches(6.5))

    p = doc.add_paragraph()
    set_paragraph_format(p, space_after=Pt(12))
    run = p.add_run("Figure 1. ")
    run.bold = True
    run.font.size = Pt(10)
    caption_rest = (
        "Clonality does not eliminate environmental variance. (A) A clonal population has narrow "
        "genetic variance (green) but can still experience wide environmental variance (orange), "
        "especially in research laboratories that do not monitor environmental parameters. "
        "(B) Monthly distribution of PSC-related GEO Series by academic-year start group "
        "(Jan/Feb-start Southern Hemisphere, Mar/Apr-start Japan/Korea, Sep/Oct-start US/EU/CN). "
        "Lines show the proportion of datasets released per month; the dashed grey line is uniform "
        "expectation. Data source: NCBI GEO.{5} "
        "(C) Over time, unmonitored environmental drift can produce outcome variation comparable "
        "to \u2014 or larger than \u2014 genetic effects, even when all cells are isogenic."
    )
    add_superscript_refs(p, caption_rest, base_size=Pt(10), ref_size=Pt(9))

    # Section 4
    add_heading(doc, "A path forward", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "What is missing is systematic environmental monitoring. Inexpensive modern Internet-of-"
        "Things sensors can record temperature, humidity, illuminance, volatile organic compounds, "
        "electromagnetic fields, barometric pressure, and vibration at one-minute intervals over "
        "months. The statistical challenge is to separate these signals from batch, operator, "
        "reagent lot, and genetic effects."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "A practical framework has three stages. First, a baseline variance-budgeting phase of at "
        "least twelve months deploys multi-parameter sensors alongside routine differentiation "
        "outcomes and estimates the magnitude and autocorrelation of environmental fluctuations. "
        "This phase is exploratory, not a formal hypothesis test. Second, a retrospective screen "
        "uses time-lagged regression with false-discovery-rate control to identify candidate "
        "variables linked to historical batch outcomes. Third, an experimental perturbation phase "
        "uses blocked factorial or crossover designs with mixed-effects models and equivalence "
        "testing for negative findings."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "Analytical choices matter. Differentiation outcomes are usually proportions or counts, so "
        "generalized linear mixed models with appropriate link functions are preferable to ordinary "
        "linear regression. Seasonal components should be modeled with circular or harmonic terms, "
        "not arbitrary month labels. Cross-validation and holdout laboratories should assess "
        "external validity, and null findings should be reported with equivalence bounds so that "
        "absence of evidence is not mistaken for evidence of absence."
    )

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.5)
    add_superscript_refs(p,
        "We are not claiming that uncontrolled environments dominate PSC variability. We are "
        "claiming that they remain largely unmeasured, that measuring them is feasible, and that the "
        "PSC field should stop assuming that isogenic cells grown in different rooms, seasons, or "
        "buildings receive the same environmental exposure. Even well-powered null results would be "
        "valuable: a decisive absence of association for a particular variable would tell the field "
        "it can stop worrying about that variable. The clonal complacency trap will persist until "
        "environmental exposure is measured, not assumed."
    )

    # Declarations
    add_heading(doc, "Declarations", level=2)

    p = doc.add_paragraph()
    set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
    run = p.add_run("Ethics approval and consent to participate: ")
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
        "All GEO dataset metadata were downloaded from NCBI GEO{5} using the Entrez E-utilities "
        "search interface. Processed metadata and reproducibility code are available at "
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

    # References
    add_heading(doc, "References", level=2)
    for i, ref in enumerate(REFERENCES, 1):
        p = doc.add_paragraph()
        set_paragraph_format(p, line_spacing=1.15, space_after=Pt(3))
        run = p.add_run(f"{i}. {ref}")
        run.font.size = Pt(10)

    out_path = os.path.join(OUTPUT_DIR, "StemCellReviewsAndReports_Comment_InvisibleVariables.docx")
    doc.save(out_path)

    # Strip CJK/fullwidth font entries from the archive XML; visible text is unchanged.
    from docx_utils import sanitize_ooxml_package
    sanitize_ooxml_package(out_path)

    total_words = count_words(doc, include_fig_legend=True, include_refs=True,
                              include_declarations=True)
    body_words = count_words(doc, include_fig_legend=False, include_refs=False,
                             include_declarations=False)

    print(f"Manuscript saved to: {out_path}")
    print(f"Total words (including declarations/figure legend): {total_words}")
    print(f"Approximate main-body words: {body_words}")
    return out_path


if __name__ == "__main__":
    create_manuscript()
