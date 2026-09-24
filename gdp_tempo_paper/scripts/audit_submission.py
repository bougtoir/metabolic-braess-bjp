"""Audit manuscript for submission readiness."""
from __future__ import annotations
import re, json, zipfile
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "manuscript" / "manuscript_en.md"
SI = ROOT / "manuscript" / "supporting_information_en.md"

def audit(md_path: Path, label: str, supplementary: bool = False):
    text = md_path.read_text()
    text_for_patterns = re.sub(r"\*\*\[(?:Supplementary\s+)?(?:Figure|Table)\s+\d+\s+here\]\*\*", "", text)
    print(f"\n=== {label} ===")
    # Main Figure citations (exclude Supplementary)
    fig_pattern = r"(?<![Ss]upplementary\s)(?<!World\s)(?<![\(\[])(?:Fig\.?|Figure)\s+(\d+)"
    fig_cites = [int(x) for x in re.findall(fig_pattern, text_for_patterns, re.IGNORECASE)]
    # Main Table citations
    table_pattern = r"(?<![Ss]upplementary\s)(?<!World\s)(?<!SNA\s)(?<!Bank\s)Table\s+(\d+)(?!\.\d|[A-Za-z])"
    table_cites = [int(x) for x in re.findall(table_pattern, text_for_patterns, re.IGNORECASE)]
    print("Figure cites:", fig_cites)
    print("Table cites:", table_cites)

    for name, cites in [("Figure", fig_cites), ("Table", table_cites)]:
        if not cites:
            continue
        if supplementary:
            # SI may contain cross-references to main manuscript figures/tables;
            # only the main manuscript itself needs sequential ordering.
            continue
        first = {}
        for i, n in enumerate(cites):
            if n not in first:
                first[n] = i
        order = [n for n, _ in sorted(first.items(), key=lambda kv: kv[1])]
        expected = list(range(1, max(cites)+1))
        missing = [n for n in expected if n not in first]
        out_of_order = [n for i, n in enumerate(order) if i+1 != n]
        print(f"{name}: first-appearance order={order}, missing={missing}, out_of_order={out_of_order}")
    # Supplementary items
    if supplementary:
        supfig = [int(x) for x in re.findall(r"Supplementary\s+(?:Fig\.?|Figure)\s+(\d+)", text_for_patterns, re.IGNORECASE)]
        suptab = [int(x) for x in re.findall(r"Supplementary\s+Table\s+(\d+)", text_for_patterns, re.IGNORECASE)]
        print("Supplementary Figure cites:", supfig)
        print("Supplementary Table cites:", suptab)
        for name, cites in [("Supp Figure", supfig), ("Supp Table", suptab)]:
            if not cites:
                continue
            first = {}
            for i, n in enumerate(cites):
                if n not in first:
                    first[n] = i
            order = [n for n, _ in sorted(first.items(), key=lambda kv: kv[1])]
            expected = list(range(1, max(cites)+1))
            missing = [n for n in expected if n not in first]
            out_of_order = [n for i, n in enumerate(order) if i+1 != n]
            print(f"{name}: first-appearance order={order}, missing={missing}, out_of_order={out_of_order}")

    # placeholders
    placeholders = re.findall(r"\*\*\[(?:Figure|Table|Supplementary (?:Figure|Table))\s+(\d+)\s+here\]\*\*", text)
    print(f"Placeholders: {placeholders}")
    return locals()

main = audit(MD, "Main manuscript")
si = audit(SI, "Supporting Information", supplementary=True)

# raw LaTeX checks
for path in [MD, SI]:
    t = path.read_text()
    raw = re.findall(r"\$[^$]+\$", t)
    print(f"\nRaw $...$ in {path.name}: {len(raw)} matches")

docx = ROOT / "manuscript" / "manuscript_en.docx"
with zipfile.ZipFile(docx) as z:
    doc_xml = z.read("word/document.xml").decode("utf-8")
print("Raw $ in manuscript_en.docx XML:", re.findall(r"\$[^$]+\$", doc_xml)[:5])

# Old version phrases
text_all = MD.read_text() + SI.read_text()
old = re.findall(r"(?i)(old version|previous version|earlier version|earlier draft|in the previous|we previously|previously we|in the old|before revision|formerly|in the prior|as before|revised version|the original|in our previous|prior version)", text_all)
print("\nOld-version / prior phrases:", old)

# AI-ish words
causal = re.findall(r"(?i)\b(causes?|caused|causing|because of|due to|leads? to|result in|driven by|drives?|determines?|responsible for)\b", text_all)
print("Causal word count:", Counter(causal).most_common())

buzz = re.findall(r"(?i)\b(leverage|delve|navigate|landscape|tapestry|intricate|realm|crucial|pivotal|foster|showcases?|holistic|notably|it is worth noting|as such|in essence|in the context of|going forward|moving forward|needless to say|it is important to note)\b", text_all)
print("Buzzword count:", Counter(buzz).most_common(20))

# Intro promises
intro_text = MD.read_text().split("## 1 Introduction")[1].split("## 2 ")[0]
promises = re.findall(r"(?i)(this paper (?:shows?|quantifies?|provides?|demonstrates?|examines?|explores?|assesses?|documents?)|we (?:show|quantify|provide|demonstrate|examine|explore|assess|document)|the paper (?:will|aims to)|we (?:will|aim to))[^.!]*[.!]", intro_text)
print("\nIntro promises count:", len(promises))
