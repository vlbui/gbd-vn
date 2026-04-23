"""
GBD Vietnam Epidemiological Transition Analysis, 1990-2023.
Target: Lancet Regional Health - Western Pacific.

Sections
--------
1. Load & Clean Data
2. Core Metrics (cause composition shares, CMNN/NCD ratio)
3. Trend Analysis (Joinpoint via `ruptures` + APC + AAPC)
   Kim HJ et al. Stat Med 2000;19:335-351.
   Clegg LX et al. Stat Med 2009 (AAPC delta-method CI).
4. Decomposition (Das Gupta 1993, Standardization and Decomposition of Rates)
5. SEA Comparison (NCD share + SDI-expected ratio;
   Lim SS et al. Lancet 2018;392:2091-138)
6. Figures (publication-ready)
7. Summary Table
"""

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import ruptures as rpt

warnings.filterwarnings("ignore")

# =============================================================================
# Paths and global config
# =============================================================================

# Resolve project root relative to this file so the script is portable.
try:
    ROOT = Path(__file__).resolve().parent
except NameError:
    ROOT = Path.cwd()
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "figures"
TAB = ROOT / "tables"
for p in (PROC, FIG, TAB):
    p.mkdir(parents=True, exist_ok=True)

YEAR_MIN, YEAR_MAX = 1990, 2023

# 11 SEA countries used in the paper (normalized form — matches scripts/).
SEA_COUNTRIES = [
    "Vietnam", "Thailand", "Indonesia", "Philippines", "Malaysia",
    "Myanmar", "Cambodia", "Lao PDR",
    "Singapore", "Brunei Darussalam", "Timor-Leste",
]

# GBD-native -> normalized. Applied at load time so downstream code can match
# SEA_COUNTRIES and both pipelines (scripts/ and analysis.py) produce tables
# with identical location_name values.
LOC_NORMALIZE = {
    "Viet Nam": "Vietnam",
    "Lao People's Democratic Republic": "Lao PDR",
}

# Display names (used in the "country" column on summary outputs).
COUNTRY_DISPLAY = {
    "Brunei Darussalam": "Brunei",
}

# Okabe-Ito colour-blind-friendly palette
PALETTE = {
    "CMNN": "#E69F00",
    "NCD": "#0072B2",
    "Injuries": "#009E73",
    "Vietnam": "#D55E00",
    "neutral": "#999999",
    "accent": "#CC79A7",
    "highlight": "#56B4E9",
}

# Publication figure defaults
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 300,
    "figure.dpi": 150,
})

# mm -> inches, column widths
MM = 1 / 25.4
W1 = 88 * MM
W2 = 180 * MM

# Canonical GBD labels
CMNN_LABEL = "Communicable, maternal, neonatal, and nutritional diseases"
NCD_LABEL = "Non-communicable diseases"
INJ_LABEL = "Injuries"
DALY_LABEL = "DALYs (Disability-Adjusted Life Years)"


# =============================================================================
# Utility functions
# =============================================================================

