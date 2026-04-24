"""Load, merge, filter and save cleaned GBD files.

Inputs (raw_data/):
  burden/query1_level1.csv          Level-1 cause groups, 10 SEA countries
  burden/query1_level1_timor.csv    Same schema, Timor-Leste only
  burden/query2a_cmnn.csv           Vietnam CMNN disease detail
  burden/query2b_ncd.csv            Vietnam NCD disease detail
  burden/query3_age.csv             Vietnam age-specific burden
  burden/query4_pop.csv             Vietnam population by age/sex
  burden/query5_yll_yld.csv         YLLs + YLDs, Vietnam + SEA
  covariates/SDI.csv                SDI, all locations 1950-2023
  covariates/hierarchy.XLSX         GBD cause hierarchy

Outputs:
  shared_processed/ — burden_sea, age_specific, population, yll_yld_sea, sdi_sea
  projects/01_epi_transition/data/ — cmnn_vietnam, ncd_vietnam
    (Vietnam-only detail tables, paper-01-scoped)
"""

import pandas as pd

from shared import (
    BURDEN_RAW, COVARIATES_RAW,
    SHARED_PROCESSED, PROJECTS,
    SEA_COUNTRIES, LOC_NORMALIZE,
    ensure_dirs, load_gbd_csv,
)


_PAPER_01_DATA = PROJECTS / "01_epi_transition" / "data"
YEAR_MIN, YEAR_MAX = 1990, 2023


def run():
    print("\n=== 01 LOAD & CLEAN ===")
    ensure_dirs(SHARED_PROCESSED, _PAPER_01_DATA)

    # Level-1 burden: main SEA + Timor concatenated.
    df1 = load_gbd_csv(BURDEN_RAW / "query1_level1.csv")
    df1t = load_gbd_csv(BURDEN_RAW / "query1_level1_timor.csv")
    df_burden = pd.concat([df1, df1t], ignore_index=True)

    df_cmnn = load_gbd_csv(BURDEN_RAW / "query2a_cmnn.csv")
    df_ncd = load_gbd_csv(BURDEN_RAW / "query2b_ncd.csv")
    df_age = load_gbd_csv(BURDEN_RAW / "query3_age.csv")
    df_pop = load_gbd_csv(BURDEN_RAW / "query4_pop.csv")
    df_yll_yld = load_gbd_csv(BURDEN_RAW / "query5_yll_yld.csv")

    df_sdi = pd.read_csv(COVARIATES_RAW / "SDI.csv")
    df_sdi.columns = [c.strip().lower() for c in df_sdi.columns]
    df_sdi = df_sdi.rename(columns={"year_id": "year", "mean_value": "sdi"})
    df_sdi["location_name"] = df_sdi["location_name"].replace(LOC_NORMALIZE)

    df_hier = pd.read_excel(COVARIATES_RAW / "hierarchy.XLSX")

    for df in (df_burden, df_yll_yld, df_sdi):
        df.drop(df[~df["location_name"].isin(SEA_COUNTRIES)].index, inplace=True)
    for df in (df_burden, df_cmnn, df_ncd, df_age, df_pop, df_yll_yld, df_sdi):
        df.drop(df[(df["year"] < YEAR_MIN) | (df["year"] > YEAR_MAX)].index,
                inplace=True)
        df.reset_index(drop=True, inplace=True)

    df_burden.to_csv(SHARED_PROCESSED / "burden_sea.csv", index=False)
    df_age.to_csv(SHARED_PROCESSED / "age_specific.csv", index=False)
    df_pop.to_csv(SHARED_PROCESSED / "population.csv", index=False)
    df_yll_yld.to_csv(SHARED_PROCESSED / "yll_yld_sea.csv", index=False)
    df_sdi.to_csv(SHARED_PROCESSED / "sdi_sea.csv", index=False)

    # Paper-01-specific detail tables (Vietnam-only disease breakouts).
    df_cmnn.to_csv(_PAPER_01_DATA / "cmnn_vietnam.csv", index=False)
    df_ncd.to_csv(_PAPER_01_DATA / "ncd_vietnam.csv", index=False)

    print(f"  Burden rows:  {len(df_burden):,}  "
          f"({df_burden['location_name'].nunique()} countries)")
    print(f"  YLL/YLD rows: {len(df_yll_yld):,}  "
          f"({df_yll_yld['location_name'].nunique()} countries)")
    print(f"  Years: {df_burden['year'].min()}-{df_burden['year'].max()}")
    print(f"  Missing in burden val/lower/upper: "
          f"{df_burden[['val', 'lower', 'upper']].isna().sum().sum()}")
    print("  [ok] cleaned files written to shared_processed/ + projects/01/data/")

    return df_burden, df_yll_yld, df_pop


if __name__ == "__main__":
    run()
