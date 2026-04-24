"""SEA cross-country comparison of epidemiological-transition metrics.

Primary indicator: NCD share of total DALYs (age-standardized, Both sex).

For each SEA country we report:
  - NCD share snapshots at 1990, 2000, 2010, 2023
  - Absolute percentage-point change 2023 - 1990 (`delta_ncd_share_pp`)
  - Joinpoint AAPC of NCD share 1990-2023 with 95% CI via delta method
    (ruptures Dynp + BIC; see utils.joinpoint_aapc).
  - Observed-to-expected ratio against the SDI-expected trajectory, fit as
    a quadratic regression of NCD share on SDI using the 10 other SEA
    countries (standard GBD approach; Lim et al. Lancet 2018;392:2091).

Also exports 2023 YLL/YLD ratio per SEA country (unchanged from before).

References
----------
  Kim HJ et al. Stat Med 2000;19:335-351 (joinpoint regression)
  Clegg LX et al. Stat Med 2009 (AAPC + delta method 95% CI)
  Lim SS et al. Lancet 2018;392:2091-138 (SDI-expected HAQ methodology)
"""

from pathlib import Path

import numpy as np
import pandas as pd

from shared import (
    SHARED_PROCESSED, SEA_COUNTRIES,
    CAUSE_GROUPS, MEASURE,
    ensure_dirs, joinpoint_aapc,
)


_PAPER_DIR = Path(__file__).resolve().parents[1]
_TABLES = _PAPER_DIR / "tables"


# GBD-native location_name -> short display name used in output tables.
# Only Brunei differs; every other SEA country uses the same short form.
COUNTRY_SHORT = {"Brunei Darussalam": "Brunei"}


def sdi_expected_ncd_share(sdi_vec, share_vec, focal_idx, deg=2):
    """Quadratic SDI->share fit on the 10 *peer* countries (focal excluded),
    evaluated at the focal's SDI. Cross-sectional at the focal year only -
    not a full panel fit - to match the published SEA comparison convention
    (Lim et al. Lancet 2018;392:2091 HAQ methodology, applied to 2023).

    Parameters
    ----------
    sdi_vec, share_vec : 1-D arrays of length N (N countries, same year).
    focal_idx : int in [0, N) - index of the country being predicted.
    """
    mask = np.ones(len(sdi_vec), dtype=bool)
    mask[focal_idx] = False
    coefs = np.polyfit(sdi_vec[mask], share_vec[mask], deg=deg)
    return float(np.polyval(coefs, sdi_vec[focal_idx]))


