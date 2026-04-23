"""Das Gupta decomposition of DALY change, Vietnam 1990 vs 2023.

Splits the change in total DALYs into three components:
    dDALY = population size effect + age structure effect + age-specific rate effect

Applied separately to CMNN (decrease) and NCD (increase).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from utils import PROC, TAB, ensure_dirs, CAUSE_GROUPS, MEASURE


AGE_GROUPS = [
    "<5 years", "5-9 years", "10-14 years", "15-19 years", "20-24 years",
    "25-29 years", "30-34 years", "35-39 years", "40-44 years",
    "45-49 years", "50-54 years", "55-59 years", "60-64 years",
    "65-69 years", "70-74 years", "75-79 years", "80+ years",
]


def das_gupta(pop_t0, rate_t0, pop_t1, rate_t1):
    """Symmetric three-factor Das Gupta decomposition for D = P * sum(s*r).

    rate_*: age-specific rates per person (not per 100k).
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


def run():
    print("\n=== 04 DECOMPOSITION ===")
    ensure_dirs()

    df_age = pd.read_csv(PROC / "age_specific.csv")
    df_pop = pd.read_csv(PROC / "population.csv")

    # Vietnam population, Both sex, the 17 age groups used for standardization.
    pop = df_pop[
        (df_pop["sex_name"] == "Both")
        & (df_pop["age_name"].isin(AGE_GROUPS))
        & (df_pop["measure_name"] == "Population")
    ]
    pop_wide = pop.pivot_table(
        index="age_name", columns="year", values="val",
    ).reindex(AGE_GROUPS)

    # Age-specific DALY rates per 100k.
    daly = df_age[
        (df_age["measure_name"] == MEASURE["daly"])
        & (df_age["metric_name"] == "Rate")
        & (df_age["sex_name"] == "Both")
        & (df_age["age_name"].isin(AGE_GROUPS))
    ].copy()

    rows = []
    for key in ("cmnn", "ncd"):
        sub = daly[daly["cause_name"] == CAUSE_GROUPS[key]]
        rate_wide = sub.pivot_table(
            index="age_name", columns="year", values="val",
        ).reindex(AGE_GROUPS)
        # Convert per-100k to per-person
        r0 = (rate_wide[1990] / 1e5).values
        r1 = (rate_wide[2023] / 1e5).values
        p0 = pop_wide[1990].values
        p1 = pop_wide[2023].values
        rows.append({"cause_group": key.upper(), **das_gupta(p0, r0, p1, r1)})

    tbl = pd.DataFrame(rows)
    tbl["direction"] = np.where(tbl["observed_change"] >= 0, "increase", "decrease")
    tbl.to_csv(TAB / "decomposition_results.csv", index=False)

    print("  Observed vs decomposed DALY change, Vietnam:")
    show = tbl[["cause_group", "pop_size", "age_structure",
                "age_rate", "total_decomp", "observed_change", "direction"]]
    print(show.to_string(index=False, float_format="%.0f"))
    print("  [ok] tables/decomposition_results.csv")
    return tbl


if __name__ == "__main__":
    run()
