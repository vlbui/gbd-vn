"""Shared utility functions and constants for the GBD Vietnam analysis.

Notes on raw data conventions (quirks we normalize at load time):
  - location_name in GBD uses 'Viet Nam', 'Lao People's Democratic Republic',
    'Brunei Darussalam'. We normalize to 'Vietnam', 'Lao PDR', 'Brunei Darussalam'
    so downstream code matches the SEA_COUNTRIES list.
  - sex_name uses 'Both' (not 'Both sexes').
  - measure_name uses the long form, e.g.
        'DALYs (Disability-Adjusted Life Years)'
        'YLLs (Years of Life Lost)'
        'YLDs (Years Lived with Disability)'
    The MEASURE dict below maps short names -> long names.
  - Cause groups are the full GBD level-1 labels; use CAUSE_GROUPS.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

try:
    import ruptures as rpt
    _HAS_RUPTURES = True
except Exception:
    _HAS_RUPTURES = False


# --- Paths ------------------------------------------------------------------

# PROJECT_ROOT is the directory *above* scripts/, resolved from this file so
# scripts work regardless of the caller's CWD.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "processed"
FIG_HTML = PROJECT_ROOT / "figures" / "html"
FIG_STATIC = PROJECT_ROOT / "figures" / "static"
TAB = PROJECT_ROOT / "tables"
SCRIPTS = PROJECT_ROOT / "scripts"


# --- Constants --------------------------------------------------------------

SEA_COUNTRIES = [
    "Vietnam", "Thailand", "Indonesia", "Philippines",
    "Malaysia", "Myanmar", "Cambodia", "Lao PDR",
    "Singapore", "Brunei Darussalam", "Timor-Leste",
]

# Map GBD-native location names -> friendly names used throughout the project
LOC_NORMALIZE = {
    "Viet Nam": "Vietnam",
    "Lao People's Democratic Republic": "Lao PDR",
}

# Long-form measure names as they appear in GBD CSVs
MEASURE = {
    "deaths": "Deaths",
    "daly": "DALYs (Disability-Adjusted Life Years)",
    "yll": "YLLs (Years of Life Lost)",
    "yld": "YLDs (Years Lived with Disability)",
}

CAUSE_GROUPS = {
    "cmnn": "Communicable, maternal, neonatal, and nutritional diseases",
    "ncd": "Non-communicable diseases",
    "injuries": "Injuries",
    "all": "All causes",
}

# Short labels for display in tables and figures
CAUSE_SHORT = {
    CAUSE_GROUPS["cmnn"]: "CMNN",
    CAUSE_GROUPS["ncd"]: "NCD",
    CAUSE_GROUPS["injuries"]: "Injuries",
    CAUSE_GROUPS["all"]: "All",
}


# --- Plotly styling ---------------------------------------------------------

# ggsci Lancet ("lanonc") qualitative palette. Enforced repo-wide so every
# figure shares a consistent, journal-compatible colour grammar.
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

# Semantic palette used throughout figure builders. Preserves the original
# keys (cmnn/ncd/injuries/yll/yld/vietnam/grid) so existing call sites resolve
# cleanly against the Lancet colour space.
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


# --- Panel borders + caption stripping (Plotly) -----------------------------
# Post-processing helpers applied uniformly across all figure builders, so
# individual figures don't need to repeat the same axis/annotation code.

_PANEL_BORDER = dict(
    showline=True, linecolor="#333333", linewidth=0.8, mirror=True,
)


def apply_panel_border(fig):
    """Force every x/y axis (including subplots, twins, insets) to render
    a four-sided panel border by setting `mirror=True` with a consistent
    line color/width. This is the Plotly equivalent of matplotlib's
    `ax.spines[side].set_visible(True)` for all four sides.
    """
    # Plotly keeps per-subplot axes keyed as xaxis, xaxis2, xaxis3, ... and
    # similarly for yaxis. Updating the *_all_xaxes/_yaxes* selectors hits
    # every one at once, including those created by make_subplots.
    fig.update_xaxes(**_PANEL_BORDER)
    fig.update_yaxes(**_PANEL_BORDER)
    return fig


def apply_lancet_style(fig):
    """Enforce Lancet/ggsci-style typography, gridlines and line weights.

    Print-crisp defaults (tuned for 300 dpi export at typical Word/PDF
    page scale):
      - Font family: Helvetica, Arial, sans-serif
      - Base font 14 pt (paragraph runs in legend/hover)
      - Axis titles 15 pt, tick labels 13 pt, legend 12 pt no frame
      - In-plot annotations 13 pt (unless explicitly set larger)
      - Primary data lines >= 1.5 pt
      - Gridlines 0.5 pt, dashed, #888888 at alpha 0.3
      - Axis lines 1.0 pt #333333, ticks outside, ticklen 5
      - Ink colour #1B1919 for axes/text

    Margin is intentionally NOT set here so per-figure overrides
    (forest plot, merged 30q70, etc.) survive.
    """
    grid_rgba = "rgba(136,136,136,0.3)"
    axis_kw = dict(
        gridcolor=grid_rgba, gridwidth=0.5, griddash="dash",
        linecolor="#333333", linewidth=1.0,
        mirror=True, ticks="outside", ticklen=5,
        zerolinecolor="#888888", zerolinewidth=0.8,
        tickfont=dict(family=FONT_FAMILY, size=13, color=LANCET_INK),
        title=dict(font=dict(family=FONT_FAMILY, size=15,
                             color=LANCET_INK)),
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
    # Annotations: keep any explicit larger size (panel letters at 16 pt
    # etc.), but force small/default annotations up to 13 pt ink.
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
    # Promote primary trace line widths up to 1.5 pt. Leave narrower
    # construction lines (stack outlines at 0.5) and any width >= 1.5 alone.
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
    # Reference shape lines: ensure dashed/dotted stay thin at 0.8 pt.
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
    """Remove figure-level title, any per-subplot title annotations created
    by make_subplots, and any top/bottom caption annotations. Keeps panel
    letter annotations (short text like 'A', 'B') and any annotations that
    are attached to data coordinates (xref/yref not starting with 'paper').
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


