---
name: figure-making-wxl
description: >-
  Publication-ready matplotlib figures in the WXL house style for Elsevier,
  IEEE and Springer submissions: every text element is Times New Roman at
  11 pt (legend at 10 pt), with a deep-blue semantic palette, full-box axes,
  framed in-plot legends, inward ticks, no grid, captions below the figure, and
  figure widths fixed to the final print width (90 / 140 / 190 mm). Before
  plotting it always asks the user for the chart type, the x/y axis labels (and
  whether each symbol is italic), the line style and the colours. Covers 21
  chart types (grouped/stacked/horizontal bars, trend lines, uncertainty bands,
  stacked areas, scatter, bubble, error bars, box, violin, histogram + KDE,
  ECDF, strip+mean, heatmap, filled contour, radar, donut, dual axis, multi
  panel 2 × 2 and 1 × 3) with a machine-checked style audit. Use when the user asks for
  publication figures, 论文配图, 科研绘图, 画图/作图 with matplotlib, or wants
  figures in "WXL 风格" / "我的绘图风格" / matching Word 11 pt text. Do not use
  for interactive dashboards or web viz (Plotly, Altair, Bokeh), exploratory
  plots with no publication target, Origin/OriginPro automation (use the
  editaplot skill), or Illustrator/Figma-first infographics.
---

# figure-making-WXL

Publication figures in the WXL house style. Open `references/` only as needed;
do not preload every file. Start from the table at the bottom, then follow links
inside the document you opened.

## Installation

This skill is self-contained and has no absolute paths. To install it on another
machine or for another agent:

1. **Copy the whole `figure-making-wxl` directory** into that agent's skills
   directory. Common locations are `~/.dsh/skills/` (DSH) and
   `~/.claude/skills/` (Claude Code). Keep the directory name.
2. **Install the Python dependencies**: `pip install -r requirements.txt`
   (matplotlib ≥ 3.5, numpy, Pillow, and python-docx for the Word assembly
   module in `assets/wxl_docx.py`). The core style module needs only the first
   three.
3. **Verify the machine can reproduce the style**:
   `python "<skill-dir>/scripts/check_wxl_style.py"` must print
   `RESULT: PASS`. If it reports a font problem, install Times New Roman (or the
   metric-compatible Nimbus Roman No9 L / Liberation Serif) and rerun.
4. **Point your scripts at the skill** with the idiom in Quickstart below. Your
   skill loader already knows the directory; `WXL_SKILL_DIR` overrides the
   default `~/.dsh/skills/figure-making-wxl`.

Nothing else needs configuring. See the Portability section for what is
guaranteed on any conforming machine and what varies with the installed fonts.

## Hard rules (non-negotiable)

These rules supersede any conflicting style text in `references/` or in upstream
`figure_*` demos.

1. **Times New Roman everywhere.** Titles, axis labels, ticks, legends,
   annotations, colorbar labels. Math uses `mathtext.fontset = "stix"`, and
   `axes.unicode_minus = False` because Times New Roman lacks U+2212. Bold and
   italic Times faces are allowed; never Helvetica, Arial or DejaVu Sans. CJK
   text falls back to SimSun.
2. **11 pt body, 10 pt legend.** Caption, axis label, tick and annotation are
   11 pt; the legend text is 10 pt. The contract is checked; do not hand-tune
   individual sizes.
3. **Figure width = final print width.** `single` = 90 mm (3.54 in),
   `onehalf` = 140 mm (5.51 in), `double` = 190 mm (7.48 in). 11 pt in the
   figure equals Word 11 pt only when the image is inserted at its original
   size, so never design a wide figure and let Word shrink it. Because
   `bbox_inches="tight"` trims the canvas, always pass
   `target_width_mm=WXL_WIDTH_MM[preset]` to `finalize_figure` so the saved
   image is exactly the print width instead of ~17 % narrower.
4. **One fixed black frame for every single-column figure.** `finalize_figure`
   puts single-column output on the shared `WXL_AXES_SINGLE_MM = (75 × 55 mm)`
   box, centred, so every rectilinear figure's black frame is the same size and
   never adapts to its tick labels. The saved width therefore follows the labels
   (roughly 87–102 mm) rather than being pinned to 90 mm; that is intended, and
   the width audit does not pin the single-column variant. Colorbars are tucked
   against their host; polar axes and pies have no rectangular frame. A
   multi-panel figure brings each subplot to `WXL_AXES_PANEL_MM` (75 × 55 mm)
   without touching the spacing.
5. **Full box on every Cartesian axes.** All four spines drawn at 0.8 pt.
   Exceptions: polar axes (radar), axes with `axison = False` (pie/donut) and
   colorbar axes.
