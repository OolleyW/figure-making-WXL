# API Reference (WXL style)

Everything here lives in `assets/wxl_style.py`. Import it after adding the
skill's `assets/` directory to `sys.path`.

---

## Constants

### WXL_PALETTE

```python
WXL_PALETTE = {
    "primary":   "#8FA2D6",   # Periwinkle Blue - proposed method / main series
    "secondary": "#6A5C95",   # Lavender Dusk   - supporting series
    "contrast":  "#D99AAE",   # Coral Bloom     - baseline / competing method
    "improve":   "#A9CBB8",   # Seafoam Mist    - improvement / positive variant
    "accent":    "#E7A889",   # Coral Peach     - emphasis, annotations
    "neutral":   "#5B608C",   # Slate Violet    - reference lines, grid, background
    "light":     "#CFE3E6",   # Pale Aqua       - light fill, uncertainty bands
}
```

Only these colors plus the ink `#2E3142`, black and white are allowed.
`check_wxl_style` enforces it.

### WXL_INK

```python
WXL_INK = "#2E3142"
```

The colour for text, axis labels, tick labels, annotations, spines, tick marks,
the legend border and every bar / marker outline. A deep slate instead of pure
black, so the line work reads calmer against the pastel fills while keeping
near-black contrast. `apply_wxl_style` installs it for `text.color`,
`axes.labelcolor`, `axes.edgecolor`, `xtick.color`, `ytick.color` and
`legend.edgecolor`; pass `edgecolor=WXL_INK` on patches and markers. Pure black
is still accepted by the audit.

### WXL_CMAP / WXL_CMAPS

`WXL_CMAP = "wxl_div_rose_blue"` is the default diverging map, built by
interpolating the palette (rose -> neutral -> periwinkle) so a heatmap always
matches the line work around it. `WXL_CMAPS` also offers `"wxl_seq_blue"`
(near-white -> periwinkle -> deep slate) for single-sided fields.

### WXL_SERIES

Ordered color cycle used when a helper is called without explicit colors:
`primary, contrast, improve, accent, secondary, neutral`.

### WXL_FONTSIZE

```python
{"caption": 11, "label": 11, "tick": 11, "legend": 11, "annot": 11, "panel": 11}
```

Uniform 11 pt for body text, 10 pt for the legend. The audit fails on any other size.

### WXL_FIGSIZE

```python
{
  "single":      (3.54, 2.70),   # 90 mm column
  "onehalf":     (5.51, 3.90),   # 140 mm
  "double":      (7.48, 2.60),   # 190 mm, deliberately short (half the old height)
  "double_tall": (7.48, 6.80),   # 190 mm, tall multi-panel (2 x 2)
  "double_1x3":  (7.48, 1.63),   # 190 mm, 1 x 3 row whose panels keep the
                                 #   single-column aspect ratio (50.4 x 38.5 mm)
  "slide":       (10.0, 6.00),   # slides only, not for submission
}
```

---

## WXLStyle

```python
@dataclass(frozen=True)
class WXLStyle:
    font_size: float = 10.0
    caption_size: float = 10.0
    tick_size: float = 10.0
    legend_size: float = 10.0
    annot_size: float = 10.0
    axes_linewidth: float = 0.8
    line_width: float = 1.5
    marker_size: float = 4.0
    bar_edge_width: float = 0.8
    error_linewidth: float = 0.8
    capsize: float = 2.0
    figsize: tuple = WXL_FIGSIZE["double"]
    dpi: int = 600
    full_box: bool = True
    legend_framed: bool = True
    ticks_in: bool = True
    grid: bool = False
```

Never set `full_box`, `legend_framed`, `ticks_in` or `grid` to anything but
their defaults under this skill.

---

## Style and layout

### apply_wxl_style(style=None) -> WXLStyle

Installs the rcParams (fonts, sizes, spines, tick direction, legend frame,
vector export options, `pdf.fonttype = 42`). Call once before creating figures.

### create_subplots(nrows=1, ncols=1, figsize=None, **kwargs) -> (fig, axes)

