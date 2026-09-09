"""WXL publication figure style (v1.0).

House style for matplotlib figures meant for Elsevier / IEEE / Springer
submissions, tuned so that figure text keeps a fixed 11 pt size when the
figure is inserted at its original physical size.

Hard rules (see SKILL.md):
  * Times New Roman everywhere, STIX math glyphs, no sans-serif faces.
  * Uniform 11 pt text (caption / axis label / tick / legend / annotation).
  * Deep-blue palette only.
  * Full box on every Cartesian axes (all four spines).
  * Legend inside the axes, opaque white face, black 0.8 pt border.
  * Ticks point inward, no grid.
  * Figure caption below the figure via add_caption (never fig.suptitle).
  * Figure width equals the final print width (90 / 140 / 190 mm).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.transforms
import numpy as np
from matplotlib import text as mtext
from matplotlib.colors import to_hex
from matplotlib.font_manager import findfont

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

#: Deep-blue semantic palette (WXL house palette).
WXL_PALETTE = {
    "primary": "#1F4E79",    # proposed method / main series
    "secondary": "#4E86C6",  # secondary blue, supporting series
    "contrast": "#B64342",   # baseline / competing method
    "improve": "#2E8B7A",    # improvement / positive variant
    "accent": "#E0A030",     # emphasis, annotations, secondary axis
    "neutral": "#7B7B7B",    # reference lines, background categories
    "light": "#C9DCF0",      # light fill, uncertainty bands
}

#: Default diverging colour map for matrices and correlation heatmaps.
WXL_CMAP = "RdBu_r"

#: Sequential / signed colour maps that stay inside the house look.
WXL_CMAPS = {"diverging": "RdBu_r", "sequential": "Blues", "signed": "coolwarm"}

#: Colour cycle used when a helper is called without explicit colours.
WXL_SERIES = [
    WXL_PALETTE["primary"], WXL_PALETTE["contrast"], WXL_PALETTE["improve"],
    WXL_PALETTE["accent"], WXL_PALETTE["secondary"], WXL_PALETTE["neutral"],
]

#: 11 pt type scale for body text, with the legend restored to 10 pt.
WXL_FONTSIZE = {
    "caption": 11, "label": 11, "tick": 11,
    "legend": 10, "annot": 11, "panel": 11,
}

#: Figure width = final print width, so 11 pt stays 11 pt after insertion.
#: single = 90 mm, onehalf = 140 mm, double = 190 mm.
#: double is deliberately short (half the old height) so the wide column holds a
#: flat figure whose 11 pt text reads larger relative to the plot.
WXL_FIGSIZE = {
    "single": (3.54, 2.70),
    "onehalf": (5.51, 3.90),
    "double": (7.48, 2.60),
    "double_tall": (7.48, 6.80),
    "double_1x3": (7.48, 1.63),   # 1x3 one-row grid: panels keep the single-column aspect
    "slide": (10.0, 6.00),
}

#: Final printed width of each preset, in millimetres.
WXL_WIDTH_MM = {
    "single": 90.0,
    "onehalf": 140.0,
    "double": 190.0,
    "double_tall": 190.0,
    "double_1x3": 190.0,
    "slide": 254.0,
}

_FONT_STACK = ["Times New Roman", "Nimbus Roman No9 L", "Liberation Serif", "SimSun"]

#: Accepted font files, by lowercase filename prefix. Times New Roman is
#: mandatory in name, but the metric-compatible serif fallbacks are accepted so
#: the skill works on machines that do not ship the Microsoft font
#: (Nimbus Roman No9 L and Liberation Serif are metric-compatible with Times).
_ALLOWED_FONT_PREFIXES = (
    "times",            # times.ttf, timesbd.ttf, "Times New Roman.ttf"
    "simsun",           # simsun.ttc (Windows CJK)
    "nimbusroman",      # NimbusRoman-Regular.otf (Linux)
    "liberationserif",  # LiberationSerif-Regular.ttf (Linux)
    "notoserifcjk",     # NotoSerifCJK*.ttc (Linux CJK)
    "songti", "stsong",  # macOS / Linux CJK serif
)

#: Backwards-compatible explicit set (Windows install).
_ALLOWED_FONT_FILES = {
    "times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf",
    "simsun.ttc", "simsunb.ttf",
}


def _font_is_allowed(filename: str) -> bool:
    name = filename.lower().replace(" ", "")
    return any(name.startswith(p) for p in _ALLOWED_FONT_PREFIXES)


@dataclass(frozen=True)
class WXLStyle:
    """Quantitative style contract. Every field is checked by check_wxl_style."""

    font_size: float = 11.0        # base text size (pt)
    caption_size: float = 11.0
    tick_size: float = 11.0
    legend_size: float = 10.0
    annot_size: float = 11.0
    axes_linewidth: float = 0.8
    line_width: float = 1.5
    marker_size: float = 4.0
    bar_edge_width: float = 0.8
    error_linewidth: float = 0.8
    capsize: float = 2.0
    figsize: tuple = WXL_FIGSIZE["double"]
    dpi: int = 600
    full_box: bool = True          # all four spines on every Cartesian axes
    legend_framed: bool = True     # legend inside axes, black 0.8 pt border
    ticks_in: bool = True
    grid: bool = False


DEFAULT_STYLE = WXLStyle()


# --------------------------------------------------------------------------
# Style application
# --------------------------------------------------------------------------

def apply_wxl_style(style: WXLStyle | None = None) -> WXLStyle:
    """Install the WXL rcParams. Call once before creating any figure."""
    st = style or DEFAULT_STYLE
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": _FONT_STACK,
        "mathtext.fontset": "stix",
        "axes.unicode_minus": False,
        "font.size": st.font_size,
        "axes.labelsize": st.font_size,
        "axes.titlesize": st.font_size,
        "xtick.labelsize": st.tick_size,
        "ytick.labelsize": st.tick_size,
        "legend.fontsize": st.legend_size,
        "axes.linewidth": st.axes_linewidth,
        "axes.spines.top": st.full_box,
        "axes.spines.right": st.full_box,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.grid": st.grid,
        "xtick.direction": "in" if st.ticks_in else "out",
        "ytick.direction": "in" if st.ticks_in else "out",
        "xtick.major.width": st.axes_linewidth,
        "ytick.major.width": st.axes_linewidth,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "lines.linewidth": st.line_width,
        "lines.markersize": st.marker_size,
        "errorbar.capsize": st.capsize,
        "patch.linewidth": st.bar_edge_width,
        "legend.frameon": st.legend_framed,
        "legend.edgecolor": "black",
        "legend.framealpha": 1.0,
        "legend.fancybox": False,
        "figure.dpi": 110,
        "savefig.dpi": st.dpi,
        "savefig.bbox": "tight",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,        # embed TrueType, editable text in vector PDF
        "ps.fonttype": 42,
    })
    return st


# --------------------------------------------------------------------------
# Layout helpers
# --------------------------------------------------------------------------

def create_subplots(nrows: int = 1, ncols: int = 1, figsize=None, **kwargs):
    """Return ``(fig, axes)`` with ``axes`` a flat 1-D numpy array of Axes."""
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
    return fig, np.atleast_1d(axes).ravel()


def framed_legend(ax, **kwargs):
    """Legend inside the axes with an opaque white face and black 0.8 pt border.

    The position is refined later by :func:`place_all_legends`, which measures
    the real overlap between the legend box and the plotted data.
    """
    kwargs.setdefault("loc", "best")
    leg = ax.legend(frameon=True, **kwargs)
    leg.get_frame().set_edgecolor("black")
    leg.get_frame().set_linewidth(0.8)
    leg.get_frame().set_alpha(1.0)
    return leg


#: Legend positions tried by :func:`place_legend_smart`, cheapest first.
_LEGEND_CANDIDATES = [
    "best", "upper right", "upper left", "lower left", "lower right",
    "upper center", "lower center", "center left", "center right",
]


def _legend_overlap_score(ax, bbox) -> float:
    """Average share of the plotted artists hidden by a legend box, in [0, 1].

    Each line and scatter series contributes the fraction of its points inside
    the box, each bar or box patch the overlapped area fraction; the result is
    the mean over all contributing artists. 0.0 means the legend sits on empty
    canvas.
    """
    if bbox is None:
        return 0.0
    parts: list[float] = []
    for line in ax.get_lines():
        if not line.get_visible():
            continue
        xy = line.get_xydata()
        if xy is None or len(xy) < 2:
            continue
        xy = np.asarray(xy, float)
        step = max(1, len(xy) // 400)
        disp = ax.transData.transform(xy[::step])
        inside = ((disp[:, 0] >= bbox.x0) & (disp[:, 0] <= bbox.x1) &
                  (disp[:, 1] >= bbox.y0) & (disp[:, 1] <= bbox.y1))
        parts.append(float(inside.mean()))
    for patch in ax.patches:
        if not patch.get_visible():
            continue
        pb = patch.get_window_extent()
        if pb.width * pb.height <= 0:
            continue
        inter = matplotlib.transforms.Bbox.intersection(pb, bbox)
        if inter is not None:
            parts.append((inter.width * inter.height) / (pb.width * pb.height))
    for coll in ax.collections:
        if not coll.get_visible():
            continue
        get_paths = getattr(coll, "get_paths", None)
        if get_paths is not None:
            # PolyCollection (stackplot / fill_between / contourf) and
            # ContourSet: sample the filled polygon vertices
            pts = []
            try:
                for path in get_paths():
                    verts = getattr(path, "vertices", None)
                    if verts is not None and len(verts):
                        pts.append(verts[:, :2])
            except Exception:                                  # pragma: no cover
                pass
            if pts:
                verts = np.vstack(pts)
                step = max(1, len(verts) // 600)
                disp = ax.transData.transform(verts[::step])
                inside = ((disp[:, 0] >= bbox.x0) & (disp[:, 0] <= bbox.x1) &
                          (disp[:, 1] >= bbox.y0) & (disp[:, 1] <= bbox.y1))
                parts.append(float(inside.mean()))
            continue
        get_offsets = getattr(coll, "get_offsets", None)
        if get_offsets is None:
            continue
        try:
            offs = np.asarray(get_offsets(), float)
        except Exception:                                  # pragma: no cover
            continue
        if offs.ndim != 2 or offs.shape[0] == 0 or offs.shape[1] < 2:
            continue
        disp = ax.transData.transform(offs[:, :2])
        inside = ((disp[:, 0] >= bbox.x0) & (disp[:, 0] <= bbox.x1) &
                  (disp[:, 1] >= bbox.y0) & (disp[:, 1] <= bbox.y1))
        parts.append(float(inside.mean()))
    return float(np.mean(parts)) if parts else 0.0


def place_legend_smart(ax, leg=None, candidates=None, fig=None):
    """Move an existing legend to the candidate position that hides least data.

    Returns ``(score, loc)`` for the chosen position.
    """
    leg = leg if leg is not None else ax.get_legend()
    if leg is None:
        return None
    fig = fig if fig is not None else ax.get_figure()
    candidates = candidates or _LEGEND_CANDIDATES
    best = None
    for loc in candidates:
        leg.set_loc(loc)
        fig.canvas.draw()
        score = _legend_overlap_score(ax, leg.get_window_extent())
        if best is None or score < best[0] - 1e-9:
            best = (score, loc)
        if score <= 1e-9:
            break
    leg.set_loc(best[1])
    fig.canvas.draw()
    return best


def _data_y_range(ax):
    """Data extent of the axes in y, from lines and bar/box patches."""
    lo, hi = np.inf, -np.inf
    for line in ax.get_lines():
        yd = np.asarray(line.get_ydata(), float)
        yd = yd[np.isfinite(yd)]
        if yd.size:
            lo, hi = min(lo, float(yd.min())), max(hi, float(yd.max()))
    for patch in ax.patches:
        try:
            lo = min(lo, float(patch.get_y()))
            hi = max(hi, float(patch.get_y()) + float(patch.get_height()))
        except Exception:                                  # pragma: no cover
            pass
    return lo, hi


def _expand_axis_for_legend(ax, leg, cap: float = 0.35):
    """Grow the y-range on the side where the legend sits, to make room.

    Expansion is capped at ``cap`` of the data span on each side, so a bar chart
    can never end up as mostly empty canvas just to host a legend. Returns True
    when the limits actually changed.
    """
    bbox = leg.get_window_extent()
    ab = ax.get_window_extent()
    if ab.height <= 0:
        return False
    rel = ((bbox.y0 + bbox.y1) / 2 - ab.y0) / ab.height
    lo, hi = (float(v) for v in ax.get_ylim())
    span = hi - lo
    if span <= 0:
        return False
    dlo, dhi = _data_y_range(ax)
    if not (np.isfinite(dlo) and np.isfinite(dhi)):
        return False
    dspan = (dhi - dlo) or span
    limit_lo = dlo - cap * dspan
    limit_hi = dhi + cap * dspan
    if rel >= 0.5:
        new_hi = min(hi + 0.35 * span, limit_hi)
        if new_hi <= hi + 1e-9:
            return False
        ax.set_ylim(lo, new_hi)
    else:
        new_lo = max(lo - 0.35 * span, limit_lo)
        if new_lo >= lo - 1e-9:
            return False
        ax.set_ylim(new_lo, hi)
    return True


def _legend_right_panel(fig, ax, leg):
    """Move a legend that cannot fit inside the axes into a dedicated axes on the
    right, so it never covers the data. Returns the new legend."""
    handles, labels = ax.get_legend_handles_labels()
    if leg is not None:
        try:
            leg.remove()
        except Exception:                                  # pragma: no cover
            pass
    pos = ax.get_position()
    leg_w = 0.30 * pos.width
    data_w = pos.width - leg_w - 0.02 * pos.width
    ax.set_position([pos.x0, pos.y0, data_w, pos.height])
    leg_ax = fig.add_axes([pos.x0 + data_w + 0.02 * pos.width, pos.y0,
                           leg_w, pos.height])
    leg_ax.set_axis_off()
    leg_ax.set_facecolor("none")
    new_leg = leg_ax.legend(handles, labels, loc="center", frameon=True,
                            fontsize=WXL_FONTSIZE["legend"], ncol=1,
                            handlelength=1.6, handletextpad=0.6,
                            borderaxespad=0.0)
    new_leg.get_frame().set_edgecolor("black")
    new_leg.get_frame().set_linewidth(0.8)
    new_leg.get_frame().set_alpha(1.0)
    # tight_layout would reset the manual positions and hide the panel again
    fig._wxl_no_tight = True
    return new_leg


def place_all_legends(fig, rounds: int = 2, candidates=None,
                      panel_threshold: float = 0.01):
    """Refine every in-axes legend so it covers as little data as possible.

    Tries the candidate positions, grows the y-range and retries, then flattens a
    legend with three or more entries into two columns. If a legend still covers
    more than ``panel_threshold`` of the data, it is moved into a dedicated axes
    on the right (``_legend_right_panel``) so it never covers the plot. Polar
    axes, colorbar axes and axes with ``axison == False`` keep their hand-placed
    legend. Returns ``[(axes, (score, loc)), ...]``.
    """
    out = []
    for ax in fig.get_axes():
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar"):
            continue
        leg = ax.get_legend()
        if leg is None:
            continue
        res = place_legend_smart(ax, leg, candidates, fig)
        tries = 0
        while res is not None and res[0] > 1e-9 and tries < rounds:
            if not _expand_axis_for_legend(ax, leg):
                break
            lock_axis_ends(ax)
            res = place_legend_smart(ax, leg, candidates, fig)
            tries += 1
        # flatten a long legend into two columns when that hides less data
        if res is not None and res[0] > 1e-9 and len(leg.get_texts()) >= 3:
            set_ncols = getattr(leg, "set_ncols", None)
            if set_ncols is not None:
                set_ncols(2)
                flat = place_legend_smart(ax, leg, candidates, fig)
                if flat is not None and flat[0] < res[0]:
                    res = flat
                elif flat is not None:
                    set_ncols(1)
                    place_legend_smart(ax, leg, candidates, fig)
        if res is not None and res[0] > panel_threshold:
            _legend_right_panel(fig, ax, leg)
            res = (0.0, "panel")
        out.append((ax, res))
    return out


#: Display offsets, in points, tried for a colliding annotation.
_ANNOT_OFFSETS = [(0, 5), (0, -13), (7, 5), (-7, 5), (7, -13), (-7, -13),
                  (0, 16), (0, -24)]


def _bbox_area(box) -> float:
    return max(box.width * box.height, 1e-9)


def _text_collision_count(ax, box, others, min_share: float = 0.02) -> float:
    """How many artists a text box touches: lines (point inside), patches and
    other text boxes (area share above ``min_share``)."""
    hits = 0.0
    for line in ax.get_lines():
        if not line.get_visible():
            continue
        xy = line.get_xydata()
        if xy is None or len(xy) < 2:
            continue
        disp = ax.transData.transform(np.asarray(xy, float))
        inside = ((disp[:, 0] >= box.x0) & (disp[:, 0] <= box.x1) &
                  (disp[:, 1] >= box.y0) & (disp[:, 1] <= box.y1))
        if inside.any():
            hits += 1.0
    area = _bbox_area(box)
    for patch in ax.patches:
        if not patch.get_visible():
            continue
        inter = matplotlib.transforms.Bbox.intersection(
            patch.get_window_extent(), box)
        if inter is not None and (inter.width * inter.height) / area > min_share:
            hits += 1.0
    for other in others:
        inter = matplotlib.transforms.Bbox.intersection(other, box)
        if inter is not None and (inter.width * inter.height) / area > min_share:
            hits += 1.0
    return hits


def _data_annotation_texts(ax):
    """Plain ``ax.text`` annotations, excluding panel tags and axis labels."""
    out = []
    for t in ax.texts:
        if not isinstance(t, mtext.Text) or isinstance(t, mtext.Annotation):
            continue
        if not t.get_text().strip():
            continue
        if t.get_transform() is not ax.transData:
            continue                       # panel tags / axes-coordinate text
        out.append(t)
    return out


def _tick_labels_overlap(ax) -> bool:
    """True when two adjacent major tick labels share pixels."""
    for axis in (ax.xaxis, ax.yaxis):
        boxes = [t.get_window_extent() for t in axis.get_majorticklabels()
                 if t.get_text().strip()]
        for a, b in zip(boxes, boxes[1:]):
            if a.overlaps(b):
                return True
    return False


def fix_tick_label_overlap(fig, tries=(8, 6, 5, 4)):
    """Thin out ticks until no two adjacent tick labels touch.

    The 11 pt size is fixed, so the only lever is tick density. Returns a list of
    ``(axes, ticks_per_axis)`` for the axes that had to be thinned.
    """
    changed = []
    for ax in fig.get_axes():
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar") or ax.images:
            continue
        if not _tick_labels_overlap(ax):
            continue
        for n in tries:
            lock_axis_ends(ax, max_ticks=n)
            fig.canvas.draw()
            if not _tick_labels_overlap(ax):
                changed.append((ax, n))
                break
    return changed


def place_annotations(fig, rounds: int = 2):
    """Nudge data annotations off the data they cover.

    For every plain ``ax.text`` annotation that touches a line, a bar or another
    text box, the candidate offsets in ``_ANNOT_OFFSETS`` are tried and the one
    with the fewest collisions is kept. If every offset still collides, the
    y-range is grown (capped at 35 % of the data span) and the search repeats.
    Returns ``[(text, collisions)]`` for the annotations that still collide.
    """
    unresolved = []
    for ax in fig.get_axes():
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar"):
            continue
        texts = _data_annotation_texts(ax)
        if not texts:
            continue
        for text in texts:
            fig.canvas.draw()
            others = [t.get_window_extent() for t in texts if t is not text]
            box = text.get_window_extent()
            best = _text_collision_count(ax, box, others)
            if best <= 0:
                continue
            pos = text.get_position()
            disp = ax.transData.transform(pos)
            ppp = fig.dpi / 72.0
            for dx, dy in _ANNOT_OFFSETS:
                text.set_position(ax.transData.inverted().transform(
                    (disp[0] + dx * ppp, disp[1] + dy * ppp)))
                fig.canvas.draw()
                box = text.get_window_extent()
                score = _text_collision_count(ax, box, others)
                if score < best:
                    best = score
                    if score <= 0:
                        break
            if best > 0:
                for _ in range(rounds):
                    if not _expand_axis_for_text(ax, text):
                        break
                    lock_axis_ends(ax)
                    fig.canvas.draw()
                    box = text.get_window_extent()
                    if _text_collision_count(ax, box, others) <= 0:
                        best = 0.0
                        break
            if best > 0:
                unresolved.append((text, best))
    return unresolved


def _expand_axis_for_text(ax, text, cap: float = 0.35) -> bool:
    """Grow the y-range when a text box sticks out or still collides."""
    box = text.get_window_extent()
    ab = ax.get_window_extent()
    if ab.height <= 0:
        return False
    lo, hi = (float(v) for v in ax.get_ylim())
    span = hi - lo
    if span <= 0:
        return False
    dlo, dhi = _data_y_range(ax)
    if not (np.isfinite(dlo) and np.isfinite(dhi)):
        return False
    dspan = (dhi - dlo) or span
    if box.y1 > ab.y1 or box.y0 < ab.y0:
        need_up = box.y1 > ab.y1
    else:
        need_up = (box.y0 + box.y1) / 2 >= (ab.y0 + ab.y1) / 2
    if need_up:
        new_hi = min(hi + 0.25 * span, dhi + cap * dspan)
        if new_hi <= hi + 1e-9:
            return False
        ax.set_ylim(lo, new_hi)
    else:
        new_lo = max(lo - 0.25 * span, dlo - cap * dspan)
        if new_lo >= lo - 1e-9:
            return False
        ax.set_ylim(new_lo, hi)
    return True


def annotate_bars(ax, bars, fmt: str = "{:.2f}", fontsize: float | None = None,
                  y_offset_frac: float = 0.02, skip_if_wider: bool = True):
    """Label bars above their top edge, skipping labels that do not fit.

    A 11 pt value label is about 10 mm wide, so in a 90 mm panel with narrow
    grouped bars the labels would cover each other and the neighbouring bars.
    With ``skip_if_wider=True`` (the default) any label wider than its own bar is
    dropped, which makes the same figure code produce labelled bars at 190 mm and
    clean bars at 90 mm. Returns ``(kept, skipped)``.
    """
    fig = ax.get_figure()
    lo, hi = (float(v) for v in ax.get_ylim())
    pad = y_offset_frac * (hi - lo) if hi > lo else 0.0
    pairs = []
    for bar in bars:
        height = float(bar.get_height())
        text = ax.text(bar.get_x() + bar.get_width() / 2.0, height + pad,
                       fmt.format(height), ha="center", va="bottom",
                       fontsize=fontsize or WXL_FONTSIZE["annot"])
        # tag the label so _enforce_label_fit can re-check it at the final
        # canvas size, where the bars are narrower than when it was created
        text._wxl_bar = bar
        pairs.append((text, bar))
    kept, skipped = 0, 0
    if skip_if_wider and pairs:
        fig.canvas.draw()
        for text, bar in pairs:
            if text.get_window_extent().width > bar.get_window_extent().width:
                text.remove()
                skipped += 1
            else:
                kept += 1
    else:
        kept = len(pairs)
    return kept, skipped


def _enforce_label_fit(fig) -> int:
    """Drop tagged bar labels that no longer fit their bar at the current size.

    :func:`annotate_bars` tags every label it creates. A figure is often authored
    at 190 mm and later resized to 90 mm, where a 11 pt label is wider than the
    bar underneath; this pass removes those labels so they cannot cover the
    neighbouring bars. Returns the number of labels removed.
    """
    removed = 0
    texts = []
    for ax in fig.get_axes():
        for text in ax.texts:
            if getattr(text, "_wxl_bar", None) is not None:
                texts.append(text)
    if not texts:
        return 0
    fig.canvas.draw()
    for text in texts:
        bar = text._wxl_bar
        try:
            if text.get_window_extent().width > bar.get_window_extent().width:
                text.remove()
                removed += 1
        except Exception:                                  # pragma: no cover
            continue
    return removed


def prepare_figure(fig, lock_ends: bool = True, auto_legend: bool = True,
                   auto_text: bool = True, center=None, caption_max_mm=None):
    """Bring a figure to contract state.

    Locks axis ends, deconflicts legends, thins crowded tick labels and nudges
    colliding annotations. Set ``fig._wxl_center = True`` (or pass
    ``center=True``) to also center the axes grid horizontally and vertically.
    Call this before :func:`check_wxl_style` when you audit a figure yourself;
    :func:`finalize_figure` calls it automatically.
    """
    if lock_ends:
        lock_axis_ends_all(fig)
    if auto_legend:
        place_all_legends(fig)
    if auto_text:
        _enforce_label_fit(fig)
        fix_tick_label_overlap(fig)
        place_annotations(fig)
    if center is None:
        center = bool(getattr(fig, "_wxl_center", False))
    if center:
        center_grid(fig)
    # re-place a caption-below-the-grid at the current canvas size, so it stays
    # a fixed 14 pt under the grid even after the width calibration resized it
    caption = getattr(fig, "_wxl_caption", None)
    if caption is not None:
        _caption_below(fig, caption[0], caption[1], caption[2],
                       max_mm=caption_max_mm if caption_max_mm else caption[3])
    return fig


def add_caption(fig, text: str, fontsize: float | None = None, y: float = -0.045, **kwargs):
    """Figure caption centered BELOW the figure (hard rule: never on top)."""
    kwargs.setdefault("ha", "center")
    kwargs.setdefault("va", "top")
    return fig.text(0.5, y, text,
                    fontsize=fontsize or WXL_FONTSIZE["caption"], **kwargs)


#: how far the figure caption sits below the grid, in points
WXL_CAPTION_PAD_PT = 14.0


def _wrap_caption(fig, text, max_mm, fontsize):
    """Wrap the caption so no line is wider than ``max_mm`` millimetres."""
    if not max_mm:
        return text
    probe = fig.text(0.5, -1000, text, ha="center", va="top", fontsize=fontsize)
    fig.canvas.draw()
    full_mm = probe.get_window_extent().width / fig.dpi * 25.4
    probe.remove()
    if full_mm <= max_mm:
        return text
    import textwrap
    n_chars = max(8, int(len(text) * max_mm / full_mm))
    wrapped = text
    for _ in range(4):
        wrapped = "\n".join(textwrap.wrap(text, width=n_chars))
        probe = fig.text(0.5, -1000, wrapped, ha="center", va="top", fontsize=fontsize)
        fig.canvas.draw()
        w_mm = probe.get_window_extent().width / fig.dpi * 25.4
        probe.remove()
        if w_mm <= max_mm:
            break
        n_chars = max(8, int(n_chars * max_mm / max(w_mm, 1e-9)) - 1)
    return wrapped


def _caption_below(fig, text, pad_pt: float = WXL_CAPTION_PAD_PT,
                   fontsize: float | None = None, max_mm: float | None = None):
    """Place the caption ``pad_pt`` points below the grid's lowest label."""
    old = getattr(fig, "_wxl_caption_artist", None)
    if old is not None:
        try:
            old.remove()
        except Exception:                                 # pragma: no cover
            pass
    fs = fontsize or WXL_FONTSIZE["caption"]
    text = _wrap_caption(fig, text, max_mm, fs)
    fig.canvas.draw()
    boxes = [ax.get_tightbbox() for ax in fig.get_axes()
             if ax.get_visible() and ax.get_tightbbox() is not None]
    if not boxes:
        artist = fig.text(0.5, 0.01, text, ha="center", va="top", fontsize=fs)
    else:
        Hpx = fig.get_size_inches()[1] * fig.dpi
        y_bottom = min(b.y0 for b in boxes) / Hpx
        y = y_bottom - pad_pt * fig.dpi / 72.0 / Hpx
        artist = fig.text(0.5, y, text, ha="center", va="top", fontsize=fs)
    fig._wxl_caption_artist = artist
    return artist