6. **Legend inside the axes, framed, and never covering data.** Opaque white
   face, black 0.8 pt border, `framealpha = 1`. Placement is automatic:
   `prepare_figure` (called by `finalize_figure`) measures the real overlap
   between the legend box and the plotted lines, bars and points, tries the nine
   candidate positions, and if none is clear it grows the y-range and retries.
   `check_wxl_style` reports any legend that still covers more than 2 % of the
   data. Use `ncol` for long label lists, and fall back to a dedicated legend
   panel only when no position works. Never place it outside the figure.
7. **Ticks point inward, no grid, and both axis ends land on a tick value.**
   Ticks are 3 pt long at 0.8 pt width. Every numeric Cartesian axis must start
   and end exactly on its first and last tick label, so a reader never sees an
   unlabelled strip at either end. `finalize_figure` calls `lock_axis_ends_all`
   automatically, and `check_wxl_style` fails a figure whose axis ends are not on
   tick values. The only grid exception is the radar chart, which keeps a light
   neutral grid so the values stay readable. Image axes (heatmaps), polar axes,
   colorbar axes and pie/donut axes are exempt because their ticks are
   categorical and already span the full extent.
8. **Caption below the figure**, centered, via `add_caption`. Never
   `fig.suptitle` and never a title on top of the axes. Panel labels go just
   below their own panel, centered, **not bold**, and carry a number plus a short
   title (`(a) Grouped bars`), not a bare `(a)`.
9. **Deep-blue palette only.** Colors come from `WXL_PALETTE`; black, white and
   the palette are the only allowed colors. See `references/design-theory.md`
   for the semantics.
10. **Export PNG 600 dpi + PDF vector.** Saving uses `bbox_inches="tight"` so
    the below-figure caption survives.
11. **Run the audit.** Call `check_wxl_style(fig)` before saving and fix every
    reported problem.
12. **No text over the data.** Legends, value labels, annotations and tick labels
    must not cover the plotted artists. `prepare_figure` measures every text box
    against the lines, bars, points and other text: it nudges colliding
    annotations to a free offset, thins crowded tick labels by increasing the
    step, and drops bar labels that are wider than their own bar at the final
    canvas size. `check_wxl_style` reports any remaining collision. When a label
    cannot be placed legibly, drop it rather than printing overlapping numbers.

13. **Ask before you plot; do not decide for the user.** Before drawing, confirm
    four things in a single question set: the **chart type** and how many panels,
    the **x and y axis labels** (text, units, and whether each symbol is
    italic), the **line style** (markers, width, dash pattern), and the
    **colours** (per-series mapping and, for matrices, the colormap). Offer a
    recommended default but do not apply anything until the user picks. Do not
    silently reuse a previous figure's choices without asking. See
    `references/preferences.md` for the exact questions and how to map the
    answers to code.

## Ask before you plot (short version)

| Decision | What to ask | Default to offer |
|---|---|---|
| Chart type | which chart, how many panels | grouped bar / trend / ... |
| Axis labels | x and y text, units, italic or not | italic symbol, upright unit |
| Line style | markers, width, dash pattern | open markers, 1.5 pt, solid |
| Colours | per-series colours; colormap for matrices | deep-blue `WXL_PALETTE` |

For a variable, italicise the symbol and keep the unit upright, e.g.
`r"Slip $s$ (mm)"` and `r"Bond stress $\tau$ (MPa)"`.

## Quickstart

```python
import os
import sys
from pathlib import Path

# Point this at wherever the skill is installed. Your skill loader knows the
# directory; WXL_SKILL_DIR overrides it, and the default assumes ~/.dsh/skills.
SKILL = Path(os.environ.get(
    "WXL_SKILL_DIR", Path.home() / ".dsh" / "skills" / "figure-making-wxl"))
sys.path.insert(0, str(SKILL / "assets"))

from wxl_style import (WXL_PALETTE as P, WXL_FIGSIZE, apply_wxl_style,
                       create_subplots, framed_legend, add_caption,
                       finalize_figure, check_wxl_style)

apply_wxl_style()
fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
ax.bar([1, 2, 3], [0.7, 0.85, 0.92], color=P["primary"],
       edgecolor="black", linewidth=0.8, label="Proposed")
ax.set_xlabel("Scenario")
ax.set_ylabel("Accuracy")
ax.set_ylim(0, 1.2)
framed_legend(ax, loc="upper left")
add_caption(fig, "Fig. 1  Accuracy across three scenarios.")

report = check_wxl_style(fig)          # audit before saving
assert report["ok"], report["problems"]
finalize_figure(fig, "figures/accuracy", formats=["png", "pdf"], dpi=600)
```

The 21 chart types the style covers, each with its core call, are listed in
`references/demos.md`; runnable code for all of them lives in
`examples/gallery.py`.

## Assembling the figures into Word

