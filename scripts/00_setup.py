"""Ensure output directories exist and verify raw inputs are present."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import ensure_dirs, RAW, PROC, FIG_HTML, FIG_STATIC, TAB


EXPECTED = [
    "query1_level1.csv",
    "query1_level1_timor.csv",
    "query2a_cmnn.csv",
    "query2b_ncd.csv",
    "query3_age.csv",
    "query4_pop.csv",
    "query5_yll_yld.csv",
    "SDI.csv",
    "hierarchy.XLSX",
]


def run():
    print("\n=== 00 SETUP ===")
    ensure_dirs()
    print(f"  project root: {RAW.parent.parent}")
    print(f"  output dirs ok: processed, figures/html, figures/static, tables")

    missing = [f for f in EXPECTED if not (RAW / f).exists()]
    if missing:
        print(f"  WARNING - missing raw files: {missing}")
    else:
        print(f"  all {len(EXPECTED)} expected raw files present")
    return missing


if __name__ == "__main__":
    run()
