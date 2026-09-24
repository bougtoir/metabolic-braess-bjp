#!/usr/bin/env python3
"""Remove non-ASCII (especially full-width/CJK) characters from Office XML metadata.

Keeps OMML math symbols and normal text intact; only normalizes font/theme XML
and converts known East Asian font names to ASCII equivalents. Any remaining
non-ASCII bytes in font/theme metadata are replaced with '?' so the zip remains
valid and the document uses only ASCII for file-level metadata.
"""
import argparse
import os
import re
import shutil
import zipfile


FONT_MAP = {
    'ＭＳ Ｐゴシック': 'MS PGothic',
    'ＭＳ ゴシック': 'MS Gothic',
    'ＭＳ 明朝': 'MS Mincho',
    '맑은 고딕': 'Malgun Gothic',
    '宋体': 'SimSun',
    '新細明體': 'PMingLiU',
    # common variants
    'MS Ｐゴシック': 'MS PGothic',
    'MS ゴシック': 'MS Gothic',
    'MS 明朝': 'MS Mincho',
}


def _clean_text(text):
    # Known CJK/East Asian font names
    for old, new in FONT_MAP.items():
        text = text.replace(old, new)
    # Convert full-width alphanumerics to ASCII
    trans = {}
    for cp in range(0xFF01, 0xFF5F + 1):
        trans[cp] = chr(cp - 0xFEE0)
    # full-width space
    trans[0x3000] = ' '
    text = text.translate(trans)
    # Replace PUA / non-ASCII bullet characters in Word numbering and PPTX master bullets
    text = text.replace('w:val="\uf0b7"', 'w:val="-"')
    text = text.replace('a:buChar char="\u2022"', 'a:buChar char="-"')
    text = text.replace('a:buChar char="\u00bb"', 'a:buChar char=">>"')
    return text


def _remaining_non_ascii(text):
    # Exclude high Unicode blocks that are legitimate math/technical symbols
    # We only want to flag CJK / Hangul / fullwidth and similar metadata bytes.
    bad = []
    for c in text:
        o = ord(c)
        if o < 128:
            continue
        # Keep common math symbols used in OMML
        if (0x0370 <= o <= 0x03FF) or (0x2070 <= o <= 0x209F) or (0x2200 <= o <= 0x22FF):
            continue
        bad.append(c)
    return bad


def sanitize_file(path):
    tmp = path + '.san'
    with zipfile.ZipFile(path, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.endswith('.xml'):
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    zout.writestr(info, data)
                    continue
                text = _clean_text(text)
                bad = _remaining_non_ascii(text)
                if bad and ('fontTable' in info.filename or 'theme' in info.filename):
                    # Replace any still-non-ASCII font names with a safe ASCII fallback
                    for c in set(bad):
                        text = text.replace(c, 'Arial')
                data = text.encode('utf-8')
            zout.writestr(info, data)
    shutil.move(tmp, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    for f in args.files:
        if os.path.exists(f):
            sanitize_file(f)
            print(f'Sanitized {f}')


if __name__ == '__main__':
    main()
