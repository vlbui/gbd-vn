# The epidemiological transition in Vietnam, 1990-2023: a Global Burden of Disease 2023 analysis

**Authors:** [Author 1]^1^, [Author 2]^2^, [Author 3]^1,3^

**Affiliations:**
^1^ [Institution 1, City, Country]
^2^ [Institution 2, City, Country]
^3^ [Institution 3, City, Country]

**Correspondence to:** [Corresponding Author], [email], [postal address]

**Target journal:** *The Lancet Regional Health - Western Pacific*
**Manuscript type:** Research paper
**Word count:** Abstract 297 / Main text 3,498 / Figures 9 / Tables 5 / References 19

**Keywords:** epidemiological transition; non-communicable diseases; disability-adjusted life years; joinpoint regression; Das Gupta decomposition; premature mortality; Vietnam; Southeast Asia; Global Burden of Disease

---

## Research in context

**Evidence before this study.** We searched PubMed, Web of Science, and the IHME Global Health Data Exchange on 15 March 2026 for English-language publications between 1 January 2015 and 28 February 2026 using ("Vietnam" OR "Viet Nam") AND ("burden of disease" OR "epidemiological transition" OR "non-communicable diseases") AND ("DALY" OR "disability-adjusted"). Previous Global Burden of Disease (GBD) country profiles for Vietnam document rising absolute NCD burden and declining communicable-disease mortality, but no single study has jointly quantified the tempo of the composition shift with formal break-point detection, decomposed the absolute burden change into demographic and epidemiological drivers, benchmarked Vietnam's tempo against regional peers conditional on the socio-demographic index (SDI), and assessed progress against the WHO Sustainable Development Goal (SDG) 3.4 target using a strict SDG 3.4.1 definition applied identically across Southeast Asia.

**Added value of this study.** Using GBD 2023 data for Vietnam and its ten Southeast-Asian (SEA) peers, we show that Vietnam has completed the mortality-dominated phase of the transition but entered a disability- and ageing-dominated phase. NCD share of total DALYs rose from 52.99% in 1990 to 70.67% in 2023 (+17.67 pp; joinpoint AAPC +1.09%/year), placing Vietnam 5.3% above the SDI-expected peer trajectory. Das Gupta decomposition attributes the +10.63 million increase in absolute NCD DALYs almost equally to population growth (+6.26 M) and population ageing (+6.08 M); falling age-specific rates removed only 1.71 M. Premature NCD mortality (30q70) fell from 25.02% to 21.80% under the broad GBD NCD aggregate and from 22.17% to 19.50% under the strict WHO SDG 3.4.1 definition - a 12-13% relative reduction, far short of the one-third target. Under SDG 3.4.1 Vietnam ranks sixth of eleven SEA countries, behind Singapore, Thailand, Brunei Darussalam, Malaysia, and Cambodia. A sensitivity analysis separating communicable, maternal, neonatal and nutritional (CMNN) into communicable-only and maternal-neonatal-nutritional sub-groups confirms the transition signal is not an artefact of cause-aggregation choice.

**Implications of all the available evidence.** Vietnam's NCD burden is driven chiefly by demographic momentum, not by rising age-specific risk. Meeting SDG 3.4 by 2030 will require population-scale primary prevention - tobacco control, dietary-salt reduction, and earlier hypertension and diabetes management - at a tempo that outpaces the demographic tailwind. On current trajectory the 2030 30q70 is projected at 21.4% rather than the 16.7% implied by a one-third reduction from the 2015 baseline.

---

## Abstract

**Background.** Vietnam's disease burden has shifted rapidly from communicable, maternal, neonatal and nutritional (CMNN) causes to non-communicable diseases (NCDs), but the tempo, drivers, and regional positioning of this transition have not been jointly quantified. We aimed to characterise Vietnam's epidemiological transition from 1990 to 2023 against its Southeast-Asian (SEA) peers.

**Methods.** Using Global Burden of Disease 2023 data for Vietnam and ten SEA comparator countries, we computed joinpoint-regression average annual percent change (AAPC) with 95% CI for age-standardised DALY rates and cause-composition shares, using a BIC-penalised dynamic-programming piecewise-linear fit with up to three break-points and delta-method CI following Clegg et al. We applied Das Gupta three-factor decomposition to partition 1990-2023 absolute DALY change into population-size, age-structure, and age-specific-rate effects. We benchmarked Vietnam's NCD share against an SDI-conditional peer trajectory by quadratic regression fitted on the ten peers excluding Vietnam. Premature mortality was quantified via the WHO 30q70 probability under the broad GBD NCD aggregate and under the strict SDG 3.4.1 four-cause definition (cardiovascular diseases, neoplasms, diabetes and kidney diseases, chronic respiratory diseases), computed identically across all eleven countries using Chiang II life-table adjustment.

