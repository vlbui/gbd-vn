"""Core metrics for the epidemiological transition:

  - Cause composition (CMNN / NCD / Injuries share of total DALYs)
  - CMNN-to-NCD ratio
  - Premature mortality probability 30q70 (WHO SDG 3.4.1) for Vietnam
  - YLL/YLD ratio
  - CMNN split sensitivity (C-only vs M+N+N)

All AAPC values use joinpoint regression (ruptures Dynp + BIC selection +
per-segment OLS + Clegg delta-method 95% CI). See shared.joinpoint_aapc.
References: Kim HJ et al. Stat Med 2000;19:335-51; Clegg LX et al. Stat
Med 2009;28:3670-82.

Exports
-------
  projects/01_epi_transition/tables/metrics.csv
  projects/01_epi_transition/tables/table1_summary.csv
  projects/01_epi_transition/tables/table_s1_cmnn_sensitivity.csv
  shared_processed/yll_yld_ratio.csv        Vietnam YLL + YLD + ratio
  shared_processed/cmnn_split.csv           C-only / M+N+N year series
  shared_processed/probability_30q70.csv    Vietnam 30q70 NCD + CMNN by year
"""

import numpy as np
import pandas as pd

from shared import (
    SHARED_PROCESSED, PROJECTS, ensure_dirs,
    CAUSE_GROUPS, CAUSE_SHORT, MEASURE, AGE_BANDS_30_69,
    get_asr, cause_shares, probability_30q70,
    joinpoint_aapc,
)


_PAPER_01 = PROJECTS / "01_epi_transition"
_PAPER_01_DATA = _PAPER_01 / "data"
_PAPER_01_TABLES = _PAPER_01 / "tables"


# Level-2 CMNN subgroups, as they appear in query2a_cmnn.csv. These sum
# exactly to the CMNN level-1 total (verified).
C_ONLY_CAUSES = [
    "HIV/AIDS and sexually transmitted infections",
    "Respiratory infections and tuberculosis",
    "Enteric infections",
    "Neglected tropical diseases and malaria",
    "Other infectious diseases",
]
MNN_CAUSES = [
    "Maternal and neonatal disorders",
    "Nutritional deficiencies",
]


# --- 30q70 (WHO SDG 3.4.1) --------------------------------------------------

def compute_30q70_vietnam():
    """Per-year, per-cause-group unconditional probability of dying between
    ages 30 and 70, Vietnam, 1990-2023.

    Uses 5-year deaths counts and populations for the eight age bands
    30-34 through 65-69 (both sexes combined). Saves the full series to
    shared_processed/probability_30q70.csv and returns it.

    Reference: WHO Global Action Plan for NCDs 2013-2020 (Indicator 10); SDG 3.4.1.
    """
    age = pd.read_csv(SHARED_PROCESSED / "age_specific.csv")
    pop = pd.read_csv(SHARED_PROCESSED / "population.csv")

    deaths = age[(age["measure_name"] == MEASURE["deaths"])
                 & (age["metric_name"] == "Number")
                 & (age["sex_name"] == "Both")
                 & (age["age_name"].isin(AGE_BANDS_30_69))]
    pop_b = pop[(pop["measure_name"] == "Population")
                & (pop["sex_name"] == "Both")
                & (pop["age_name"].isin(AGE_BANDS_30_69))]

    pop_wide = (pop_b.pivot_table(index="age_name", columns="year",
                                  values="val")
                .reindex(AGE_BANDS_30_69))

    rows = []
    for key, full in [("ncd", CAUSE_GROUPS["ncd"]),
                      ("cmnn", CAUSE_GROUPS["cmnn"])]:
        d_c = deaths[deaths["cause_name"] == full]
        dwide = (d_c.pivot_table(index="age_name", columns="year",
                                 values="val")
                 .reindex(AGE_BANDS_30_69))
        for year in sorted(dwide.columns):
            if year not in pop_wide.columns:
                continue
            q = probability_30q70(dwide[year].values, pop_wide[year].values)
            rows.append(dict(year=int(year), cause_group=key.upper(),
                             probability_30q70=q,
                             probability_30q70_pct=q * 100 if not np.isnan(q)
                             else np.nan))

    out = pd.DataFrame(rows).sort_values(["cause_group", "year"]).reset_index(drop=True)
    out.to_csv(SHARED_PROCESSED / "probability_30q70.csv", index=False)
    return out


