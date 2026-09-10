# Design theory (WXL style)

Why the WXL style looks the way it does. Everything here is derived from the
locked decisions: Elsevier / IEEE / Springer target, Times New Roman, uniform
11 pt, soft science palette, full box, framed legend, inward ticks, no grid.

---

## 1) The 11 pt contract and Word insertion

The requirement is that figure text matches **Word 11 pt body text**. Points are
absolute physical units, so this only holds when the image is placed in Word at
**100 % of its original size**:

- A figure authored at 190 mm wide and inserted at 190 mm shows 11 pt text as
  11 pt.
- If the same figure is dragged to 140 mm, every glyph shrinks to 10 × 140/190
  = 7.4 pt, and the match is lost.

Therefore the workflow is:

1. Decide the final column width **before** drawing (90 / 140 / 190 mm).
2. Author the figure at exactly that width with `WXL_FIGSIZE`.
3. In Word, insert with **Original Size** and never resize by dragging.

`check_wxl_style` cannot see Word, so it verifies the other half of the
contract: every text artist is exactly 11 pt.

### The tight-crop trap (important)

`bbox_inches="tight"` is mandatory so the below-figure caption survives, but it
also **trims the canvas margins**. A figure authored with
`figsize=(7.48, 5.20)` (190 mm) therefore usually saves around **158 mm** wide.
The text inside is still physically 11 pt, so inserting that image at its natural
158 mm keeps the match. The trap is the next step: to fill a 190 mm column you
stretch the image to 190 mm, every glyph scales by 158/190 = 0.83, and the 11 pt
text silently becomes 8.3 pt.

Two ways to stay safe:

1. Pass `target_width_mm=WXL_WIDTH_MM[preset]` to `finalize_figure`. It
   calibrates the canvas with up to six probe renders so the trimmed image is
   exactly 90 / 140 / 190 mm wide, and the aspect ratio is preserved. This is
   the default workflow in `examples/gallery.py`.
2. If you skip the calibration, insert the image at its **measured** width
   (`measure_width_mm`) rather than stretching it, and accept the narrower
   figure.

Verify after saving: `measure_width_mm("figures/result.png", 600)` should return
90 / 140 / 190 mm within about 0.5 mm.

### Type scale

| Element | Size | Note |
|---|---|---|
| Figure caption | 11 pt | below the figure, centered |
| Axis label | 11 pt | |
| Tick label | 11 pt | |
| Legend text | 10 pt | |
| Data annotation | 11 pt | |
| Panel label `(a) Grouped bars` | 11 pt, not bold | centered below its own panel |

Because everything is one size, hierarchy comes from **weight, color and
position** instead of size: panel tags are bold, emphasis annotations use
`accent`, reference lines use `neutral` and a dashed style.

### One black frame for every single-column figure

`finalize_figure` puts every single-column figure on one fixed black frame,
`WXL_AXES_SINGLE_MM = (75 × 55 mm)`, centred. The frame is therefore identical
across figures and does not grow or shrink with the tick labels — a run of
single-column figures in a manuscript reads as one consistent set. The trade-off
is that the saved width then follows the labels (about 87–102 mm) instead of
being pinned to 90 mm; a colorbar adds its bar and labels on the right. The width
audit consequently does not pin the single-column variant. Polar axes and pies
have no rectangular frame, and their legend stays in the conventional place
outside the circle (still inside the figure). A multi-panel figure instead brings
each subplot to `WXL_AXES_PANEL_MM` (75 × 55 mm) without changing the spacing.

### Single-column caution

At 90 mm width, 11 pt text consumes a much larger share of the canvas. A
single-column figure therefore needs fewer tick labels, shorter axis labels and
at most a two-entry legend. If a panel feels crowded at 90 mm, move it to
140 mm rather than shrinking the type.

---

## 2) Palette semantics

A soft, low-saturation "science" set of seven colours, in the spirit of the soft
pastel palettes used by modern journal-figure libraries (for example SciPalette's
pastel sets, the AAAS/Nature palettes in `ggsci`, and the `science` preset in
`plotstyle`). Muted fills with black edges keep the figures calm and print-safe.

| Key | Hex | Name | Meaning | Typical use |
|---|---|---|---|---|
| `primary` | `#8FA2D6` | Periwinkle Blue | the method or series you are arguing for | main bars, main curve |
| `secondary` | `#6A5C95` | Lavender Dusk | supporting role | extra series |
| `contrast` | `#D99AAE` | Coral Bloom | baseline or competitor | comparison bars/curves |
| `improve` | `#A9CBB8` | Seafoam Mist | improvement, variant | ablation, positive deltas |
| `accent` | `#E7A889` | Coral Peach | emphasis | annotations, highlighted points |
| `neutral` | `#5B608C` | Slate Violet | reference, background | gridlines, target lines |
| `light` | `#CFE3E6` | Pale Aqua | fill, low-emphasis mass | histograms, bands |

Design intent:

- **The light members carry the area, the deep ones carry the line.** This set
  has only two dark colours (Lavender Dusk #6A5C95 and Slate Violet #5B608C,
  both luminance ≈ 99/255); the other five sit at 162–223. Putting a deep violet
  on `primary` fills the largest bar or stacked area with the darkest ink and
  makes the whole figure read heavy, so `primary` is the light periwinkle and the
  deep violets are reserved for thin lines, emphasis and references.
- Coral is reserved for the thing you compare against, so a reader who only skims
  the colour still reads the comparison.
- Seafoam marks gain; peach marks emphasis. Do not use them as a second baseline.
- Slate violet is the deliberate low-chroma one: it is the only colour used for
  reference lines and grids, so nothing in the data competes with it.
- These are 300 dpi-ready pastels, so the 0.8 pt black edge on every patch does
  the definition work that a saturated fill would otherwise do.
- Grayscale safety: the set separates by lightness as well as hue, so the figure
  survives a black-and-white print. When more than four series are needed, add
  hatch or marker-shape encoding rather than new hues.

Colour maps: `RdBu_r` for signed matrices (correlation), `Blues` for
non-negative fields (intensity, temperature), `coolwarm` when the sign matters
and more contrast is needed.

---

## 3) Geometry

- **Spines**: 0.8 pt on all four sides. A full box makes the plot area read as a
  bounded region and matches the table rules used in the same manuscripts.
- **Ticks**: inward, 3 pt long, 0.8 pt wide. Inward ticks keep the outer canvas
  clean and avoid collisions with adjacent panels.
- **Axis ends**: every numeric axis starts and ends exactly on a tick label.
  Matplotlib's default autoscaling leaves a 5 % margin, so the last tick often
  falls short of the axis end and the reader sees an unlabelled strip on the
  right or top. `lock_axis_ends_all` rounds the limits outward to a
  1 / 2 / 2.5 / 5 / 10 step grid, sets the ticks explicitly and installs a plain
  formatter, so the first and last labels sit on the spines. Steps are chosen to
  keep four to eight ticks while minimising padding. Non-negative data keeps a
  zero lower bound, which is why a strain axis spanning 10 to 410 mm is drawn as
  0 to 500 mm rather than −100 to 500 mm.
- **Grid**: none. Tick values plus the full box carry the reading task. The only
  exception is the radar chart, where a light `neutral` grid at 35 % alpha is
  required to read values off the polar axes.
- **Line width**: 1.5 pt for data curves, 0.8 pt for error bars and edges.
- **Markers**: 4 pt, white fill, 0.9 pt colored edge, so overlapping points stay
  distinguishable.
- **Bars**: 0.8 pt black edge. In grouped bars, bar width 0.26 of the category
  spacing leaves a visible gap without looking sparse.

## 4) Layout

- **Aspect ratios**: `double` figures are deliberately short — 7.48 × 2.60 in
  (190 × 66 mm, half the old 190 × 132 mm height). The 11 pt text is unchanged,
  so it reads larger relative to the shorter plot. This suits a wide, flat
  comparison figure. The 2 × 2 multi-panel grid stays tall via `double_tall`
  (190 × 173 mm).
- **Legends**: inside the axes, `loc="best"` first, then the emptiest corner,
  then two columns. `ylim` is deliberately loosened (for example to 1.55 for
  bars topping out at 0.94) so the legend never sits on data.
- **Captions**: below the figure, `Fig. N  sentence case description.` Panel
  tags sit below their own panel, never on top.
- **Consistency**: every panel in a multi-panel figure shares the same font
  size, spine width, tick direction and color semantics.

## 5) Export policy

| Purpose | Setting |
|---|---|
| Submission PNG | `dpi=600`, `bbox_inches="tight"` |
| Vector | `pdf` (and `svg` when editable text is wanted) |
| HTML preview | `dpi=300` |
| Fonts in vector | `pdf.fonttype = 42`, `svg.fonttype = "none"` |

`bbox_inches="tight"` is mandatory: the caption lives outside the axes, and a
fixed bounding box would clip it.

## 6) Documented exceptions

| Case | Exception | Why |
|---|---|---|
| Radar (polar) | keeps a light grid, no rectangular spines | polar axes have no four-spine frame, and values are unreadable without a grid |
| Pie / donut | `ax.set_axis_off()` | there are no axes to frame |
| Categorical axes | not end-locked | category labels sit at bar / box centers, and locking the ends would clip half of the first and last category |
| Colorbar | spines not checked | the colorbar draws its own 0.8 pt outline |
| Slide export | `WXL_FIGSIZE["slide"]` | slides are viewed, not printed, so the 11 pt/print-width contract does not apply |

## 7) Reproduction checklist

1. Pick the width preset, then `apply_wxl_style()`.
2. Draw with `WXL_PALETTE` colors only; black edges on bars and markers.
3. Legend inside, framed; loosen limits so it never covers data.
4. Caption below via `add_caption`; panel tags below their panels.
5. `report = check_wxl_style(fig)`; fix every problem before saving.
6. `finalize_figure(..., formats=["png", "pdf"], dpi=600)`.

## Related files

- [../SKILL.md](../SKILL.md) — the hard rules
- [api.md](api.md) — signatures and constants
- [common-patterns.md](common-patterns.md) — operational patterns
- [demos.md](demos.md) — the 21 chart types
