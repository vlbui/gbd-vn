# Main Results — GBD Vietnam Epidemiological Transition, 1990–2023

**Target journal:** *Lancet Regional Health — Western Pacific*
**Data source:** Global Burden of Disease 2023, 11 Southeast-Asian countries

All numbers below are pulled directly from `tables/` and `data/processed/`
and regenerate with the pipeline (`python analysis.py` or
`run_analysis.ipynb`).

**Methodology note.** The analysis uses only conventional, literature-backed
indicators: cause composition shares, Das Gupta decomposition (Das Gupta
1993), AAPC via **joinpoint regression with up to 3 joinpoints selected by
BIC and 95% CI via the delta method** (Kim HJ et al. Stat Med 2000;19:335-51;
Clegg LX et al. Stat Med 2009;28:3670-82), implemented in pure NumPy as a
BIC-penalized dynamic-programming piecewise-linear fit (Dynp-equivalent) —
no dependency on the `ruptures` package. 30q70 premature-mortality
probability follows the WHO Global Action Plan for the Prevention and
Control of NCDs 2013-2020 (SDG indicator 3.4.1), and SDI-expected
trajectories are computed by quadratic regression of NCD share on SDI,
fitted on the 10 SEA peers excluding the focal country to avoid
data-leakage (Lim SS et al. Lancet 2018;392:2091-138). All full-period
AAPC values in Tables 1, 2 (full period), 4 and S1 come from the same
`utils.joinpoint_aapc` helper, so they reconcile across tables. Sub-period
AAPCs in Table 2 (1990–2000, 2000–2010, 2010–2023) use single-segment
log-linear regression because ~10 yearly observations per decade are too
few for joinpoint BIC selection. No ad-hoc indices are used.

---

## 1. Headline findings

- Vietnam's **age-standardized DALY rate** fell for every level-1 cause group between 1990 and 2023, but at different speeds (joinpoint AAPC): **CMNN rate −4.63%/yr**, **Injuries rate −1.13%/yr**, **NCD rate −0.37%/yr**.
- **NCD share of total DALYs** rose from **52.99% (1990) to 70.67% (2023)** — a **+17.67 percentage-point** absolute change and a joinpoint AAPC of **+1.09%/year** (95% CI +1.04, +1.15, 3 joinpoints selected by BIC). Vietnam is now the **4th-ranked of 11 SEA countries** on this metric, up from **6th** in 1990.
- Vietnam's NCD share in 2023 sits **5.3% above** the SDI-expected trajectory (obs/exp = **1.053**; quadratic fit on the 10 SEA peers, focal country excluded) — **modestly above** what its level of development predicts.
- Premature-NCD-mortality probability 30q70 fell from **25.02% (1990) to 21.80% (2023)**, joinpoint AAPC **−0.25%/yr** — a modest decline that leaves Vietnam far from the SDG 3.4 target of a one-third reduction by 2030.
- Premature-CMNN-mortality probability 30q70 fell sharply from **6.18% to 2.12%**, joinpoint AAPC **−5.86%/yr**.
- The absolute NCD DALY count grew by **+10.6 million** — driven roughly equally by population growth and ageing, partly offset by falling age-specific NCD rates.
- YLL/YLD ratio dropped from **2.85 → 1.84** (joinpoint AAPC **−1.51%/yr**): classic *compression of mortality, expansion of morbidity*.

---

## 2. Table 1 — Vietnam key-metric summary

*(`tables/table1_summary.csv`; all AAPC values from joinpoint regression,
BIC-penalized DP piecewise-linear fit, max 3 breakpoints, 95% CI by
Clegg 2009 delta method)*

