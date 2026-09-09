# Ask before you plot (per-figure preferences)

The house style (11 pt Times, deep-blue palette, full box, framed legends,
inward ticks, axis ends on ticks) is the default, but four decisions belong to
the user and must be confirmed **before** drawing each figure. Never pick them
yourself, and never silently reuse a previous figure's choices.

Ask all four in **one** compact question set (the `ask_user_question` tool),
offering a recommended default first. Only draw after the user answers.

---

## 1) Chart type and panel count

Ask which chart(s) and how many panels when it is not unambiguous from the task.
The options and their recommended print widths are in `references/demos.md`.

| Family | Options |
|---|---|
| Bar | grouped (with error bars), stacked, horizontal |
| Line | multi-series trend, trend + uncertainty band, stacked area |
| Relationship | scatter + fit, bubble, bidirectional error bars |
| Distribution | box, violin, histogram + KDE, ECDF, strip + mean |
| Matrix | annotated heatmap, filled contour |
| Special | radar, donut, dual axis, 2 × 2 multi-panel |

Recommended width: `single` 90 mm / `onehalf` 140 mm / `double` 190 mm. A 2 × 2
grid and a wide matrix want `double`; a single compact series often fits
`single`. Every single-column figure shares the standard 62 × 44 mm axes box
(black frame), so the rendered figure is normally narrower than 90 mm.

## 2) Axis labels and italic

Ask the x and y label text, their units, and whether each symbol is italic.

- A **physical quantity symbol** is italic; its **unit** stays upright (roman).
- Write the unit in parentheses, upright, after the symbol.
- Use mathtext for the italic symbol.

```
x:   Slip s (mm)             ->  ax.set_xlabel(r"Slip $s$ (mm)")
y:   Bond stress τ (MPa)     ->  ax.set_ylabel(r"Bond stress $\tau$ (MPa)")
y:   Vertical strain ε (με)  ->  ax.set_ylabel(r"Vertical strain $\varepsilon$ (\textmu m/m)")
```

Rules of thumb:

- A single Latin/Greek letter that names a variable → italic (`$s$`, `$\tau$`,
  `$\varepsilon$`).
- A unit (mm, MPa, %, s, ms, με) or a word (Slip, Bond stress) → upright.
- Do not italicise a subscript that is a word (e.g. `$E_{\rm{t}}$` uses upright
  `t` for a label, `$E_{\rm i}$` italic `i` for an index) — check with the user.

## 3) Line style

Ask markers, line width, and dash pattern per series.

| Attribute | Default | Alternatives |
|---|---|---|
| markers | open circle `o`, `ms=3.2`, white fill, `mew=0.9` | square `s`, triangle `^`, diamond `D`, or none for dense data |
| line width | 1.5 pt | 1.0 pt for many series, 2.0 pt for the key curve |
| dash | solid for the main series | dashed `--` for a reference / baseline / fitted model |
| marker frequency | every point | every 2nd-5th for dense data, or markers on a subset |

If a series has hundreds of points, use lines only and tell the user; markers
would just smear.

## 4) Colours and palette

Ask the per-series colour mapping, and for matrices the colormap.

- Default series order: `WXL_SERIES` = primary, contrast, improve, accent,
  secondary, neutral.
- Colour semantics to confirm: proposed / key method = primary blue, baseline /
  competitor = red (`contrast`), gain = teal (`improve`), emphasis = amber
  (`accent`), reference = grey (`neutral`).
- Matrices: `WXL_CMAP` = `RdBu_r` (signed), `Blues` (non-negative),
  `coolwarm` (signed, more contrast).
- If the user names a keyword (e.g. "Nature", "彩图1"), map it to a palette and
  confirm the concrete colours.

---

## How to ask (worked example)

```python
# not real code: the question set you send to the user
"Before I draw this figure, please confirm four things:
 1. chart type        -> [grouped bar (recommended) | stacked | ...]
 2. x-axis label      -> text: 'Slip $s$ (mm)'?  italic symbol s?
    y-axis label      -> text: 'Bond stress $\\tau$ (MPa)'?  italic symbol τ?
 3. line style        -> [open markers, 1.5 pt, solid (recommended) | dashed | ...]
 4. colours           -> [deep-blue house palette (recommended) | keyword | custom]"
```

Only after the user answers do you call `apply_wxl_style()` and draw. If a
choice stays unanswered, ask again; do not assume.

## Related files

- [../SKILL.md](../SKILL.md) — hard rule 12 (ask before you plot)
- [demos.md](demos.md) — the 20 chart types and their widths
- [design-theory.md](design-theory.md) — palette semantics, type scale