# --- CMNN split sensitivity -------------------------------------------------

def cmnn_sensitivity():
    """Sensitivity: decompose CMNN into C-only (HIV + respiratory + enteric +
    NTDs + other infectious) and M+N+N (maternal/neonatal + nutritional).
    """
    cmnn_det = pd.read_csv(_PAPER_01_DATA / "cmnn_vietnam.csv")
    burden = pd.read_csv(SHARED_PROCESSED / "burden_sea.csv")

    def _filter(df):
        return df[(df["location_name"] == "Vietnam")
                  & (df["age_name"] == "Age-standardized")
                  & (df["sex_name"] == "Both")
                  & (df["measure_name"] == MEASURE["daly"])
                  & (df["metric_name"] == "Rate")]

    det = _filter(cmnn_det)
    lvl1 = _filter(burden)

    lvl1_wide = (lvl1[lvl1["cause_name"].isin(CAUSE_SHORT.keys())]
                 .assign(short=lvl1["cause_name"].map(CAUSE_SHORT))
                 .pivot_table(index="year", columns="short", values="val"))

    c_only = (det[det["cause_name"].isin(C_ONLY_CAUSES)]
              .groupby("year")["val"].sum().rename("C_only"))
    mnn = (det[det["cause_name"].isin(MNN_CAUSES)]
           .groupby("year")["val"].sum().rename("MNN"))

    split = pd.concat([lvl1_wide, c_only, mnn], axis=1).sort_index()
    split["CMNN_check"] = split["C_only"] + split["MNN"]
    max_err = (split["CMNN"] - split["CMNN_check"]).abs().max()

    split["ncd_share_main_pct"] = (
        split["NCD"] / (split["NCD"] + split["CMNN"] + split["Injuries"]) * 100)
    split["ncd_share_vs_Conly_pct"] = (
        split["NCD"] / (split["NCD"] + split["C_only"] + split["Injuries"]) * 100)
    split["ncd_share_vs_MNN_pct"] = (
        split["NCD"] / (split["NCD"] + split["MNN"] + split["Injuries"]) * 100)

    split.to_csv(SHARED_PROCESSED / "cmnn_split.csv")

    years = [1990, 2000, 2010, 2023]
    s1_rows = []
    for col, label in [
        ("CMNN", "CMNN (full, main analysis)"),
        ("C_only", "Communicable only (sensitivity)"),
        ("MNN", "Maternal+Neonatal+Nutritional (sensitivity)"),
        ("NCD", "Non-communicable diseases"),
        ("Injuries", "Injuries"),
    ]:
        series = split[col].dropna()
        aapc = joinpoint_aapc(series.index.values, series.values)
        s1_rows.append({
            "group": label,
            **{str(y): round(series.loc[y], 1) if y in series.index else np.nan
               for y in years},
            "AAPC_%": round(aapc["aapc"], 2),
            "AAPC_95CI": f"{aapc['ci_low']:.2f}, {aapc['ci_high']:.2f}",
        })

    for col, label in [
        ("ncd_share_main_pct",
         "NCD share vs full CMNN (main analysis, % of total DALYs)"),
        ("ncd_share_vs_Conly_pct",
         "NCD share vs C-only CMNN (% of total DALYs)"),
        ("ncd_share_vs_MNN_pct",
         "NCD share vs M+N+N only CMNN (% of total DALYs)"),
    ]:
        s1_rows.append({
            "group": label,
            **{str(y): round(split.loc[y, col], 2) if y in split.index
               else np.nan for y in years},
            "AAPC_%": "", "AAPC_95CI": "",
        })

    s1 = pd.DataFrame(s1_rows)
    s1.to_csv(_PAPER_01_TABLES / "table_s1_cmnn_sensitivity.csv", index=False)

    print(f"  CMNN split max reconciliation error: {max_err:.3f}")
    print(f"  NCD share (main)         2023 = {split.loc[2023, 'ncd_share_main_pct']:.2f}%")
    print(f"  NCD share vs C-only      2023 = {split.loc[2023, 'ncd_share_vs_Conly_pct']:.2f}%")
    print(f"  NCD share vs M+N+N only  2023 = {split.loc[2023, 'ncd_share_vs_MNN_pct']:.2f}%")
    print("  [ok] projects/01/tables/table_s1_cmnn_sensitivity.csv, "
          "shared_processed/cmnn_split.csv")
    return split