| Metric | 1990 | 2000 | 2010 | 2023 | AAPC% (95% CI) |
|---|---:|---:|---:|---:|---|
| CMNN age-std DALY rate /100k | 13,295.9 | 8,549.0 | 5,870.2 | 4,022.1 | **−4.63** (−4.80, −4.46) |
| NCD age-std DALY rate /100k | 21,688.2 | 19,960.4 | 19,742.8 | 19,282.8 | **−0.37** (−0.45, −0.30) |
| Injuries age-std DALY rate /100k | 5,942.0 | 5,409.9 | 4,683.0 | 3,981.8 | **−1.13** (−1.24, −1.03) |
| CMNN share of total DALYs (%) | 32.49 | 25.20 | 19.38 | 14.74 | **−3.44** (−3.54, −3.33) |
| **NCD share of total DALYs (%)** | **52.99** | **58.85** | **65.17** | **70.67** | **+1.09** (+1.04, +1.15) |
| Injuries share of total DALYs (%) | 14.52 | 15.95 | 15.46 | 14.59 | +0.17 (+0.03, +0.30) |
| CMNN/NCD ratio | 0.613 | 0.428 | 0.297 | 0.209 | **−4.41** (−4.57, −4.25) |
| 30q70 NCD probability (%) | 25.02 | 22.76 | 22.70 | 21.80 | **−0.25** (−0.33, −0.16) |
| 30q70 CMNN probability (%) | 6.18 | 3.98 | 3.29 | 2.12 | **−5.86** (−6.25, −5.47) |
| YLL rate /100k | 30,304.5 | 23,903.6 | 20,687.4 | 17,687.7 | **−1.79** (−1.87, −1.71) |
| YLD rate /100k | 10,621.7 | 10,015.7 | 9,608.7 | 9,599.0 | **−0.34** (−0.37, −0.30) |
| YLL/YLD ratio | 2.85 | 2.39 | 2.15 | 1.84 | **−1.51** (−1.59, −1.43) |

---

## 3. Table 2 — Period-specific AAPC, Vietnam

*(`tables/trend_results.csv`; 1990–2023 full-period row = joinpoint
regression and matches Table 1; decade sub-periods = single-segment
log-linear regression)*

| Cause | 1990–2023 (joinpoint) | 1990–2000 | 2000–2010 | 2010–2023 |
|---|---:|---:|---:|---:|
| CMNN DALY rate | −4.63 (−4.80, −4.46) | −4.35 (−4.62, −4.09) | −3.58 (−3.78, −3.37) | −2.04 (−3.24, −0.82) |
| NCD DALY rate | −0.37 (−0.45, −0.30) | −0.86 (−0.89, −0.82) | −0.10 (−0.11, −0.08) | −0.28 (−0.38, −0.18) |
| Injuries DALY rate | −1.13 (−1.24, −1.03) | −0.86 (−1.12, −0.60) | −1.55 (−1.65, −1.44) | −1.37 (−1.47, −1.26) |
| YLL rate (all causes) | −1.79 (−1.87, −1.71) | −2.37 (−2.47, −2.27) | −1.41 (−1.49, −1.32) | −1.09 (−1.29, −0.88) |
| YLD rate (all causes) | −0.34 (−0.38, −0.30) | −0.58 (−0.65, −0.51) | −0.41 (−0.43, −0.40) | −0.03 (−0.10, +0.04) |

All full-period and decade coefficients are statistically significant
(p < 0.001) except YLD rate in 2010–2023 (p = 0.44), indicating that
disability burden has **plateaued** over the last decade while mortality
continues to fall.

---

## 4. Table 3 — Das Gupta decomposition of 1990→2023 DALY change

*(`tables/decomposition_results.csv`, absolute DALYs; Das Gupta 1993)*

| Component | NCD | CMNN |
|---|---:|---:|
| Population size effect | +6,257,108 | +3,247,842 |
| Age structure (ageing) effect | +6,080,731 | −1,508,711 |
| Age-specific rate effect | −1,710,855 | −8,184,520 |
| **Total (observed) change** | **+10,626,984** | **−6,445,388** |
| Direction | increase | decrease |

For NCDs, **population growth (+6.26 M)** and **population ageing
(+6.08 M)** each add roughly 6 million DALYs; falling age-specific rates
pull back only 1.7 million. For CMNN, demographic pressures are smaller,
while falling age-specific rates (−8.2 M) dominate and drive the overall
decline.

---

## 5. Table 4 — SEA NCD-share ranking, delta, joinpoint AAPC and SDI-expected ratio

*(`tables/sea_comparison.csv`, age-standardized DALY shares, Both sex;
joinpoint AAPC via BIC-penalized dynamic-programming piecewise-linear
regression (max 3 breakpoints) with delta-method 95% CI; SDI-expected
values from a quadratic fit of NCD share on SDI over the 10 SEA peers,
focal country excluded to avoid data-leakage; sorted by 2023 NCD share)*

