---
name: figure-making-WXL
description: >-
  Publication-ready matplotlib figures in the WXL house style for Elsevier,
  IEEE and Springer submissions: every text element is Times New Roman at a
  uniform 10 pt (so figure text matches Word 10 pt body text when the figure is
  inserted at its original size), a deep-blue semantic palette, full-box axes,
  framed in-plot legends, inward ticks, no grid, captions below the figure, and
  figure widths fixed to the final print width (90 / 140 / 190 mm). Covers 20
  chart types (grouped/stacked/horizontal bars, trend lines, uncertainty bands,
  stacked areas, scatter, bubble, error bars, box, violin, histogram + KDE,
  ECDF, strip+mean, heatmap, filled contour, radar, donut, dual axis, multi
  panel) with a machine-checked style audit. Use when the user asks for
  publication figures, 论文配图, 科研绘图, 画图/作图 with matplotlib, or wants
  figures in "WXL 风格" / "我的绘图风格" / matching Word 10 pt text. Do not use
  for interactive dashboards or web viz (Plotly, Altair, Bokeh), exploratory
  plots with no publication target, Origin/OriginPro automation (use the
  editaplot skill), or Illustrator/Figma-first infographics.
---

# figure-making-WXL

Publication figures in the WXL house style. Open `references/` only as needed;
do not preload every file. Start from the table at the bottom, then follow links
inside the document you opened.

## Hard rules (non-negotiable)

These rules supersede any conflicting style text in `references/` or in upstream
`figure_*` demos.

1. **Times New Roman everywhere.** Titles, axis labels, ticks, legends,
   annotations, colorbar labels. Math uses `mathtext.fontset = "stix"`, and
   `axes.unicode_minus = False` because Times New Roman lacks U+2212. Bold and
   italic Times faces are allowed; never Helvetica, Arial or DejaVu Sans. CJK
   text falls back to SimSun.
2. **Uniform 10 pt.** Caption, axis label, tick, legend and annotation are all
   10 pt. The contract is checked; do not hand-tune individual sizes.
3. **Figure width = final print width.** `single` = 90 mm (3.54 in),
   `onehalf` = 140 mm (5.51 in), `double` = 190 mm (7.48 in). 10 pt in the
   figure equals Word 10 pt only when the image is inserted at its original
   size, so never design a wide figure and let Word shrink it. Because
   `bbox_inches="tight"` trims the canvas, always pass
   `target_width_mm=WXL_WIDTH_MM[preset]` to `finalize_figure` so the saved
   image is exactly the print width instead of ~17 % narrower.
4. **Full box on every Cartesian axes.** All four spines drawn at 0.8 pt.
   Exceptions: polar axes (radar), axes with `axison = False` (pie/donut) and
   colorbar axes.
5. **Legend inside the axes, framed.** `loc="best"` or the emptiest corner,
   opaque white face, black 0.8 pt border, `framealpha = 1`. If `"best"` would
   cover bars, move it or use two columns. Never place it outside the figure.
6. **Ticks point inward, no grid, and both axis ends land on a tick value.**
   Ticks are 3 pt long at 0.8 pt width. Every numeric Cartesian axis must start
   and end exactly on its first and last tick label, so a reader never sees an
   unlabelled strip at either end. `finalize_figure` calls `lock_axis_ends_all`
   automatically, and `check_wxl_style` fails a figure whose axis ends are not on
   tick values. The only grid exception is the radar chart, which keeps a light
   neutral grid so the values stay readable. Image axes (heatmaps), polar axes,
   colorbar axes and pie/donut axes are exempt because their ticks are
   categorical and already span the full extent.
7. **Caption below the figure**, centered, via `add_caption`. Never
   `fig.suptitle` and never a title on top of the axes. Panel tags `(a)`, `(b)`
   go just below their own panel.
8. **Deep-blue palette only.** Colors come from `WXL_PALETTE`; black, white and
   the palette are the only allowed colors. See `references/design-theory.md`
   for the semantics.
9. **Export PNG 600 dpi + PDF vector.** Saving uses `bbox_inches="tight"` so
   the below-figure caption survives.
10. **Run the audit.** Call `check_wxl_style(fig)` before saving and fix every
    reported problem.

## Quickstart

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"C:\Users\24976\.dsh\skills\figure-making-WXL\assets")))
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

The 20 chart types the style covers, each with its core call, are listed in
`references/demos.md`; runnable code for all of them lives in
`examples/gallery.py`.

## When to load this skill

- Matplotlib figures for **Elsevier / IEEE / Springer** manuscripts, theses or
  reports that must match the WXL look (10 pt Times, deep blue, full box).
- Requests for **论文配图 / 科研绘图 / 画图** where the figure will be pasted
  into Word and should match 10 pt body text.
- Any of the 20 chart types in `references/demos.md`, or multi-panel layouts.

## When not to load

- **Plotly, Altair, Bokeh** or other interactive / web-first plotting.
- **Origin / OriginPro** automation (use the `editaplot` skill).
- **Exploratory** plots with no publication target.
- **3D, GIS** or **Illustrator / Figma-first** infographics.

## Related files

| File | Open when |
|------|-----------|
| [references/api.md](references/api.md) | Function signatures, `WXL_PALETTE`, `WXLStyle`, validation rules |
| [references/design-theory.md](references/design-theory.md) | Why 10 pt, Word insertion, palette semantics, print widths, exceptions |
| [references/common-patterns.md](references/common-patterns.md) | Legend placement, panel tags, multi-panel, print-safe encoding |
| [references/tutorials.md](references/tutorials.md) | End-to-end walkthroughs (bar, trend + band, heatmap) |
| [references/demos.md](references/demos.md) | The 20 chart types and where the runnable code lives |
| `assets/wxl_style.py` | The importable style module (rcParams, palette, helpers, audit) |
| `scripts/check_wxl_style.py` | Run `python scripts/check_wxl_style.py` to self-test the install |
| `examples/gallery.py` | Render all 20 chart types plus an HTML preview gallery |
