"""WXL style gallery: every supported chart type rendered under the house style.

Usage:
    python gallery.py --out ./wxl_gallery        # defaults to ~/wxl_gallery

Produces <out>/figs/<id>.png (300 dpi, for the HTML preview),
<out>/figs/<id>.pdf (vector) and <out>/index.html.
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "assets"))

from wxl_style import (  # noqa: E402
    WXL_AXES_PANEL_MM, WXL_CMAP, WXL_CMAPS, WXL_FIGSIZE, WXL_FONTSIZE, WXL_INK,
    WXL_LINE_PALETTE, WXL_PALETTE, WXL_WIDTH_MM, add_caption, add_caption_below,
    annotate_bars, apply_wxl_style, center_grid, check_wxl_style, create_subplots,
    finalize_figure, framed_legend, marker_handle, measure_width_mm,
    paint_markers, panel_tag, plot_series, prepare_figure,
)

P = WXL_PALETTE          # light fills
PL = WXL_LINE_PALETTE    # deep lines / markers
RNG = np.random.default_rng(20260910)

# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
FIGS: list[dict] = []


def figure(fig_id, title, category, desc, code, width="double"):
    def deco(fn):
        FIGS.append({"id": fig_id, "title": title, "category": category,
                     "desc": desc, "code": code, "width": width, "fn": fn})
        return fn
    return deco


def _kde(x, grid, bw=None):
    x = np.asarray(x, float)
    n = x.size
    bw = bw or 1.06 * x.std(ddof=1) * n ** (-0.2)
    d = (grid[:, None] - x[None, :]) / bw
    return np.exp(-0.5 * d ** 2).sum(axis=1) / (n * bw * np.sqrt(2 * np.pi))


# --------------------------------------------------------------------------
# line / marker family (shown first)
# --------------------------------------------------------------------------
@figure("line_markers", "多曲线点线图（不同点样式）", "line",
        "一张图叠放五条测量曲线，每条曲线的标记形状都不同、统一白色填充，"
        "即使黑白打印也能靠点形区分。",
        'for name, key, mk, vals in series:\n'
        '    handles.append(plot_series(ax, x, vals, PL[key], label=name,\n'
        '                               marker=mk))\n'
        'framed_legend(ax, handles=handles, loc="upper left", ncol=2)')
def fig_line_markers():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["single"])
    x = np.linspace(0, 10, 11)
    # (label, palette key, marker, values) - the marker shape carries the series
    # identity, so the set still separates in greyscale
    series = [
        ("Mix A", "primary", "o",
         [0.30, 0.43, 0.54, 0.62, 0.69, 0.75, 0.79, 0.83, 0.86, 0.89, 0.91]),
        ("Mix B", "contrast", "s",
         [0.15, 0.26, 0.36, 0.44, 0.51, 0.57, 0.62, 0.67, 0.71, 0.75, 0.78]),
        ("Mix C", "improve", "^",
         [0.08, 0.17, 0.25, 0.32, 0.38, 0.44, 0.49, 0.54, 0.58, 0.62, 0.66]),
        ("Mix D", "accent", "D",
         [0.38, 0.52, 0.63, 0.72, 0.78, 0.83, 0.87, 0.90, 0.92, 0.94, 0.95]),
        ("Mix E", "secondary", "v",
         [0.22, 0.34, 0.44, 0.53, 0.60, 0.66, 0.71, 0.76, 0.80, 0.83, 0.86]),
    ]
    handles = []
    for name, key, mk, vals in series:
        handles.append(plot_series(ax, x, vals, PL[key], label=name, marker=mk))
    ax.set_xlabel("Age (d)")
    ax.set_ylabel("Degree of hydration (-)")
    ax.set_xlim(0, 10)
    # generous headroom so the five-entry legend clears the top curve
    ax.set_ylim(0, 1.55)
    framed_legend(ax, handles=handles, loc="upper left", ncol=2,
                  columnspacing=0.9, handlelength=1.3, handletextpad=0.5,
                  labelspacing=0.35)
    add_caption_below(fig, r"$\mathbf{Fig.}$  1  Multi-series line chart with distinct marker shapes.")
    return fig


# --------------------------------------------------------------------------
# bar family
# --------------------------------------------------------------------------
@figure("grouped_bar", "分组柱状图（含误差棒）", "bar",
        "三组方法在四个场景下的对比，柱顶标数值，误差棒表示标准差。",
        'ax.bar(x + (i-1)*w, vals, w, yerr=err, color=PALETTE[key],\n'
        '       edgecolor=WXL_INK, linewidth=0.5,\n'
        '       error_kw=dict(elinewidth=0.5, capsize=2))')
def fig_grouped_bar():
    cats = ["S1", "S2", "S3", "S4"]
    series = [("Proposed", [0.82, 0.88, 0.91, 0.94], "primary"),
              ("Baseline", [0.61, 0.64, 0.67, 0.70], "contrast"),
              ("Variant", [0.70, 0.75, 0.79, 0.83], "improve")]
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x, w = np.arange(len(cats)), 0.26
    for i, (name, vals, key) in enumerate(series):
        v = np.asarray(vals)
        e = np.full_like(v, 0.02)
        bars = ax.bar(x + (i - 1) * w, v, w, yerr=e, label=name,
                      color=P[key], edgecolor=WXL_INK, linewidth=0.5,
                      error_kw=dict(elinewidth=0.5, capsize=2, ecolor=PL[key]))
        annotate_bars(ax, bars, y_offset_frac=0.035)   # skipped when too wide
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.55)
    framed_legend(ax, loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  2  Grouped bars with error bars across four scenarios.")
    return fig


@figure("stacked_bar", "堆叠柱状图", "bar",
        "组成占比类数据，总高度表示总量，分段颜色表示构成。",
        'ax.bar(x, a, label="A", color=PALETTE["primary"], edgecolor=WXL_INK)\n'
        'ax.bar(x, b, bottom=a, label="B", color=PALETTE["contrast"], ...)')
def fig_stacked_bar():
    cats = ["2021", "2022", "2023", "2024"]
    parts = [("Cement", [42, 45, 44, 46], "primary"),
             ("Aggregate", [31, 30, 33, 32], "contrast"),
             ("Admixture", [27, 25, 23, 22], "improve")]
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.arange(len(cats))
    bottom = np.zeros(len(cats))
    for name, vals, key in parts:
        v = np.asarray(vals, float)
        ax.bar(x, v, 0.5, bottom=bottom, label=name, color=P[key],
               edgecolor=WXL_INK, linewidth=0.5)
        bottom += v
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_xlabel("Year")
    ax.set_ylabel("Mass fraction (%)")
    # raise the upper y-limit so a vertical legend fits in the headroom above
    # the bars (the stack tops out at 100)
    ax.set_ylim(0, 165)
    framed_legend(ax, loc="upper left", ncol=1, handlelength=1.8, handletextpad=0.6)
    add_caption_below(fig, r"$\mathbf{Fig.}$  3  Stacked bars of mixture composition by year.")
    return fig


@figure("horizontal_bar", "水平条形图（排序 + 数值）", "bar",
        "类别名较长或需要排序时使用，数值直接标在条末。",
        'ax.barh(y, vals, color=PALETTE["primary"], edgecolor=WXL_INK)\n'
        'ax.text(v + pad, y, f"{v:.1f}", va="center")')
def fig_horizontal_bar():
    names = ["Mix A", "Mix B", "Mix C", "Mix D", "Mix E", "Mix F"]
    vals = np.array([86.4, 79.1, 74.8, 68.2, 61.5, 55.9])
    order = np.argsort(vals)
    names = [names[i] for i in order]
    vals = vals[order]
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    y = np.arange(len(names))
    ax.barh(y, vals, 0.55, color=P["primary"], edgecolor=WXL_INK, linewidth=0.5)
    for yi, v in zip(y, vals):
        ax.text(v + 1.2, yi, f"{v:.1f}", va="center", ha="left")
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Strength retention (%)")
    ax.set_xlim(0, 100)
    add_caption_below(fig, r"$\mathbf{Fig.}$  4  Horizontal bars sorted by strength retention.")
    return fig


# --------------------------------------------------------------------------
# line family
# --------------------------------------------------------------------------
@figure("line_trend", "多序列折线图（带标记）", "line",
        "最常见的趋势图，四组方法随 epoch 变化，每条曲线用不同的点形区分，"
        "黑白打印也能读。",
        'for name, key, mk, base, slope in curves:\n'
        '    handles.append(plot_series(ax, x, y, PL[key], label=name,\n'
        '                               marker=mk))')
def fig_line_trend():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.linspace(0, 10, 11)
    curves = [("Method A", "primary", "o", 0.62, 0.030),
              ("Method B", "contrast", "s", 0.58, 0.024),
              ("Method C", "improve", "^", 0.54, 0.020),
              ("Method D", "accent", "D", 0.50, 0.015)]
    handles = []
    for name, key, mk, base, slope in curves:
        y = base + slope * x + RNG.normal(0, 0.005, x.size)
        handles.append(plot_series(ax, x, y, PL[key], label=name, marker=mk))
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Score")
    framed_legend(ax, handles=handles, loc="upper left", ncol=2,
                  columnspacing=1.0, handlelength=1.6, handletextpad=0.5)
    add_caption_below(fig, r"$\mathbf{Fig.}$  5  Multi-series trend lines with distinct markers.")
    return fig


@figure("line_band", "折线 + 不确定度带", "line",
        "用 fill_between 画置信区间或标准差带，主曲线压在上层。",
        'ax.fill_between(x, y-sd, y+sd, color=PALETTE["light"],\n'
        '                edgecolor=PALETTE["primary"], linewidth=0.5)\n'
        'ax.plot(x, y, "-", color=PALETTE["primary"], lw=1.5)')
def fig_line_band():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.linspace(0, 10, 60)
    for key, label, base, slope, sd in [("primary", "Proposed", 0.55, 0.035, 0.035),
                                        ("contrast", "Baseline", 0.50, 0.022, 0.045)]:
        y = base + slope * x
        band = sd * (1 + 0.12 * x)
        ax.fill_between(x, y - band, y + band, color=P["light"] if key == "primary"
                        else P["neutral"], alpha=0.35, edgecolor=PL[key], linewidth=0.5)
        ax.plot(x, y, "-", color=PL[key], lw=1.5, label=label)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Response (mV)")
    framed_legend(ax, loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  6  Trend lines with uncertainty bands.")
    return fig


@figure("stacked_area", "堆叠面积图", "line",
        "构成随时间变化，面积顺序与图例顺序一致。",
        'ax.stackplot(x, *series, colors=[PALETTE[k] for k in keys],\n'
        '             edgecolor=WXL_INK, linewidth=0.5)')
def fig_stacked_area():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.linspace(0, 10, 200)
    keys = ["primary", "contrast", "improve", "accent"]
    labels = ["Phase I", "Phase II", "Phase III", "Phase IV"]
    raw = [0.6 + 0.05 * x, 0.4 + 0.06 * x, 0.3 + 0.04 * x, 0.2 + 0.03 * x]
    ax.stackplot(x, *raw, colors=[P[k] for k in keys], labels=labels,
                 edgecolor=WXL_INK, linewidth=0.5)
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Cumulative release (%)")
    ax.set_xlim(0, 10)
    framed_legend(ax, loc="upper left", ncol=2, columnspacing=1.0, handlelength=1.4)
    add_caption_below(fig, r"$\mathbf{Fig.}$  7  Stacked area chart of cumulative release.")
    return fig


# --------------------------------------------------------------------------
# relationship family
# --------------------------------------------------------------------------
@figure("scatter_fit", "散点 + 拟合线", "rel",
        "两组样本的实测 vs 预测，配一条最小二乘拟合线。",
        'ax.scatter(x, y, s=14, color=WXL_LINE_PALETTE[key],\n'
        '           edgecolor=WXL_INK, linewidth=0.4, label=name)\n'
        'ax.plot(xs, k*xs+b, "-", color=PALETTE[key], lw=1.2)')
def fig_scatter_fit():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    for name, key, slope, noise in [("Group I", "primary", 1.02, 0.7),
                                    ("Group II", "accent", 0.86, 0.9)]:
        x = RNG.uniform(2, 9, 45)
        y = slope * x + RNG.normal(0, noise, x.size)
        k, b = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, k * xs + b, "-", color=PL[key], lw=1.2)
        # no gap here: the points are not threaded on the line, so breaking the
        # fit around all 45 of them would shred it
        paint_markers(ax, x, y, PL[key], gap=0.0)
    ax.set_xlabel("Measured")
    ax.set_ylabel("Predicted")
    framed_legend(ax, handles=[marker_handle(PL[k], n)
                               for n, k in (("Group I", "primary"),
                                            ("Group II", "accent"))],
                  loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  8  Scatter plot with least-squares fits.")
    return fig


@figure("bubble", "气泡图（大小 + 颜色双编码）", "rel",
        "第三个变量用点面积表示，第四个变量用颜色表示。",
        'ax.scatter(x, y, s=size*scale, c=[PALETTE[k] for k in keys],\n'
        '           edgecolor=WXL_INK, linewidth=0.4, alpha=0.85)')
def fig_bubble():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = RNG.uniform(1, 10, 18)
    y = 0.6 * x + RNG.normal(0, 1.0, 18)
    size = RNG.uniform(20, 260, 18)
    ax.scatter(x, y, s=size, color=PL["primary"], edgecolor=WXL_INK,
               linewidth=0.4, alpha=0.75, label="Sample")
    big = np.argsort(size)[-3:]
    ax.scatter(x[big], y[big], s=size[big], color=PL["accent"], edgecolor=WXL_INK,
               linewidth=0.4, alpha=0.9, label="Outlier candidate")
    ax.set_xlabel("Dosage (mg)")
    ax.set_ylabel("Response")
    framed_legend(ax, loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  9  Bubble chart with size- and colour-encoded groups.")
    return fig


@figure("errorbar", "误差棒图（x、y 双向）", "rel",
        "实验点同时带 x 和 y 方向误差，常用于标定曲线。",
        'ax.errorbar(x, y, xerr=xe, yerr=ye, fmt="none",\n'
        '            ecolor=WXL_LINE_PALETTE["primary"], elinewidth=0.5, capsize=2)\n'
        'paint_markers(ax, x, y, WXL_LINE_PALETTE["primary"])')
def fig_errorbar():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.linspace(1, 9, 9)
    y = 1.8 * np.log(x) + 0.9
    xe = np.full_like(x, 0.25)
    ye = np.full_like(x, 0.18)
    ax.errorbar(x, y, xerr=xe, yerr=ye, fmt="none", ecolor=PL["primary"],
                elinewidth=0.5, capsize=2, zorder=1)
    paint_markers(ax, x, y, PL["primary"])
    ax.plot(x, 1.8 * np.log(x) + 0.9, "-", color=PL["contrast"], lw=1.2,
            label="Model")
    ax.set_xlabel("Strain (%)")
    ax.set_ylabel("Stress (MPa)")
    framed_legend(ax, handles=[marker_handle(PL["primary"], "Measured"),
                               Line2D([], [], color=PL["contrast"], lw=1.2,
                                      label="Model")], loc="lower right")
    add_caption_below(fig, r"$\mathbf{Fig.}$  10  Error bars in both x and y directions.")
    return fig


# --------------------------------------------------------------------------
# distribution family
# --------------------------------------------------------------------------
@figure("boxplot", "箱线图", "dist",
        "四组分布对比，箱体填主色，中位数加粗黑线。",
        'ax.boxplot(data, patch_artist=True, widths=0.55,\n'
        '           medianprops=dict(color=WXL_INK, linewidth=1.2))\n'
        'for patch, key in zip(bp["boxes"], keys): patch.set_facecolor(PALETTE[key])',
        width="onehalf")
def fig_boxplot():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["onehalf"])
    keys = ["primary", "contrast", "improve", "accent"]
    labels = ["A", "B", "C", "D"]
    data = [RNG.normal(m, s, 60) for m, s in [(10, 1.6), (12, 2.2), (11, 1.1), (13, 2.8)]]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                    medianprops=dict(color=WXL_INK, linewidth=1.2),
                    whiskerprops=dict(color=WXL_INK, linewidth=0.5),
                    capprops=dict(color=WXL_INK, linewidth=0.5),
                    boxprops=dict(edgecolor=WXL_INK, linewidth=0.5))
    for patch, key in zip(bp["boxes"], keys):
        patch.set_facecolor(P[key])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Value")
    framed_legend(ax, handles=[Patch(facecolor=P[k], edgecolor=WXL_INK,
                                     linewidth=0.5, label=l)
                               for k, l in zip(keys, labels)], loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  11  Box plots of four groups.")
    return fig


@figure("violin", "小提琴图", "dist",
        "展示分布形状，均值用黑点标出，适合样本量较大的组间比较。",
        'vp = ax.violinplot(data, showmeans=True, showextrema=False)\n'
        'for body, key in zip(vp["bodies"], keys):\n'
        '    body.set_facecolor(PALETTE[key]); body.set_edgecolor(WXL_INK)',
        width="onehalf")
def fig_violin():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["onehalf"])
    keys = ["primary", "contrast", "improve"]
    labels = ["Control", "Treated", "Optimised"]
    data = [RNG.normal(m, s, 160) for m, s in [(0.0, 1.0), (0.7, 1.3), (1.4, 0.8)]]
    vp = ax.violinplot(data, showmeans=True, showextrema=False, widths=0.7)
    for body, key in zip(vp["bodies"], keys):
        body.set_facecolor(P[key])
        body.set_edgecolor(WXL_INK)
        body.set_linewidth(0.5)
        body.set_alpha(0.9)
    vp["cmeans"].set_color(WXL_INK)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(labels)
    ax.set_ylabel("Normalised response")
    framed_legend(ax, handles=[Patch(facecolor=P[k], edgecolor=WXL_INK,
                                     linewidth=0.5, label=l)
                               for k, l in zip(keys, labels)], loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  12  Violin plots with mean markers.")
    return fig


@figure("hist_kde", "直方图 + 核密度曲线", "dist",
        "直方图用浅色填充黑边，核密度曲线叠加显示分布形态。",
        'ax.hist(data, bins=20, color=PALETTE["light"], edgecolor=WXL_INK,\n'
        '        linewidth=0.5, label="Histogram")\n'
        'ax.plot(grid, kde, color=PALETTE["primary"], lw=1.5, label="KDE")')
def fig_hist_kde():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    data = np.concatenate([RNG.normal(0, 1.0, 400), RNG.normal(3.2, 0.8, 160)])
    ax.hist(data, bins=22, density=True, color=P["light"], edgecolor=WXL_INK,
            linewidth=0.5, label="Histogram")
    grid = np.linspace(data.min() - 0.5, data.max() + 0.5, 400)
    ax.plot(grid, _kde(data, grid), "-", color=PL["primary"], lw=1.5, label="KDE")
    ax.axvline(float(np.mean(data)), color=PL["contrast"], lw=1.2, ls="--",
               label="Mean")
    ax.set_xlabel("Residual (mm)")
    ax.set_ylabel("Density")
    framed_legend(ax, loc="upper right")
    add_caption_below(fig, r"$\mathbf{Fig.}$  13  Histogram with kernel density estimate.")
    return fig


@figure("ecdf", "经验累积分布（ECDF）", "dist",
        "比直方图更稳健的分布比较，用阶梯线绘制。",
        'ax.step(x_sorted, np.arange(1, n+1)/n, where="post",\n'
        '        color=PALETTE[key], lw=1.5, label=name)',
        width="single")
def fig_ecdf():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["single"])
    for name, key, mu, sd in [("Set A", "primary", 0.0, 1.0),
                              ("Set B", "contrast", 0.8, 1.2)]:
        x = np.sort(RNG.normal(mu, sd, 220))
        ax.step(x, np.arange(1, x.size + 1) / x.size, where="post",
                color=P[key], lw=1.5, label=name)
    ax.set_xlabel("Value")
    ax.set_ylabel("Cumulative probability")
    ax.set_ylim(0, 1.02)
    framed_legend(ax, loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  14  Empirical cumulative distribution functions.")
    return fig


@figure("strip_mean", "散点条带 + 均值误差（分类分布）", "dist",
        "原始点抖动铺开，叠加均值与标准差，适合小样本。",
        'ax.scatter(jitter, y, s=12, color=PALETTE[key], alpha=0.6,\n'
        '           edgecolor=WXL_INK, linewidth=0.3)\n'
        'ax.errorbar(centers, means, yerr=sds, fmt="s", color=WXL_INK)')
def fig_strip_mean():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    keys = ["primary", "contrast", "improve", "accent"]
    labels = ["Batch 1", "Batch 2", "Batch 3", "Batch 4"]
    means = [8.2, 9.6, 9.1, 10.4]
    sds = [1.1, 1.4, 0.9, 1.6]
    for i, (key, mu, sd) in enumerate(zip(keys, means, sds)):
        y = RNG.normal(mu, sd, 26)
        ax.scatter(i + RNG.normal(0, 0.07, y.size), y, s=12, color=PL[key],
                   alpha=0.6, edgecolor=WXL_INK, linewidth=0.3,
                   label=labels[i])
    ax.errorbar(np.arange(4), means, yerr=sds, fmt="s", color=WXL_INK,
                ms=3.5, elinewidth=0.5, capsize=3)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Measured value")
    framed_legend(ax, loc="upper left", ncol=2, columnspacing=1.0, handlelength=1.4)
    add_caption_below(fig, r"$\mathbf{Fig.}$  15  Strip plot with mean and standard deviation.")
    return fig


# --------------------------------------------------------------------------
# matrix family
# --------------------------------------------------------------------------
@figure("heatmap", "热图（带色条与数值）", "matrix",
        "相关系数矩阵，玫红↔蓝发散色图（采样配色适配），单元格标数值。只出单栏版。",
        'im = ax.imshow(m, cmap=WXL_CMAP, vmin=-1, vmax=1)\n'
        'cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)\n'
        'cb.outline.set_linewidth(0.5)', width="single")
def fig_heatmap():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    m = RNG.uniform(-1, 1, (6, 6))
    m = (m + m.T) / 2
    np.fill_diagonal(m, 1.0)
    im = ax.imshow(m, cmap=WXL_CMAP, vmin=-1, vmax=1)
    ticks = [f"V{i + 1}" for i in range(6)]
    ax.set_xticks(range(6), ticks)
    ax.set_yticks(range(6), ticks)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center",
                    fontsize=WXL_FONTSIZE["annot"])
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Correlation")
    cb.ax.tick_params(direction="in", width=0.8)
    cb.outline.set_linewidth(0.5)
    add_caption_below(fig, r"$\mathbf{Fig.}$  16  Correlation heatmap with annotated values.")
    return fig


@figure("contour", "填色等值线图", "matrix",
        "二维场分布，色条显示量级，适合应力场、温度场等。",
        'cf = ax.contourf(X, Y, Z, levels=12,\n'
        '                 cmap=WXL_CMAPS["sequential"])\n'
        'cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.03)')
def fig_contour():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.linspace(-3, 3, 160)
    y = np.linspace(-3, 3, 160)
    X, Y = np.meshgrid(x, y)
    Z = np.exp(-(X ** 2 + Y ** 2) / 2) + 0.6 * np.exp(-((X - 1.2) ** 2 + (Y + 1.0) ** 2))
    cf = ax.contourf(X, Y, Z, levels=12, cmap=WXL_CMAPS["sequential"])
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    cb = fig.colorbar(cf, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Normalised intensity")
    cb.ax.tick_params(direction="in", width=0.8)
    cb.outline.set_linewidth(0.5)
    add_caption_below(fig, r"$\mathbf{Fig.}$  17  Filled contour map of a two-dimensional field.")
    return fig


# --------------------------------------------------------------------------
# special family
# --------------------------------------------------------------------------
@figure("radar", "雷达图（极坐标）", "special",
        "多指标综合对比，极坐标例外地保留浅灰网格以便读数。只出单栏版。",
        'ax = fig.add_subplot(projection="polar")\n'
        'ax.plot(theta, values, "-", color=WXL_LINE_PALETTE[key], lw=1.2)\n'
        'paint_markers(ax, theta, values, WXL_LINE_PALETTE[key])',
        width="single")
def fig_radar():
    fig = plt.figure(figsize=WXL_FIGSIZE["double"])
    ax = fig.add_subplot(projection="polar")
    labels = ["Strength", "Ductility", "Durability", "Cost", "Workability"]
    n = len(labels)
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    theta = np.concatenate([theta, theta[:1]])
    handles = []
    for name, key, vals in [("Mix A", "primary", [0.85, 0.72, 0.90, 0.55, 0.80]),
                            ("Mix B", "contrast", [0.70, 0.88, 0.65, 0.78, 0.60])]:
        v = np.concatenate([vals, vals[:1]])
        ax.plot(theta, v, "-", color=PL[key], lw=1.2, zorder=2)
        ax.fill(theta, v, color=P[key], alpha=0.12)
        paint_markers(ax, theta, v, PL[key])
        handles.append(marker_handle(PL[key], name))
    ax.set_xticks(theta[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"])
    ax.grid(True, color=PL["neutral"], alpha=0.35, linewidth=0.5)
    ax.tick_params(direction="in")
    framed_legend(ax, handles=handles, loc="lower right", bbox_to_anchor=(1.16, -0.08))
    add_caption_below(fig, r"$\mathbf{Fig.}$  18  Radar chart of five performance indices.")
    return fig


@figure("donut", "环形图 / 饼图", "special",
        "占比展示，坐标轴关闭，图例带黑框置于图内空白处。",
        'ax.pie(vals, colors=[PALETTE[k] for k in keys], startangle=90,\n'
        '       wedgeprops=dict(width=0.42, edgecolor=WXL_INK, linewidth=0.5))\n'
        'ax.set_axis_off()', width="single")
def fig_donut():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["single"])
    keys = ["primary", "contrast", "improve", "accent"]
    labels = ["Cement", "Aggregate", "Water", "Admixture"]
    vals = [34, 41, 17, 8]
    wedges, _ = ax.pie(vals, colors=[P[k] for k in keys], startangle=90,
                       counterclock=False,
                       wedgeprops=dict(width=0.42, edgecolor=WXL_INK, linewidth=0.5))
    ax.set_axis_off()
    framed_legend(ax, handles=[Patch(facecolor=P[k], edgecolor=WXL_INK,
                                     linewidth=0.5, label=f"{l} ({v}%)")
                               for k, l, v in zip(keys, labels, vals)],
                  loc="center left", bbox_to_anchor=(0.92, 0.5))
    add_caption_below(fig, r"$\mathbf{Fig.}$  19  Donut chart of mixture proportions.")
    return fig


@figure("dual_axis", "双纵轴图", "special",
        "两个量纲不同的变量共用横轴，右轴用强调色区分。",
        'ax2 = ax.twinx()\n'
        'ax.bar(x, a, color=PALETTE["light"], edgecolor=WXL_INK)\n'
        'ax2.plot(x, b, "-o", color=PALETTE["contrast"], lw=1.5)')
def fig_dual_axis():
    fig, (ax,) = create_subplots(figsize=WXL_FIGSIZE["double"])
    x = np.arange(6)
    load = np.array([12, 26, 41, 55, 68, 74], float)
    temp = np.array([22, 35, 52, 68, 79, 84], float)
    ax.bar(x, load, 0.5, color=P["light"], edgecolor=WXL_INK, linewidth=0.5,
           label="Load")
    ax.set_ylabel("Load (kN)")
    ax.set_xticks(x)
    ax.set_xticklabels(["0", "2", "4", "6", "8", "10"])
    ax.set_xlabel("Time (h)")
    ax.set_ylim(0, 95)
    ax2 = ax.twinx()
    ax2.plot(x, temp, "-", color=PL["contrast"], lw=1.2, zorder=2)
    paint_markers(ax2, x, temp, PL["contrast"])
    ax2.set_ylabel("Temperature (C)")
    ax2.set_ylim(0, 110)
    for side in ("top", "bottom", "left", "right"):
        ax2.spines[side].set_visible(True)
        ax2.spines[side].set_linewidth(0.5)
    ax2.tick_params(direction="in", width=0.8)
    ax2.grid(False)
    h1, l1 = ax.get_legend_handles_labels()
    framed_legend(ax, handles=h1 + [marker_handle(PL["contrast"], "Temperature")],
                  labels=l1 + ["Temperature"], loc="upper left")
    add_caption_below(fig, r"$\mathbf{Fig.}$  20  Dual-axis chart with bars and a line series.")
    return fig


@figure("multi_panel", "多子图（2x2 混合排版）", "special",
        "四种图型拼版，网格在画布中水平竖直居中，每个子图下方居中放编号加标题。"
        "热图不放进拼版，单独作为图型 15 展示。",
        'fig, axes = create_subplots(2, 2, figsize=WXL_FIGSIZE["double_tall"])\n'
        'panel_tag(axes[0], "(a)", "Grouped bars")\n'
        'center_grid(fig)          # centre the grid horizontally and vertically\n'
        'add_caption_below(fig, r"$\mathbf{Fig.}$  21  Multi-panel figure.")', width="double_tall")
def fig_multi_panel():
    fig, axes = create_subplots(2, 2, figsize=WXL_FIGSIZE["double_tall"])
    fig._wxl_no_tight = True      # keep the manual centering
    fig._wxl_center = True        # centre the grid at every layout pass
    # every panel's black frame matches a single-column figure (75 x 55 mm);
    # wspace/hspace and the caption gap are left unchanged
    fig._wxl_panel_axes_mm = WXL_AXES_PANEL_MM
    # row/column gap tuned so the top-row panel labels sit ~14 pt above the
    # bottom-row panels, matching the caption gap (add_caption_below, 14 pt)
    fig.subplots_adjust(hspace=0.28, wspace=0.30)

    ax = axes[0]
    cats = ["A", "B", "C"]
    for i, (name, key, vals) in enumerate([("S1", "primary", [0.7, 0.8, 0.9]),
                                           ("S2", "contrast", [0.5, 0.6, 0.7])]):
        ax.bar(np.arange(3) + (i - 0.5) * 0.3, vals, 0.3, label=name,
               color=P[key], edgecolor=WXL_INK, linewidth=0.5)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(cats)
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.1)
    framed_legend(ax, loc="upper left")
    panel_tag(ax, "(a)", "Grouped bars")

    ax = axes[1]
    x = np.linspace(0, 10, 11)
    handles = [plot_series(ax, x, 0.5 + 0.03 * x, PL["primary"], label="Curve 1",
                           marker="o"),
               plot_series(ax, x, 0.45 + 0.02 * x, PL["improve"], label="Curve 2",
                           marker="s")]
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    framed_legend(ax, handles=handles, loc="upper left")
    panel_tag(ax, "(b)", "Trend lines")

    ax = axes[2]
    data = [RNG.normal(m, 1.0, 50) for m in (0, 1, 2)]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                    medianprops=dict(color=WXL_INK, linewidth=1.2),
                    whiskerprops=dict(color=WXL_INK, linewidth=0.5),
                    capprops=dict(color=WXL_INK, linewidth=0.5),
                    boxprops=dict(edgecolor=WXL_INK, linewidth=0.5))
    for patch, key in zip(bp["boxes"], ["primary", "contrast", "improve"]):
        patch.set_facecolor(P[key])
    ax.set_xticklabels(["G1", "G2", "G3"])
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    panel_tag(ax, "(c)", "Box plots")

    ax = axes[3]
    for name, key, slope, noise in [("Set 1", "primary", 1.0, 0.7),
                                    ("Set 2", "accent", 0.85, 0.9)]:
        xs = RNG.uniform(2, 9, 40)
        ys = slope * xs + RNG.normal(0, noise, xs.size)
        ax.scatter(xs, ys, s=14, color=PL[key], edgecolor=WXL_INK, linewidth=0.4,
                   alpha=0.85, label=name)
    ax.set_xlabel("Measured")
    ax.set_ylabel("Predicted")
    framed_legend(ax, loc="upper left")
    panel_tag(ax, "(d)", "Scatter")

    add_caption_below(fig, r"$\mathbf{Fig.}$  21  Multi-panel figure with four chart types.")
    return fig


@figure("multi_panel_1x3", "多子图（1x3 一行三图）", "special",
        "三种图型并排一行，网格居中，每个子图下方居中放编号加标题；只出两栏版。",
        'fig, axes = create_subplots(1, 3, figsize=WXL_FIGSIZE["double"])\n'
        'panel_tag(axes[0], "(a)", "Grouped bars")\n'
        'center_grid(fig)\n'
        'add_caption_below(fig, r"$\\mathbf{Fig.}$  22  One-row three-panel figure.")',
        width="double_1x3")
def fig_multi_panel_1x3():
    fig, axes = create_subplots(1, 3, figsize=WXL_FIGSIZE["double_1x3"])
    fig._wxl_no_tight = True      # keep the manual centering
    fig._wxl_center = True        # centre the grid at every layout pass
    fig.subplots_adjust(wspace=0.25)

    ax = axes[0]
    cats = ["A", "B", "C"]
    for i, (name, key, vals) in enumerate([("S1", "primary", [0.7, 0.8, 0.9]),
                                           ("S2", "contrast", [0.5, 0.6, 0.7])]):
        ax.bar(np.arange(3) + (i - 0.5) * 0.3, vals, 0.3, label=name,
               color=P[key], edgecolor=WXL_INK, linewidth=0.5)
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(cats)
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.35)
    framed_legend(ax, loc="upper left", ncol=2, columnspacing=0.8, handlelength=1.2)
    panel_tag(ax, "(a)", "Grouped bars")

    ax = axes[1]
    x = np.linspace(0, 10, 11)
    handles = [plot_series(ax, x, 0.5 + 0.03 * x, PL["primary"], label="Curve 1",
                           marker="o"),
               plot_series(ax, x, 0.45 + 0.02 * x, PL["improve"], label="Curve 2",
                           marker="s")]
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_ylim(0.35, 0.95)
    framed_legend(ax, handles=handles, loc="upper left", ncol=2, columnspacing=0.8,
                  handlelength=1.2)
    panel_tag(ax, "(b)", "Trend lines")

    ax = axes[2]
    data = [RNG.normal(m, 1.0, 50) for m in (0, 1, 2)]
    bp = ax.boxplot(data, patch_artist=True, widths=0.55,
                    medianprops=dict(color=WXL_INK, linewidth=1.2),
                    whiskerprops=dict(color=WXL_INK, linewidth=0.5),
                    capprops=dict(color=WXL_INK, linewidth=0.5),
                    boxprops=dict(edgecolor=WXL_INK, linewidth=0.5))
    for patch, key in zip(bp["boxes"], ["primary", "contrast", "improve"]):
        patch.set_facecolor(P[key])
    ax.set_xticklabels(["G1", "G2", "G3"])
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    panel_tag(ax, "(c)", "Box plots")

    add_caption_below(fig, r"$\mathbf{Fig.}$  22  One-row three-panel figure.")
    return fig


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
HTML_HEAD = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>figure-making-WXL · 全部图型预览</title>
<style>
  :root{--ink:#111;--line:#111;--muted:#6b6b6b;--bg:#f5f5f3;}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font-size:14px;line-height:1.55;
       font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif}
  header{padding:22px 26px 16px;background:#fff;border-bottom:1px solid #ddd}
  h1{margin:0 0 6px;font-family:"Times New Roman",serif;font-size:24px}
  .sub{margin:0;color:var(--muted);font-size:13px}
  main{padding:18px 26px 70px;max-width:1280px;margin:0 auto}
  h2{font-family:"Times New Roman",serif;font-size:17px;margin:26px 0 10px;
     padding-bottom:6px;border-bottom:1px solid #ddd}
  .contract{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px}
  .cbox{border:1px solid var(--line);background:#fff;padding:8px 10px;font-size:12.5px}
  .cbox b{display:block;font-family:"Times New Roman",serif;font-size:13px;margin-bottom:2px}
  .swatches{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;margin-top:8px}
  .sw{border:1px solid var(--line);background:#fff}
  .sw .chip{height:44px}
  .sw .meta{padding:5px 7px;font-size:11.5px;font-family:"Times New Roman",serif}
  .filters{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 16px}
  .fbtn{cursor:pointer;border:1px solid var(--line);background:#fff;padding:6px 13px;
        font:inherit;border-radius:2px}
  .fbtn[aria-selected="true"]{background:#111;color:#fff}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  @media (max-width:1000px){.grid{grid-template-columns:1fr}}
  .card{border:1px solid var(--line);background:#fff;display:flex;flex-direction:column}
  .card .head{display:flex;justify-content:space-between;align-items:baseline;
              gap:10px;padding:9px 12px 6px;border-bottom:1px solid #e6e6e6}
  .card .head h3{margin:0;font-family:"Times New Roman",serif;font-size:15px}
  .card .cat{font-size:11.5px;color:#fff;background:#9E95BA;padding:1px 7px;border-radius:2px}
  .card img{width:100%;height:auto;display:block;background:#fff;cursor:zoom-in;
            border-bottom:1px solid #e6e6e6}
  .card .body{padding:9px 12px 12px;font-size:12.5px;color:#333}
  .card pre{margin:8px 0 0;background:#fafafa;border:1px solid #e6e6e6;padding:8px 10px;
            font-family:Consolas,"Courier New",monospace;font-size:11.5px;
            white-space:pre-wrap;overflow-x:auto}
  .badge{font-size:11px;padding:1px 7px;border-radius:2px;font-family:"Times New Roman",serif}
  .badge.pass{background:#E4F2E9;color:#1d6b3f;border:1px solid #9dcdb1}
  .badge.fail{background:#FBE6E4;color:#8d2b23;border:1px solid #e2aaa3}
  .issues{margin:6px 0 0;padding-left:18px;color:#8d2b23;font-size:11.5px}
  .lb{position:fixed;inset:0;background:rgba(0,0,0,.86);display:none;align-items:center;
      justify-content:center;padding:24px;z-index:50}
  .lb img{max-width:96vw;max-height:92vh;background:#fff}
  .lb.on{display:flex}
  footer{color:var(--muted);font-size:12px;margin-top:28px}
</style>
</head>
<body>
<header>
  <h1>figure-making-WXL · 全部图型预览</h1>
  <p class="sub">统一 11 pt · Times New Roman · 柔和科研配色 · 四边全包围 · 图例带黑框 · 刻度朝内 · 无网格</p>
</header>
<main>
<section>
  <h2>样式契约</h2>
  <div class="contract">
    <div class="cbox"><b>字号</b>统一 11 pt（图题 / 轴标题 / 刻度 / 图例 / 标注）</div>
    <div class="cbox"><b>与 Word 对齐</b>图幅 = 最终印刷宽度，按原始大小插入即等于正文 11 pt</div>
    <div class="cbox"><b>字体</b>Times New Roman + STIX 数学，中文宋体回退</div>
    <div class="cbox"><b>图幅</b>单栏 90 mm / 1.5 栏 140 mm / 双栏 190 mm</div>
    <div class="cbox"><b>轴与图例</b>四边全包围，线宽 0.8；图例框内、白底、黑边 0.8</div>
    <div class="cbox"><b>刻度与网格</b>朝内，无网格（极坐标例外，保留浅灰网格）</div>
    <div class="cbox"><b>图题</b>整图下方居中，禁止顶部标题</div>
    <div class="cbox"><b>导出</b>PNG 600 dpi + PDF 矢量（本页用 300 dpi 预览）</div>
    <div class="cbox"><b>图宽校准</b>tight 裁切会缩窄画布，已按目标栏宽迭代校准</div>
  </div>
</section>
<section>
  <h2>主色板</h2>
  <div class="swatches">__SWATCHES__</div>
</section>
<section>
  <h2>图型（__COUNT__ 种）</h2>
  <div class="filters" id="filters"></div>
  <div class="grid" id="grid">__CARDS__</div>
</section>
<footer>生成脚本 examples/gallery.py · 每张图都跑过 check_wxl_style 自检</footer>
</main>
<div class="lb" id="lb"><img id="lbimg" alt=""></div>
<script>
const cats = __CATS__;
function renderFilters(){
  const box = document.getElementById("filters");
  box.innerHTML = ['<button class="fbtn" data-cat="all" aria-selected="true">全部</button>']
    .concat(Object.keys(cats).map(k =>
      `<button class="fbtn" data-cat="${k}" aria-selected="false">${cats[k]}</button>`)).join("");
  box.querySelectorAll(".fbtn").forEach(b => b.addEventListener("click", () => {
    box.querySelectorAll(".fbtn").forEach(x => x.setAttribute("aria-selected", "false"));
    b.setAttribute("aria-selected", "true");
    const c = b.dataset.cat;
    document.querySelectorAll("#grid .card").forEach(card => {
      card.style.display = (c === "all" || card.dataset.cat === c) ? "" : "none";
    });
  }));
}
function renderLightbox(){
  const lb = document.getElementById("lb"), img = document.getElementById("lbimg");
  document.querySelectorAll("#grid img").forEach(im => im.addEventListener("click", () => {
    img.src = im.src; lb.classList.add("on");
  }));
  lb.addEventListener("click", () => lb.classList.remove("on"));
  document.addEventListener("keydown", e => { if (e.key === "Escape") lb.classList.remove("on"); });
}
renderFilters(); renderLightbox();
</script>
</body>
</html>
"""

