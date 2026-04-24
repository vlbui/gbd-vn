"""SDI-expected comparisons (leave-one-out polynomial fit on SDI).

Standard GBD method: fit polynomial regression of a metric on SDI using
all locations except the focal country, then evaluate at the focal
(country, year)'s SDI. Ratio of observed/expected is the indicator.

Reference: Lim SS et al. Lancet 2018;392:2091-138 (HAQ Index method).
"""

import numpy as np
import pandas as pd


def expected_vs_observed_on_sdi(df_metric, df_sdi, country, year,
                                value_col, exclude_country=None, deg=2):
    """Fit poly of `value_col` on SDI over all rows except `exclude_country`,
    evaluate the curve at (country, year)'s SDI, return observed, expected,
    and ratio.
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