**Findings.** The CMNN age-standardised DALY rate fell from 13,295.9 to 4,022.1 per 100,000 (AAPC -4.63%/year; 95% CI -4.80 to -4.46), while the NCD rate fell only from 21,688.2 to 19,282.8 (AAPC -0.37; -0.45 to -0.30). NCD share of total DALYs rose from 52.99% to 70.67% (+17.67 pp; AAPC +1.09; 1.04 to 1.15). Vietnam ranked fourth of eleven SEA countries on 2023 NCD share (up from sixth in 1990) and sat 5.3% above the SDI-expected peer trajectory. Das Gupta decomposition attributed the +10.63 million increase in absolute NCD DALYs to population growth (+6.26 M) and ageing (+6.08 M); age-specific rate change removed only 1.71 M. Premature NCD mortality fell from 25.02% to 21.80% under the broad definition (12.9% relative reduction) and from 22.17% to 19.50% under SDG 3.4.1 (12.0%), ranking Vietnam sixth of eleven SEA countries. All three metrics fell far short of the SDG 3.4 one-third-reduction trajectory.

**Interpretation.** Vietnam has entered a disability- and ageing-dominated NCD phase of the epidemiological transition. Meeting SDG 3.4 by 2030 will require population-scale primary prevention sized to demographic momentum.

**Funding.** [To be specified].

---

## 1. Introduction

The epidemiological transition - the shift from communicable, maternal, neonatal and nutritional causes to non-communicable diseases - has reshaped population health over four decades.^11,12^ In Southeast Asia the transition has been uneven: Singapore and Brunei Darussalam completed the shift before 2000,^6^ while Cambodia, Lao PDR, and Timor-Leste still carry a double burden of incomplete CMNN control and rising NCD incidence.^8,9^ Vietnam occupies an intermediate position whose tempo has been described as accelerated relative to its development level,^9,10^ and GBD 2023 places the country in the middle of Southeast Asia's disease-burden distribution.^1,2^

Three questions motivate this work. First, how fast has Vietnam's transition proceeded, and does its tempo match what the country's socio-demographic index (SDI) would predict from its regional peers? Second, which forces drive the observed increase in absolute NCD DALYs - demographic shifts (population growth, ageing) or changes in age-specific disease rates? Third, how close is Vietnam to the WHO SDG 3.4 target of a one-third reduction in premature NCD mortality by 2030?

Prior work has addressed each question in isolation. GBD 2023 country profiles report cause-specific DALY rates^1,2^ but do not benchmark trend velocity against SDI-expected trajectories. Cause-specific studies of Vietnam have focused on single disease groups - chiefly stroke^4^ and cardiovascular disease more broadly^6^ - rather than the level-1 aggregate, and projections of NCD management indicators stop at 2030.^7,10^ Vietnam's commitments under the WHO NCD Global Action Plan 2013-2030^13^ and the UN SDG 3.4 target^14^ have not been jointly evaluated using the GBD 2023 round. We integrate these elements here, reporting (i) joinpoint-regression trends with 95% CI, (ii) Das Gupta three-factor decomposition, (iii) SDI-expected trajectories fitted on peer countries with the focal country excluded, (iv) 30q70 progress against SDG 3.4 using the strict SDG 3.4.1 four-cause definition, and (v) a sensitivity analysis that separates CMNN into communicable-only and maternal-neonatal-nutritional sub-groups.

---

## 2. Methods

### 2.1 Data source

We extracted GBD 2023 estimates from the IHME Global Health Data Exchange (October 2025 release) for eleven SEA countries: Vietnam, Thailand, Indonesia, the Philippines, Malaysia, Myanmar, Cambodia, Lao PDR, Singapore, Brunei Darussalam, and Timor-Leste.^1-3^ For each country-year-age-sex-cause stratum we obtained age-standardised and all-age DALY rates, years of life lost (YLL), years lived with disability (YLD), and deaths, with 95% uncertainty intervals. Cause-specific estimates are produced by the Cause of Death Ensemble model (CODEm) and the DisMod-MR 2.1 Bayesian meta-regression framework.^15^ Analyses were performed at GBD cause-hierarchy level 1 (CMNN, NCD, Injuries) unless otherwise stated. Age groups followed the standard GBD 5-year bands; annual data were available for every year 1990-2023.

### 2.2 Composition metrics

Age-standardised rates used the GBD 2010 world standard population. NCD share of total DALYs was computed as `NCD / (CMNN + NCD + Injuries)`, expressed as a percentage; CMNN and Injury shares were computed analogously. The CMNN/NCD ratio captures compositional parity.

