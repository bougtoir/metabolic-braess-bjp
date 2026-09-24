#!/usr/bin/env python3
"""Mechanical checks on the built manuscript and supplementary file.

* every Fig./Table in the main text and every Fig. S/Table S in the supplement is
  cited in the main text before (or in the paragraph preceding) its caption,
* first citations appear in numerical order,
* each caption follows its first-citing paragraph without another figure/table in between,
* no orphan or phantom figure/table numbers,
* the abstract has <= 200 words, no .dot file exists, figure/table text is ASCII/Latin (English).
"""

import re
import sys
from pathlib import Path

from docx import Document

HERE = Path(__file__).resolve().parent
MAIN = HERE / 'manuscript_pattern_recognition.docx'
SUPP = HERE / 'supplementary_material.docx'

CAP = re.compile(r'^(Fig\.|Table) (S?\d+)\. ')
CITE_MAIN = {'Fig.': re.compile(r'Figs?\. (\d+)(?![\d\.])'), 'Table': re.compile(r'Tables? (\d+)(?![\d\.])')}
CITE_SUPP = {'Fig.': re.compile(r'Supplementary Fig\. (S\d+)'), 'Table': re.compile(r'Supplementary Tables? (S\d+)')}


def body_items(doc):
    """Yield (kind, text) in document order; tables appear as ('TABLE', None)."""
    from docx.text.paragraph import Paragraph
    for el in doc.element.body.iterchildren():
        if el.tag.endswith('}p'):
            yield 'P', Paragraph(el, doc).text.strip()
        elif el.tag.endswith('}tbl'):
            yield 'TABLE', None


def check(main, supp):
    errors = []
    main_items = list(body_items(main))
    texts = [t for k, t in main_items if k == 'P']
    # abstract
    i = texts.index('Abstract')
    n_abs = len(texts[i + 1].split())
    if n_abs > 200:
        errors.append(f'abstract has {n_abs} words')
    # captions in main text, in order, cited before appearance
    seen = {'Fig.': [], 'Table': []}
    cited = {'Fig.': [], 'Table': []}
    cited_supp = {'Fig.': [], 'Table': []}
    last_cite_par = {}
    par_idx = -1
    for kind, t in main_items:
        if kind != 'P':
            continue
        par_idx += 1
        m = CAP.match(t)
        if m and not m.group(2).startswith('S'):
            key, num = m.group(1), int(m.group(2))
            seen[key].append(num)
            if num not in cited[key]:
                errors.append(f'{key} {num} appears before it is cited')
            elif last_cite_par[(key, num)] != par_idx - 1 and not _only_captions_between(texts, last_cite_par[(key, num)], par_idx):
                errors.append(f'{key} {num} is not placed directly after its first-citing paragraph')
            continue
        for key, rx in CITE_MAIN.items():
            for n in rx.findall(t):
                n = int(n)
                if n not in cited[key]:
                    cited[key].append(n)
                    last_cite_par[(key, n)] = par_idx
        for key, rx in CITE_SUPP.items():
            for s in rx.findall(t):
                if s not in cited_supp[key]:
                    cited_supp[key].append(s)
    for key in ('Fig.', 'Table'):
        if seen[key] != list(range(1, len(seen[key]) + 1)):
            errors.append(f'{key} numbering not 1..n: {seen[key]}')
        if cited[key] != sorted(cited[key]):
            errors.append(f'{key} first citations out of order: {cited[key]}')
        phantom = set(cited[key]) - set(seen[key])
        if phantom:
            errors.append(f'{key} cited but absent: {sorted(phantom)}')
    # supplement
    supp_seen = {'Fig.': [], 'Table': []}
    for kind, t in body_items(supp):
        if kind == 'P':
            m = CAP.match(t)
            if m and m.group(2).startswith('S'):
                supp_seen[m.group(1)].append(m.group(2))
    for key in ('Fig.', 'Table'):
        if supp_seen[key] != [f'S{i}' for i in range(1, len(supp_seen[key]) + 1)]:
            errors.append(f'supplementary {key} numbering not S1..Sn: {supp_seen[key]}')
        if set(supp_seen[key]) != set(cited_supp[key]):
            errors.append(f'supplementary {key}: cited {cited_supp[key]} vs present {supp_seen[key]}')
        if cited_supp[key] != sorted(cited_supp[key], key=lambda s: int(s[1:])):
            errors.append(f'supplementary {key} first citations out of order: {cited_supp[key]}')
    # English-only captions/tables (Latin script)
    for doc in (main, supp):
        for tbl in doc.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', cell.text):
                        errors.append(f'non-English table text: {cell.text[:40]}')
    if list(HERE.rglob('*.dot')):
        errors.append('.dot file present')
    return errors, seen, supp_seen, n_abs


def _only_captions_between(texts, a, b):
    return all(CAP.match(t) or not t for t in texts[a + 1:b])


def main():
    errors, seen, supp_seen, n_abs = check(Document(MAIN), Document(SUPP))
    print(f'main: {len(seen["Fig."])} figures, {len(seen["Table"])} tables; '
          f'supplement: {len(supp_seen["Fig."])} figures, {len(supp_seen["Table"])} tables; abstract {n_abs} words')
    for e in errors:
        print('ERROR:', e)
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
