#!/usr/bin/env python3
"""Shared DOCX/PPTX helpers for manuscript generation."""

import os
import re
import shutil
import tempfile
import zipfile


def count_docx_words(docx_path, include_fig_legend=True, include_refs=True,
                     include_declarations=True):
    """Approximate word count from a python-docx generated manuscript."""
    from docx import Document
    doc = Document(docx_path)
    ref_block = False
    text = []
    for p in doc.paragraphs:
        t = p.text
        if t.startswith("References"):
            ref_block = True
        if not include_refs and ref_block and re.match(r'^\d+\.\s', t):
            continue
        if not include_fig_legend and t.startswith("Figure 1."):
            continue
        if not include_declarations and t.startswith((
            "Ethics approval", "Availability of data",
            "Competing interests", "Funding",
            "Consent for publication", "Authors' contributions"
        )):
            continue
        text.append(t)
    full = ' '.join(text)
    return len(full.split())


def sanitize_ooxml_package(package_path):
    """Remove CJK/fullwidth font entries from OOXML theme/fontTable XML.

    This keeps the visible text unchanged while ensuring that no double-byte
    characters remain anywhere in the generated DOCX/PPTX archive.
    """
    temp_path = tempfile.mktemp(suffix=os.path.splitext(package_path)[1])
    cjk_re = re.compile(r'[\uFF01-\uFF5E\u3000\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF]')

    with zipfile.ZipFile(package_path, 'r') as zin, \
         zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith('.xml'):
                try:
                    xml = data.decode('utf-8')
                    # Theme files: drop CJK script font entries (Jpan/Hang/Hans/Hant)
                    if 'theme' in item.filename.lower():
                        xml = re.sub(
                            r'<a:font\s+script="(?:Jpan|Hang|Hans|Hant)"[^/]*/>',
                            '', xml
                        )
                    # Font tables: drop any font whose name contains CJK characters
                    if 'fontTable' in item.filename or 'font' in item.filename.lower():
                        # For Word fontTable.xml entries
                        xml = re.sub(
                            r'<w:font\s+w:name="[^"]*['
                            r'\uFF01-\uFF5E\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF'
                            r'][^"]*">.*?</w:font>\s*',
                            '', xml, flags=re.DOTALL
                        )
                        # Remove any stray CJK typeface attributes in theme-like XML inside ppt
                        xml = re.sub(
                            r'<a:font\s+script="(?:Jpan|Hang|Hans|Hant)"[^/]*/>',
                            '', xml
                        )
                        xml = re.sub(
                            r'typeface="[^"]*['
                            r'\uFF01-\uFF5E\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3400-\u4DBF'
                            r'][^"]*"',
                            'typeface="Arial"', xml
                        )
                    data = xml.encode('utf-8')
                except UnicodeDecodeError:
                    pass
            zout.writestr(item, data)

    shutil.move(temp_path, package_path)