# --- IO helpers -------------------------------------------------------------

def ensure_dirs():
    for d in [PROC, FIG_HTML, FIG_STATIC, TAB, SCRIPTS]:
        d.mkdir(parents=True, exist_ok=True)


def load_gbd_csv(filepath):
    """Read a GBD-format CSV, standardize columns and normalize location names."""
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "year" in df.columns:
        df["year"] = df["year"].astype(int)
    for col in ("val", "lower", "upper"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "location_name" in df.columns:
        df["location_name"] = df["location_name"].replace(LOC_NORMALIZE)
    return df


def format_ci(val, lower, upper, decimals=1):
    fmt = f"{{:.{decimals}f}}"
    return f"{fmt.format(val)} ({fmt.format(lower)}-{fmt.format(upper)})"


def get_asr(df):
    return df[df["age_name"] == "Age-standardized"].copy()


def get_all_ages(df):
    return df[df["age_name"] == "All ages"].copy()


def calculate_aapc(years, rates):
    """Single-segment log-linear AAPC with 95% CI and p-value.

    Assumes a constant annual percent change over the full period. For the
    NCD share joinpoint AAPC used in SEA comparison we instead call
    `joinpoint_aapc_ci` below, which allows piecewise slopes.
    """
    years = np.asarray(years, dtype=float)
    rates = np.asarray(rates, dtype=float)
    mask = ~np.isnan(rates) & ~np.isinf(rates) & (rates > 0)
    y = years[mask]
    r = rates[mask]
    if len(y) < 3:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan, p_value=np.nan,
                    n_obs=len(y))
    slope, intercept, _, p, se = stats.linregress(y, np.log(r))
    aapc = (np.exp(slope) - 1) * 100
    ci_low = (np.exp(slope - 1.96 * se) - 1) * 100
    ci_hi = (np.exp(slope + 1.96 * se) - 1) * 100
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_hi, p_value=p,
                n_obs=int(len(y)))


# --- Standard transition indicators ----------------------------------------
# All indicators here follow published conventions (GBD, WHO SDG, Das Gupta,
# Clegg, Lim et al.). See inline citations on each function.