### 2.3 Joinpoint regression and AAPC

We fitted log-linear piecewise regression of the annual age-standardised rate (or share), `log(y_t) = alpha + beta_k * t` for segment *k*, with up to three break-points. The optimal number of break-points was selected by minimising the Bayesian information criterion, `BIC = n * log(SSR/n) + p * log(n)`. Segments were identified by dynamic programming.^16^ The annual percent change in segment *k* is `APC_k = 100 * (exp(beta_k) - 1)`; the average annual percent change over the full window is the length-weighted geometric mean of segment APCs. 95% confidence intervals were computed by the delta method following Clegg et al.^17^ For decade sub-periods (1990-2000, 2000-2010, 2010-2023) we fitted a single-segment log-linear regression because approximately ten annual observations per decade are too few for BIC-selected break-point detection.

### 2.4 Das Gupta decomposition

We partitioned the 1990-to-2023 change in absolute DALYs (CMNN and NCD separately) into three components using Das Gupta's symmetric formulation:^18^

```
Delta(D) = Delta(population size) * s_bar * r_bar     [population-size effect]
         + P_bar * Delta(age structure) * r_bar        [age-structure (ageing) effect]
         + P_bar * s_bar * Delta(age-specific rate)    [rate effect]
```

where barred quantities are 1990/2023 averages. The method is exact: the three effects sum to the observed change up to floating-point precision (residuals < 10^-9).

### 2.5 SDI-benchmarked expectation

For each focal country we fitted a quadratic regression of 2023 NCD share on SDI using the ten SEA peer countries excluding the focal country. This leave-one-out fit prevents the data-leakage that would bias the observed-to-expected ratio toward unity. The predicted value at the focal country's own SDI gave the SDI-expected NCD share; the ratio `observed / expected` quantifies whether the country sits above (>1.00) or below (<1.00) the peer trajectory.

### 2.6 Premature mortality (30q70)

The unconditional probability of a 30-year-old dying before age 70 was computed from GBD 2023 age-band death rates via the Chiang II life-table adjustment:

```
30q70 = 1 - prod_{a=30,35,...,65} (1 - 5*m_a / (1 + 2.5*m_a))
```

where `m_a` is the cause-specific death rate in 5-year age band *a* (eight bands from 30-34 to 65-69). For the strict WHO SDG 3.4.1 indicator we pooled the four main NCDs (cardiovascular diseases, neoplasms, diabetes and kidney diseases, chronic respiratory diseases); for the broad-NCD Vietnam trend in Table 1 we used the GBD level-1 NCD aggregate to remain comparable with our level-1 composition analysis. The identical pipeline was applied to Vietnam and the ten peer countries to enable cross-country ranking.

### 2.7 Sensitivity analyses

To probe robustness of the composition narrative to the CMNN level-1 grouping convention, we reran all core computations after separating CMNN into a communicable-only sub-group (HIV/STIs, respiratory infections and tuberculosis, enteric infections, neglected tropical diseases and malaria, other infectious) and a maternal-neonatal-nutritional (M+N+N) sub-group. Results are reported in the Supplement.

### 2.8 Reporting and reproducibility

This study follows the GATHER reporting guideline for population-based health estimates (checklist in Supplement §S3).^19^ All code, intermediate tables, and figures are available from the corresponding author on request. The full analysis pipeline (`scripts/01_load_clean.py` through `06_figures.py`, plus `07_30q70_sea.py`) runs end-to-end in under 10 minutes on a standard laptop with no internet connection. Ethical approval was not required because only publicly available aggregated data were used.

---

## 3. Results

### 3.1 Level-1 cause-group trajectories

Vietnam's age-standardised DALY rate fell for every level-1 cause group between 1990 and 2023, but at markedly different tempos (Table 1, Figure 1). The CMNN rate fell from 13,295.9 to 4,022.1 per 100,000 - a joinpoint AAPC of **-4.63%/year** (95% CI -4.80 to -4.46) and a 69.8% relative reduction. The NCD rate fell only from 21,688.2 to 19,282.8 (AAPC **-0.37%/year**, -0.45 to -0.30), an 11.1% relative reduction. The Injury rate fell from 5,942.0 to 3,981.8 (AAPC **-1.13%/year**, -1.24 to -1.03).

The contrast between rapidly declining CMNN and near-flat NCD rates produced a large composition shift. CMNN's share of total DALYs fell from 32.49% to 14.74% (AAPC -3.44%/year), while **NCD share rose from 52.99% to 70.67%** - a +17.67 percentage-point absolute change and a joinpoint AAPC of **+1.09%/year** (1.04 to 1.15; three break-points selected by BIC). The Injury share was approximately stable (14.52% to 14.59%). The CMNN/NCD ratio collapsed from 0.613 to 0.209.

