"""Publication-ready Plotly figures (HTML + PNG 300dpi + SVG).

Figures:
  fig1_overview            2x2 Vietnam overview
                             A absolute DALYs, B % composition,
                             C age-std rate + 95% UI,
                             D NCD share of total DALYs over time
  fig2_heatmap             Top-15 Vietnam cause heatmap (relative to 1990)
  fig3_decomposition       NCD + CMNN Das Gupta waterfall
  fig4_sea_comparison      SEA NCD-share trajectories + SDI-vs-share scatter
  fig5_age_sex_pyramid     1990 vs 2023 age-sex DALY pyramid
  fig6_yll_yld_trends      Vietnam YLL/YLD rate + ratio
  fig7_sea_yll_yld         SEA YLL/YLD ratio bar ranking
  fig8_cmnn_sensitivity    Main vs CMNN-split sensitivity side-by-side
  fig9_30q70_vietnam       Vietnam 30q70 NCD vs CMNN probability
                             (WHO SDG 3.4.1, 1990-2023)
  fig10_sea_ncd_premature  SEA age-standardized NCD death rate 2023 ranking
                             (premature-mortality proxy for cross-country
                              comparison; Vietnam-level 30q70 not available
                              for other SEA countries)
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
    fig.add_hline(y=50, line_dash="dot", line_color="#888888",
                  row=2, col=2,
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
# Figure 2 - heatmap of top-15 Vietnam causes
# ---------------------------------------------------------------------------

def fig2_heatmap():
    q2a = pd.read_csv(PROC / "cmnn_vietnam.csv")
    q2b = pd.read_csv(PROC / "ncd_vietnam.csv")
    det = pd.concat([q2a, q2b], ignore_index=True)
    det = det[(det["measure_name"] == MEASURE["daly"])
              & (det["metric_name"] == "Rate")
              & (det["age_name"] == "Age-standardized")
              & (det["sex_name"] == "Both")
              & (~det["cause_name"].isin(
                  [CAUSE_GROUPS["cmnn"], CAUSE_GROUPS["ncd"]]))]

    latest = det[det["year"] == 2023]
    top15 = (latest.sort_values("val", ascending=False)
             .drop_duplicates("cause_name")["cause_name"].head(15).tolist())

    years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]
    mat = (det[det["cause_name"].isin(top15) & det["year"].isin(years)]
           .pivot_table(index="cause_name", columns="year", values="val")
           .reindex(top15))
    rel = mat.div(mat[1990], axis=0)

    def _wrap(s, maxw=45):
        return s if len(s) <= maxw else s[:maxw - 1] + "..."

    # Annotation text = absolute rate (rounded)
    z = rel.values
    text = np.vectorize(lambda v: "" if np.isnan(v) else f"{v:.0f}")(mat.values)
    vmax = float(np.nanmax(np.abs(z - 1)))

    fig = go.Figure(go.Heatmap(
        z=z, x=[str(y) for y in years],
        y=[_wrap(c) for c in top15],
        colorscale="RdBu_r",
        zmin=1 - vmax, zmax=1 + vmax, zmid=1,
        text=text, texttemplate="%{text}",
        textfont=dict(size=9, color="black"),
        colorbar=dict(title="Rate ratio<br>vs 1990", len=0.8),
        hovertemplate=("<b>%{y}</b><br>Year: %{x}"
                       "<br>Ratio: %{z:.2f}<extra></extra>"),
    ))

    _apply_base_layout(
        fig,
        title="<b>Figure 2 - Age-standardized DALY rate of top-15 causes</b>",
        title_subtitle="Vietnam, relative to 1990; absolute rate shown in cells",
        width=1000, height=650,
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
    )
    save_fig(fig, "fig2_heatmap", width=1000, height=650)
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

    for col, cg in enumerate(["NCD", "CMNN"], start=1):
        row = decomp[decomp["cause_group"] == cg].iloc[0]
        vals = [row["pop_size"] / 1e6,
                row["age_structure"] / 1e6,
                row["age_rate"] / 1e6]
        labels = ["Population size", "Age structure", "Age-specific rate"]
        total = sum(vals)

        measures = ["relative"] * 3 + ["total"]
        xs = labels + ["Net change"]
        ys = vals + [total]
        texts = [f"{v:+.2f}M" for v in vals] + [f"{total:+.2f}M"]

        fig.add_trace(go.Waterfall(
            orientation="v",
            measure=measures,
            x=xs, y=ys,
            text=texts, textposition="outside",
            connector=dict(line=dict(color="#888888", width=1)),
            increasing=dict(marker=dict(color=PALETTE["injuries"])),
            decreasing=dict(marker=dict(color=PALETTE["cmnn"])),
            totals=dict(marker=dict(
                color=PALETTE["ncd"] if cg == "NCD" else PALETTE["cmnn"])),
            showlegend=False,
            hovertemplate="%{x}<br>%{y:+.2f}M DALYs<extra></extra>",
        ), row=1, col=col)

        fig.add_hline(y=0, line_color="black", line_width=0.8, row=1, col=col)
        # Extend y-axis so outside text labels don't collide with subplot title.
        cumulative = [sum(vals[:i + 1]) for i in range(len(vals))] + [total]
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

    # Panel A: NCD share over time
    for country in SEA_COUNTRIES:
        sub = metrics[metrics["location_name"] == country].sort_values("year")
        if country == "Vietnam":
            fig.add_trace(go.Scatter(
                x=sub["year"], y=sub["ncd_share_pct"],
                mode="lines", name="Vietnam",
                line=dict(color=PALETTE["vietnam"], width=3),
                legendgroup="vn", legendrank=1,
                hovertemplate=("Vietnam %{x}: "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=sub["year"], y=sub["ncd_share_pct"],
                mode="lines", name=country,
                line=dict(color="#AAAAAA", width=1.2),
                opacity=0.8, legendgroup="sea",
                hovertemplate=f"{country} %{{x}}: NCD share=%{{y:.2f}}%"
                              "<extra></extra>",
            ), row=1, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="black",
                  line_width=1, row=1, col=1,
                  annotation_text="50% reference",
                  annotation_position="bottom right")

    # Panel B: SDI vs NCD share (cross-sectional across country-years)
    for country in SEA_COUNTRIES:
        sub = merged[merged["location_name"] == country].sort_values("year")
        if country == "Vietnam":
            fig.add_trace(go.Scatter(
                x=sub["sdi"], y=sub["ncd_share_pct"], mode="lines",
                name="Vietnam (SDI path)",
                line=dict(color=PALETTE["vietnam"], width=3),
                showlegend=False,
                hovertemplate=("Vietnam %{text}<br>SDI=%{x:.2f}"
                               "<br>NCD share=%{y:.2f}%<extra></extra>"),
                text=sub["year"],
            ), row=1, col=2)
            fig.add_trace(go.Scatter(
                x=[sub["sdi"].iloc[0]], y=[sub["ncd_share_pct"].iloc[0]],
                mode="markers", marker=dict(color=PALETTE["vietnam"],
                                            size=10, line=dict(width=1)),
                name="Vietnam 1990", showlegend=False,
                hovertemplate=("Vietnam 1990: SDI=%{x:.2f}, "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=2)
            fig.add_trace(go.Scatter(
                x=[sub["sdi"].iloc[-1]], y=[sub["ncd_share_pct"].iloc[-1]],
                mode="markers", marker=dict(color=PALETTE["vietnam"],
                                            size=16, symbol="star",
                                            line=dict(width=1)),
                name="Vietnam 2023", showlegend=False,
                hovertemplate=("Vietnam 2023: SDI=%{x:.2f}, "
                               "NCD share=%{y:.2f}%<extra></extra>"),
            ), row=1, col=2)
        else:
            fig.add_trace(go.Scatter(
                x=sub["sdi"], y=sub["ncd_share_pct"], mode="lines",
                line=dict(color="#AAAAAA", width=1), opacity=0.55,
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
            line=dict(color="black", width=1.5, dash="dash"),
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
                arrowcolor=PALETTE["vietnam"],
                font=dict(size=9, color=PALETTE["vietnam"]),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor=PALETTE["vietnam"], borderwidth=1,
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
             & (df["cause_name"].isin(
                 [CAUSE_GROUPS["cmnn"], CAUSE_GROUPS["ncd"]]))
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
        m_cmnn = -(pv[("Male", "CMNN")].values / 1e6)
        m_ncd = -(pv[("Male", "NCD")].values / 1e6)
        f_cmnn = pv[("Female", "CMNN")].values / 1e6
        f_ncd = pv[("Female", "NCD")].values / 1e6
        panels[yr] = (m_cmnn, m_ncd, f_cmnn, f_ncd)
        xmax = max(xmax, float(np.nanmax(np.abs(
            np.concatenate([m_cmnn + m_ncd, f_cmnn + f_ncd])))))

    fig = make_subplots(
        rows=1, cols=2, shared_yaxes=True,
        subplot_titles=["A", "B"],
        horizontal_spacing=0.06,
    )
    for col, yr in enumerate([1990, 2023], start=1):
        m_cmnn, m_ncd, f_cmnn, f_ncd = panels[yr]
        first = (col == 1)
        fig.add_trace(go.Bar(
            y=AGE_GROUPS, x=m_cmnn, orientation="h",
            marker=dict(color=PALETTE["cmnn"]),
            name="CMNN", legendgroup="cmnn", showlegend=first,
            hovertemplate=(
                f"Male CMNN, %{{y}}<br>"
                f"{yr}: %{{customdata:.2f}}M<extra></extra>"),
            customdata=np.abs(m_cmnn),
        ), row=1, col=col)
        fig.add_trace(go.Bar(
            y=AGE_GROUPS, x=m_ncd, orientation="h",
            marker=dict(color=PALETTE["ncd"]),
            name="NCD", legendgroup="ncd", showlegend=first,
            hovertemplate=(
                f"Male NCD, %{{y}}<br>"
                f"{yr}: %{{customdata:.2f}}M<extra></extra>"),
            customdata=np.abs(m_ncd),
        ), row=1, col=col)
        fig.add_trace(go.Bar(
            y=AGE_GROUPS, x=f_cmnn, orientation="h",
            marker=dict(color=PALETTE["cmnn"]),
            legendgroup="cmnn", showlegend=False,
            hovertemplate=(
                f"Female CMNN, %{{y}}<br>"
                f"{yr}: %{{x:.2f}}M<extra></extra>"),
        ), row=1, col=col)
        fig.add_trace(go.Bar(
            y=AGE_GROUPS, x=f_ncd, orientation="h",
            marker=dict(color=PALETTE["ncd"]),
            legendgroup="ncd", showlegend=False,
            hovertemplate=(
                f"Female NCD, %{{y}}<br>"
                f"{yr}: %{{x:.2f}}M<extra></extra>"),
        ), row=1, col=col)
        fig.add_vline(x=0, line_color="black", line_width=0.8,
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
        ("yll", PALETTE["yll"], "YLL rate"),
        ("yld", PALETTE["yld"], "YLD rate"),
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
        line=dict(color="#333333", width=2.5),
        marker=dict(
            size=7, color=ratio.values,
            colorscale="RdBu_r", showscale=True,
            cmin=float(ratio.min()), cmax=float(ratio.max()),
            colorbar=dict(title="Ratio", x=1.04, xanchor="left",
                          len=0.7, thickness=12),
        ),
        hovertemplate="Year: %{x}<br>YLL/YLD: %{y:.2f}<extra></extra>",
    ), row=1, col=2)
    fig.add_hline(y=1, line_dash="dash", line_color="#888888",
                  row=1, col=2,
                  annotation_text="YLL = YLD",
                  annotation_position="top right")

    _apply_base_layout(
        fig,
        title="<b>Figure 6 - YLL and YLD, Vietnam 1990-2023</b>",
        title_subtitle="Age-standardized rates per 100,000, all causes",
        width=1200, height=520,
        legend=dict(x=0.45, y=1.0, xanchor="left", yanchor="top",
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="#CCCCCC", borderwidth=1),
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
    colors = [PALETTE["vietnam"] if c == "Vietnam" else "#ADB5BD"
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
    fig.add_vline(x=1, line_dash="dash", line_color="#888888",
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

    # Colors for the split components: keep CMNN red for the combined group,
    # assign lighter coral for C-only and accent pink for M+N+N.
    c_only_color = "#F08080"   # light coral
    mnn_color = "#9C6B6B"      # muted rose-brown

    # Panel A: main
    for short, color_key, col in [
        ("CMNN",     "cmnn",     "CMNN"),
        ("NCD",      "ncd",      "NCD"),
        ("Injuries", "injuries", "Injuries"),
    ]:
        fig.add_trace(go.Scatter(
            x=years, y=split[col].values,
            stackgroup="A", name=short,
            line=dict(color=PALETTE[color_key], width=0.5),
            fillcolor=_hex_to_rgba(PALETTE[color_key], 0.85),
            legendgroup=short,
            hovertemplate=f"{short}<br>%{{x}}: %{{y:,.0f}}/100k<extra></extra>",
        ), row=1, col=1)

    # Panel B: sensitivity. Share legend groups with Panel A for NCD/Injuries
    # so they appear once in the legend; the new split components get their
    # own entries.
    for short, color, col_name, legend_name, legend_group, show_leg in [
        ("C-only",   c_only_color,         "C_only",   "Communicable only",
         "c_only", True),
        ("M+N+N",    mnn_color,            "MNN",      "Maternal+Neonatal+Nutritional",
         "mnn", True),
        ("NCD",      PALETTE["ncd"],       "NCD",      "NCD", "NCD", False),
        ("Injuries", PALETTE["injuries"],  "Injuries", "Injuries",
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
# Figure 9 - Vietnam 30q70 NCD vs CMNN probability (WHO SDG 3.4.1)
# ---------------------------------------------------------------------------

def fig9_30q70_vietnam():
    """Premature (ages 30-69) death probability for NCD and CMNN in Vietnam,
    1990-2023. Computed from deaths numbers + 5-year age-band populations
    following the WHO SDG 3.4.1 formulation (see utils.probability_30q70).

    Uncertainty band: because the age-specific mortality rates from GBD come
    with 95% UI on the *rate*, we re-compute 30q70 at the low and high ends
    of those UIs to produce an indicator-level uncertainty band.
    """
    age = pd.read_csv(PROC / "age_specific.csv")
    pop = pd.read_csv(PROC / "population.csv")
    q30 = pd.read_csv(PROC / "probability_30q70.csv")

    # Reconstruct UI bands by recomputing 30q70 at the lower/upper end of
    # the deaths-number UIs (rate-based UI would also work; numbers UI is
    # what GBD exposes directly).
    from utils import AGE_BANDS_30_69, probability_30q70

    pop_wide = (pop[(pop["measure_name"] == "Population")
                    & (pop["sex_name"] == "Both")
                    & (pop["age_name"].isin(AGE_BANDS_30_69))]
                .pivot_table(index="age_name", columns="year", values="val")
                .reindex(AGE_BANDS_30_69))

    def _ui_series(cause_full):
        deaths = age[(age["measure_name"] == MEASURE["deaths"])
                     & (age["metric_name"] == "Number")
                     & (age["sex_name"] == "Both")
                     & (age["cause_name"] == cause_full)
                     & (age["age_name"].isin(AGE_BANDS_30_69))]
        out = {}
        for col, agg in [("val", "val"), ("lower", "lo"),
                         ("upper", "hi")]:
            wide = (deaths.pivot_table(index="age_name", columns="year",
                                       values=col)
                    .reindex(AGE_BANDS_30_69))
            out[agg] = {
                int(y): probability_30q70(wide[y].values, pop_wide[y].values)
                for y in wide.columns if y in pop_wide.columns
            }
        return out

    ncd = _ui_series(CAUSE_GROUPS["ncd"])
    cmnn = _ui_series(CAUSE_GROUPS["cmnn"])

    def _arr(d):
        yrs = sorted(d)
        return np.asarray(yrs, dtype=int), np.asarray([d[y] for y in yrs],
                                                      dtype=float) * 100

    fig = go.Figure()
    for data_dict, label, color in [
        (ncd, "NCD 30q70", PALETTE["ncd"]),
        (cmnn, "CMNN 30q70", PALETTE["cmnn"]),
    ]:
        yrs, val = _arr(data_dict["val"])
        _, lo = _arr(data_dict["lo"])
        _, hi = _arr(data_dict["hi"])
        fig.add_trace(go.Scatter(
            x=np.concatenate([yrs, yrs[::-1]]),
            y=np.concatenate([hi, lo[::-1]]),
            fill="toself", fillcolor=_hex_to_rgba(color, 0.15),
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=yrs, y=val, mode="lines+markers", name=label,
            line=dict(color=color, width=2.5), marker=dict(size=4),
            hovertemplate=f"{label}<br>%{{x}}: %{{y:.2f}}%<extra></extra>",
        ))

    _apply_base_layout(
        fig,
        title=("<b>Figure 9 - Probability of dying between ages 30 and 70, "
               "Vietnam 1990-2023</b>"),
        title_subtitle=("30q70 by cause group (WHO SDG 3.4.1); "
                        "Both sex; shaded bands = 95% uncertainty interval"),
        width=900, height=500,
    )
    fig.update_xaxes(title_text="Year", range=[1990, 2023])
    fig.update_yaxes(title_text="Probability of premature death (%)",
                     rangemode="tozero")

    save_fig(fig, "fig9_30q70_vietnam", width=900, height=500)
    return fig


# ---------------------------------------------------------------------------
# Figure 10 - SEA strict SDG 3.4.1 30q70 ranking, 2023 (+ 1990 reference)
# ---------------------------------------------------------------------------

def fig10_sea_ncd_premature():
    """Horizontal bar ranking of the 11 SEA countries by strict WHO
    SDG 3.4.1 30q70 (premature NCD mortality probability) in 2023, with
    1990 values overlaid as open black circles so the 33-year movement is
    visible at a glance.

    Data source: tables/sea_30q70_summary.csv (see scripts/07_30q70_sea.py).
    The indicator follows the narrow SDG definition (cardiovascular disease,
    neoplasms, diabetes+CKD, chronic respiratory disease), computed per
    country via Chiang II on 5-year age-band GBD death rates.
    """
    df = pd.read_csv(TAB / "sea_30q70_summary.csv")
    # Ascending by 2023: best performers at bottom, worst at top.
    df = df.sort_values("30q70_2023").reset_index(drop=True)

    colors = ["#c0392b" if c == "Vietnam" else "#ADB5BD" for c in df["country"]]

    fig = go.Figure()

    # 2023 bars
    fig.add_trace(go.Bar(
        x=df["30q70_2023"], y=df["country"],
        orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=0.5)),
        text=[f"{v:.1f}%" for v in df["30q70_2023"]],
        textposition="outside",
        name="2023",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "2023 30q70: %{x:.2f}%<br>"
            "1990 30q70: %{customdata:.2f}%"
            "<extra></extra>"
        ),
        customdata=df["30q70_1990"].values,
    ))

    # 1990 open-black-circle overlay
    fig.add_trace(go.Scatter(
        x=df["30q70_1990"], y=df["country"],
        mode="markers",
        marker=dict(symbol="circle-open", size=10,
                    color="black", line=dict(width=1.5)),
        name="1990",
        hoverinfo="skip",
    ))

    _apply_base_layout(fig, width=900, height=520, showlegend=True)
    fig.update_xaxes(title_text="30q70 probability of premature NCD "
                     "mortality (%)", rangemode="tozero")
    fig.update_yaxes(title_text="")

    save_fig(fig, "fig10_sea_ncd_premature", width=900, height=520)
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
    fig2_heatmap()
    fig3_decomposition(decomp)
    fig4_sea_comparison(metrics)
    fig5_age_sex_pyramid()
    fig6_yll_yld_trends(df_yll_yld)
    fig7_sea_yll_yld(df_ratio)
    fig8_cmnn_sensitivity()
    fig9_30q70_vietnam()
    fig10_sea_ncd_premature()
    print("  [ok] all 10 figures written to figures/html + figures/static")


if __name__ == "__main__":
    run()