def snake_case(df):
    df = df.copy()
    df.columns = [
        c.strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df


def save_fig(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    print(f"  saved figures/{name}.png + .svg")


def shade_ui(ax, x, lower, upper, color, alpha=0.18, label=None):
    ax.fill_between(x, lower, upper, color=color, alpha=alpha,
                    linewidth=0, label=label)


# =============================================================================
# SECTION 1 - LOAD & CLEAN DATA
# =============================================================================

def section1_load_clean():
    print("=" * 70)
    print("SECTION 1 - Load & Clean Data")
    print("=" * 70)

    # Level-1 cause groups: SEA countries + Timor concatenated first,
    # then standardized, filtered, and tagged.
    q1a = pd.read_csv(RAW / "query1_level1.csv")
    q1b = pd.read_csv(RAW / "query1_level1_timor.csv")
    q1 = pd.concat([q1a, q1b], ignore_index=True)
    q1 = snake_case(q1)
    # Normalize raw GBD names to the forms used throughout the project.
    q1["location_name"] = q1["location_name"].replace(LOC_NORMALIZE)
    print(f"  query1 (level-1 SEA+Timor): {len(q1):,} rows, "
          f"{q1['location_name'].nunique()} locations")

    q1 = q1[q1["location_name"].isin(SEA_COUNTRIES)].copy()
    q1 = q1[(q1["year"] >= YEAR_MIN) & (q1["year"] <= YEAR_MAX)].copy()
    q1["cause_group"] = q1["cause_name"].map({
        CMNN_LABEL: "CMNN",
        NCD_LABEL: "NCD",
        INJ_LABEL: "Injuries",
        "All causes": "All",
    })

    # Vietnam disease-detail tables
    q2a = snake_case(pd.read_csv(RAW / "query2a_cmnn.csv"))
    q2b = snake_case(pd.read_csv(RAW / "query2b_ncd.csv"))
    q2a = q2a[(q2a["year"] >= YEAR_MIN) & (q2a["year"] <= YEAR_MAX)].copy()
    q2b = q2b[(q2b["year"] >= YEAR_MIN) & (q2b["year"] <= YEAR_MAX)].copy()
    print(f"  query2a (Vietnam CMNN detail): {len(q2a):,} rows, "
          f"{q2a['cause_name'].nunique()} causes")
    print(f"  query2b (Vietnam NCD detail):  {len(q2b):,} rows, "
          f"{q2b['cause_name'].nunique()} causes")

    # Age-specific Vietnam data
    q3 = snake_case(pd.read_csv(RAW / "query3_age.csv"))
    q3 = q3[(q3["year"] >= YEAR_MIN) & (q3["year"] <= YEAR_MAX)].copy()
    print(f"  query3 (Vietnam age-specific): {len(q3):,} rows, "
          f"ages={q3['age_name'].nunique()}")

    # Population
    q4 = snake_case(pd.read_csv(RAW / "query4_pop.csv"))
    q4 = q4[(q4["year"] >= YEAR_MIN) & (q4["year"] <= YEAR_MAX)].copy()
    print(f"  query4 (Vietnam population): {len(q4):,} rows")

    # SDI (rename to match conventional GBD column names)
    sdi = snake_case(pd.read_csv(RAW / "SDI.csv"))
    sdi = sdi.rename(columns={"year_id": "year", "mean_value": "sdi"})
    sdi["location_name"] = sdi["location_name"].replace(LOC_NORMALIZE)
    sdi = sdi[sdi["location_name"].isin(SEA_COUNTRIES)].copy()
    sdi = sdi[(sdi["year"] >= YEAR_MIN) & (sdi["year"] <= YEAR_MAX)].copy()
    print(f"  SDI: {len(sdi):,} rows, locations={sdi['location_name'].nunique()}")

    # Cause hierarchy (for reference)
    hier = snake_case(pd.read_excel(RAW / "hierarchy.XLSX"))

    # Data-quality report
    print("\n  --- Data quality ---")
    for name, df in [("q1", q1), ("q2a", q2a), ("q2b", q2b),
                     ("q3", q3), ("q4", q4), ("sdi", sdi)]:
        na = df.isna().sum().sum()
        yr_lo, yr_hi = df["year"].min(), df["year"].max()
        locs = df["location_name"].nunique() if "location_name" in df else "n/a"
        print(f"  {name}: missing={na}, year=[{yr_lo}-{yr_hi}], locations={locs}")

    # Split age-standardized vs all-ages rows for later use
    def split_ages(df, label):
        asr = df[df["age_name"] == "Age-standardized"].copy()
        allages = df[df["age_name"] == "All ages"].copy()
        print(f"  {label}: age-std={len(asr):,} rows, all-ages={len(allages):,} rows")
        return asr, allages

    q1_asr, q1_all = split_ages(q1, "q1")
    q2a_asr, _ = split_ages(q2a, "q2a")
    q2b_asr, _ = split_ages(q2b, "q2b")

    # Save cleaned files
    q1.to_csv(PROC / "level1_sea_1990_2023.csv", index=False)
    q1_asr.to_csv(PROC / "level1_sea_asr.csv", index=False)
    q1_all.to_csv(PROC / "level1_sea_allages.csv", index=False)
    q2a.to_csv(PROC / "vietnam_cmnn_detail.csv", index=False)
    q2b.to_csv(PROC / "vietnam_ncd_detail.csv", index=False)
    q3.to_csv(PROC / "vietnam_age_specific.csv", index=False)
    q4.to_csv(PROC / "vietnam_population.csv", index=False)
    sdi.to_csv(PROC / "sdi_sea.csv", index=False)
    print("  --> cleaned files written to data/processed/")

    return dict(
        q1=q1, q1_asr=q1_asr, q1_all=q1_all,
        q2a=q2a, q2b=q2b, q3=q3, q4=q4, sdi=sdi, hier=hier,
    )


# =============================================================================
# SECTION 2 - CORE METRICS (cause composition shares)
# =============================================================================
# Uses the standard GBD-convention cause-composition metrics: CMNN / NCD /
# Injuries share of total age-standardized DALYs, plus CMNN/NCD ratio.

def section2_core_metrics(data):
    print("\n" + "=" * 70)
    print("SECTION 2 - Core Metrics (cause composition shares)")
    print("=" * 70)

    q1_asr = data["q1_asr"]
    daly = q1_asr[
        (q1_asr["measure_name"] == DALY_LABEL)
        & (q1_asr["metric_name"] == "Rate")
        & (q1_asr["sex_name"] == "Both")
        & (q1_asr["cause_group"].isin(["CMNN", "NCD", "Injuries"]))
    ].copy()

    pvt = daly.pivot_table(
        index=["location_name", "year"],
        columns="cause_group",
        values="val",
    ).reset_index()
    pvt.columns.name = None
    for c in ("CMNN", "NCD", "Injuries"):
        if c not in pvt.columns:
            pvt[c] = np.nan

    total = pvt[["CMNN", "NCD", "Injuries"]].sum(axis=1)
    pvt["cmnn_share_pct"] = pvt["CMNN"] / total * 100
    pvt["ncd_share_pct"] = pvt["NCD"] / total * 100
    pvt["injuries_share_pct"] = pvt["Injuries"] / total * 100
    pvt["cmnn_ncd_ratio"] = pvt["CMNN"] / pvt["NCD"]

    pvt["country"] = pvt["location_name"].map(
        lambda x: COUNTRY_DISPLAY.get(x, x)
    )
    pvt.to_csv(TAB / "metrics.csv", index=False)

    print("  NCD share of total DALYs in 2023 by country:")
    latest = (pvt[pvt["year"] == 2023]
              [["country", "cmnn_share_pct", "ncd_share_pct",
                "injuries_share_pct", "cmnn_ncd_ratio"]]
              .sort_values("ncd_share_pct", ascending=False))
    print(latest.to_string(index=False, float_format="%.3f"))
    print("  --> tables/metrics.csv")
    return pvt


# =============================================================================
# SECTION 3 - JOINPOINT / APC / AAPC
# =============================================================================

def joinpoint_apc_aapc(years, y, max_bkps=3):
    """
    Piecewise-linear joinpoint regression on log(y) vs year using
    ruptures.Dynp with RSS cost, selecting the number of breakpoints
    (0..max_bkps) by BIC. Returns joinpoints, per-segment APC and overall AAPC.
    """
    years = np.asarray(years, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = y > 0
    years = years[mask]
    y = y[mask]
    n = len(years)
    if n < 4:
        return None
    log_y = np.log(y)

    # Detrend against linear fit first so change-point detection picks slope
    # changes rather than absolute level. We then refit per segment on log_y.
    X_full = np.vstack([years, np.ones_like(years)]).T
    beta_full, *_ = np.linalg.lstsq(X_full, log_y, rcond=None)
    resid = log_y - X_full @ beta_full

    def _ssr_partition(bkps_idx):
        # bkps_idx: list of right-endpoints (exclusive), last is n
        ssr = 0.0
        prev = 0
        for b in bkps_idx:
            xs = years[prev:b]
            ys = log_y[prev:b]
            if len(xs) < 2:
                ssr += 0.0
            else:
                Xs = np.vstack([xs, np.ones_like(xs)]).T
                bts, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
                ssr += float(((ys - Xs @ bts) ** 2).sum())
            prev = b
        return ssr

    # BIC across k = 0..max_bkps breakpoints
    best = {"bic": np.inf, "bkps_idx": [n], "ssr": None, "k": 0}
    for k in range(0, max_bkps + 1):
        # Need at least 2 points per segment
        if (k + 1) * 2 > n:
            continue
        try:
            if k == 0:
                bkps = [n]
            else:
                algo = rpt.Dynp(model="l2", min_size=2, jump=1).fit(resid)
                bkps = algo.predict(n_bkps=k)
        except Exception:
            continue
        ssr = _ssr_partition(bkps)
        if ssr <= 0:
            ssr = 1e-12
        # 2 params per segment + k breakpoint positions
        p = 2 * (k + 1) + k
        bic = n * np.log(ssr / n) + p * np.log(n)
        if bic < best["bic"]:
            best.update({"bic": bic, "bkps_idx": bkps, "ssr": ssr, "k": k})

    # Build segments
    segments = []
    prev = 0
    for b in best["bkps_idx"]:
        xs = years[prev:b]
        ys = log_y[prev:b]
        if len(xs) < 2:
            prev = b
            continue
        Xs = np.vstack([xs, np.ones_like(xs)]).T
        bts, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
        slope = float(bts[0])
        apc = (np.exp(slope) - 1) * 100
        segments.append({
            "start_year": int(xs[0]),
            "end_year": int(xs[-1]),
            "slope_logyear": slope,
            "intercept": float(bts[1]),
            "apc_pct": apc,
            "n_years": int(len(xs)),
        })
        prev = b

    # Interior joinpoints are the years at segment boundaries
    joinpoints = [s["end_year"] for s in segments[:-1]]

    # AAPC = weighted log-mean of (1 + APC/100), weights = segment span in years
    weights = np.array([max(s["n_years"] - 1, 1) for s in segments], dtype=float)
    if weights.sum() <= 0:
        aapc = segments[0]["apc_pct"] if segments else np.nan
    else:
        log_mean = np.sum(
            np.log1p(np.array([s["apc_pct"] / 100 for s in segments])) * weights
        ) / weights.sum()
        aapc = (np.exp(log_mean) - 1) * 100

    return {
        "joinpoints": joinpoints,
        "segments": segments,
        "aapc_pct": float(aapc),
        "n_obs": int(n),
        "bic_k": int(best["k"]),
    }


def section3_trends(data):
    print("\n" + "=" * 70)
    print("SECTION 3 - Trend Analysis (Joinpoint + APC + AAPC)")
    print("=" * 70)

    q1_asr = data["q1_asr"]
    daly = q1_asr[
        (q1_asr["measure_name"] == DALY_LABEL)
        & (q1_asr["metric_name"] == "Rate")
        & (q1_asr["sex_name"] == "Both")
        & (q1_asr["cause_group"].isin(["CMNN", "NCD", "Injuries"]))
    ].copy()

    rows = []
    for country in SEA_COUNTRIES:
        sub_c = daly[daly["location_name"] == country]
        for group in ["CMNN", "NCD", "Injuries"]:
            sub = sub_c[sub_c["cause_group"] == group].sort_values("year")
            if len(sub) < 4:
                continue
            res = joinpoint_apc_aapc(sub["year"].values, sub["val"].values,
                                     max_bkps=3)
            if res is None:
                continue
            for seg in res["segments"]:
                rows.append({
                    "country": COUNTRY_DISPLAY.get(country, country),
                    "location_name": country,
                    "cause_group": group,
                    "segment_start": seg["start_year"],
                    "segment_end": seg["end_year"],
                    "apc_pct": seg["apc_pct"],
                    "aapc_pct_1990_2023": res["aapc_pct"],
                    "joinpoints": ";".join(str(j) for j in res["joinpoints"]),
                    "n_years_segment": seg["n_years"],
                    "n_breakpoints": res["bic_k"],
                })
    tr = pd.DataFrame(rows)
    tr.to_csv(TAB / "trend_results.csv", index=False)

    vn = (tr[tr["country"] == "Vietnam"]
          .drop_duplicates(subset=["cause_group"], keep="first")
          [["cause_group", "aapc_pct_1990_2023", "joinpoints", "n_breakpoints"]])
    print("  Vietnam AAPC 1990-2023 (age-std DALY rate):")
    print(vn.to_string(index=False, float_format="%.2f"))
    print(f"  --> tables/trend_results.csv ({len(tr)} segment rows)")
    return tr


# =============================================================================
# SECTION 4 - DAS GUPTA DECOMPOSITION
# =============================================================================

def das_gupta_decomposition(pop_t0, rate_t0, pop_t1, rate_t1):
    """
    Symmetric three-factor Das Gupta decomposition of the change in total
    events D = P * sum(s * r) between two time points:

        dD = (population size effect)
           + (age structure effect)
           + (age-specific rate effect)

    pop_*:  age-specific populations
    rate_*: age-specific rates per person
    """
    P0, P1 = pop_t0.sum(), pop_t1.sum()
    s0 = pop_t0 / P0
    s1 = pop_t1 / P1
    r0, r1 = rate_t0, rate_t1

    size = ((P1 - P0) / 2) * (np.sum(s0 * r0) + np.sum(s1 * r1))
    age_struct = ((P0 + P1) / 2) * np.sum((s1 - s0) * (r0 + r1) / 2)
    rate_eff = ((P0 + P1) / 2) * np.sum((s0 + s1) / 2 * (r1 - r0))

    total = size + age_struct + rate_eff
    observed = np.sum(pop_t1 * r1) - np.sum(pop_t0 * r0)
    return {
        "pop_size": size,
        "age_structure": age_struct,
        "age_rate": rate_eff,
        "total_decomp": total,
        "observed_change": observed,
        "residual": observed - total,
    }


def section4_decomposition(data):
    print("\n" + "=" * 70)
    print("SECTION 4 - Das Gupta Decomposition (1990 -> 2023)")
    print("=" * 70)

    q3 = data["q3"]
    q4 = data["q4"]

    age_groups = [
        "<5 years", "5-9 years", "10-14 years", "15-19 years", "20-24 years",
        "25-29 years", "30-34 years", "35-39 years", "40-44 years",
        "45-49 years", "50-54 years", "55-59 years", "60-64 years",
        "65-69 years", "70-74 years", "75-79 years", "80+ years",
    ]

    pop = q4[
        (q4["sex_name"] == "Both")
        & (q4["age_name"].isin(age_groups))
        & (q4["measure_name"] == "Population")
    ].copy()
    pop_wide = pop.pivot_table(
        index="age_name", columns="year", values="val"
    ).reindex(age_groups)

    daly_age = q3[
        (q3["measure_name"] == DALY_LABEL)
        & (q3["metric_name"] == "Rate")
        & (q3["sex_name"] == "Both")
        & (q3["age_name"].isin(age_groups))
    ].copy()
    daly_age["cause_group"] = daly_age["cause_name"].map(
        {CMNN_LABEL: "CMNN", NCD_LABEL: "NCD"}
    )
    daly_age = daly_age[daly_age["cause_group"].notna()]

    rows = []
    for cg in ["CMNN", "NCD"]:
        sub = daly_age[daly_age["cause_group"] == cg]
        rate_wide = sub.pivot_table(
            index="age_name", columns="year", values="val"
        ).reindex(age_groups)
        # GBD rates are per 100k — convert to per-person for DALY totals
        r1990 = (rate_wide[1990] / 1e5).values
        r2023 = (rate_wide[2023] / 1e5).values
        p1990 = pop_wide[1990].values
        p2023 = pop_wide[2023].values
        decomp = das_gupta_decomposition(p1990, r1990, p2023, r2023)
        rows.append({"cause_group": cg, **decomp})

    tbl = pd.DataFrame(rows)
    tbl["direction"] = np.where(tbl["observed_change"] >= 0, "increase", "decrease")
    tbl.to_csv(TAB / "decomposition_results.csv", index=False)

    print("  Observed vs decomposed change in total DALYs (Vietnam):")
    show = tbl[["cause_group", "pop_size", "age_structure",
                "age_rate", "total_decomp", "observed_change", "direction"]]
    print(show.to_string(index=False, float_format="%.0f"))
    print("  --> tables/decomposition_results.csv")
    return tbl


# =============================================================================
# SECTION 5 - SEA COMPARISON
# =============================================================================

def section5_sea(data, metrics):
    print("\n" + "=" * 70)
    print("SECTION 5 - SEA Comparison")
    print("=" * 70)

    snapshot_years = [1990, 2000, 2010, 2023]
    snap = (metrics[metrics["year"].isin(snapshot_years)]
            [["country", "year", "ncd_share_pct"]]
            .pivot(index="country", columns="year",
                   values="ncd_share_pct"))
    snap.columns = [f"ncd_share_{y}" for y in snap.columns]
    snap["delta_ncd_share_pp"] = (
        snap["ncd_share_2023"] - snap["ncd_share_1990"]
    )

    # SDI-expected NCD share (quadratic fit, Vietnam excluded). Annotates
    # Vietnam's observed/expected ratio for 2023.
    # Lim SS et al. Lancet 2018;392:2091-138.
    sdi = data["sdi"]
    m23 = metrics[metrics["year"] == 2023].merge(
        sdi[sdi["year"] == 2023][["location_name", "sdi"]],
        on="location_name", how="left",
    )
    fit = m23[(m23["country"] != "Vietnam")
              & m23["sdi"].notna() & m23["ncd_share_pct"].notna()]
    ratios = {}
    if len(fit) >= 3:
        coef = np.polyfit(fit["sdi"].values,
                          fit["ncd_share_pct"].values, 2)
        for _, row in m23.iterrows():
            if pd.isna(row["sdi"]):
                continue
            exp = float(np.polyval(coef, row["sdi"]))
            obs = float(row["ncd_share_pct"])
            ratios[row["country"]] = obs / exp if exp else np.nan
    snap["obs_vs_expected_ratio_2023"] = (
        snap.index.map(ratios.get).astype(float)
    )

    sea = snap.reset_index().sort_values("ncd_share_2023", ascending=False)
    sea.to_csv(TAB / "sea_comparison.csv", index=False)

    print("  SEA countries ranked by NCD share of total DALYs, 2023:")
    print(sea[["country", "ncd_share_1990", "ncd_share_2023",
               "delta_ncd_share_pp", "obs_vs_expected_ratio_2023"]]
          .to_string(index=False, float_format="%.3f"))
    print("  --> tables/sea_comparison.csv")
    return sea


# =============================================================================
# SECTION 6 - FIGURES
# =============================================================================

def figure_1(data, metrics):
    """2x2 overview panel for Vietnam."""
    print("\n  Figure 1 - 2x2 Overview Panel (Vietnam)")
    q1 = data["q1"]
    vn = q1[
        (q1["location_name"] == "Vietnam")
        & (q1["measure_name"] == DALY_LABEL)
        & (q1["sex_name"] == "Both")
    ].copy()

    num_aa = vn[(vn["metric_name"] == "Number") & (vn["age_name"] == "All ages")]
    rate_as = vn[(vn["metric_name"] == "Rate") & (vn["age_name"] == "Age-standardized")]

    num_pvt = num_aa.pivot_table(index="year", columns="cause_group", values="val")
    rate_pvt = rate_as.pivot_table(index="year", columns="cause_group", values="val")
    rate_lo = rate_as.pivot_table(index="year", columns="cause_group", values="lower")
    rate_hi = rate_as.pivot_table(index="year", columns="cause_group", values="upper")
    for df in (num_pvt, rate_pvt, rate_lo, rate_hi):
        for col in ["CMNN", "NCD", "Injuries"]:
            if col not in df.columns:
                df[col] = np.nan

    years = num_pvt.index.values
    cmnn = num_pvt["CMNN"].values
    ncd = num_pvt["NCD"].values
    inj = num_pvt["Injuries"].values
    total = cmnn + ncd + inj

    fig, axes = plt.subplots(2, 2, figsize=(W2, W2 * 0.70))

    # Panel A: absolute DALYs stacked
    ax = axes[0, 0]
    ax.stackplot(years, cmnn / 1e6, ncd / 1e6, inj / 1e6,
                 labels=["CMNN", "NCD", "Injuries"],
                 colors=[PALETTE["CMNN"], PALETTE["NCD"], PALETTE["Injuries"]],
                 alpha=0.85)
    ax.set_title("A. Absolute DALYs by cause group, Vietnam")
    ax.set_xlabel("Year")
    ax.set_ylabel("DALYs (millions)")
    ax.legend(loc="upper right", frameon=False)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)

    # Panel B: % contribution stacked
    ax = axes[0, 1]
    ax.stackplot(years, cmnn / total * 100, ncd / total * 100, inj / total * 100,
                 labels=["CMNN", "NCD", "Injuries"],
                 colors=[PALETTE["CMNN"], PALETTE["NCD"], PALETTE["Injuries"]],
                 alpha=0.85)
    ax.set_title("B. % contribution of each group, Vietnam")
    ax.set_xlabel("Year")
    ax.set_ylabel("% of total DALYs")
    ax.set_ylim(0, 100)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)
    ax.legend(loc="center right", frameon=False)

    # Panel C: Age-std DALY rates with UI
    ax = axes[1, 0]
    for g, color in [("CMNN", PALETTE["CMNN"]), ("NCD", PALETTE["NCD"]),
                     ("Injuries", PALETTE["Injuries"])]:
        ax.plot(rate_pvt.index, rate_pvt[g], color=color, lw=2, label=g)
        shade_ui(ax, rate_pvt.index, rate_lo[g], rate_hi[g], color=color)
    ax.set_title("C. Age-standardized DALY rate, Vietnam")
    ax.set_xlabel("Year")
    ax.set_ylabel("DALYs per 100,000")
    ax.legend(frameon=False)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)

    # Panel D: NCD share of total DALYs
    # share = NCD age-std DALYs / (CMNN + NCD + Injuries) x 100.
    ax = axes[1, 1]
    vn_metrics = metrics[metrics["country"] == "Vietnam"].sort_values("year")
    ax.plot(vn_metrics["year"], vn_metrics["ncd_share_pct"],
            color=PALETTE["NCD"], lw=2.2, label="NCD share (%), Vietnam")
    ax.axhline(50, color=PALETTE["neutral"], ls=":", lw=1, label="50% reference")
    ax.set_ylim(0, 100)
    ax.set_title("D. NCD share of total DALYs, Vietnam")
    ax.set_xlabel("Year")
    ax.set_ylabel("NCD share of total DALYs (%)")
    ax.legend(loc="lower right", frameon=False)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)

    fig.tight_layout()
    save_fig(fig, "figure1_overview")
    plt.close(fig)


