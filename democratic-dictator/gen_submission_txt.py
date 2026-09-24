import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / 'paper_draft_en.txt'
DEST = ROOT / 'paper_draft_en_submission.txt'

with open(SRC, 'r', encoding='utf-8') as f:
    lines = f.readlines()

fig_markers = []
fig_captions = []
out_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.rstrip('\n').rstrip()
    m = re.match(r'^\[FIGURE:(.+)\]$', stripped)
    if m:
        fig_markers.append(m.group(1).strip())
        # next non-empty line should be the caption; skip it in body and record
        j = i + 1
        while j < len(lines) and lines[j].strip() == '':
            j += 1
        if j < len(lines) and re.match(r'^Figure\s+\d+', lines[j].strip()):
            fig_captions.append(lines[j].rstrip('\n').strip())
            i = j + 1
            continue
    out_lines.append(line)
    i += 1

# Append figure legends before Data Availability if present, otherwise at end
legend_block = ['\nFigure Legends\n\n']
for cap in fig_captions:
    legend_block.append(cap + '\n\n')

# Insert legends before Data Availability if present
text = ''.join(out_lines)
da_match = re.search(r'\nData Availability\n', text)
if da_match:
    idx = da_match.start()
    text = text[:idx] + ''.join(legend_block) + '\n' + text[idx:]
else:
    text += ''.join(legend_block)

with open(DEST, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Updated {DEST}')
print('Captions appended:', len(fig_captions))