| Country | NCD share 1990 | NCD share 2023 | Δ (pp) | Joinpoint AAPC % (95% CI) | Obs/Exp 2023 |
|---|---:|---:|---:|---:|---:|
| Brunei Darussalam | 76.12 | 81.26 | +5.15 | +0.22 (+0.17, +0.28) | 1.051 |
| Singapore | 78.05 | 79.28 | +1.24 | +0.10 (+0.04, +0.15) | 0.945 |
| Malaysia | 67.40 | 75.04 | +7.65 | +0.84 (+0.68, +1.01) | 1.005 |
| **Vietnam** | **52.99** | **70.67** | **+17.67** | **+1.09 (+1.04, +1.15)** | **1.053** |
| Thailand | 61.32 | 68.38 | +7.05 | +0.45 (+0.35, +0.56) | 0.969 |
| Indonesia | 46.92 | 68.04 | +21.12 | +0.77 (+0.46, +1.09) | 0.983 |
| Philippines | 55.09 | 67.34 | +12.25 | +0.98 (+0.80, +1.17) | 0.967 |
| Myanmar | 44.73 | 65.39 | +20.65 | +0.62 (+0.53, +0.71) | 1.051 |
| Cambodia | 37.28 | 63.83 | +26.55 | +1.82 (+1.58, +2.07) | 1.054 |
| Timor-Leste | 36.13 | 59.58 | +23.45 | +0.79 (+0.59, +0.99) | 0.968 |
| Lao PDR | 28.73 | 58.65 | +29.92 | +2.30 (+2.14, +2.46) | 0.932 |

Vietnam is the **largest rank mover** in the region (6th → 4th, +2 ranks)
and the biggest absolute climber (+17.67 pp) among the already-transitioned
top cluster whose 1990 NCD share already exceeded 50% (Singapore, Brunei,
Malaysia, Thailand, Philippines, Vietnam). Its **observed-to-expected
ratio of 1.053** places Vietnam modestly above the SDI-expected
trajectory — its NCD share is about 5.3% higher than what its level of
development alone would predict, suggesting that non-SDI drivers
(tobacco, diet, ageing momentum) have accelerated Vietnam's transition
beyond the pace seen in SEA peers at comparable SDI.

---

## 6. Premature-mortality (WHO SDG 3.4.1) findings

30q70 is the unconditional probability of a 30-year-old dying before their
70th birthday from a given cause group (WHO Global Action Plan for the
Prevention and Control of NCDs 2013-2020, Indicator 10). The Vietnam-specific
indicator, computed from GBD 5-year age-band deaths and populations, is
summarized below (also see Figure 9):

| Cause group | 1990 | 2023 | AAPC % (joinpoint, 95% CI) |
|---|---:|---:|---:|
| **NCD 30q70** | 25.02% | 21.80% | **−0.25** (−0.33, −0.16) |
| CMNN 30q70 | 6.18% | 2.12% | **−5.86** (−6.25, −5.47) |

Cross-country 30q70 cannot be computed from the extracted raw data because
GBD does not expose 5-year age-band deaths for the other SEA countries
in the current query. For the cross-country ranking we use the
age-standardized NCD death rate per 100,000 as a direct WHO-recommended
proxy (Figure 10): Vietnam ranks **8th of 11 SEA countries** at 492/100k,
well below Myanmar (927), Lao PDR (768), and Timor-Leste (640) and near
the Southeast-Asia regional median.

---

## 7. Table 5 — SEA YLL/YLD ratio, 2023

*(`tables/sea_yll_yld_ratio.csv`, age-standardized, all causes, 2023;
sorted by YLL/YLD ratio descending)*

| Country | YLL rate | YLD rate | YLL/YLD ratio |
|---|---:|---:|---:|
| Lao PDR | 36,318 | 9,841 | **3.69** |
| Myanmar | 37,841 | 10,831 | 3.49 |
| Timor-Leste | 28,567 | 10,354 | 2.76 |
| Philippines | 23,920 | 10,228 | 2.34 |
| Indonesia | 24,038 | 10,281 | 2.34 |
| Cambodia | 22,510 | 10,566 | 2.13 |
| **Vietnam** | **17,688** | **9,599** | **1.84** |
| Thailand | 16,484 | 10,205 | 1.62 |
| Malaysia | 15,691 | 9,997 | 1.57 |
| Brunei | 13,758 | 10,248 | 1.34 |
| Singapore | 6,277 | 9,427 | **0.67** |