def cause_shares(df_level1, country=None):
    """Percent-of-total DALY composition by cause group.

    Parameters
    ----------
    df_level1 : DataFrame
        Long-format level-1 burden data (burden_sea.csv style). Must contain
        columns: location_name, year, measure_name, metric_name, age_name,
        sex_name, cause_name, val.
    country : str, optional
        If given, restrict to this location_name.

    Returns a wide DataFrame indexed by (location_name, year) with columns:
        CMNN, NCD, Injuries           absolute age-standardized DALY rates
        cmnn_share_pct,
        ncd_share_pct,
        injuries_share_pct,
        cmnn_ncd_ratio

    Uses Both-sex age-standardized DALY *Rate* per 100k as the composition
    substrate (internally equivalent to using age-standardized Number because
    shares are scale-invariant). This is the GBD-convention comparison
    across countries and time (IHME GBD Results Tool; Murray et al. 2020).
    """
    df = df_level1
    if country is not None:
        df = df[df["location_name"] == country]
    cmnn = CAUSE_GROUPS["cmnn"]
    ncd = CAUSE_GROUPS["ncd"]
    inj = CAUSE_GROUPS["injuries"]
    sub = df[(df["measure_name"] == MEASURE["daly"])
             & (df["metric_name"] == "Rate")
             & (df["age_name"] == "Age-standardized")
             & (df["sex_name"] == "Both")
             & (df["cause_name"].isin([cmnn, ncd, inj]))]
    wide = (sub.assign(short=sub["cause_name"].map(CAUSE_SHORT))
            .pivot_table(index=["location_name", "year"],
                         columns="short", values="val"))
    # Enforce column order even if some are missing
    for c in ("CMNN", "NCD", "Injuries"):
        if c not in wide.columns:
            wide[c] = np.nan
    total = wide[["CMNN", "NCD", "Injuries"]].sum(axis=1)
    wide["cmnn_share_pct"] = wide["CMNN"] / total * 100
    wide["ncd_share_pct"] = wide["NCD"] / total * 100
    wide["injuries_share_pct"] = wide["Injuries"] / total * 100
    wide["cmnn_ncd_ratio"] = wide["CMNN"] / wide["NCD"]
    return wide.reset_index()


# Age intervals used for the 30q70 WHO SDG 3.4.1 indicator
AGE_BANDS_30_69 = [
    "30-34 years", "35-39 years", "40-44 years", "45-49 years",
    "50-54 years", "55-59 years", "60-64 years", "65-69 years",
]


def probability_30q70(deaths, population):
    """Unconditional probability of dying between ages 30 and 70 from a
    given cause, following the WHO/GBD life-table formulation.

    Formula (actuarial 5-year intervals):
        q_{30,70} = 1 - prod_{x in {30,35,...,65}} (1 - 5 m_x / (1 + 2.5 m_x))
    where m_x is the age-specific mortality rate (deaths per person-year) in
    five-year age band starting at x.

    References
    ----------
    WHO. Global Action Plan for the Prevention and Control of NCDs
        2013-2020. Geneva, 2013. (Indicator 10 = 30q70 NCD.)
    UN SDG indicator 3.4.1: probability of dying from any of CVD, cancer,
        diabetes, or chronic respiratory disease between ages 30 and 70.

    Parameters
    ----------
    deaths, population : array-like of length 8
        Both ordered to match AGE_BANDS_30_69. deaths is *numbers*, not
        rates; rate m_x = deaths_x / population_x.

    Returns
    -------
    float in [0, 1] (or np.nan if any input is NaN/non-positive).
    """
    d = np.asarray(deaths, dtype=float)
    p = np.asarray(population, dtype=float)
    if d.shape != p.shape or d.size != 8:
        raise ValueError(f"expected 8 age bands; got d={d.shape}, p={p.shape}")
    if np.any(np.isnan(d)) or np.any(np.isnan(p)) or np.any(p <= 0):
        return np.nan
    m = d / p
    # 5-year conditional probability of death: n=5, a=n/2=2.5
    q5 = 5 * m / (1 + 2.5 * m)
    return float(1 - np.prod(1 - q5))


