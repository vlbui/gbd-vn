# 01 — Epidemiological transition, Vietnam 1990-2023

**Target journal**: Lancet Regional Health — Western Pacific
**Status**: manuscript drafted; figures + tables regenerable from pipeline

## What the paper shows

- Cause-composition trajectory (CMNN / NCD / Injuries share of DALYs) for
  Vietnam 1990-2023 and the 11 Southeast Asian comparator countries.
- Joinpoint AAPC trend analysis (Clegg 2009 delta-method 95% CI).
- Das Gupta three-factor decomposition of the change in total DALYs into
  population-size, age-structure, and age-specific-rate effects.
- WHO SDG 3.4.1 30q70 premature-NCD-mortality probability for Vietnam and SEA.
- CMNN split sensitivity (C-only vs M+N+N subgroups).
- SDI-expected comparison (leave-one-out polynomial fit, Lim 2018 HAQ method).

## Running

Pre-requisite: `shared/pipeline/run_pipeline.py` has been run so that
`shared_processed/` and this folder's `data/` are populated.

```
python scripts/sea_comparison.py       # SEA NCD-share comparison + rankings
python scripts/chiang_30q70.py         # strict SDG 3.4.1 30q70 for all 11 SEA
python scripts/figures.py              # publication figures (PNG 300dpi + SVG + HTML)
```

## Folder map

- `manuscript/` — canonical `MANUSCRIPT.docx` and `SUPPLEMENT.docx`
- `scripts/` — paper-specific analysis (post-pipeline)
- `notebooks/` — exploratory analysis (legacy pre-pipeline duplicate)
- `data/` — Vietnam-specific detail tables produced by pipeline stage 01
- `tables/` — manuscript tables, CSV
- `figures/` — `html/` (interactive) + `static/` (PNG 300dpi + SVG) outputs