---

## 8. Figures (main analysis)

All figures are saved at 300 DPI (PNG + SVG) in
[`figures/static/`](figures/static/) and interactively in
[`figures/html/`](figures/html/).

| # | Title | Static | Interactive |
|---|---|---|---|
| 1 | Vietnam DALY overview (2×2: absolute / %, age-std rate + 95% UI, **NCD share** of total DALYs) | [fig1_overview.png](figures/static/fig1_overview.png) | [html](figures/html/fig1_overview.html) |
| 2 | Top-15 Vietnam cause heatmap, rate ratio vs 1990 | [fig2_heatmap.png](figures/static/fig2_heatmap.png) | [html](figures/html/fig2_heatmap.html) |
| 3 | Das Gupta decomposition waterfall, NCD and CMNN | [fig3_decomposition.png](figures/static/fig3_decomposition.png) | [html](figures/html/fig3_decomposition.html) |
| 4 | SEA **NCD-share** trajectories + SDI-vs-share scatter with obs/exp annotation | [fig4_sea_comparison.png](figures/static/fig4_sea_comparison.png) | [html](figures/html/fig4_sea_comparison.html) |
| 5 | Age-sex DALY pyramid, 1990 vs 2023 | [fig5_age_sex_pyramid.png](figures/static/fig5_age_sex_pyramid.png) | [html](figures/html/fig5_age_sex_pyramid.html) |
| 6 | Vietnam YLL vs YLD rate + YLL/YLD ratio | [fig6_yll_yld_trends.png](figures/static/fig6_yll_yld_trends.png) | [html](figures/html/fig6_yll_yld_trends.html) |
| 7 | SEA YLL/YLD ratio ranking, 2023 | [fig7_sea_yll_yld.png](figures/static/fig7_sea_yll_yld.png) | [html](figures/html/fig7_sea_yll_yld.html) |
| 9 | Vietnam 30q70 NCD and CMNN probability, 1990–2023 (WHO SDG 3.4.1) | [fig9_30q70_vietnam.png](figures/static/fig9_30q70_vietnam.png) | [html](figures/html/fig9_30q70_vietnam.html) |
| 10 | SEA age-standardized NCD death rate 2023 (cross-country proxy for 30q70) | [fig10_sea_ncd_premature.png](figures/static/fig10_sea_ncd_premature.png) | [html](figures/html/fig10_sea_ncd_premature.html) |

Sensitivity analysis (CMNN split): Figure 8 + Table S1, see
[`SENSITIVITY_DISCUSSION.md`](SENSITIVITY_DISCUSSION.md).

---

## 9. Interpretation (draft paragraphs for Results section)

### 9.1 Composition shift

Between 1990 and 2023, Vietnam's DALY composition shifted from a mixed
CMNN / NCD / Injuries profile (32.5% / 53.0% / 14.5%, respectively) to
one overwhelmingly dominated by NCDs (14.7% / 70.7% / 14.6%). The
**NCD share rose by +17.67 percentage points** — the largest absolute
climb among SEA countries whose 1990 NCD share already exceeded 50%
(Figure 1B, Figure 4A; Table 4).

### 9.2 Transition tempo

Vietnam's **joinpoint AAPC of NCD share** was **+1.09%/year** (95% CI
+1.04, +1.15) over 1990–2023, faster than Singapore (+0.10), Brunei
(+0.22), Thailand (+0.45), and Malaysia (+0.84), but slower than the
low-baseline climbers Cambodia (+1.82) and Lao PDR (+2.30). Its
**observed-to-expected ratio** against the SDI-predicted curve is
**1.053** — 5.3% above the SDI-expected trajectory. Vietnam's transition
tempo is therefore **modestly faster than its SDI level alone would
predict**. Likely contributors include an ageing population, high
adult tobacco prevalence, rapid nutrition and physical-activity
transitions, and concurrent acceleration of CMNN control — rather than
structural drivers fully captured by SDI.

### 9.3 What drives the NCD increase