def figure_2(data):
    """Heatmap of top-15 Vietnam causes (age-std DALY rate)."""
    print("  Figure 2 - Top-15 cause heatmap (Vietnam)")
    det = pd.concat([data["q2a"], data["q2b"]], ignore_index=True)
    det = det[
        (det["measure_name"] == DALY_LABEL)
        & (det["metric_name"] == "Rate")
        & (det["age_name"] == "Age-standardized")
        & (det["sex_name"] == "Both")
        & (~det["cause_name"].isin([CMNN_LABEL, NCD_LABEL]))
    ].copy()

    latest = det[det["year"] == 2023]
    top15 = (latest.sort_values("val", ascending=False)
             .drop_duplicates("cause_name")["cause_name"].head(15).tolist())

    years_plot = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]
    mat = (det[det["cause_name"].isin(top15) & det["year"].isin(years_plot)]
           .pivot_table(index="cause_name", columns="year", values="val")
           .reindex(top15))

    rel = mat.div(mat[1990], axis=0)
    fig, ax = plt.subplots(figsize=(W2, W2 * 0.62))
    cmap = plt.get_cmap("RdBu_r")
    vmax = float(np.nanmax(np.abs(rel - 1)))
    im = ax.imshow(rel.values, aspect="auto", cmap=cmap,
                   vmin=1 - vmax, vmax=1 + vmax, interpolation="nearest")
    ax.set_xticks(range(len(years_plot)))
    ax.set_xticklabels(years_plot)
    def wrap(s, maxw=40):
        return s if len(s) < maxw else s[:maxw - 1] + "..."
    ax.set_yticks(range(len(top15)))
    ax.set_yticklabels([wrap(c) for c in top15])
    ax.set_title("Age-standardized DALY rate relative to 1990 "
                 "(Vietnam, top 15 causes by 2023 rate)")
    for i in range(len(top15)):
        for j in range(len(years_plot)):
            v = mat.iloc[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=7, color="black")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Rate ratio vs 1990")
    fig.tight_layout()
    save_fig(fig, "figure2_heatmap")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2 v2 — Lancet RH-WP rebuild: 2-panel heatmap with group indicator,