def joinpoint_aapc(years, y, max_joins=3, max_bkps=None):
    """Joinpoint (piecewise log-linear) AAPC with 95% CI via the delta method.

    This is the single canonical AAPC calculation used everywhere in the
    pipeline (Table 1, Table 4, sensitivity). Uses `ruptures.Dynp` with an
    l2 cost on detrended log(y) to locate up to `max_joins` breakpoints,
    selecting the best k (0..max_joins) by BIC. Each segment is refit as
    a simple log-linear regression with pooled residual variance; AAPC is
    the weighted (by segment-year span) mean of segment log-slopes, and
    its 95% CI uses the delta method assuming segments are approximately
    independent.

    References
    ----------
    Kim HJ, Fay MP, Feuer EJ, Midthune DN. Permutation tests for joinpoint
        regression with applications to cancer rates. Stat Med 2000;19:335-51.
    Clegg LX, Hankey BF, Tiwari R, Feuer EJ, Edwards BK. Estimating Average
        Annual Per Cent Change in Trend Analysis. Stat Med 2009;28:3670-82.

    Returns a dict with keys: aapc (%), ci_low, ci_high (%), p_value,
    n_obs, bkps_k, segments (list).
    """
    if max_bkps is not None:  # legacy name
        max_joins = max_bkps
    # Sort by x and filter non-positive/NaN so joinpoint operates on a clean,
    # chronologically ordered sequence regardless of caller input.
    years = np.asarray(years, dtype=float)
    y = np.asarray(y, dtype=float)
    order = np.argsort(years)
    years, y = years[order], y[order]
    mask = (y > 0) & ~np.isnan(y)
    years, y = years[mask], y[mask]
    n = len(years)
    if n < 4:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    p_value=np.nan, n_obs=int(n),
                    bkps_k=0, segments=[])
    log_y = np.log(y)

    def _fit_segments(bkps):
        """Fit per-segment log-linear regression, return segments list + SSR.

        Variance is estimated using *pooled* residual variance across all
        segments (s² = RSS_total / (n - 2*num_segments)) so segments with
        only 2 data points inherit a stable SE estimate from longer ones.
        This matches the Clegg 2009 joinpoint-regression convention.
        """
        segs_xy = []
        ssr = 0.0
        prev = 0
        for b in bkps:
            xs = years[prev:b]
            ys = log_y[prev:b]
            if len(xs) < 2:
                prev = b
                continue
            X = np.vstack([xs, np.ones_like(xs)]).T
            beta, *_ = np.linalg.lstsq(X, ys, rcond=None)
            resid = ys - X @ beta
            ssr += float((resid ** 2).sum())
            segs_xy.append((xs, ys, beta, X))
            prev = b

        num_seg = len(segs_xy)
        dof_total = n - 2 * num_seg
        s2 = (ssr / dof_total) if dof_total > 0 else float("nan")

        segs = []
        for xs, ys, beta, X in segs_xy:
            if not np.isnan(s2):
                cov = np.linalg.inv(X.T @ X) * s2
                slope_se = float(np.sqrt(cov[0, 0]))
            else:
                slope_se = float("nan")
            segs.append({
                "start_year": int(xs[0]), "end_year": int(xs[-1]),
                "n_years": int(len(xs)),
                "slope": float(beta[0]), "slope_se": slope_se,
                "apc_pct": float((np.exp(beta[0]) - 1) * 100),
            })
        return segs, ssr

    # Linear detrend so change-point detection picks slope changes
    X_full = np.vstack([years, np.ones_like(years)]).T
    beta_full, *_ = np.linalg.lstsq(X_full, log_y, rcond=None)
    resid_full = log_y - X_full @ beta_full

    best = None
    for k in range(0, max_joins + 1):
        if (k + 1) * 2 > n:
            continue
        if k == 0 or not _HAS_RUPTURES:
            bkps = [n]
        else:
            try:
                algo = rpt.Dynp(model="l2", min_size=2, jump=1).fit(resid_full)
                bkps = algo.predict(n_bkps=k)
            except Exception:
                bkps = [n]
        segs, ssr = _fit_segments(bkps)
        if not segs:
            continue
        p = 2 * len(segs) + k  # 2 params per segment + k breakpoint positions
        bic = n * np.log(max(ssr / n, 1e-12)) + p * np.log(n)
        if best is None or bic < best["bic"]:
            best = dict(bic=bic, segs=segs, k=k)

    segs = best["segs"]
    w = np.array([max(s["n_years"] - 1, 1) for s in segs], dtype=float)
    w_tot = w.sum()
    if w_tot <= 0 or any(np.isnan(s["slope_se"]) for s in segs):
        aapc = (np.exp(segs[0]["slope"]) - 1) * 100 if segs else np.nan
        return dict(aapc=aapc, ci_low=np.nan, ci_high=np.nan,
                    p_value=np.nan, n_obs=int(n),
                    bkps_k=best["k"], segments=segs)
    # Clegg 2009 delta-method AAPC
    weighted_slope = float(np.sum([w[i] * segs[i]["slope"]
                                   for i in range(len(segs))]) / w_tot)
    var_slope = float(np.sum([(w[i] / w_tot) ** 2 * segs[i]["slope_se"] ** 2
                              for i in range(len(segs))]))
    se = float(np.sqrt(var_slope))
    aapc = (np.exp(weighted_slope) - 1) * 100
    ci_low = (np.exp(weighted_slope - 1.96 * se) - 1) * 100
    ci_high = (np.exp(weighted_slope + 1.96 * se) - 1) * 100
    # Two-sided z-test on H0: weighted log-slope = 0
    if se > 0:
        z = weighted_slope / se
        p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
    else:
        p_value = float("nan")
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_high,
                p_value=p_value, n_obs=int(n),
                bkps_k=best["k"], segments=segs)


