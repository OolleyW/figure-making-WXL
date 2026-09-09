# Common patterns (WXL style)

Operational recipes for the situations that come up most often. Every snippet
assumes `apply_wxl_style()` has been called and `P` is `WXL_PALETTE`.

---

## 1) Legend placement that never covers data

Order of preference:

1. `framed_legend(ax, loc="best")` — matplotlib avoids data, but only for the
   artists it knows about.
2. An explicit empty corner: `loc="upper left"`, `"upper right"`,
   `"lower left"`, `"lower right"`.
3. Two or three columns to flatten the box:
   `framed_legend(ax, loc="upper left", ncol=3, columnspacing=1.0, handlelength=1.4)`.
4. Loosen the limits so a corner becomes empty. For bars topping out at 0.94,
   `ax.set_ylim(0, 1.55)` buys a clear top strip:

```python
ax.set_ylim(0, 1.55)
framed_legend(ax, loc="upper left")
```

5. For pie/donut, place the legend beside the wedge and turn the axes off:

```python
ax.set_axis_off()
framed_legend(ax, handles=handles, loc="center left", bbox_to_anchor=(0.92, 0.5))
```

`check_wxl_style` reports a soft warning when a legend's box overlaps a bar or
box patch by more than 5 % of the legend area.

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
