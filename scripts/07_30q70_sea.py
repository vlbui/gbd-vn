"""Strict WHO SDG 3.4.1 premature-NCD-mortality probability (30q70) for the
11 SEA countries, 1990-2023.

SDG 3.4.1 defines premature NCD mortality as the unconditional probability
of a 30-year-old dying before age 70 from one of four main NCDs:
cardiovascular disease, cancer (neoplasms), diabetes (+CKD in GBD 2023),
or chronic respiratory disease. Computed from 5-year age-band death rates
per 100,000 (Both sex) via the Chiang II life-table approximation:

    q5(x) = 5 * m(x) / (1 + 2.5 * m(x))
    30q70 = 1 - prod_{x in {30,35,...,65}} (1 - q5(x))

where m(x) is the age-band death rate (deaths per person-year, i.e. rate
per 100k divided by 1e5) summed across the 4 main NCDs.

Two AAPCs are reported per country:
  - AAPC_loglin:  single-segment log-linear OLS on 30q70 vs year
                  (scipy.stats.linregress on log(q70)). Delta-method 95% CI.
  - AAPC_joinpoint: ruptures.Pelt(model='l2') with BIC penalty 2*log(n),
                    max 3 joinpoints; weighted segment APCs, SEs combined
                    in quadrature (see utils.joinpoint_aapc_pelt).

Outputs
-------
  data/processed/sea_30q70.csv        long form, one row per country-year-age
  tables/sea_30q70_summary.csv        one row per country with snapshots,
                                      deltas, and both AAPCs

References
----------
  WHO Global Action Plan for the Prevention and Control of NCDs 2013-2020.
  UN SDG Indicator 3.4.1. Chiang CL. The Life Table and Its Applications.
  Krieger 1984. Clegg LX et al. Stat Med 2009;28:3670-82 (AAPC + CI).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from scipy import stats

from utils import (
    PROC, TAB, RAW, LOC_NORMALIZE, SEA_COUNTRIES,
    ensure_dirs, joinpoint_aapc_pelt,
)


# Strict SDG 3.4.1 NCD cause list (GBD 2023 naming; diabetes is bundled
# with CKD in GBD Level-2). These four must match the raw file exactly.
SDG_NCDS = [
    "Cardiovascular diseases",
    "Neoplasms",
    "Diabetes and kidney diseases",
    "Chronic respiratory diseases",
]

AGE_BANDS = [
    "30-34 years", "35-39 years", "40-44 years", "45-49 years",
    "50-54 years", "55-59 years", "60-64 years", "65-69 years",
]

YEARS = list(range(1990, 2024))


def _q5(rate_per_100k):
    """Chiang II 5-year conditional death probability from a rate/100k."""
    m = rate_per_100k / 1e5
    return 5 * m / (1 + 2.5 * m)


def compute_30q70_country(df_country):
    """Given a country subset with columns [year, age_name, val] for Both
    sex + one or more cause rows per age band, collapse causes to total NCD
    rate, then compute 30q70 per year via the Chiang II product.
    """
    totals = (df_country.groupby(["year", "age_name"], as_index=False)["val"]
              .sum()
              .rename(columns={"val": "ncd_rate_per_100k"}))
    totals["q5"] = _q5(totals["ncd_rate_per_100k"])

    rows = []
    for y, sub in totals.groupby("year"):
        sub = sub.set_index("age_name").reindex(AGE_BANDS)
        if sub["q5"].isna().any():
            continue
        q70 = 1 - float(np.prod(1 - sub["q5"].values))
        rows.append({"year": int(y), "q30q70": q70,
                     "q30q70_pct": q70 * 100})
    return pd.DataFrame(rows), totals


def _loglin_aapc(years, q_pct):
    """Single-segment log-linear AAPC on 30q70_pct, with delta-method CI.

    AAPC% = (exp(slope) - 1) * 100
    SE(AAPC) ~ 100 * exp(slope) * SE(slope)  (delta method, linearization
              around slope for the transformation y -> (exp(y)-1)*100)
    """
    y = np.asarray(years, dtype=float)
    v = np.asarray(q_pct, dtype=float)
    mask = (v > 0) & ~np.isnan(v)
    y, v = y[mask], v[mask]
    if len(y) < 3:
        return dict(aapc=np.nan, ci_low=np.nan, ci_high=np.nan, n_obs=len(y))
    lr = stats.linregress(y, np.log(v))
    slope, stderr = float(lr.slope), float(lr.stderr)
    aapc = (np.exp(slope) - 1) * 100
    half = 1.96 * stderr * 100 * np.exp(slope)
    return dict(aapc=aapc, ci_low=aapc - half, ci_high=aapc + half,
                n_obs=int(len(y)))


def run():
    print("\n=== 07 SEA 30Q70 (strict SDG 3.4.1) ===")
    ensure_dirs()

    df = pd.read_csv(RAW / "query6_30q70.csv")
    df["location_name"] = df["location_name"].replace(LOC_NORMALIZE)

    df = df[(df["measure_name"] == "Deaths")
            & (df["metric_name"] == "Rate")
            & (df["sex_name"] == "Both")
            & (df["age_name"].isin(AGE_BANDS))
            & (df["cause_name"].isin(SDG_NCDS))
            & (df["year"].isin(YEARS))]

    missing_causes = set(SDG_NCDS) - set(df["cause_name"].unique())
    if missing_causes:
        raise RuntimeError(f"Raw file missing SDG causes: {missing_causes}")
    missing_countries = set(SEA_COUNTRIES) - set(df["location_name"].unique())
    if missing_countries:
        raise RuntimeError(f"Raw file missing SEA countries: "
                           f"{missing_countries}")

    long_rows = []
    summary_rows = []
    q_series_by_country = {}

    for country in SEA_COUNTRIES:
        sub = df[df["location_name"] == country]
        q_df, long_df = compute_30q70_country(sub)
        if q_df.empty or len(q_df) != len(YEARS):
            raise RuntimeError(f"{country}: expected {len(YEARS)} years, "
                               f"got {len(q_df)}")
        q_df.insert(0, "country", country)
        long_df.insert(0, "country", country)
        long_rows.append(long_df)
        q_series_by_country[country] = q_df.sort_values("year")

        q_years = q_df["year"].values
        q_vals = q_df["q30q70_pct"].values

        snap = {y: float(q_df[q_df["year"] == y]["q30q70_pct"].iloc[0])
                for y in (1990, 2000, 2010, 2023)}
        delta_abs = snap[2023] - snap[1990]
        rel_red_pct = (1 - snap[2023] / snap[1990]) * 100

        lin = _loglin_aapc(q_years, q_vals)
        jp = joinpoint_aapc_pelt(q_years, q_vals, max_joins=3)

        summary_rows.append({
            "country": country,
            "30q70_1990": round(snap[1990], 3),
            "30q70_2000": round(snap[2000], 3),
            "30q70_2010": round(snap[2010], 3),
            "30q70_2023": round(snap[2023], 3),
            "delta_abs": round(delta_abs, 3),
            "rel_reduction_pct": round(rel_red_pct, 2),
            "AAPC_loglin": round(lin["aapc"], 3),
            "AAPC_loglin_CI": f"{lin['ci_low']:.2f}, {lin['ci_high']:.2f}",
            "AAPC_joinpoint": round(jp["aapc"], 3),
            "AAPC_joinpoint_CI": f"{jp['ci_low']:.2f}, {jp['ci_high']:.2f}",
            "n_joinpoints": int(jp["n_bkps"]),
        })

    long_df_out = (pd.concat(long_rows, ignore_index=True)
                   [["country", "year", "age_name", "ncd_rate_per_100k", "q5"]]
                   .sort_values(["country", "year", "age_name"]))
    long_df_out.to_csv(PROC / "sea_30q70.csv", index=False)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(TAB / "sea_30q70_summary.csv", index=False)

    # ---- Verification ------------------------------------------------------
    vn = summary_df[summary_df["country"] == "Vietnam"].iloc[0]
    vn_2023 = vn["30q70_2023"]
    if not (18.5 <= vn_2023 <= 20.5):
        raise RuntimeError(f"Vietnam 30q70_2023 = {vn_2023:.3f} outside "
                           f"expected [18.5, 20.5]")

    ranked = summary_df.sort_values("30q70_2023", ascending=True).reset_index(drop=True)
    ranked["rank_ascending"] = ranked.index + 1
    vn_rank = int(ranked[ranked["country"] == "Vietnam"]["rank_ascending"].iloc[0])
    if vn_rank != 6:
        raise RuntimeError(f"Vietnam 30q70 ascending rank = {vn_rank}, "
                           f"expected 6 of 11")

    diff_loglin_jp = abs(vn["AAPC_loglin"] - vn["AAPC_joinpoint"])
    print(f"  Vietnam 30q70 1990 = {vn['30q70_1990']:.2f}%")
    print(f"  Vietnam 30q70 2023 = {vn_2023:.2f}%  (rank {vn_rank}/11 ascending)")
    print(f"  Vietnam AAPC loglin    = {vn['AAPC_loglin']:+.3f} "
          f"({vn['AAPC_loglin_CI']})")
    print(f"  Vietnam AAPC joinpoint = {vn['AAPC_joinpoint']:+.3f} "
          f"({vn['AAPC_joinpoint_CI']})  n_bkps={vn['n_joinpoints']}")
    print(f"  |AAPC_loglin - AAPC_joinpoint| = {diff_loglin_jp:.3f} pp "
          f"({'within' if diff_loglin_jp <= 0.1 else 'exceeds'} 0.1 pp)")

    print(f"  [ok] data/processed/sea_30q70.csv ({len(long_df_out)} rows)")
    print(f"  [ok] tables/sea_30q70_summary.csv ({len(summary_df)} rows)")
    return dict(summary=summary_df, long=long_df_out)


if __name__ == "__main__":
    run()
