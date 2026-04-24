"""Lancet / ggsci palette and base Plotly layout.

Enforced repo-wide so every figure shares a consistent, journal-compatible
colour grammar.
"""

# ggsci "lanonc" qualitative palette.
LANCET = ["#00468B", "#ED0000", "#42B540", "#0099B4", "#925E9F",
          "#FDAF91", "#AD002A", "#ADB6B6", "#1B1919"]
LANCET_CMNN    = "#00468B"   # dark blue
LANCET_NCD     = "#ED0000"   # red
LANCET_INJURY  = "#42B540"   # green
LANCET_YLL     = "#925E9F"   # purple
LANCET_YLD     = "#0099B4"   # teal
LANCET_VIETNAM = "#ED0000"   # focal-country highlight
LANCET_PEER    = "#ADB6B6"   # peer-country grey
LANCET_INK     = "#1B1919"   # axes / text
LANCET_MUTED   = "#FDAF91"   # non-significant / historical

PALETTE = {
    "cmnn":     LANCET_CMNN,
    "ncd":      LANCET_NCD,
    "injuries": LANCET_INJURY,
    "yll":      LANCET_YLL,
    "yld":      LANCET_YLD,
    "vietnam":  LANCET_VIETNAM,
    "peer":     LANCET_PEER,
    "ink":      LANCET_INK,
    "muted":    LANCET_MUTED,
    "grid":     "#888888",
}

FONT_FAMILY = "Helvetica, Arial, sans-serif"

BASE_LAYOUT = dict(
    font=dict(family=FONT_FAMILY, size=11, color=LANCET_INK),
    paper_bgcolor="white",
    plot_bgcolor="white",
    margin=dict(l=60, r=30, t=50, b=60),
    legend=dict(
        bgcolor="rgba(255,255,255,0)",
        bordercolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(family=FONT_FAMILY, size=9, color=LANCET_INK),
    ),
    xaxis=dict(
        showgrid=True, gridcolor=PALETTE["grid"], gridwidth=0.5,
        griddash="dash",
        showline=True, linecolor="#333333", linewidth=0.8, mirror=True,
    ),
    yaxis=dict(
        showgrid=True, gridcolor=PALETTE["grid"], gridwidth=0.5,
        griddash="dash",
        showline=True, linecolor="#333333", linewidth=0.8, mirror=True,
    ),
)