def add_caption_below(fig, text: str, pad_pt: float = WXL_CAPTION_PAD_PT,
                      fontsize: float | None = None, max_mm: float | None = None):
    """Caption close below the grid, re-applied after grid centering.

    Records the caption on the figure so :func:`prepare_figure` re-places it
    after :func:`center_grid` moves the axes. Use this for a centered multi-panel
    figure where the default ``add_caption`` (placed below the canvas) would end
    up far from the grid. ``max_mm`` wraps the caption so no line exceeds the
    print width; ``finalize_figure`` passes its ``target_width_mm`` for this.
    """
    fig._wxl_caption = (text, pad_pt, fontsize, max_mm)
    return _caption_below(fig, text, pad_pt, fontsize, max_mm)


def _nice_axis(lo: float, hi: float, min_ticks: int = 4, max_ticks: int = 8):
    """Return ``(lo2, hi2, step)`` so that lo2/hi2 sit exactly on tick values."""
    span = hi - lo
    raw = span / max(max_ticks - 1, 1)
    mag = 10.0 ** np.floor(np.log10(raw)) if raw > 0 else 1.0
    best = None
    for m in (1, 2, 2.5, 5, 10, 20, 25, 50):
        step = m * mag
        lo2 = np.floor(lo / step) * step
        hi2 = np.ceil(hi / step) * step
        count = int(round((hi2 - lo2) / step)) + 1
        if count < min_ticks or count > max_ticks:
            continue
        pad = (lo - lo2) + (hi2 - hi)
        score = pad / span + 0.05 * abs(count - 6)
        if best is None or score < best[0]:
            best = (score, float(lo2), float(hi2), float(step))
    if best is None:
        step = raw if raw > 0 else 1.0
        return float(lo), float(hi), float(step)
    _, lo2, hi2, step = best
    # keep essentially non-negative data axes starting at zero
    if lo2 < 0 and lo > -0.05 * span:
        lo2 = 0.0
    if hi2 > 0 and hi < 0.05 * span and hi <= 0:
        hi2 = 0.0
    return lo2, hi2, step


