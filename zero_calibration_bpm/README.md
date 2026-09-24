# What zeroing cannot fix — IEEE TIM submission

Reproducible simulation + real-waveform validation study for *IEEE Transactions on
Instrumentation and Measurement*:
**"What zeroing cannot fix: detecting residual gain and dynamic-response
errors after zero calibration in invasive arterial pressure monitoring."**

Zero calibration of an invasive arterial pressure transducer removes the
direct-current (DC) offset but cannot correct the transducer gain (scale) or
the frequency-dependent damping of a fluid-filled catheter–transducer system.
This project quantifies which of the analyses commonly reported in
device-validation studies actually detect a residual gain error after zeroing,
and adds a real-waveform validation using the public VitalDB Open Dataset
(SNUADC/ART track).

> The simulation data are **synthetic** (seeded, reproducible). The
> real-waveform validation uses the **VitalDB Open Dataset**, which is publicly
> available at https://api.vitaldb.net/.

## Reproducing everything

```bash
pip install -r requirements.txt
python3 scripts/build_all.py      # or: make all
```

This regenerates, in order:

1. `data/*.csv` — synthetic static, dynamic and range-dependence datasets, plus
   the extracted real-waveform beat pairs and example waveform segment.
2. `results/*.csv` and `results/summary.json` — machine-readable metrics for
   the simulation and real-waveform analyses.
3. `figures/*.png` (English), `figures/pdf/*.pdf` (English vector copies),
   `figures/tiff/*.tif` (English, 300 dpi), and `figures/submission/*.tif`
   (numbered submission figures).
4. `manuscripts/TIM_ZeroFree_Manuscript_EN.docx` — main manuscript with inline
   figures and tables (Word OMML equations, numbered references by first
   appearance).
5. `manuscripts/TIM_Tables_EN.docx` — editable separate tables.
6. `manuscripts/TIM_Figures_EN.pptx` — editable figure deck (one slide per
   figure).
7. `cover_letter/TIM_Cover_Letter_EN.docx` — cover letter for IEEE TIM.

Two further steps are run separately because they need an input that is not
redistributed here (the IEEE template) or only produce a package:

```bash
python3 scripts/format_to_ieee_template.py --template /path/to/Transactions-template.docx
python3 scripts/make_submission_zip.py
```

To show what changed between two revisions of the manuscript (insertions in
red, deletions in blue strike-through):

```bash
python3 scripts/make_tracked_changes.py \
    --old previous.docx \
    --new manuscripts/TIM_ZeroFree_Manuscript_EN_formatted.docx \
    --out manuscripts/TIM_ZeroFree_Manuscript_EN_tracked.docx
```

Every number, table and figure in the manuscripts is read from
`results/summary.json`; **no results are hard-coded** in the manuscript
generators.

## IEEE TIM submission notes

The English manuscript is formatted as an *Original Article* for *IEEE
Transactions on Instrumentation and Measurement*: structured abstract under 300
words, main text of approximately 4,200 words, and seven inline figures plus
three inline tables. Section II positions the work against the I&M literature,
as required by the journal's screening criteria. In-text citations use bracketed Arabic numerals (`[1]`,
`[1,2]`) numbered in order of first appearance; the reference list follows the
journal's conventions. Equations are rendered as Word-native OMML (not LaTeX).
Ethics status (VitalDB Open Dataset; no new human/animal participants) and use
of an AI coding assistant are disclosed in the Methods; conflicts of interest
and funding appear on the title page.

## Layout

| Path | Contents |
|------|----------|
| `src/methods.py` | Pure statistics/signal functions (CCC, Bland–Altman + proportional-bias regression, Deming, Passing–Bablok, second-order dynamic response) |
| `src/simulate.py` | Seeded synthetic data generation |
| `src/real_waveforms.py` | Downloads/reads VitalDB SNUADC/ART waveforms and extracts paired beats |
| `src/analyze.py` | Consumes `data/`, writes `results/` |
| `src/figures.py` | Figures from `data/` + `results/` (EN + JA, plus TIFF/PDF/submission exports) |
| `scripts/manuscript_common.py` | Vancouver citation manager + results loader |
| `scripts/create_bpm_docx_en.py` | English TIM manuscript generator |
| `scripts/create_tables_docx_en.py` | Editable separate tables |
| `scripts/create_figures_pptx_en.py` | Editable figure deck |
| `scripts/create_tim_cover_letter.py` | Cover letter |
| `scripts/build_all.py` | One-command reproduction pipeline |
| `scripts/format_to_ieee_template.py` | Applies the IEEE Transactions template styles/layout to the generated manuscript and appends the author biography (requires the template docx from IEEE Author Center, passed with `--template`) |
| `scripts/make_submission_zip.py` | Packages manuscript, tables, figures, cover letter and replication code into `TIM_submission.zip` |
| `scripts/make_tracked_changes.py` | Marks up the differences between two manuscript revisions (red insertions, blue struck-through deletions) |

## Method summary

- **Static scenarios** (n per scenario fixed in `src/simulate.py`): offset
  only, ideal zeroing, uncompensated gain error, and a gain error masked by a
  compensating offset.
- **Analyses**: mean bias + 95% limits of agreement, Bland–Altman
  difference-versus-mean regression, Deming and Passing–Bablok regression,
  and Lin's concordance correlation coefficient (CCC) with decomposition into
  precision (r), bias-correction factor (C_b), location shift (u) and scale
  shift (v).
- **Dynamic scenarios**: synthetic arterial waveforms passed through optimal,
  under-damped and over-damped second-order catheter–transducer models;
  fast-flush parameters (natural frequency, damping) are the direct diagnostic.
- **Range-dependence**: one fixed device sampled over pressure ranges of
  increasing width to illustrate CCC range-dependence.
- **Real-waveform validation**: beats from the VitalDB SNUADC/ART track are
  rescaled to introduce the same four static scenarios and then re-analysed
  with the same metrics.
