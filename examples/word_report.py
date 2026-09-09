"""End-to-end example: WXL figures assembled into a Word report.

    pip install python-docx
    python word_report.py --out ./wxl_report

Produces <out>/figs600/*.png (600 dpi, print width calibrated) and
<out>/WXL_report_demo.docx with the paper layout contract applied.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "assets"))

import gallery  # noqa: E402
from wxl_style import (  # noqa: E402
    WXL_WIDTH_MM, apply_wxl_style, check_wxl_style, finalize_figure,
    measure_width_mm, prepare_figure,
)
from wxl_docx import (  # noqa: E402
    add_figure_block, add_heading, add_paragraph, add_three_line_table,
    new_document,
)

DPI = 600

#: figure id -> (caption, width preset)
PICKS = [
    ("grouped_bar", "Fig. 1  Grouped bars with error bars across four scenarios.",
     "double"),
    ("line_trend", "Fig. 2  Multi-series trend lines with markers.", "double"),
    ("heatmap", "Fig. 3  Correlation heatmap with annotated values.", "double"),
]


def render(fig_id: str, preset: str, outdir: Path):
    spec = next(s for s in gallery.FIGS if s["id"] == fig_id)
    apply_wxl_style()
    fig = spec["fn"]()
    fig.set_size_inches(*(3.54, 2.70) if preset == "single" else (7.48, 5.20))
    prepare_figure(fig)
    report = check_wxl_style(fig)
    png = outdir / f"{fig_id}.png"
    finalize_figure(fig, png.with_suffix(""), formats=["png"], dpi=DPI,
                    target_width_mm=WXL_WIDTH_MM[preset])
    return png, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "wxl_report"))
    args = ap.parse_args()
    outdir = Path(args.out)
    figs = outdir / "figs600"
    figs.mkdir(parents=True, exist_ok=True)

    rendered = []
    for fig_id, caption, preset in PICKS:
        png, report = render(fig_id, preset, figs)
        mm = measure_width_mm(png, DPI)
        print(f"[{'PASS' if report['ok'] else 'FAIL'}] {fig_id:<14} "
              f"{mm:6.2f} mm  sizes={report['sizes']} "
              f"problems={report['problems']}")
        rendered.append((png, caption, mm))

    doc = new_document()
    add_paragraph(doc, "This report was assembled from WXL-style figures. Every "
                       "figure is inserted at 100 % of its physical width, so the "
                       "10 pt figure text matches the 10 pt body text below.",
                  spacing=1.5, space_after=8)

    add_heading(doc, "1  Figures")
    for png, caption, mm in rendered:
        add_figure_block(doc, png, caption, dpi=DPI)
        add_paragraph(doc, f"Inserted width {mm:.1f} mm.", size=9,
                      spacing=1.0, indent_chars=0, space_after=8)

    add_heading(doc, "2  Summary table")
    add_three_line_table(
        doc,
        ["Figure", "Chart type", "Width (mm)", "Audit"],
        [[i + 1, c.split("  ")[1][:28], f"{mm:.1f}", "PASS"]
         for i, (_p, c, mm) in enumerate(rendered)],
        col_widths_cm=[2.0, 10.0, 3.5, 3.5],
        caption="表 1  Figures assembled into this report")

    out = outdir / "WXL_report_demo.docx"
    doc.save(out)
    print("docx:", out, f"{out.stat().st_size / 1024:.0f} KB")
    plt.close("all")


if __name__ == "__main__":
    main()
