"""WXL publication figure style (v1.0).

House style for matplotlib figures meant for Elsevier / IEEE / Springer
submissions, tuned so that figure text matches Word 10 pt body text when the
figure is inserted at its original physical size.

Hard rules (see SKILL.md):
  * Times New Roman everywhere, STIX math glyphs, no sans-serif faces.
  * Uniform 10 pt text (caption / axis label / tick / legend / annotation).
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

#: Uniform 10 pt type scale (matches Word 10 pt at 100 % insertion).
WXL_FONTSIZE = {
    "caption": 10, "label": 10, "tick": 10,
    "legend": 10, "annot": 10, "panel": 10,
}

#: Figure width = final print width, so 10 pt stays 10 pt after insertion.
#: single = 90 mm, onehalf = 140 mm, double = 190 mm.
WXL_FIGSIZE = {
    "single": (3.54, 2.70),
    "onehalf": (5.51, 3.90),
    "double": (7.48, 5.20),
    "double_tall": (7.48, 6.80),
    "slide": (10.0, 6.00),
}

#: Final printed width of each preset, in millimetres.
WXL_WIDTH_MM = {
    "single": 90.0,
    "onehalf": 140.0,
    "double": 190.0,
    "double_tall": 190.0,
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

    font_size: float = 10.0        # base text size (pt)
    caption_size: float = 10.0
    tick_size: float = 10.0
    legend_size: float = 10.0
    annot_size: float = 10.0
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


def place_all_legends(fig, rounds: int = 2, candidates=None):
    """Refine every in-axes legend so it covers as little data as possible.

    Tries the candidate positions, grows the y-range and retries, then flattens a
    legend with three or more entries into two columns. Polar axes, colorbar axes
    and axes with ``axison == False`` keep their hand-placed legend.
    Returns ``[(axes, (score, loc)), ...]``.
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
        out.append((ax, res))
    return out


def prepare_figure(fig, lock_ends: bool = True, auto_legend: bool = True):
    """Bring a figure to contract state: axis ends locked, legends deconflicted.

    Call this before :func:`check_wxl_style` when you audit a figure yourself.
    :func:`finalize_figure` calls it automatically.
    """
    if lock_ends:
        lock_axis_ends_all(fig)
    if auto_legend:
        place_all_legends(fig)
    return fig


def add_caption(fig, text: str, fontsize: float | None = None, y: float = -0.045, **kwargs):
    """Figure caption centered BELOW the figure (hard rule: never on top)."""
    kwargs.setdefault("ha", "center")
    kwargs.setdefault("va", "top")
    return fig.text(0.5, y, text,
                    fontsize=fontsize or WXL_FONTSIZE["caption"], **kwargs)


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


def panel_tag(ax, tag: str, y: float = -0.32):
    """Panel label such as ``(a)`` placed just BELOW its own panel."""
    return ax.text(0.0, y, tag, transform=ax.transAxes, ha="left", va="top",
                   fontsize=WXL_FONTSIZE["panel"], fontweight="bold")


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
                    lock_ends: bool = True, auto_legend: bool = True):
    """Save the figure to one or more formats and return the list of paths.

    Saving always uses ``bbox_inches="tight"`` so a caption placed below the
    figure is captured instead of clipped.

    ``target_width_mm`` closes the trap that tight cropping opens: the tight
    bounding box trims the canvas margins, so a figure authored with
    ``figsize=(7.48, 5.20)`` (190 mm) often saves as ~158 mm wide. Inserting that
    image at its natural size keeps the text at 10 pt, but stretching it to fill
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
        if layout:
            try:
                fig.tight_layout(pad=1.0)
            except Exception:
                pass

    def _prepare():
        # Axis-end locking and legend placement must run AFTER any canvas resize:
        # resizing changes how much of the axes a fixed 10 pt legend occupies.
        if lock_ends or auto_legend:
            prepare_figure(fig, lock_ends=lock_ends, auto_legend=auto_legend)

    w0, h0 = (float(v) for v in fig.get_size_inches())
    aspect = h0 / w0 if w0 else 1.0

    if target_width_mm:
        # Alternate calibration and layout until both the trimmed width and the
        # legend placement are stable, because moving a legend changes the tight
        # bounding box.
        probe = stem.with_suffix(".probe.png")
        for _ in range(5):
            _prepare()
            _relayout()
            fig.savefig(probe, dpi=dpi, bbox_inches="tight", pad_inches=pad)
            m = measure_width_mm(probe, dpi)
            if abs(m - target_width_mm) <= tol_mm:
                break
            w = float(fig.get_size_inches()[0]) * target_width_mm / m
            fig.set_size_inches(w, w * aspect)
        else:
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

    # ---- text: font file and size -------------------------------------
    for t in fig.findobj(lambda a: isinstance(a, mtext.Text)):
        if not t.get_text().strip():
            continue
        fp = t.get_fontproperties()
        fonts.add(Path(findfont(fp)).name.lower())
        sizes.add(round(float(fp.get_size()), 2))
    for f in sorted(fonts):
        if not _font_is_allowed(f):
            problems.append(
                f"non-house font in use: {f} (expected a Times New Roman file or "
                f"a metric-compatible serif fallback)")

    allowed_sizes = {round(float(st.font_size), 2)}
    if strict_sizes:
        for s in sorted(sizes):
            if s not in allowed_sizes:
                problems.append(f"font size {s} pt is outside the uniform {st.font_size:g} pt scale")

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
