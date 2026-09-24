"""Final-check script for the EHPM R4 manuscript."""
import re
from collections import OrderedDict
from docx import Document

DOCX = 'output/docx/Healthcare_EHPM_Manuscript_R4.docx'

# Tokens that precede figure/table numbers (e.g. 'Figure 1', 'Table 2') -- not reference citations.
NON_CITATION_TOKENS = frozenset({'figure', 'fig', 'figures', 'table', 'tables'})

CITE_RE = re.compile(
    r'(?:[1-9]|[12]\d)(?!\d)'
    r'(?:,(?:[1-9]|[12]\d)(?!\d))*'
    r'(?:[-\u2013\u2014](?:[1-9]|[12]\d)(?!\d))?'
)


def parse_citation_text(txt):
    """Return a list of reference numbers from a citation cluster.
    Handles '1', '1,23', '15-19', '6-10,12' etc."""
    nums = []
    for part in re.split(r'[,;]', txt):
        part = part.strip()
        if not part:
            continue
        if '-' in part or '\u2013' in part or '\u2014' in part:
            m = re.match(r'(\d+)\s*[-\u2013\u2014]\s*(\d+)$', part)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                nums.extend(range(a, b + 1))
        elif part.isdigit():
            nums.append(int(part))
    return nums


def _after_cluster_ok(text, end):
    """Exclude decimals, 4-digit years, and counts that are followed by a word."""
    if end >= len(text):
        return True
    after = text[end]
    # A citation is normally followed by punctuation/end-of-string, not by a word.
    # Reject counts like '12 other', '2 years', '4 million'.
    if after.isspace():
        i = end + 1
        while i < len(text) and text[i].isspace():
            i += 1
        if i < len(text) and text[i].isalpha():
            return False
    if after.isdigit():
        return False
    if after == '.' and end + 1 < len(text) and text[end + 1].isdigit():
        return False
    # '1' in '1,000' (thousands separator)
    if after == ',' and end + 3 < len(text) and text[end + 1:end + 4].isdigit():
        return False
    if after == '%':
        return False
    # '1' in '1-year-old' or '2-year steps' is a count, not a citation
    if after in '-\u2013\u2014' and end + 1 < len(text) and text[end + 1].isalpha():
        return False
    return True


def _is_model_or_subscript_digit(text, start, cluster):
    """Return True if a digit is part of M0-M9 or a subscript letter (e.g. μ_H1)."""
    # M1, M2, etc.
    if len(cluster) == 1 and cluster.isdigit() and start >= 1:
        if text[start - 1] == 'M':
            return True
        # subscript pattern: _X<digit> (e.g. μ_H1, t₀ is not ASCII digit)
        m = re.search(r'([A-Za-z])_$', text[:start])
        if m and text[start - 2:start - 1] == '_':
            return True
    return False


def is_citation_usage(text, match):
    """Decide whether a numeric cluster is a Vancouver citation in this context."""
    cluster = match.group(0)
    start = match.start()
    end = match.end()
    if not _after_cluster_ok(text, end):
        return False
    nums = parse_citation_text(cluster)
    if not nums or any(n < 1 or n > 29 for n in nums):
        return False
    if _is_model_or_subscript_digit(text, start, cluster):
        return False
    if start == 0:
        after_nonspace = text[end:].lstrip()
        if after_nonspace and after_nonspace[0].isalpha():
            return False
        # Standalone number in a table cell (e.g. '3' for parameter count) is not a citation
        if text.strip() == cluster:
            return False
        return True
    # If already separated by a space, look at the preceding token.
    if text[start - 1].isspace():
        token_match = re.search(r'\S+$', text[:start].rstrip())
        if not token_match:
            return False
        token = token_match.group(0)
        if token[-1] in ')]':
            return True
        if token[-1].isalpha() and token != 'M':
            if token.lower().rstrip('.') in NON_CITATION_TOKENS:
                return False
            return True
        if token[-1].isdigit():
            # Year-citation boundary (e.g. 2023 1,23)
            if re.fullmatch(r'\d{4}', token):
                before_idx = start - len(token) - 2
                if before_idx < 0 or not text[before_idx].isalnum():
                    return True
        return False
    # Glued to preceding character
    before = text[start - 1]
    if before in ")]'\"\u201d":
        return True
    if before.isalpha():
        m = re.search(r'([A-Za-z]+)$', text[:start])
        if m and m.group(1) == 'M' and cluster in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            return False
        if m and m.group(1).lower().rstrip('.') in NON_CITATION_TOKENS:
            return False
        # subscript letter before digit (e.g. H in μ_H1)
        if start >= 2 and text[start - 2] == '_':
            return False
        return True
    if before.isdigit():
        m = re.search(r'\d+$', text[:start])
        if m and len(m.group(0)) == 4:
            before_idx = start - 5
            if before_idx < 0 or not text[before_idx].isalnum():
                return True
        return False
    return False


def extract_citations(text):
    """Return list of citation numbers found in a paragraph or run."""
    found = []
    for m in CITE_RE.finditer(text):
        if is_citation_usage(text, m):
            found.extend(parse_citation_text(m.group(0)))
    return found