def _axis_is_categorical(axis) -> bool:
    """True when an axis carries category names rather than plain numbers.

    A label counts as categorical when it is not numeric, or when its numeric
    value does not match the tick position (years 2021..2024 placed at 0..3, for
    example).
    """
    try:
        ticks = [float(t) for t in axis.get_majorticklocs()]
        labels = [t.get_text().strip() for t in axis.get_majorticklabels()]
    except Exception:                                      # pragma: no cover
        return False
    if not ticks or len(ticks) != len(labels):
        return False
    for t, s in zip(ticks, labels):
        if not s:
            continue
        try:
            v = float(s.replace("\u2212", "-").replace(",", ""))
        except ValueError:
            return True
        if abs(v - t) > 1e-6 * max(1.0, abs(t)):
            return True
    return False


def lock_axis_ends(ax, max_ticks: int = 8, min_ticks: int = 4) -> int:
    """Make both axis ends land exactly on the first and last tick label.

    Expands the current limits outward to the nearest tick grid, sets the ticks
    explicitly and uses a plain formatter (no offset, no scientific notation).
    Categorical axes (bar categories, box labels, specimen names) are left alone
    so their text labels survive. Returns the number of axes modified.
    """
    from matplotlib.ticker import FuncFormatter
    n = 0
    for name in ("x", "y"):
        scale = ax.get_xscale() if name == "x" else ax.get_yscale()
        if scale != "linear":
            continue
        get_lim = ax.get_xlim if name == "x" else ax.get_ylim
        set_lim = ax.set_xlim if name == "x" else ax.set_ylim
        set_ticks = ax.set_xticks if name == "x" else ax.set_yticks
        axis = ax.xaxis if name == "x" else ax.yaxis
        if _axis_is_categorical(axis):
            continue
        lo, hi = sorted(float(v) for v in get_lim())
        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
            continue
        lo2, hi2, step = _nice_axis(lo, hi, min_ticks, max_ticks)
        if hi2 <= lo2:
            continue
        ticks = np.arange(lo2, hi2 + step * 0.5, step)
        set_lim(lo2, hi2)
        set_ticks(ticks)
        decimals = max(0, int(np.ceil(-np.log10(step)))) if step < 1 else 0
        fmt = f"{{:.{decimals}f}}"
        axis.set_major_formatter(FuncFormatter(lambda v, _pos: fmt.format(v)))
        n += 1
    return n


