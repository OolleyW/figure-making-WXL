# figure-making-WXL

Publication-ready matplotlib figures in the **WXL house style** for Elsevier,
IEEE and Springer submissions. Every text element is Times New Roman at a
uniform **10 pt**, so figure text matches Word 10 pt body text when the image is
inserted at its original size.

论文配图样式技能：Times New Roman 统一 10 pt、深蓝主色系、四边全包围、图例带黑框、
刻度朝内、无网格，图幅按 90 / 140 / 190 mm 印刷宽度校准。

## Style contract

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

## Usage

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"C:\Users\24976\.dsh\skills\figure-making-WXL\assets")))
from wxl_style import (WXL_PALETTE as P, WXL_FIGSIZE, WXL_WIDTH_MM, apply_wxl_style,
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
finalize_figure(fig, "figures/accuracy", formats=["png", "pdf"], dpi=600,
                target_width_mm=WXL_WIDTH_MM["double"])
```

## Chart types (20)

Bar: grouped with error bars, stacked, horizontal.
Line: multi-series trend, trend + uncertainty band, stacked area.
Relationship: scatter + fit, bubble, bidirectional error bars.
Distribution: box, violin, histogram + KDE, ECDF, strip + mean.
Matrix: annotated heatmap, filled contour.
Special: radar, donut, dual axis, 2 × 2 multi-panel.

Runnable code for all of them is in `examples/gallery.py`; rendered previews are
in `preview/`.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | hard rules and when to load the skill |
| `references/api.md` | constants, `WXLStyle`, signatures, audit contract |
| `references/design-theory.md` | why 10 pt, the tight-crop trap, palette semantics, exceptions |
| `references/common-patterns.md` | legend placement, multi-panel, dual axes, print-safe encoding |
| `references/tutorials.md` | three end-to-end walkthroughs |
| `references/demos.md` | the 20 chart types with core calls |
| `assets/wxl_style.py` | importable style module (rcParams, palette, helpers, audit) |
| `scripts/check_wxl_style.py` | installation self-test |
| `examples/gallery.py` | render all 20 types + an HTML gallery |
| `preview/*.png` | 300 dpi previews of the 20 chart types |

## Regenerate

```powershell
# installation self-test
python scripts\check_wxl_style.py

# all 20 figures + HTML gallery
python examples\gallery.py --out C:\DSH_work\wxl_gallery
```

## Requirements

Python 3.10+, `matplotlib`, `numpy`, `Pillow` (width measurement). The Word
preview script additionally needs `python-docx`.

## Notes

- The style is enforced, not suggested: `check_wxl_style` fails on a non-Times
  font, a non-10 pt size, a hidden spine, a grid line, an outward tick, an
  unframed legend or an off-palette color.
- Documented exceptions: polar axes (radar) keep a light grid, pie/donut axes
  are turned off, colorbar axes are exempt from the four-spine rule.
- Slide export uses the `slide` preset; the 10 pt / print-width contract does
  not apply to slides.
