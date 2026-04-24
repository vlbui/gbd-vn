# GBD Vietnam — monorepo

Analysis of the Global Burden of Disease (GBD) dataset, focused on Vietnam and
Southeast Asia (SEA). Organized as a monorepo: one folder per paper under
`projects/`, shared Python utilities under `shared/`, raw data inputs under
`raw_data/`, and derived multi-paper data under `shared_processed/`.

## Layout

```
GBD/
├── projects/
│   ├── 01_epi_transition/         epidemiological transition 1990-2023 (Lancet RH-WP)
│   ├── 02_cause_specific_30q70/
│   ├── 03_level2_ncd/
│   ├── ...                         see plans/PUBLICATION_PLAN.xlsx for full roadmap
│   └── 12_heat_attributable/
├── shared/                         reusable Python code
│   ├── paths.py                    repo-rooted path constants
│   ├── constants.py                SEA countries, cause groups, GBD naming
│   ├── palette.py                  Lancet/ggsci colour grammar
│   ├── stats.py                    joinpoint AAPC, probability_30q70, ...
│   ├── sdi.py                      SDI-expected leave-one-out regression
│   ├── figures.py                  Plotly styling + save_fig
│   ├── io.py                       GBD CSV loader + small helpers
│   └── pipeline/                   multi-stage preprocessing (00-04)
├── raw_data/                       immutable IHME downloads, .gitignored
├── shared_processed/               derived data used by >=2 projects
└── plans/                          publication roadmap + extraction protocol
```

## Setup

```
pip install -e .
pip install -r requirements.txt
```

The editable install registers `shared` as an importable package, so from
anywhere in the repo you can write `from shared import joinpoint_aapc`.

## Running the shared pipeline

```
python shared/pipeline/run_pipeline.py
```

Or individual stages:

```
python -m shared.pipeline.00_setup
python -m shared.pipeline.01_load_clean
...
```

Outputs land in `shared_processed/` (multi-paper artifacts) and in
`projects/01_epi_transition/{data,tables}/` (paper-01-scoped outputs).

## Running paper 01 (epidemiological transition)

```
cd projects/01_epi_transition
python scripts/sea_comparison.py
python scripts/chiang_30q70.py
python scripts/figures.py
```

## Adding a new paper

1. Pick the next unused number under `projects/` (placeholders 02-12 exist).
2. Populate `README.md`, `scripts/`, `data/`, `figures/`, `tables/`,
   `notebooks/`, `manuscript/`.
3. Import shared utilities: `from shared import <helper>`.
4. Read inputs from `shared_processed/` (or `raw_data/` for IHME-native data).
5. Write paper-specific outputs into the paper's own `data/` and `tables/`.