`axes` is a flat 1-D numpy array, so `axes[0]` always works.

### framed_legend(ax, **kwargs)

Builds a legend **inside** the axes with an opaque white face and a black
0.8 pt border. Pass `loc`, `ncol`, `handles`, `labels` as usual. The position is
refined later by `place_all_legends`, so `loc="best"` is a fine starting point.

```python
framed_legend(ax, loc="upper left", ncol=2, columnspacing=1.0, handlelength=1.6)
```

### place_legend_smart(ax, leg=None, candidates=None, fig=None) -> (score, loc)

Moves an existing legend to the candidate position that hides least data.
Candidates are tried in this order: `best`, `upper right`, `upper left`,
`lower left`, `lower right`, `upper center`, `lower center`, `center left`,
`center right`. The score is computed by `_legend_overlap_score`; the search
stops at the first position with score 0.

### place_all_legends(fig, rounds=2, candidates=None)

Refines every in-axes legend of a figure. If no candidate is clear, it grows the
y-range on the side where the legend sits (35 % of the span), re-locks the axis
ends and retries, up to `rounds` times. Polar axes, colorbar axes and axes with
`axison == False` keep their hand-placed legend.

### prepare_figure(fig, lock_ends=True, auto_legend=True, auto_text=True)

Puts a figure into contract state: locks axis ends, deconflicts legends, thins
crowded tick labels and nudges colliding annotations. Call it before
`check_wxl_style` when you audit a figure yourself; `finalize_figure` calls it
automatically.

```python
fig = build_my_figure()
prepare_figure(fig)
report = check_wxl_style(fig)
assert report["ok"], report["problems"]
finalize_figure(fig, "figures/result", dpi=600,
                target_width_mm=WXL_WIDTH_MM["double"])
```

### annotate_bars(ax, bars, fmt="{:.2f}", fontsize=None, y_offset_frac=0.02, skip_if_wider=True)

Labels bars above their top edge and returns `(kept, skipped)`. With
`skip_if_wider=True` any label wider than its own bar is dropped, and every label
is tagged so `prepare_figure` re-checks it at the final canvas size. This is what
makes the same figure code produce labelled bars at 190 mm and clean bars at
90 mm, where a 11 pt label is wider than the bar underneath.

### place_annotations(fig, rounds=2)

Nudges plain `ax.text` annotations off the data. For each annotation that touches
a line, a bar or another text box it tries the offsets in `_ANNOT_OFFSETS`
(above, below, left, right, diagonals), keeps the one with the fewest
collisions, and if none is clear it grows the y-range (capped at 35 % of the data
span) and retries. Returns the annotations that still collide.

### fix_tick_label_overlap(fig, tries=(8, 6, 5, 4))

Thins out major ticks until no two adjacent tick labels touch. The 11 pt size is
fixed, so tick density is the only lever. Returns `[(axes, ticks)]` for the axes
that had to be thinned.

### add_caption(fig, text, fontsize=None, y=-0.045, **kwargs)

Places the figure caption centered **below** the whole figure and returns the
`Text` artist. Never use `fig.suptitle`.

### panel_tag(ax, tag, title=None, pad_pt=5.0, bold=False)

Panel label below its own panel, centered on the panel, **not bold** by default.
Pass a `title` to get `(a) Grouped bars` instead of a bare `(a)`. The label sits
`pad_pt` points below the lowest text already under the axes (x-label and tick
labels included), so it stays close to the panel instead of drifting away with
the axes height.

```python
panel_tag(ax, "(a)", "Grouped bars")
```

### center_grid(fig, pad_frac=0.01, max_shift=0.2)

Shifts every axes by the same amount so the union of their tight bounding boxes
(tick labels, axis labels and panel labels included) is centered horizontally and
vertically in the canvas. The shift is capped at `max_shift` of the canvas and
skipped in a dimension whose content already exceeds the canvas, so repeated
calls converge instead of drifting.

