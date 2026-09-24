"""Generate a standalone cover letter DOCX for CPE submission."""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = Path(__file__).parent
DEST = ROOT / 'cover_letter_en.docx'

# Extract cover letter from submission package manifest if available
src = ROOT / 'cpe_submission_package.md'
if src.exists():
    text = src.read_text(encoding='utf-8')
    start = text.find('## 8. Cover Letter (template)')
    body = text[start:].split('---')[0] if start != -1 else ''
    # drop heading line
    body = '\n'.join(line for line in body.splitlines()[1:] if line.strip())
else:
    body = ''

def add_para(doc, text, bold=False, italic=False, alignment=None, space_after=Pt(12)):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    p.paragraph_format.space_after = space_after
    if alignment:
        p.alignment = alignment
    return p

doc = Document()
section = doc.sections[0]
section.page_height = Inches(11)
section.page_width = Inches(8.5)
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)

add_para(doc, '[Date]', alignment=WD_ALIGN_PARAGRAPH.RIGHT)
add_para(doc, 'The Editors')
add_para(doc, 'Constitutional Political Economy')
add_para(doc, 'Springer Nature')
add_para(doc, '[Editor-in-Chief or Handling Editor name, if known]')
add_para(doc, '')

if body:
    for line in body.splitlines():
        if line.startswith('Dear'):
            add_para(doc, line)
        elif line.startswith('Sincerely'):
            add_para(doc, '', space_after=Pt(6))
            add_para(doc, line)
        elif line.startswith('Tatsuki Onishi') or line.startswith('['):
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        else:
            p = add_para(doc, line, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=Pt(6))
            # strip leading markdown bold/italic markers for Word formatting
            for run in p.runs:
                run.text = run.text.replace('**', '').replace('*', '')
else:
    add_para(doc, 'Dear Editors,')
    add_para(doc, (
        'We are pleased to submit our manuscript, "Democracy as Control over Delegated Authority: '
        'Constitutional Design under Periodic Delegation," for consideration as an Original Paper in '
        'Constitutional Political Economy.'
    ))
    add_para(doc, 'Sincerely,')
    add_para(doc, 'Tatsuki Onishi')
    add_para(doc, '[Affiliation]')
    add_para(doc, '[Email]')

DEST.unlink(missing_ok=True)
doc.save(DEST)
print(f'Saved {DEST}')