# log-scaled absolute rate (Panel A) and log2-ratio % change (Panel B).
# ---------------------------------------------------------------------------

# Short labels for cause names. Include the Lancet-style level-3 keys
# requested by the task (forward-compatible if future queries include them)
# AND the level-2 labels actually present in query2a_cmnn / query2b_ncd.
# Any cause not matched is truncated to 25 characters.
SHORT_NAMES_V2 = {
    # Level-3 (forward-compat; not present in the current level-2 extract)
    "Ischemic heart disease": "IHD",
    "Stroke": "Stroke",
    "Chronic obstructive pulmonary disease": "COPD",
    "Lower respiratory infections": "LRI",
    "Tracheal, bronchus, and lung cancer": "Lung cancer",
    "Diabetes mellitus type 2": "T2DM",
    "Chronic kidney disease": "CKD",
    "Alzheimer's disease and other dementias": "Dementia",
    "Neonatal disorders": "Neonatal",
    "Diarrheal diseases": "Diarrhea",
    "Tuberculosis": "TB",
    "HIV/AIDS": "HIV/AIDS",
    "Road injuries": "Road injuries",
    "Self-harm": "Self-harm",
    "Protein-energy malnutrition": "PEM",
    # Level-2 labels present in query2a/query2b (CMNN then NCD)
    "Enteric infections": "Enteric inf.",
    "HIV/AIDS and sexually transmitted infections": "HIV/AIDS & STIs",
    "Maternal and neonatal disorders": "Maternal/neonatal",
    "Neglected tropical diseases and malaria": "NTDs & malaria",
    "Nutritional deficiencies": "Nutritional def.",
    "Other infectious diseases": "Other infections",
    "Respiratory infections and tuberculosis": "Resp. inf. & TB",
    "Cardiovascular diseases": "Cardiovascular",
    "Chronic respiratory diseases": "Chronic resp.",
    "Diabetes and kidney diseases": "Diabetes & CKD",
    "Digestive diseases": "Digestive",
    "Mental disorders": "Mental disorders",
    "Musculoskeletal disorders": "Musculoskeletal",
    "Neoplasms": "Neoplasms",
    "Neurological disorders": "Neurological",
    "Other non-communicable diseases": "Other NCDs",
    "Sense organ diseases": "Sense organ",
    "Skin and subcutaneous diseases": "Skin/subcut.",
    "Substance use disorders": "Substance use",
}