Das Gupta decomposition (Figure 3, Table 3) attributes Vietnam's +10.6 M
NCD DALY increase almost equally to **population growth (+6.26 M)** and
**ageing (+6.08 M)**. Age-specific NCD rates fell slightly (−1.71 M),
meaning public-health gains against NCD risk were more than swamped by
demographic momentum. Without the population-structure shift, absolute
NCD burden would have fallen; the story is one of demographic pressure
overwhelming modest prevention success.

### 9.4 Premature mortality (WHO SDG 3.4.1)

Vietnam's **NCD 30q70 probability** declined modestly from 25.02% (1990)
to 21.80% (2023), a joinpoint AAPC of only **−0.25%/year** (95% CI −0.33,
−0.16). By contrast, **CMNN 30q70** fell from 6.18% to 2.12% (joinpoint
AAPC **−5.86%/year**, 95% CI −6.25, −5.47). This divergence (Figure 9)
means that while Vietnam has made major gains against infectious and
maternal/neonatal causes of premature death, the premature burden of
NCDs has been stubborn. At the current pace, Vietnam will **not** reach
the SDG 3.4 target of a one-third reduction in NCD 30q70 by 2030.
Across the region (Figure 10), Vietnam's age-standardized NCD death rate
(492/100k) sits **below the SEA median**, but roughly double Singapore's
rate (236/100k).

### 9.5 Dominant causes at level-2

The top-five level-2 CMNN causes in 1990 — respiratory infections and
tuberculosis, maternal and neonatal disorders, HIV/STIs, enteric
infections, and nutritional deficiencies — all fell by **≥ 60%**
(Figure 2; details in `data/processed/vietnam_cmnn_detail.csv`).
Level-2 NCD detail (`data/processed/vietnam_ncd_detail.csv`) shows the
fastest rises are in cardiovascular disease, diabetes, and mental-health
disorders.

### 9.6 Age-sex pyramid (Figure 5)

In 1990 the DALY mass was concentrated in **<5 years** (CMNN-dominated).
By 2023 the largest DALY masses sit in **55–79 years** and are almost
entirely NCD. The burden has shifted both upward in age and rightward
in the CMNN→NCD composition axis.

### 9.7 YLL vs YLD (Figures 6–7)

The YLL rate fell at a joinpoint AAPC of **−1.79%/year** while YLD fell
only **−0.34%/year** (and has effectively plateaued since 2010,
sub-period p = 0.44). The YLL/YLD ratio therefore fell at AAPC
**−1.51%/year** and stands at **1.84** in 2023 — below Southeast Asia's
mid-income cluster (Cambodia 2.13, Indonesia 2.34) and approaching the
high-income benchmark (Thailand 1.62, Malaysia 1.57). Vietnam has moved
past the mortality-dominated phase into the disability-dominated phase
of the epidemiological transition.

---

## 10. File index

| Layer | Path |
|---|---|
| Cleaned inputs | `data/processed/*.csv` |
| Main result tables | `tables/metrics.csv`, `tables/trend_results.csv`, `tables/decomposition_results.csv`, `tables/sea_comparison.csv`, `tables/sea_yll_yld_ratio.csv`, `tables/sea_ncd_death_rate_2023.csv`, `tables/table1_summary.csv` |
| Sensitivity | `tables/table_s1_cmnn_sensitivity.csv`, `data/processed/cmnn_split.csv` |
| 30q70 (WHO SDG 3.4.1) | `data/processed/probability_30q70.csv` |
| Figures (main) | `figures/static/fig1–fig7,fig9,fig10.*`, `figures/html/fig*.html` |
| Figures (sensitivity) | `figures/static/fig8_cmnn_sensitivity.*` |
| Pipeline (Plotly) | `scripts/01_load_clean.py` → `06_figures.py`, `utils.py` |
| Pipeline (matplotlib) | `analysis.py` / `analysis.ipynb` |
| Runner notebook | `run_analysis.ipynb` |
| Discussion template | `SENSITIVITY_DISCUSSION.md` |

Reproduce everything from scratch:

```bash
# canonical (scripts/ + run_analysis.ipynb)
python scripts/00_setup.py
python scripts/01_load_clean.py
python scripts/02_metrics.py
python scripts/03_trends.py
python scripts/04_decomposition.py
python scripts/05_sea_comparison.py
python scripts/06_figures.py

# legacy matplotlib pipeline
python analysis.py
jupyter nbconvert --to notebook --execute analysis.ipynb --inplace
```
