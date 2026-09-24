"""Build GEB manuscript .docx with inline figures.
Source: GEB_main_blinded.md + structured abstract + captions;
figures inserted at first citation point in text."""
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "manuscript" / "GEB"
FIGDIR = ROOT / "figures"
OUT = M / "GEB_manuscript_inline_figures.docx"

FIGMAP = {  # caption key -> png file; insertion marker = "(Fig. N" / "Figure N"
    "Figure 1": "fig_geb1_conceptual.png",
    "Figure 2": "fig_geb2_gamma_dominance.png",
    "Figure 3": "fig_geb3_2d_decay.png",
    "Figure 4": "fig_geb4_lumping_temporal.png",
    "Figure 5": "fig3_bias_heatmap.png",
    "Figure 6": "fig_geb6_empirical.png",
}
INSERT_AFTER = {
    "Figure 1": "Our objectives are",
    "Figure 2": "(Fig. 2b)",
    "Figure 3": "(Fig. 3)",
    "Figure 4": "Fig. 4b)",
    "Figure 5": "(Fig. 5)",
    "Figure 6": "(Fig. 6)",
}
CAPTIONS = Path(M / "GEB_figure_captions.md").read_text()
cap = {}
for m in re.finditer(r"\*\*Figure (\d)\.\s*(.*?)\*\*\s*(.*?)(?=\n\*\*Figure|\Z)",
                     CAPTIONS, re.S):
    cap[f"Figure {m.group(1)}"] = (
        f"Figure {m.group(1)}. {m.group(2)} {m.group(3).strip()}")

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11)

title = doc.add_heading("Structural asymmetries distort guild-level "
                        "beta-diversity contrasts", 0)
doc.add_paragraph("Blinded main text (double-anonymous). Structured abstract "
                  "in GEB_structured_abstract.md; all values traceable to "
                  "results/manuscript_values.csv.").italic = True

body = Path(M / "GEB_main_blinded.md").read_text()
# drop md title line + abstract pointer
lines = body.split("\n")
inserted = set()

def add_fig(key):
    doc.add_picture(str(FIGDIR / FIGMAP[key]), width=Inches(6.0))
    doc.paragraphs[-1].alignment = 1
    p = doc.add_paragraph(cap.get(key, key))
    p.style = doc.styles["Intense Quote"] if "Intense Quote" in [
        s.name for s in doc.styles] else doc.styles["Normal"]
    p.runs[0].font.size = Pt(9)
    inserted.add(key)

# merge hard-wrapped lines into paragraphs
paras = []
buf = []
for line in lines:
    s = line.strip()
    if not s:
        if buf:
            paras.append(" ".join(buf)); buf = []
        continue
    if s.startswith("#"):
        if buf:
            paras.append(" ".join(buf)); buf = []
        paras.append(s)
        continue
    if s.startswith(("(", "*(")) and not buf:
        pass
    buf.append(s)
if buf:
    paras.append(" ".join(buf))

for s in paras:
    if not s:
        continue
    if s.startswith("# "):
        continue
    if s.startswith("## "):
        doc.add_heading(s[3:], 1)
        continue
    if s.startswith("### "):
        doc.add_heading(s[4:], 2)
        continue
    if s.startswith("*(blinded"):
        continue
    doc.add_paragraph(s)
    for key, marker in INSERT_AFTER.items():
        if key not in inserted and marker in s:
            add_fig(key)

doc.add_page_break()
doc.add_heading("Figures (as placed)", 1)
for k in sorted(inserted):
    doc.add_paragraph(f"{k}: {FIGMAP[k]}")
doc.save(str(OUT))
print("saved", OUT, "| inserted:", sorted(inserted))