CATEGORY_NAMES = {"bar": "柱状 / 条形", "line": "折线 / 面积", "rel": "关系",
                  "dist": "分布", "matrix": "矩阵 / 场", "special": "特殊"}


def build(outdir: Path):
    apply_wxl_style()
    figs_dir = outdir / "figs"
    figs_dir.mkdir(parents=True, exist_ok=True)
    records = []
    #: charts that keep their full composite layout in the gallery; every other
    #: chart is shown as a single-column figure, so all the displayed images are
    #: the same compact size
    COMPOSITE = {"multi_panel", "multi_panel_1x3"}
    for spec in FIGS:
        apply_wxl_style()
        fig = spec["fn"]()
        if spec["id"] in COMPOSITE:
            base = WXL_FIGSIZE[spec["width"]]
            target = WXL_WIDTH_MM[spec["width"]]
        else:
            base = WXL_FIGSIZE["single"]
            target = WXL_WIDTH_MM["single"]
        fig.set_size_inches(*base)
        prepare_figure(fig)
        report = check_wxl_style(fig)
        paths = finalize_figure(fig, figs_dir / spec["id"],
                                formats=["png", "pdf"], dpi=300,
                                target_width_mm=target)
        width_mm = measure_width_mm(paths[0], 300)
        report["width_mm"] = round(width_mm, 2)
        report["target_mm"] = target
        report["preset"] = "double" if spec["id"] in COMPOSITE else "single"
        # a single-column figure shares one fixed black frame, so its width
        # follows the tick labels; only the composite layout is width-checked
        if (spec["id"] in COMPOSITE
                and abs(width_mm - report["target_mm"]) > 0.6):
            report["problems"].append(
                f"saved width {width_mm:.2f} mm misses target "
                f"{report['target_mm']:.0f} mm")
            report["ok"] = not report["problems"]
        records.append({**spec, "report": report, "png": paths[0].name})
        flag = "PASS" if report["ok"] else "FAIL"
        print(f"[{flag}] {spec['id']:<16} {width_mm:6.2f} mm "
              f"(target {report['target_mm']:.0f}) fonts={report['fonts']} "
              f"sizes={report['sizes']} problems={len(report['problems'])}")
        for pr in report["problems"]:
            print("        -", pr)

    swatches = "".join(
        f'<div class="sw"><div class="chip" style="background:{v}"></div>'
        f'<div class="meta">{k}<br>{v}</div></div>'
        for k, v in WXL_PALETTE.items())

    cards = []
    for rec in records:
        rep = rec["report"]
        badge = ('<span class="badge pass">check PASS</span>' if rep["ok"]
                 else '<span class="badge fail">check FAIL</span>')
        issues = ""
        if rep["problems"]:
            issues = '<ul class="issues">' + "".join(
                f"<li>{html.escape(p)}</li>" for p in rep["problems"]) + "</ul>"
        cards.append(
            f'<div class="card" data-cat="{rec["category"]}">'
            f'<div class="head"><h3>{html.escape(rec["title"])}</h3>'
            f'<span class="cat">{CATEGORY_NAMES[rec["category"]]}</span></div>'
            f'<img src="figs/{rec["png"]}" alt="{rec["id"]}" loading="lazy">'
            f'<div class="body"><div>{html.escape(rec["desc"])}</div>'
            f'<pre>{html.escape(rec["code"])}</pre>'
            f'<div style="margin-top:8px">{badge}'
            f'<span style="color:#6b6b6b;font-size:11.5px">'
            f' 字体 {", ".join(rep["fonts"])} · 字号 {rep["sizes"]} pt · '
            f'图宽 {rep["width_mm"]:.2f} mm（目标 {rep["target_mm"]:.0f}）· '
            f'坐标轴 {rep["n_axes"]} · 图例 {rep["n_legends"]}</span></div>'
            f'{issues}</div></div>')

    import json
    html_text = (HTML_HEAD
                 .replace("__SWATCHES__", swatches)
                 .replace("__CARDS__", "".join(cards))
                 .replace("__COUNT__", str(len(records)))
                 .replace("__CATS__", json.dumps(CATEGORY_NAMES, ensure_ascii=False)))
    index = outdir / "index.html"
    index.write_text(html_text, encoding="utf-8")
    n_fail = sum(1 for r in records if not r["report"]["ok"])
    print(f"\nfigures: {len(records)}  failed checks: {n_fail}")
    print("gallery:", index)
    return index, n_fail


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path.home() / "wxl_gallery"))
    args = ap.parse_args()
    _, fails = build(Path(args.out))
    raise SystemExit(1 if fails else 0)