def lock_axis_ends_all(fig, max_ticks: int = 8, min_ticks: int = 4) -> int:
    """Apply :func:`lock_axis_ends` to every numeric Cartesian axes of a figure.

    Image axes (``imshow`` heatmaps), polar axes, colorbar axes and axes with
    ``axison == False`` (pie/donut) are skipped: their ticks are categorical and
    already span the full extent.
    """
    n = 0
    for ax in fig.get_axes():
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar") or ax.images:
            continue
        n += lock_axis_ends(ax, max_ticks=max_ticks, min_ticks=min_ticks)
    return n


def panel_tag(ax, tag: str, title: str | None = None, pad_pt: float = 5.0,
              bold: bool = False):
    """Panel label below its own panel, centered on the panel.

    Pass a ``title`` to get ``(a) Grouped bars`` instead of a bare ``(a)``. The
    label sits ``pad_pt`` points below the lowest text already under the axes
    (x-label and tick labels included), so it stays close to the panel instead of
    drifting away with the axes height. Centered, and NOT bold by default.
    """
    text = f"{tag} {title}".strip() if title else tag
    fig = ax.get_figure()
    fig.canvas.draw()
    extra_pt = max(ax.get_window_extent().y0 - ax.get_tightbbox().y0, 0.0) \
        / fig.dpi * 72.0
    return ax.annotate(text, xy=(0.5, 0.0), xycoords="axes fraction",
                       xytext=(0, -(extra_pt + pad_pt)),
                       textcoords="offset points", ha="center", va="top",
                       fontsize=WXL_FONTSIZE["panel"],
                       fontweight="bold" if bold else "normal")


