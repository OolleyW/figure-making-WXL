# Demos: the 22 chart types

All 21 are implemented in `examples/gallery.py` and rendered by

```bash
python "<skill-dir>/examples/gallery.py" --out ./wxl_gallery
```

The generated `index.html` shows every figure with its audit result. Each entry
below gives the figure id, the width preset used, and the core call to copy.

## Bar family

| id | Chart | Width | Core call |
|---|---|---|---|
| `grouped_bar` | Grouped bars with error bars and value labels | double | `ax.bar(x + (i-1)*w, v, w, yerr=e, edgecolor="black")` |
| `stacked_bar` | Stacked bars of composition | double | `ax.bar(x, v, bottom=bottom)` |
| `horizontal_bar` | Sorted horizontal bars with values | double | `ax.barh(y, v); ax.text(v + pad, y, ...)` |

## Line family

| id | Chart | Width | Core call |
|---|---|---|---|
| `line_markers` | Multi-curve marker chart: one white-filled marker shape per series | double | `ax.plot(x, y, "-", marker=mk, mfc="white", mec=key, mew=0.9, ms=4.2)` |
| `line_trend` | Multi-series trend with markers | double | `ax.plot(x, y, "-o", mfc="white", mew=0.6, ms=3.5, lw=1.5)` |
| `line_band` | Trend with uncertainty band | double | `ax.fill_between(x, y-sd, y+sd, alpha=0.35)` |
| `stacked_area` | Stacked area | double | `ax.stackplot(x, *series, edgecolor=WXL_INK)` |

`line_markers` is the type to reach for when several curves share one axes: give
each series a distinct marker shape (circle, square, triangle, diamond,
down-triangle) and keep every marker white-filled, so the shape alone carries the
series identity and the figure stays readable in a black-and-white print. Defaults
that were tuned and agreed: marker size 5.0 pt, line width 2.0 pt, alpha 1.0 —
(the rest of the gallery keeps the house default of 3.5 pt / 1.5 pt) —
below 0.8 alpha the overlapping curves bleed into each other and print grey. Keep
the legend to two columns and leave headroom on the y-axis: a five-entry legend is
wider than it looks inside the 75 × 55 mm single-column frame.

## Relationship family

| id | Chart | Width | Core call |
|---|---|---|---|
| `scatter_fit` | Scatter with least-squares fits | double | `ax.scatter(...); ax.plot(xs, k*xs+b)` |
| `bubble` | Size- and color-encoded bubble | double | `ax.scatter(x, y, s=size, color=PALETTE[key])` |
| `errorbar` | Error bars in x and y | double | `ax.errorbar(x, y, xerr=xe, yerr=ye, fmt="o")` |

## Distribution family

| id | Chart | Width | Core call |
|---|---|---|---|
| `boxplot` | Box plot, filled boxes | onehalf | `ax.boxplot(data, patch_artist=True, widths=0.55)` |
| `violin` | Violin plot with mean markers | onehalf | `ax.violinplot(data, showmeans=True)` |
| `hist_kde` | Histogram + kernel density | double | `ax.hist(..., color=PALETTE["light"]); ax.plot(grid, kde)` |
| `ecdf` | Empirical CDF | single | `ax.step(x_sorted, np.arange(1, n+1)/n, where="post")` |
| `strip_mean` | Strip plot + mean ± SD | double | `ax.scatter(jitter, y); ax.errorbar(cx, mu, yerr=sd, fmt="s")` |

## Matrix family

| id | Chart | Width | Core call |
|---|---|---|---|
| `heatmap` | Annotated correlation heatmap | double | `ax.imshow(m, cmap="wxl_div_rose_blue", vmin=-1, vmax=1)` |
| `contour` | Filled contour field | double | `ax.contourf(X, Y, Z, levels=12, cmap=WXL_CMAPS["sequential"])` |

## Special family

| id | Chart | Width | Core call |
|---|---|---|---|
| `radar` | Radar / polar multi-index | single | `fig.add_subplot(projection="polar"); ax.plot(theta, v, "-o")` |
| `donut` | Donut / pie with framed legend | single | `ax.pie(vals, wedgeprops=dict(width=0.42)); ax.set_axis_off()` |
| `dual_axis` | Dual y-axis (bars + line) | double | `ax2 = ax.twinx(); ax2.plot(...)` |
| `multi_panel` | 2 × 2 mixed-type grid | double_tall | `create_subplots(2, 2); panel_tag(axes[0], "(a)", "Grouped bars"); center_grid(fig)` |
| `multi_panel_1x3` | 1 × 3 mixed-type grid, one row | double_1x3 | `create_subplots(1, 3); panel_tag(axes[0], "(a)", "Grouped bars"); center_grid(fig)` |

Single-column-only types: `heatmap`, `radar`, `donut`. Double-column-only types:
`multi_panel`, `multi_panel_1x3` (the column gallery renders each type only in
the layouts it suits).

Note: the `double` preset is deliberately short — 190 × 66 mm, half the height it
used to be — while every text element stays 11 pt. `double_tall` (190 × 173 mm)
is the tall 2 × 2 multi-panel preset and is unchanged. `double_1x3`
(190 × 41 mm) is the 1 × 3 row preset, sized so each panel keeps the
single-column aspect ratio (50.4 × 38.5 mm, 1.31).

## Choosing a type

- Comparing a few methods across a few categories → grouped bars.
- Anything over time or over an ordered variable → trend lines, with a band if
  uncertainty is known.
- Two continuous variables, sample-level detail → scatter, plus a fit when the
  relationship is the point.
- Distribution shape across groups → box (compact, n > 20), violin (shape
  matters, n > 100) or strip + mean (n < 20, show every point).
- Many × many comparisons → heatmap; continuous 2-D fields → filled contour.
- Multi-index summaries → radar, but keep it to five axes and two series.
- Proportions → donut, only when there are four slices or fewer.

## Upstream reference

The style descends from the `figure_*` demos in
[figures4papers](https://github.com/ChenLiu-1996/figures4papers). Those demos use
the older sans-serif, top-title, unframed-legend look; under this skill their
layout ideas are reusable but the typography, palette and framing must be
overridden by the WXL hard rules.

## Related files

- [../SKILL.md](../SKILL.md) — hard rules
- [api.md](api.md) — signatures
- [tutorials.md](tutorials.md) — worked examples
- `examples/gallery.py` — runnable code for every chart above