### 3.2 Period-specific dynamics

Decade sub-periods (Table 2) reveal that the rapid CMNN decline occurred steadily across all three decades (-4.35%/year in the 1990s, -3.58 in the 2000s, -2.04 in 2010-2023), decelerating gradually as the absolute burden approached a floor. The NCD rate decline was non-monotonic: it fell fastest in the 1990s (-0.86%/year), stalled almost completely in the 2000s (-0.10%/year), and resumed a modest decline in 2010-2023 (-0.28%/year). The YLD rate plateaued after 2010 (sub-period AAPC -0.03%/year, p = 0.44), while the YLL rate continued to fall (-1.09%/year, p < 0.001) - the classical signature of mortality compression with morbidity expansion.

### 3.3 Decomposition of absolute change

Between 1990 and 2023 Vietnam's absolute NCD DALYs grew by **+10.63 million**, while CMNN DALYs fell by 6.45 million (Table 3, Figure 3). Das Gupta decomposition attributes the NCD increase almost equally to **population growth (+6.26 M)** and **population ageing (+6.08 M)**; the age-specific-rate effect contributed only -1.71 M. In the absence of demographic change, falling age-specific NCD rates alone would have reduced absolute NCD DALYs; instead, demographic momentum delivered a net +10.63 M increase. For CMNN the rate effect (-8.18 M) dominated, with population growth (+3.25 M) and a mild de-ageing effect (-1.51 M) partially offsetting.

### 3.4 Regional positioning (SEA comparison)

Across eleven SEA countries (Table 4, Figure 4), the 2023 NCD share ranged from 58.65% (Lao PDR) to 81.26% (Brunei Darussalam). Vietnam's 70.67% placed it **fourth of eleven SEA countries in 2023**, up from sixth in 1990 - the largest positive rank mover in the region. Among countries whose 1990 NCD share already exceeded 50% (the already-transitioning cluster: Singapore, Brunei, Malaysia, Thailand, Philippines, Vietnam), Vietnam posted the **largest absolute climb** at +17.67 pp. Only the low-baseline climbers Lao PDR (+29.92 pp), Cambodia (+26.55 pp), Timor-Leste (+23.45 pp), Indonesia (+21.12 pp), and Myanmar (+20.65 pp) registered larger absolute shifts - reflecting lower 1990 starting points rather than faster tempo from equivalent starting conditions.

Vietnam's joinpoint AAPC of NCD share (+1.09%/year) exceeded the high-SDI peers (Singapore +0.10, Brunei +0.22, Thailand +0.45, Malaysia +0.84) but lagged the low-baseline rapid climbers (Cambodia +1.82, Lao PDR +2.30). Against the SDI-expected trajectory fitted on the ten peer countries, **Vietnam's obs/exp ratio was 1.053** - 5.3% above the expected peer curve. This placed Vietnam in the same "above-expected" cluster as Brunei (1.051), Myanmar (1.051), and Cambodia (1.054), while Singapore (0.945), Lao PDR (0.932), and Thailand (0.969) sat below their SDI-expected shares.

### 3.5 Premature NCD mortality and the SDG 3.4 trajectory

Under the broad GBD NCD aggregate, Vietnam's premature NCD mortality (30q70) declined from **25.02% in 1990 to 21.80% in 2023** - a joinpoint AAPC of **-0.25%/year** (95% CI -0.33 to -0.16) and a 12.9% relative reduction (Table 1, Figure 9). Under the strict WHO SDG 3.4.1 definition, 30q70 fell from **22.17% to 19.50%** - a 12.0% relative reduction. Both trajectories fall far short of the SDG 3.4 one-third-reduction pace required to reach the 2030 target. Extrapolating the 2010-2023 slope forward, Vietnam's projected 2030 broad-NCD 30q70 is 21.4% (against 16.7% implied by a one-third reduction from the 2015 baseline of 22.76%) - a 1990-2030 reduction of roughly 14%, less than half the target. Premature CMNN mortality, by contrast, fell sharply from **6.18% to 2.12%** (AAPC -5.86%/year; 65.7% relative reduction), indicating near-completion of the CMNN-mortality phase.

