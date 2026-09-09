# figure-making-WXL

Publication-ready matplotlib figures in the **WXL house style** for Elsevier,
IEEE and Springer submissions. Every text element is Times New Roman at a
uniform **10 pt**, so figure text matches Word 10 pt body text when the image is
inserted at its original size.

论文配图样式技能：Times New Roman 统一 10 pt、深蓝主色系、四边全包围、图例带黑框、
刻度朝内、无网格，图幅按 90 / 140 / 190 mm 印刷宽度校准。

## Install for an agent

The skill is a plain directory: no build step, no absolute paths, no config file.
Copy it into the skills folder the agent scans and it is live.

### 1. Put it in the agent's skills directory

| Runtime | Skills directory |
|---|---|
| DSH | `~/.dsh/skills/figure-making-WXL` |
| Claude Code | `~/.claude/skills/figure-making-WXL` |
| Other loaders | wherever the loader scans for `SKILL.md` |

```bash
git clone https://github.com/OolleyW/figure-making-WXL.git \
  ~/.dsh/skills/figure-making-WXL
```

Keep the directory name `figure-making-WXL`: loaders match it against the `name`
field in `SKILL.md`.

### 2. Install the Python dependencies

```bash
pip install -r ~/.dsh/skills/figure-making-WXL/requirements.txt
```

matplotlib ≥ 3.5, numpy, Pillow. `python-docx` is only used by the Word
assembly module; figures work without it.

### 3. Verify the machine can reproduce the style

```bash
python ~/.dsh/skills/figure-making-WXL/scripts/check_wxl_style.py
```

`RESULT: PASS` confirms the audit runs and the fonts resolve. If it reports a
font problem, install Times New Roman, or the metric-compatible Nimbus Roman
No9 L / Liberation Serif.

### 4. What the agent must do to stay on-style

1. `apply_wxl_style()` before creating any figure.
2. Draw only with `WXL_PALETTE` colors, black edges, no custom fonts or sizes.
3. `prepare_figure(fig)` then `check_wxl_style(fig)`; fix every reported problem.
4. `finalize_figure(fig, ..., target_width_mm=WXL_WIDTH_MM[preset])`.
5. Insert the PNG into Word at 100 %, or assemble the document with
   `assets/wxl_docx.py`.

The audit is the enforcement mechanism. It fails on a non-Times font, a non-10 pt
size, a hidden spine, a grid line, an outward tick, an unframed legend, an
off-palette color, or an axis end that is not on a tick value, so an agent that
runs it cannot silently drift off-style.

## Style contract

Before drawing **any** figure, confirm with the user the chart type, the x and y
axis labels (text, units, and whether each symbol is italic), the line style, and
the colours — the skill never decides these for them. See `references/preferences.md`.

| Item | Value |
|---|---|
| Target | Elsevier / IEEE / Springer |
| Font | Times New Roman + STIX math, SimSun for CJK |
| Type scale | uniform 10 pt (caption / label / tick / legend / annotation) |
| Palette | deep blue `#1F4E79` primary, `#B64342` contrast, `#2E8B7A` improve, `#E0A030` accent, `#7B7B7B` neutral, `#C9DCF0` light |
| Axes | full box, 0.8 pt spines |
| Legend | inside the axes, white face, black 0.8 pt border |
| Ticks | inward, no grid, both axis ends land on a tick label |
| Caption | below the figure, centered |
| Width | single 90 mm / onehalf 140 mm / double 190 mm |
| Export | PNG 600 dpi + vector PDF |

## Why the width matters

`bbox_inches="tight"` trims the canvas, so a figure authored at 190 mm usually
saves around 158 mm. Stretching that image to fill a 190 mm column scales every
glyph by 0.83 and silently turns 10 pt into 8.3 pt. `finalize_figure` therefore
takes `target_width_mm` and calibrates the canvas until the trimmed image is
exactly the print width. All 20 preview figures land within 0.5 mm of their
target.

## How to call the skill

The skill is a set of instructions plus a Python module. There are three ways in.

### A. Through an agent (the typical case)

An agent that has the skill installed loads it when the user asks for a
publication figure / 科研绘图 / 论文配图, then follows `SKILL.md`:

1. **Ask the user** for the chart type and panel count, the x / y axis labels
   (text, units, and whether each symbol is italic), the line style, and the
   colours. Do not decide these for them — see `references/preferences.md`.
2. `apply_wxl_style()`.
3. Draw with `WXL_PALETTE` colours and black edges; every label at 10 pt.
4. `prepare_figure(fig)` then `check_wxl_style(fig)`; fix every reported problem.
5. `finalize_figure(fig, ..., target_width_mm=WXL_WIDTH_MM[preset])`.
6. Insert the PNG into Word at 100 %, or assemble the document with
   `assets/wxl_docx.py`.

### B. Directly in Python