# Back-compat alias for earlier drafts that imported the CI variant.
joinpoint_aapc_ci = joinpoint_aapc


def expected_vs_observed_on_sdi(df_metric, df_sdi, country, year,
                                value_col, exclude_country=None, deg=2):
    """Fit a polynomial regression of `value_col` on SDI using all rows
    *except* `exclude_country` and evaluate the fitted curve at the given
    (country, year)'s SDI to produce an "expected" value. Returns the
    observed/expected ratio and components.

    This is the standard GBD SDI-expected comparison (Lim et al. Lancet
    2018;392:2091-138, Healthcare Access and Quality Index method).
    """
    m = df_metric.merge(
        df_sdi[["location_name", "year", "sdi"]],
        on=["location_name", "year"], how="left",
    )
    fit = m[(m["location_name"] != (exclude_country or country))
            & m["sdi"].notna() & m[value_col].notna()]
    if len(fit) < (deg + 1):
        return dict(observed=np.nan, expected=np.nan, ratio=np.nan, coef=None)
    coef = np.polyfit(fit["sdi"].values, fit[value_col].values, deg)
    row = m[(m["location_name"] == country) & (m["year"] == year)]
    if row.empty or pd.isna(row["sdi"].iloc[0]):
        return dict(observed=np.nan, expected=np.nan, ratio=np.nan, coef=coef)
    sdi = float(row["sdi"].iloc[0])
    expected = float(np.polyval(coef, sdi))
    observed = float(row[value_col].iloc[0])
    return dict(observed=observed, expected=expected,
                ratio=(observed / expected) if expected else np.nan,
                coef=coef, sdi=sdi)


# --- Figure export ---------------------------------------------------------

def save_fig(fig, name, width=900, height=600):
    """Save a Plotly figure to HTML, PNG (~200 DPI) and SVG.

    Before writing, panel borders are enforced and any caption-like text
    baked into the figure is stripped - captions belong in the manuscript
    text, not the image.
    """
    ensure_dirs()
    strip_figure_titles(fig)
    apply_lancet_style(fig)
    apply_panel_border(fig)
    fig.write_html(FIG_HTML / f"{name}.html", include_plotlyjs="cdn")
    # 300 dpi PNG: scale = 300/72 on Plotly's 72-dpi base. Needed for crisp
    # axis/text rendering at typical Lancet / Word print size.
    fig.write_image(FIG_STATIC / f"{name}.png",
                    width=width, height=height, scale=300 / 72)
    fig.write_image(FIG_STATIC / f"{name}.svg",
                    width=width, height=height)
    print(f"  [ok] saved: figures/html/{name}.html + static/{name}.png/.svg")