# Group color patches (left margin). Colour-blind-safe blue / red / neutral grey.
GROUP_COLOR_V2 = {
    "CMNN":     "#1F77B4",   # blue
    "NCD":      "#C1272D",   # red
    "Injuries": "#7F7F7F",   # grey
}


def figure_2_v2(data):
    """Two-panel cause heatmap for Vietnam, 1990-2023 (Lancet RH-WP rebuild).

    Panel A — absolute age-standardized DALY rates (viridis, LogNorm 10-5000),
    cells labelled with the absolute rate.
    Panel B — log2 ratio of each year's rate to the 1990 rate
    (RdBu_r, TwoSlopeNorm centred at 0), cells labelled with the % change
    versus 1990 and hatched where the 95% UI of the ratio spans 1.0.

    Row selection: union of the 10 highest-rate causes in 1990 and in 2023,
    excluding aggregate groups. Left-margin colour patches indicate the
    level-1 cause group (CMNN / NCD / Injuries).

    Outputs
    -------
    figures/static/fig2_heatmap_v2.png (300 DPI), .svg, and fig2_caption.txt.
    """
    from matplotlib.colors import LogNorm, TwoSlopeNorm
    from matplotlib.patches import Rectangle, Patch as MplPatch
    import subprocess

    print("\n  Figure 2 v2 - Two-panel top-cause heatmap (Vietnam)")

    # Excluded aggregates
    exclude = {CMNN_LABEL, NCD_LABEL, INJ_LABEL, "All causes"}
    det = pd.concat([data["q2a"], data["q2b"]], ignore_index=True)
    det = det[(det["measure_name"] == DALY_LABEL)
              & (det["metric_name"] == "Rate")
              & (det["age_name"] == "Age-standardized")
              & (det["sex_name"] == "Both")
              & (~det["cause_name"].isin(exclude))].copy()

    # --- Union of top-10 in 1990 and 2023 (de-duplicated, order preserved) --
    def top10(year):
        return (det[det["year"] == year]
                .sort_values("val", ascending=False)
                .drop_duplicates("cause_name")["cause_name"]
                .head(10).tolist())
    causes = list(dict.fromkeys(top10(1990) + top10(2023)))
    n_causes = len(causes)

    # --- Group lookup: q2a = CMNN, q2b = NCD, else = Injuries --------------
    cmnn_set = set(data["q2a"]["cause_name"].unique())
    ncd_set = set(data["q2b"]["cause_name"].unique())

    def group_of(cause):
        if cause in cmnn_set:
            return "CMNN"
        if cause in ncd_set:
            return "NCD"
        return "Injuries"

    # Stable sort: CMNN -> NCD -> Injuries, within each by 2023 rate desc
    def _sort_key(c):
        rate_2023 = (det[(det["cause_name"] == c) & (det["year"] == 2023)]
                     ["val"].iloc[0])
        return ({"CMNN": 0, "NCD": 1, "Injuries": 2}[group_of(c)], -rate_2023)
    causes = sorted(causes, key=_sort_key)
    groups = [group_of(c) for c in causes]

    # --- Build value + UI matrices -----------------------------------------
    years = [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023]
    mat_val = np.full((n_causes, len(years)), np.nan)
    mat_lo = np.full_like(mat_val, np.nan)
    mat_hi = np.full_like(mat_val, np.nan)
    for i, c in enumerate(causes):
        for j, y in enumerate(years):
            sub = det[(det["cause_name"] == c) & (det["year"] == y)]
            if len(sub):
                mat_val[i, j] = sub["val"].iloc[0]
                mat_lo[i, j] = sub["lower"].iloc[0]
                mat_hi[i, j] = sub["upper"].iloc[0]

    # Ratio vs 1990 and its 95% UI (conservative, independent-UI approx)
    base = mat_val[:, :1]
    base_lo = mat_lo[:, :1]
    base_hi = mat_hi[:, :1]
    ratio_val = mat_val / base
    ratio_lo = mat_lo / base_hi  # lower of ratio
    ratio_hi = mat_hi / base_lo  # upper of ratio

    # --- Short labels -------------------------------------------------------
    def short(c):
        if c in SHORT_NAMES_V2:
            return SHORT_NAMES_V2[c]
        return c if len(c) <= 25 else (c[:24] + "…")
    labels = [short(c) for c in causes]

    # --- Figure -------------------------------------------------------------
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
    })
    MM = 1 / 25.4
    row_h_mm = 8.0     # 8mm per row
    header_mm = 35.0   # title + top margin
    footer_mm = 45.0   # colorbars + legend + bottom margin
    fig_h_in = (header_mm + row_h_mm * n_causes + footer_mm) * MM
    fig_w_in = 180 * MM
    fig, axes = plt.subplots(1, 2, figsize=(fig_w_in, fig_h_in),
                             gridspec_kw=dict(wspace=0.50))

    # Panel A: absolute rates, viridis, LogNorm ------------------------------
    normA = LogNorm(vmin=10, vmax=5000)
    axA = axes[0]
    imA = axA.imshow(mat_val, aspect="auto", cmap="viridis", norm=normA,
                     interpolation="nearest")
    axA.set_xticks(range(len(years)))
    axA.set_xticklabels(years, fontsize=8)
    axA.set_yticks(range(n_causes))
    axA.set_yticklabels(labels, fontsize=8)
    axA.tick_params(axis="x", length=2)
    axA.tick_params(axis="y", length=2)
    axA.set_title("A. Age-standardized DALY rate (per 100,000)",
                  fontsize=11, fontweight="bold", loc="left")

    def _fmt_rate(v):
        """Compact cell label: <100 one-decimal, <1000 integer, otherwise 'X.Xk'."""
        if v < 100:
            return f"{v:.1f}"
        if v < 1000:
            return f"{v:.0f}"
        return f"{v/1000:.1f}k"

    for i in range(n_causes):
        for j in range(len(years)):
            v = mat_val[i, j]
            if np.isnan(v):
                continue
            # Contrast: light text on dark viridis (low rate), dark on yellow
            log_mid = np.log10(300)  # perceptual midpoint on vmin=10, vmax=5000
            tcolor = "black" if np.log10(max(v, 1)) > log_mid else "white"
            axA.text(j, i, _fmt_rate(v), ha="center", va="center",
                     fontsize=6.5, color=tcolor)

    # Panel B: log2 ratio vs 1990, RdBu_r, symmetric TwoSlopeNorm ------------
    normB = TwoSlopeNorm(vcenter=0.0, vmin=-2.0, vmax=2.0)
    axB = axes[1]
    log2_ratio = np.log2(np.where(ratio_val > 0, ratio_val, np.nan))
    imB = axB.imshow(log2_ratio, aspect="auto", cmap="RdBu_r", norm=normB,
                     interpolation="nearest")
    axB.set_xticks(range(len(years)))
    axB.set_xticklabels(years, fontsize=8)
    axB.set_yticks(range(n_causes))
    axB.set_yticklabels(labels, fontsize=8)
    axB.tick_params(axis="x", length=2)
    axB.tick_params(axis="y", length=2)
    axB.set_title(r"B. Change vs 1990 ($\log_2$ ratio)",
                  fontsize=11, fontweight="bold", loc="left")

    n_hatched = 0
    for i in range(n_causes):
        for j in range(len(years)):
            r = ratio_val[i, j]
            if np.isnan(r) or r <= 0:
                continue
            lo, hi = ratio_lo[i, j], ratio_hi[i, j]
            ui_spans_unity = (not np.isnan(lo) and not np.isnan(hi)
                              and lo <= 1.0 <= hi)
            if ui_spans_unity:
                axB.add_patch(Rectangle(
                    (j - 0.5, i - 0.5), 1, 1,
                    fill=False, hatch="///", edgecolor="#444444",
                    linewidth=0.2, alpha=0.4,
                ))
                n_hatched += 1
            # Text: darker where |log2 ratio| is small (near white cell)
            abs_l2 = abs(np.log2(r))
            tcolor = "black" if abs_l2 < 0.8 else "white"
            axB.text(j, i, f"{r - 1:+.0%}", ha="center", va="center",
                     fontsize=6.5, color=tcolor,
                     alpha=0.75 if ui_spans_unity else 1.0)

    # --- Left-margin group patches (4mm wide) -------------------------------
    # Convert 4mm to data units (approximated using axes display size).
    for ax in (axA, axB):
        # Place patches just outside the axes to the left. In data-coords for
        # a heatmap with x ranging [-0.5, n_years-0.5], use x = -1.2 .. -0.6.
        for i, g in enumerate(groups):
            ax.add_patch(Rectangle(
                (-1.2, i - 0.48), 0.6, 0.96,
                facecolor=GROUP_COLOR_V2[g], edgecolor="none",
                clip_on=False, zorder=5,
            ))
        ax.set_xlim(-1.5, len(years) - 0.5)

    # --- Colorbars (horizontal, below each panel) ---------------------------
    cbA = fig.colorbar(imA, ax=axA, orientation="horizontal",
                       pad=0.14, shrink=0.9, aspect=25)
    cbA.set_label("DALY rate per 100,000 (log scale)", fontsize=8)
    cbA.ax.tick_params(labelsize=7)

    cbB = fig.colorbar(imB, ax=axB, orientation="horizontal",
                       pad=0.14, shrink=0.9, aspect=25,
                       ticks=[-2, -1, 0, 1, 2])
    cbB.set_label(r"$\log_2$(rate / rate$_{1990}$)", fontsize=8)
    cbB.ax.tick_params(labelsize=7)
    cbB.ax.set_xticklabels(["−75%", "−50%", "0%",
                            "+100%", "+300%"])

    # Legend (hatch + group patches)
    legend_handles = [
        MplPatch(facecolor="white", hatch="///", edgecolor="#444444",
                 label="hatched: 95% UI spans 1.0"),
        MplPatch(facecolor=GROUP_COLOR_V2["CMNN"], label="CMNN"),
        MplPatch(facecolor=GROUP_COLOR_V2["NCD"], label="NCD"),
        MplPatch(facecolor=GROUP_COLOR_V2["Injuries"], label="Injuries"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=4,
               frameon=False, bbox_to_anchor=(0.5, 0.005), fontsize=8)

    # Save --------------------------------------------------------------------
    out_dir = ROOT / "figures" / "static"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "fig2_heatmap_v2.png"
    svg_path = out_dir / "fig2_heatmap_v2.svg"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {png_path.relative_to(ROOT)} + .svg")

    # Caption -----------------------------------------------------------------
    caption = (
        f"Figure 2. Age-standardized DALY rate heatmap for the top causes of "
        f"disability-adjusted life years in Vietnam, 1990-2023.\n"
        f"Rows (n={n_causes}) are the union of the ten highest-ranked causes by "
        f"age-standardized DALY rate in 1990 and in 2023, restricted to GBD "
        f"level-2 causes and excluding the aggregate groups Communicable / "
        f"maternal / neonatal / nutritional diseases, Non-communicable diseases, "
        f"Injuries and All causes.\n"
        f"Rates are age-standardized to the GBD 2010 world standard population "
        f"and expressed per 100,000 person-years.\n"
        f"Panel A shows absolute DALY rate on a log colour scale (viridis, "
        f"vmin=10, vmax=5,000 per 100,000); cell labels report the absolute rate. "
        f"Panel B shows the log₂ ratio of each year's rate to the 1990 rate "
        f"on a diverging colour scale (RdBu_r, TwoSlopeNorm centred at 0, "
        f"vmin=−2, vmax=+2); cell labels report the percentage change vs 1990. "
        f"Hatched cells in Panel B indicate years whose 95% uncertainty interval "
        f"on the ratio spans 1.0 (no detectable change at α=0.05 under the "
        f"independent-UI approximation, using rate_low/rate_high_1990 and "
        f"rate_high/rate_low_1990 as the ratio UI bounds).\n"
        f"Left-margin colour patches indicate the level-1 cause group: "
        f"CMNN (blue), NCD (red), Injuries (grey)."
    )
    (out_dir / "fig2_caption.txt").write_text(caption + "\n", encoding="utf-8")
    print()
    print("CAPTION:")
    # Console may be cp1252 on Windows; emit ASCII-safe substitutions for
    # the printed copy. The .txt file keeps the full unicode form.
    console_caption = (caption
                       .replace("log₂", "log2")
                       .replace("α", "alpha")
                       .replace("₁₉₉₀", "_1990")
                       .replace("−", "-"))
    print(console_caption)
    print()

    # Console summary --------------------------------------------------------
    print(f"Selected {n_causes} causes (union of top-10 in 1990 and 2023):")
    for c in causes:
        print(f"  [{group_of(c):<8}] {short(c):<22} <- {c}")

    pct_change = ratio_val[:, -1] - 1.0
    order = np.argsort(pct_change)
    print("\n3 largest decreases 1990->2023 (% change):")
    for i in order[:3]:
        print(f"  {short(causes[i]):<22} {pct_change[i]:+.0%}")
    print("\n3 largest increases 1990->2023 (% change):")
    for i in order[::-1][:3]:
        print(f"  {short(causes[i]):<22} {pct_change[i]:+.0%}")

    print(f"\nPanel B: {n_hatched} cells hatched "
          f"(95% UI spans 1.0 -> not significantly different from 1990)")
    print(f"Panel A rendered rate range: "
          f"min={np.nanmin(mat_val):,.1f}, max={np.nanmax(mat_val):,.1f} "
          f"per 100,000 (colour clipped to [{normA.vmin}, {normA.vmax}])")

    # Verify the PNG via `file` (bash GNU file / git-bash on Windows) --------
    try:
        res = subprocess.run(["file", str(png_path)],
                             capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout.strip():
            print(f"\nfile(1): {res.stdout.strip()}")
        else:
            print(f"\nfile(1): {res.stderr.strip() or 'empty output'}")
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"\n  `file` command unavailable ({type(e).__name__})")


def figure_3(decomp):
    """Waterfall decomposition chart."""
    print("  Figure 3 - Decomposition waterfall")
    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.45))

    for ax, cg in zip(axes, ["NCD", "CMNN"]):
        row = decomp[decomp["cause_group"] == cg].iloc[0]
        components = [
            ("Population size", row["pop_size"]),
            ("Age structure", row["age_structure"]),
            ("Age-specific rate", row["age_rate"]),
        ]
        values = [v / 1e6 for _, v in components]
        total = sum(values)
        labels = [n for n, _ in components]

        running = 0
        bottom, heights, colors = [], [], []
        for v in values:
            if v >= 0:
                bottom.append(running)
                heights.append(v)
                colors.append(PALETTE["Injuries"])
            else:
                bottom.append(running + v)
                heights.append(-v)
                colors.append(PALETTE["CMNN"])
            running += v

        ax.bar(labels, heights, bottom=bottom, color=colors, alpha=0.85,
               edgecolor="black", lw=0.5)
        ax.bar("Net change", abs(total), bottom=0 if total >= 0 else total,
               color=PALETTE["NCD"] if cg == "NCD" else PALETTE["CMNN"],
               alpha=0.9, edgecolor="black", lw=0.5)
        for i, v in enumerate(values):
            top_y = bottom[i] + heights[i]
            ax.text(i, top_y, f"{v:+.1f}M",
                    ha="center", va="bottom" if v >= 0 else "top", fontsize=8)
        ax.text(3, total, f"{total:+.1f}M",
                ha="center", va="bottom" if total >= 0 else "top",
                fontsize=9, fontweight="bold")
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title(f"{cg} DALY change 1990-2023")
        ax.set_ylabel("DALYs (millions)")
        ax.tick_params(axis="x", rotation=20)

    fig.suptitle("Das Gupta decomposition of DALY change, Vietnam", fontsize=11)
    fig.tight_layout()
    save_fig(fig, "figure3_decomposition")
    plt.close(fig)


