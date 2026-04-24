"""Shared utilities for the GBD Vietnam monorepo.

Re-exports the public API from submodules so call sites can write
    from shared import joinpoint_aapc, LANCET_NCD, RAW_DATA
without caring about internal module layout.
"""

from .constants import (
    SEA_COUNTRIES,
    LOC_NORMALIZE,
    MEASURE,
    CAUSE_GROUPS,
    CAUSE_SHORT,
    AGE_BANDS_30_69,
)
from .palette import (
    LANCET,
    LANCET_CMNN,
    LANCET_NCD,
    LANCET_INJURY,
    LANCET_YLL,
    LANCET_YLD,
    LANCET_VIETNAM,
    LANCET_PEER,
    LANCET_INK,
    LANCET_MUTED,
    PALETTE,
    FONT_FAMILY,
    BASE_LAYOUT,
)
from .stats import (
    calculate_aapc,
    joinpoint_aapc,
    joinpoint_aapc_ci,
    joinpoint_aapc_pelt,
    probability_30q70,
    cause_shares,
)
from .sdi import expected_vs_observed_on_sdi
from .figures import (
    apply_panel_border,
    apply_lancet_style,
    strip_figure_titles,
    save_fig,
)
from .io import (
    ensure_dirs,
    load_gbd_csv,
    format_ci,
    get_asr,
    get_all_ages,
)
from .paths import (
    PROJECT_ROOT,
    RAW_DATA,
    SHARED_PROCESSED,
    BURDEN_RAW,
    COVARIATES_RAW,
    AIR_POLLUTION_RAW,
    PROJECTS,
)