def center_grid(fig, pad_frac: float = 0.01, max_shift: float = 0.2):
    """Center the whole axes grid horizontally and vertically in the canvas.

    Shifts every axes by the same amount so the union of their tight bounding
    boxes (tick labels, axis labels and panel labels included) sits centered,
    with at least ``pad_frac`` of the canvas left on each side. Pair it with
    ``fig._wxl_no_tight = True`` so ``finalize_figure`` does not re-run
    tight_layout and undo the centering, and set ``fig._wxl_center = True`` so it
    runs again after every canvas resize. The shift is capped at ``max_shift`` of
    the canvas and skipped in a dimension whose content already exceeds the
    canvas, which keeps repeated calls from drifting.
    """
    fig.canvas.draw()
    boxes = [ax.get_tightbbox() for ax in fig.get_axes()
             if ax.get_visible() and ax.get_tightbbox() is not None]
    if not boxes:
        return False
    x0 = min(b.x0 for b in boxes)
    x1 = max(b.x1 for b in boxes)
    y0 = min(b.y0 for b in boxes)
    y1 = max(b.y1 for b in boxes)
    W = fig.get_size_inches()[0] * fig.dpi
    H = fig.get_size_inches()[1] * fig.dpi
    if W <= 0 or H <= 0:
        return False

    dx = 0.0
    if (x1 - x0) <= W:
        left, right = x0 / W, 1.0 - x1 / W
        # moving the grid right by dx turns (left, right) into
        # (left + dx, right - dx); equalising them needs dx = (right - left)/2
        dx = (right - left) / 2.0
        dx = min(max(dx, -max_shift), max_shift)
        lo, hi = pad_frac - left, right - pad_frac
        if lo <= hi:                      # only clamp when it is consistent
            dx = min(max(dx, lo), hi)
    dy = 0.0
    if (y1 - y0) <= H:
        bottom, top = y0 / H, 1.0 - y1 / H
        dy = (top - bottom) / 2.0
        dy = min(max(dy, -max_shift), max_shift)
        lo, hi = pad_frac - bottom, top - pad_frac
        if lo <= hi:
            dy = min(max(dy, lo), hi)
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return False
    for ax in fig.get_axes():
        pos = ax.get_position()
        ax.set_position([pos.x0 + dx, pos.y0 + dy, pos.width, pos.height])
    return True