```python
import os
import sys
from pathlib import Path

# Wherever the skill is installed; WXL_SKILL_DIR overrides the default.
SKILL = Path(os.environ.get(
    "WXL_SKILL_DIR", Path.home() / ".dsh" / "skills" / "figure-making-WXL"))
sys.path.insert(0, str(SKILL / "assets"))

from wxl_style import (WXL_PALETTE as P, WXL_FIGSIZE, WXL_WIDTH_MM, apply_wxl_style,
                       create_subplots, framed_legend, add_caption_below,
                       finalize_figure, check_wxl_style, prepare_figure)

apply_wxl_style()
fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
ax.plot([1, 2, 3], [0.7, 0.85, 0.92], "-o", color=P["primary"], lw=1.5,
        ms=3.2, mfc="white", mew=0.9, label="Proposed")
ax.set_xlabel(r"Slip $s$ (mm)")          # symbol italic, unit upright
ax.set_ylabel(r"Bond stress $\tau$ (MPa)")
ax.set_ylim(0, 1.2)
framed_legend(ax, loc="upper left")
add_caption_below(fig, r"$\mathbf{Fig.}$  1  Bond stress against slip.")

prepare_figure(fig)
report = check_wxl_style(fig)          # audit before saving
assert report["ok"], report["problems"]
finalize_figure(fig, "figures/curve", formats=["png", "pdf"], dpi=600,
                target_width_mm=WXL_WIDTH_MM["double"])
```

A text variable goes in `$...$` (italic), a unit stays outside and upright:
`r"Slip $s$ (mm)"`, `r"Bond stress $\tau$ (MPa)"`. The figure caption is
`$\mathbf{Fig.}$  1  ...` so the "Fig." is bold and the number is not padded.

### C. From the command line

```bash
# verify the install on this machine
python "<skill-dir>/scripts/check_wxl_style.py"

# render all 20 chart types + an HTML gallery
python "<skill-dir>/examples/gallery.py" --out ./wxl_gallery

# every chart type at 90 mm and 190 mm in one Word document
python "<skill-dir>/examples/column_gallery.py" --out ./wxl_columns

# render three figures and assemble a Word report
python "<skill-dir>/examples/word_report.py" --out ./wxl_report
```


## Chart types (20)

Bar: grouped with error bars, stacked, horizontal.
Line: multi-series trend, trend + uncertainty band, stacked area.
Relationship: scatter + fit, bubble, bidirectional error bars.
Distribution: box, violin, histogram + KDE, ECDF, strip + mean.
Matrix: annotated heatmap, filled contour.
Special: radar, donut, dual axis, 2 × 2 multi-panel, 1 × 3 one-row multi-panel.

Runnable code for all of them is in `examples/gallery.py`; rendered previews are
in `preview/`. `heatmap`, `radar` and `donut` are rendered in single column only;
`multi_panel` and `multi_panel_1x3` in double column only. The `double` preset is
deliberately short (190 × 66 mm) with the 10 pt text unchanged.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | hard rules and when to load the skill |
| `references/preferences.md` | what to ask the user before plotting (labels, italic, type, style, colours) |
| `references/api.md` | constants, `WXLStyle`, signatures, audit contract |
| `references/design-theory.md` | why 10 pt, the tight-crop trap, palette semantics, exceptions |
| `references/common-patterns.md` | legend placement, multi-panel, dual axes, print-safe encoding |
| `references/tutorials.md` | three end-to-end walkthroughs |
| `references/demos.md` | the 20 chart types with core calls |
| `assets/wxl_style.py` | importable style module (rcParams, palette, helpers, audit) |
| `assets/wxl_docx.py` | Word assembly: 100 % insertion, captions, three-line tables |
| `scripts/check_wxl_style.py` | installation self-test |
| `examples/gallery.py` | render all 20 types + an HTML gallery |
| `examples/word_report.py` | render figures and assemble a Word report |
| `examples/column_gallery.py` | all 20 types at 90 mm and 190 mm in one Word document |
| `requirements.txt` | dependencies (python-docx optional) |
| `preview/*.png` | 300 dpi previews of the 20 chart types |

## Regenerate

```bash
# installation self-test
python "<skill-dir>/scripts/check_wxl_style.py"

# all 20 figures + HTML gallery (default output ~/wxl_gallery)
python "<skill-dir>/examples/gallery.py" --out ./wxl_gallery

# figures assembled into a Word report (needs python-docx)
python "<skill-dir>/examples/word_report.py" --out ./wxl_report

# every chart type at 90 mm and 190 mm in one Word document
python "<skill-dir>/examples/column_gallery.py" --out ./wxl_columns
```

## Word assembly

`assets/wxl_docx.py` (needs `python-docx`) applies the same contract to the
document: A4 with 10 mm side margins so the usable width is 190 mm, figures
inserted at 100 % of their measured physical width, captions below figures,
table captions above three-line tables, headings in black CJK serif bold with
double spacing, body text in Times New Roman 10 pt with a two-character indent.

```python
from wxl_docx import new_document, add_heading, add_figure_block, add_three_line_table

doc = new_document()
add_heading(doc, "1  Results")
add_figure_block(doc, "figures/accuracy.png", "Fig. 1  Accuracy across scenarios.")
add_three_line_table(doc, ["Method", "Accuracy"], [["Proposed", "0.94"]],
                     col_widths_cm=[12.0, 7.0], caption="表 1  Accuracy by method")
doc.save("report.docx")
```

## Requirements

Python 3.9+, `matplotlib` ≥ 3.5, `numpy`, `Pillow` (width measurement) — see
`requirements.txt`. Times New Roman is mandatory by name; on machines without it
the stack falls back to the metric-compatible Nimbus Roman No9 L or Liberation
Serif, which the audit accepts.

## Notes

- The style is enforced, not suggested: `check_wxl_style` fails on a non-Times
  font, a non-10 pt size, a hidden spine, a grid line, an outward tick, an
  unframed legend or an off-palette color.
- Documented exceptions: polar axes (radar) keep a light grid, pie/donut axes
  are turned off, colorbar axes are exempt from the four-spine rule.
- Slide export uses the `slide` preset; the 10 pt / print-width contract does
  not apply to slides.
