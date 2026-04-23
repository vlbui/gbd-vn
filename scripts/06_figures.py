"""Publication-ready Plotly figures (HTML + PNG 300dpi + SVG).

Figures:
  fig1_overview            2x2 Vietnam overview
                             A absolute DALYs, B % composition,
                             C age-std rate + 95% UI,
                             D NCD share of total DALYs over time
  fig2_period_aapc         Period-stratified AAPC forest plot for the five
                             headline Vietnam indicators (CMNN / NCD / Injury
                             DALY rate + YLL + YLD rate), four time windows
  fig3_decomposition       NCD + CMNN Das Gupta waterfall
  fig4_sea_comparison      SEA NCD-share trajectories + SDI-vs-share scatter
  fig5_age_sex_pyramid     1990 vs 2023 age-sex DALY pyramid
  fig6_yll_yld_trends      Vietnam YLL/YLD rate + ratio (moved to supplement)
  fig7_sea_yll_yld         SEA YLL/YLD ratio bar ranking (moved to supplement)
  fig8_cmnn_sensitivity    Main vs CMNN-split sensitivity side-by-side
  fig4_30q70_combined      Two-panel merged figure: Vietnam 30q70 trajectory
                             (broad GBD NCD + CMNN + SDG 3.4 target) and SEA
                             2023 strict SDG 3.4.1 ranking with 1990 overlay
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import (
    PROC, TAB, SEA_COUNTRIES, PALETTE, BASE_LAYOUT,
    CAUSE_GROUPS, CAUSE_SHORT, MEASURE,
    LANCET, LANCET_CMNN, LANCET_NCD, LANCET_INJURY,
    LANCET_YLL, LANCET_YLD, LANCET_VIETNAM, LANCET_PEER,
    LANCET_INK, LANCET_MUTED,
    ensure_dirs, save_fig,
)


AGE_GROUPS = [
    "<5 years", "5-9 years", "10-14 years", "15-19 years", "20-24 years",
    "25-29 years", "30-34 years", "35-39 years", "40-44 years",
    "45-49 years", "50-54 years", "55-59 years", "60-64 years",
    "65-69 years", "70-74 years", "75-79 years", "80+ years",
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _hex_to_rgba(h, a=0.18):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


def _apply_base_layout(fig, title=None, title_subtitle=None, **overrides):
    """Apply BASE_LAYOUT to a figure.

    Figure-level titles and subtitles are NOT baked into the image. The
    `title` and `title_subtitle` parameters remain in the signature for
    call-site compatibility but are ignored. Captions belong in the
    manuscript text, not the PNG/SVG (see utils.save_fig, which also
    strips any lingering titles via utils.strip_figure_titles).
    """
    del title, title_subtitle  # intentionally unused
    layout = {k: v for k, v in BASE_LAYOUT.items()
              if k not in ("xaxis", "yaxis", "margin")}
    for k in list(overrides):
        if k in layout:
            layout.pop(k)
    fig.update_layout(
        **layout,
        title=None,
        margin=dict(l=60, r=30, t=50, b=60),
        **overrides,
    )
    fig.update_xaxes(showgrid=True, gridcolor=PALETTE["grid"],
                     showline=True, linecolor="#333333", linewidth=0.8,
                     mirror=True)
    fig.update_yaxes(showgrid=True, gridcolor=PALETTE["grid"],
                     showline=True, linecolor="#333333", linewidth=0.8,
                     mirror=True)


# ---------------------------------------------------------------------------
# Figure 1 - 2x2 overview (Vietnam)
# ---------------------------------------------------------------------------

def fig1_overview(df_burden, metrics):
    vn = df_burden[(df_burden["location_name"] == "Vietnam")
                   & (df_burden["measure_name"] == MEASURE["daly"])
                   & (df_burden["sex_name"] == "Both")].copy()

    num_aa = vn[(vn["metric_name"] == "Number")
                & (vn["age_name"] == "All ages")
                & (vn["cause_name"].isin(CAUSE_SHORT.keys()))]
    rate_as = vn[(vn["metric_name"] == "Rate")
                 & (vn["age_name"] == "Age-standardized")
                 & (vn["cause_name"].isin(CAUSE_SHORT.keys()))]

    def _pivot(df, col):
        return (df.assign(short=df["cause_name"].map(CAUSE_SHORT))
                  .pivot_table(index="year", columns="short", values=col))
    num = _pivot(num_aa, "val")
    rate = _pivot(rate_as, "val")
    lo = _pivot(rate_as, "lower")
    hi = _pivot(rate_as, "upper")

    years = num.index.values
    total = num[["CMNN", "NCD", "Injuries"]].sum(axis=1)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["A", "B", "C", "D"],
        horizontal_spacing=0.10, vertical_spacing=0.16,
    )

    # Panel A: absolute DALYs stacked (millions)
    for g, key in [("CMNN", "cmnn"), ("NCD", "ncd"), ("Injuries", "injuries")]:
        fig.add_trace(go.Scatter(
            x=years, y=num[g].values / 1e6,
            stackgroup="A", name=g,
            line=dict(color=PALETTE[key], width=0.5),
            fillcolor=_hex_to_rgba(PALETTE[key], 0.85),
            legendgroup=g,
            hovertemplate=f"{g}<br>%{{x}}: %{{y:.2f}}M DALYs<extra></extra>",
        ), row=1, col=1)

    # Panel B: % contribution
    for g, key in [("CMNN", "cmnn"), ("NCD", "ncd"), ("Injuries", "injuries")]:
        fig.add_trace(go.Scatter(
            x=years, y=(num[g].values / total.values * 100),
            stackgroup="B", name=g,
            line=dict(color=PALETTE[key], width=0.5),
            fillcolor=_hex_to_rgba(PALETTE[key], 0.85),
            legendgroup=g, showlegend=False,
            hovertemplate=f"{g}<br>%{{x}}: %{{y:.1f}}%<extra></extra>",
        ), row=1, col=2)

    # Panel C: age-std rate with 95% UI
    for g, key in [("CMNN", "cmnn"), ("NCD", "ncd"), ("Injuries", "injuries")]:
        color = PALETTE[key]
        fig.add_trace(go.Scatter(
            x=np.concatenate([years, years[::-1]]),
            y=np.concatenate([hi[g].values, lo[g].values[::-1]]),
            fill="toself", fillcolor=_hex_to_rgba(color, 0.18),
            line=dict(color="rgba(0,0,0,0)"), showlegend=False,
            hoverinfo="skip",
        ), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=years, y=rate[g].values, mode="lines",
            name=g, line=dict(color=color, width=2.2),
            legendgroup=g, showlegend=False,
            hovertemplate=f"{g}<br>%{{x}}: %{{y:,.0f}} / 100k<extra></extra>",
        ), row=2, col=1)

    # Panel D: NCD share of total DALYs.
    # Share = NCD age-std DALYs / (CMNN + NCD + Injuries) x 100.
    vn_m = metrics[metrics["location_name"] == "Vietnam"].sort_values("year")
    fig.add_trace(go.Scatter(
        x=vn_m["year"], y=vn_m["ncd_share_pct"],
        mode="lines+markers", name="NCD share (%), Vietnam",
        line=dict(color=PALETTE["ncd"], width=2.6),
        marker=dict(size=4, color=PALETTE["ncd"]),
        legendgroup="ncdshare",
        hovertemplate="%{x}: NCD share = %{y:.2f}%<extra></extra>",
    ), row=2, col=2)
    fig.add_hline(y=50, line_dash="dot", line_color=LANCET_INK,
                  line_width=0.8, row=2, col=2,
                  annotation_text="50% reference",
                  annotation_position="bottom right")

    _apply_base_layout(
        fig,
        title="<b>Figure 1 - Vietnam DALY burden overview, 1990-2023</b>",
        width=1100, height=820,
    )
    fig.update_yaxes(title_text="DALYs (millions)", row=1, col=1)
    fig.update_yaxes(title_text="% of total DALYs", range=[0, 100], row=1, col=2)
    fig.update_yaxes(title_text="DALYs per 100,000", row=2, col=1)
    fig.update_yaxes(title_text="NCD share of total DALYs (%)",
                     range=[0, 100], row=2, col=2)
    for r, c in [(1, 1), (1, 2), (2, 1), (2, 2)]:
        fig.update_xaxes(title_text="Year", row=r, col=c)

    save_fig(fig, "fig1_overview", width=1100, height=820)
    return fig


# ---------------------------------------------------------------------------
# Figure 2 - period-stratified AAPC forest plot
# ---------------------------------------------------------------------------

def build_fig2_period_aapc():
    """Dot-and-whisker (forest) plot of period-stratified AAPC for the five
    headline Vietnam indicators (CMNN / NCD / Injuries DALY rate + all-cause
    YLL rate + all-cause YLD rate), each shown for four time windows:
    1990-2023 (full), 1990-2000, 2000-2010, 2010-2023.

    Filled marker = p < 0.05 (significant change); open marker = p >= 0.05.
    """
    trend = pd.read_csv(TAB / "trend_results.csv")

    # Row order (top -> bottom) and display labels.
    row_spec = [
        ("DALY - CMNN",            "CMNN rate"),
        ("DALY - NCD",             "NCD rate"),
        ("DALY - Injuries",        "Injury rate"),
        ("YLL rate - All causes",  "YLL rate"),
        ("YLD rate - All causes",  "YLD rate"),
    ]
    row_keys  = [r[0] for r in row_spec]
    row_names = [r[1] for r in row_spec]
    row_idx = {k: i for i, (k, _) in enumerate(row_spec)}

    # Window colour + vertical offset (dodge within a row).
    window_spec = [
        ("1990-2023", LANCET_INK,  +0.30),
        ("1990-2000", LANCET[0],   +0.10),
        ("2000-2010", LANCET[1],   -0.10),
        ("2010-2023", LANCET[2],   -0.30),
    ]

    fig = go.Figure()

    # Zero reference line.
    fig.add_vline(x=0, line_color=LANCET_INK, line_width=0.8)

    for period, color, dy in window_spec:
        sub = trend[trend["period"] == period]
        xs, ys, lo, hi, psig = [], [], [], [], []
        for _, r in sub.iterrows():
            if r["cause"] not in row_idx:
                continue
            i = row_idx[r["cause"]]
            ys.append(i + dy)
            xs.append(float(r["aapc"]))
            lo.append(float(r["aapc"] - r["ci_low"]))
            hi.append(float(r["ci_high"] - r["aapc"]))
            psig.append(float(r["p_value"]) < 0.05)

        # Filled vs open markers: Plotly scatter doesn't accept per-point
        # symbols and a shared colour with per-point fill, so we use a
        # list of symbols ("circle" / "circle-open") with the trace colour.
        symbols = ["circle" if s else "circle-open" for s in psig]
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers",
            marker=dict(
                symbol=symbols, size=8, color=color,
                line=dict(color=color, width=1.5),
            ),
            error_x=dict(
                type="data", symmetric=False,
                array=hi, arrayminus=lo,
                color=color, thickness=1.5, width=0,
            ),
            name=period,
            hovertemplate=(
                "%{text}<br>" + period +
                "<br>AAPC: %{x:+.2f}%/yr<extra></extra>"
            ),
            text=[row_names[int(round(y - dy))] for y in ys],
        ))

    _apply_base_layout(
        fig,
        width=900, height=500,
        legend=dict(
            orientation="h", x=0.5, xanchor="center",
            y=-0.18, yanchor="top",
        ),
    )
    fig.update_layout(margin=dict(l=100, r=30, t=40, b=90))
    fig.update_xaxes(title_text="AAPC (% per year)", zeroline=False)
    # y runs top-down: top row = index 0, so visually we want y=0 at the
    # top. Setting a reversed range (4.5 -> -0.5) achieves this without
    # fighting autorange.
    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(row_names))),
        ticktext=row_names,
        range=[len(row_names) - 0.5, -0.5],
        title_text="",
    )
    save_fig(fig, "fig2_period_aapc", width=900, height=500)
    return fig


# ---------------------------------------------------------------------------
# Figure 3 - Decomposition waterfall
# ---------------------------------------------------------------------------

def fig3_decomposition(decomp):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.14,
    )

    # Per-component Lancet colours (see task spec).
    comp_colors = {
        "Population size":   LANCET_MUTED,   # pop-size = muted peach
        "Age structure":     LANCET[4],      # ageing  = purple
        "Age-specific rate": LANCET[2],      # rate    = green
        "Net change":        LANCET_INK,     # net bar = ink
    }

    for col, cg in enumerate(["NCD", "CMNN"], start=1):
        row = decomp[decomp["cause_group"] == cg].iloc[0]
        vals = [row["pop_size"] / 1e6,
                row["age_structure"] / 1e6,
                row["age_rate"] / 1e6]
        labels = ["Population size", "Age structure", "Age-specific rate"]
        total = sum(vals)

        # Manual waterfall: cumulative bases for the three contribution bars,
        # total bar sits from 0. This lets us colour every bar independently.
        cum = [0.0, vals[0], vals[0] + vals[1]]
        bases = cum + [0.0]
        heights = vals + [total]
        xs = labels + ["Net change"]
        texts = [f"{v:+.2f}M" for v in vals] + [f"{total:+.2f}M"]
        bar_colors = [comp_colors[name] for name in xs]

        fig.add_trace(go.Bar(
            x=xs, y=heights, base=bases,
            marker=dict(color=bar_colors,
                        line=dict(color=LANCET_INK, width=0.6)),
            text=texts, textposition="outside",
            showlegend=False,
            hovertemplate="%{x}<br>%{y:+.2f}M DALYs<extra></extra>",
        ), row=1, col=col)

        # Connector segments between consecutive bars.
        endpoints = [cum[0] + vals[0],
                     cum[1] + vals[1],
                     cum[2] + vals[2]]
        for k in range(3):
            fig.add_shape(
                type="line", xref=f"x{col}", yref=f"y{col}",
                x0=k + 0.4, x1=k + 0.6,
                y0=endpoints[k], y1=endpoints[k],
                line=dict(color="#888888", width=0.8),
            )

        fig.add_hline(y=0, line_color=LANCET_INK, line_width=0.8,
                      row=1, col=col)
        # Extend y-axis so outside text labels don't collide with subplot title.
        cumulative = endpoints + [total]
        y_max = max(max(cumulative), 0)
        y_min = min(min(cumulative), 0)
        span = y_max - y_min
        pad = span * 0.15
        fig.update_yaxes(title_text="DALYs (millions)",
                         range=[y_min - pad, y_max + pad],
                         row=1, col=col)

    _apply_base_layout(
        fig,
        title="<b>Figure 3 - Das Gupta decomposition of DALY change, Vietnam</b>",
        title_subtitle=("Total change split into population size, "
                        "age structure, and age-specific rate effects"),
        width=1000, height=550,
    )
    save_fig(fig, "fig3_decomposition", width=1000, height=550)
    return fig


# ---------------------------------------------------------------------------
# Figure 4 - SEA NCD share + SDI vs NCD share
# ---------------------------------------------------------------------------

def fig4_sea_comparison(metrics):
    """Left panel: NCD share of total DALYs trajectories 1990-2023 for all
    11 SEA countries (Vietnam highlighted).

    Right panel: SDI vs NCD share cross-sectional scatter with a quadratic
    fit on 10 SEA countries (Vietnam excluded). Vietnam's observed-to-
    expected ratio at its 2023 SDI is annotated directly on the plot.
    """
    sdi = pd.read_csv(PROC / "sdi_sea.csv")
    merged = metrics.merge(sdi[["location_name", "year", "sdi"]],
                           on=["location_name", "year"], how="left")

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.12,
    )

    # Peer-country alpha gradient by 2023 NCD share rank (higher share ->
    # higher alpha). 10 peers -> linear ramp 0.35..0.95.
    peers = [c for c in SEA_COUNTRIES if c != "Vietnam"]
    peer_2023 = (metrics[(metrics["location_name"].isin(peers))
                         & (metrics["year"] == metrics["year"].max())]
                 .set_index("location_name")["ncd_share_pct"])
    # Fallback if a peer lacks a 2023 row: rank by most recent year available.
    if peer_2023.isna().any() or len(peer_2023) < len(peers):
        peer_2023 = (metrics[metrics["location_name"].isin(peers)]
                     .sort_values("year")
                     .drop_duplicates("location_name", keep="last")
                     .set_index("location_name")["ncd_share_pct"])
    peer_order = peer_2023.sort_values().index.tolist()
    peer_alpha = {c: 0.35 + 0.60 * (i / max(len(peer_order) - 1, 1))
                  for i, c in enumerate(peer_order)}
    # Unpack LANCET_PEER hex into rgba().
    _pr = int(LANCET_PEER[1:3], 16)
    _pg = int(LANCET_PEER[3:5], 16)
    _pb = int(LANCET_PEER[5:7], 16)

    def _peer_rgba(c, a_override=None):
        a = a_override if a_override is not None else peer_alpha.get(c, 0.6)
        return f"rgba({_pr},{_pg},{_pb},{a:.2f})"

    # Panel A: NCD share over time
    for country in SEA_COUNTRIES:
        sub = metrics[metrics["location_name"] == country].sort_values("year")
        if country == "Vietnam":
            fig.add_trace(go.Scatter(
                x=sub["year"], y=sub["ncd_share_pct"],
                mode="lines", name="Vietnam",
                line=dict(color=LANCET_VIETNAM, width=3),
                legendgroup="vn", legendrank=1,
                hovertemplate=("Vietnam %{x}: "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=sub["year"], y=sub["ncd_share_pct"],
                mode="lines", name=country,
                line=dict(color=_peer_rgba(country), width=1.2),
                legendgroup="sea",
                hovertemplate=f"{country} %{{x}}: NCD share=%{{y:.2f}}%"
                              "<extra></extra>",
            ), row=1, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color=LANCET_INK,
                  line_width=0.8, row=1, col=1,
                  annotation_text="50% reference",
                  annotation_position="bottom right")

    # Panel B: SDI vs NCD share (cross-sectional across country-years)
    for country in SEA_COUNTRIES:
        sub = merged[merged["location_name"] == country].sort_values("year")
        if country == "Vietnam":
            fig.add_trace(go.Scatter(
                x=sub["sdi"], y=sub["ncd_share_pct"], mode="lines",
                name="Vietnam (SDI path)",
                line=dict(color=LANCET_VIETNAM, width=3),
                showlegend=False,
                hovertemplate=("Vietnam %{text}<br>SDI=%{x:.2f}"
                               "<br>NCD share=%{y:.2f}%<extra></extra>"),
                text=sub["year"],
            ), row=1, col=2)
            fig.add_trace(go.Scatter(
                x=[sub["sdi"].iloc[0]], y=[sub["ncd_share_pct"].iloc[0]],
                mode="markers",
                marker=dict(color=LANCET_VIETNAM, size=10,
                            line=dict(color=LANCET_VIETNAM, width=1)),
                name="Vietnam 1990", showlegend=False,
                hovertemplate=("Vietnam 1990: SDI=%{x:.2f}, "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=2)
            fig.add_trace(go.Scatter(
                x=[sub["sdi"].iloc[-1]], y=[sub["ncd_share_pct"].iloc[-1]],
                mode="markers",
                marker=dict(color=LANCET_VIETNAM, size=16, symbol="star",
                            line=dict(color=LANCET_VIETNAM, width=1)),
                name="Vietnam 2023", showlegend=False,
                hovertemplate=("Vietnam 2023: SDI=%{x:.2f}, "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=2)
        else:
            fig.add_trace(go.Scatter(
                x=sub["sdi"], y=sub["ncd_share_pct"], mode="lines",
                line=dict(color=_peer_rgba(country), width=1),
                showlegend=False, hoverinfo="skip",
            ), row=1, col=2)

    # SEA-expected quadratic trajectory (fit excluding Vietnam).
    # Lim SS et al. Lancet 2018;392:2091-138 (SDI-expected method).
    fit = merged[(merged["location_name"] != "Vietnam")
                 & merged["sdi"].notna() & merged["ncd_share_pct"].notna()]
    obs_exp_text = ""
    if len(fit) >= 3:
        coef = np.polyfit(fit["sdi"].values,
                          fit["ncd_share_pct"].values, 2)
        xline = np.linspace(fit["sdi"].min(), fit["sdi"].max(), 100)
        yline = np.polyval(coef, xline)
        fig.add_trace(go.Scatter(
            x=xline, y=yline, mode="lines",
            name="SEA expected (quadratic, VN excluded)",
            line=dict(color=LANCET_INK, width=1.5, dash="dash"),
            hoverinfo="skip",
        ), row=1, col=2)
        vn23 = merged[(merged["location_name"] == "Vietnam")
                      & (merged["year"] == 2023)]
        if not vn23.empty:
            sdi23 = float(vn23["sdi"].iloc[0])
            obs = float(vn23["ncd_share_pct"].iloc[0])
            exp = float(np.polyval(coef, sdi23))
            ratio = obs / exp if exp else np.nan
            obs_exp_text = (f"VN 2023 obs/exp = {ratio:.3f}"
                            f"<br>(obs {obs:.1f}% vs exp {exp:.1f}%)")
            fig.add_annotation(
                xref="x2", yref="y2", x=sdi23, y=obs,
                ax=sdi23 - 0.08, ay=obs + 10,
                text=obs_exp_text, showarrow=True,
                arrowhead=2, arrowsize=1, arrowwidth=1,
                arrowcolor=LANCET_VIETNAM,
                font=dict(size=9, color=LANCET_VIETNAM),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor=LANCET_VIETNAM, borderwidth=1,
                row=1, col=2,
            )

    _apply_base_layout(
        fig,
        title="<b>Figure 4 - NCD share of total DALYs across Southeast Asia</b>",
        title_subtitle=("Age-standardized DALYs, Both sex; SDI-expected "
                        "trajectory fit on 10 SEA countries (Vietnam excluded)"),
        width=1200, height=600,
    )
    fig.update_xaxes(title_text="Year", row=1, col=1, range=[1990, 2023])
    fig.update_xaxes(title_text="Socio-Demographic Index (SDI)", row=1, col=2)
    fig.update_yaxes(title_text="NCD share of total DALYs (%)",
                     range=[0, 100], row=1, col=1)
    fig.update_yaxes(title_text="NCD share of total DALYs (%)",
                     range=[0, 100], row=1, col=2)

    save_fig(fig, "fig4_sea_comparison", width=1200, height=600)
    return fig


# ---------------------------------------------------------------------------
# Figure 5 - Age-sex pyramid 1990 vs 2023
# ---------------------------------------------------------------------------

def fig5_age_sex_pyramid():
    df = pd.read_csv(PROC / "age_specific.csv")
    sub = df[(df["measure_name"] == MEASURE["daly"])
             & (df["metric_name"] == "Number")
             & (df["sex_name"].isin(["Male", "Female"]))
             & (df["age_name"].isin(AGE_GROUPS))
             & (df["cause_name"].isin([
                 CAUSE_GROUPS["cmnn"],
                 CAUSE_GROUPS["ncd"],
                 CAUSE_GROUPS["injuries"],
             ]))
             & (df["year"].isin([1990, 2023]))].copy()
    sub["short"] = sub["cause_name"].map(CAUSE_SHORT)

    panels = {}
    xmax = 0.0
    for yr in (1990, 2023):
        pv = (sub[sub["year"] == yr]
              .pivot_table(index="age_name",
                           columns=["sex_name", "short"],
                           values="val", aggfunc="sum")
              .reindex(AGE_GROUPS))

        def _col(sex, short):
            if (sex, short) in pv.columns:
                return pv[(sex, short)].values
            return np.zeros(len(AGE_GROUPS))

        m_cmnn = -(_col("Male",   "CMNN")     / 1e6)
        m_ncd  = -(_col("Male",   "NCD")      / 1e6)
        m_inj  = -(_col("Male",   "Injuries") / 1e6)
        f_cmnn =  (_col("Female", "CMNN")     / 1e6)
        f_ncd  =  (_col("Female", "NCD")      / 1e6)
        f_inj  =  (_col("Female", "Injuries") / 1e6)
        panels[yr] = (m_cmnn, m_ncd, m_inj, f_cmnn, f_ncd, f_inj)
        xmax = max(xmax, float(np.nanmax(np.abs(np.concatenate([
            m_cmnn + m_ncd + m_inj, f_cmnn + f_ncd + f_inj,
        ])))))

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.06,
    )
    for col, yr in enumerate([1990, 2023], start=1):
        m_cmnn, m_ncd, m_inj, f_cmnn, f_ncd, f_inj = panels[yr]
        first = (col == 1)
        for short, m_arr, f_arr, color in [
            ("CMNN",     m_cmnn, f_cmnn, LANCET_CMNN),
            ("NCD",      m_ncd,  f_ncd,  LANCET_NCD),
            ("Injuries", m_inj,  f_inj,  LANCET_INJURY),
        ]:
            fig.add_trace(go.Bar(
                y=AGE_GROUPS, x=m_arr, orientation="h",
                marker=dict(color=color,
                            line=dict(color=color, width=0)),
                name=short, legendgroup=short, showlegend=first,
                hovertemplate=(
                    f"Male {short}, %{{y}}<br>"
                    f"{yr}: %{{customdata:.2f}}M<extra></extra>"),
                customdata=np.abs(m_arr),
            ), row=1, col=col)
            fig.add_trace(go.Bar(
                y=AGE_GROUPS, x=f_arr, orientation="h",
                marker=dict(color=color,
                            line=dict(color=color, width=0)),
                legendgroup=short, showlegend=False,
                hovertemplate=(
                    f"Female {short}, %{{y}}<br>"
                    f"{yr}: %{{x:.2f}}M<extra></extra>"),
            ), row=1, col=col)
        fig.add_vline(x=0, line_color=LANCET_INK, line_width=0.8,
                      row=1, col=col)

    _apply_base_layout(
        fig,
        title="<b>Figure 5 - Vietnam DALY burden by age, sex and cause group</b>",
        title_subtitle="Male (left) | Female (right); DALYs in millions",
        width=1100, height=700,
        barmode="relative", bargap=0.05,
    )
    for col in (1, 2):
        fig.update_xaxes(range=[-xmax * 1.05, xmax * 1.05], row=1, col=col,
                         tickformat=".2f", title_text="DALYs (millions)")
    save_fig(fig, "fig5_age_sex_pyramid", width=1100, height=700)
    return fig


# ---------------------------------------------------------------------------
# Figure 6 (NEW) - YLL / YLD trends, Vietnam
# ---------------------------------------------------------------------------

def fig6_yll_yld_trends(df_yll_yld):
    vn = df_yll_yld[(df_yll_yld["location_name"] == "Vietnam")
                    & (df_yll_yld["age_name"] == "Age-standardized")
                    & (df_yll_yld["sex_name"] == "Both")
                    & (df_yll_yld["metric_name"] == "Rate")
                    & (df_yll_yld["cause_name"] == CAUSE_GROUPS["all"])]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.13,
    )

    for measure_key, color, label in [
        ("yll", LANCET_YLL, "YLL rate"),
        ("yld", LANCET_YLD, "YLD rate"),
    ]:
        d = (vn[vn["measure_name"] == MEASURE[measure_key]]
             .sort_values("year"))
        fig.add_trace(go.Scatter(
            x=pd.concat([d["year"], d["year"][::-1]]),
            y=pd.concat([d["upper"], d["lower"][::-1]]),
            fill="toself", fillcolor=_hex_to_rgba(color, 0.15),
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=d["year"], y=d["val"],
            mode="lines+markers", name=label,
            line=dict(color=color, width=2.5),
            marker=dict(size=5),
            hovertemplate=f"{label}<br>%{{x}}: %{{y:,.0f}}/100k<extra></extra>",
        ), row=1, col=1)

    # Ratio panel
    yll = vn[vn["measure_name"] == MEASURE["yll"]].set_index("year")["val"]
    yld = vn[vn["measure_name"] == MEASURE["yld"]].set_index("year")["val"]
    ratio = yll / yld
    fig.add_trace(go.Scatter(
        x=ratio.index, y=ratio.values,
        mode="lines+markers", name="YLL/YLD ratio",
        line=dict(color=LANCET_INK, width=2.5),
        marker=dict(size=7, color=LANCET_INK),
        hovertemplate="Year: %{x}<br>YLL/YLD: %{y:.2f}<extra></extra>",
    ), row=1, col=2)
    fig.add_hline(y=1, line_dash="dash", line_color=LANCET_INK,
                  line_width=0.8, row=1, col=2,
                  annotation_text="YLL = YLD",
                  annotation_position="top right")

    _apply_base_layout(
        fig,
        title="<b>Figure 6 - YLL and YLD, Vietnam 1990-2023</b>",
        title_subtitle="Age-standardized rates per 100,000, all causes",
        width=1200, height=520,
        legend=dict(x=0.45, y=1.0, xanchor="left", yanchor="top",
                    bgcolor="rgba(255,255,255,0)"),
    )
    fig.update_yaxes(title_text="Rate per 100,000", row=1, col=1)
    fig.update_yaxes(title_text="YLL/YLD ratio", row=1, col=2)
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=1, col=2)
    save_fig(fig, "fig6_yll_yld_trends", width=1100, height=520)
    return fig


# ---------------------------------------------------------------------------
# Figure 7 (NEW) - YLL/YLD ratio SEA ranking
# ---------------------------------------------------------------------------

def fig7_sea_yll_yld(df_ratio):
    df = df_ratio.sort_values("ratio")  # ascending for horizontal bars
    colors = [LANCET_VIETNAM if c == "Vietnam" else LANCET_PEER
              for c in df["country"]]

    fig = go.Figure(go.Bar(
        x=df["ratio"], y=df["country"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=0.5)),
        text=[f"{r:.2f}" for r in df["ratio"]],
        textposition="outside",
        customdata=df[["yll_rate", "yld_rate"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "YLL/YLD ratio: %{x:.2f}<br>"
            "YLL rate: %{customdata[0]:,.0f}<br>"
            "YLD rate: %{customdata[1]:,.0f}<extra></extra>"
        ),
    ))
    fig.add_vline(x=1, line_dash="dash", line_color=LANCET_INK,
                  line_width=0.8,
                  annotation_text="YLL = YLD",
                  annotation_position="top")

    _apply_base_layout(
        fig,
        title="<b>Figure 7 - YLL/YLD ratio by country, Southeast Asia 2023</b>",
        title_subtitle="Age-standardized, all causes; Vietnam highlighted",
        xaxis_title="YLL/YLD ratio", yaxis_title="",
        width=750, height=520,
    )
    fig.update_xaxes(range=[0, float(df["ratio"].max()) * 1.2])
    save_fig(fig, "fig7_sea_yll_yld", width=750, height=520)
    return fig


# ---------------------------------------------------------------------------
# Figure 8 - CMNN split sensitivity (main vs C-only + M+N+N)
# ---------------------------------------------------------------------------

def fig8_cmnn_sensitivity():
    """Side-by-side comparison of main vs split-CMNN framings, Vietnam.

    Panel A - CMNN/NCD/Injuries (main analysis).
    Panel B - C-only / M+N+N / NCD / Injuries (sensitivity).

    Both panels use age-standardized DALY rate per 100k, Both sex, 1990-2023,
    shown as stacked area.
    """
    split = pd.read_csv(PROC / "cmnn_split.csv", index_col=0)
    years = split.index.values

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.10,
    )

    # Colours for the split components: CMNN total -> dark blue;
    # communicable-only -> LANCET teal; maternal+neonatal+nutritional -> purple.
    c_only_color = LANCET[3]  # teal
    mnn_color    = LANCET[4]  # purple

    # Panel A: main
    for short, color, col in [
        ("CMNN",     LANCET_CMNN,   "CMNN"),
        ("NCD",      LANCET_NCD,    "NCD"),
        ("Injuries", LANCET_INJURY, "Injuries"),
    ]:
        fig.add_trace(go.Scatter(
            x=years, y=split[col].values,
            stackgroup="A", name=short,
            line=dict(color=color, width=0.5),
            fillcolor=_hex_to_rgba(color, 0.85),
            legendgroup=short,
            hovertemplate=f"{short}<br>%{{x}}: %{{y:,.0f}}/100k<extra></extra>",
        ), row=1, col=1)

    # Panel B: sensitivity. Share legend groups with Panel A for NCD/Injuries
    # so they appear once in the legend; the new split components get their
    # own entries.
    for short, color, col_name, legend_name, legend_group, show_leg in [
        ("C-only",   c_only_color,  "C_only",   "Communicable only",
         "c_only", True),
        ("M+N+N",    mnn_color,     "MNN",      "Maternal+Neonatal+Nutritional",
         "mnn", True),
        ("NCD",      LANCET_NCD,    "NCD",      "NCD", "NCD", False),
        ("Injuries", LANCET_INJURY, "Injuries", "Injuries",
         "Injuries", False),
    ]:
        fig.add_trace(go.Scatter(
            x=years, y=split[col_name].values,
            stackgroup="B", name=legend_name,
            line=dict(color=color, width=0.5),
            fillcolor=_hex_to_rgba(color, 0.85),
            legendgroup=legend_group, showlegend=show_leg,
            hovertemplate=f"{short}<br>%{{x}}: %{{y:,.0f}}/100k<extra></extra>",
        ), row=1, col=2)

    _apply_base_layout(
        fig,
        title="<b>Figure 8 - CMNN split sensitivity, Vietnam 1990-2023</b>",
        title_subtitle=("Age-standardized DALY rate per 100,000; CMNN "
                        "decomposed into communicable (C-only) vs "
                        "maternal+neonatal+nutritional (M+N+N)"),
        width=1200, height=560,
    )
    fig.update_xaxes(title_text="Year", range=[1990, 2023], row=1, col=1)
    fig.update_xaxes(title_text="Year", range=[1990, 2023], row=1, col=2)
    fig.update_yaxes(title_text="DALYs per 100,000", row=1, col=1)
    fig.update_yaxes(title_text="DALYs per 100,000", row=1, col=2)

    save_fig(fig, "fig8_cmnn_sensitivity", width=1200, height=560)
    return fig


# ---------------------------------------------------------------------------
# Figure 4 - merged Vietnam 30q70 trajectory + SEA strict SDG 3.4.1 ranking
# ---------------------------------------------------------------------------

def build_fig4_30q70_combined():
    """Two-panel figure covering premature-NCD-mortality for Vietnam
    (panel A) and its SEA peers (panel B).

    Panel A: Vietnam 30q70 for NCD (broad GBD level-1) and CMNN, 1990-2023,
    with joinpoint-fit overlay in a faint matching colour. The WHO SDG 3.4
    one-third-reduction target trajectory from the 2015 NCD baseline to
    2030 is drawn dashed in ink.

    Panel B: 11 SEA countries ranked ascending by the strict SDG 3.4.1
    30q70 (cardiovascular diseases, neoplasms, diabetes + CKD, chronic
    respiratory diseases) in 2023. Open black circles overlay each
    country's 1990 value, so the 33-year movement is visible at a glance.
    """
    # --- Panel A data: Vietnam 30q70 (broad aggregate) -------------------
    age = pd.read_csv(PROC / "age_specific.csv")
    pop = pd.read_csv(PROC / "population.csv")
    from utils import AGE_BANDS_30_69, probability_30q70, joinpoint_aapc

    pop_wide = (pop[(pop["measure_name"] == "Population")
                    & (pop["sex_name"] == "Both")
                    & (pop["age_name"].isin(AGE_BANDS_30_69))]
                .pivot_table(index="age_name", columns="year", values="val")
                .reindex(AGE_BANDS_30_69))

    def _series(cause_full):
        deaths = age[(age["measure_name"] == MEASURE["deaths"])
                     & (age["metric_name"] == "Number")
                     & (age["sex_name"] == "Both")
                     & (age["cause_name"] == cause_full)
                     & (age["age_name"].isin(AGE_BANDS_30_69))]
        wide = (deaths.pivot_table(index="age_name", columns="year",
                                   values="val")
                .reindex(AGE_BANDS_30_69))
        data = {int(y): probability_30q70(wide[y].values, pop_wide[y].values)
                for y in wide.columns if y in pop_wide.columns}
        yrs = np.asarray(sorted(data), dtype=int)
        val = np.asarray([data[int(y)] for y in yrs], dtype=float) * 100
        return yrs, val

    vn_ncd_years,  vn_ncd_val  = _series(CAUSE_GROUPS["ncd"])
    vn_cmnn_years, vn_cmnn_val = _series(CAUSE_GROUPS["cmnn"])

    def _joinpoint_fit(years, values):
        """Piecewise log-linear fit; returns (years, fitted_values)."""
        res = joinpoint_aapc(years.astype(float), values.astype(float))
        fitted = np.full(len(years), np.nan, dtype=float)
        for seg in res.get("segments", []) or []:
            mask = (years >= seg["start_year"]) & (years <= seg["end_year"])
            if not mask.any():
                continue
            x = years[mask].astype(float)
            y = values[mask].astype(float)
            logy = np.log(y)
            X = np.vstack([x, np.ones_like(x)]).T
            beta, *_ = np.linalg.lstsq(X, logy, rcond=None)
            fitted[mask] = np.exp(beta[0] * x + beta[1])
        return years, fitted

    ncd_fit_y  = _joinpoint_fit(vn_ncd_years,  vn_ncd_val)[1]
    cmnn_fit_y = _joinpoint_fit(vn_cmnn_years, vn_cmnn_val)[1]

    # SDG 3.4 trajectory: linear from 2015 NCD baseline (22.76%) to 16.7%
    # at 2030. Task spec fixes both endpoints; we draw on [2015, 2030].
    sdg_x = np.array([2015, 2030], dtype=float)
    sdg_y = np.array([22.76, 16.70], dtype=float)

    # --- Panel B data: SEA strict SDG 3.4.1 ranking ---------------------
    sea = pd.read_csv(TAB / "sea_30q70_summary.csv")
    sea = sea.sort_values("30q70_2023").reset_index(drop=True)
    bar_colors = [LANCET_VIETNAM if c == "Vietnam" else LANCET_PEER
                  for c in sea["country"]]

    # --- Build figure ---------------------------------------------------
    fig = make_subplots(
        rows=1, cols=2,
        column_widths=[0.45, 0.55],
        horizontal_spacing=0.14,
    )

    # === Panel A: Vietnam trajectory ===
    # NCD observed
    fig.add_trace(go.Scatter(
        x=vn_ncd_years, y=vn_ncd_val,
        mode="lines+markers", name="NCD (broad)",
        line=dict(color=LANCET_NCD, width=2.5),
        marker=dict(size=5, color=LANCET_NCD),
        legendgroup="ncd",
        hovertemplate="NCD<br>%{x}: %{y:.2f}%<extra></extra>",
    ), row=1, col=1)
    # NCD joinpoint fit
    fig.add_trace(go.Scatter(
        x=vn_ncd_years, y=ncd_fit_y,
        mode="lines", name="NCD joinpoint fit",
        line=dict(color=LANCET_NCD, width=1.2),
        opacity=0.5, showlegend=False, hoverinfo="skip",
    ), row=1, col=1)
    # CMNN observed
    fig.add_trace(go.Scatter(
        x=vn_cmnn_years, y=vn_cmnn_val,
        mode="lines+markers", name="CMNN",
        line=dict(color=LANCET_CMNN, width=2.5),
        marker=dict(size=5, color=LANCET_CMNN),
        legendgroup="cmnn",
        hovertemplate="CMNN<br>%{x}: %{y:.2f}%<extra></extra>",
    ), row=1, col=1)
    # CMNN joinpoint fit
    fig.add_trace(go.Scatter(
        x=vn_cmnn_years, y=cmnn_fit_y,
        mode="lines", name="CMNN joinpoint fit",
        line=dict(color=LANCET_CMNN, width=1.2),
        opacity=0.5, showlegend=False, hoverinfo="skip",
    ), row=1, col=1)
    # SDG target trajectory
    fig.add_trace(go.Scatter(
        x=sdg_x, y=sdg_y,
        mode="lines", name="SDG 3.4 target",
        line=dict(color=LANCET_INK, width=1.2, dash="dot"),
        hovertemplate="SDG target<br>%{x}: %{y:.2f}%<extra></extra>",
    ), row=1, col=1)

    # Panel A endpoint annotations (xref="x" is the first subplot; plotly
    # reserves x1 suffix-less naming even with make_subplots).
    ncd_2023_val = float(vn_ncd_val[-1])
    cmnn_2023_val = float(vn_cmnn_val[-1])
    fig.add_annotation(
        xref="x", yref="y",
        x=2023, y=ncd_2023_val,
        text=f"{ncd_2023_val:.1f}%",
        xanchor="left", yanchor="middle",
        xshift=6, showarrow=False,
        font=dict(size=12, color=LANCET_NCD),
    )
    fig.add_annotation(
        xref="x", yref="y",
        x=2023, y=cmnn_2023_val,
        text=f"{cmnn_2023_val:.1f}%",
        xanchor="left", yanchor="middle",
        xshift=6, showarrow=False,
        font=dict(size=12, color=LANCET_CMNN),
    )
    fig.add_annotation(
        xref="x", yref="y",
        x=2030, y=16.70,
        text="16.7%",
        xanchor="left", yanchor="middle",
        xshift=4, showarrow=False,
        font=dict(size=12, color=LANCET_INK),
    )

    # Panel A letter
    fig.add_annotation(
        xref="x domain", yref="y domain",
        x=0.0, y=1.0, xanchor="left", yanchor="bottom",
        text="<b>A</b>", showarrow=False,
        font=dict(family="Helvetica, Arial, sans-serif",
                  size=16, color=LANCET_INK),
    )

    # === Panel B: SEA strict 30q70 ranking ===
    fig.add_trace(go.Bar(
        x=sea["30q70_2023"], y=sea["country"],
        orientation="h",
        marker=dict(color=bar_colors,
                    line=dict(color=LANCET_INK, width=0.6)),
        showlegend=False,
        customdata=sea["30q70_1990"].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "2023 30q70: %{x:.2f}%<br>"
            "1990 30q70: %{customdata:.2f}%"
            "<extra></extra>"
        ),
    ), row=1, col=2)
    # 1990 open-black-circle overlay
    fig.add_trace(go.Scatter(
        x=sea["30q70_1990"], y=sea["country"],
        mode="markers", name="1990",
        marker=dict(symbol="circle-open", size=9,
                    color="black",
                    line=dict(color="black", width=1.5)),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=2)

    # Panel B letter
    fig.add_annotation(
        xref="x2 domain", yref="y2 domain",
        x=0.0, y=1.0, xanchor="left", yanchor="bottom",
        text="<b>B</b>", showarrow=False,
        font=dict(family="Helvetica, Arial, sans-serif",
                  size=16, color=LANCET_INK),
    )

    # Legend (phantom traces): filled red = VN 2023, filled grey = Peer
    # 2023, open circle = 1990. Placed top-right in paper coords.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(symbol="square", size=12, color=LANCET_VIETNAM),
        name="Vietnam 2023",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(symbol="square", size=12, color=LANCET_PEER),
        name="Peer 2023",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(symbol="circle-open", size=10,
                    color="black", line=dict(color="black", width=1.5)),
        name="1990",
    ))

    _apply_base_layout(
        fig,
        width=1400, height=620,
        showlegend=True,
        legend=dict(
            x=1.0, y=1.08, xanchor="right", yanchor="bottom",
            orientation="h",
            bgcolor="rgba(255,255,255,0)",
            bordercolor="rgba(0,0,0,0)", borderwidth=0,
        ),
    )
    fig.update_layout(margin=dict(l=70, r=30, t=70, b=70))

    # Panel A axes
    fig.update_xaxes(title_text="Year", range=[1990, 2030], row=1, col=1)
    fig.update_yaxes(title_text="30q70 (%)", rangemode="tozero", row=1, col=1)
    # Panel B axes
    fig.update_xaxes(
        title_text=("30q70 (%) - WHO SDG 3.4.1 strict 4-NCD definition"),
        rangemode="tozero", row=1, col=2,
    )
    fig.update_yaxes(title_text="", row=1, col=2)

    # Country-name tick styling: Vietnam red + bold, others ink normal.
    vn_label = "<b><span style='color:#ED0000'>Vietnam</span></b>"
    tick_labels = [vn_label if c == "Vietnam" else c for c in sea["country"]]
    fig.update_yaxes(
        row=1, col=2,
        tickmode="array",
        tickvals=list(sea["country"]),
        ticktext=tick_labels,
        tickfont=dict(size=13, color=LANCET_INK),
    )

    save_fig(fig, "fig4_30q70_combined", width=1400, height=620)
    return fig


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def run():
    print("\n=== 06 FIGURES ===")
    ensure_dirs()

    df_burden = pd.read_csv(PROC / "burden_sea.csv")
    df_yll_yld = pd.read_csv(PROC / "yll_yld_sea.csv")
    metrics = pd.read_csv(TAB / "metrics.csv")
    decomp = pd.read_csv(TAB / "decomposition_results.csv")
    df_ratio = pd.read_csv(TAB / "sea_yll_yld_ratio.csv")

    fig1_overview(df_burden, metrics)
    build_fig2_period_aapc()
    fig3_decomposition(decomp)
    fig4_sea_comparison(metrics)
    fig5_age_sex_pyramid()
    fig6_yll_yld_trends(df_yll_yld)
    fig7_sea_yll_yld(df_ratio)
    fig8_cmnn_sensitivity()
    build_fig4_30q70_combined()
    print("  [ok] all 9 figures written to figures/html + figures/static")


if __name__ == "__main__":
    run()