def measure_width_mm(path, dpi: int | None = None) -> float:
    """Physical width of a saved raster file, in millimetres (px / dpi * 25.4)."""
    dpi = dpi or DEFAULT_STYLE.dpi
    path = Path(path)
    try:
        from PIL import Image
        with Image.open(path) as im:
            px = im.size[0]
    except Exception:                                  # pragma: no cover
        import matplotlib.image as mpimg
        px = mpimg.imread(str(path)).shape[1]
    return px / dpi * 25.4


def finalize_figure(fig, out_path, formats=None, dpi: int | None = None,
                    close: bool = True, pad: float = 0.06, layout: bool = True,
                    target_width_mm: float | None = None, tol_mm: float = 0.5,
                    lock_ends: bool = True, auto_legend: bool = True,
                    auto_text: bool = True):
    """Save the figure to one or more formats and return the list of paths.

    Saving always uses ``bbox_inches="tight"`` so a caption placed below the
    figure is captured instead of clipped.

    ``target_width_mm`` closes the trap that tight cropping opens: the tight
    bounding box trims the canvas margins, so a figure authored with
    ``figsize=(7.48, 5.20)`` (190 mm) often saves as ~158 mm wide. Inserting that
    image at its natural size keeps the text at 11 pt, but stretching it to fill
    a 190 mm column shrinks the text to ~8.3 pt. When ``target_width_mm`` is
    given, the canvas width is calibrated (two probe renders) so the trimmed
    image is exactly that wide, and the aspect ratio is preserved.
    """
    out_path = Path(out_path)
    formats = formats or [out_path.suffix.lstrip(".") or "pdf"]
    dpi = dpi or DEFAULT_STYLE.dpi
    stem = out_path.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)

    def _relayout():
        if layout and not getattr(fig, "_wxl_no_tight", False):
            try:
                with warnings.catch_warnings():
                    # a very short figure (the half-height double preset) can be
                    # too small for tight_layout; bbox_inches="tight" still keeps
                    # every decoration in the saved image
                    warnings.simplefilter("ignore", UserWarning)
                    fig.tight_layout(pad=1.0)
            except Exception:
                pass

    def _prepare():
        # Axis-end locking, legend placement, annotation nudging and grid
        # centering must run AFTER any canvas resize: resizing changes how much
        # of the axes a fixed 12 pt text box occupies.
        if lock_ends or auto_legend or auto_text or getattr(fig, "_wxl_center", False):
            prepare_figure(fig, lock_ends=lock_ends, auto_legend=auto_legend,
                           auto_text=auto_text, caption_max_mm=target_width_mm)

    w0, h0 = (float(v) for v in fig.get_size_inches())
    aspect = h0 / w0 if w0 else 1.0

    if target_width_mm:
        # Alternate calibration and layout until both the trimmed width and the
        # legend placement are stable, because moving a legend changes the tight
        # bounding box. Text does not scale with the canvas, so a very large type
        # scale can make the width jump between iterations; keep the canvas size
        # whose measured width was closest to the target and restore it at the end.
        probe = stem.with_suffix(".probe.png")
        best = None
        for _ in range(8):
            _prepare()
            _relayout()
            fig.savefig(probe, dpi=dpi, bbox_inches="tight", pad_inches=pad)
            m = measure_width_mm(probe, dpi)
            w, h = (float(v) for v in fig.get_size_inches())
            err = abs(m - target_width_mm)
            if best is None or err < best[0] - 1e-9:
                best = (err, w, h)
            if err <= tol_mm:
                break
            new_w = w * target_width_mm / m
            fig.set_size_inches(new_w, new_w * aspect)
        if best is not None:
            cur_w = float(fig.get_size_inches()[0])
            if abs(cur_w - best[1]) > 1e-9:
                fig.set_size_inches(best[1], best[2])
                _prepare()
                _relayout()
        probe.unlink(missing_ok=True)
    else:
        _prepare()
        _relayout()

    saved = []
    for ext in formats:
        p = stem.with_suffix(f".{ext}")
        fig.savefig(p, dpi=dpi, bbox_inches="tight", pad_inches=pad)
        saved.append(p)
    if close:
        plt.close(fig)
    return saved


