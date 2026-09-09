# Common patterns (WXL style)

Operational recipes for the situations that come up most often. Every snippet
assumes `apply_wxl_style()` has been called and `P` is `WXL_PALETTE`.

---

## 1) Legend placement that never covers data

Placement is automatic. Write `framed_legend(ax)` with no `loc`, and
`prepare_figure` (called by `finalize_figure`) does the rest:

1. It renders the figure and measures the legend box against the actual data
   geometry. Lines and scatter contribute the fraction of their points inside
   the box, bars and boxes contribute the overlapped area fraction.
2. It tries nine positions in order: `best`, `upper right`, `upper left`,
   `lower left`, `lower right`, `upper center`, `lower center`, `center left`,
   `center right`, stopping at the first one with zero overlap.
3. If none is clear it grows the y-range by 35 % on the side where the legend
   sits, re-locks the axis ends and retries, twice.
4. `check_wxl_style` reports a soft warning naming the measured percentage when
   a legend still covers more than 2 % of the data.

Measured result across all 20 chart types at both 90 mm and 190 mm: overlap
score 0.0000 for every legend (the radar chart's hand-placed legend, which is
exempt, sits at 0.009).

Things you still do by hand:

- **Flatten a tall legend** with columns when the labels are long:
  `framed_legend(ax, ncol=3, columnspacing=1.0, handlelength=1.4)`. The automatic
  pass already tries two columns for legends with three or more entries.
- **Leave headroom before plotting** when you know the data will reach the top.
  The automatic pass can only grow the range afterwards, which is equivalent but
  happens late in the pipeline.
- **Use a legend panel** when a figure is genuinely too dense for any in-axes
  position. Dedicate one subplot, `ax.set_axis_off()`, draw the handles there and
  keep it inside the same figure.
- **Pie / donut**: turn the axes off and place the legend beside the wedges.
  These axes are exempt from the automatic pass.

### When no position can work

Sometimes the geometry is impossible, not the algorithm. Measured example: a
2 × 2 multi-panel at 90 mm gives each panel an 83 × 52 pt axes, while a two-entry
10 pt legend box is 68 × 31 pt. The legend alone takes 81 % of the panel width,
so it must cover data. `check_wxl_style` reports exactly this:

```
axes[1]: legend covers about 59% of the plotted data and takes 50% of the
panel. Widen the figure, drop the legend for direct labels, or give it a
dedicated panel
```

The range expansion is capped at 35 % of the data span on each side, so the
algorithm never "fixes" an overlap by turning a bar chart into mostly empty
canvas. When the cap is reached the overlap stays and the warning stands.

The fix is a layout decision, not a style tweak, in this order:

1. Move the figure to the wider preset (single 90 mm → onehalf 140 mm →
   double 190 mm). This solves almost every case.
2. Replace the legend with direct labels on the curves, or annotate only the
   first and last series.
3. Give the legend its own subplot inside the same figure.
4. Drop a series so the legend shrinks.

Do not shrink the legend font: the uniform 10 pt rule is non-negotiable, and
`check_wxl_style` rejects any other size.

```python
ax.set_axis_off()
framed_legend(ax, handles=handles, loc="center left", bbox_to_anchor=(0.92, 0.5))
```

## 2) Grouped bars

```python
x, w = np.arange(len(cats)), 0.26
for i, (name, vals, key) in enumerate(series):
    bars = ax.bar(x + (i - 1) * w, vals, w, yerr=err, label=name,
                  color=P[key], edgecolor="black", linewidth=0.8,
                  error_kw=dict(elinewidth=0.8, capsize=2, ecolor=P[key]))
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width()/2, v + 0.05, f"{v:.2f}",
                ha="center", va="bottom")
```

Keep at most three groups per category. With four or more, switch to a heatmap
or a small-multiples grid.

## 3) Uncertainty bands

```python
ax.fill_between(x, y - band, y + band, color=P["light"], alpha=0.35,
                edgecolor=P["primary"], linewidth=0.6)
ax.plot(x, y, "-", color=P["primary"], lw=1.5, label="Proposed")
```

Draw the band first so the curve stays on top. Use `light` for the primary
series and `neutral` for the comparison series so the two bands stay separable.

## 4) Value annotations

```python
ax.text(x, y, f"{v:.2f}", ha="center", va="bottom")   # 10 pt by rcParams
```

- Keep annotations inside the limits; raise `ylim` instead of clipping.
- For dense data, annotate only extremes and label the axis with units.
- Use `P["accent"]` for an annotation that must stand out, black for the rest.

## 5) Multi-panel grids

```python
fig, axes = create_subplots(2, 2, figsize=WXL_FIGSIZE["double_tall"])
# ... draw each panel ...
panel_tag(axes[0], "(a)", y=-0.42)
panel_tag(axes[1], "(b)", y=-0.42)
panel_tag(axes[2], "(c)", y=-0.42)
panel_tag(axes[3], "(d)", y=-0.42)
add_caption(fig, "Fig. 4  Multi-panel comparison of the four settings.")
```

- One legend per panel, not one shared legend floating outside.
- Same limits across panels that share a quantity, so the reader can compare
  visually.
- Panel tags go below their own panel; use `y=-0.42` when the panel has an
  x-label.
- Mixing types in one grid (bar + line + box + heatmap) is fine as long as the
  type scale, spine width and color semantics stay identical.

## 6) Heatmaps and fields

```python
im = ax.imshow(m, cmap=WXL_CMAP, vmin=-1, vmax=1)
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
cb.set_label("Correlation")
cb.ax.tick_params(direction="in", width=0.8)
cb.outline.set_linewidth(0.8)
```

- Always set `vmin`/`vmax` explicitly; auto-scaling makes panels incomparable.
- Use `RdBu_r` for signed data and `Blues` for non-negative fields.
- Annotate cells only when the matrix is 8 × 8 or smaller.
- Colorbar axes are exempt from the full-box check but must still use inward
  ticks and a 0.8 pt outline.

## 7) Dual axes

```python
ax2 = ax.twinx()
ax2.plot(x, temp, "-o", color=P["contrast"], lw=1.5, ms=4, mfc="white", mew=0.9)
ax2.set_ylabel("Temperature (C)")
for side in ("top", "bottom", "left", "right"):
    ax2.spines[side].set_visible(True)      # twinx hides some spines by default
    ax2.spines[side].set_linewidth(0.8)
ax2.tick_params(direction="in", width=0.8)
ax2.grid(False)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
framed_legend(ax, handles=h1 + h2, labels=l1 + l2, loc="upper left")
```

Color the right axis label and ticks to match the `contrast` series, and state
both units in the caption.

## 8) Print-safe encoding

- Beyond four series, vary marker shape (`o`, `s`, `^`, `D`) and add hatch
  (`//`, `\\`, `..`) instead of introducing new hues.
- Keep bar edges black at 0.8 pt so adjacent bars stay separated in grayscale.
- Avoid alpha below 0.6 for data marks; light fills are for bands only.

## 9) Headless and batch runs

```python
import matplotlib
matplotlib.use("Agg")
```

Set the backend before importing pyplot. For batch output, loop over the figure
functions, call `check_wxl_style(fig)` on each, and fail the run if any report
has `ok == False`. `examples/gallery.py` is a complete template for this.

## Related files

- [../SKILL.md](../SKILL.md) — hard rules
- [api.md](api.md) — signatures
- [design-theory.md](design-theory.md) — rationale
- [tutorials.md](tutorials.md) — worked examples