`assets/wxl_docx.py` turns finished figures into a manuscript-ready `.docx`
(requires `python-docx`). It applies the same paper contract the figures follow:
A4 with 10 mm side margins so the usable width is exactly 190 mm, figures
inserted at 100 % of their measured physical width, captions below figures,
table captions above three-line tables, section headings in black CJK serif bold
with double spacing, body text in Times New Roman 11 pt with a two-character
first-line indent.

```python
from wxl_docx import (new_document, add_heading, add_paragraph,
                      add_figure_block, add_three_line_table)

doc = new_document()                       # A4, 190 mm usable width
add_paragraph(doc, "Results are shown in Fig. 1.", spacing=1.5)
add_heading(doc, "1  Results")
add_figure_block(doc, "figures/accuracy.png", "Fig. 1  Accuracy across scenarios.",
                 dpi=600)
add_three_line_table(doc, ["Method", "Accuracy"], [["Proposed", "0.94"]],
                     col_widths_cm=[12.0, 7.0],
                     caption="表 1  Accuracy by method")
doc.save("report.docx")
```

A complete runnable pipeline (render three figures, audit them, assemble the
document, print the inserted widths) is `examples/word_report.py`:

```bash
python "<skill-dir>/examples/word_report.py" --out ./wxl_report
```

Figures must come from `finalize_figure(..., target_width_mm=...)` so their
physical width is the print width; otherwise `add_figure` inserts a wrongly sized
image and the 11 pt match is lost.

## Portability (another machine or another agent)

The skill is self-contained and has no absolute paths. Scripts resolve the skill
directory from `__file__`; the docs use `<skill-dir>`. Install it by copying the
whole `figure-making-wxl` directory into the target agent's skills directory,
then run `scripts/check_wxl_style.py` to confirm the machine can reproduce the
style.

| Requirement | Behaviour |
|---|---|
| Python | 3.9 or newer. |
| `matplotlib` ≥ 3.5, `numpy`, `Pillow` | See `requirements.txt`. Pillow is only used to measure saved image width. |
| Times New Roman | Mandatory **by name**. Present on Windows and on macOS with Office. On Linux the stack falls back to Nimbus Roman No9 L or Liberation Serif, which are metric-compatible Times clones, and `check_wxl_style` accepts them. A few glyph details differ. |
| CJK text | SimSun on Windows. Elsewhere install a CJK serif (Noto Serif CJK, Songti) or keep figure text in English. |
| `legend.set_ncols` | Used for the flatten fallback when available (matplotlib ≥ 3.6); skipped silently otherwise. |
| `python-docx` | Only imported by `assets/wxl_docx.py`; the core style module never imports it. Figures work without it. |

What is guaranteed on any conforming machine: 11 pt Times text, the deep-blue
palette, full-box axes, framed legends placed by measured overlap, inward ticks,
axis ends on tick values, the 90 / 140 / 190 mm width calibration, and a
`check_wxl_style` audit that fails on any deviation.

## When to load this skill

- Matplotlib figures for **Elsevier / IEEE / Springer** manuscripts, theses or
  reports that must match the WXL look (11 pt Times, deep blue, full box).
- Requests for **论文配图 / 科研绘图 / 画图** where the figure will be pasted
  into Word and should match 11 pt body text.
- Any of the 21 chart types in `references/demos.md`, or multi-panel layouts.

## When not to load

- **Plotly, Altair, Bokeh** or other interactive / web-first plotting.
- **Origin / OriginPro** automation (use the `editaplot` skill).
- **Exploratory** plots with no publication target.
- **3D, GIS** or **Illustrator / Figma-first** infographics.

## Related files

| File | Open when |
|------|-----------|
| [references/preferences.md](references/preferences.md) | The four questions to ask before plotting, and how to map the answers |
| [references/api.md](references/api.md) | Function signatures, `WXL_PALETTE`, `WXLStyle`, validation rules |
| [references/design-theory.md](references/design-theory.md) | Why 11 pt, Word insertion, palette semantics, print widths, exceptions |
| [references/common-patterns.md](references/common-patterns.md) | Legend placement, panel tags, multi-panel, print-safe encoding |
| [references/tutorials.md](references/tutorials.md) | End-to-end walkthroughs (bar, trend + band, heatmap) |
| [references/demos.md](references/demos.md) | The 21 chart types and where the runnable code lives |
| `assets/wxl_style.py` | The importable style module (rcParams, palette, helpers, audit) |
| `assets/wxl_docx.py` | Word assembly: 100 % insertion, captions, three-line tables |
| `scripts/check_wxl_style.py` | Run `python scripts/check_wxl_style.py` to self-test the install |
| `examples/gallery.py` | Render all 21 chart types plus an HTML preview gallery |
| `examples/word_report.py` | Render figures and assemble a Word report end to end |
| `examples/column_gallery.py` | All 21 chart types at 90 mm and 190 mm in one Word document |
| `requirements.txt` | Python dependencies (matplotlib, numpy, Pillow; python-docx optional) |
