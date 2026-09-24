"""Generate the EHS resubmission cover letter (docx)."""
import os
from docx import Document
from docx.shared import Pt

HERE = os.path.dirname(os.path.abspath(__file__))

BODY = [
    "Dear Editors of Evolutionary Human Sciences,",

    "I am grateful for your letter of 27 July 2026 regarding manuscript EHS-2026-0079, "
    "suggesting that the appropriate format for our submission is a Commentary on Itao "
    "(2026). I have now revised the work accordingly.",

    "The enclosed Commentary, \u201cTwo pathways, many clocks: a commentary on Itao "
    "(2026),\u201d is approximately 1,000 words and contains one composite figure (Figure 1), "
    "within the Commentary limits specified in the Author Instructions.",

    "This Commentary engages directly with Itao (2026, \u201cTwo universal pathways in demographic "
    "transition,\u201d Evolutionary Human Sciences, https://doi.org/10.1017/ehs.2026.10054), "
    "whose statistical-physics reading of demography\u2014identifying two conserved quantities "
    "that organise the crude birth rate against life expectancy\u2014is an imaginative "
    "cross-disciplinary contribution. My aim is not to overturn that framework but to build on "
    "it: to ask how far the reported regularity extends once national transitions are aligned "
    "on their own timing and the analysis is pushed to sub-national scales.",

    "Using the same public data, I show three complementary results. (1) National fertility "
    "transitions are highly asynchronous (onsets spanning 1828\u20132013), so a single mid-century "
    "change point is best read as a summary of aggregated timing rather than a synchronised "
    "global event. (2) Re-aligning each country on its own transition onset sharpens the first "
    "conserved quantity considerably, while the second quantity does not tighten\u2014so the "
    "two \u2018pathways\u2019 are asymmetric. (3) Below the national level, regions of the same "
    "country at nearly identical life expectancy differ in birth rate by as much as the "
    "cross-national spread the law treats as universal. These findings point to event-time "
    "alignment and hierarchical modelling as natural complements to the original programme.",

    "All numbers and figures regenerate from public data and public code with a single "
    "command; the repository is at "
    "https://github.com/bougtoir/demographic-transition-universality and will be archived "
    "on acceptance. No value in the manuscript is hand-entered.",

    "This Commentary is original, has not been published previously, and is not under "
    "consideration elsewhere. I have no conflicts of interest to declare and the work received "
    "no specific funding. I am the sole author.",

    "Thank you for considering this revised submission. I look forward to your response.",

    "Sincerely,",
    "Tatsuki Onishi",
    "[Affiliation to be completed]",
    "[Email to be completed]",
]


def main():
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    for para in BODY:
        p = doc.add_paragraph(para)
        p.paragraph_format.space_after = Pt(10)
    out = os.path.join(HERE, "Cover_letter_EHS.docx")
    doc.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
