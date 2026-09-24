#!/usr/bin/env python3
"""Generate the Pattern Recognition manuscript (manuscript_pattern_recognition.docx).

Target: Pattern Recognition (Elsevier).  Format followed here: single column,
double-spaced, numbered pages and lines, Times New Roman 12 pt, structured
abstract-free (one paragraph, <= 200 words), up to 6 keywords, numbered
sections, bracketed numbered citations [n] in order of first appearance
(Elsevier numbered style), figures and tables inline immediately after their
first mention (plus separate figure files for Editorial Manager, see
create_pr_supporting.py), Declaration of competing interest, CRediT and
Data availability sections before the references.

All numbers are read from results/*.json through pr_numbers.py; the
figures are produced by make_pr_figures.py from the same JSON files.  The
OMML equation and citation helpers are shared with the JATIS generator.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt
from docx.text.paragraph import Paragraph
from lxml import etree

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PROJECT / 'jatis_submission'))

import create_jatis_docx as jd
from pr_numbers import (
    auc,
    auc_sd,
    dauc,
    dauc_sd,
    fmt,
    load_numbers,
    pct,
    pfmt,
)

N = load_numbers()
OUT_DIR = HERE

TITLE = ('Self-calibrating unsupervised anomaly detection in sparse event streams: '
         'replacing designer-chosen time scales with data-native scales')
AUTHOR = 'Tatsuki Onishi'
AUTHOR_INITIALS = 'T.O.'
AFFILIATION = 'Data Science and AI Innovation Research Promotion Center, Shiga University, Hikone, Japan'
ADDRESS = '1-1-1 Banba, Hikone, Shiga 522-8522, Japan'
PHONE = '+81-749-27-1023'
EMAIL = 'bougtoir@gmail.com'

# =========================================================
# Reference database; numbering is automatic, in order of first appearance
# =========================================================
REFS = dict(jd.REFS)
REFS.update({
    'baldwin': 'R. W. Baldwin, M. Almatrafi, V. Asari, and K. Hirakawa, "Event probability mask (EPM) '
               'and event denoising convolutional neural network (EDnCNN) for neuromorphic cameras," '
               'in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition, 1698-1707 (2020).',
    'chandola': 'V. Chandola, A. Banerjee, and V. Kumar, "Anomaly detection: a survey," ACM Comput. Surv. '
                '41(3), Art. 15, 1-58 (2009).',
    'ruff': 'L. Ruff, J. R. Kauffmann, R. A. Vandermeulen, et al., "A unifying review of deep and shallow '
            'anomaly detection," Proc. IEEE 109(5), 756-795 (2021).',
    'pimentel': 'M. A. F. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko, "A review of novelty '
                'detection," Signal Process. 99, 215-249 (2014).',
    'aednet': 'H. Fang, J. Wu, L. Li, et al., "AEDNet: asynchronous event denoising with spatial-temporal '
              'correlation among irregular data," in Proc. 30th ACM Int. Conf. Multimedia, 1427-1435 (2022).',
    'wednet': 'H. Fang, J. Wu, Q. Hou, W. Dong, and G. Shi, "Fast window-based event denoising with '
              'spatiotemporal correlation enhancement," IEEE Trans. Pattern Anal. Mach. Intell. 47(3), '
              '1381-1394 (2025).',
    'pfd': 'C. Shi, B. Wei, X. Wang, et al., "Polarity-focused denoising for event cameras," IEEE Trans. '
           'Circuits Syst. Video Technol. 35(5), 4370-4383 (2025).',
    'emlb': 'S. Ding, J. Chen, Y. Wang, et al., "E-MLB: multilevel benchmark for event-based camera denoising," '
            'IEEE Trans. Multimedia 26, 65-76 (2024).',
    'v2e': 'Y. Hu, S.-C. Liu, and T. Delbruck, "v2e: from video frames to realistic DVS events," in Proc. '
           'IEEE/CVF Conf. Computer Vision and Pattern Recognition Workshops, 1312-1321 (2021).',
    'shi_rot': 'C. Shi, Y. He, W. Li, et al., "Modeling multi-segment acceleration for event camera rotation '
               'estimation," Pattern Recognit. 179, Art. 113946 (2026).',
    'vo_ppp': 'B.-N. Vo, N. Dam, D. Phung, Q. N. Tran, and B.-T. Vo, "Model-based learning for point pattern '
              'data," Pattern Recognit. 84, 136-151 (2018).',
    'doshi': 'K. Doshi and Y. Yilmaz, "Online anomaly detection in surveillance videos with asymptotic bound '
             'on false alarm rate," Pattern Recognit. 114, Art. 107865 (2021).',
    'liu2015': 'H. Liu, C. Brandli, C. Li, S.-C. Liu, and T. Delbruck, "Design of a spatiotemporal correlation '
               'filter for event-based sensors," in Proc. IEEE Int. Symp. Circuits and Systems, 722-725 (2015).',
    'hanley': 'J. A. Hanley and B. J. McNeil, "The meaning and use of the area under a receiver operating '
              'characteristic (ROC) curve," Radiology 143(1), 29-36 (1982).',
    'efron': 'B. Efron and R. J. Tibshirani, An Introduction to the Bootstrap, Chapman & Hall, New York (1993).',
    'kerby': 'D. S. Kerby, "The simple difference formula: an approach to teaching nonparametric correlation," '
             'Compr. Psychol. 3, Art. 11.IT.3.1 (2014).',
})
jd.REFS = REFS
jd.CITE_ORDER = []
jd.FIG_DIR = HERE

_PUNCT_CITE = re.compile(r'([.,;:])(\{cite:[^}]+\})')


def add_runs(p, text, size=None, bold=False, italic=False):
    """Elsevier numbered style: citations as [n] in line with the text, placed before punctuation."""
    text = _PUNCT_CITE.sub(r'\2\1', text)
    parts = jd.TOKEN.split(text)
    for i, part in enumerate(parts):
        if part.startswith('{cite:'):
            keys = [k.strip() for k in part[6:-1].split(',')]
            prev = parts[i - 1] if i else ''
            lead = '' if (not prev or prev.endswith((' ', '('))) else ' '
            run = p.add_run(f'{lead}[{jd._format_numbers([jd.cite_number(k) for k in keys])}]')
        elif part:
            run = p.add_run(part)
            run.bold = bold
            run.italic = italic
        else:
            continue
        if size:
            run.font.size = size


jd.add_runs = add_runs  # jd.para calls add_runs through its module globals
para = jd.para
_mr, _sub, _sup, _frac, _delim, _hat, _nary = jd._mr, jd._sub, jd._sup, jd._frac, jd._delim, jd._hat, jd._nary


def para_math(doc, segments, space_after=6):
    """Paragraph mixing text and inline native (OMML) equations; segments are str or builder callables."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    for seg in segments:
        if callable(seg):
            seg(etree.SubElement(p._element, qn('m:oMath')))
        else:
            add_runs(p, seg)
    return p


# Eq. (5): tau_alpha = Q_alpha({P_i}); pass event i if P_i < tau_alpha (strict, see Section 3.4)
def eq_threshold(o):
    _sub(o, '\u03c4', '\u03b1')
    _mr(o, ' = ')
    _mr(o, 'Q', italic=False)
    _sub(o, '', '\u03b1')
    _delim(o, lambda e: (_mr(e, '{'), _sub(e, 'P', 'i'), _mr(e, '}')))
    _mr(o, ',      pass event i if ', italic=False)
    _sub(o, 'P', 'i')
    _mr(o, ' < ')
    _sub(o, '\u03c4', '\u03b1')


# Eq. (6): W = k / median_i( sum_{|u|,|v| <= r} lambda_hat_{x_i+u, y_i+v} )
def eq_window(o):
    _mr(o, 'W = ')
    _frac(o, lambda n: _mr(n, 'k'),
          lambda d: (_mr(d, 'median', italic=False), _sub(d, '', 'i'),
                     _delim(d, lambda e: _nary(e, '\u2211', lambda s: _mr(s, '|u|,|v| \u2264 r'), lambda s: None,
                                                lambda b: (_hat(b, '\u03bb'), _sub(b, '', 'x_i+u, y_i+v'))))))


# inline: Delta_xy(q) = -ln(1 - q) / lambda
def eq_quantile_inline(o):
    _sub(o, '\u0394', 'xy')
    _mr(o, '(q) = ')
    _frac(o, lambda n: (_mr(n, '\u2212ln', italic=False), _delim(n, lambda e: _mr(e, '1 \u2212 q'))),
          lambda d: _mr(d, '\u03bb'))


# inline: e_i = (x_i, y_i, t_i, p_i)
def eq_event_inline(o):
    _sub(o, 'e', 'i')
    _mr(o, ' = ')
    _delim(o, lambda e: (_sub(e, 'x', 'i'), _mr(e, ', '), _sub(e, 'y', 'i'), _mr(e, ', '),
                         _sub(e, 't', 'i'), _mr(e, ', '), _sub(e, 'p', 'i')))

# registry of every figure and table placed in the manuscript, in order, for the
# supporting files (editable tables DOCX, PPTX, figure legends)
ORDER = ['edlr', 'edlr_adaptive', 'bilateral', 'ynoise', 'motion', 'temporal', 'dwf', 'nearest', 'knoise',
         'bilateral_ed', 'knn_pp', 'waiting_lr', 'flow_matched', 'dwf_ed', 'recursive',
         'plr', 'pi_dc_dvs', 'fano', 'edncnn', 'mlpf']
FIGURES = []
TABLES = []
SUPP_FIGURES = []
SUPP_TABLES = []


BODY_PT = 10       # Pattern Recognition: text incl. tables 10 pt
CAPTION_PT = 8     # captions and footnotes 8 pt
TITLE_PT = 14      # title 14 pt; author block 8 pt
AUTHOR_PT = 8
LINE_SPACING = 1.5  # 'double-spaced (1.5 in MS Word)'
TEXT_WIDTH = Cm(21.0 - 4.8 - 4.8)  # A4, margins 4.3/4.8/4.3/4.8 cm (top/right/bottom/left)


def _set_runs(p, size):
    for r in p.runs:
        r.font.size = Pt(size)
    return p


def heading(doc, text, level=1):
    return _set_runs(jd.heading(doc, text, level), BODY_PT)


def add_display_equation(doc, builder_func, eq_num):
    p = jd.add_display_equation(doc, builder_func, eq_num)
    if p is not None:
        _set_runs(p, BODY_PT)
    return p


def _figure_body(doc, filename, caption, width):
    cap = jd.figure(doc, filename, caption, width=min(width, TEXT_WIDTH))
    cap.paragraph_format.line_spacing = 1.0
    _set_runs(cap, CAPTION_PT)
    return cap


def figure(doc, filename, caption, width=Inches(6.0)):
    FIGURES.append({'file': filename, 'caption': caption})
    _figure_body(doc, filename, caption, width)


def _new_section(doc, landscape):
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    w, h = (Cm(29.7), Cm(21.0)) if landscape else (Cm(21.0), Cm(29.7))
    sec.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = w, h
    sec.top_margin, sec.right_margin, sec.bottom_margin, sec.left_margin = Cm(4.3), Cm(4.8), Cm(4.3), Cm(4.8)
    return sec


def _table_body(doc, caption, headers, rows, col_widths=None, font_pt=9, landscape=False):
    if landscape:
        _new_section(doc, True)
    text_width = Cm(29.7 - 4.8 - 4.8) if landscape else TEXT_WIDTH
    if col_widths:
        scale = text_width.inches / sum(col_widths)
        col_widths = [w * scale for w in col_widths]  # inches, filling the text width
    t = jd.table(doc, caption, headers, rows, col_widths=col_widths, font_pt=BODY_PT)
    if col_widths:  # LibreOffice/Word honour the grid, not only the cell widths
        t.autofit = False
        for gc, w in zip(t._tbl.tblGrid.findall(qn('w:gridCol')), col_widths):
            gc.set(qn('w:w'), str(int(Inches(w).twips)))
    if landscape:
        _new_section(doc, False)
    cap = Paragraph(t._tbl.getprevious(), t._parent)
    cap.paragraph_format.line_spacing = 1.0
    _set_runs(cap, CAPTION_PT)
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(0)
    return t


def table(doc, caption, headers, rows, col_widths=None, font_pt=9, landscape=False):
    TABLES.append({'caption': caption, 'headers': headers, 'rows': rows})
    return _table_body(doc, caption, headers, rows, col_widths, font_pt, landscape)


def sfigure(doc, filename, caption, width=Inches(6.0)):
    SUPP_FIGURES.append({'file': filename, 'caption': caption})
    _figure_body(doc, filename, caption, width)


def stable(doc, caption, headers, rows, col_widths=None, font_pt=9, landscape=False):
    SUPP_TABLES.append({'caption': caption, 'headers': headers, 'rows': rows})
    return _table_body(doc, caption, headers, rows, col_widths, font_pt, landscape)


def ci(e):
    return f"[{e['ci95'][0]:+.3f}, {e['ci95'][1]:+.3f}]"


def label(key):
    return N['methods'][key]['label']


SHORT = {'bilateral': 'event bilateral filter', 'ynoise': 'YNoise', 'motion': 'motion-compensated proxy',
         'temporal': 'background-activity filter', 'dwf': 'DWF', 'nearest': 'nearest-neighbour filter',
         'knoise': 'kNoise'}


def short(key):
    return SHORT.get(key, label(key))


class _LFLabel(dict):
    def __missing__(self, key):
        if key.startswith('hybrid_'):
            return f'the two-stage cascade at f = {key.split("_", 1)[1]}'
        return key.replace('_', ' ')


LF_LABEL = _LFLabel({'zero_knowledge': 'the untuned proposal', 'ynoise_default': 'YNoise at its published default',
                     'ynoise_handoff': 'YNoise with the handed-over window'})


def cond_name(c):
    return c.replace('_', ' ').replace('hz', ' Hz')


def zk_max_drop(key):
    return max(v[key]['drop'] for v in N['zk']['cross_sensor_transfer'].values())


def ieee_ref(ref):
    """Journal example style: authors comma-separated, unquoted title, venue (year)."""
    if ref.count('"') != 2:  # books: the author list ends at the first ', ' not followed by an initial
        m = re.match(r'^(.*?), (?![A-Z]\.|and [A-Z]\.)', ref)
        authors, rest = ref[:m.end() - 2], ref[m.end():]
        return re.sub(r',? and ', ', ', authors) + ', ' + rest
    authors, title, rest = ref.split('"')
    authors = re.sub(r',? and ', ', ', authors)
    return authors + title.rstrip(',') + ',' + rest


def _page_setup(doc):
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(BODY_PT)
    style.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    style.paragraph_format.line_spacing = LINE_SPACING
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.top_margin, sec.right_margin, sec.bottom_margin, sec.left_margin = Cm(4.3), Cm(4.8), Cm(4.3), Cm(4.8)
    # continuous line numbers (Elsevier reviewing convenience)
    ln = OxmlElement('w:lnNumType')
    ln.set(qn('w:countBy'), '1')
    ln.set(qn('w:restart'), 'continuous')
    sec._sectPr.append(ln)
    # page number field in the footer
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    for tag, text in (('begin', None), (None, 'PAGE'), ('end', None)):
        if tag:
            el = OxmlElement('w:fldChar')
            el.set(qn('w:fldCharType'), tag)
        else:
            el = OxmlElement('w:instrText')
            el.set(qn('xml:space'), 'preserve')
            el.text = text
        run._r.append(el)