Applying the identical Chiang II pipeline to all eleven SEA countries under the strict SDG 3.4.1 definition (Figure 10, Table S5) yields a clear 2023 ranking. Vietnam's 19.5% places it **sixth of eleven SEA countries**, below Singapore (7.7%), Thailand (15.5%), Brunei Darussalam (16.7%), Malaysia (18.6%), and Cambodia (19.3%), and above Timor-Leste (22.1%), the Philippines (23.2%), Indonesia (25.1%), Lao PDR (29.5%), and Myanmar (32.4%). Across the region, Singapore achieved the largest relative reduction (65.8%), followed by Brunei (37.6%) and Thailand (27.2%); Lao PDR, Indonesia, and the Philippines show essentially no progress or mild worsening since 1990. Vietnam's 12.0% reduction is mid-pack for SEA - ahead of Myanmar (9.8%) and Cambodia (8.5%) but well behind Thailand, Brunei, Malaysia, and Singapore. No SEA country is currently on the SDG 3.4 trajectory; Singapore is the only peer whose 2023 value already sits below a one-third reduction from its 1990 baseline.

### 3.6 YLL versus YLD

Vietnam's YLL rate fell at joinpoint AAPC **-1.79%/year** (95% CI -1.87 to -1.71) while its YLD rate fell only **-0.34%/year** (-0.37 to -0.30) (Table 1, Figure 6). The YLL/YLD ratio therefore fell from 2.85 in 1990 to 1.84 in 2023 (AAPC -1.51%/year). Regionally (Table 5, Figure 7), Vietnam's 2023 YLL/YLD of 1.84 placed it below the mid-income SEA cluster (Cambodia 2.13, Indonesia 2.34, Philippines 2.34) and approached the high-income benchmark (Thailand 1.62, Malaysia 1.57, Brunei 1.34, Singapore 0.67) - consistent with transition to a disability-dominated phase.

### 3.7 Age-sex burden distribution

The DALY pyramid (Figure 5) shows the burden axis shifted both upward in age and rightward in composition. In 1990 the largest DALY mass sat in the <5-year age band and was overwhelmingly CMNN (neonatal, respiratory infection, diarrhoea). By 2023 the largest DALY masses sat in the 55-79 year bands and were almost entirely NCD (ischaemic heart disease, stroke, cancers, diabetes). Sex differentials were modest: males carried higher Injury and cardiovascular burden, females higher dementia and musculoskeletal burden.

### 3.8 Sensitivity to CMNN grouping

Separating CMNN into communicable-only and M+N+N sub-groups (Supplement §S1, Figure 8) confirmed the transition signal under either framing. The communicable-only rate fell from 8,908.8 to 2,688.2 per 100,000 (AAPC -5.05%/year) and the M+N+N rate from 4,387.1 to 1,334.0 (AAPC -3.45%/year). NCD share in 2023 varied with denominator choice - 70.67% against full CMNN (main analysis), 74.30% against communicable-only, 78.39% against M+N+N alone - but the direction and ordering were preserved across all three. The residual 2023 CMNN burden retained an approximate 2:1 split between communicable and M+N+N causes, preserving the 1990 composition ratio.

---

## 4. Discussion

### 4.1 Principal findings

Between 1990 and 2023 Vietnam completed the mortality-dominated phase of the epidemiological transition. NCD share of total DALYs rose by 17.67 percentage points - the largest absolute climb among SEA countries whose 1990 NCD share already exceeded 50% - and sat 5.3% above the SDI-conditional peer expectation. Three findings qualify this apparent progress.

First, **age-specific NCD rates have barely moved**. The joinpoint AAPC of the age-standardised NCD rate was only -0.37%/year and was indistinguishable from zero in the 2000s (sub-period AAPC -0.10%/year). The +10.63 million absolute NCD DALY increase is therefore almost entirely explained by demographic pressure - population growth (+6.26 M) and ageing (+6.08 M) - rather than by failing rate control. The ageing contribution alone is of the same magnitude as the population-growth contribution, indicating that Vietnam has entered the phase of the transition in which demographic momentum, not epidemiology, dominates burden dynamics.

Second, **premature NCD mortality has been sticky**. Vietnam's 30q70 fell only modestly, from 25.02% to 21.80% under the broad NCD aggregate (AAPC -0.25%/year) and from 22.17% to 19.50% under the strict WHO SDG 3.4.1 definition. Extrapolating the 2010-2023 slope forward, the projected 2030 broad-NCD 30q70 is 21.4% - far above the 16.7% implied by a one-third reduction from the 2015 baseline of 22.76%. Under SDG 3.4.1 Vietnam ranks sixth of eleven SEA countries, and no SEA country other than Singapore is currently on the 2030 trajectory.

Third, **morbidity has begun to expand as mortality compresses**. The YLD rate plateaued after 2010 (sub-period AAPC -0.03%/year, p = 0.44) while the YLL rate continued to fall (-1.09%/year, p < 0.001). This signature of expansion of morbidity with compression of mortality is the hallmark of a disability-dominated transition phase.

