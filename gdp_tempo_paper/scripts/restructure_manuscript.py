#!/usr/bin/env python3
"""Split manuscript_en.md into a concise main text and Supporting Information.

Main text keeps the core narrative (Intro, Theory, Data, core Results,
Discussion, Conclusion, key Tables). Technical diagnostics are moved to
supporting_information_en.md and built as a separate document.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
SRC = MS / "manuscript_en.md"
SI = MS / "supporting_information_en.md"

MAIN_KEEP_SECTIONS = {
    "1 Introduction",
    "2 Related literature",
    "3 Theory",
    "3.1 Flow-side production function with tempo",
    "3.2 Stock-side intangibles: the forgotten beta",
    "3.3 Unifying identity: the flow-stock joint loss",
    "3.4 Quantum–tempo correspondence between population and capital",
    "3.5 Relational PIM: a Brass model for capital accounting",
    "4 Data and methods",
    "4.1 Data",
    "4.2 Models M0–M4 and M_obs",
    "4.3 Estimation protocol and grid search",
    "4.4 Bootstrap confidence intervals",
    "4.5 gamma_price sensitivity",
    "5 Results",
    "5.1 In-sample parameter distributions and fit",
    "5.2 Out-of-sample prediction gains from the tempo correction",
    "5.3 Flow–stock consistency",
    "5.10 Capital-level measurement consequences of tempo correction",
    "5.11 Solow-residual historical decomposition",
    "6 Discussion and policy implications",
    "6.1 Re-interpreting the Solow residual",
    "6.2 The Bongaarts-Feeney-Goldstein-Lutz-Scherbov analogy",
    "6.3 Identification strategy and credibility",
    "6.4 Concrete policy implications",
    "6.5 Flow–stock reconciliation and Beyond-GDP",
    "6.6 Extensions",
    "6.7 Limitations",
    "7 Conclusion",
    "Tables",
    "References",
}

MAIN_KEEP_TABLES = {1, 2, 5, 7}


def parse_sections(path: Path):
    """Parse markdown into preamble (title page) and sections.

    Returns (preamble_lines, sections) where sections is a list of
    (level, heading, body_lines).
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    # Preamble: everything before the [MANUSCRIPT] marker (inclusive)
    preamble = []
    i = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("[MANUSCRIPT]"):
            preamble.append(line)
            break
        preamble.append(line)
    start = i + 1

    sections = []
    cur_level = None
    cur_heading = None
    cur_body = []

    for line in lines[start:]:
        if line.startswith("## "):
            if cur_heading is not None:
                sections.append((cur_level, cur_heading, cur_body))
            cur_level = 2
            cur_heading = line[3:].strip()
            cur_body = []
        elif line.startswith("### "):
            if cur_heading is not None:
                sections.append((cur_level, cur_heading, cur_body))
            cur_level = 3
            cur_heading = line[4:].strip()
            cur_body = []
        else:
            if cur_heading is None:
                # stray line before first heading (e.g. title)
                cur_level = 1
                cur_heading = "__PREAMBLE2__"
                cur_body = []
            cur_body.append(line)
    if cur_heading is not None:
        sections.append((cur_level, cur_heading, cur_body))
    return preamble, sections


def extract_tables_from_section(body: list[str], keep_set: set[int]) -> list[str]:
    """Given a Tables-section body, return only the kept table blocks."""
    out = []
    buffer = []
    current_table = None
    i = 0
    while i < len(body):
        line = body[i]
        stripped = line.strip()
        if stripped.startswith("**Table "):
            # flush previous buffer
            if current_table is not None and buffer:
                out.extend(buffer)
            buffer = [line]
            # parse table number
            try:
                num = int(stripped.split("Table ")[1].split(".")[0].split(" ")[0])
            except Exception:
                num = None
            current_table = num
        elif stripped.startswith("**[Insert table") or stripped.startswith("**[Insert Table"):
            buffer.append(line)
            if current_table is not None and current_table in keep_set:
                out.extend(buffer)
            buffer = []
            current_table = None
        elif current_table is None:
            # Between table blocks, keep blank lines and separators
            if not stripped or stripped == "---":
                out.append(line)
        else:
            buffer.append(line)
        i += 1
    return out


def build_main(preamble: list[str], sections: list):
    out = list(preamble)
    # body: title/abstract block before first heading
    for level, heading, body in sections:
        if heading == "__PREAMBLE2__":
            # title / author lines before Introduction
            out.extend(body)
            continue
        if heading in MAIN_KEEP_SECTIONS:
            prefix = "## " if level == 2 else "### "
            if heading == "Tables":
                out.append(f"{prefix}{heading}")
                out.extend(extract_tables_from_section(body, MAIN_KEEP_TABLES))
                out.append("")
            else:
                out.append(f"{prefix}{heading}")
                out.extend(body)
    return "\n".join(out) + "\n"


def build_si(sections: list):
    out = ["# Supporting Information", ""]
    # body: include all sections not in main, plus all tables not kept.
    # Keep references for self-containedness.
    main_headings = {h for h in MAIN_KEEP_SECTIONS if not h.startswith("5.")}
    # For Results subsections, we keep specific ones; move the others.
    moved_tables = set(range(1, 14)) - MAIN_KEEP_TABLES
    for level, heading, body in sections:
        if heading == "__PREAMBLE2__":
            continue
        if heading in MAIN_KEEP_SECTIONS and heading != "Tables":
            continue
        prefix = "## " if level == 2 else "### "
        if heading == "Tables":
            out.append(f"{prefix}{heading}")
            out.extend(extract_tables_from_section(body, moved_tables))
            out.append("")
        else:
            out.append(f"{prefix}{heading}")
            out.extend(body)
    return "\n".join(out) + "\n"


def main():
    preamble, sections = parse_sections(SRC)
    main_text = build_main(preamble, sections)
    si_text = build_si(sections)
    (MS / "manuscript_en.md").write_text(main_text, encoding="utf-8")
    SI.write_text(si_text, encoding="utf-8")
    print(f"wrote {MS / 'manuscript_en.md'} and {SI}")


if __name__ == "__main__":
    main()
