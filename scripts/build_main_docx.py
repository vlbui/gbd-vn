"""Build `MANUSCRIPT_MAIN.docx` from `MANUSCRIPT_MAIN.md`.

Captions live in the manuscript text, not in the image files: for every
"**Figure N.**" paragraph in the Figure-legends section, we embed the
matching PNG from `figures/static/` *above* the caption paragraph so the
reader sees image + caption together in the docx. The PNGs themselves
have no titles or captions baked in (see scripts/06_figures.py +
utils.strip_figure_titles).

Styling: Arial 11pt, 1.5 line spacing, ASCII dashes only, bold on headings
and caption labels only. (Lancet Regional Health - Western Pacific).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from md_to_docx import md_to_docx
from utils import PROJECT_ROOT, FIG_STATIC


# Main-manuscript figure labels -> PNG. The 9 figures embedded are 1-7, 9,
# 10 (Figure 8 is the CMNN sensitivity and lives in the supplement only).
FIG_PNGS = {
    "1":  FIG_STATIC / "fig1_overview.png",
    "2":  FIG_STATIC / "fig2_heatmap.png",
    "3":  FIG_STATIC / "fig3_decomposition.png",
    "4":  FIG_STATIC / "fig4_sea_comparison.png",
    "5":  FIG_STATIC / "fig5_age_sex_pyramid.png",
    "6":  FIG_STATIC / "fig6_yll_yld_trends.png",
    "7":  FIG_STATIC / "fig7_sea_yll_yld.png",
    "9":  FIG_STATIC / "fig9_30q70_vietnam.png",
    "10": FIG_STATIC / "fig10_sea_ncd_premature.png",
}


def run():
    md = PROJECT_ROOT / "MANUSCRIPT_MAIN.md"
    out = PROJECT_ROOT / "MANUSCRIPT_MAIN.docx"
    inserted = md_to_docx(md, out, image_lookup={k: str(v)
                                                 for k, v in FIG_PNGS.items()})
    print(f"  [ok] {out}")
    print(f"  inserted {inserted} images "
          f"(expected {len(FIG_PNGS)} for main docx)")


if __name__ == "__main__":
    run()