### 4.2 Comparison with previous work

Our NCD share estimates are closely aligned with published GBD 2023 country estimates.^1,2^ The +17.67 percentage-point 1990-2023 increase is consistent with prior Vietnam NCD burden projections^10^ and with the "paradox of progress" characterisation of Vietnam's transition in which economic development has simultaneously reduced CMNN burden and accelerated NCD incidence.^9^ The finding that demographic forces dominate NCD DALY growth is convergent with regional CVD and projection analyses across ASEAN^6^ and aligns with global NCD projections through 2050.^7^

This analysis adds three new elements. First, the BIC-selected joinpoint structure identifies three regime changes in Vietnam's NCD share - clustered around 1995, 2005, and 2015 - that coincide with the 1995 health-sector reform, the 2005 ASEAN NCD commitment, and the 2013 national NCD action plan. Whether these are causal associations or coincident secular drift cannot be resolved from annual aggregate data alone. Second, the SDI-peer benchmark uses a leave-one-out quadratic fit that excludes the focal country, avoiding the data-leakage bias of global GBD regressions that include the focal country on both sides of the comparison. Third, the 30q70 projection against SDG 3.4, applied identically across all eleven SEA countries under the strict SDG 3.4.1 four-cause definition, has not to our knowledge been reported for Vietnam using GBD 2023; prior Vietnam-specific 30q70 estimates relied on the broader NCD aggregate and on single-country pipelines that are not directly comparable with peers.

### 4.3 Policy implications

Vietnam's NCD burden is demographically driven. This has a stark corollary: any NCD strategy that targets only age-specific rates - even an ambitious one - will be inadequate, because the demographic tailwind will continue to add DALYs for at least two more decades. The effective policy lever is **population-scale primary prevention sized to demographic momentum**, aligned with the WHO Global Action Plan for NCDs.^13^ Four "best-buy" domains are most relevant to Vietnam's epidemiological profile: tobacco control, dietary sodium reduction, alcohol control, and hypertension and diabetes screening with community-based management. Each targets upstream risk in the 30-60 age band where the 30q70 denominator accrues, and rising dementia and Alzheimer burden^5^ adds further weight to cardiovascular and metabolic risk-factor control as cognitive-reserve protection.

The 30q70 target has a direct, testable implication for Vietnam's progress against SDG 3.4.^14^ Achieving the SDG one-third reduction by 2030 would require a 30q70 annual decline of approximately 2.9%/year - roughly an order of magnitude faster than the observed 2010-2023 pace of 0.28%/year under the broad definition. Absent structural change in risk-factor exposure and health-system response times, the target is unreachable on current trajectory. The finding that the morbidity rate has plateaued also argues for investment in secondary and tertiary prevention - early diagnosis, continuity of chronic care - rather than primary prevention alone; the two strategies address different segments of the disability-dominated phase.

### 4.4 Strengths and limitations

Strengths of this analysis include the use of a single unified GBD 2023 data release across eleven SEA countries, joinpoint regression with BIC-selected break-points rather than pre-specified windows, exact Das Gupta decomposition (residuals < 10^-9), a leave-one-out SDI-peer benchmark that avoids data-leakage, a strict SDG 3.4.1 30q70 pipeline applied identically across all eleven SEA countries, and a sensitivity analysis that confirms the CMNN grouping convention does not drive the main result. The entire pipeline runs offline in under 10 minutes on a standard laptop.

Limitations are four. First, GBD DALY estimates themselves carry uncertainty from verbal autopsy, cause-of-death misclassification, and modelling of sparse data from low-income settings; this is reflected in the 95% UI bands but not in the point estimates reported in the main text. Second, the SDI-peer regression uses ten data points (leave-one-out), so the SDI-expected estimates are imprecise; bootstrapped confidence intervals on the obs/exp ratio (not reported in the main table) are of order ±0.08. Third, our analysis is at GBD level 1; level-2 cause-specific narratives (cardiovascular disease, cancer, diabetes) are shown only descriptively, and no formal cause-specific AAPCs are reported in the main text. Fourth, the cross-country 30q70 AAPCs in Table S5 use a single-segment log-linear fit rather than BIC-selected joinpoint regression; this is a conservative choice that does not affect the 2023 ranking but may under-represent recent accelerations or plateaus in individual peer countries.

### 4.5 Conclusion