# --------------------------------------------------------------------------
# Style verification
# --------------------------------------------------------------------------

def _is_polar(ax) -> bool:
    return getattr(ax, "name", "") == "polar"


def check_wxl_style(fig, style: WXLStyle | None = None, strict_sizes: bool = True):
    """Audit a live Figure against the WXL contract.

    Returns a dict with ``ok`` plus the measured fonts/sizes and a list of
    human-readable ``problems``. Cartesian axes must carry all four spines;
    polar axes and axes with ``axison == False`` (pie/donut) are exempt.
    """
    st = style or DEFAULT_STYLE
    problems: list[str] = []
    soft: list[str] = []
    fonts: set[str] = set()
    sizes: set[float] = set()
    legend_sizes: set[float] = set()

    # legend text objects are verified separately at legend_size
    try:
        fig.canvas.draw()
        legend_text_ids = set()
        for ax in fig.get_axes():
            leg = ax.get_legend()
            if leg is not None:
                legend_text_ids.update(id(t) for t in leg.get_texts())
    except Exception:                                  # pragma: no cover
        legend_text_ids = set()

    # ---- text: font file and size -------------------------------------
    for t in fig.findobj(lambda a: isinstance(a, mtext.Text)):
        if not t.get_text().strip():
            continue
        fp = t.get_fontproperties()
        fonts.add(Path(findfont(fp)).name.lower())
        s = round(float(fp.get_size()), 2)
        if id(t) in legend_text_ids:
            legend_sizes.add(s)
        else:
            sizes.add(s)
    for f in sorted(fonts):
        if not _font_is_allowed(f):
            problems.append(
                f"non-house font in use: {f} (expected a Times New Roman file or "
                f"a metric-compatible serif fallback)")

    if strict_sizes:
        want = round(float(st.font_size), 2)
        for s in sorted(sizes):
            if abs(s - want) > 1e-9:
                problems.append(
                    f"font size {s} pt is outside the uniform {st.font_size:g} pt scale")
        want_leg = round(float(st.legend_size), 2)
        for s in sorted(legend_sizes):
            if abs(s - want_leg) > 1e-9:
                problems.append(
                    f"legend font size {s} pt is outside {st.legend_size:g} pt")

    # ---- missing glyphs ----------------------------------------------
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always")
        try:
            fig.canvas.draw()
        except Exception as exc:                      # pragma: no cover
            problems.append(f"canvas draw failed: {exc}")
        glyphs = {str(w.message) for w in wlist if "missing from font" in str(w.message)}
    for g in sorted(glyphs):
        problems.append(g)

    # ---- axes: spines, ticks, grid ------------------------------------
    axes = [a for a in fig.get_axes() if a.get_visible()]
    n_axes = len(axes)
    for i, ax in enumerate(axes):
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar"):
            continue
        for side in ("top", "right", "left", "bottom"):
            if not ax.spines[side].get_visible():
                problems.append(f"axes[{i}]: spine '{side}' hidden (full box required)")
        if any(l.get_visible() for l in ax.get_xgridlines()) or \
           any(l.get_visible() for l in ax.get_ygridlines()):
            problems.append(f"axes[{i}]: grid lines visible (grid must be off)")
        ticks = list(ax.xaxis.majorTicks) + list(ax.yaxis.majorTicks)
        for tk in ticks:
            if getattr(tk, "_tickdir", "in") != "in":
                problems.append(f"axes[{i}]: tick direction is not 'in'")
                break
        # axis ends must land exactly on the first and last tick label
        if not ax.images:
            for name in ("x", "y"):
                axis = ax.xaxis if name == "x" else ax.yaxis
                if _axis_is_categorical(axis):
                    continue                      # categorical axis
                lims = sorted(float(v) for v in
                              (ax.get_xlim() if name == "x" else ax.get_ylim()))
                span = lims[1] - lims[0]
                if span <= 0:
                    continue
                locs = sorted(float(t) for t in axis.get_majorticklocs()
                              if lims[0] - 1e-9 <= float(t) <= lims[1] + 1e-9)
                if not locs:
                    problems.append(f"axes[{i}]: {name}-axis has no tick labels")
                    continue
                tol = max(1e-6 * span, 1e-9)
                if abs(locs[0] - lims[0]) > tol or abs(locs[-1] - lims[1]) > tol:
                    problems.append(
                        f"axes[{i}]: {name}-axis ends {lims[0]:g}..{lims[1]:g} do not "
                        f"sit on tick values {locs[0]:g}..{locs[-1]:g}")
                labels = [t.get_text().strip() for t in axis.get_majorticklabels()]
                labels = [l for l in labels if l]
                if len(labels) < 2:
                    problems.append(f"axes[{i}]: {name}-axis ends are unlabelled")

    # ---- legends: framed, inside, opaque ------------------------------
    n_legends = 0
    for i, ax in enumerate(axes):
        leg = ax.get_legend()
        if leg is None:
            continue
        n_legends += 1
        frame = leg.get_frame()
        if not frame.get_visible():
            problems.append(f"axes[{i}]: legend frame hidden")
        ec = to_hex(frame.get_edgecolor(), keep_alpha=False).upper()
        if ec != "#000000":
            problems.append(f"axes[{i}]: legend border is {ec}, expected #000000")
        if float(frame.get_alpha() or 1.0) < 0.999:
            problems.append(f"axes[{i}]: legend frame is transparent")
        # soft check: the legend should sit on empty canvas
        try:
            score = _legend_overlap_score(ax, leg.get_window_extent())
            if score > 0.02:
                ab = ax.get_window_extent()
                lb = leg.get_window_extent()
                share = (lb.width * lb.height) / max(ab.width * ab.height, 1e-9)
                soft.append(
                    f"axes[{i}]: legend covers about {score * 100:.0f}% of the "
                    f"plotted data and takes {share * 100:.0f}% of the panel. "
                    f"Widen the figure, drop the legend for direct labels, or "
                    f"give it a dedicated panel")
        except Exception:
            pass

    # ---- text: annotations and crowded tick labels ---------------------
    for i, ax in enumerate(axes):
        if not ax.axison or _is_polar(ax) or hasattr(ax, "_colorbar"):
            continue
        texts = _data_annotation_texts(ax)
        for text in texts:
            others = [t.get_window_extent() for t in texts if t is not text]
            hits = _text_collision_count(ax, text.get_window_extent(), others)
            if hits > 0:
                soft.append(
                    f"axes[{i}]: annotation '{text.get_text()[:18]}' touches "
                    f"{hits:.0f} plotted artist(s)")
        if _tick_labels_overlap(ax):
            soft.append(f"axes[{i}]: adjacent tick labels overlap")

    # ---- colours -------------------------------------------------------
    allowed_colors = {v.upper() for v in WXL_PALETTE.values()} | {"#000000", "#FFFFFF"}
    for art in fig.findobj(lambda a: isinstance(a, matplotlib.lines.Line2D)):
        if not art.get_visible():
            continue
        c = to_hex(art.get_color(), keep_alpha=False).upper()
        if c not in allowed_colors:
            problems.append(f"off-palette line colour {c}")
    for art in fig.findobj(lambda a: isinstance(a, matplotlib.patches.Patch)):
        if not art.get_visible():
            continue
        for attr in ("get_facecolor", "get_edgecolor"):
            rgba = getattr(art, attr)()
            if rgba is None or (np.ndim(rgba) == 1 and rgba[3] == 0):
                continue
            c = to_hex(rgba, keep_alpha=False).upper()
            if c not in allowed_colors:
                problems.append(f"off-palette patch colour {c}")
    for art in fig.findobj(lambda a: isinstance(a, matplotlib.collections.PathCollection)):
        if not art.get_visible():
            continue
        fcs = art.get_facecolors()
        if fcs is None or len(fcs) == 0:
            continue
        for rgba in fcs:
            c = to_hex(rgba, keep_alpha=False).upper()
            if c not in allowed_colors:
                problems.append(f"off-palette scatter colour {c}")

    return {
        "ok": not problems,
        "fonts": sorted(fonts),
        "sizes": sorted(sizes),
        "n_axes": n_axes,
        "n_legends": n_legends,
        "problems": sorted(set(problems)),
        "warnings": sorted(set(soft)),
    }
