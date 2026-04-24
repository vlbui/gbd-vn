"""Plotly post-processing + figure export.

`apply_panel_border`, `apply_lancet_style`, `strip_figure_titles` are
applied uniformly by `save_fig`, so individual figure builders don't need
to repeat axis/annotation code.
"""

from .palette import FONT_FAMILY, LANCET_INK, PALETTE
from .io import ensure_dirs
from .paths import PROJECTS


# Default write target is paper 01's figures dir. Individual paper scripts
# can override by passing fig_html_dir / fig_static_dir to save_fig.
_DEFAULT_FIG_HTML = PROJECTS / "01_epi_transition" / "figures" / "html"
_DEFAULT_FIG_STATIC = PROJECTS / "01_epi_transition" / "figures" / "static"


_PANEL_BORDER = dict(
    showline=True, linecolor="#333333", linewidth=0.8, mirror=True,
)


def apply_panel_border(fig):
    """Force every x/y axis (including subplots, twins, insets) to render
    a four-sided panel border (Plotly equivalent of matplotlib spines on
    all four sides).
    """
    fig.update_xaxes(**_PANEL_BORDER)
    fig.update_yaxes(**_PANEL_BORDER)
    return fig


def apply_lancet_style(fig):
    """Enforce Lancet/ggsci-style typography, gridlines and line weights.

    Print-crisp defaults (tuned for 300 dpi export):
      - Helvetica/Arial, base 14 pt, axis titles 15 pt, ticks 13 pt, legend 12 pt.
      - Primary data lines >= 1.5 pt; dashed reference shapes 0.8 pt.
      - Gridlines 0.5 pt dashed #888888 at alpha 0.3; axis lines 1.0 pt #333333.
      - Margin NOT set here so per-figure overrides survive.
    """
    grid_rgba = "rgba(136,136,136,0.3)"
    axis_kw = dict(
        gridcolor=grid_rgba, gridwidth=0.5, griddash="dash",
        linecolor="#333333", linewidth=1.0,
        mirror=True, ticks="outside", ticklen=5,
        zerolinecolor="#888888", zerolinewidth=0.8,
        tickfont=dict(family=FONT_FAMILY, size=13, color=LANCET_INK),
        title=dict(font=dict(family=FONT_FAMILY, size=15, color=LANCET_INK)),
    )
    fig.update_xaxes(**axis_kw)
    fig.update_yaxes(**axis_kw)
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=14, color=LANCET_INK),
        title=None,
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            bordercolor="#333333", borderwidth=0,
            font=dict(family=FONT_FAMILY, size=12, color=LANCET_INK),
        ),
    )
    # Annotations: keep explicit larger sizes (panel letters); promote
    # small/default ones to 13 pt ink.
    for ann in (fig.layout.annotations or []):
        existing = getattr(ann, "font", None)
        existing_size = None
        if existing is not None:
            try:
                existing_size = existing.size
            except Exception:
                existing_size = None
        ann.font = dict(
            family=FONT_FAMILY,
            size=existing_size if existing_size and existing_size >= 13 else 13,
            color=LANCET_INK,
        )
    # Primary trace lines: bump 0.9-1.5 pt up to 1.5.
    for tr in fig.data:
        line = getattr(tr, "line", None)
        if line is None:
            continue
        try:
            w = line.width
        except Exception:
            w = None
        if w is not None and 0.9 < float(w) < 1.5:
            tr.update(line=dict(width=1.5))
    # Dashed reference shape lines stay thin at 0.8 pt.
    shapes = list(fig.layout.shapes or [])
    new_shapes = []
    for s in shapes:
        try:
            dash = getattr(s.line, "dash", None)
        except Exception:
            dash = None
        if dash in ("dash", "dot", "dashdot", "longdash", "longdashdot"):
            s.line.width = 0.8
        new_shapes.append(s)
    if new_shapes:
        fig.update_layout(shapes=new_shapes)
    return fig


def strip_figure_titles(fig):
    """Remove figure-level title and caption-like annotations (xref/yref
    both 'paper' and text length > 3). Keeps short panel letters and
    data-referenced annotations.
    """
    fig.update_layout(title=None)
    keep = []
    for ann in (fig.layout.annotations or []):
        text = (ann.text or "").strip()
        xref = str(getattr(ann, "xref", "") or "")
        yref = str(getattr(ann, "yref", "") or "")
        data_ref = not (xref.startswith("paper") and yref.startswith("paper"))
        short_label = len(text) <= 3
        if data_ref or short_label:
            keep.append(ann)
    fig.update_layout(annotations=keep)
    return fig


def save_fig(fig, name, width=900, height=600,
             fig_html_dir=None, fig_static_dir=None):
    """Save a Plotly figure to HTML, PNG (300 dpi) and SVG.

    By default writes to `projects/01_epi_transition/figures/{html,static}/`.
    Pass fig_html_dir / fig_static_dir to target another paper's folder.

    Panel borders are enforced and caption-like annotations are stripped
    before export — captions belong in manuscript text, not the image.
    """
    html_dir = fig_html_dir if fig_html_dir is not None else _DEFAULT_FIG_HTML
    static_dir = fig_static_dir if fig_static_dir is not None else _DEFAULT_FIG_STATIC
    ensure_dirs(html_dir, static_dir)

    strip_figure_titles(fig)
    apply_lancet_style(fig)
    apply_panel_border(fig)

    fig.write_html(html_dir / f"{name}.html", include_plotlyjs="cdn")
    # 300 dpi PNG: scale = 300/72 on Plotly's 72-dpi base.
    fig.write_image(static_dir / f"{name}.png",
                    width=width, height=height, scale=300 / 72)
    fig.write_image(static_dir / f"{name}.svg",
                    width=width, height=height)
    print(f"  [ok] saved: {name}.html + {name}.png/.svg")