def run():
    print("\n=== 05 SEA COMPARISON ===")
    ensure_dirs(_TABLES)

    metrics = pd.read_csv(_TABLES / "metrics.csv")  # per-country/year shares
    sdi = pd.read_csv(SHARED_PROCESSED / "sdi_sea.csv")
    df_yll_yld = pd.read_csv(SHARED_PROCESSED / "yll_yld_sea.csv")

    # ---- Snapshot NCD share per country at milestone years ----------------
    snapshot_years = [1990, 2000, 2010, 2023]
    snap = (metrics[metrics["year"].isin(snapshot_years)]
            [["location_name", "year", "ncd_share_pct"]]
            .pivot(index="location_name", columns="year",
                   values="ncd_share_pct"))
    snap.columns = [f"ncd_share_{y}" for y in snap.columns]

    # Absolute percentage-point change (2023 - 1990)
    snap["delta_ncd_share_pp"] = snap["ncd_share_2023"] - snap["ncd_share_1990"]

    # ---- Joinpoint AAPC of NCD share per country (1990-2023) --------------
    aapc_rows = []
    for country in SEA_COUNTRIES:
        s = (metrics[metrics["location_name"] == country]
             .sort_values("year"))
        r = joinpoint_aapc(s["year"].values, s["ncd_share_pct"].values)
        aapc_rows.append({
            "location_name": country,
            "aapc_ncd_share": r["aapc"],
            "aapc_ncd_share_lo": r["ci_low"],
            "aapc_ncd_share_hi": r["ci_high"],
            "aapc_ncd_share_n_bkps": r["bkps_k"],
        })
    aapc_tbl = pd.DataFrame(aapc_rows).set_index("location_name")

    # ---- Observed-vs-expected ratio in 2023 (SDI model fit on 10 peers) ---
    # Cross-sectional fit at year=2023 across the 10 peer countries (focal
    # excluded), then evaluated at the focal country's 2023 SDI. This is the
    # leave-one-out HAQ-style expected (Lim et al. 2018).
    panel_2023 = (metrics[metrics["year"] == 2023]
                  [["location_name", "ncd_share_pct"]]
                  .merge(sdi[sdi["year"] == 2023][["location_name", "sdi"]],
                         on="location_name", how="inner"))
    # Align to SEA_COUNTRIES order so focal_idx is well-defined.
    panel_2023 = (panel_2023.set_index("location_name")
                  .reindex(SEA_COUNTRIES).reset_index())
    sdi_vec = panel_2023["sdi"].to_numpy(dtype=float)
    share_vec = panel_2023["ncd_share_pct"].to_numpy(dtype=float)

    obs_exp_rows = []
    for i, country in enumerate(SEA_COUNTRIES):
        expected = sdi_expected_ncd_share(sdi_vec, share_vec, focal_idx=i)
        observed = float(share_vec[i])
        obs_exp_rows.append({
            "location_name": country,
            "ncd_share_expected_2023": expected,
            "obs_vs_expected_ratio_2023": observed / expected if expected else np.nan,
        })
    obs_exp = pd.DataFrame(obs_exp_rows).set_index("location_name")

    # ---- Assemble final SEA comparison table ------------------------------
    sea = (snap.join(aapc_tbl).join(obs_exp)
               .reset_index()
               .sort_values("ncd_share_2023", ascending=False))
    sea["country"] = sea["location_name"].replace(COUNTRY_SHORT)
    col_order = [
        "country",
        "ncd_share_1990", "ncd_share_2000", "ncd_share_2010", "ncd_share_2023",
        "delta_ncd_share_pp",
        "aapc_ncd_share", "aapc_ncd_share_lo", "aapc_ncd_share_hi",
        "aapc_ncd_share_n_bkps",
        "ncd_share_expected_2023", "obs_vs_expected_ratio_2023",
    ]
    sea = sea[col_order]
    sea.to_csv(_TABLES / "sea_comparison.csv", index=False)

    # ---- YLL/YLD ratio 2023 (unchanged) -----------------------------------
    snap23 = df_yll_yld[
        (df_yll_yld["year"] == 2023)
        & (df_yll_yld["age_name"] == "Age-standardized")
        & (df_yll_yld["sex_name"] == "Both")
        & (df_yll_yld["metric_name"] == "Rate")
        & (df_yll_yld["cause_name"] == CAUSE_GROUPS["all"])
    ]
    rows = []
    for country in SEA_COUNTRIES:
        c_data = snap23[snap23["location_name"] == country]
        yll = c_data[c_data["measure_name"] == MEASURE["yll"]]["val"].values
        yld = c_data[c_data["measure_name"] == MEASURE["yld"]]["val"].values
        if len(yll) and len(yld):
            rows.append({"country": country,
                         "yll_rate": float(yll[0]),
                         "yld_rate": float(yld[0]),
                         "ratio": float(yll[0] / yld[0])})
    df_ratio = (pd.DataFrame(rows)
                .sort_values("ratio", ascending=False)
                .reset_index(drop=True))
    df_ratio.to_csv(_TABLES / "sea_yll_yld_ratio.csv", index=False)

    # ---- SEA age-standardized NCD death rate 2023 (for Figure 10 proxy
    #      of 30q70 across countries, which isn't directly available) -------
    burden = pd.read_csv(SHARED_PROCESSED / "burden_sea.csv")
    ncd_death_2023 = burden[
        (burden["measure_name"] == MEASURE["deaths"])
        & (burden["metric_name"] == "Rate")
        & (burden["age_name"] == "Age-standardized")
        & (burden["sex_name"] == "Both")
        & (burden["cause_name"] == CAUSE_GROUPS["ncd"])
        & (burden["year"] == 2023)
    ][["location_name", "val", "lower", "upper"]].rename(
        columns={"val": "ncd_death_rate_asr",
                 "lower": "ncd_death_rate_asr_lo",
                 "upper": "ncd_death_rate_asr_hi"})
    ncd_death_2023 = (ncd_death_2023.sort_values("ncd_death_rate_asr",
                                                 ascending=False)
                      .reset_index(drop=True))
    ncd_death_2023.to_csv(_TABLES / "sea_ncd_death_rate_2023.csv", index=False)

    # ---- Print summary -----------------------------------------------------
    print("  SEA countries ranked by NCD share of total DALYs in 2023:")
    cols = ["country", "ncd_share_1990", "ncd_share_2023",
            "delta_ncd_share_pp", "aapc_ncd_share",
            "obs_vs_expected_ratio_2023"]
    print(sea[cols].to_string(index=False, float_format="%.3f"))
    print("  [ok] tables/sea_comparison.csv")
    print("  [ok] tables/sea_yll_yld_ratio.csv")
    print("  [ok] tables/sea_ncd_death_rate_2023.csv "
          "(for Figure 10 - SEA premature-NCD-mortality proxy)")
    return dict(sea=sea, yll_yld_ratio=df_ratio, ncd_death_2023=ncd_death_2023)


if __name__ == "__main__":
    run()