# --- Main entry point -------------------------------------------------------

def run():
    print("\n=== 02 METRICS ===")
    ensure_dirs(SHARED_PROCESSED, _PAPER_01_TABLES)

    df_burden = pd.read_csv(SHARED_PROCESSED / "burden_sea.csv")
    df_yll_yld = pd.read_csv(SHARED_PROCESSED / "yll_yld_sea.csv")

    shares = cause_shares(df_burden)
    shares.to_csv(_PAPER_01_TABLES / "metrics.csv", index=False)

    vn_yy = df_yll_yld[
        (df_yll_yld["location_name"] == "Vietnam")
        & (df_yll_yld["age_name"] == "Age-standardized")
        & (df_yll_yld["sex_name"] == "Both")
        & (df_yll_yld["metric_name"] == "Rate")
        & (df_yll_yld["cause_name"] == CAUSE_GROUPS["all"])
    ].copy()

    yll = (vn_yy[vn_yy["measure_name"] == MEASURE["yll"]]
           .set_index("year")[["val", "lower", "upper"]]
           .rename(columns={"val": "yll", "lower": "yll_lo", "upper": "yll_hi"}))
    yld = (vn_yy[vn_yy["measure_name"] == MEASURE["yld"]]
           .set_index("year")[["val", "lower", "upper"]]
           .rename(columns={"val": "yld", "lower": "yld_lo", "upper": "yld_hi"}))
    yll_yld = yll.join(yld, how="inner").sort_index()
    yll_yld["ratio"] = yll_yld["yll"] / yll_yld["yld"]
    yll_yld.to_csv(SHARED_PROCESSED / "yll_yld_ratio.csv")

    q30 = compute_30q70_vietnam()

    vn_shares = shares[shares["location_name"] == "Vietnam"].set_index("year")
    vn_rates = (df_burden[(df_burden["location_name"] == "Vietnam")
                          & (df_burden["age_name"] == "Age-standardized")
                          & (df_burden["measure_name"] == MEASURE["daly"])
                          & (df_burden["metric_name"] == "Rate")
                          & (df_burden["sex_name"] == "Both")
                          & (df_burden["cause_name"].isin(CAUSE_SHORT.keys()))]
                .assign(short=lambda d: d["cause_name"].map(CAUSE_SHORT))
                .pivot_table(index="year", columns="short", values="val"))

    years_snap = [1990, 2000, 2010, 2023]
    rows = []
    for g in ("CMNN", "NCD", "Injuries"):
        series = vn_rates[g]
        aapc = joinpoint_aapc(series.index.values, series.values)
        rows.append({
            "metric": f"{g} age-std DALY rate (per 100k)",
            **{str(y): round(series.loc[y], 1) if y in series.index else np.nan
               for y in years_snap},
            "AAPC_%": round(aapc["aapc"], 2),
            "AAPC_95CI": f"{aapc['ci_low']:.2f}, {aapc['ci_high']:.2f}",
        })

    for col, label in [
        ("cmnn_share_pct", "CMNN share of total DALYs (%)"),
        ("ncd_share_pct", "NCD share of total DALYs (%)"),
        ("injuries_share_pct", "Injuries share of total DALYs (%)"),
        ("cmnn_ncd_ratio", "CMNN/NCD ratio"),
    ]:
        series = vn_shares[col]
        aapc = joinpoint_aapc(series.index.values, series.values.astype(float))
        rows.append({
            "metric": label,
            **{str(y): round(float(series.loc[y]),
                             3 if "ratio" in col else 2)
               if y in series.index else np.nan for y in years_snap},
            "AAPC_%": round(aapc["aapc"], 2),
            "AAPC_95CI": f"{aapc['ci_low']:.2f}, {aapc['ci_high']:.2f}",
        })

    for cg_label, cg_key in [("NCD", "NCD"), ("CMNN", "CMNN")]:
        series = (q30[q30["cause_group"] == cg_key]
                  .set_index("year")["probability_30q70_pct"])
        if not series.empty:
            aapc = joinpoint_aapc(series.index.values, series.values)
            rows.append({
                "metric": f"30q70 {cg_label} probability (%)",
                **{str(y): round(series.loc[y], 2) if y in series.index else np.nan
                   for y in years_snap},
                "AAPC_%": round(aapc["aapc"], 2),
                "AAPC_95CI": f"{aapc['ci_low']:.2f}, {aapc['ci_high']:.2f}",
            })

    if set(years_snap).issubset(yll_yld.index):
        for col, label in [("yll", "YLL rate (per 100k)"),
                           ("yld", "YLD rate (per 100k)")]:
            aapc = joinpoint_aapc(yll_yld.index.values, yll_yld[col].values)
            rows.append({
                "metric": label,
                **{str(y): round(yll_yld.loc[y, col], 1) for y in years_snap},
                "AAPC_%": round(aapc["aapc"], 2),
                "AAPC_95CI": f"{aapc['ci_low']:.2f}, {aapc['ci_high']:.2f}",
            })
        aapc_ratio = joinpoint_aapc(yll_yld.index.values,
                                    yll_yld["ratio"].values)
        rows.append({
            "metric": "YLL/YLD ratio",
            **{str(y): round(yll_yld.loc[y, "ratio"], 2) for y in years_snap},
            "AAPC_%": round(aapc_ratio["aapc"], 2),
            "AAPC_95CI": (f"{aapc_ratio['ci_low']:.2f}, "
                         f"{aapc_ratio['ci_high']:.2f}"),
        })

    tbl1 = pd.DataFrame(rows)
    tbl1.to_csv(_PAPER_01_TABLES / "table1_summary.csv", index=False)

    print(f"  Vietnam NCD share 1990->2023: "
          f"{vn_shares.loc[1990, 'ncd_share_pct']:.2f}% "
          f"-> {vn_shares.loc[2023, 'ncd_share_pct']:.2f}%")
    print(f"  Vietnam 30q70 NCD 1990->2023: "
          f"{q30.loc[(q30['cause_group']=='NCD') & (q30['year']==1990), 'probability_30q70_pct'].iloc[0]:.2f}% "
          f"-> {q30.loc[(q30['cause_group']=='NCD') & (q30['year']==2023), 'probability_30q70_pct'].iloc[0]:.2f}%")
    print(f"  YLL/YLD ratio 1990: {yll_yld.loc[1990, 'ratio']:.2f}")
    print(f"  YLL/YLD ratio 2023: {yll_yld.loc[2023, 'ratio']:.2f}")
    print("  [ok] tables/metrics.csv, tables/table1_summary.csv, "
          "shared_processed/probability_30q70.csv")

    print("  -- CMNN sensitivity analysis --")
    split = cmnn_sensitivity()

    return dict(shares=shares, yll_yld=yll_yld, table1=tbl1,
                cmnn_split=split, q30=q30)


if __name__ == "__main__":
    run()
