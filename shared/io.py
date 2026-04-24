"""IO helpers: directory creation, GBD CSV loading, small formatters.

Loader normalizes GBD naming quirks (see shared.constants docstring).
"""

from pathlib import Path

import pandas as pd

from .constants import LOC_NORMALIZE


def ensure_dirs(*dirs):
    """Create any missing directories. Accepts Path or str; no-op on existing."""
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def load_gbd_csv(filepath):
    """Read a GBD-format CSV; standardize columns; normalize location names."""
    df = pd.read_csv(filepath)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    if "year" in df.columns:
        df["year"] = df["year"].astype(int)
    for col in ("val", "lower", "upper"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "location_name" in df.columns:
        df["location_name"] = df["location_name"].replace(LOC_NORMALIZE)
    return df


def format_ci(val, lower, upper, decimals=1):
    fmt = f"{{:.{decimals}f}}"
    return f"{fmt.format(val)} ({fmt.format(lower)}-{fmt.format(upper)})"


def get_asr(df):
    return df[df["age_name"] == "Age-standardized"].copy()


def get_all_ages(df):
    return df[df["age_name"] == "All ages"].copy()