def ebssa_transfer_name(k):
    return {'edlr_adaptive_ebssa': 'proposed, rate-adaptive window', 'edlr_ebssa': 'proposed, fixed window',
            'ynoise_ebssa': 'YNoise', 'bilateral_ebssa': 'event bilateral filter', 'dwf_ebssa': 'DWF',
            'knoise_ebssa': 'kNoise', 'temporal_ebssa': 'background-activity filter',
            'plr_ebssa': 'voxelised Poisson LR'}.get(k, k)


def build():
    FIGURES.clear()
    TABLES.clear()
    SUPP_FIGURES.clear()
    SUPP_TABLES.clear()
    jd.CITE_ORDER.clear()
    doc = Document()
    _page_setup(doc)
    supp = Document()
    _page_setup(supp)
    para(supp, 'Supplementary material', size=Pt(TITLE_PT), bold=True, space_after=8)
    para(supp, TITLE, size=Pt(AUTHOR_PT), italic=True, space_after=2)
    para(supp, f'{AUTHOR}; {AFFILIATION}; {EMAIL}', size=Pt(AUTHOR_PT), space_after=12)
    para(supp, 'This file contains the comparator feasibility table, the effect-size tables, the exploratory '
               'stratified results, the cost-scaling figure and table, the zero-knowledge transfer table, the '
               'qualitative example and the AEDNet transfer table referred to in the main text as Supplementary '
               'Fig. S1-S2 and Table S1-S7. All values are '
               'generated from the same result files as the main text.', space_after=12)
    m = N['methods']
    tests = N['tests']
    es_e = N['es_ebssa']
    es_d = N['es_dnd']
    sc = N['selfcal']
    pa = N['pauc']
    dm = N['dnd_methods']
    dt = N['dnd_tests_tuned']
    df = N['dnd_tests_free']
    n_pub = 7  # published unsupervised filters with grids on EBSSA (listed in Sec. 4.3)

    # ---------------- Title block ----------------
    para(doc, TITLE, size=Pt(TITLE_PT), bold=True, space_after=8)
    para(doc, AUTHOR, size=Pt(AUTHOR_PT), bold=True, space_after=2)
    para(doc, AFFILIATION, size=Pt(AUTHOR_PT), space_after=2)
    para(doc, f'Correspondence to: {AUTHOR}; {AFFILIATION}; {ADDRESS}; Telephone: {PHONE}; E-mail: {EMAIL}',
         size=Pt(AUTHOR_PT), space_after=10)

    # ---------------- Abstract ----------------
    hand_frac = N['hyb']['ynoise_full']['handoff']['auc']['mean'] / N['hyb']['ynoise_cv_reference']['auc_mean']
    aed_e, aed_d = N['aednet_ebssa'], N['aednet_dnd']
    abstract = (
        'Sparse asynchronous event streams mix a few informative events with spontaneous pixel noise. We cast '
        'their separation as self-calibrating, unsupervised anomaly detection on a point process: each pixel\'s '
        'background rate is estimated from its own inter-event intervals, every event is scored by the Poisson '
        'tail probability of the count in a causal neighbourhood, and the operating point follows from a stated '
        'false-alarm budget, not from labels. '
        f'On all {N["n_rec"]} labelled recordings of the Event-Based Space Situational Awareness (EBSSA) dataset '
        '(two sensors), with grouped-cross-validated comparators, the untuned detector reaches a mean area '
        f'under the receiver operating characteristic curve (ROC-AUC) of {auc(N, "edlr")}; the best label-tuned '
        f'filter (YNoise) reaches {auc(N, "ynoise")}, supervised networks up to {auc(N, "edncnn")}, and a released '
        f'supervised denoiser (AEDNet) applied unchanged {aed_e["aednet_mean_auc"]:.3f}. '
        'The false-alarm budget is met (requested 0.01, achieved '
        f'median {sc["edlr"]["0.01"]["fpr_median"]:.4f}). Its by-products transfer: the rate-adaptive '
        f'window, handed to YNoise without labels, brings that filter to {pct(hand_frac, 1)} of its label-tuned '
        'value, and a screen-then-confirm cascade improves on either alone. On '
        f'DND21, a third-sensor benchmark of dense scenes ({N["dnd_n_rec"]} mixtures), the detector '
        f'reaches only {dauc(N, "zero_knowledge")} against {dauc(N, "ynoise_default")} for the default '
        f'filter and {aed_d["aednet_mean_auc"]:.3f} for AEDNet, and the hand-over helps only on its sparse scenes, '
        'bounding the method to the sparse-transient regime.'
    )
    n_words = len(abstract.split())
    assert n_words <= 200, f'abstract has {n_words} words'
    heading(doc, 'Abstract')
    para(doc, abstract, space_after=6)
    para(doc, 'Keywords: anomaly detection; unsupervised learning; point process; event camera; '
              'Poisson likelihood ratio; self-calibration', space_after=12)

    # ---------------- 1 Introduction ----------------
    heading(doc, '1. Introduction')
    para(doc,
         'Many sensing systems deliver their measurements as a sparse, asynchronous stream of time-stamped '
         'discrete events rather than as regularly sampled arrays, and the pattern-recognition task is to '
         'decide, event by event, whether an event belongs to a structured source or to a spontaneous '
         'background. Event cameras, or dynamic vision sensors (DVS), are the most developed instance: each '
         'pixel emits an event when its log-intensity changes by more than a contrast threshold, giving '
         'microsecond timing and a dynamic range above 120 dB without a global exposure,{cite:gallego,lichtsteiner} '
         'and their streams are an active object of pattern-recognition research from ego-motion estimation '
         'to denoising.{cite:shi_rot,guo} '
         'Their dominant contaminant is background activity (BA), spontaneous events from junction leakage '
         'and shot noise in the pixel front end whose rate depends on temperature and illumination and '
         'differs from pixel to pixel.{cite:nozaki,guo} When the scene itself is sparse, as in optical space '
         'surveillance where faint resident space objects (RSOs) move over an almost static field,'
         '{cite:cohen,afshar,ralph} the stream is dominated by this background: in the recordings analysed '
         f'here the median rate is {N["rate_median"] / 1e3:.0f} kilo-events per second over a 180 x 240- or '
         f'240 x 304-pixel array, and only {pct(N["sig_median"], 2)} of the events (median) fall inside the '
         'annotated object boxes.')
    para(doc,
         'Event denoising is a mature topic: spatiotemporal correlation and density filters,'
         '{cite:delbruck2008,khodamoradi,feng} the double-window filter,{cite:guo} polarity-focused filters{cite:pfd} '
         'and supervised networks trained on labelled streams{cite:baldwin,guo,aednet,wednet} are reviewed in '
         'Section 2. Seen from the anomaly-detection literature,{cite:chandola,pimentel,ruff} they share two '
         'limitations. First, they output a heuristic score (a neighbour count or a network logit) whose '
         'threshold must be tuned on labelled data for each sensor and observing condition, and the supervised '
         'methods need labelled training streams from the same domain. Second, many high-performing variants '
         'run on a voxel grid of time bins and pixels, so their cost is set by the array and the recording '
         'length rather than by the number of events, and in a sparse regime most of the work is spent on '
         'empty voxels.')
    para(doc,
         'We take the starting point of unsupervised anomaly detection with an explicit null model. Under the '
         'null hypothesis that a pixel produces only BA, its events form an approximately Poisson point '
         'process with a pixel-specific rate that can be estimated from the stream itself; a source adds '
         'events that are clustered in space and time relative to that rate. The most powerful test for such a '
         'hypothesis, by the Neyman-Pearson lemma, is a likelihood ratio,{cite:neyman,kay} which for a Poisson '
         'count reduces to a tail probability monotone in the observed neighbourhood count. This gives an '
         'event-driven anomaly detector with three properties: (i) it '
         'requires no labels because the background model is fitted to the same stream it filters; (ii) its '
         'output is a probability on a common scale, so a false-alarm budget can be converted directly into a '
         'threshold; and (iii) it touches each event once with a small neighbourhood lookup, so its cost scales '
         'with the number of events rather than with the voxel grid.')
    para(doc,
         'A detector with these properties is more useful as a component than as a competitor: its window and '
         'threshold, derived from the target stream, can parameterise a downstream filter that would otherwise '
         'need labels, and its calibrated score can select the fraction of the stream that a more expensive stage '
         'examines. We are explicit that the detector alone does not exceed the best label-tuned filter or the '
         'supervised networks; its contribution is to reach most of their accuracy with no labels, no per-sensor '
         'tuning and no manually chosen threshold, and to supply the parameters those methods need.')
    para(doc,
         'The paper makes the following contributions, in three steps: the detector on its own with no prior '
         'knowledge of the stream, its parameters handed to other methods, and the regime in which either helps. '
         '(1) We formulate the event-driven Poisson '
         'likelihood-ratio (LR) detector as self-calibrating anomaly detection on a marked point process, with a '
         'per-event cost that is logarithmic in the stream length and a window stated as an expected background '
         'count rather than a time, a data-native scale in the sense that the stream itself supplies it, and we '
         'show that its probability output can be set to a requested false-alarm '
         'rate without labels. (2) We evaluate it, untuned, against '
         f'{sum(1 for k in m if not m[k]["supervised"] and not k.startswith("edlr"))} '
         f'unsupervised comparators and ablations, two supervised networks trained under grouped cross-validation '
         'and a released supervised denoiser (AEDNet) applied as a fixed model, on all '
         f'{N["n_rec"]} labelled recordings of the '
         'Event-Based Space Situational Awareness (EBSSA) dataset,{cite:afshar} using the published object '
         'annotations as ground truth, and we document which other learning-based denoisers cannot be run under '
         'this protocol. (3) We show that a window stated as an expected count transfers between sensor models '
         'whereas a window in milliseconds does not, and that this rate-derived window, handed to YNoise as its '
         f'time constant, recovers {pct(hand_frac, 1)} of the accuracy that labelled tuning gives that filter; a '
         'two-stage front end in which the proposal screens and YNoise confirms improves on both. (4) We test the '
         'whole label-free path unchanged on an independent benchmark recorded with a third sensor '
         f'(DND21,{{cite:guo}} {N["dnd_n_rec"]} mixtures of public signal and measured-noise recordings with exact '
         'origin labels), with leave-one-scene-out selection for every tuned comparator, and report the negative '
         'result on its dense scenes: the detector and the hand-over help on sparse, transient streams and not on '
         'dense ones. (5) We measure how the cost of '
         'event-driven and voxel-based formulations changes when real streams are thinned by two orders of '
         'magnitude. Every number, table and figure is generated from result files by the code named in the '
         'Data availability statement, and the reproducibility scope of each result file is stated there.')

    # ---------------- 2 Related work ----------------
    heading(doc, '2. Related work')
    heading(doc, '2.1. Event denoising', 2)
    para(doc,
         'Hand-crafted event filters use the observation that signal events are correlated in space and time '
         'while BA is not. The background-activity filter passes an event if a neighbour fired within a time '
         'constant,{cite:delbruck2008} kNoise keeps per-row and per-column memories to reduce its memory to '
         'O(N),{cite:khodamoradi} YNoise counts neighbours within a spatiotemporal window,{cite:feng} the '
         'double-window filter compares an event with the most recent signal and noise events,{cite:guo} and '
         'the polarity-focused filter (PFD) adds the consistency of polarity and of polarity change within the '
         'neighbourhood and has a seven-clock-cycle FPGA implementation.{cite:pfd} All have one or more time '
         'constants and radii that their authors set on their own sensors and scenes. Learning-based denoisers '
         'include the multilayer-perceptron filter (MLPF) on time-surface patches,{cite:guo} the event-denoising '
         'convolutional network (EDnCNN) trained on event-probability masks derived from frames and inertial '
         'data,{cite:baldwin} the asynchronous point-set network AEDNet,{cite:aednet} and the window-based '
         'network WedNet,{cite:wednet} all supervised. Benchmarks are DVSNOISE20, whose labels are '
         'model-derived probabilities,{cite:baldwin} DND21, which mixes clean or simulated signal recordings '
         'with measured sensor noise so that the origin of every event is known,{cite:guo} and E-MLB, which has '
         'no per-event ground truth and proposes a label-free structural metric instead.{cite:emlb} Section '
         '4.3 records which of these methods and datasets could be run fairly under a common ROC protocol.')
    heading(doc, '2.2. Unsupervised anomaly detection and point processes', 2)
    para(doc,
         'Unsupervised anomaly detection assumes a model of normal behaviour and flags observations that are '
         'improbable under it; classical reviews distinguish density-based, distance-based and '
         'reconstruction-based approaches and stress that calibration of the anomaly score to a false-alarm '
         'rate is as important as ranking accuracy;{cite:chandola,pimentel,ruff} for streaming video this has been '
         'pursued with an explicit asymptotic bound on the false-alarm rate.{cite:doshi} For a point process, the '
         'natural normal model is a Poisson process,{cite:kingman} and model-based learning on point-pattern data '
         'uses the same Poisson likelihood for classification and novelty detection;{cite:vo_ppp} the natural '
         'statistic is the probability of the observed count under that process. The present work applies this classical scheme to a stream '
         'in which the normal model differs from pixel to pixel and must be fitted online, and makes two '
         'additions that the review literature identifies as open: a calibrated score whose threshold is a '
         'stated false-alarm rate, and the reuse of the fitted normal model to parameterise other detectors.')

    # ---------------- 3 Method ----------------
    heading(doc, '3. Method')
    heading(doc, '3.1. Event stream and hypotheses', 2)
    para_math(doc, [
         'An event camera produces a time-ordered stream of events ', eq_event_inline, ', where (x_i, y_i) '
         'is the pixel address, t_i the timestamp in microseconds and p_i the polarity. We ignore polarity in '
         'the detector. For every event we test the null hypothesis H0 that the events in a small causal '
         'neighbourhood of e_i were produced by the pixel-wise BA process alone, against the alternative H1 '
         'that an additional source contributed to them. Under H0 we model the BA of pixel (x, y) as a '
         'homogeneous Poisson process with rate \u03bb_xy;{cite:kingman} the rates differ between pixels because '
         'leakage and hot-pixel behaviour do.{cite:nozaki} Fig. 1 summarises the pipeline.'])
    figure(doc, 'fig1_method.png',
           'Fig. 1. Event-driven Poisson likelihood-ratio detector. Each event is scored from the estimated '
           'background rate of its neighbourhood and the number of events that arrived in that neighbourhood '
           'during the preceding window W, which is stated as an expected background count k rather than a '
           'fixed number of milliseconds; the tail probability is used directly as the noise probability. Blue '
           'boxes: what the stream itself delivers without labels, the operating point at a requested false-alarm '
           'rate, a window W that carries across sensor models and can set the time constant of another filter, '
           'and a per-event cost without a voxel grid.', width=Inches(6.0))
    heading(doc, '3.2. Per-pixel background-rate estimation', 2)
    para_math(doc, [
         'The rate of each pixel is estimated from its own inter-event intervals. Let \u0394_xy(q) be the '
         'q-quantile of the intervals between successive events at pixel (x, y). For an exponential interval '
         'distribution with rate \u03bb the q-quantile is ', eq_quantile_inline, ', so'])
    add_display_equation(doc, jd.eq_rate, 1)
    para(doc,
         'is a consistent estimate of the BA rate. A high quantile is deliberately used: source events shorten '
         'a minority of the intervals at the pixels they cross, and a high quantile of the interval '
         'distribution is insensitive to that minority, whereas the mean interval is not. Pixels with fewer '
         'than four events receive the median rate of the array. The quantile q, the window W and the radius r '
         'introduced below are the only tuned parameters (Section 4.4).')
    heading(doc, '3.3. Event-driven Poisson tail test', 2)
    para(doc,
         'For event i let N_i be the number of events, including e_i itself, that arrived at most W '
         'microseconds earlier within the (2r + 1) x (2r + 1) pixel neighbourhood centred on (x_i, y_i):')
    add_display_equation(doc, jd.eq_count, 2)
    para(doc, 'Under H0 the count is Poisson with mean')
    add_display_equation(doc, jd.eq_lambda, 3)
    para(doc,
         'The likelihood ratio of H1 against H0 for a Poisson count with a larger alternative rate is monotone '
         'increasing in N_i, so by the Neyman-Pearson lemma thresholding N_i given \u039b_i is the most '
         'powerful test at any size, and the size attained by observing N_i is the upper tail probability{cite:kay}')
    add_display_equation(doc, jd.eq_tail, 4)
    para(doc,
         'P_i is reported as the noise probability of event i. Because \u039b_i differs between events, the '
         'comparison is made on the probability scale rather than on the raw count, which lets one threshold '
         'serve the whole array. The stream is processed in time order: a per-pixel ring of recent timestamps '
         'and a running pointer into the sorted stream give N_i in O((2r + 1)^2 + log n) operations per event, '
         'and the rate sum in Eq. (3) is a box filter over the rate map computed once; no voxel grid or dense '
         'frame is allocated. The implementation uses NumPy and Numba.{cite:numba}')
    heading(doc, '3.4. Self-calibrated operating point', 2)
    para(doc,
         'A consumer downstream of the detector typically tolerates a stated false-alarm rate \u03b1 rather '
         'than a stated threshold. Because P_i is a probability, a label-free operating point is obtained by '
         'asking the detector to pass exactly a fraction \u03b1 of the stream:')
    add_display_equation(doc, eq_threshold, 5)
    para(doc,
         'where Q_\u03b1 denotes the empirical \u03b1-quantile. If the anomalous fraction is small and the '
         'background model is adequate, the achieved false-alarm rate on true noise events is close to \u03b1. '
         'The same rule is applied to the comparators, but an integer neighbour count has few distinct values '
         'and cannot be cut at an arbitrary quantile, whereas a continuous probability can. The inequality is '
         'strict, so that tied scores at the quantile are not passed and the achieved rate stays at or below '
         '\u03b1; such ties arise for the proposed detector when \u039b_i is so large that P_i rounds to one, '
         'and the fraction of saturated scores is a label-free diagnostic that the window is too long for the '
         'background rate.')
    heading(doc, '3.5. Rate-adaptive window', 2)
    zc = N['zk_config']
    para(doc,
         'A window stated in milliseconds is a sensor-specific choice: the same W gives a background '
         'expectation \u039b_i that is several times larger on a sensor with a higher BA rate, and the tail '
         'probability saturates. The window is therefore also specified in a dimensionless form, as the '
         'expected number k of background events in the neighbourhood,')
    add_display_equation(doc, eq_window, 6)
    para(doc,
         'with the sum over the (2r + 1) x (2r + 1) neighbourhood of event i and the median over the events of '
         'the stream; W is clipped to [1 ms, 2 s]. The rate estimate is that of Section 3.2, so the rule uses '
         f'nothing but the target stream. The deployment configuration is r = {zc["radius"]}, '
         f'k = {zc["expected_count"]:g}, q = {zc["interval_quantile"]}. The value of k was fixed once, from the '
         f'trade-off between ranking accuracy and saturation over k in {{{", ".join(f"{x:g}" for x in N["zk_grid_k"])}}} '
         'on EBSSA (Section 5.6); it is a constant of the method, not a per-sensor setting, and Sections 4.6 '
         'and 4.2 test whether it carries over.')
    heading(doc, '3.6. Parameter hand-over and two-stage cascade', 2)
    hyb = N['hyb']
    para(doc,
         'The detector produces two label-free by-products: the per-pixel rate map and the rate-adaptive window '
         'W. In the hand-over, the time constant dt of the density filter YNoise, which counts the neighbours '
         'of an event that fired within dt and whose published default is dt = '
         f'{hyb["ynoise_default"]["dt_us"] / 1e3:g} ms with radius {hyb["ynoise_default"]["radius"]},{{cite:feng}} '
         f'is set equal to W and its radius to r = {hyb["stage1_config"]["radius"]}, per recording and without '
         'labels. In the two-stage cascade, the detector first passes the fraction f of the stream with the '
         'smallest noise probability (Eq. (5); if the strict quantile would pass fewer than half the requested '
         'number because of tied probabilities, the whole tied block is passed and the achieved fraction is '
         'reported), and YNoise is run on the passed events alone, so that its recent-event map and its cost '
         'see only that fraction. The two-stage score ranks rejected events (by stage-1 probability) below '
         'passed ones (by stage-2 density); its operating point is again a quantile of the stream.')

    # ---------------- 4 Experimental setup ----------------
    heading(doc, '4. Experimental setup')
    heading(doc, '4.1. EBSSA: two sensors, annotated sky recordings', 2)
    para(doc,
         'We used the labelled split of the EBSSA dataset,{cite:afshar} downloaded through the Tonic '
         'library.{cite:tonic} It contains recordings of RSOs and stars made with two event-camera models: '
         f'{N["n_small"]} recordings from a 180 x 240-pixel sensor and {N["n_large"]} from a 240 x 304-pixel '
         'sensor. Ground truth is the published object annotation: an event is labelled as object if it lies '
         'within a 10 x 10-pixel box around an annotated position and within 10 ms of its timestamp; all other '
         'events are labelled as background. For each recording the analysis window was restricted to the '
         f'annotated interval (plus 0.5 s on each side) and the central {N["max_events"]:,} events of that '
         f'window were kept, giving {N["n_events_total"]:,} events in total. Recordings with fewer than 50 '
         f'events in either class were excluded, leaving all {N["n_rec"]} labelled recordings. The median event '
         f'rate was {N["rate_median"] / 1e3:.1f} k events/s (range {N["rate_min"] / 1e3:.1f}-'
         f'{N["rate_max"] / 1e3:.1f}); the object fraction ranged from {pct(N["sig_min"], 2)} to '
         f'{pct(N["sig_max"])} (median {pct(N["sig_median"], 2)}). No synthetic data enter this evaluation.')
    heading(doc, '4.2. DND21: a third sensor with exact origin labels', 2)
    src = N['dnd_sources']
    rates = N['dnd_rates_hz']
    nsr = N['dnd_noise_source_rate']
    para(doc,
         'To test generalisation to a sensor, a scene type and a noise regime not seen in EBSSA, the label-free '
         'path was run unchanged on recordings of the DND21 benchmark of Guo and Delbruck,{cite:guo} made with '
         f'a DAVIS346 camera ({N["dnd_shape"][1]} x {N["dnd_shape"][0]} pixels; W x H). DND21 follows the standard '
         'protocol of the denoising literature: a signal recording nearly free of background activity is mixed '
         'with measured sensor noise, so the origin of every event, and hence its label, is exact. We built '
         'the mixtures ourselves from the public files. Signal '
         f'sources ({len(src)}): {"; ".join(f"{k}: {v}" for k, v in src.items())}; the two sparse synthetic '
         'targets are rendered with the v2e simulator{cite:v2e} with its noise models disabled and are the '
         'closest analogue in DND21 to the point-like transits of EBSSA. Noise sources (2): the measured DAVIS346 '
         f'recordings made with the lens capped (dark, {nsr.get("dark_1hz", nsr.get("dark_0.5hz", 0)):.1f} Hz per '
         f'pixel) and under uniform illumination (light, {nsr["light_native"]:.2f} Hz per pixel). The dark '
         'recording was thinned by independent Bernoulli sampling to nominal per-pixel rates of '
         f'{", ".join(f"{r:g}" for r in rates)} Hz, and the light recording was used at its native rate, giving '
         f'{len(N["dnd_conditions"])} noise conditions. From every signal source up to {N["dnd_n_segments"]} '
         f'evenly spaced windows of at most {N["dnd_segment_s"]:g} s were cut and each was paired with a distinct '
         'slice of the noise recording, so that no noise event is reused; the window was shortened where '
         f'necessary so that a mixture stays near {N["dnd_target_events"]:,} events, and mixtures were truncated '
         f'to {N["max_events"]:,} events. This gave {N["dnd_n_rec"]} mixtures of {N["dnd_events_min"]:,} to '
         f'{N["dnd_events_max"]:,} events ({N["dnd_events_total"]:,} in total), {N["dnd_dur_min"]:.2f}-'
         f'{N["dnd_dur_max"]:.2f} s long, with signal fractions from {pct(N["dnd_sig_min"], 2)} to '
         f'{pct(N["dnd_sig_max"])} (median {pct(N["dnd_sig_median"])}); the signal fraction varies by design, '
         'because the same signal segment is mixed with noise at every nominal rate. Cross-validation is '
         f'grouped by signal source (leave-one-scene-out, {N["dnd_n_sources"]} folds), so a tuned or trained '
         'comparator never sees the scene it is scored on. Three parameterisations are reported for every '
         'gridded method: nested selection on the other DND21 scenes; the configuration selected on EBSSA, '
         'applied unchanged (no DND21 labels used); and, for the proposal and YNoise, the fixed label-free '
         'deployment path of Sections 3.5 and 3.6. These mixtures are synthetic combinations of two real '
         'recordings, not native annotations of a natural scene, and are described as such throughout.')
    heading(doc, '4.3. Comparators, ablations and feasibility', 2)
    para(doc,
         'Supplementary Table S1 records, for each recent denoiser considered, its input and training '
         'requirements, whether public code exists and whether it could be run fairly under the common protocol '
         '(event-only input, exact or annotated labels, grouped cross-validation). Two supervised references '
         'were trained inside the folds with the labels of each dataset: an MLPF-style multilayer '
         'perceptron{cite:guo} and an EDnCNN-style convolutional network{cite:baldwin} on '
         f'{N["features"]["n_features"]}-dimensional time-surface patches (radius {N["features"]["patch_radius"]} '
         f'pixels, time constant {N["features"]["tau_us"] / 1e3:.0f} ms, {N["train_events_per_rec"]:,} events '
         'sampled per training recording); they are reimplementations trained on the labels available here, '
         'not the published weights. PFD was added on DND21 through a Python re-implementation of its PFD-A '
         'stage converted from a keep/reject rule into a ranking (the official C++ code assumes a 1280 x 720 '
         'array). AEDNet was run as a transfer test of a fixed model: its only released weights (a DVSCLEAN '
         'background-activity model for a 1280 x 720 sensor) were applied unchanged to both datasets on '
         'stratified event subsets, with the proposal and YNoise scored on the same subsets and on the full '
         'streams; the re-implemented patch construction reproduces the official loader and model on the '
         f'authors\' released sample ({N["aednet_parity"]["n_checked"]} events; maximum absolute probability '
         f'difference {N["aednet_parity"]["max_abs_probability_difference"]:g}; protocol in the supplementary '
         'material), and its results are reported separately (Section 5.9). No public code or weights of WedNet '
         'were located, so it is listed, not scored. DVSNOISE20 was not used because its labels are '
         'model-derived probability masks rather than exact origins, and E-MLB because it has no per-event '
         'ground truth.')
    para(supp,
         'AEDNet transfer protocol (Section 4.3 of the main text). The released weights were applied on the '
         'CPU with the sensor frame set to that of each recording (180 x 240 or 240 x 304 pixels for EBSSA, '
         f'{N["dnd_shape"][1]} x {N["dnd_shape"][0]} for DND21), the released neighbourhood '
         f'({N["aednet"]["released_hyperparameters"]["x_lim_px"]} x {N["aednet"]["released_hyperparameters"]["y_lim_px"]} '
         f'pixels, {N["aednet"]["released_hyperparameters"]["points_per_patch"]} events), the softmax noise '
         f'probability as a ranking score and a stratified random subset of at most {N["aednet"]["n_per_class"]:,} '
         f'signal and {N["aednet"]["n_per_class"]:,} background events per recording, since the CPU throughput of '
         'the network is tens of events per second. ROC-AUC does not depend on the class prior, so the subset '
         'AUC estimates the full-stream AUC. On the authors\' released sample the re-implemented patch '
         f'construction matched the official loader to a maximum absolute difference of '
         f'{N["aednet_parity"]["max_abs_patch_difference"]:g} in the patches and '
         f'{N["aednet_parity"]["max_abs_probability_difference"]:g} in the output probabilities '
         f'({N["aednet_parity"]["n_checked"]} events).')
    feas_rows = []
    for mm in N['feas_methods']:
        feas_rows.append([mm['name'], mm['type'], mm['input'], mm['training_labels'],
                          mm['extra_sensors_required'], mm['public_code'], mm['executed_here']])
    stable(supp,
          'Table S1. Comparator feasibility under the common protocol (event-only input, exact or annotated '
          'labels, grouped cross-validation). "Executed here" states whether the method was scored in this '
          'paper and on which dataset; caveats are given in the text and in results/comparator_feasibility.json.',
          ['Method', 'Type', 'Input', 'Training labels', 'Extra sensors', 'Public code', 'Executed here'],
          feas_rows, col_widths=[0.9, 1.0, 1.1, 1.0, 0.8, 0.9, 0.8], font_pt=8, landscape=True)
    para(doc,
         'On EBSSA, published unsupervised filters were re-implemented from their descriptions and their '
         'parameters selected by the same grouped cross-validation as those of the proposal, so that no '
         f'comparator is handicapped by author defaults chosen for other sensors ({n_pub} filters): the '
         'background-activity filter,{cite:delbruck2008} a nearest-neighbour filter,{cite:liu2015} an event bilateral filter, '
         'a motion-compensated proxy, kNoise,{cite:khodamoradi} the double-window filter (DWF){cite:guo} and '
         'YNoise.{cite:feng} Ablations isolate the two design choices of the proposal. A voxelised Poisson LR '
         'filter applies the same tail test to counts on a fixed time-bin x pixel grid, differing only in being '
         'frame-based. Event-driven forms of the bilateral and double-window filters use the same causal '
         'neighbourhood machinery as the proposal but replace the Poisson probability with the original '
         'heuristic score. Further event-driven alternatives (a gamma waiting-time test, a k-nearest-neighbour '
         'point-process test, a recursive rate tracker and a velocity-adaptive matched filter), a Fano-factor '
         f'overdispersion score{{cite:fano}} ({N["fano_bins"]} time bins; not causal) and a physics-informed '
         f'network (PI-DC-DVS, {N["pidc_bins"]} bins, {N["pidc_epochs"]} label-free epochs per recording) are '
         'reported at one fixed configuration each, since none has a published default; a multiscale variant '
         'combines the tail probabilities of three (r, W) scales with Fisher\'s method{cite:fisher} and is used '
         'only in the operating-point analysis. All configurations are listed in the code repository.')
    heading(doc, '4.4. Evaluation protocol', 2)
    para(doc,
         'The unit of analysis is the recording. Event-level ROC-AUC{cite:hanley} against the labels was computed per '
         'recording and summarised as mean and standard deviation (SD) over recordings; F1, noise-removal rate '
         '(NRR; fraction of background events with P_i of at least 0.5) and signal-preservation rate (SPR) are '
         'also reported on EBSSA. Tunable parameters of the proposed detector (r in '
         f'{{{", ".join(str(x) for x in N["grid_radii"])}}}, W in '
         f'{{{", ".join(f"{x:.0f}" for x in N["grid_windows_ms"])}}} ms, q in '
         f'{{{", ".join(str(x) for x in N["grid_quantiles"])}}}; {N["n_grid"]} combinations), of the voxelised '
         'ablation, of every published comparator and of the two event-driven ablations that share their form '
         f'(grids of {N["grid_size_min"]} to {N["grid_size_max"]} combinations) were selected by grouped '
         f'{N["n_folds"]}-fold cross-validation over recordings on EBSSA and by leave-one-scene-out '
         'cross-validation on DND21: the configuration with the highest mean AUC on the training folds was '
         'applied to the held-out fold, so every reported number for these methods is out of fold; the '
         'supervised networks used the same folds. The cross-validation gives every comparator its best fair '
         'configuration; in operation the proposed detector runs with one fixed configuration and sets its '
         'threshold from the false-alarm budget. Paired differences were tested '
         'with the two-sided Wilcoxon signed-rank test over recordings,{cite:wilcoxon} with Holm adjustment '
         f'within each family of comparisons ({len(tests)} on EBSSA).{{cite:holm}} Because a p-value alone does '
         'not convey the size of a difference, every paired difference is also given with a 95% percentile '
         f'bootstrap confidence interval ({N["es_n_boot"]:,} resamples){{cite:efron}} and, in the supplementary material, '
         'with the matched-pairs rank-biserial correlation{cite:kerby} as a standardised effect size. On DND21 the '
         f'{N["dnd_n_rec"]} mixtures are not independent (each signal segment is mixed with every noise '
         'condition, and only four signal sources exist). The mixture is retained as the unit of the primary '
         'test because the noise realisations differ, but the bootstrap resamples whole signal segments '
         f'({N["dnd_n_segment_clusters"]} clusters), each conclusion is checked at the segment level (mean AUC '
         f'over the noise conditions of one segment, paired Wilcoxon over {N["dnd_n_segment_clusters"]} '
         'segments), and the sign of the difference is reported per signal source without a test. Partial AUC below '
         'false-positive rates of 0.01 and 0.001 is reported in the standardised form of McClish,{cite:mcclish} '
         f'using scikit-learn.{{cite:sklearn}} The random seed was fixed at {N["seed"]}. Stratified results by '
         'sensor and by event rate were not pre-specified and are reported as exploratory.')
    heading(doc, '4.5. Cost versus sparsity', 2)
    para(doc,
         f'A real EBSSA recording ({N["max_events"]:,} events) was thinned by keeping a uniformly random fraction '
         f'f of its events, f in {{{", ".join(f"{x:g}" for x in N["keep_fractions"])}}}, while leaving the '
         'sensor array and the recording interval unchanged, so the voxel grid of the frame-based methods '
         'keeps its size; thinning a Poisson process yields a Poisson process.{cite:kingman} Wall-clock time '
         f'and peak Python-level memory were recorded over {N["cost_repeats"]} repeats after a warm-up call on '
         'a single processor core, and a cost exponent \u03b2 was fitted by least squares on log-log axes:')
    add_display_equation(doc, jd.eq_cost, 7)
    para(doc,
         'An exponent near one means cost proportional to the number of events; near zero, cost fixed by the '
         'grid. The timings indicate scaling, not absolute throughput.')
    heading(doc, '4.6. Zero-knowledge protocol on EBSSA', 2)
    zks = N['zk']
    sens = list(zks['sensors'])
    para(doc,
         'The cross-validation of Section 4.4 still lets each method see labelled recordings from both sensor '
         'models. To emulate a new instrument, the two models were treated as source and target '
         f'({zks["sensors"][sens[0]]} and {zks["sensors"][sens[1]]} recordings) in both directions. '
         '(A) Configuration transfer: the configuration with the highest mean AUC on the source sensor was '
         'applied unchanged to the target, and the AUC lost relative to the best configuration on the target '
         'itself was recorded (an optimistic, label-selected reference). (B) No tuning: every method was run at '
         'one fixed configuration (publication defaults for the comparators; fixed-window and rate-adaptive '
         'forms of the proposal). (C) Threshold transfer: for a requested budget \u03b1 in '
         f'{{{", ".join(f"{a:g}" for a in zks["alphas"])}}} a numerical threshold fixed on the source sensor was '
         'applied to the target recordings and compared with the label-free recalibration of Eq. (5) on each '
         'target stream. With two sensor models the transfer directions are two case studies, which is why '
         'the third-sensor evaluation of Section 4.2 was added.')
    heading(doc, '4.7. Hand-over and cascade protocol', 2)
    para(doc,
         'On EBSSA, YNoise was run on the whole stream with dt = W (hand-over) and compared with its published '
         'default and with its label-tuned cross-validated value; the two-stage cascade was run for f in '
         f'{{{", ".join(f"{x:g}" for x in hyb["screen_fractions"])}}} with stage 2 parameterised by the hand-over, '
         'by the published default and by a pseudo-label choice (the grid point that best separated the passed '
         'from the rejected events; labels not used). We report AUC, achieved false-positive and detection '
         'rates at the budgets of Section 3.4 and the wall-clock time of each stage relative to YNoise on the '
         'whole stream, with Wilcoxon tests on paired per-recording AUC. For a visual check, one recording per '
         'sensor model was selected by a fixed rule (stage-1 AUC closest to the sensor median; shown in the '
         'supplementary material). On DND21 the same hand-over and the cascade with f in '
         f'{{{", ".join(f"{x:g}" for x in N["dnd_screen_fractions"])}}} were run unchanged.')

    # ---------------- 5 Results ----------------
    heading(doc, '5. Results')
    heading(doc, '5.1. Detection performance on EBSSA', 2)
    pub = ['bilateral', 'ynoise', 'motion', 'temporal', 'dwf', 'nearest', 'knoise']
    pdf = zks['published_defaults']
    ns_pub = [k for k in pub if tests[k]['p_holm'] >= 0.05]
    better_pub = [k for k in pub if tests[k]['p_holm'] < 0.05 and tests[k]['auc_diff_mean'] < 0]
    worse_pub = [k for k in pub if tests[k]['p_holm'] < 0.05 and tests[k]['auc_diff_mean'] > 0]

    def cmp_list(keys):
        return ', '.join(f'{short(k)} {auc(N, k)} ({tests[k]["auc_diff_mean"]:+.3f}, p {pfmt(tests[k]["p_holm"])})'
                         for k in keys)

    para(doc,
         f'Table 1 lists the mean AUC of every method over the {N["n_rec"]} recordings, and Fig. 2 shows the '
         f'same values with their spread. The proposed detector reached an AUC of {auc_sd(N, "edlr")}, '
         f'{es_e["ynoise"]["mean_diff"]:+.3f} (95% CI {ci(es_e["ynoise"])}) from label-tuned YNoise and '
         f'{es_e["edncnn"]["mean_diff"]:+.3f} (95% CI {ci(es_e["edncnn"])}) from the EDnCNN-style network. With '
         f'every published filter tuned by the same grouped cross-validation, {len(ns_pub)} of the {len(pub)} '
         'were statistically indistinguishable from it (mean paired difference of the proposal minus the '
         f'comparator and Holm-adjusted p: {cmp_list(ns_pub)}), {len(better_pub)} '
         f'{"was" if len(better_pub) == 1 else "were"} significantly higher ({cmp_list(better_pub)}) and '
         f'{len(worse_pub)} were significantly lower ({cmp_list(worse_pub)}). The supervised networks were '
         f'higher still: MLPF-style {auc(N, "mlpf")} and EDnCNN-style {auc(N, "edncnn")} (differences '
         f'{tests["mlpf"]["auc_diff_mean"]:+.3f} and {tests["edncnn"]["auc_diff_mean"]:+.3f}; Holm-adjusted p '
         f'{pfmt(tests["mlpf"]["p_holm"])} and p {pfmt(tests["edncnn"]["p_holm"])}). The unsupervised detector '
         'alone is therefore in the group of the stronger heuristic filters rather than above it: when the '
         'comparators are given labels to tune their time constants and radii, the best of them, YNoise, '
         'exceeds it, and the label-trained networks exceed both (standardised effect sizes in Supplementary '
         'Table S2). The column "AUC, no labels" of Table 1 and the open circles of Fig. 2 give the other side: at '
         f'one fixed configuration chosen without labels, the rate-adaptive proposal reached {fmt(pdf["edlr_adaptive"]["auc_mean"])} '
         f'against {fmt(pdf["ynoise"]["auc_mean"])} for YNoise and {fmt(pdf["bilateral"]["auc_mean"])} for the '
         'bilateral filter at their published defaults (Section 5.6). Sections 5.5-5.7 show what the detector adds '
         'to this picture without labels.')
    es_rows = []
    for k in ORDER:
        e = es_e.get(k)
        if e is None:
            continue
        es_rows.append([label(k), f"{e['mean_diff']:+.3f}", f"{e['median_diff']:+.3f}", ci(e),
                        f"{e['n_a_better']}/{e['n']}", f"{e['rank_biserial']:+.2f}"])
    stable(supp,
           f'Table S2. Effect sizes of the paired comparison on EBSSA ({N["n_rec"]} recordings): mean and median '
           'paired \u0394AUC of the proposed fixed-window detector minus each method, 95% percentile bootstrap CI '
           f'({N["es_n_boot"]:,} resamples of recordings), number of recordings on which the proposal is ahead, and '
           'matched-pairs rank-biserial correlation r (\u22121 to +1; positive favours the proposal).',
           ['Method', 'Mean \u0394AUC', 'Median \u0394AUC', '95% CI', 'Proposal ahead', 'r'],
           es_rows, col_widths=[2.4, 0.8, 0.8, 1.2, 0.9, 0.5], font_pt=8)

    def row(k):
        mm = m[k]
        t = tests.get(k)
        e = es_e.get(k)
        return [label(k), 'training' if mm['supervised'] else 'tuning', auc_sd(N, k),
                fmt(pdf[k]['auc_mean']) if k in pdf else '-', fmt(mm['f1']['mean']),
                fmt(mm['nrr']['mean']), fmt(mm['spr']['mean']),
                '-' if t is None else f"{t['auc_diff_mean']:+.3f}",
                '-' if e is None else ci(e),
                '-' if t is None else (f"{t['p_holm']:.3f}" if t['p_holm'] >= 0.001 else '<0.001')]

    order = ORDER
    table(doc,
          f'Table 1. Event-level detection performance on the {N["n_rec"]} labelled EBSSA recordings (mean over '
          'recordings; AUC also with SD). Labels used: how the labels entered the main AUC, F1, NRR and SPR columns, '
          'to tune the configuration by grouped cross-validation (tuning) or to train the model (training); no '
          'method in these columns is label-free. AUC, no labels: mean AUC of the same method at one fixed '
          'configuration chosen without labels (the published default of each filter, the deployment configuration '
          'of the proposal; Section 5.6), where such a configuration exists. \u0394AUC is the mean paired difference '
          'of the proposed detector minus the comparator, both label-tuned, with its 95% bootstrap confidence '
          'interval (CI); p is the Holm-adjusted two-sided Wilcoxon signed-rank p-value. NRR: noise-removal '
          'rate; SPR: signal-preservation rate at a probability threshold of 0.5. Rows are grouped as proposed '
          '(fixed window; rate-adaptive window), published unsupervised filters, event-driven ablations, '
          'frame-based and label-free learned ablations, and supervised references.',
          ['Method', 'Labels used', 'AUC (mean \u00b1 SD)', 'AUC, no labels', 'F1', 'NRR', 'SPR', '\u0394AUC', '95% CI',
           'p (Holm)'],
          [row(k) for k in order], col_widths=[2.25, 0.6, 1.05, 0.6, 0.5, 0.5, 0.5, 0.6, 1.35, 0.5],
          font_pt=7.5, landscape=True)
    figure(doc, 'fig2_methods_auc.png',
           f'Fig. 2. Mean ROC-AUC with SD over the {N["n_rec"]} EBSSA recordings for all methods in Table 1. '
           'Bars: configuration tuned on labels by grouped cross-validation (supervised networks: trained). Open '
           'circles: the same method at one fixed configuration chosen without labels (published default; '
           'deployment configuration of the proposal), where one exists. Dashed line: the proposed rate-adaptive detector '
           'without labels; dotted line: chance. Colours group the proposed method, published unsupervised '
           'event filters, event-driven ablations, frame-based and label-free learned ablations, and supervised '
           'networks.', width=Inches(4.8))
    para(doc,
         'Fig. 3 shows the paired per-recording comparison. The proposed detector was above the tuned event '
         f'bilateral filter on {N["n_unsup_edlr_better"]} of {N["n_rec"]} recordings, above tuned YNoise on '
         f'{N["n_edlr_better_ynoise"]}, and above its own voxelised form on {N["n_edlr_better_plr"]}. '
         'Recording-to-recording variation was large for every method, and the two sensor models behaved '
         'differently (Section 5.3), which is why the recording rather than the event is the statistical unit.')
    figure(doc, 'fig3_paired.png',
           'Fig. 3. Per-recording ROC-AUC of the proposed detector against (a) the event bilateral filter, (b) '
           'YNoise, (c) its voxelised, frame-based form and (d) the supervised MLPF-style network. Circles: '
           '180 x 240-pixel sensor; squares: 240 x 304-pixel sensor. Points above the diagonal favour the '
           f'proposed detector. \u0394AUC and Holm-adjusted p refer to the paired Wilcoxon test over {N["n_rec"]} '
           'recordings.', width=Inches(4.2))

    heading(doc, '5.2. Ablations', 2)
    para(doc,
         f'Replacing the event-driven neighbourhood with a voxel grid lowered AUC from {auc(N, "edlr")} to '
         f'{auc(N, "plr")} (difference {tests["plr"]["auc_diff_mean"]:+.3f}, Holm-adjusted p = '
         f'{tests["plr"]["p_holm"]:.4f}), because fixed time bins split tracks across bin boundaries and the '
         'cross-validated bin count is a compromise across recordings with very different event rates. '
         'Replacing the Poisson probability with a heuristic score while keeping the event-driven neighbourhood '
         f'made no significant difference for the bilateral weight ({auc(N, "bilateral_ed")}, p = '
         f'{tests["bilateral_ed"]["p_holm"]:.2f}) but degraded the double-window rule ({auc(N, "dwf_ed")}). The '
         f'other event-driven alternatives were significantly worse ({auc(N, "knn_pp")} to {auc(N, "recursive")}). '
         f'The Fano-factor score reached {auc(N, "fano")}, close to chance, and the physics-informed network '
         f'{auc(N, "pi_dc_dvs")} at about {N["runtime"]["pi_dc_dvs"]["mean"] / N["runtime"]["edlr"]["mean"]:.0f} '
         'times the runtime. The probability output therefore matters mainly for calibration (Section 5.5); the '
         'event-driven neighbourhood matters for both accuracy and cost. The rate-adaptive window, '
         f'cross-validated over k, reached {auc(N, "edlr_adaptive")} (difference from the fixed window '
         f'{tests["edlr_adaptive"]["auc_diff_mean"]:+.3f}, Holm-adjusted p {pfmt(tests["edlr_adaptive"]["p_holm"])}).')

    heading(doc, '5.3. Stratified results', 2)
    st = N['strata']
    strata_rows = []
    for key, name in (('sensor_180x240', '180 x 240-pixel sensor'), ('sensor_240x304', '240 x 304-pixel sensor'),
                      ('activity_low', 'Event rate below median'), ('activity_high', 'Event rate above median')):
        s = st[key]
        strata_rows.append([name, str(s['n_recordings'])] +
                           [fmt(s[k]['mean']) for k in ('edlr', 'bilateral', 'ynoise', 'plr', 'mlpf', 'edncnn')])

    def swing(k):
        return abs(st['activity_high'][k]['mean'] - st['activity_low'][k]['mean'])

    def gap(stratum, k):
        return st[stratum]['edlr']['mean'] - st[stratum][k]['mean']

    n_strata = sorted(st[k]['n_recordings'] for k in ('sensor_180x240', 'sensor_240x304', 'activity_low',
                                                        'activity_high'))
    para(doc,
         'Supplementary Table S3 stratifies the main comparison. On the 180 x 240-pixel sensor the proposed detector '
         f'({fmt(st["sensor_180x240"]["edlr"]["mean"])}) was {gap("sensor_180x240", "bilateral"):+.3f} from the '
         f'event bilateral filter and {gap("sensor_180x240", "ynoise"):+.3f} from YNoise; on the 240 x 304-pixel '
         f'sensor ({fmt(st["sensor_240x304"]["edlr"]["mean"])}) the gaps were {gap("sensor_240x304", "bilateral"):+.3f} '
         f'and {gap("sensor_240x304", "ynoise"):+.3f}. Across the event-rate split the proposed detector moved by '
         f'{swing("edlr"):.3f} AUC, the bilateral filter by {swing("bilateral"):.3f} and YNoise by '
         f'{swing("ynoise"):.3f}. These strata are exploratory: they contain {n_strata[0]} to {n_strata[-1]} '
         'recordings each and were not pre-specified.')
    stable(supp,
          'Table S3. Mean ROC-AUC on EBSSA by sensor model and by event-rate stratum (split at the median rate of '
          f'{st["activity_low"]["median_event_rate_hz"] / 1e3:.1f} k events/s). Supervised networks for reference.',
          ['Stratum', 'n', 'Proposed', 'Bilateral', 'YNoise', 'Voxelised LR', 'MLPF-style', 'EDnCNN-style'],
          strata_rows, col_widths=[1.9, 0.4, 0.8, 0.8, 0.8, 0.9, 0.8, 0.9], font_pt=8, landscape=True)

    heading(doc, '5.4. Cost versus sparsity', 2)
    cs = N['cost']['scaling']
    cost_rows = []
    for k in ('edlr', 'edlr_zk', 'bilateral_ed', 'ynoise', 'recursive', 'plr', 'bilateral', 'temporal'):
        s = cs[k]
        cost_rows.append([('Event-driven Poisson LR, zero-knowledge form' if k == 'edlr_zk'
                           else label(k).replace(' (proposed)', '').replace(' (frame-based ablation)', '')),
                          s['family'], f"{s['cost_exponent_mean']:.2f} \u00b1 {s['cost_exponent_std']:.2f}",
                          f"{s['seconds_dense'] * 1e3:.1f}", f"{s['seconds_sparse'] * 1e3:.2f}",
                          f"{s['ns_per_event_dense']:.0f}", f"{s['ns_per_event_sparse']:.0f}",
                          f"{s['peak_bytes_dense'] / 1e6:.1f}", f"{s['peak_bytes_sparse'] / 1e6:.2f}"])
    para(doc,
         'Supplementary Fig. S1 and Supplementary Table S4 show the cost claim. The wall-clock time of the proposed detector fell with the '
         f'number of events with an exponent of {cs["edlr"]["cost_exponent_mean"]:.2f}: from '
         f'{cs["edlr"]["seconds_dense"] * 1e3:.0f} ms on the full stream to {cs["edlr"]["seconds_sparse"] * 1e3:.1f} '
         f'ms at one percent of the events, with peak memory falling from {cs["edlr"]["peak_bytes_dense"] / 1e6:.1f} '
         f'to {cs["edlr"]["peak_bytes_sparse"] / 1e6:.1f} MB. The voxelised form of the same test had an exponent '
         f'of {cs["plr"]["cost_exponent_mean"]:.2f}: its time stayed at about {cs["plr"]["seconds_dense"]:.1f} s and '
         f'its memory at {cs["plr"]["peak_bytes_dense"] / 1e6:.0f} MB regardless of sparsity, so that at one '
         f'percent of the events it was {cs["plr"]["seconds_sparse"] / cs["edlr"]["seconds_sparse"]:.0f} times '
         f'slower and spent {cs["plr"]["ns_per_event_sparse"] / 1e3:.0f} microseconds per event against '
         f'{cs["edlr"]["ns_per_event_sparse"] / 1e3:.2f} microseconds. The frame-based bilateral and background-activity '
         f'filters showed the same plateau (exponents {cs["bilateral"]["cost_exponent_mean"]:.2f} and '
         f'{cs["temporal"]["cost_exponent_mean"]:.2f}), while the event-driven comparators scaled like the '
         f'proposal (YNoise {cs["ynoise"]["cost_exponent_mean"]:.2f}, event-driven bilateral '
         f'{cs["bilateral_ed"]["cost_exponent_mean"]:.2f}). The zero-knowledge form, which additionally estimates '
         f'the rate map and chooses its own window, cost {cs["edlr_zk"]["ns_per_event_dense"]:.0f} ns per event '
         f'on the full stream (exponent {cs["edlr_zk"]["cost_exponent_mean"]:.2f}).')
    sfigure(supp, 'fig4_sparsity_cost.png',
           'Fig. S1. Computational cost as the real EBSSA stream is thinned. (a) Wall-clock time per recording '
           f'and (b) time per event, medians over {N["cost_repeats"]} repeats, against the fraction of events '
           'kept (array and recording interval unchanged). Solid lines: event-driven methods; dashed lines: '
           'frame- or voxel-based methods. Legend entries give the fitted cost exponent \u03b2 of Eq. (7).',
           width=Inches(6.0))
    stable(supp,
          'Table S4. Cost-scaling summary from Fig. S1. Exponent: mean \u00b1 SD of \u03b2 over repeats. Dense: all '
          'events; sparse: one percent of events. Memory is the peak Python-level allocation.',
          ['Method', 'Family', 'Exponent \u03b2', 'Time dense (ms)', 'Time sparse (ms)', 'ns/event dense',
           'ns/event sparse', 'Memory dense (MB)', 'Memory sparse (MB)'],
          cost_rows, col_widths=[1.5, 0.75, 0.8, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6], font_pt=7, landscape=True)

    heading(doc, '5.5. Self-calibrated operating points', 2)
    ops_rows = []
    for k in ('edlr', 'multiscale', 'ynoise', 'bilateral_ed'):
        r_ = [label(k) if k in m else 'Multiscale Fisher combination (proposed, 3 scales)']
        for a in N['alphas']:
            v = sc[k][f'{a:g}']
            r_ += [f"{v['fpr_median']:.4f}", f"{v['tpr_median']:.3f}"]
        ops_rows.append(r_)

    def budget_phrase(k):
        parts = []
        for a in N['alphas']:
            f = sc[k][f'{a:g}']['fpr_median']
            parts.append(f'{f:.4f}' + ('' if f <= a else f' ({(f / a - 1) * 100:.0f}% over)'))
        return ', '.join(parts)

    para(doc,
         'Fig. 4 and Table 2 report the label-free operating points of Eq. (5), with every comparator at its '
         f'cross-validated configuration. For requested false-alarm budgets of {", ".join(f"{a:g}" for a in N["alphas"])} '
         f'the proposed detector achieved median false-positive rates of {budget_phrase("edlr")} on the true '
         f'background events, i.e. it stayed within budget at every level, as did the multiscale variant '
         f'({budget_phrase("multiscale")}). YNoise, whose score is an integer density, gave {budget_phrase("ynoise")}: '
         'the quantile falls inside a tie and every tied event is passed. The event-driven bilateral score gave '
         f'{budget_phrase("bilateral_ed")} but detected {sc["bilateral_ed"]["0.01"]["tpr_median"]:.3f} of the object '
         f'events at a requested 0.01. At a requested 0.01 the median detection rate was '
         f'{sc["edlr"]["0.01"]["tpr_median"]:.3f} for the proposed detector and {sc["ynoise"]["0.01"]["tpr_median"]:.3f} '
         f'for YNoise, and the partial AUC below 0.01 was {pa["edlr"]["p01"]:.3f} against {pa["ynoise"]["p01"]:.3f} '
         f'(below 0.001: {pa["edlr"]["p001"]:.3f} against {pa["ynoise"]["p001"]:.3f}). Where YNoise is tuned on labels '
         'it detects more object events at these budgets; the point of this section is that with one fixed '
         'configuration and no labels the proposed detector met the requested budget at every level, because '
         'its score is a continuous probability without the ties of a density count.')
    figure(doc, 'fig5_calibration.png',
           'Fig. 4. Self-calibrated operating points and low-false-positive performance on EBSSA. (a) Median '
           'achieved false-positive rate on background events against the requested budget \u03b1 when each score '
           'is cut at its own \u03b1-quantile (Eq. (5)); dotted line: ideal calibration. (b) Median detection '
           'rate of object events at the same budgets. (c) Standardised partial AUC below false-positive rates '
           'of 0.01 and 0.001 (0.5 is chance).', width=Inches(6.0))
    table(doc,
          'Table 2. Median achieved false-positive rate (FPR) and detection rate (TPR) over EBSSA recordings when '
          'each detector is cut at the \u03b1-quantile of its own score, without labels.',
          ['Method'] + [f'FPR (\u03b1 = {a:g})' if i % 2 == 0 else f'TPR (\u03b1 = {a:g})'
                        for a in N['alphas'] for i in (0, 1)],
          ops_rows, col_widths=[2.0] + [0.7] * 6, font_pt=8)

    heading(doc, '5.6. Zero-knowledge deployment across the two EBSSA sensors', 2)
    tr = zks['cross_sensor_transfer']
    dfl = zks['published_defaults']
    tt = zks['threshold_transfer']
    dirs = list(tr)
    d01, d10 = dirs

    def dname(d):
        return d.replace('x', ' x ').replace('->', ' to ')

    zk_rows = []
    for k, nm in (('edlr', 'Proposed, fixed window'), ('edlr_adaptive', 'Proposed, rate-adaptive window'),
                  ('ynoise', 'YNoise'), ('bilateral', 'Event bilateral (frame-based)'),
                  ('bilateral_ed', 'Event bilateral (event-driven)'), ('dwf', 'Double-window filter'),
                  ('knoise', 'kNoise'), ('temporal', 'Background-activity filter'),
                  ('plr', 'Voxelised Poisson LR')):
        zk_rows.append([nm, fmt(dfl[k]['auc_mean'])]
                       + [fmt(tr[d][k]['auc_transferred']) + f" ({-tr[d][k]['drop']:+.3f})" for d in dirs])
    sat = zks['saturation']

    def sat_at(key, cfg, sensor):
        return sat[key][json.dumps(cfg, sort_keys=True)][sensor]['frac_saturated_median']

    fixed_cfg = dfl['edlr']['config']
    k_curve = {}
    for c, v in sat['edlr_adaptive'].items():
        cfg = json.loads(c)
        if cfg['radius'] == zc['radius'] and cfg['interval_quantile'] == zc['interval_quantile']:
            k_curve[cfg['expected_count']] = v
    ks = sorted(k_curve)
    k_best = {s: max(ks, key=lambda k: k_curve[k][s]['auc_mean']) for s in sens}
    k_next = ks[ks.index(zc['expected_count']) + 1]
    dense = sens[1]
    para(doc,
         'Fig. 5 and Supplementary Table S5 report the protocol of Section 4.6. Without any tuning (protocol B), the '
         f'fixed-window proposal reached {fmt(dfl["edlr"]["auc_mean"])} and the rate-adaptive form '
         f'{fmt(dfl["edlr_adaptive"]["auc_mean"])}, against {fmt(dfl["ynoise"]["auc_mean"])} for YNoise at its '
         f'published defaults and {fmt(dfl["bilateral"]["auc_mean"])} for the bilateral filter; the advantage of '
         f'YNoise in Table 1 ({auc(N, "ynoise")}) therefore rests on its labelled tuning. Configuration transfer '
         '(protocol A) exposed the weakness of a window stated in milliseconds: the configuration selected on '
         f'the {dname(d01).split(" to ")[0]}-pixel sensor (W = {tr[d01]["edlr"]["config_from_source"]["window_us"] / 1e3:.0f} '
         f'ms) lost {tr[d01]["edlr"]["drop"]:.3f} AUC on the other sensor, and the reverse transfer lost '
         f'{tr[d10]["edlr"]["drop"]:.3f}, because the denser sensor drives the tail probability into saturation '
         f'(median fraction of scores equal to one {pct(sat_at("edlr", fixed_cfg, dense), 0)} for the fixed '
         f'configuration on the {dense.replace("x", " x ")}-pixel sensor against '
         f'{pct(sat_at("edlr", fixed_cfg, sens[0]), 1)} on the other). The rate-adaptive window lost '
         f'{tr[d01]["edlr_adaptive"]["drop"]:.3f} and {tr[d10]["edlr_adaptive"]["drop"]:.3f}: stated as a count, '
         'the window carried over to a sensor with a different background rate. Fig. 5(a) shows the trade-off '
         f'behind k: mean AUC peaked at k = {k_best[sens[0]]:g} on the {sens[0].replace("x", " x ")}-pixel sensor '
         f'and at k = {k_best[sens[1]]:g} on the {sens[1].replace("x", " x ")}-pixel sensor, while the median '
         f'saturated fraction on the denser sensor was {pct(sat_at("edlr_adaptive", zc, dense), 0)} at k = '
         f'{zc["expected_count"]:g} and {pct(k_curve[k_next][dense]["frac_saturated_median"], 0)} at k = {k_next:g}, '
         f'so k = {zc["expected_count"]:g} is the longest window that keeps the probability scale usable on both.')
    figure(doc, 'fig6_zero_knowledge.png',
           'Fig. 5. Zero-knowledge deployment on EBSSA. (a) Mean AUC (red) and median fraction of saturated scores '
           '(grey) of the rate-adaptive proposal against the dimensionless window k on the two sensor models; '
           'dotted line: deployment value. (b) AUC lost when the configuration selected on one sensor is applied '
           'to the other. (c) Median achieved false-positive rate on the target sensor with a threshold carried '
           'over from the other sensor (dashed) and recalibrated on the target stream without labels (solid); '
           'dotted line: ideal calibration.', width=Inches(6.0))
    stable(supp,
          f'Table S5. Zero-knowledge evaluation on EBSSA. No tuning: mean AUC over all {N["n_rec"]} recordings at '
          'one fixed configuration (publication defaults for the comparators). Transfer: mean AUC on the target '
          'sensor with the configuration selected on the source sensor, and in parentheses the AUC lost relative '
          'to the best configuration on the target itself (negative values are losses).',
          ['Method', 'No tuning (all recordings)'] + [f'Transfer {dname(d)}' for d in dirs],
          zk_rows, col_widths=[2.3, 1.3, 1.5, 1.5], font_pt=8)
    a_mid = f'{zks["alphas"][1]:g}'
    para(doc,
         'Threshold transfer (protocol C, Fig. 5(c)) shows why the operating point must be recalibrated on the '
         f'target stream. A threshold fixed on the {dname(d10).split(" to ")[0]}-pixel sensor for a requested '
         f'{a_mid} and applied to the other gave a median false-positive rate of '
         f'{tt[d10]["edlr_adaptive"][a_mid]["transferred"]["fpr_median"]:.3f} for the rate-adaptive proposal and '
         f'{tt[d10]["ynoise"][a_mid]["transferred"]["fpr_median"]:.4f} for YNoise; in the opposite direction the '
         f'transferred thresholds passed almost nothing ({tt[d01]["edlr_adaptive"][a_mid]["transferred"]["fpr_median"]:.4f} '
         f'and {tt[d01]["ynoise"][a_mid]["transferred"]["fpr_median"]:.4f}). Recalibrating on the target stream with '
         f'Eq. (5) brought the rate-adaptive proposal to {tt[d01]["edlr_adaptive"][a_mid]["self_calibrated_on_target"]["fpr_median"]:.4f} '
         f'and {tt[d10]["edlr_adaptive"][a_mid]["self_calibrated_on_target"]["fpr_median"]:.4f} in the two directions, '
         f'with detection rates of {tt[d01]["edlr_adaptive"][a_mid]["self_calibrated_on_target"]["tpr_median"]:.3f} and '
         f'{tt[d10]["edlr_adaptive"][a_mid]["self_calibrated_on_target"]["tpr_median"]:.3f}. The three protocols '
         'separate what is knowledge-free in the proposal: the threshold is, on the target stream; the window is, '
         'once stated as an expected count; the radius and k are constants chosen once on this dataset, whose '
         'transfer to a third sensor is tested in Section 5.8.')

    heading(doc, '5.7. Parameter hand-over and two-stage cascade on EBSSA', 2)
    hy = N['hyb']
    yf = hy['ynoise_full']
    ps = hy['per_sensor']
    scr = hy['screen']
    f_keys = list(scr)
    f_mid, f_hi = f_keys[2], f_keys[-1]
    ps_names = list(ps)
    para(doc,
         'Table 3 and Fig. 6 report the hand-over. Setting the YNoise time constant to the rate-adaptive window '
         f'of the proposal, per recording and without labels, raised its AUC over all {hy["n_recordings"]} '
         f'recordings from {fmt(yf["default"]["auc"]["mean"])} at the published default to '
         f'{fmt(yf["handoff"]["auc"]["mean"])} (Wilcoxon p = {yf["handoff"]["vs_default"]["p_raw"]:.1e}), which is '
         f'{pct(hand_frac, 1)} of the {fmt(hy["ynoise_cv_reference"]["auc_mean"])} that label-tuned cross-validation '
         f'reached in Table 1, and above the zero-knowledge proposal itself ({fmt(hy["stage1"]["auc"]["mean"])}, '
         f'p = {yf["handoff"]["vs_stage1"]["p_raw"]:.1e}). The gain held on both sensor models '
         f'({fmt(ps[ps_names[0]]["ynoise_default_auc"]["mean"])} to {fmt(ps[ps_names[0]]["ynoise_handoff_auc"]["mean"])} '
         f'and {fmt(ps[ps_names[1]]["ynoise_default_auc"]["mean"])} to {fmt(ps[ps_names[1]]["ynoise_handoff_auc"]["mean"])}), '
         f'where the handed-over windows had medians of {ps[ps_names[0]]["window_ms"]["median"]:.0f} and '
         f'{ps[ps_names[1]]["window_ms"]["median"]:.0f} ms. The tuning that YNoise needed to reach its Table 1 '
         'value therefore did not have to come from labels: a time constant read from the background rate of '
         'the target stream closed most of the gap.')
    hyb_rows = [['Proposed, zero-knowledge form (stage 1 alone)', fmt(hy['stage1']['auc']['mean']),
                 fmt(ps[ps_names[0]]['stage1_auc']['mean']), fmt(ps[ps_names[1]]['stage1_auc']['mean']), 'n/a', 'n/a'],
                ['YNoise, published default', fmt(yf['default']['auc']['mean']),
                 fmt(ps[ps_names[0]]['ynoise_default_auc']['mean']), fmt(ps[ps_names[1]]['ynoise_default_auc']['mean']),
                 'n/a', '1.00'],
                ['YNoise, dt = W handed over', fmt(yf['handoff']['auc']['mean']),
                 fmt(ps[ps_names[0]]['ynoise_handoff_auc']['mean']), fmt(ps[ps_names[1]]['ynoise_handoff_auc']['mean']),
                 'n/a', '1.00'],
                ['YNoise, label-tuned CV (Table 1)', fmt(hy['ynoise_cv_reference']['auc_mean']), 'n/a', 'n/a', 'n/a', '1.00']]
    for fk in f_keys:
        e = scr[fk]
        hyb_rows.append([f'Two-stage, f = {fk}, stage 2 dt = W', fmt(e['handoff']['auc']['mean']), 'n/a', 'n/a',
                         f"{e['signal_recall']['mean']:.2f}", f"{e['handoff']['stage2_time_over_ynoise_full']['median']:.2f}"])
    table(doc,
          f'Table 3. Parameter hand-over and two-stage cascade on all {hy["n_recordings"]} EBSSA recordings. AUC: '
          'mean over recordings (pooled and per sensor model). Recall: fraction of object events passed by stage '
          '1. Stage-2 time: median wall-clock time of YNoise on the passed events relative to YNoise on the whole '
          'stream. No labels are used by any row except the label-tuned reference.',
          ['Configuration', 'AUC, all', f'AUC, {dname(ps_names[0])}', f'AUC, {dname(ps_names[1])}',
           'Recall of stage 1', 'Stage-2 time'],
          hyb_rows, col_widths=[2.6, 0.8, 0.9, 0.9, 0.9, 0.8], font_pt=8)
    figure(doc, 'fig7_hybrid.png',
           'Fig. 6. Parameter hand-over and two-stage cascade on EBSSA. (a) Mean AUC of the zero-knowledge '
           'proposal, of YNoise at its published default and of YNoise with dt set to the rate-adaptive window W '
           'handed over from the proposal, pooled and per sensor model; dotted line: YNoise with label-tuned '
           'cross-validation (Table 1). (b) Mean AUC of the two-stage score against the fraction of the stream '
           'passed by stage 1, with stage 2 parameterised by the hand-over, the published default and a '
           'pseudo-label choice; dashed line: stage 1 alone; black squares (right axis): median stage-2 time '
           'relative to YNoise on the whole stream.', width=Inches(6.0))
    a_mid = f'{hy["alphas"][1]:g}'
    para(doc,
         'The cascade (Fig. 6(b)) improved on stage 1 alone by a margin that grew with the passed fraction: from '
         f'{fmt(hy["stage1"]["auc"]["mean"])} to {fmt(scr[f_mid]["handoff"]["auc"]["mean"])} at f = {f_mid} (p = '
         f'{scr[f_mid]["handoff"]["vs_stage1"]["p_raw"]:.1e}) and {fmt(scr[f_hi]["handoff"]["auc"]["mean"])} at f = '
         f'{f_hi} (p = {scr[f_hi]["handoff"]["vs_stage1"]["p_raw"]:.1e}). With the published default in stage 2 the '
         f'cascade did not improve on stage 1 (p = {scr[f_mid]["default"]["vs_stage1"]["p_raw"]:.2f} at f = {f_mid}), '
         f'and the pseudo-label choice tracked the hand-over ({fmt(scr[f_mid]["pseudo"]["auc"]["mean"])} at f = {f_mid}), '
         'so the improvement comes from the handed-over time constant rather than from the second density count '
         f'as such. Stage 1 passed {scr[f_mid]["signal_recall"]["mean"]:.2f} of the object events at f = {f_mid} '
         f'and {scr[f_hi]["signal_recall"]["mean"]:.2f} at f = {f_hi}, which bounds the recall of the cascade. Its '
         f'quantile operating point remained calibrated (median false-positive rate '
         f'{scr[f_mid]["handoff"]["operating"][a_mid]["fpr"]["median"]:.4f} at a requested {a_mid}, f = {f_mid}). The '
         f'stage-2 workload fell in proportion to f ({scr[f_mid]["handoff"]["stage2_time_over_ynoise_full"]["median"]:.2f} '
         f'of the full-stream YNoise time at f = {f_mid}); the pseudo-label search cost '
         f'{scr[f_mid]["pseudo"]["stage2_time_over_ynoise_full"]["median"]:.0f} times the full-stream time. In this '
         f'implementation stage 1 itself ({hy["stage1"]["time_s"]["median"] * 1e3:.0f} ms per recording, median) '
         f'costs more than YNoise on the whole stream ({yf["default"]["time_s"]["median"] * 1e3:.0f} ms), so the '
         'cascade lowers total cost only when the confirmation stage is expensive, such as a network, or when '
         'the screened stream must leave the sensor.')
    qual = N['qual']
    qr = qual['recordings']
    qk = list(qr)

    def q(key, name, k):
        return qr[key]['methods'][name][k]

    s0, s1 = (k.replace('x', ' x ') for k in qk)
    for kk in qk:
        assert min(q(kk, 'ynoise_handoff', 'tpr'), q(kk, 'two_stage', 'tpr')) > \
            max(q(kk, 'proposal_zk', 'tpr'), q(kk, 'ynoise_default', 'tpr')), 'qualitative summary sentence'
    para(doc,
         'Supplementary Fig. S2 shows one recording per sensor model after each stage at a requested false-alarm '
         f'rate of {qual["alpha"]:g}; the hand-over and the cascade passed more of the object events than the '
         'proposal alone or YNoise at its default, and the Fano-factor score, whose per-pixel ratio takes few '
         'distinct values, could not be set to the budget by a quantile (smallest passable false-positive rate '
         f'{q(qk[0], "fano", "fpr"):.3f} and {q(qk[1], "fano", "fpr"):.3f}).')
    para(supp,
         'Fig. S2 shows the same two recordings, one per sensor model, after each stage at a requested false-alarm '
         f'rate of {qual["alpha"]:g}. On the {s0} recording the zero-knowledge proposal passed '
         f'{q(qk[0], "proposal_zk", "tpr"):.2f} of the object events, YNoise at its default '
         f'{q(qk[0], "ynoise_default", "tpr"):.2f}, YNoise with the handed-over W {q(qk[0], "ynoise_handoff", "tpr"):.2f} '
         f'and the two-stage score at f = {qual["screen_fraction"]:g} {q(qk[0], "two_stage", "tpr"):.2f}; on the {s1} '
         f'recording the corresponding values were {q(qk[1], "proposal_zk", "tpr"):.2f}, '
         f'{q(qk[1], "ynoise_default", "tpr"):.2f}, {q(qk[1], "ynoise_handoff", "tpr"):.2f} and '
         f'{q(qk[1], "two_stage", "tpr"):.2f}. The Fano-factor score is shown for contrast: its per-pixel ratio takes '
         'few distinct values, so the \u03b1-quantile falls inside a block of tied scores and the smallest block '
         f'that can be passed already has a false-positive rate of {q(qk[0], "fano", "fpr"):.3f} and '
         f'{q(qk[1], "fano", "fpr"):.3f}; a score with few distinct values cannot be set to a false-alarm budget by '
         'a quantile. The two recordings were chosen by a fixed rule (stage-1 AUC closest to the sensor median) and the events each method passed were accumulated into per-pixel count images; the pooled figures are those of Table 3 of the main text.')
    sfigure(supp, 'fig8_qualitative.png',
           'Fig. S2. The same two EBSSA recordings processed by every stage. Rows: one recording per sensor model '
           f'({", ".join(qr[k]["recording_id"] for k in qk)}), the recording whose stage-1 AUC is closest to the '
           'median of that sensor, with its rate-adaptive window W. Columns: all events; events inside the '
           f'annotated object boxes; events passed at a requested false-alarm rate of {qual["alpha"]:g} by the '
           'zero-knowledge proposal alone, by YNoise at its published default, by the hand-over (YNoise with '
           f'dt = W), by the two-stage cascade with f = {qual["screen_fraction"]:g}, and by the Fano-factor score. '
           'Each panel is the per-pixel count of passed events over the analysed interval on a logarithmic grey '
           'scale; achieved detection and false-positive rates are given above each panel.', width=Inches(6.0))

    heading(doc, '5.8. Generalisation to a third sensor: DND21', 2)
    strata = N['dnd_strata']
    conds = N['dnd_conditions']
    hyb_keys = sorted(k for k in dm if k.startswith('hybrid_'))
    zk_vs_ebssa = dm['zero_knowledge']['mean'] - dm['edlr_adaptive_ebssa']['mean']
    handoff_frac = dm['ynoise_handoff']['mean'] / dm['ynoise']['mean']
    cond_zk = {c: strata[f'noise_{c}']['zero_knowledge']['mean'] for c in conds}
    cond_hand = {c: strata[f'noise_{c}']['ynoise_handoff']['mean'] for c in conds}
    cond_def = {c: strata[f'noise_{c}']['ynoise_default']['mean'] for c in conds}
    worst_c = min(cond_zk, key=cond_zk.get)
    best_c = max(cond_zk, key=cond_zk.get)
    src_zk = {s: strata[f'source_{s}']['zero_knowledge']['mean'] for s in src}
    src_hand = {s: strata[f'source_{s}']['ynoise_handoff']['mean'] for s in src}
    src_def = {s: strata[f'source_{s}']['ynoise_default']['mean'] for s in src}
    src_gain = {s: src_hand[s] - src_def[s] for s in src}
    hand_vs_def = dm['ynoise_handoff']['mean'] - dm['ynoise_default']['mean']
    sub_chance = [r for r in N['dnd_recs'] if r['metrics']['zero_knowledge']['auc'] < 0.5]
    sub_src = sorted({r['source'] for r in sub_chance})
    src_n = {s: sum(1 for r in N['dnd_recs'] if r['source'] == s) for s in src}
    hd = es_d['ynoise_handoff_vs_ynoise_default']
    zd = es_d['zero_knowledge_vs_ynoise_default']
    ze = es_d['zero_knowledge_vs_edlr_adaptive_ebssa']
    hand_split = (all(src_gain[s] > 0 for s in ('dots5', 'accel_dot'))
                  and all(src_gain[s] <= 0 for s in ('hotel_bar', 'driving')))
    assert hand_split, 'abstract/discussion wording assumes the hand-over helps only on the sparse synthetic scenes'
    best_lf = max(('zero_knowledge', 'ynoise_default', 'ynoise_handoff', *hyb_keys), key=lambda k: dm[k]['mean'])
    best_tuned = max((k for k in dm if not k.endswith('_ebssa') and k not in
                      ('zero_knowledge', 'ynoise_default', 'ynoise_handoff', *hyb_keys)), key=lambda k: dm[k]['mean'])
    para(doc,
         f'Table 4 and Fig. 7 report the DND21 evaluation on {N["dnd_n_rec"]} mixtures from {N["dnd_n_sources"]} '
         'scenes. The result is negative for the detector as a ranker and mixed for the hand-over, and we report '
         'it as such. With no DND21 labels and no tuning, the rate-adaptive proposal at its fixed deployment '
         f'configuration reached {dauc_sd(N, "zero_knowledge")}, {zd["mixture_level"]["mean_diff"]:+.3f} '
         f'(95% CI {ci(zd["mixture_level"])}) from YNoise at its published default, below it on '
         f'{zd["segment_level"]["n"] - zd["segment_level"]["n_a_better"]} of {zd["segment_level"]["n"]} signal segments '
         f'and on {zd["source_level"]["n_sources"] - zd["source_level"]["n_sources_a_better"]} of {zd["source_level"]["n_sources"]} '
         f'sources; with the configuration selected on EBSSA it '
         f'reached {dauc(N, "edlr_adaptive_ebssa")} ({zk_vs_ebssa:+.3f}, 95% CI {ci(ze["mixture_level"])}), and with nested leave-one-scene-out '
         f'selection on DND21 itself {dauc(N, "edlr_adaptive")} (fixed window {dauc(N, "edlr")}). The label-tuned '
         f'comparators again ranked above it: YNoise {dauc(N, "ynoise")}, event bilateral {dauc(N, "bilateral")}, '
         f'PFD-A approximation {dauc(N, "pfd")}, DWF {dauc(N, "dwf")} (mean paired difference of the nested fixed-window proposal '
         f'minus YNoise {dt["ynoise"]["auc_diff_mean"]:+.3f}, Holm-adjusted p {pfmt(dt["ynoise"]["p_holm"])}), and '
         f'the supervised networks trained on the other scenes reached {dauc(N, "mlpf")} (MLPF-style) and '
         f'{dauc(N, "edncnn")} (EDnCNN-style)'
         + ('; the latter was the best method overall' if best_tuned == 'edncnn'
            else f'; the best method overall was {short(best_tuned) if best_tuned in m else best_tuned} ({dauc(N, best_tuned)})')
         + '. Unlike on EBSSA, the published default of YNoise was already close to its '
         f'nested-tuned value ({dauc(N, "ynoise_default")} against {dauc(N, "ynoise")}), so the hand-over had little '
         f'to recover: YNoise with dt = W reached {dauc(N, "ynoise_handoff")}, {hand_vs_def:+.3f} relative to the '
         f'default (95% CI {ci(hd["mixture_level"])}; Wilcoxon p {pfmt(N["dnd"]["ynoise_handoff_vs_default"]["p_raw"])} over '
         f'mixtures, but p = {hd["segment_level"]["p_wilcoxon"]:.2f} over the {hd["segment_level"]["n"]} signal segments, '
         f'with the hand-over ahead on {hd["segment_level"]["n_a_better"]} of them), i.e. no difference that survives the '
         f'dependence between mixtures (Supplementary Table S6 gives the segment- and source-level check for every row of Table 4), '
         f'and {pct(handoff_frac, 1)} of the nested label-tuned value. The direction of the hand-over depended on the scene: '
         f'{"; ".join(f"{s} {src_gain[s]:+.3f}" for s in src)} (handed-over minus default, by signal source; '
         f'descriptive, {min(src_n.values())}-{max(src_n.values())} mixtures per scene, not tested), i.e. it '
         + ('helped on the sparse synthetic targets and cost accuracy on the dense natural scenes. '
            if hand_split else 'did not separate cleanly by scene density. ')
         + f'The two-stage cascade reached {", ".join(f"{dauc(N, k)} at f = {k.split(chr(95))[1]}" for k in hyb_keys)}, '
         f'no better than the screening stage alone, consistent with the weak screen it inherits here; the best '
         f'label-free configuration on DND21 was therefore {LF_LABEL[best_lf]} ({dauc(N, best_lf)}). '
         f'The handed-over window had a median of {N["dnd_window_ms"]["median"]:.0f} ms (range '
         f'{N["dnd_window_ms"]["min"]:.0f}-{N["dnd_window_ms"]["max"]:.0f} ms) against the '
         f'{hyb["ynoise_default"]["dt_us"] / 1e3:g} ms default. By noise condition the untuned proposal fell from '
         f'{fmt(cond_zk[best_c])} ({cond_name(best_c)}) to {fmt(cond_zk[worst_c])} ({cond_name(worst_c)}), '
         f'while the hand-over held between {fmt(min(cond_hand.values()))} and {fmt(max(cond_hand.values()))} '
         f'(default {fmt(min(cond_def.values()))}-{fmt(max(cond_def.values()))}); by scene, the untuned proposal '
         f'ranged from {fmt(min(src_zk.values()))} ({min(src_zk, key=src_zk.get)}) to {fmt(max(src_zk.values()))} '
         f'({max(src_zk, key=src_zk.get)}). In {len(sub_chance)} of the {N["dnd_n_rec"]} mixtures (all from '
         f'{", ".join(sub_src)}) the untuned proposal scored below chance (AUC < 0.5): the simulated target dwells '
         'on the same pixels for many events, so those pixels acquire a high estimated background rate and their '
         'events are scored as expected rather than as anomalous, the failure mode implied by the per-pixel '
         'Poisson null (Section 3.2), which assumes a stationary background and a transient signal at each '
         'pixel. Two conclusions carry over from EBSSA and one does not: the untuned proposal is a weaker '
         'ranker than the tuned density filters; a window stated as an expected count still transfers '
         f'({dauc(N, "edlr_adaptive_ebssa")} with the EBSSA-selected k against {dauc(N, "edlr_adaptive")} with '
         f'nested selection, whereas the EBSSA-selected fixed window in milliseconds gave {dauc(N, "edlr_ebssa")}); '
         'but the gain of the hand-over over the published default did not reappear on average, only on the '
         'sparse scenes.')

    def dpair(k):
        return es_d.get(f'edlr_vs_{k}' if k in dt else f'zero_knowledge_vs_{k}')

    def drow(k, name):
        t = dt.get(k) or df.get(k)
        e = dpair(k)
        return [name, dauc_sd(N, k), '-' if t is None else f"{t['auc_diff_mean']:+.3f}",
                '-' if e is None else ci(e['mixture_level']),
                '-' if t is None else (f"{t['p_holm']:.3f}" if t['p_holm'] >= 0.001 else '<0.001'),
                '-' if e is None else pfmt(e['segment_level']['p_wilcoxon']),
                '-' if e is None else f"{e['source_level']['n_sources_a_better']}/{e['source_level']['n_sources']}"]

    dnd_rows = [drow('zero_knowledge', 'Proposed, rate-adaptive, fixed deployment (no tuning)'),
                drow('edlr_adaptive_ebssa', 'Proposed, rate-adaptive, EBSSA-selected k'),
                drow('edlr_adaptive', 'Proposed, rate-adaptive, nested CV on DND21'),
                drow('edlr', 'Proposed, fixed window, nested CV on DND21'),
                drow('ynoise_default', 'YNoise, published default'),
                drow('ynoise_ebssa', 'YNoise, EBSSA-selected'),
                drow('ynoise_handoff', 'YNoise, dt = W handed over (no labels)')]
    dnd_rows += [drow(k, f'Two-stage cascade, f = {k.split("_")[1]} (no labels)') for k in hyb_keys]
    dnd_rows += [drow('ynoise', 'YNoise, nested CV'), drow('bilateral', 'Event bilateral, nested CV'),
                 drow('pfd', 'PFD-A (approximation), nested CV'), drow('dwf', 'DWF, nested CV'),
                 drow('knoise', 'kNoise, nested CV'), drow('temporal', 'Background-activity filter, nested CV'),
                 drow('plr', 'Voxelised Poisson LR, nested CV'),
                 drow('mlpf', 'MLPF-style (supervised, other scenes)'),
                 drow('edncnn', 'EDnCNN-style (supervised, other scenes)')]
    table(doc,
          f'Table 4. DND21 (DAVIS346, third sensor): mean \u00b1 SD ROC-AUC over {N["dnd_n_rec"]} mixtures with '
          'exact origin labels. \u0394AUC and p (Holm): for tuned and supervised rows, the paired difference of the '
          'nested-CV fixed-window proposal minus the method with Holm adjustment over mixtures; for label-free rows, the '
          'paired difference of the fixed-deployment proposal minus the method. 95% CI: cluster bootstrap over '
          f'signal segments ({N["dnd_n_segment_clusters"]} clusters). p (segment): unadjusted paired Wilcoxon over the '
          f'{N["dnd_n_segment_clusters"]} segments (sensitivity analysis). Sources: number of the '
          f'{N["dnd_n_sources"]} signal sources on which the proposal has the higher mean AUC (descriptive). Nested CV: leave-one-scene-out. '
          'EBSSA-selected: configuration chosen on EBSSA and applied unchanged.',
          ['Configuration', 'AUC (mean \u00b1 SD)', '\u0394AUC', '95% CI', 'p (Holm)', 'p (segment)', 'Sources'],
          dnd_rows, col_widths=[2.8, 1.15, 0.6, 1.3, 0.6, 0.75, 0.6], font_pt=7, landscape=True)
    figure(doc, 'fig9_dnd21.png',
           f'Fig. 7. DND21 evaluation on {N["dnd_n_rec"]} mixtures recorded with a third sensor (DAVIS346). '
           '(a) Mean ROC-AUC with SD for every configuration of Table 4, grouped by how the parameters were '
           'obtained: without labels or tuning on DND21, by nested leave-one-scene-out selection, or by '
           'supervised training on the other scenes. (b) Mean AUC with SD of the label-free path (zero-knowledge '
           'proposal, YNoise at its default, YNoise with the handed-over window) against the measured-noise '
           'condition; the nominal per-pixel rate of the thinned dark recording is given, and "light (native)" is '
           'the unthinned recording under uniform illumination.', width=Inches(6.0))

    heading(doc, '5.9. Transfer of a released supervised denoiser', 2)
    ad, ae = N['aednet_dnd'], N['aednet_ebssa']
    ae_vs, yn_vs = ad['zero_knowledge_minus_aednet'], ad['ynoise_default_minus_aednet']
    ae_vs_e, yn_vs_e = ae['zero_knowledge_minus_aednet'], ae['ynoise_default_minus_aednet']
    ae_src, ae_cond = ad['by_source'], ad['by_condition']
    ae_recs, ae_recs_e = N['aednet_dnd_recs'], N['aednet_ebssa_recs']
    n_ae_below = sum(1 for r in ae_recs if r['aednet_auc_subset'] < 0.5)
    n_ae_below_e = sum(1 for r in ae_recs_e if r['aednet_auc_subset'] < 0.5)
    ae_rel = ('above' if ae_vs['mean'] < 0 else 'below')
    ae_rel_e = ('above' if ae_vs_e['mean'] < 0 else 'below')

    def ae_sensor(hw):
        rs = [r for r in ae_recs_e if tuple(r['sensor_hw']) == hw]
        return fmt(np.mean([r['aednet_auc_subset'] for r in rs])), fmt(np.mean([r['zero_knowledge_auc_subset'] for r in rs]))
    ae_s, zk_s = ae_sensor((180, 240))
    ae_l, zk_l = ae_sensor((240, 304))
    para(doc,
         'The released AEDNet model, applied without re-training under the adaptations of Section 4.3, reached a '
         f'mean AUC of {fmt(ae["aednet_mean_auc"])} \u00b1 {fmt(ae["aednet_sd_auc"])} over the {ae["n_recordings"]} '
         f'EBSSA recordings on the scored event subsets (range {fmt(ae["aednet_min_auc"])}-{fmt(ae["aednet_max_auc"])}; '
         f'{n_ae_below_e} recording{"s" if n_ae_below_e != 1 else ""} below chance). On the same events the untuned '
         f'proposal reached {fmt(ae["zero_knowledge_mean_auc_subset"])} and YNoise at its published default '
         f'{fmt(ae["ynoise_default_mean_auc_subset"])} (full-stream values {fmt(ae["zero_knowledge_mean_auc_full"])} '
         f'and {fmt(ae["ynoise_default_mean_auc_full"])}, the fixed-configuration values of Supplementary Table S5; the largest '
         f'subset-versus-full-stream discrepancy in any recording was {ae["subset_sampling_error_max_abs"]:.3f}), so the '
         f'transferred network ranked {ae_rel_e} the untuned proposal: proposal minus AEDNet {ae_vs_e["mean"]:+.3f} '
         f'(95% bootstrap CI {ci(ae_vs_e)}), with the proposal ahead on {ae["wins_zero_knowledge_over_aednet"]} of '
         f'{ae["n_recordings"]} recordings, and YNoise default minus AEDNet {yn_vs_e["mean"]:+.3f} (95% CI '
         f'{ci(yn_vs_e)}). The gap was concentrated on the 180 x 240-pixel sensor (AEDNet {ae_s} against {zk_s} for '
         f'the proposal) and small on the 240 x 304-pixel sensor ({ae_l} against {zk_l}).')
    para(doc,
         f'On DND21 the same model reached {fmt(ad["aednet_mean_auc"])} \u00b1 {fmt(ad["aednet_sd_auc"])} over the '
         f'{ad["n_recordings"]} mixtures (range {fmt(ad["aednet_min_auc"])}-{fmt(ad["aednet_max_auc"])}; '
         f'{n_ae_below} mixture{"s" if n_ae_below != 1 else ""} below chance), against '
         f'{fmt(ad["zero_knowledge_mean_auc_subset"])} for the untuned proposal and '
         f'{fmt(ad["ynoise_default_mean_auc_subset"])} for YNoise at its default on the same events (full-stream '
         f'values {fmt(ad["zero_knowledge_mean_auc_full"])} and {fmt(ad["ynoise_default_mean_auc_full"])}; largest '
         f'subset-versus-full-stream discrepancy {ad["subset_sampling_error_max_abs"]:.3f}). Here the network ranked '
         f'{ae_rel} the untuned proposal: proposal minus AEDNet {ae_vs["mean"]:+.3f} (95% cluster-bootstrap CI '
         f'{ci(ae_vs)}), with the proposal ahead on {ad["wins_zero_knowledge_over_aednet"]} of {ad["n_recordings"]} '
         f'mixtures, and YNoise default minus AEDNet {yn_vs["mean"]:+.3f} (95% CI {ci(yn_vs)}). By scene, AEDNet '
         f'ranged from {fmt(min(ae_src.values()))} ({min(ae_src, key=ae_src.get)}) to {fmt(max(ae_src.values()))} '
         f'({max(ae_src, key=ae_src.get)}), and by noise condition from {fmt(min(ae_cond.values()))} '
         f'({cond_name(min(ae_cond, key=ae_cond.get))}) to {fmt(max(ae_cond.values()))} '
         f'({cond_name(max(ae_cond, key=ae_cond.get))}) (Supplementary Table S7). These are the numbers of a fixed '
         'network trained on another sensor and noise distribution and scored on event subsets; they locate the '
         'released model on these two datasets and say nothing about what AEDNet re-trained on their labels would reach.')

    es5_rows = []
    for key, e in es_d.items():
        ml, sl, so = e['mixture_level'], e['segment_level'], e['source_level']
        es5_rows.append([e['a'].replace('_', ' '), e['b'].replace('_', ' '), f"{ml['mean_diff']:+.3f}", ci(ml),
                         pfmt(ml['p_wilcoxon']), f"{ml['rank_biserial']:+.2f}", f"{sl['mean_diff']:+.3f}",
                         pfmt(sl['p_wilcoxon']), f"{sl['n_a_better']}/{sl['n']}",
                         f"{so['n_sources_a_better']}/{so['n_sources']}"])
    stable(supp,
           f'Table S6. Dependence-aware sensitivity analysis on DND21. Mixture level: {N["dnd_n_rec"]} mixtures, paired '
           'difference A minus B with cluster-bootstrap 95% CI over signal segments, unadjusted Wilcoxon p and '
           f'rank-biserial r. Segment level: mean AUC over the noise conditions of each of the {N["dnd_n_segment_clusters"]} '
           f'signal segments, paired difference, Wilcoxon p and number of segments with A ahead. Source level: number of the '
           f'{N["dnd_n_sources"]} signal sources with A ahead (no test). Method keys as in the result files: edlr, nested-CV '
           'fixed-window proposal; edlr adaptive, nested-CV rate-adaptive proposal; zero knowledge, fixed-deployment proposal; '
           'ebssa suffix, configuration selected on EBSSA; hybrid f, two-stage cascade passing fraction f.',
           ['A', 'B', 'Mix. \u0394', 'Mix. 95% CI', 'Mix. p', 'r', 'Seg. \u0394', 'Seg. p', 'Seg. A ahead', 'Sources A ahead'],
           es5_rows, col_widths=[1.1, 1.1, 0.55, 1.0, 0.6, 0.45, 0.55, 0.6, 0.6, 0.6], font_pt=7, landscape=True)

    def ae_group(rs):
        return [f"{np.mean([r['aednet_auc_subset'] for r in rs]):.3f}",
                f"{np.mean([r['zero_knowledge_auc_subset'] for r in rs]):.3f}",
                f"{np.mean([r['ynoise_default_auc_subset'] for r in rs]):.3f}",
                f"{np.mean([r['zero_knowledge_auc_full'] for r in rs]):.3f}",
                f"{np.mean([r['ynoise_default_auc_full'] for r in rs]):.3f}",
                f"{np.mean([r['n_scored'] for r in rs]):.0f}", str(len(rs))]

    es6_rows = ([[f'EBSSA, {hw[0]} x {hw[1]}-pixel sensor', *ae_group([r for r in ae_recs_e if tuple(r['sensor_hw']) == hw])]
                 for hw in ((180, 240), (240, 304))]
                + [['EBSSA, all recordings', *ae_group(ae_recs_e)]]
                + [['DND21 scene: ' + s, *ae_group([r for r in ae_recs if r['source'] == s])] for s in N['dnd_sources']]
                + [['DND21 condition: ' + cond_name(c), *ae_group([r for r in ae_recs if r['condition'] == c])]
                   for c in N['dnd_conditions']]
                + [['DND21, all mixtures', *ae_group(ae_recs)]])
    for row, s in ((es6_rows[2], ae), (es6_rows[-1], ad)):
        assert row[1:6] == [fmt(s['aednet_mean_auc']), fmt(s['zero_knowledge_mean_auc_subset']),
                            fmt(s['ynoise_default_mean_auc_subset']), fmt(s['zero_knowledge_mean_auc_full']),
                            fmt(s['ynoise_default_mean_auc_full'])], 'Table S7 totals must match the summary'
    stable(supp,
           f'Table S7. Zero-shot transfer of the released AEDNet weights to EBSSA and DND21 (Section 4.3): mean ROC-AUC on '
           f'stratified subsets of at most {N["aednet"]["n_per_class"]:,} signal and {N["aednet"]["n_per_class"]:,} '
           'background events per recording, next to the untuned proposal and YNoise at its published default on the '
           'same subsets and on the full streams. Rows: EBSSA by sensor and overall; DND21 by signal scene, by noise '
           'condition and overall. Events: mean number of scored events per recording. n: number of recordings or '
           'mixtures. Adaptations from the published protocol: '
           + '; '.join(N['aednet']['adaptations']) + '. Environment: PyTorch '
           f'{N["aednet"]["environment"]["torch"]}, CUDA {"available" if N["aednet"]["environment"]["cuda_available"] else "not available"}. '
           f'Code {N["aednet"]["code_url"]} at commit {N["aednet"]["code_commit"][:7]}; weights SHA-256 '
           f'{N["aednet"]["weights_sha256"]}.',
           ['Stratum', 'AEDNet (subset)', 'Proposal (subset)', 'YNoise default (subset)', 'Proposal (full)',
            'YNoise default (full)', 'Events', 'n'],
           es6_rows, col_widths=[1.5, 0.8, 0.8, 0.9, 0.8, 0.9, 0.6, 0.4], font_pt=7, landscape=True)

    # ---------------- 6 Discussion ----------------
    heading(doc, '6. Discussion')
    para(doc,
         'Read as anomaly detection, the per-pixel Poisson test sits where a well-specified parametric normal '
         'model is expected to sit: a competent but not the best ranker, distinguished by calibration and by '
         'the reuse of the fitted normal model. '
         f'On EBSSA its ROC-AUC is statistically indistinguishable from {len(ns_pub)} of the {len(pub)} published '
         'unsupervised event filters when those filters are given cross-validated tuning, and below the best of them by '
         f'{abs(tests["ynoise"]["auc_diff_mean"]):.2f}; without labels that gap closes '
         f'({fmt(dfl["edlr_adaptive"]["auc_mean"])} against {fmt(dfl["ynoise"]["auc_mean"])} at fixed configurations, '
         'Supplementary Table S5). On DND21 the gap is wider and does not close '
         f'({dauc(N, "zero_knowledge")} untuned against {dauc(N, "ynoise_default")} for YNoise at its published default), '
         'and on the dwelling synthetic target the detector fell below chance. What it adds, on the evidence here, is that its '
         'false-alarm budget is honoured without labels, that its window transfers between sensors when stated '
         'as an expected count, and that the same window, handed to YNoise, recovers '
         f'{pct(hand_frac, 1)} of the accuracy of label tuning on EBSSA, where the published default is far from '
         f'the tuned value. On DND21, where the default is already near the tuned value, the hand-over gave '
         f'{hand_vs_def:+.3f} on average (95% CI {ci(hd["mixture_level"])}, not significant at the segment level), '
         'with a positive difference on the two sparse synthetic scenes and a negative one on the two dense natural scenes (descriptive). The '
         'claim we can support is therefore narrower than "the stream calibrates the filter": the rate-derived '
         'window is a label-free substitute for tuning when the scene is sparse and transient at each pixel, '
         'and it is not a substitute for a scene-appropriate default when the scene is dense. More generally, a '
         'window in milliseconds encodes a scale the designer chose for one sensor and one scene; stating it in '
         'a unit the stream itself supplies, the expected number of background events, is what let one setting '
         'carry across three sensor models here, and the same substitution is open to any filter with a time '
         'constant.')
    para(doc,
         f'Relative to supervised networks, the detector is {abs(tests["mlpf"]["auc_diff_mean"]):.2f} to '
         f'{abs(tests["edncnn"]["auc_diff_mean"]):.2f} AUC lower on EBSSA. We regard this as the price of not '
         'requiring labels rather than a deficiency to be hidden: the networks were trained on annotated '
         'recordings from the same sensors and would need new annotations for a new sensor or observing mode. '
         'The released AEDNet model, trained for another sensor and noise distribution, reached '
         f'{fmt(ae["aednet_mean_auc"])} on EBSSA against {fmt(ae["zero_knowledge_mean_auc_subset"])} for the '
         f'untuned proposal and {fmt(ad["aednet_mean_auc"])} on DND21 against '
         f'{fmt(ad["zero_knowledge_mean_auc_subset"])}, on the same events in each case. '
         + ('It thus went both ways: below the untuned proposal on the sparse sky recordings of EBSSA, far from '
            'the scenes it was trained on, and above it on the DND21 mixtures, whose background-activity noise '
            'is of the kind it was trained on. The two transfers are consistent with a fixed supervised model '
            'carrying its training distribution with it; the label-free detector was ahead only where the stream '
            'resembled the sparse regime it assumes. '
            if ae_vs['mean'] < 0 < ae_vs_e['mean'] else
            'The released network ranked '
            + ('above' if ae_vs['mean'] < 0 else 'below') + ' the untuned proposal on DND21 and '
            + ('above' if ae_vs_e['mean'] < 0 else 'below') + ' it on EBSSA. ')
         + 'What the proposal retains in both cases is the calibrated operating point and the transferable '
         'window, which the network does not offer. The cost argument for the cascade applies when the '
         'confirmation stage is expensive, such as one of these networks, or when the screened stream must '
         'leave the sensor; the argument from the data is that the proposal supplies, without labels, the '
         'parameter the confirmation stage otherwise needs labels to find. The cost comparison is also '
         'one-sided in favour of the comparators, since the labelled recordings and grid search they needed '
         'before inference are not charged to them.')
    para(doc,
         'Several limitations bound these conclusions. First, the EBSSA ground truth is a 10 x 10-pixel box '
         'around a tracked position over 10 ms, which compresses the AUC of every method and may affect them '
         'unequally; the DND21 labels are exact, but the signal fraction of the mixtures spans two orders of '
         'magnitude by construction, the mixtures are synthetic combinations of two real recordings with only '
         f'{N["dnd_n_sources"]} scenes (two simulator-rendered), so the leave-one-scene-out folds are few and the '
         'strata by scene are descriptive, and in the one real scene residual background activity of the '
         'source recording is counted as signal. Second, only three sensor models were available and the '
         'constant k was chosen on EBSSA; DND21 shows that the count-based window carries to a DAVIS346 '
         f'({dauc(N, "zero_knowledge")} untuned against {dauc(N, "edlr_adaptive")} with nested selection) but '
         'also that the detector itself is not competitive on dense or dwelling scenes, so its domain of use is '
         'the sparse-transient regime it was designed for. Third, the homogeneous-Poisson null ignores '
         'refractory behaviour and burst noise, so the achieved false-alarm rate is close to but not exactly '
         'the requested one, and persistent sources are treated as background only because their pixels '
         'acquire a high estimated rate. Fourth, the cost measurements are single-core Python and Numba timings, '
         'and the hand-over was tested for one comparator. Fifth, the published comparators were re-implemented '
         'from their descriptions, the PFD comparator approximates one stage of the published method, the '
         'AEDNet result is a released model scored on event subsets outside its training distribution, and the '
         'supervised references are re-implementations trained on the labels available here; the comparator '
         'accuracies under cross-validation are upper bounds that an operator without labels could not reach. '
         'Finally, the analysis is retrospective and the strata were not pre-specified.')
    para(doc,
         'The case for the method is strongest when three things hold at once: no labels exist for the sensor '
         'or observing condition, the signal occupies few pixels for a short time, and an operating point must '
         'be stated in advance as a false-alarm rate. Space surveillance with event cameras is the clearest '
         'example; faint moving sources against a static background (meteors, aircraft lights, distant '
         'vessels) and the commissioning of a new sensor before any annotation exists are others. There the '
         'detector can run on its own or hand its window to an existing filter as a first setting, with '
         f'label-tuned or supervised alternatives taking over once labels exist. The DND21 result ({dauc(N, "zero_knowledge")} '
         f'against {dauc(N, "ynoise_default")}) marks the other boundary: when the scene is dense, or a source '
         'dwells on the same pixels long enough to raise their estimated rate, a scene-appropriate default or a '
         'network trained on the same domain will do better, and where labelled data from the same domain '
         'exist the supervised gap on EBSSA is the expected cost of not using them.')

    # ---------------- 7 Conclusion ----------------
    heading(doc, '7. Conclusion')
    para(doc,
         'A per-event Poisson tail test with the background rate of each pixel estimated from its own '
         'inter-event intervals is a self-calibrating, unsupervised anomaly detector for sparse event streams. '
         f'On all {N["n_rec"]} labelled EBSSA recordings it was statistically indistinguishable from {len(ns_pub)} of '
         f'the {len(pub)} label-tuned heuristic filters, met a '
         'stated false-alarm budget without labels, and transferred between sensor models when its window was '
         'stated as an expected background count. Its main value is as a source of parameters rather than as a '
         f'competitor: handed to the density filter YNoise, its window recovered {pct(hand_frac, 1)} of the '
         'accuracy that label tuning gives that filter on EBSSA, and a two-stage cascade in which the detector '
         'screens and the filter confirms improved on both. On the independent DND21 benchmark, recorded with a '
         'third sensor and dominated by dense or dwelling scenes, the detector was clearly outranked by the tuned '
         f'filters and by YNoise at its published default ({dauc(N, "zero_knowledge")} against '
         f'{dauc(N, "ynoise_default")}), and the hand-over was ahead of the default only on the sparse scenes; the count-based '
         'window did transfer. The method is therefore a label-free calibrator for the sparse-transient regime, '
         'not a general event denoiser: it sets a first operating point, or the time constant of an existing '
         'filter, on a new sensor or observing condition before any annotation exists. On dense or dwelling '
         'scenes, or wherever labelled data from the same domain are available, a tuned filter or a supervised '
         'network should be preferred.')

    # ---------------- Declarations ----------------
    heading(doc, 'CRediT authorship contribution statement')
    para(doc, f'{AUTHOR_INITIALS}: Conceptualization, Methodology, Software, Validation, Formal analysis, '
              'Writing - original draft, Writing - review and editing.')
    heading(doc, 'Declaration of competing interest')
    para(doc,
         'The author declares that he has no known competing financial interests or personal relationships '
         'that could have appeared to influence the work reported in this paper.')
    heading(doc, 'Declaration of generative AI and AI-assisted technologies in the writing process')
    para(doc,
         'During the preparation of this work the author used an AI coding assistant (Devin, Cognition AI) to '
         'write the analysis code, generate the figures from the result files and draft and edit the text under '
         'the author\'s direction. After using this tool, the author reviewed and edited the content as needed '
         'and takes full responsibility for the content of the published article.')
    heading(doc, 'Data availability')
    para(doc,
         'The EBSSA dataset is publicly available and was accessed through the Tonic library (version 1.6.0), '
         'which downloads the labelled split from the authors\' repository; the same file is served by the '
         f'authors\' institutional mirror ({N["ebssa_h5_mirror"]}; SHA-256 {N["ebssa_h5_sha256"][:16]}...). '
         'The DND21 recordings are publicly '
         'available from the DND21 project page (https://sites.google.com/view/dnd21); the exact files and the '
         'mixture protocol are specified in the code. All analysis and manuscript-generation code, the result '
         'files (JSON) and a one-command build that regenerates every number, table and figure in this paper '
         'from those result files are released at https://github.com/bougtoir/dvs-noise-inverse-pattern-recognition '
         '(a mirror of the development repository; its contents and the SHA-256 checksums of the result files are '
         'listed in the accompanying REPRODUCIBILITY file). The DND21 analysis re-runs end-to-end from the public '
         'recordings. The EBSSA result files were produced by the released code from the Tonic download; at the '
         'time of writing the EBSSA host limited re-downloads, so those files are shipped as frozen outputs with '
         'their checksums rather than re-derived in the clean-clone check. No additional data were created.')
    heading(doc, 'Acknowledgements')
    para(doc, 'The author thanks the creators of the EBSSA and DND21 datasets for making them publicly available. '
              'This research did not receive any specific grant from funding agencies in the public, commercial, '
              'or not-for-profit sectors.')

    # ---------------- References ----------------
    heading(doc, 'References')
    uncited = set(REFS) - set(jd.CITE_ORDER)
    if uncited:
        raise RuntimeError(f'uncited references: {sorted(uncited)}')
    for i, key in enumerate(jd.CITE_ORDER, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        run = p.add_run(f'[{i}] {ieee_ref(REFS[key])}')
        run.font.size = Pt(BODY_PT)

    out = OUT_DIR / 'manuscript_pattern_recognition.docx'
    doc.save(out)
    supp.save(OUT_DIR / 'supplementary_material.docx')
    print(f'wrote {out}  ({n_words} words in abstract, {len(jd.CITE_ORDER)} references)')
    return out


if __name__ == '__main__':
    build()
