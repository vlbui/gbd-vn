"""Load, merge, filter and save cleaned GBD files to data/processed/.

Inputs (raw):
  query1_level1.csv          Level-1 cause groups, 10 SEA countries
  query1_level1_timor.csv    Same schema, Timor-Leste only
  query2a_cmnn.csv           Vietnam CMNN disease detail
  query2b_ncd.csv            Vietnam NCD disease detail
  query3_age.csv             Vietnam age-specific burden
  query4_pop.csv             Vietnam population by age/sex
  query5_yll_yld.csv         YLLs + YLDs, Vietnam + SEA (NEW)
  SDI.csv                    SDI, all locations 1950-2023
  hierarchy.XLSX             GBD cause hierarchy

Outputs (processed):
  burden_sea.csv, cmnn_vietnam.csv, ncd_vietnam.csv,
  age_specific.csv, population.csv, yll_yld_sea.csv, sdi_sea.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from utils import (
    RAW, PROC, SEA_COUNTRIES, LOC_NORMALIZE,
    ensure_dirs, load_gbd_csv,
)

YEAR_MIN, YEAR_MAX = 1990, 2023


def run():
    print("\n=== 01 LOAD & CLEAN ===")
    ensure_dirs()

    # Level-1 burden: main SEA + Timor concatenated.
    df1 = load_gbd_csv(RAW / "query1_level1.csv")
    df1t = load_gbd_csv(RAW / "query1_level1_timor.csv")
    df_burden = pd.concat([df1, df1t], ignore_index=True)

    df_cmnn = load_gbd_csv(RAW / "query2a_cmnn.csv")
    df_ncd = load_gbd_csv(RAW / "query2b_ncd.csv")
    df_age = load_gbd_csv(RAW / "query3_age.csv")
    df_pop = load_gbd_csv(RAW / "query4_pop.csv")
    df_yll_yld = load_gbd_csv(RAW / "query5_yll_yld.csv")

    # SDI has a different column naming; rename so year/location work identically
    df_sdi = pd.read_csv(RAW / "SDI.csv")
    df_sdi.columns = [c.strip().lower() for c in df_sdi.columns]
    df_sdi = df_sdi.rename(columns={"year_id": "year", "mean_value": "sdi"})
    df_sdi["location_name"] = df_sdi["location_name"].replace(LOC_NORMALIZE)

    df_hier = pd.read_excel(RAW / "hierarchy.XLSX")

    # Filter to SEA countries + analysis window.
    for df in (df_burden, df_yll_yld, df_sdi):
        df.drop(df[~df["location_name"].isin(SEA_COUNTRIES)].index, inplace=True)
    for df in (df_burden, df_cmnn, df_ncd, df_age, df_pop, df_yll_yld, df_sdi):
        df.drop(df[(df["year"] < YEAR_MIN) | (df["year"] > YEAR_MAX)].index,
                inplace=True)
        df.reset_index(drop=True, inplace=True)

    # Persist cleaned tables.
    df_burden.to_csv(PROC / "burden_sea.csv", index=False)
    df_cmnn.to_csv(PROC / "cmnn_vietnam.csv", index=False)
    df_ncd.to_csv(PROC / "ncd_vietnam.csv", index=False)
    df_age.to_csv(PROC / "age_specific.csv", index=False)
    df_pop.to_csv(PROC / "population.csv", index=False)
    df_yll_yld.to_csv(PROC / "yll_yld_sea.csv", index=False)
    df_sdi.to_csv(PROC / "sdi_sea.csv", index=False)

    # Quality report.
    print(f"  Burden rows:  {len(df_burden):,}  "
          f"({df_burden['location_name'].nunique()} countries)")
    print(f"  YLL/YLD rows: {len(df_yll_yld):,}  "
          f"({df_yll_yld['location_name'].nunique()} countries)")
    print(f"  Years: {df_burden['year'].min()}-{df_burden['year'].max()}")
    print(f"  Missing in burden val/lower/upper: "
          f"{df_burden[['val', 'lower', 'upper']].isna().sum().sum()}")
    print(f"  [ok] cleaned files written to data/processed/")

    return df_burden, df_yll_yld, df_pop


if __name__ == "__main__":
    run()
