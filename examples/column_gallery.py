"""Column-format gallery: every chart type at 90 mm and 190 mm, in one .docx.

    pip install python-docx
    python column_gallery.py --out ./wxl_columns

Renders all 20 chart types twice (single column 90 mm, double column 190 mm),
audits each render, then assembles a Word document with the paper layout
contract applied through ``assets/wxl_docx.py``: one page per chart type showing
both variants stacked, a cover page with a three-line summary table, figure
captions below each figure.

Exit code is non-zero if any figure fails the audit or misses its target width.
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
    WXL_FIGSIZE, WXL_WIDTH_MM, apply_wxl_style, check_wxl_style,
    finalize_figure, measure_width_mm, prepare_figure,
)
from wxl_docx import (  # noqa: E402
    add_caption, add_figure, add_heading, add_page_break, add_paragraph,
    add_three_line_table, add_title, new_document,
)

DPI = 600
VARIANTS = [("single", "单栏", "90 mm"), ("double", "两栏", "190 mm")]

CATEGORY_CN = {"bar": "柱状 / 条形", "line": "折线 / 面积", "rel": "关系",
               "dist": "分布", "matrix": "矩阵 / 场", "special": "特殊"}

#: layout recommendation per chart type
RECOMMEND = {
    "grouped_bar": "两栏", "stacked_bar": "两者皆可", "horizontal_bar": "单栏",
    "line_trend": "两者皆可", "line_band": "单栏", "stacked_area": "两栏",
    "scatter_fit": "两者皆可", "bubble": "两者皆可", "errorbar": "两者皆可",
    "boxplot": "两者皆可", "violin": "两者皆可", "hist_kde": "两者皆可",
    "ecdf": "单栏", "strip_mean": "两栏", "heatmap": "两栏", "contour": "两栏",
    "radar": "两栏", "donut": "单栏", "dual_axis": "两栏", "multi_panel": "两栏",
}


def render_variant(spec, preset, outdir: Path, reuse: bool = False):
    png = outdir / f'{spec["id"]}_{preset}.png'
    if reuse and png.exists():
        mm = measure_width_mm(png, DPI)
        ok = abs(mm - WXL_WIDTH_MM[preset]) <= 0.6
        report = {"ok": ok, "sizes": ["reused"], "warnings": [], "problems": []}
        return png, mm, report, ok
    apply_wxl_style()
    fig = spec["fn"]()
    fig.set_size_inches(*WXL_FIGSIZE[preset])
    prepare_figure(fig)
    report = check_wxl_style(fig)
    finalize_figure(fig, png.with_suffix(""), formats=["png"], dpi=DPI,
                    target_width_mm=WXL_WIDTH_MM[preset])
    plt.close(fig)
    mm = measure_width_mm(png, DPI)
    ok = report["ok"] and abs(mm - WXL_WIDTH_MM[preset]) <= 0.6
    return png, mm, report, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "wxl_columns"))
    ap.add_argument("--reuse", action="store_true",
                    help="rebuild the document from existing PNGs without re-rendering")
    args = ap.parse_args()
    outdir = Path(args.out)
    figs = outdir / "figs600"
    figs.mkdir(parents=True, exist_ok=True)

    records, failures = [], 0
    for i, spec in enumerate(gallery.FIGS, start=1):
        entry = {"idx": i, "spec": spec, "variants": {}}
        for preset, label, mm_label in VARIANTS:
            png, mm, report, ok = render_variant(spec, preset, figs, args.reuse)
            failures += 0 if ok else 1
            entry["variants"][preset] = {"png": png, "mm": mm, "label": label,
                                         "mm_label": mm_label, "report": report,
                                         "ok": ok}
            print(f"[{'PASS' if ok else 'FAIL'}] {i:02d} {spec['id']:<16} "
                  f"{label} {mm:7.2f} mm (target {WXL_WIDTH_MM[preset]:.0f}) "
                  f"sizes={report['sizes']} warns={len(report['warnings'])}")
            for wmsg in report["warnings"]:
                print("        warn:", wmsg)
            for pmsg in report["problems"]:
                print("        prob:", pmsg)
        records.append(entry)

    # ---- document -----------------------------------------------------
    doc = new_document()
    add_title(doc, "figure-making-WXL · 全部图型 · 单栏与两栏")
    add_paragraph(doc, "本文件把 WXL 样式的 20 种图型各出两版，单栏 90 mm 与两栏 "
                       "190 mm，同页上下对比。两版使用相同纵横比与相同字号，差异只"
                       "来自物理宽度，也就是 10 pt 文字在版面上占多大比例。全部图片"
                       "按 100 % 原始尺寸插入，图内文字与正文 10 pt 字号一致。",
                  spacing=1.5, space_after=8)
    add_paragraph(doc, "选择原则：图内元素少、图例不超过三项时用单栏更省版面。"
                       "分组较多、图例较长，或需要热图、雷达图这类宽幅图形时用两栏。",
                  spacing=1.5, space_after=8)

    add_heading(doc, "图型与版式一览")
    rows = []
    for rec in records:
        single = rec["variants"]["single"]
        double = rec["variants"]["double"]
        rows.append([rec["idx"], rec["spec"]["title"],
                     CATEGORY_CN[rec["spec"]["category"]],
                     f'{single["mm"]:.1f} mm', f'{double["mm"]:.1f} mm',
                     RECOMMEND.get(rec["spec"]["id"], "两者皆可")])
    add_three_line_table(doc, ["序号", "图型", "类别", "单栏", "两栏", "推荐"],
                         rows, col_widths_cm=[1.4, 7.6, 3.0, 2.0, 2.0, 2.6])

    for rec in records:
        add_page_break(doc)
        add_heading(doc, f'{rec["idx"]}. {rec["spec"]["title"]}')
        for preset, _label, _mm in VARIANTS:
            v = rec["variants"][preset]
            inserted = add_figure(doc, v["png"], dpi=DPI)
            add_caption(doc, f'图 {rec["idx"]}{"a" if preset == "single" else "b"}  '
                             f'{v["label"]}版式（{v["mm_label"]}，实际插入 '
                             f'{inserted:.1f} mm）')
        warn = (rec["variants"]["single"]["report"]["warnings"]
                + rec["variants"]["double"]["report"]["warnings"])
        note = (f'推荐版式：{RECOMMEND.get(rec["spec"]["id"], "两者皆可")}    '
                f'单栏自检：{"PASS" if rec["variants"]["single"]["ok"] else "FAIL"}    '
                f'两栏自检：{"PASS" if rec["variants"]["double"]["ok"] else "FAIL"}')
        if warn:
            note += "    提示：" + "；".join(sorted(set(warn)))
        add_paragraph(doc, note, size=9, spacing=1.0, indent_chars=0, space_after=0)

    out = outdir / "WXL_chart_types_single_and_double_column.docx"
    doc.save(out)
    print(f"\ntypes: {len(records)}  renders: {len(records) * 2}  failures: {failures}")
    print("docx:", out, f"{out.stat().st_size / 1024 / 1024:.2f} MB")
    sys.stdout.flush()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
