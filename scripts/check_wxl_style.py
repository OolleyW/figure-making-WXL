"""Self-test for the WXL figure style.

Run it after installing or editing the style module:

    python scripts/check_wxl_style.py

It builds a reference figure that exercises bars, lines, an error bar, a
colorbar, a framed legend, an annotation, panel tags and a below-figure
caption, then audits it against the WXL contract and prints the measured
values. Exit code 0 = PASS, 1 = FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))

from wxl_style import (  # noqa: E402
    WXL_FIGSIZE, WXL_FONTSIZE, WXL_PALETTE, add_caption, apply_wxl_style,
    check_wxl_style, create_subplots, framed_legend, panel_tag,
)

P = WXL_PALETTE


def build_reference_figure():
    apply_wxl_style()
    fig, axes = create_subplots(1, 2, figsize=WXL_FIGSIZE["double"])
    rng = np.random.default_rng(0)

    ax = axes[0]
    x = np.arange(4)
    for i, (name, key, vals) in enumerate([
            ("Proposed", "primary", [0.82, 0.88, 0.91, 0.94]),
            ("Baseline", "contrast", [0.61, 0.64, 0.67, 0.70])]):
        v = np.asarray(vals)
        ax.bar(x + (i - 0.5) * 0.3, v, 0.3, yerr=0.02, label=name, color=P[key],
               edgecolor="black", linewidth=0.8,
               error_kw=dict(elinewidth=0.8, capsize=2, ecolor=P[key]))
    ax.set_xticks(x)
    ax.set_xticklabels(["S1", "S2", "S3", "S4"])
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.35)
    ax.text(0.02, 0.98, "n = 30", transform=ax.transAxes, va="top")
    framed_legend(ax, loc="upper left")
    panel_tag(ax, "(a)", y=-0.28)

    ax = axes[1]
    xv = np.linspace(0, 10, 11)
    ax.errorbar(xv, 0.6 + 0.03 * xv, yerr=0.03, fmt="-o", color=P["primary"],
                mfc="white", ms=3.2, mew=0.9, elinewidth=0.8, capsize=2,
                label="Measured")
    ax.plot(xv, 0.55 + 0.028 * xv, "-s", color=P["improve"], lw=1.5, ms=3.2,
            mfc="white", mew=0.9, label="Model")
    ax.fill_between(xv, 0.5 + 0.02 * xv, 0.62 + 0.03 * xv,
                    color=P["light"], edgecolor=P["primary"], linewidth=0.6)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Score")
    framed_legend(ax, loc="upper left", ncol=2, columnspacing=1.0, handlelength=1.6)
    panel_tag(ax, "(b)", y=-0.28)

    im = ax.scatter(rng.random(5), rng.random(5), s=14, color=P["accent"],
                    edgecolor="black", linewidth=0.4)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.ax.tick_params(direction="in", width=0.8)
    cb.outline.set_linewidth(0.8)

    add_caption(fig, "Fig. 1  Reference figure exercising every WXL style element.")
    return fig


def main() -> int:
    fig = build_reference_figure()
    report = check_wxl_style(fig)
    plt.close(fig)

    print("WXL style self-test")
    print("-" * 58)
    print(f"  font files      : {report['fonts']}")
    print(f"  font sizes (pt) : {report['sizes']}")
    print(f"  axes checked    : {report['n_axes']}")
    print(f"  framed legends  : {report['n_legends']}")
    print(f"  expected size   : {sorted({float(WXL_FONTSIZE['caption'])})} pt uniform")
    print(f"  palette keys    : {sorted(P)}")
    if report["warnings"]:
        for w in report["warnings"]:
            print(f"  [warning] {w}")
    if report["problems"]:
        print("  problems:")
        for p in report["problems"]:
            print(f"    - {p}")
    print("-" * 58)
    print("RESULT:", "PASS" if report["ok"] else "FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
