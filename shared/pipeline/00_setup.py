"""Ensure output directories exist and verify raw inputs are present."""

from shared import (
    ensure_dirs,
    BURDEN_RAW, COVARIATES_RAW,
    SHARED_PROCESSED, PROJECTS,
)


_PAPER_01 = PROJECTS / "01_epi_transition"
_PAPER_01_DIRS = (
    _PAPER_01 / "data",
    _PAPER_01 / "tables",
    _PAPER_01 / "figures" / "html",
    _PAPER_01 / "figures" / "static",
)

EXPECTED_BURDEN = [
    "query1_level1.csv",
    "query1_level1_timor.csv",
    "query2a_cmnn.csv",
    "query2b_ncd.csv",
    "query3_age.csv",
    "query4_pop.csv",
    "query5_yll_yld.csv",
]
EXPECTED_COVARIATES = ["SDI.csv", "hierarchy.XLSX"]


def run():
    print("\n=== 00 SETUP ===")
    ensure_dirs(SHARED_PROCESSED, *_PAPER_01_DIRS)
    print(f"  project root: {SHARED_PROCESSED.parent}")
    print("  output dirs ok: shared_processed, projects/01_epi_transition/{data,tables,figures}")

    missing = [f for f in EXPECTED_BURDEN if not (BURDEN_RAW / f).exists()]
    missing += [f for f in EXPECTED_COVARIATES if not (COVARIATES_RAW / f).exists()]
    if missing:
        print(f"  WARNING - missing raw files: {missing}")
    else:
        print(f"  all {len(EXPECTED_BURDEN) + len(EXPECTED_COVARIATES)} expected raw files present")
    return missing


if __name__ == "__main__":
    run()