Vietnam's epidemiological transition from 1990 to 2023 has been rapid, demographically driven, and unevenly distributed across burden dimensions. NCD share rose faster than in most already-transitioned SEA peers, yet age-specific NCD rates barely moved - meaning that ageing and population growth, not prevention failure, account for most of the NCD burden increase. Premature NCD mortality declined too slowly to meet SDG 3.4 by 2030 under either definition. Vietnam has entered a disability- and ageing-dominated phase of the epidemiological transition. The required policy response is population-scale primary prevention scaled to match demographic momentum, combined with investment in secondary and tertiary prevention for the disability-dominated phase - not incremental improvements in age-specific rates alone.

---

## Contributors

[AU1] conceived the study and wrote the first draft. [AU2] performed the statistical analyses and generated all tables and figures. [AU3] supervised the analysis and provided epidemiological interpretation. All authors reviewed and approved the final manuscript. [AU2] accessed and verified the underlying data.

## Declaration of interests

[Authors declare no competing interests / To be specified].

## Data sharing

All input data are publicly available from the IHME Global Health Data Exchange (https://ghdx.healthdata.org). The analysis code (Python, NumPy, pandas, matplotlib, plotly) will be deposited on Zenodo upon acceptance with a DOI.

## Acknowledgments

[To be specified].

## Funding

[To be specified].

---

## Tables

**Table 1.** Vietnam key-metric summary, 1990-2023. Age-standardised DALY rates (per 100,000), composition shares, premature-mortality probabilities (30q70), and YLL/YLD metrics with joinpoint-regression AAPC and 95% CI. See main text §3.1.

**Table 2.** Period-specific AAPC for Vietnam: full 1990-2023 window (joinpoint) versus three decade sub-periods (1990-2000, 2000-2010, 2010-2023; single-segment log-linear).

**Table 3.** Das Gupta decomposition of 1990-to-2023 absolute DALY change, Vietnam, NCD and CMNN separately. Population-size, age-structure, and age-specific-rate effects in absolute DALYs.

**Table 4.** Southeast-Asian NCD-share ranking, delta, joinpoint AAPC, and SDI-expected ratio (obs/exp 2023). Eleven countries, sorted by 2023 NCD share.

**Table 5.** Southeast-Asian YLL/YLD ratio, 2023. Age-standardised rates, sorted by YLL/YLD descending.

*(Tables as rendered are in `tables/` - see Supplement §S2 for the full numeric content.)*

---

## Figure legends

**Figure 1.** Vietnam DALY overview, 1990-2023 (2x2 panel). **(A)** Absolute DALYs by level-1 cause group with 95% uncertainty bands. **(B)** Share of total DALYs by level-1 cause group, showing NCD rising from 52.99% to 70.67%. **(C)** Age-standardised DALY rate per 100,000 by cause group, log scale, with 95% UI bands. **(D)** NCD share of total DALYs with joinpoint regression fit; three break-points selected by BIC. Source: GBD 2023.

**Figure 2.** Heatmap of Vietnam's top-15 level-2 causes, 1990-2023 (8-year columns). Rows sorted by 2023 age-standardised DALY rate. Cell colour: rate ratio versus 1990 (RdBu_r diverging scale). Cell text: absolute rate per 100,000.

**Figure 3.** Das Gupta decomposition waterfall, Vietnam 1990 to 2023. Separately for NCD (left, +10.63 M observed change) and CMNN (right, -6.45 M). Components: population-size, age-structure (ageing), age-specific-rate. Positive bars indicate contribution toward increase, negative toward decrease.

**Figure 4.** Southeast-Asian NCD-share trajectories. **(A)** Time series 1990-2023 for eleven SEA countries, Vietnam highlighted. **(B)** 2023 NCD share versus SDI, with per-country quadratic SDI-expected curve (ten-peer fit, focal excluded). Annotations give obs/exp ratio.

**Figure 5.** Age-sex DALY pyramid for Vietnam, 1990 (left) versus 2023 (right). X-axis: DALYs per 100,000 (males left, females right). Colour: CMNN / NCD / Injuries.

**Figure 6.** Vietnam YLL rate, YLD rate, and YLL/YLD ratio, 1990-2023. Joinpoint fits overlaid.

**Figure 7.** Southeast-Asian YLL/YLD ratio ranking, 2023. Vietnam highlighted.

**Figure 8.** CMNN grouping sensitivity: full CMNN, communicable-only, and M+N+N sub-groups, 1990-2023. Lines show age-standardised rate trajectories; shaded bands show the resulting NCD-share ranges.

**Figure 9.** Vietnam 30q70 (NCD and CMNN), 1990-2023, with joinpoint fits. SDG 3.4 target trajectory (one-third reduction by 2030 from 2015 baseline) overlaid on the NCD panel.

**Figure 10.** Premature NCD mortality across eleven SEA countries, 1990 versus 2023. Bars show the WHO SDG 3.4.1 30q70 (strict four-cause definition: cardiovascular diseases, neoplasms, diabetes and kidney diseases, chronic respiratory diseases) for 2023, computed identically for every country via Chiang II life-table adjustment on GBD 2023 age-band death rates. Open circles show the 1990 value. Vietnam (highlighted) = 19.5% in 2023, ranked sixth of eleven.

---

## References

1. GBD 2023 Diseases and Injuries Collaborators. Burden of 375 diseases and injuries, risk-attributable burden of 88 risk factors, and healthy life expectancy in 204 countries and territories, including 660 subnational locations, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023. *Lancet* 2025. doi:10.1016/S0140-6736(25)01637-X.

2. GBD 2023 Causes of Death Collaborators. Global burden of 292 causes of death in 204 countries and territories and 660 subnational locations, 1990-2023: a systematic analysis for the Global Burden of Disease Study 2023. *Lancet* 2025. doi:10.1016/S0140-6736(25)01917-8.

3. GBD 2023 Demographics Collaborators. Global age-sex-specific all-cause mortality and life expectancy estimates for 204 countries and territories and 660 subnational locations, 1950-2023: a demographic analysis for the Global Burden of Disease Study 2023. *Lancet* 2025. doi:10.1016/S0140-6736(25)01330-3.

4. Tran MC, Prisco L, Pham PM, et al. Comprehensive analysis of stroke epidemiology in Vietnam: insights from GBD 1990-2019 and RES-Q 2017-2023. *Clin Epidemiol Glob Health* 2025;32:101923. PMID: 40276373.

5. [Authors to confirm]. Burden and risk factors of Alzheimer's disease and other dementias in Vietnam from 1990 to 2021: a comprehensive analysis from the Global Burden of Disease Study. 2025. PMID: 40687730.

6. GBD 2021 ASEAN CVD Collaborators. The epidemiology and burden of cardiovascular diseases in countries of the Association of Southeast Asian Nations (ASEAN), 1990-2021: findings from the Global Burden of Disease Study 2021. *Lancet Public Health* 2025. doi:10.1016/S2468-2667(25)00087-8.

7. [Authors to confirm]. Global burden and future projections of non-communicable diseases (2000-2050): progress toward SDG 3.4 and disparities across regions and risk factors. *PLoS One* 2025. PMCID: PMC12694828.

8. [Authors and DOI to verify]. The double burden of communicable and non-communicable diseases in low- and middle-income countries. *Sci Rep* 2023.

9. Nguyen KQ, Taylor-Robinson AW. A "paradox of progress" shapes the social determinants of infectious diseases in Vietnam, 1975-2025. *Nat Commun* 2026. doi:10.1038/s41467-026-71419-7.

10. Ikeda N, Yamashita H, Hattori J, et al. Trends in, projections of, and inequalities in non-communicable disease management indicators in Vietnam 2010-2030 and progress toward universal health coverage: a Bayesian analysis at national and sub-national levels. *eClinicalMedicine* 2022;52:101670. doi:10.1016/j.eclinm.2022.101670.

11. Omran AR. The epidemiologic transition: a theory of the epidemiology of population change. *Milbank Mem Fund Q* 1971;49:509-38.

12. Olshansky SJ, Ault AB. The fourth stage of the epidemiologic transition: the age of delayed degenerative diseases. *Milbank Q* 1986;64:355-91.

13. World Health Organization. Global action plan for the prevention and control of noncommunicable diseases 2013-2020 (extended to 2030). Geneva: WHO, 2013.

14. United Nations General Assembly. Transforming our world: the 2030 Agenda for Sustainable Development. Resolution A/RES/70/1 (Sustainable Development Goal target 3.4). New York: United Nations, 25 September 2015.

15. Flaxman AD, Vos T, Murray CJL, eds. An integrative metaregression framework for descriptive epidemiology (DisMod-MR 2.1). Seattle: University of Washington Press, 2015.

16. Killick R, Fearnhead P, Eckley IA. Optimal detection of changepoints with a linear computational cost. *J Am Stat Assoc* 2012;107:1590-8.

17. Clegg LX, Hankey BF, Tiwari R, Feuer EJ, Edwards BK. Estimating average annual per cent change in trend analysis. *Stat Med* 2009;28:3670-82.

18. Das Gupta P. Standardization and decomposition of rates: a user's manual. US Bureau of the Census, Current Population Reports, Series P23-186. Washington, DC: US Government Printing Office, 1993.

19. Stevens GA, Alkema L, Black RE, et al. Guidelines for accurate and transparent health estimates reporting: the GATHER statement. *Lancet* 2016;388:e19-23.

---

*End of main manuscript.*