def figure_4(metrics, sdi_df):
    """SEA NCD-share trajectories + SDI vs NCD share scatter.
    Lim SS et al. Lancet 2018;392:2091-138 (SDI-expected method).
    """
    print("  Figure 4 - SEA NCD share comparison")
    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.55))

    # NCD-share trajectories
    ax = axes[0]
    for country in SEA_COUNTRIES:
        sub = metrics[metrics["location_name"] == country].sort_values("year")
        disp = COUNTRY_DISPLAY.get(country, country)
        if country == "Vietnam":
            ax.plot(sub["year"], sub["ncd_share_pct"],
                    color=PALETTE["Vietnam"], lw=2.5, label="Vietnam", zorder=10)
        else:
            ax.plot(sub["year"], sub["ncd_share_pct"],
                    color=PALETTE["neutral"], lw=1, alpha=0.7, label=disp)
    ax.axhline(50, color="black", ls=":", lw=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("NCD share of total DALYs (%)")
    ax.set_title("NCD share trajectories, 11 SEA countries")
    ax.set_ylim(0, 100)
    ax.set_xlim(YEAR_MIN, YEAR_MAX)

    # End-of-line labels, pushed apart vertically to avoid overlap
    ends = []
    for country in SEA_COUNTRIES:
        sub = metrics[metrics["location_name"] == country].sort_values("year")
        if len(sub):
            ends.append((country, float(sub["ncd_share_pct"].iloc[-1])))
    ends.sort(key=lambda t: t[1])
    min_gap = 2.8  # percentage points
    adjusted = []
    for i, (c, y) in enumerate(ends):
        if i == 0:
            adjusted.append((c, y))
        else:
            prev_y = adjusted[-1][1]
            adjusted.append((c, max(y, prev_y + min_gap)))
    for country, y_text in adjusted:
        sub = metrics[metrics["location_name"] == country].sort_values("year")
        disp = COUNTRY_DISPLAY.get(country, country)
        y_end = float(sub["ncd_share_pct"].iloc[-1])
        col = PALETTE["Vietnam"] if country == "Vietnam" else PALETTE["neutral"]
        ax.annotate(
            disp, xy=(YEAR_MAX, y_end), xytext=(YEAR_MAX + 0.8, y_text),
            fontsize=7, color=col, va="center",
            arrowprops=dict(arrowstyle="-", color=col, lw=0.3,
                            shrinkA=0, shrinkB=0, alpha=0.7),
        )
    ax.set_xlim(YEAR_MIN, YEAR_MAX + 7)

    # SDI vs NCD share scatter + quadratic fit excluding Vietnam
    ax = axes[1]
    merged = metrics.merge(
        sdi_df[["location_name", "year", "sdi"]],
        on=["location_name", "year"], how="left",
    )
    for country in SEA_COUNTRIES:
        sub = merged[merged["location_name"] == country].sort_values("year")
        if country == "Vietnam":
            ax.plot(sub["sdi"], sub["ncd_share_pct"],
                    color=PALETTE["Vietnam"], lw=2.5, label="Vietnam", zorder=10)
            ax.scatter(sub["sdi"].iloc[0], sub["ncd_share_pct"].iloc[0],
                       color=PALETTE["Vietnam"], s=35, edgecolor="black",
                       zorder=11, label="1990")
            ax.scatter(sub["sdi"].iloc[-1], sub["ncd_share_pct"].iloc[-1],
                       color=PALETTE["Vietnam"], s=80, marker="*",
                       edgecolor="black", zorder=11, label="2023")
        else:
            ax.plot(sub["sdi"], sub["ncd_share_pct"],
                    color=PALETTE["neutral"], lw=0.9, alpha=0.55)

    fit_data = merged[(merged["location_name"] != "Vietnam")
                      & merged["sdi"].notna() & merged["ncd_share_pct"].notna()]
    x = fit_data["sdi"].values
    y = fit_data["ncd_share_pct"].values
    if len(x) >= 3:
        coef = np.polyfit(x, y, 2)
        xline = np.linspace(x.min(), x.max(), 100)
        yline = np.polyval(coef, xline)
        ax.plot(xline, yline, color="black", ls="--", lw=1.3,
                label="SEA expected (quadratic, VN excluded)")
        # Annotate Vietnam 2023 observed/expected ratio
        vn23 = merged[(merged["location_name"] == "Vietnam")
                      & (merged["year"] == 2023)]
        if not vn23.empty:
            sdi23 = float(vn23["sdi"].iloc[0])
            obs = float(vn23["ncd_share_pct"].iloc[0])
            exp = float(np.polyval(coef, sdi23))
            ratio = obs / exp if exp else np.nan
            ax.annotate(
                f"VN obs/exp 2023 = {ratio:.3f}",
                xy=(sdi23, obs), xytext=(sdi23 - 0.08, obs + 12),
                fontsize=8, color=PALETTE["Vietnam"],
                arrowprops=dict(arrowstyle="->", color=PALETTE["Vietnam"],
                                lw=0.8, shrinkA=0, shrinkB=2),
            )
    ax.set_xlabel("Socio-Demographic Index (SDI)")
    ax.set_ylabel("NCD share of total DALYs (%)")
    ax.set_title("SDI vs NCD share, SEA (Vietnam highlighted)")
    ax.set_ylim(0, 100)
    ax.legend(loc="lower right", frameon=False, fontsize=8)

    fig.tight_layout()
    save_fig(fig, "figure4_sea_comparison")
    plt.close(fig)


def figure_5(data):
    """Age-sex pyramid 1990 vs 2023, CMNN vs NCD burden."""
    print("  Figure 5 - Age-sex pyramid shift")
    q3 = data["q3"]
    age_groups = [
        "<5 years", "5-9 years", "10-14 years", "15-19 years", "20-24 years",
        "25-29 years", "30-34 years", "35-39 years", "40-44 years",
        "45-49 years", "50-54 years", "55-59 years", "60-64 years",
        "65-69 years", "70-74 years", "75-79 years", "80+ years",
    ]
    groups_map = {CMNN_LABEL: "CMNN", NCD_LABEL: "NCD"}
    sub = q3[
        (q3["measure_name"] == DALY_LABEL)
        & (q3["metric_name"] == "Number")
        & (q3["sex_name"].isin(["Male", "Female"]))
        & (q3["age_name"].isin(age_groups))
        & (q3["cause_name"].isin(groups_map.keys()))
        & (q3["year"].isin([1990, 2023]))
    ].copy()
    sub["cause_group"] = sub["cause_name"].map(groups_map)

    fig, axes = plt.subplots(1, 2, figsize=(W2, W2 * 0.55),
                             sharey=True, sharex=True)

    panels = {}
    global_xmax = 0.0
    for yr in [1990, 2023]:
        pv = sub[sub["year"] == yr].pivot_table(
            index="age_name", columns=["sex_name", "cause_group"],
            values="val", aggfunc="sum",
        ).reindex(age_groups)
        m_cmnn = -(pv[("Male", "CMNN")].values / 1e6)
        m_ncd = -(pv[("Male", "NCD")].values / 1e6)
        f_cmnn = pv[("Female", "CMNN")].values / 1e6
        f_ncd = pv[("Female", "NCD")].values / 1e6
        panels[yr] = (m_cmnn, m_ncd, f_cmnn, f_ncd)
        global_xmax = max(global_xmax, float(np.nanmax(np.abs(
            np.concatenate([m_cmnn + m_ncd, f_cmnn + f_ncd])))))

    for ax, yr in zip(axes, [1990, 2023]):
        m_cmnn, m_ncd, f_cmnn, f_ncd = panels[yr]
        ys = np.arange(len(age_groups))
        ax.barh(ys, m_cmnn, color=PALETTE["CMNN"], alpha=0.9,
                edgecolor="white", lw=0.4)
        ax.barh(ys, m_ncd, left=m_cmnn, color=PALETTE["NCD"], alpha=0.9,
                edgecolor="white", lw=0.4)
        ax.barh(ys, f_cmnn, color=PALETTE["CMNN"], alpha=0.9,
                edgecolor="white", lw=0.4)
        ax.barh(ys, f_ncd, left=f_cmnn, color=PALETTE["NCD"], alpha=0.9,
                edgecolor="white", lw=0.4)
        ax.axvline(0, color="black", lw=0.6)
        ax.set_yticks(ys)
        ax.set_yticklabels(age_groups)
        ax.set_title(f"{yr}")
        ax.set_xlabel("DALYs (millions)  -  male (left) / female (right)")
        ax.set_xlim(-global_xmax * 1.05, global_xmax * 1.05)
        ax.xaxis.set_major_formatter(
            mpl.ticker.FuncFormatter(lambda v, _: f"{abs(v):.1f}")
        )

    handles = [
        Patch(color=PALETTE["CMNN"], label="CMNN"),
        Patch(color=PALETTE["NCD"], label="NCD"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2,
               frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.suptitle("Vietnam DALY burden by age, sex and cause group: 1990 vs 2023",
                 fontsize=11, y=1.06)
    fig.tight_layout()
    save_fig(fig, "figure5_age_sex_pyramid")
    plt.close(fig)


def section6_figures(data, metrics, decomp, sdi_df):
    print("\n" + "=" * 70)
    print("SECTION 6 - Figures")
    print("=" * 70)
    figure_1(data, metrics)
    figure_2(data)
    figure_2_v2(data)
    figure_3(decomp)
    figure_4(metrics, sdi_df)
    figure_5(data)


# =============================================================================
# SECTION 7 - SUMMARY TABLE
# =============================================================================

def section7_summary(data, metrics, trends):
    print("\n" + "=" * 70)
    print("SECTION 7 - Summary Table")
    print("=" * 70)

    q1_asr = data["q1_asr"]
    vn = q1_asr[
        (q1_asr["location_name"] == "Vietnam")
        & (q1_asr["measure_name"] == DALY_LABEL)
        & (q1_asr["metric_name"] == "Rate")
        & (q1_asr["sex_name"] == "Both")
    ].copy()
    pvt = vn.pivot_table(index="year", columns="cause_group", values="val")

    years = [1990, 2000, 2010, 2023]
    aapc_by_group = (trends[trends["country"] == "Vietnam"]
                     .drop_duplicates("cause_group")
                     .set_index("cause_group")["aapc_pct_1990_2023"])
    vn_m = metrics[metrics["country"] == "Vietnam"].set_index("year")

    rows = []
    for g in ["CMNN", "NCD", "Injuries"]:
        r = {"metric": f"{g} age-std DALY rate (per 100k)"}
        for y in years:
            r[str(y)] = round(pvt.loc[y, g], 1) if y in pvt.index else np.nan
        r["AAPC_%"] = round(aapc_by_group.get(g, np.nan), 2)
        rows.append(r)

    for col, label in [
        ("cmnn_share_pct", "CMNN share of total DALYs (%)"),
        ("ncd_share_pct", "NCD share of total DALYs (%)"),
        ("injuries_share_pct", "Injuries share of total DALYs (%)"),
        ("cmnn_ncd_ratio", "CMNN/NCD ratio"),
    ]:
        r = {"metric": label}
        for y in years:
            r[str(y)] = (round(vn_m.loc[y, col],
                               3 if "ratio" in col else 2)
                         if y in vn_m.index else np.nan)
        r["AAPC_%"] = ""
        rows.append(r)

    tbl = pd.DataFrame(rows)
    tbl.to_csv(TAB / "table1_summary.csv", index=False)
    print(tbl.to_string(index=False))
    print("  --> tables/table1_summary.csv")
    return tbl


# =============================================================================
# MAIN
# =============================================================================

def main():
    data = section1_load_clean()
    metrics = section2_core_metrics(data)
    trends = section3_trends(data)
    decomp = section4_decomposition(data)
    _ = section5_sea(data, metrics)
    section6_figures(data, metrics, decomp, data["sdi"])
    _ = section7_summary(data, metrics, trends)
    print("\nDONE.")


if __name__ == "__main__":
    main()
