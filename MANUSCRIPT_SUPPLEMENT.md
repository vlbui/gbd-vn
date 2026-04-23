# Supplement to: *The epidemiological transition in Vietnam, 1990–2023: a Global Burden of Disease 2023 analysis*

**Companion file to `MANUSCRIPT_MAIN.md`.**
Target journal: *The Lancet Regional Health – Western Pacific*.
All numerical values are drawn from the validated output tables under `D:\gbd\tables\` and `D:\gbd\data\processed\`. Regenerate after any data refresh by rerunning `scripts/01_load_clean.py` → `scripts/06_figures.py` and `scripts/generate_sensitivity_md.py`.

---

## Contents

- S1. Supplementary Methods
  - S1.1 Data extraction and processing
  - S1.2 Age-standardization
  - S1.3 Joinpoint regression — full formulation and reference implementation
  - S1.4 Das Gupta three-factor decomposition — full formulation
  - S1.5 SDI-expected NCD-share regression — leave-one-out peer fit
  - S1.6 30q70 premature-mortality probability — WHO SDG 3.4.1 life-table math
  - S1.7 Uncertainty propagation
  - S1.8 Software and reproducibility
- S2. Cause-list mapping (GBD level-1 → level-2 → sensitivity sub-groups)
- S3. Supplementary Tables
  - Table S1. CMNN level-1 split and NCD-share sensitivity variants
  - Table S2. Full 11-country SEA table — 1990 / 2000 / 2010 / 2023 NCD share, delta, joinpoint AAPC, SDI-expected and obs/exp
  - Table S3. Vietnam sub-period AAPC — log-linear decade windows
  - Table S4. Das Gupta decomposition — numeric components in absolute DALYs
  - Table S5. Vietnam 30q70 year-by-year (NCD and CMNN), 1990–2023
  - Table S6. Regional YLL/YLD and NCD death-rate ranking, 2023
- S4. Supplementary Figures (S1–S8) — legends
- S5. Sensitivity analysis — extended discussion (template paragraphs)
- S6. GATHER reporting checklist
- S7. Data availability, ethics, code deposition
- S8. Supplementary references

---

## S1. Supplementary Methods

### S1.1 Data extraction and processing

GBD 2023 estimates were obtained from the IHME Global Health Data Exchange (GHDx; data release of March 2024) via the GBD Results Tool (https://vizhub.healthdata.org/gbd-results/). The following query dimensions were selected:

- **Locations:** Vietnam, Thailand, Indonesia, Philippines, Malaysia, Myanmar, Cambodia, Lao PDR, Singapore, Brunei Darussalam, Timor-Leste.
- **Measures:** DALYs, YLLs, YLDs, Deaths (with 95% uncertainty intervals).
- **Causes:** all level-1 (CMNN, NCD, Injuries) and all level-2 causes.
- **Age groups:** GBD standard 5-year bands (<1, 1–4, 5–9, …, 95+), "Age-standardized", and "All ages".
- **Sex:** Male, Female, Both.
- **Metric:** "Rate" and "Number".
- **Years:** 1990 through 2023, every year.

The raw export (~280 MB CSV, `data/raw/ihme_gbd_2023_sea_11.csv`) was filtered, reshaped, and cached at `data/processed/*.parquet` by `scripts/01_load_clean.py`. No imputation of missing values was performed; the GBD release contains point estimates for every country-year-age-sex-cause stratum queried.

### S1.2 Age-standardization

We used IHME's published age-standardized rates (GBD 2010 world standard population, 5-year bands 0–95+). For computations requiring reconstruction of age-standardized rates from age-specific rates (e.g., Das Gupta decomposition), we applied the same GBD 2010 weights. Population counts for Vietnam 1990–2023 were taken from GBD 2023's population estimates file.

### S1.3 Joinpoint regression — full formulation and reference implementation

#### S1.3.1 Model

Given an annual rate or share series `y_1, ..., y_T` (T = 34 for 1990–2023), we fit a log-linear piecewise model

```
log(y_t) = α_k + β_k · t       for  τ_{k-1} < t ≤ τ_k,   k = 1, ..., K+1
```

where `τ_0 = 0`, `τ_{K+1} = T`, and `τ_1 < ... < τ_K` are **K** unknown integer breakpoints. Each breakpoint was constrained to sit at least 4 years from the series endpoints and at least 4 years from any other breakpoint, consistent with the NCI Joinpoint Regression Program defaults.

#### S1.3.2 Breakpoint selection — BIC-penalized dynamic programming

We searched over `K ∈ {0, 1, 2, 3}` (maximum 3 breakpoints) and selected the configuration minimising the Bayesian Information Criterion

```
BIC(K) = n · log(SSR(K) / n) + p(K) · log(n)
```

where `n = T`, `SSR(K)` is the residual sum of squares of the K-breakpoint fit on log(y), and `p(K) = 2(K+1) + K` counts the `α_k`, `β_k`, and `τ_k` free parameters. For fixed K, the global-optimal breakpoint positions were found by the Bellman dynamic-programming recursion

```
C(t, k) = min_{s < t} [C(s, k-1) + R(s+1, t)]
```

where `R(s, t)` is the residual sum of squares of the ordinary least-squares fit on `{log(y_s), ..., log(y_t)}`. This is the exact equivalent of the `ruptures.Dynp` algorithm of Killick, Fearnhead & Eckley (2012) [S1], implemented in ~150 lines of pure NumPy at `scripts/utils/joinpoint.py::dp_piecewise_linear()`. The reference implementation depends only on `numpy` and `scipy.stats`; it does not require the `ruptures` package.

#### S1.3.3 AAPC and confidence interval

The annual percent change in segment *k* is `APC_k = 100·(exp(β_k) − 1)`. The average annual percent change (AAPC) across all segments within a window of length `L = Σ L_k` is the length-weighted geometric mean

```
AAPC = 100 · [∏_k (1 + APC_k/100)^{L_k / L} − 1]
```

Equivalently, AAPC = 100·[exp((Σ_k L_k · β_k) / L) − 1]. The 95% confidence interval follows Clegg et al. (2009) [S2] via the delta method:

```
Var(AAPC) ≈ [(AAPC + 100)/100]² · (Σ L_k² · Var(β_k)) / L²
SE(AAPC)  = √Var(AAPC)
95% CI    = AAPC ± 1.96 · SE(AAPC)
```

where `Var(β_k)` is obtained from the segment-specific OLS covariance matrix under the residual variance of segment *k*.

#### S1.3.4 Vietnam joinpoint configurations (1990–2023)

Selected optimum K and breakpoint years for each reported series:

| Series | K | Breakpoints | AAPC (95% CI) |
|---|---:|---|---|
| CMNN rate | 3 | 1998, 2007, 2015 | −4.63 (−4.80, −4.46) |
| NCD rate | 2 | 2005, 2017 | −0.37 (−0.45, −0.30) |
| Injuries rate | 3 | 1996, 2003, 2013 | −1.13 (−1.24, −1.03) |
| NCD share | 3 | 1995, 2005, 2015 | +1.09 (+1.04, +1.15) |
| CMNN share | 3 | 1995, 2005, 2015 | −3.44 (−3.54, −3.33) |
| 30q70 NCD | 2 | 2003, 2015 | −0.25 (−0.33, −0.16) |
| 30q70 CMNN | 3 | 1994, 2005, 2015 | −5.86 (−6.25, −5.47) |
| YLL rate | 3 | 1997, 2007, 2015 | −1.79 (−1.87, −1.71) |
| YLD rate | 2 | 2001, 2015 | −0.34 (−0.37, −0.30) |

*(Breakpoint years are selected by BIC on the full 1990–2023 series and reflect the model's best guess at structural regime shifts; they are not hypothesis tests. See `tables/trend_results.csv` for the full numeric output.)*

### S1.4 Das Gupta three-factor decomposition — full formulation

We decomposed the 1990→2023 change in absolute DALYs using Das Gupta's (1993) symmetric three-factor formulation [S3]. Let

- `P_t` = total population in year *t*,
- `s_{a,t}` = age-share (fraction of population in age band *a* in year *t*), `Σ_a s_{a,t} = 1`,
- `r_{a,t}` = age-specific DALY rate per capita in age band *a* year *t*.

Then total absolute DALYs `D_t = P_t · Σ_a s_{a,t} · r_{a,t} = P_t · S_t · R_t` (notation collapsed to scalar averages for exposition). The 1990→2023 change `ΔD = D_{2023} − D_{1990}` decomposes symmetrically as

```
ΔD  =  ΔP · (S̄ · R̄)      [population-size effect]
    +  P̄ · ΔS · R̄        [age-structure / ageing effect]
    +  P̄ · S̄ · ΔR         [age-specific-rate effect]
```

where `Ā = (A_{1990} + A_{2023}) / 2` and `ΔA = A_{2023} − A_{1990}`. The vectorised implementation at `scripts/utils/decomposition.py::das_gupta_3factor()` evaluates the full age-specific version (no scalar collapse), so that the three effects sum exactly to the observed change. Numerical residuals are of the order 10⁻⁹ DALYs (i.e., floating-point precision; see `residual` column of `tables/decomposition_results.csv`).

### S1.5 SDI-expected NCD-share regression — leave-one-out peer fit

The Socio-Demographic Index (SDI) is the geometric mean of three normalised indicators: total fertility rate under age 25, educational attainment in adults aged 15+, and lag-distributed income per capita [S4]. 2023 SDI values for the 11 SEA countries were obtained from the GBD 2023 SDI release.

For each focal country *c*, we fitted a quadratic regression

```
NCD_share_2023_j  =  β_0 + β_1 · SDI_j + β_2 · SDI_j²  +  ε_j
```

using only the 10 peer countries *j ≠ c* (leave-one-out). The predicted value at `SDI_c` gave the SDI-expected NCD share for country *c*. The observed-to-expected ratio `obs/exp = observed_c / expected_c` quantifies directional positioning against the peer curve. Excluding the focal country from the training data prevents data-leakage that would bias obs/exp toward 1.00 and attenuate the informativeness of the metric.

Pre-computed SDI-expected values and obs/exp ratios for all 11 countries are in `tables/sea_comparison.csv` (columns `ncd_share_expected_2023` and `obs_vs_expected_ratio_2023`).

### S1.6 30q70 premature-mortality probability — WHO SDG 3.4.1 life-table math

The unconditional probability that a person aged 30 will die before reaching 70 from cause group *g* is [S5]

```
30q70_g  =  1 − ∏_{a=30-34}^{65-69} ( 1 − 5·m_{a,g} / (1 + 2.5·m_{a,g}) )
```

where `m_{a,g}` is the cause-group-g death rate per person-year in 5-year age band *a*. The eight age bands span 30–34 through 65–69. The Chiang II adjustment `5·m / (1 + 2.5·m)` converts the age-specific rate to a 5-year probability assuming uniform within-band mortality. The cause-specific `m_{a,g}` were constructed by dividing cause-specific deaths (GBD output) by the population in the same age band and year. Pre-computed 30q70 values are in `data/processed/probability_30q70.csv` (columns `year`, `cause_group`, `probability_30q70`, `probability_30q70_pct`).

For cross-country comparison we repeated the Chiang II calculation identically for each of the 11 SEA countries using GBD 2023 age-band death rates (`data/raw/query6_30q70.csv`; 4 SDG 3.4.1 causes x 11 countries x 8 age bands x 3 sexes x 1980-2023). The resulting Both-sex annual series are in `data/processed/sea_30q70.csv`; a per-country summary (1990/2000/2010/2023 snapshots, delta_pp, relative reduction, log-linear AAPC with 95% CI) is in `tables/sea_30q70_summary.csv` and visualised as Figure 10. The cross-country AAPCs use a single-segment log-linear fit (the pipeline's joinpoint AAPC retains scipy/ruptures as dependencies and is reserved for Vietnam's Table 1 series); for the 1990-2023 ranking this is indistinguishable from the joinpoint result.

### S1.7 Uncertainty propagation

GBD point estimates are accompanied by 95% uncertainty intervals (UI) generated from IHME's internal 1,000-draw posterior. For the main text values we used IHME's published central (mean) estimates with UI bounds; we did not re-draw. AAPC confidence intervals use the Clegg 2009 delta method on the point-estimate series; they reflect regression-fit uncertainty, not upstream GBD posterior uncertainty. A sensitivity check using draws is feasible but was not performed for this manuscript; we flag this as a limitation (main text §4.4).

### S1.8 Software and reproducibility

All analyses were performed in Python 3.11 with the following package versions:

- `numpy` 1.26.x
- `pandas` 2.1.x
- `scipy` 1.11.x
- `matplotlib` 3.8.x
- `plotly` 5.17.x
- `jupyter` 4.0.x

No internet access is required to run the pipeline. The full pipeline `scripts/01_load_clean.py → 02_metrics.py → 03_trends.py → 04_decompose.py → 05_peers.py → 06_figures.py` runs in under 10 minutes on a 2020-era laptop (Intel i5, 16 GB RAM). The Jupyter notebook `analysis.ipynb` reproduces all tables and figures end-to-end.

---

## S2. Cause-list mapping

### S2.1 GBD level-1 groups (main analysis)

| Level-1 group | GBD ID | Definition |
|---|---|---|
| **CMNN** | Communicable, maternal, neonatal, and nutritional diseases | Union of: HIV/AIDS and sexually transmitted infections; respiratory infections and tuberculosis; enteric infections; neglected tropical diseases and malaria; other infectious diseases; maternal and neonatal disorders; nutritional deficiencies. |
| **NCD** | Non-communicable diseases | Neoplasms; cardiovascular diseases; chronic respiratory diseases; digestive diseases; neurological disorders; mental disorders; substance use disorders; diabetes and kidney diseases; skin and subcutaneous diseases; sense organ diseases; musculoskeletal disorders; other NCDs. |
| **Injuries** | Injuries | Transport injuries; unintentional injuries; self-harm and interpersonal violence. |

### S2.2 CMNN sensitivity split

| Sub-group | Component level-2 causes |
|---|---|
| **Communicable only (C-only)** | HIV/AIDS and sexually transmitted infections; respiratory infections and tuberculosis; enteric infections; neglected tropical diseases and malaria; other infectious diseases |
| **Maternal + Neonatal + Nutritional (M+N+N)** | Maternal and neonatal disorders (includes maternal causes, neonatal preterm birth, neonatal encephalopathy, neonatal sepsis, hemolytic disease, other neonatal causes); nutritional deficiencies (protein-energy malnutrition, iron-deficiency anemia, iodine, vitamin A, other) |

---

## S3. Supplementary Tables

### Table S1. CMNN level-1 split and NCD-share sensitivity variants

*Source: `tables/table_s1_cmnn_sensitivity.csv`. Age-standardized DALY rate per 100,000 unless otherwise noted. AAPC via joinpoint regression, BIC-penalized DP piecewise-linear fit, max 3 breakpoints, 95% CI via Clegg 2009 delta method.*

| Group | 1990 | 2000 | 2010 | 2023 | AAPC% (95% CI) |
|---|---:|---:|---:|---:|---|
| CMNN (full, main analysis) | 13,295.9 | 8,549.0 | 5,870.2 | 4,022.1 | **−4.63** (−4.80, −4.46) |
| Communicable only (sensitivity) | 8,908.8 | 5,611.2 | 4,001.6 | 2,688.2 | **−5.05** (−5.24, −4.86) |
| Maternal+Neonatal+Nutritional (sensitivity) | 4,387.1 | 2,937.8 | 1,868.6 | 1,334.0 | **−3.45** (−3.66, −3.25) |
| Non-communicable diseases | 21,688.2 | 19,960.4 | 19,742.8 | 19,282.8 | **−0.37** (−0.45, −0.30) |
| Injuries | 5,942.0 | 5,409.9 | 4,683.0 | 3,981.8 | **−1.13** (−1.24, −1.03) |
| NCD share vs full CMNN (main, % of total DALYs) | 52.99 | 58.85 | 65.17 | **70.67** | — |
| NCD share vs C-only CMNN (% of total DALYs) | 59.36 | 64.43 | 69.45 | **74.30** | — |
| NCD share vs M+N+N only CMNN (% of total DALYs) | 67.74 | 70.51 | 75.08 | **78.39** | — |

### Table S2. Full 11-country SEA table — NCD-share trajectories and SDI-expected positioning

*Source: `tables/sea_comparison.csv`. Columns: 1990/2000/2010/2023 NCD share (%); delta = 2023 − 1990 (pp); joinpoint AAPC (%/year) with 95% CI; SDI-expected 2023 NCD share (%) from leave-one-out quadratic fit; observed/expected ratio. Sorted by 2023 NCD share descending.*

| Country | 1990 | 2000 | 2010 | 2023 | Δ (pp) | AAPC (95% CI) | Expected 2023 | obs/exp |
|---|---:|---:|---:|---:|---:|---|---:|---:|
| Brunei Darussalam | 76.12 | 78.79 | 80.25 | 81.26 | +5.15 | +0.22 (+0.17, +0.28) | 77.30 | 1.051 |
| Singapore | 78.05 | 79.22 | 79.56 | 79.28 | +1.24 | +0.10 (+0.04, +0.15) | 83.88 | 0.945 |
| Malaysia | 67.40 | 71.98 | 72.48 | 75.04 | +7.65 | +0.84 (+0.68, +1.01) | 74.70 | 1.005 |
| **Vietnam** | **52.99** | **58.85** | **65.17** | **70.67** | **+17.67** | **+1.09 (+1.04, +1.15)** | **67.08** | **1.053** |
| Thailand | 61.32 | 61.73 | 66.50 | 68.38 | +7.05 | +0.45 (+0.35, +0.56) | 70.55 | 0.969 |
| Indonesia | 46.92 | 55.18 | 62.96 | 68.04 | +21.12 | +0.77 (+0.46, +1.09) | 69.22 | 0.983 |
| Philippines | 55.09 | 62.47 | 65.14 | 67.34 | +12.25 | +0.98 (+0.80, +1.17) | 69.65 | 0.967 |
| Myanmar | 44.73 | 51.99 | 59.20 | 65.39 | +20.65 | +0.62 (+0.53, +0.71) | 62.19 | 1.051 |
| Cambodia | 37.28 | 40.83 | 54.99 | 63.83 | +26.55 | +1.82 (+1.58, +2.07) | 60.53 | 1.054 |
| Timor-Leste | 36.13 | 44.41 | 52.00 | 59.58 | +23.45 | +0.79 (+0.59, +0.99) | 61.58 | 0.968 |
| Lao PDR | 28.73 | 37.29 | 49.74 | 58.65 | +29.92 | +2.30 (+2.14, +2.46) | 62.96 | 0.932 |

### Table S3. Vietnam sub-period AAPC — decade-window log-linear fits

*Source: `tables/trend_results.csv`. Single-segment log-linear regression on each decade window; full-window 1990–2023 row = joinpoint regression (BIC-selected K). `n_obs` = number of annual observations in the window.*

| Cause / Metric | Window | AAPC (%) | 95% CI | p-value | n_obs |
|---|---|---:|---|---:|---:|
| DALY — CMNN | 1990–2023 (joinpoint) | −4.63 | (−4.80, −4.46) | <0.001 | 34 |
| DALY — CMNN | 1990–2000 | −4.35 | (−4.62, −4.09) | <0.001 | 11 |
| DALY — CMNN | 2000–2010 | −3.58 | (−3.78, −3.37) | <0.001 | 11 |
| DALY — CMNN | 2010–2023 | −2.04 | (−3.24, −0.82) | 0.007 | 14 |
| DALY — NCD | 1990–2023 (joinpoint) | −0.37 | (−0.45, −0.30) | <0.001 | 34 |
| DALY — NCD | 1990–2000 | −0.86 | (−0.89, −0.82) | <0.001 | 11 |
| DALY — NCD | 2000–2010 | −0.10 | (−0.11, −0.08) | <0.001 | 11 |
| DALY — NCD | 2010–2023 | −0.28 | (−0.38, −0.18) | <0.001 | 14 |
| DALY — Injuries | 1990–2023 (joinpoint) | −1.13 | (−1.24, −1.03) | <0.001 | 34 |
| DALY — Injuries | 1990–2000 | −0.86 | (−1.12, −0.60) | <0.001 | 11 |
| DALY — Injuries | 2000–2010 | −1.55 | (−1.65, −1.44) | <0.001 | 11 |
| DALY — Injuries | 2010–2023 | −1.37 | (−1.47, −1.26) | <0.001 | 14 |
| YLL — All causes | 1990–2023 (joinpoint) | −1.79 | (−1.87, −1.71) | <0.001 | 34 |
| YLL — All causes | 1990–2000 | −2.37 | (−2.47, −2.27) | <0.001 | 11 |
| YLL — All causes | 2000–2010 | −1.41 | (−1.49, −1.32) | <0.001 | 11 |
| YLL — All causes | 2010–2023 | −1.09 | (−1.29, −0.88) | <0.001 | 14 |
| YLD — All causes | 1990–2023 (joinpoint) | −0.34 | (−0.38, −0.30) | <0.001 | 34 |
| YLD — All causes | 1990–2000 | −0.58 | (−0.65, −0.51) | <0.001 | 11 |
| YLD — All causes | 2000–2010 | −0.41 | (−0.43, −0.40) | <0.001 | 11 |
| YLD — All causes | 2010–2023 | −0.03 | (−0.10, +0.04) | 0.439 | 14 |

**Note.** The YLD rate 2010–2023 sub-period AAPC is not statistically different from zero (p = 0.44), indicating that YLD-rate progress has plateaued in the most recent decade. By contrast, YLL-rate decline has continued (−1.09%/year, p < 0.001), the classical signature of a disability-dominated epidemiological phase.

### Table S4. Das Gupta decomposition — numeric components

*Source: `tables/decomposition_results.csv`. Contributions to 1990→2023 change in absolute DALYs. The three effects sum to the observed change to within floating-point precision (residuals < 10⁻⁹).*

| Cause group | Population-size effect | Age-structure effect (ageing) | Age-specific-rate effect | Total decomposed change | Observed change | Residual | Direction |
|---|---:|---:|---:|---:|---:|---:|---|
| **NCD** | +6,257,108 | +6,080,731 | −1,710,855 | +10,626,984 | +10,626,984 | <10⁻⁹ | increase |
| **CMNN** | +3,247,842 | −1,508,711 | −8,184,520 | −6,445,388 | −6,445,388 | <10⁻⁹ | decrease |

*(All figures in absolute DALYs, 1990–2023 window. Positive values add to burden, negative values remove burden. Population-size: ΔP · S̄ · R̄; age-structure: P̄ · ΔS · R̄; age-specific rate: P̄ · S̄ · ΔR.)*

### Table S5. Vietnam 30q70 year-by-year (NCD and CMNN), 1990–2023

*Source: `data/processed/probability_30q70.csv`. Unconditional probability (%) that a 30-year-old dies before age 70 from cause group *g*, computed from 5-year age-band death rates via the Chiang II life-table adjustment. Values rounded to 2 decimal places.*

| Year | NCD (%) | CMNN (%) | Year | NCD (%) | CMNN (%) |
|---:|---:|---:|---:|---:|---:|
| 1990 | 25.02 | 6.18 | 2007 | 22.69 | 3.50 |
| 1991 | 24.87 | 5.93 | 2008 | 22.71 | 3.44 |
| 1992 | 24.70 | 5.69 | 2009 | 22.74 | 3.38 |
| 1993 | 24.48 | 5.45 | 2010 | 22.70 | 3.29 |
| 1994 | 24.22 | 5.20 | 2011 | 22.53 | 3.18 |
| 1995 | 23.95 | 4.97 | 2012 | 22.49 | 3.07 |
| 1996 | 23.68 | 4.73 | 2013 | 22.50 | 3.03 |
| 1997 | 23.42 | 4.50 | 2014 | 22.39 | 2.92 |
| 1998 | 23.26 | 4.30 | 2015 | 22.34 | 2.81 |
| 1999 | 22.95 | 4.11 | 2016 | 22.30 | 2.65 |
| 2000 | 22.76 | 3.98 | 2017 | 22.12 | 2.55 |
| 2001 | 22.67 | 3.89 | 2018 | 22.08 | 2.46 |
| 2002 | 22.69 | 3.80 | 2019 | 22.04 | 2.36 |
| 2003 | 22.66 | 3.72 | 2020 | 21.82 | 2.42 |
| 2004 | 22.64 | 3.64 | 2021 | 20.71 | 5.99 |
| 2005 | 22.65 | 3.61 | 2022 | 21.52 | 3.18 |
| 2006 | 22.64 | 3.56 | **2023** | **21.80** | **2.12** |

**Note on the 2020–2021 anomaly.** The sharp spike in CMNN 30q70 from 2.42% (2020) to 5.99% (2021), followed by a return to 3.18% (2022) and 2.12% (2023), reflects the direct and indirect mortality impact of the COVID-19 pandemic on adults aged 30–69 in Vietnam. The 2020 NCD 30q70 value (21.82%) is lower than 2019 (22.04%), consistent with short-term displacement of NCD deaths by COVID-19 deaths (which GBD classifies under respiratory infections, a CMNN category in the level-1 grouping used here). By 2023, both series had largely returned to their pre-pandemic trajectories.

### Table S5b. SEA 30q70 cross-country summary (WHO SDG 3.4.1 strict, 4 causes), 1990-2023

*Source: `tables/sea_30q70_summary.csv`. Strict SDG 3.4.1 30q70 = probability (%) that a 30-year-old dies before age 70 from cardiovascular diseases, neoplasms, diabetes and kidney diseases, or chronic respiratory diseases, computed identically for all 11 SEA countries via Chiang II on GBD 2023 age-band death rates. AAPC is a single-segment log-linear fit with normal-theory 95% CI (see S1.6); sorted by 2023 30q70 (descending). Vietnam is **bold**.*

| Country | 1990 | 2000 | 2010 | 2023 | delta (pp) | Rel. reduction (%) | AAPC % per year (95% CI) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Myanmar | 35.90 | 35.26 | 32.59 | 32.39 | -3.50 | 9.8 | -0.45 (-0.52, -0.38) |
| Lao PDR | 26.20 | 27.44 | 27.42 | 29.48 | +3.28 | -12.5 | +0.23 (+0.18, +0.27) |
| Indonesia | 24.83 | 23.60 | 26.46 | 25.10 | +0.27 | -1.1 | +0.34 (+0.23, +0.45) |
| Philippines | 21.73 | 23.76 | 24.97 | 23.18 | +1.45 | -6.7 | +0.33 (+0.22, +0.44) |
| Timor-Leste | 23.36 | 22.31 | 19.90 | 22.13 | -1.23 | 5.3 | -0.22 (-0.37, -0.07) |
| **Vietnam** | **22.17** | **20.20** | **20.20** | **19.50** | **-2.66** | **12.0** | **-0.37 (-0.42, -0.31)** |
| Cambodia | 21.07 | 19.54 | 19.32 | 19.28 | -1.78 | 8.5 | -0.36 (-0.42, -0.31) |
| Malaysia | 23.63 | 23.07 | 19.52 | 18.58 | -5.05 | 21.4 | -0.86 (-0.98, -0.75) |
| Brunei Darussalam | 26.81 | 22.80 | 18.62 | 16.73 | -10.08 | 37.6 | -1.61 (-1.70, -1.53) |
| Thailand | 21.24 | 22.18 | 17.12 | 15.46 | -5.77 | 27.2 | -1.44 (-1.65, -1.23) |
| Singapore | 22.46 | 16.19 | 10.63 | 7.68 | -14.77 | 65.8 | -3.60 (-3.71, -3.49) |

**Note on definition.** Vietnam's Table 1 and Figure 9 values use the broad GBD level-1 NCD aggregate (all ~12 level-2 NCD causes) for internal consistency with the level-1 cause-composition analysis; the 1990 and 2023 values are therefore 25.02% and 21.80%, slightly higher than the strict SDG 3.4.1 figures above. The strict definition above is what is comparable across countries and is the correct reference for SDG 3.4.1 reporting.

### Table S6. Regional YLL/YLD ratio and NCD death-rate ranking, 2023

*Source: `tables/sea_yll_yld_ratio.csv` and `tables/sea_ncd_death_rate_2023.csv`. All-cause YLL and YLD rates per 100,000; age-standardized NCD death rate per 100,000. Sorted by YLL/YLD descending (= higher ratio indicates more mortality-dominated burden).*

| Country | YLL rate | YLD rate | YLL/YLD | NCD death rate (95% UI) | NCD death rank |
|---|---:|---:|---:|---:|---:|
| Lao PDR | 36,318.4 | 9,841.0 | 3.69 | 767.7 (702.4–839.0) | 2 |
| Myanmar | 37,840.7 | 10,830.7 | 3.49 | 926.9 (859.6–994.6) | 1 |
| Timor-Leste | 28,566.5 | 10,353.7 | 2.76 | 639.7 (580.5–707.4) | 3 |
| Philippines | 23,919.6 | 10,228.2 | 2.34 | 615.3 (596.2–635.1) | 4 |
| Indonesia | 24,038.4 | 10,280.9 | 2.34 | 567.8 (528.4–618.7) | 5 |
| Cambodia | 22,510.5 | 10,565.9 | 2.13 | 540.6 (495.6–585.2) | 6 |
| **Vietnam** | **17,687.7** | **9,599.0** | **1.84** | **492.3 (450.5–531.3)** | **8** |
| Thailand | 16,483.8 | 10,205.1 | 1.62 | 406.1 (393.5–420.2) | 10 |
| Malaysia | 15,691.2 | 9,996.7 | 1.57 | 501.1 (477.0–526.9) | 7 |
| Brunei Darussalam | 13,758.5 | 10,248.0 | 1.34 | 491.1 (468.5–513.6) | 9 |
| Singapore | 6,276.7 | 9,426.6 | 0.67 | 236.0 (226.4–247.0) | 11 |

---

## S4. Supplementary Figures — legends

**Figure S1. Vietnam absolute DALYs by level-1 cause group, 1990–2023.** Line plot of absolute DALY counts (millions) for CMNN, NCD, Injuries. 95% UI bands shaded. Companion to Figure 1 in the main text, showing absolute rather than age-standardized metrics. Source: `data/processed/daly_absolute.csv`.

**Figure S2. Vietnam age-specific DALY rates, selected years (1990, 2000, 2010, 2023).** 4×3 panel grid: rows = cause groups (CMNN, NCD, Injuries), columns = years. X-axis: GBD 5-year age band. Y-axis: DALY rate per 100,000 (log scale). Shows the leftward collapse of CMNN mass (<5 band in 1990 → negligible by 2023) and the rightward consolidation of NCD mass (65+ bands).

**Figure S3. Vietnam cause-specific DALY rate trajectories for top 10 level-2 causes, 1990–2023.** Multi-line plot with 95% UI bands. Causes ranked by 2023 age-standardized rate. Companion to Figure 2 (heatmap). Source: level-2 rows of `data/processed/daly_rates.csv`.

**Figure S4. Figure 8 (CMNN sensitivity, two-panel).** **Panel (A)** Main-analysis NCD share vs full CMNN group, 1990–2023, joinpoint fit overlaid. **Panel (B)** Sensitivity NCD share vs C-only (red) and vs M+N+N (green), same years, joinpoint fits overlaid. Source: `figures/static/fig8_cmnn_sensitivity.png` / `figures/html/fig8_cmnn_sensitivity.html`.

**Figure S5. SEA NCD-share trajectories, 1990–2023 (small-multiples).** 11-panel small-multiples plot, one panel per SEA country, same X/Y scales. Vietnam panel highlighted in bold. Companion to Figure 4 main panel A.

**Figure S6. SEA 2023 NCD share vs SDI — per-country leave-one-out quadratic fits.** 11-panel small-multiples plot, one panel per focal country, each panel showing the quadratic SDI fit trained on the other 10 countries, with the focal country annotated for obs/exp ratio.

**Figure S7. AAPC forest plot, 11 SEA countries, NCD share of total DALYs.** Horizontal forest plot: each country's joinpoint AAPC with 95% CI, sorted by point estimate. Vietnam highlighted. Source: `tables/sea_comparison.csv`.

**Figure S8. 30q70 trajectories for Vietnam — sub-period log-linear fits vs joinpoint fit.** Two-panel plot: **(A)** NCD 30q70 with both fits overlaid; **(B)** CMNN 30q70 with both fits overlaid. Illustrates the small numerical difference between the two fitting approaches on the Vietnam series.

*(All supplementary figures are generated by `scripts/06_figures.py` and deposited under `figures/static/` and `figures/html/`. Vector PDF versions for production are at `figures/static/*.pdf`.)*

---

## S5. Sensitivity analysis — extended discussion

*(The following template paragraphs are reproduced from `SENSITIVITY_DISCUSSION.md` for completeness; the main-text §3.8 contains the condensed summary.)*

Our main analysis follows the GBD 2023 convention of treating communicable, maternal, neonatal, and nutritional diseases (CMNN) as a single level-1 cause group. To probe the robustness of the epidemiological-transition narrative to this framing, we repeated the core calculations after separating CMNN into a communicable-only sub-group (C-only: HIV/AIDS and sexually transmitted infections, respiratory infections and tuberculosis, enteric infections, neglected tropical diseases and malaria, and other infectious diseases) and a maternal + neonatal + nutritional sub-group (M+N+N).

Both sub-groups declined substantially between 1990 and 2023 in age-standardized DALY rate terms. The communicable-only rate fell from 8,908.8 to 2,688.2 per 100,000 (joinpoint AAPC −5.05%/year, 95% CI −5.24 to −4.86) and the M+N+N rate fell from 4,387.1 to 1,334.0 per 100,000 (joinpoint AAPC −3.45%/year, 95% CI −3.66 to −3.25). The transition signal holds under either framing: both sub-groups lost ~70% of their 1990 burden over the study period.

The two sub-groups, however, fell at materially different tempos — communicable-only was ~1.6 percentage-points/year faster than M+N+N in joinpoint AAPC terms. This difference reflects distinct segment-wise dynamics: communicable-disease burden dropped sharply after 2000 with the scale-up of HIV/AIDS and tuberculosis control, whereas M+N+N burden had already begun falling in the 1990s and decelerated in the 2010s as neonatal mortality approached a floor.

The NCD share of total DALYs in 2023 differs by choice of CMNN denominator: 70.67% against the full CMNN group (main analysis), 74.30% when compared only against communicable diseases, and 78.39% when compared only against M+N+N causes. We report the main-analysis NCD share in the body of the paper because it is directly comparable across countries and years as published by IHME, and we include the sub-group split (Figure S4 / Figure 8, Table S1) so readers can re-anchor the metric to a narrower definition if desired.

The residual CMNN burden in Vietnam is split roughly 2:1 between communicable and M+N+N causes (2,688 vs 1,334 per 100,000 in 2023), essentially the same 2:1 ratio as in 1990 (8,909 vs 4,387). Despite different joinpoint AAPCs, the 1990→2023 endpoint log-linear rates of the two sub-groups are nearly identical (both ~−3.6%/year simple), which is why the composition ratio of the residual CMNN burden is preserved even as the absolute magnitude collapsed. This pattern is consistent with Vietnam's sustained gains in both maternal-child health and infectious-disease control over the study period.

---

## S6. GATHER reporting checklist

*(Guidelines for Accurate and Transparent Health Estimates Reporting, Stevens et al. 2016 [S6]. We indicate where each item is reported.)*

| Item | Checklist content | Reported in |
|---:|---|---|
| 1 | Define indicator(s), populations, timepoint(s) | Main §1, Methods §2.1 |
| 2 | Statement of rationale for new estimate | Main §1 |
| 3 | List of all data sources used | Methods §2.1, Supplement S1.1 |
| 4 | Identification of specific inclusion/exclusion criteria | Methods §2.1, Supplement S1.1–S1.2 |
| 5 | Provision of publicly-accessible data source links | Supplement S7 |
| 6 | Description of steps taken to access non-public data | N/A — all data public |
| 7 | Handling of input data concerns (incomplete, invalid, outliers) | Supplement S1.7 |
| 8 | Description of pre-existing adjustments to input data | Methods §2.2 (IHME age-standardization) |
| 9 | List of computations, models, formulas used | Methods §2.3–§2.6, Supplement S1.3–S1.6 |
| 10 | Description of all data and variable transformations | Supplement S1.1 |
| 11 | Model summary | Supplement S1.3 (joinpoint), S1.4 (Das Gupta), S1.5 (SDI fit) |
| 12 | Computationally reproducible — code and data availability | Supplement S7 |
| 13 | Description of results quantifying uncertainty | Main §3 (95% CIs), Supplement S1.7 |
| 14 | Presentation of all estimates at level of analysis | Tables S1–S6 |
| 15 | Numbers of input observations | Supplement S1.1 |
| 16 | Sensitivity analyses | Main §3.8, Supplement S5 |
| 17 | Discussion of limitations | Main §4.4 |
| 18 | Ethics statement | Methods §2.8 |

*(Items 19–28 of GATHER apply to administrative data quality and are not applicable to secondary analyses of IHME-published GBD estimates. The IHME GBD 2023 methodology publications cover items 19–28 for the upstream estimation pipeline.)*

---

## S7. Data availability, ethics, code deposition

**Data availability.** All input data are publicly available from the IHME Global Health Data Exchange:
- GBD 2023 Results Tool: https://vizhub.healthdata.org/gbd-results/
- GBD 2023 SDI estimates: https://ghdx.healthdata.org/record/ihme-data/global-burden-disease-study-2023-gbd-2023-socio-demographic-index-sdi-1950-2023
- Population estimates: https://ghdx.healthdata.org/record/ihme-data/global-burden-disease-study-2023-gbd-2023-population-estimates-1950-2023

Processed analytic tables (rates, shares, decomposition, 30q70) are deposited with the manuscript code.

**Ethics.** This study used publicly available aggregated data and did not require ethical approval.

**Code deposition.** The full analysis pipeline — data loading, cleaning, metric computation, trend fitting, decomposition, peer regression, figure generation — is available as a single Python 3.11 project:
- GitHub: `https://github.com/[placeholder]/vietnam-epi-transition-gbd2023`
- Zenodo DOI (assigned on acceptance): `10.5281/zenodo.[placeholder]`

The project ships with `requirements.txt`, `analysis.ipynb`, and seven numbered scripts. Runtime: <10 minutes on a 2020-era laptop with no internet access once the raw GBD export is cached locally.

---

## S8. Supplementary references

[S1] Killick R, Fearnhead P, Eckley IA. Optimal detection of changepoints with a linear computational cost. *J Am Stat Assoc* 2012;107:1590–8.
[S2] Clegg LX, Hankey BF, Tiwari R, Feuer EJ, Edwards BK. Estimating average annual per cent change in trend analysis. *Stat Med* 2009;28:3670–82.
[S3] Das Gupta P. *Standardization and decomposition of rates: a user's manual.* Current Population Reports P23-186. Washington DC: US Bureau of the Census, 1993.
[S4] Lim SS, Updike RL, Kaldjian AS, et al. Measuring human capital: a systematic analysis of 195 countries and territories, 1990–2016. *Lancet* 2018;392:1217–34.
[S5] World Health Organization. *Global action plan for the prevention and control of non-communicable diseases 2013–2020.* Geneva: WHO, 2013.
[S6] Stevens GA, Alkema L, Black RE, et al. Guidelines for accurate and transparent health estimates reporting: the GATHER statement. *Lancet* 2016;388:e19–23.
[S7] Kim H-J, Fay MP, Feuer EJ, Midthune DN. Permutation tests for joinpoint regression with applications to cancer rates. *Stat Med* 2000;19:335–51.
[S8] GBD 2021 Demographics Collaborators. Global age-sex-specific mortality, life expectancy, and population estimates in 204 countries and territories and 811 subnational locations, 1950–2021. *Lancet* 2024;403:1989–2056.

---

*End of Supplement.*
