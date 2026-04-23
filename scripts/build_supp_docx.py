"""Build `MANUSCRIPT_SUPPLEMENT.docx` from `MANUSCRIPT_SUPPLEMENT.md`.

Only Figure S4 has a corresponding rendered PNG in this pipeline (it is
the same artifact as Figure 8 in the main-text convention - the CMNN
sensitivity plot). Figures S1-S3 and S5-S8 are described in the legend
section but will be generated in a future revision; for now they appear
as caption-only paragraphs in the docx, which is the Lancet supplement
convention.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from md_to_docx import md_to_docx
from utils import PROJECT_ROOT, FIG_STATIC


SUPP_FIG_PNGS = {
    "S4": FIG_STATIC / "fig8_cmnn_sensitivity.png",
}


def run():
    md = PROJECT_ROOT / "MANUSCRIPT_SUPPLEMENT.md"
    out = PROJECT_ROOT / "MANUSCRIPT_SUPPLEMENT.docx"
    inserted = md_to_docx(md, out, image_lookup={k: str(v)
                                                 for k, v in SUPP_FIG_PNGS.items()})
    print(f"  [ok] {out}")
    print(f"  inserted {inserted} image(s) "
          f"(expected {len(SUPP_FIG_PNGS)} for supplement)")


if __name__ == "__main__":
    run()
