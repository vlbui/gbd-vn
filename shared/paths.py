"""Filesystem paths for the GBD Vietnam monorepo.

PROJECT_ROOT is derived from this file's location (shared/paths.py), so all
paths resolve correctly regardless of the caller's CWD — whether invoked
from `shared/pipeline/`, a `projects/XX/scripts/`, or a notebook.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA = PROJECT_ROOT / "raw_data"
BURDEN_RAW = RAW_DATA / "burden"
COVARIATES_RAW = RAW_DATA / "covariates"
AIR_POLLUTION_RAW = RAW_DATA / "air_pollution"

SHARED_PROCESSED = PROJECT_ROOT / "shared_processed"

PROJECTS = PROJECT_ROOT / "projects"