Pair it with `fig._wxl_no_tight = True` (so `finalize_figure` does not re-run
`tight_layout` and undo the centering) and `fig._wxl_center = True` (so
`prepare_figure` re-centers after every canvas resize):

```python
fig, axes = create_subplots(2, 2, figsize=WXL_FIGSIZE["double_tall"])
fig._wxl_no_tight = True
fig._wxl_center = True
# ... draw the panels and their labels ...
```

Measured on the 2 × 2 demo: left/right margins 0.0826/0.0826 and top/bottom
0.0770/0.0770 of the canvas.

### finalize_figure(fig, out_path, formats=None, dpi=None, close=True, pad=0.06, layout=True, target_width_mm=None, tol_mm=0.5, lock_ends=True)

Saves to one or more formats (`png`, `pdf`, `svg`, `eps`, `tif`), creates parent
directories, applies `tight_layout(pad=1.0)` unless `layout=False`, and always
uses `bbox_inches="tight"`. Returns the list of saved paths. Use
`dpi=600` for submission and `dpi=300` for HTML previews.

`lock_ends=True` (default) runs `lock_axis_ends_all` before saving, so every
numeric axis ends exactly on a tick label. Set it to `False` only for a figure
whose axes must keep hand-set limits.

`target_width_mm` iteratively calibrates the canvas width (up to six probe
renders) so the **trimmed** image is exactly that wide while keeping the text at
11 pt. Pass `WXL_WIDTH_MM[preset]`; without it a `double` figure saves around
158 mm instead of 190 mm, and stretching it to fill the column drops the text to
about 8.3 pt.

A multi-panel figure can bring every subplot to one physical size: set
`fig._wxl_panel_axes_mm = WXL_AXES_PANEL_MM` (75 × 55 mm) before saving.
`finalize_figure` then resizes each panel to that box while leaving the layout
alone — the column position, the `wspace` / `hspace` proportions and the 14 pt
caption gap are unchanged, so only the black frames change size. The rows below
the first are also shifted so the top row's panel titles clear the next row by
the same 14 pt the caption uses.

