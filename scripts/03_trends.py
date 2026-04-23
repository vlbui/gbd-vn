"""Log-linear AAPC for CMNN/NCD/Injuries DALY rates + YLL/YLD rates.

AAPC is computed over four periods: full window 1990-2023, and the three
decades 1990-2000, 2000-2010, 2010-2023. Output columns:

    cause, period, aapc, ci_low, ci_high, p_value, n_obs

Saved to tables/trend_results.csv.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from utils import (
    PROC, TAB, ensure_dirs,
    CAUSE_GROUPS, CAUSE_SHORT, MEASURE,
    get_asr, calculate_aapc, joinpoint_aapc,
)

# Sub-periods use single-segment log-linear AAPC (Clegg 2009 log-linear
# case) because ~10 yearly points per decade are too few for joinpoint
# BIC selection to be meaningful. The full 1990-2023 row uses joinpoint
# AAPC (ruptures + BIC + delta-method CI) so it matches Table 1.
PERIODS = [
    ("1990-2023", 1990, 2023, joinpoint_aapc),
    ("1990-2000", 1990, 2000, calculate_aapc),
    ("2000-2010", 2000, 2010, calculate_aapc),
    ("2010-2023", 2010, 2023, calculate_aapc),
]


def _aapc_rows(subset, label):
    """Run AAPC over all PERIODS for a year-indexed Series-like frame."""
    rows = []
    subset = subset.sort_values("year")
    for period_name, y0, y1, fn in PERIODS:
        s = subset[(subset["year"] >= y0) & (subset["year"] <= y1)]
        r = fn(s["year"].values, s["val"].values)
        rows.append({"cause": label, "period": period_name,
                     "aapc": r["aapc"], "ci_low": r["ci_low"],
                     "ci_high": r["ci_high"],
                     "p_value": r.get("p_value", float("nan")),
                     "n_obs": r.get("n_obs", len(s))})
    return rows


def run():
    print("\n=== 03 TRENDS ===")
    ensure_dirs()

    df_burden = pd.read_csv(PROC / "burden_sea.csv")
    df_yll_yld = pd.read_csv(PROC / "yll_yld_sea.csv")

    # Vietnam, age-std DALY rate, Both sex, level-1 cause groups.
    vn_asr = get_asr(df_burden[df_burden["location_name"] == "Vietnam"])
    vn_asr = vn_asr[(vn_asr["measure_name"] == MEASURE["daly"])
                    & (vn_asr["metric_name"] == "Rate")
                    & (vn_asr["sex_name"] == "Both")]

    results = []
    for full_name, short in CAUSE_SHORT.items():
        if short == "All":
            continue
        sub = vn_asr[vn_asr["cause_name"] == full_name]
        results.extend(_aapc_rows(sub, f"DALY - {short}"))

    # Vietnam YLL / YLD age-std rate, Both sex, all-cause.
    vn_yy = df_yll_yld[
        (df_yll_yld["location_name"] == "Vietnam")
        & (df_yll_yld["age_name"] == "Age-standardized")
        & (df_yll_yld["sex_name"] == "Both")
        & (df_yll_yld["metric_name"] == "Rate")
        & (df_yll_yld["cause_name"] == CAUSE_GROUPS["all"])
    ]
    for key, label in [("yll", "YLL"), ("yld", "YLD")]:
        sub = vn_yy[vn_yy["measure_name"] == MEASURE[key]]
        results.extend(_aapc_rows(sub, f"{label} rate - All causes"))

    df_results = pd.DataFrame(results)
    df_results[["aapc", "ci_low", "ci_high"]] = \
        df_results[["aapc", "ci_low", "ci_high"]].round(3)
    df_results["p_value"] = df_results["p_value"].round(6)
    df_results.to_csv(TAB / "trend_results.csv", index=False)

    # Print the full-period AAPC block
    full = df_results[df_results["period"] == "1990-2023"]
    print("  Vietnam AAPC 1990-2023:")
    for _, r in full.iterrows():
        print(f"    {r['cause']:<28} "
              f"AAPC = {r['aapc']:+.2f}% "
              f"(95% CI {r['ci_low']:+.2f}, {r['ci_high']:+.2f}; "
              f"p={r['p_value']:.2g})")
    print(f"  [ok] tables/trend_results.csv ({len(df_results)} rows)")
    return df_results


if __name__ == "__main__":
    run()
