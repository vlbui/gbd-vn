"""Domain constants for GBD Vietnam analysis.

Notes on raw-data conventions (normalized at load time in shared.io):
  - location_name in GBD uses 'Viet Nam', 'Lao People's Democratic Republic',
    'Brunei Darussalam'. We normalize to 'Vietnam', 'Lao PDR', 'Brunei
    Darussalam' so downstream code matches SEA_COUNTRIES.
  - sex_name uses 'Both' (not 'Both sexes').
  - measure_name uses the long form. MEASURE maps short -> long.
  - Cause groups are full GBD level-1 labels; use CAUSE_GROUPS.
"""

SEA_COUNTRIES = [
    "Vietnam", "Thailand", "Indonesia", "Philippines",
    "Malaysia", "Myanmar", "Cambodia", "Lao PDR",
    "Singapore", "Brunei Darussalam", "Timor-Leste",
]

LOC_NORMALIZE = {
    "Viet Nam": "Vietnam",
    "Lao People's Democratic Republic": "Lao PDR",
}

MEASURE = {
    "deaths": "Deaths",
    "daly": "DALYs (Disability-Adjusted Life Years)",
    "yll": "YLLs (Years of Life Lost)",
    "yld": "YLDs (Years Lived with Disability)",
}

CAUSE_GROUPS = {
    "cmnn": "Communicable, maternal, neonatal, and nutritional diseases",
    "ncd": "Non-communicable diseases",
    "injuries": "Injuries",
    "all": "All causes",
}

CAUSE_SHORT = {
    CAUSE_GROUPS["cmnn"]: "CMNN",
    CAUSE_GROUPS["ncd"]: "NCD",
    CAUSE_GROUPS["injuries"]: "Injuries",
    CAUSE_GROUPS["all"]: "All",
}

# Age intervals for the WHO SDG 3.4.1 30q70 indicator.
AGE_BANDS_30_69 = [
    "30-34 years", "35-39 years", "40-44 years", "45-49 years",
    "50-54 years", "55-59 years", "60-64 years", "65-69 years",
]
