# Design theory (WXL style)

Why the WXL style looks the way it does. Everything here is derived from the
locked decisions: Elsevier / IEEE / Springer target, Times New Roman, uniform
10 pt, deep-blue palette, full box, framed legend, inward ticks, no grid.

---

## 1) The 10 pt contract and Word insertion

The requirement is that figure text matches **Word 10 pt body text**. Points are
absolute physical units, so this only holds when the image is placed in Word at
**100 % of its original size**:

- A figure authored at 190 mm wide and inserted at 190 mm shows 10 pt text as
  10 pt.
- If the same figure is dragged to 140 mm, every glyph shrinks to 10 × 140/190
  = 7.4 pt, and the match is lost.

Therefore the workflow is:

1. Decide the final column width **before** drawing (90 / 140 / 190 mm).
2. Author the figure at exactly that width with `WXL_FIGSIZE`.
3. In Word, insert with **Original Size** and never resize by dragging.

`check_wxl_style` cannot see Word, so it verifies the other half of the
contract: every text artist is exactly 10 pt.

### The tight-crop trap (important)

`bbox_inches="tight"` is mandatory so the below-figure caption survives, but it
also **trims the canvas margins**. A figure authored with
`figsize=(7.48, 5.20)` (190 mm) therefore usually saves around **158 mm** wide.
The text inside is still physically 10 pt, so inserting that image at its natural
158 mm keeps the match. The trap is the next step: to fill a 190 mm column you
stretch the image to 190 mm, every glyph scales by 158/190 = 0.83, and the 10 pt
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
| Figure caption | 10 pt | below the figure, centered |
| Axis label | 10 pt | |
| Tick label | 10 pt | |
| Legend text | 10 pt | |
| Data annotation | 10 pt | |
| Panel tag `(a)` | 10 pt bold | below its own panel |

Because everything is one size, hierarchy comes from **weight, color and
position** instead of size: panel tags are bold, emphasis annotations use
`accent`, reference lines use `neutral` and a dashed style.

### Single-column caution

At 90 mm width, 10 pt text consumes a much larger share of the canvas. A
single-column figure therefore needs fewer tick labels, shorter axis labels and
at most a two-entry legend. If a panel feels crowded at 90 mm, move it to
140 mm rather than shrinking the type.

---

## 2) Palette semantics

| Key | Hex | Meaning | Typical use |
|---|---|---|---|
| `primary` | `#1F4E79` | the method or series you are arguing for | main bars, main curve |
| `secondary` | `#4E86C6` | same family, supporting role | extra blue series |
| `contrast` | `#B64342` | baseline or competitor | comparison bars/curves |
| `improve` | `#2E8B7A` | improvement, variant | ablation, positive deltas |
| `accent` | `#E0A030` | emphasis | annotations, secondary axis |
| `neutral` | `#7B7B7B` | reference, background | gridlines, target lines |
| `light` | `#C9DCF0` | fill, low-emphasis mass | histograms, bands |

Design intent:

- Blues carry the argument. If two blue series appear together, the darker one
  is the primary.
- Red is reserved for the thing you are comparing against, so a reader who only
  skims the color still reads the comparison.
- Teal marks gain; amber marks emphasis. Do not use them as a second baseline.
- Grayscale safety: `primary` vs `contrast` vs `improve` differ in both hue and
  lightness, so the figure survives a black-and-white print. When more than
  four series are needed, add hatch or marker-shape encoding rather than new
  hues.

Colour maps: `RdBu_r` for signed matrices (correlation), `Blues` for
non-negative fields (intensity, temperature), `coolwarm` when the sign matters
and more contrast is needed.

---

## 3) Geometry

- **Spines**: 0.8 pt on all four sides. A full box makes the plot area read as a
  bounded region and matches the table rules used in the same manuscripts.
- **Ticks**: inward, 3 pt long, 0.8 pt wide. Inward ticks keep the outer canvas
  clean and avoid collisions with adjacent panels.
- **Grid**: none. Tick values plus the full box carry the reading task. The only
  exception is the radar chart, where a light `neutral` grid at 35 % alpha is
  required to read values off the polar axes.
- **Line width**: 1.5 pt for data curves, 0.8 pt for error bars and edges.
- **Markers**: 4 pt, white fill, 0.9 pt colored edge, so overlapping points stay
  distinguishable.
- **Bars**: 0.8 pt black edge. In grouped bars, bar width 0.26 of the category
  spacing leaves a visible gap without looking sparse.

## 4) Layout

- **Aspect ratios**: `double` figures use 7.48 × 5.20 in (190 × 132 mm), which
  fits a full-width single-row figure. Multi-panel grids use `double_tall`
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
| Colorbar | spines not checked | the colorbar draws its own 0.8 pt outline |
| Slide export | `WXL_FIGSIZE["slide"]` | slides are viewed, not printed, so the 10 pt/print-width contract does not apply |

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
- [demos.md](demos.md) — the 20 chart types