# --- Joinpoint AAPC, Pelt variant (strict SDG 30q70) ------------------------

def joinpoint_aapc_pelt(years, values, max_joins=3):
    """Joinpoint AAPC using `ruptures.Pelt(model='l2')` with BIC-style
    penalty `pen = 2*log(n)`, capped at `max_joins` breakpoints.

    Compared with `joinpoint_aapc` (which uses Dynp and selects k by full
    BIC model search), Pelt is faster and is the variant asked for by the
    SDG 3.4.1 30q70 pipeline. Both return comparable AAPC estimates but
    segment splits may differ on series with ambiguous change points.

    Aggregation follows Clegg 2009: weighted mean of segment log-slopes
    (weights = segment-year span), CI via quadrature of segment SEs, with
    pooled residual variance across segments.

    Returns a dict with keys aapc (%), ci_low, ci_high, n_bkps, segments.
    """
    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)
    order = np.argsort(years)
    years, values = years[order], values[order]
    mask = (values > 0) & ~np.isnan(values)
    years, values = years[mask], values[mask]
    n = len(years)
    if n < 4:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    n_bkps=0, segments=[])

    log_y = np.log(values)

    if _HAS_RUPTURES:
        try:
            algo = rpt.Pelt(model="l2", min_size=2, jump=1).fit(log_y)
            raw = algo.predict(pen=2 * np.log(n))
            # ruptures returns breakpoints as the index *past the segment
            # end*, with the final element == n. Convert to cut positions.
            cuts = [c for c in raw if 0 < c < n][:max_joins]
            bkps = cuts + [n]
        except Exception:
            bkps = [n]
    else:
        bkps = [n]

    # Fit per-segment log-linear regression with pooled residual variance
    segs_xy = []
    ssr = 0.0
    prev = 0
    for b in bkps:
        xs = years[prev:b]
        ys = log_y[prev:b]
        if len(xs) >= 2:
            X = np.vstack([xs, np.ones_like(xs)]).T
            beta, *_ = np.linalg.lstsq(X, ys, rcond=None)
            resid = ys - X @ beta
            ssr += float((resid ** 2).sum())
            segs_xy.append((xs, ys, beta, X))
        prev = b

    num_seg = len(segs_xy)
    if num_seg == 0:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan,
                    n_bkps=0, segments=[])
    dof = n - 2 * num_seg
    s2 = (ssr / dof) if dof > 0 else float("nan")

    segs = []
    for xs, _ys, beta, X in segs_xy:
        slope_se = float("nan")
        if not np.isnan(s2):
            cov = np.linalg.inv(X.T @ X) * s2
            slope_se = float(np.sqrt(cov[0, 0]))
        segs.append(dict(start=int(xs[0]), end=int(xs[-1]),
                         n_years=int(len(xs)),
                         slope=float(beta[0]), slope_se=slope_se,
                         apc_pct=float((np.exp(beta[0]) - 1) * 100)))

    w = np.array([max(s["n_years"] - 1, 1) for s in segs], dtype=float)
    w_tot = w.sum()
    if w_tot <= 0 or any(np.isnan(s["slope_se"]) for s in segs):
        return dict(aapc=(np.exp(segs[0]["slope"]) - 1) * 100,
                    ci_low=np.nan, ci_high=np.nan,
                    n_bkps=max(0, num_seg - 1), segments=segs)

    weighted_slope = float(sum(w[i] * segs[i]["slope"]
                               for i in range(num_seg)) / w_tot)
    # Quadrature of per-segment contributions (weights sum to 1)
    var_slope = float(sum((w[i] / w_tot) ** 2 * segs[i]["slope_se"] ** 2
                          for i in range(num_seg)))
    se = float(np.sqrt(var_slope))
    aapc = (np.exp(weighted_slope) - 1) * 100
    ci_low = (np.exp(weighted_slope - 1.96 * se) - 1) * 100
    ci_high = (np.exp(weighted_slope + 1.96 * se) - 1) * 100
    return dict(aapc=aapc, ci_low=ci_low, ci_high=ci_high,
                n_bkps=max(0, num_seg - 1), segments=segs)
