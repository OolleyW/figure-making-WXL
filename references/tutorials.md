# Tutorials (WXL style)

Three end-to-end walkthroughs plus how to run the gallery. Every example starts
from the same import block:

```python
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(r"C:\Users\24976\.dsh\skills\figure-making-WXL\assets")))
from wxl_style import (WXL_PALETTE as P, WXL_FIGSIZE, add_caption,
                       apply_wxl_style, check_wxl_style, create_subplots,
                       finalize_figure, framed_legend, panel_tag)
```

---

## Tutorial 1 — Grouped bars for a 190 mm column

Goal: compare three methods across four scenarios, values readable without a
grid.

```python
apply_wxl_style()
fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])

cats = ["S1", "S2", "S3", "S4"]
series = [("Proposed", [0.82, 0.88, 0.91, 0.94], "primary"),
          ("Baseline", [0.61, 0.64, 0.67, 0.70], "contrast"),
          ("Variant",  [0.70, 0.75, 0.79, 0.83], "improve")]
x, w = np.arange(len(cats)), 0.26
for i, (name, vals, key) in enumerate(series):
    v = np.asarray(vals)
    bars = ax.bar(x + (i - 1) * w, v, w, yerr=0.02, label=name, color=P[key],
                  edgecolor="black", linewidth=0.8,
                  error_kw=dict(elinewidth=0.8, capsize=2, ecolor=P[key]))
    for b, val in zip(bars, v):
        ax.text(b.get_x() + b.get_width() / 2, val + 0.05, f"{val:.2f}",
                ha="center", va="bottom")

ax.set_xticks(x)
ax.set_xticklabels(cats)
ax.set_ylabel("Accuracy")
ax.set_ylim(0, 1.55)                       # headroom so the legend clears the bars
framed_legend(ax, loc="upper left")
add_caption(fig, "Fig. 1  Grouped bars with error bars across four scenarios.")

report = check_wxl_style(fig)
assert report["ok"], report["problems"]
finalize_figure(fig, "figures/grouped_bar", formats=["png", "pdf"], dpi=600,
                target_width_mm=WXL_WIDTH_MM["double"])
```

Points worth noticing:

- `target_width_mm` keeps the saved image at exactly 190 mm despite tight
  cropping, so inserting it in Word at 100 % fills the column **and** keeps the
  text at 10 pt. Without it the image saves near 158 mm.

- `ylim` is raised to 1.55 although the tallest bar plus error reaches 0.96.
  That strip is what keeps the legend off the data.
- Every text artist inherits 10 pt from rcParams; nothing is passed a size.
- The error bar color is set to the series color, not black, so the audit and
  the reader both see the series identity.

## Tutorial 2 — Trend lines with an uncertainty band

Goal: two methods over time, each with a confidence band.

```python
apply_wxl_style()
fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])

x = np.linspace(0, 10, 60)
for key, label, base, slope, sd in [("primary", "Proposed", 0.55, 0.035, 0.035),
                                    ("contrast", "Baseline", 0.50, 0.022, 0.045)]:
    y = base + slope * x
    band = sd * (1 + 0.12 * x)
    ax.fill_between(x, y - band, y + band,
                    color=P["light"] if key == "primary" else P["neutral"],
                    alpha=0.35, edgecolor=P[key], linewidth=0.6)
    ax.plot(x, y, "-", color=P[key], lw=1.5, label=label)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Response (mV)")
framed_legend(ax, loc="upper left")
add_caption(fig, "Fig. 2  Trend lines with uncertainty bands.")
finalize_figure(fig, "figures/trend_band", formats=["png", "pdf"], dpi=600)
```

Points worth noticing:

- Bands are drawn before the curves so the curves stay legible.
- The primary band uses `light`, the comparison band `neutral`, so two
  overlapping bands never read as one.
- Alpha 0.35 is the floor; anything lower disappears in print.

## Tutorial 3 — Annotated correlation heatmap

Goal: a 6 × 6 correlation matrix with readable values and a framed colorbar.

```python
apply_wxl_style()
fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])

rng = np.random.default_rng(0)
m = rng.uniform(-1, 1, (6, 6))
m = (m + m.T) / 2
np.fill_diagonal(m, 1.0)

im = ax.imshow(m, cmap="RdBu_r", vmin=-1, vmax=1)   # WXL_CMAP
ticks = [f"V{i+1}" for i in range(6)]
ax.set_xticks(range(6), ticks)
ax.set_yticks(range(6), ticks)
for i in range(6):
    for j in range(6):
        ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center")

cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
cb.set_label("Correlation")
cb.ax.tick_params(direction="in", width=0.8)
cb.outline.set_linewidth(0.8)

add_caption(fig, "Fig. 3  Correlation heatmap with annotated values.")
finalize_figure(fig, "figures/heatmap", formats=["png", "pdf"], dpi=600)
```

Points worth noticing:

- `vmin`/`vmax` are pinned to ±1 so the colors mean the same thing in every
  panel of a paper.
- Cell annotations stay at 10 pt; stop annotating beyond 8 × 8.
- The colorbar axes is exempt from the full-box rule but keeps inward ticks and
  a 0.8 pt outline.

---

## Running the full gallery

```powershell
python C:\Users\24976\.dsh\skills\figure-making-WXL\examples\gallery.py --out C:\DSH_work\wxl_gallery
```

This renders all 20 chart types to `<out>/figs/*.png` (300 dpi) and
`*.pdf` (vector), runs `check_wxl_style` on each, and writes
`<out>/index.html` — a gallery that shows every figure with its category, its
core API call and its audit result. The script exits non-zero if any figure
fails the audit, so it doubles as a regression test after editing the style
module.

## Verifying an installation

```powershell
python C:\Users\24976\.dsh\skills\figure-making-WXL\scripts\check_wxl_style.py
```

Expected tail: `RESULT: PASS`, with `font files: ['times.ttf', ...]` and
`font sizes (pt): [10.0]`.

## Related files

- [../SKILL.md](../SKILL.md) — hard rules
- [api.md](api.md) — signatures
- [common-patterns.md](common-patterns.md) — more recipes
- [demos.md](demos.md) — the 20 chart types