def iter_text_nodes(doc, refs_start):
    """Yield body paragraph and table-cell paragraph text before References."""
    for i, p in enumerate(doc.paragraphs):
        if i == refs_start:
            break
        yield p.text
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p.text


def main():
    doc = Document(DOCX)

    all_paras = [p.text.strip() for p in doc.paragraphs]
    refs_start = None
    for i, t in enumerate(all_paras):
        if t == 'References':
            refs_start = i
            break
    if refs_start is None:
        refs_start = len(all_paras)

    body_paras = all_paras[:refs_start]

    # --- Figures / Tables ---
    fig_caps = {}
    tbl_caps = {}
    for i, t in enumerate(all_paras):
        m = re.match(r'(?i)^Figure\s+(\d+)\.\s*(.*)', t)
        if m:
            fig_caps[int(m.group(1))] = (i, m.group(2))
        m = re.match(r'(?i)^Table\s+(\d+)\.\s*(.*)', t)
        if m:
            tbl_caps[int(m.group(1))] = (i, m.group(2))

    fig_cites = set()
    tbl_cites = set()
    first_fig_cite = {}
    first_tbl_cite = {}
    for i, p in enumerate(body_paras):
        for m in re.finditer(r'(?i)Fig(?:ure)?\.?\s*(\d+)', p):
            n = int(m.group(1))
            fig_cites.add(n)
            if n not in first_fig_cite:
                first_fig_cite[n] = i
        for m in re.finditer(r'(?i)Table\s+(\d+)', p):
            n = int(m.group(1))
            tbl_cites.add(n)
            if n not in first_tbl_cite:
                first_tbl_cite[n] = i

    print('=== Figure / Table check ===')
    print(f'In-text figure citations: {sorted(fig_cites)}')
    print(f'Figure captions present:   {sorted(fig_caps)}')
    print(f'In-text table citations:   {sorted(tbl_cites)}')
    print(f'Table captions present:    {sorted(tbl_caps)}')

    issues = []
    for n in fig_cites:
        if n not in fig_caps:
            issues.append(f'Figure {n} cited but no caption')
    for n in fig_caps:
        if n not in fig_cites:
            issues.append(f'Figure {n} caption not cited')
    for n in tbl_cites:
        if n not in tbl_caps:
            issues.append(f'Table {n} cited but no caption')
    for n in tbl_caps:
        if n not in tbl_cites:
            issues.append(f'Table {n} caption not cited')

    order_issues = []
    for n in sorted(fig_cites & set(fig_caps)):
        if first_fig_cite[n] > fig_caps[n][0]:
            order_issues.append(f'Figure {n}: first citation after caption (para {first_fig_cite[n]} > {fig_caps[n][0]})')
    for n in sorted(tbl_cites & set(tbl_caps)):
        if first_tbl_cite[n] > tbl_caps[n][0]:
            order_issues.append(f'Table {n}: first citation after caption (para {first_tbl_cite[n]} > {tbl_caps[n][0]})')

    if issues:
        for issue in issues:
            print('WARNING:', issue)
    else:
        print('OK: all figures/tables are cited and captioned')

    if order_issues:
        for issue in order_issues:
            print('ORDER ISSUE:', issue)
    else:
        print('OK: all figures/tables cited before their captions')

    # --- References / citations ---
    refs = OrderedDict()
    for t in all_paras[refs_start + 1:]:
        m = re.match(r'^(\d+)\.\s+', t)
        if m:
            refs[int(m.group(1))] = t[m.end():].strip()

    cite_counts = {}
    first_use = []
    seen = set()
    for text in iter_text_nodes(doc, refs_start):
        for n in extract_citations(text):
            cite_counts[n] = cite_counts.get(n, 0) + 1
            if n not in seen:
                seen.add(n)
                first_use.append(n)

    print('\n=== Reference check ===')
    print(f'References in list: {len(refs)}')
    print(f'Unique citation numbers used: {sorted(cite_counts.keys())}')
    print(f'First-use order: {first_use}')

    orphan_cites = [n for n in cite_counts if n not in refs]
    orphan_refs = [n for n in refs if n not in cite_counts]
    if orphan_cites:
        print('ERROR: citations not in reference list:', orphan_cites)
    else:
        print('OK: all citations have reference list entries')
    if orphan_refs:
        print('WARNING: references not cited in body/tables:', orphan_refs)
    else:
        print('OK: all reference list entries are cited')

    expected = list(range(1, len(first_use) + 1))
    if first_use == expected:
        print(f'OK: first-use citations are sequential 1..{len(expected)}')
    else:
        print('WARNING: first-use citation order is not sequential')
        print('  expected:', expected)
        print('  actual:  ', first_use)

    # Word counts
    body_text = ' '.join(body_paras)
    word_count = len(re.findall(r'\w+', body_text))
    print('\n=== Word / structure check ===')
    print(f'Paragraph count (body): {len(body_paras)}')
    print(f'Approx word count (body, incl refs? no): {word_count}')
    print(f'Total paragraphs in docx: {len(all_paras)}')


if __name__ == '__main__':
    main()