Every single-column figure shares one fixed black frame:
`WXL_AXES_SINGLE_MM = (75 × 55 mm)`. After the width calibration,
`_standardize_axes_box` puts every rectilinear Cartesian axes on that box,
centred, so the frame is identical across figures and never grows or shrinks
with the tick labels. Because the box is fixed, the saved width follows the
labels (about 87–102 mm) instead of being pinned to 90 mm, and the width audit
does not pin the single-column variant. Colorbars are tucked against their host
(host read from the colorbar's mappable, so `contourf` works too); polar axes
and pies have no rectangular frame and keep their conventional legend outside
the circle. Set `fig._wxl_skip_uniform_size = True` to opt a figure out.

```python
finalize_figure(fig, "figures/result", formats=["png", "pdf"], dpi=600,
                target_width_mm=WXL_WIDTH_MM["double"])
```

### lock_axis_ends(ax, max_ticks=8, min_ticks=4) -> int

Expands the current limits outward to the nearest tick grid, sets the ticks
explicitly, and installs a plain formatter with no offset and no scientific
notation, so the axis starts and ends exactly on its first and last tick label.
Essentially non-negative data keeps a zero lower bound. Returns the number of
axes modified.

### lock_axis_ends_all(fig, max_ticks=8, min_ticks=4) -> int

Applies `lock_axis_ends` to every numeric Cartesian axes of a figure. Image axes
(`imshow` heatmaps), polar axes, colorbar axes and axes with `axison == False`
are skipped because their ticks are categorical and already span the full
extent. `finalize_figure` calls this automatically, so figures produced through
the normal path are compliant. Call it yourself only when you audit a figure with
`check_wxl_style` before saving.

### measure_width_mm(path, dpi=None) -> float

Physical width of a saved raster file in millimetres (`px / dpi × 25.4`). Use it
to verify that a figure really is 90 / 140 / 190 mm wide before inserting it into
a manuscript.

---

## Word assembly (`assets/wxl_docx.py`)

Optional module that assembles finished figures into a manuscript-style `.docx`.
It needs `python-docx`. Import it the same way as `wxl_style`.

### new_document(side_mm=10, top_mm=20, bottom_mm=20, base_size=10) -> Document

A4 document whose usable text width is `210 − 2 × side_mm` millimetres, 190 mm by
default. Body style is Times New Roman 11 pt with a CJK fallback.

### add_heading(doc, text, size=12)

Section heading in black CJK serif bold, double line spacing, no indent.

### add_paragraph(doc, text, size=10, bold=False, align=None, font=TNR, spacing=2.0, indent_chars=2, space_after=0)

Body paragraph with the paper contract defaults: 11 pt Times, double spacing,
two-character first-line indent.

### add_caption(doc, text, size=10, spacing=1.5, space_after=6)

Centered caption. Use it **below** a figure and **above** a table.

### add_figure(doc, png, dpi=600, space_after=4) -> float

Inserts the image centered at 100 % of its measured physical width and returns
that width in millimetres. The PNG must come from
`finalize_figure(..., target_width_mm=...)`, otherwise the inserted size is wrong
and the 11 pt match is lost.

### add_figure_block(doc, png, caption, dpi=600) -> float

`add_figure` followed by `add_caption`.

### add_three_line_table(doc, headers, rows, col_widths_cm=None, caption=None, font_size=10, spacing=1.5)

Three-line table: 1.5 pt top rule, 0.75 pt header rule, 1.5 pt bottom rule, no
vertical rules. The caption goes above the table. Column widths default to an
even split of the 190 mm usable width.

### add_page_break(doc)

Insert a page break.

---

### check_wxl_style(fig, style=None, strict_sizes=True) -> dict

Audits a live figure. Returns:

```python
{
  "ok": bool,            # True when "problems" is empty
  "fonts": [...],        # font files actually used
  "sizes": [...],        # font sizes in pt actually used
  "n_axes": int,
  "n_legends": int,
  "problems": [...],     # hard contract violations
  "warnings": [...],     # soft notes, e.g. a legend that may cover a bar
}
```

Checks performed:

- every text artist resolves to a Times New Roman (or SimSun) font file;
- every font size equals `font_size` when `strict_sizes=True`;
- no missing-glyph warnings when the canvas draws;
- all four spines visible on every Cartesian axes (polar, `axison=False` and
  colorbar axes are exempt);
- no visible grid lines;
- tick direction is `in`;
- both ends of every numeric Cartesian axis sit on tick values, and the first
  and last tick carry a label (image, polar, colorbar and pie/donut axes are
  exempt);
- every legend has a visible frame, black border and no transparency;
- no legend covers more than 2 % of the plotted data (soft warning, reported
  with the measured percentage);
- no annotation touches a plotted artist or another annotation, and no two
  adjacent tick labels share pixels (soft warnings);
- every `Line2D`, `Patch` and `PathCollection` color comes from the palette
  plus black/white.

Soft warnings currently cover legends whose bounding box overlaps a bar or box
patch by more than 5 % of the legend area.

---

## Conventions

- **Ask before you plot.** Before drawing, confirm the chart type and panel
  count, the x and y axis labels (text, units, italic or not), the line style,
  and the colours. Offer a default but apply nothing until the user picks. See
  `preferences.md`. The user, not the skill, decides these.
- Save outputs under a project `figures/` directory with stable basenames.
- Legend colors and markers must match the series colors exactly.
- When the comparison target, panel count, color role or data layout is
  underspecified in a way that changes the figure, ask the user before
  finalizing.
- In headless runs, set `matplotlib.use("Agg")` before importing pyplot.

## Related files

- [../SKILL.md](../SKILL.md) — hard rules and when to load
- [design-theory.md](design-theory.md) — rationale for 11 pt, palette, widths
- [common-patterns.md](common-patterns.md) — layout patterns
- [tutorials.md](tutorials.md) — worked examples
- [demos.md](demos.md) — the 22 chart types
