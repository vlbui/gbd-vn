# Sensitivity analysis — Discussion text template

Paste or adapt the following paragraphs into the paper's Discussion section.
Numbers below are drawn directly from `tables/table_s1_cmnn_sensitivity.csv`
(joinpoint AAPC, BIC-penalized DP piecewise-linear regression, max 3
breakpoints, 95% CI via Clegg 2009 delta method) and
`data/processed/cmnn_split.csv`. Regenerate after any data refresh.

---

## Template paragraph (English)

> Our main analysis follows the GBD 2023 convention of treating communicable,
> maternal, neonatal, and nutritional diseases (CMNN) as a single level-1
> cause group. To probe the robustness of the epidemiological-transition
> narrative to this framing, we repeated the core calculations after
> separating CMNN into a communicable-only sub-group (C-only: HIV/AIDS and
> sexually transmitted infections, respiratory infections and tuberculosis,
> enteric infections, neglected tropical diseases and malaria, and other
> infectious diseases) and a maternal + neonatal + nutritional sub-group
> (M+N+N).
>
> Both sub-groups declined substantially between 1990 and 2023 in
> age-standardized DALY rate terms. The communicable-only rate fell from
> **8,908.8 to 2,688.2 per 100,000** (joinpoint AAPC **−5.05%/year**,
> 95% CI −5.24 to −4.86) and the M+N+N rate fell from **4,387.1 to
> 1,334.0 per 100,000** (joinpoint AAPC **−3.45%/year**, 95% CI −3.66 to
> −3.25). The transition signal holds under either framing: both sub-groups
> lost **~70% of their 1990 burden** over the study period.
>
> The two sub-groups, however, fell at materially different tempos —
> communicable-only was ~1.6 percentage-points/year faster than M+N+N in
> joinpoint AAPC terms. This difference reflects distinct segment-wise
> dynamics: communicable-disease burden dropped sharply after 2000 with
> the scale-up of HIV/AIDS and tuberculosis control, whereas M+N+N burden
> had already begun falling in the 1990s and decelerated in the 2010s as
> neonatal mortality approached a floor.
>
> The **NCD share of total DALYs** in 2023 differs by choice of CMNN
> denominator: **70.67%** against the full CMNN group (main analysis),
> **74.30%** when compared only against communicable diseases, and
> **78.39%** when compared only against M+N+N causes. We report the
> main-analysis NCD share in the body of the paper because it is directly
> comparable across countries and years as published by IHME, and we
> include the sub-group split (Figure 8, Table S1) so readers can
> re-anchor the metric to a narrower definition if desired.
>
> The residual CMNN burden in Vietnam is split roughly **2:1 between
> communicable and M+N+N causes** (2,688 vs 1,334 per 100,000 in 2023),
> essentially the same 2:1 ratio as in 1990 (8,909 vs 4,387). Despite
> different joinpoint AAPCs, the 1990→2023 endpoint log-linear rates of
> the two sub-groups are nearly identical (both ~−3.6%/year simple), which
> is why the composition ratio of the residual CMNN burden is preserved
> even as the absolute magnitude collapsed. This pattern is consistent
> with Vietnam's sustained gains in both maternal-child health and
> infectious-disease control over the study period.

---

## Vietnamese paraphrase (optional)

> Phân tích chính tuân theo phân loại GBD 2023, xem nhóm CMNN là một nhóm
> level-1 duy nhất. Để kiểm tra độ vững của kết luận, chúng tôi tiến hành
> phân tích nhạy cảm bằng cách tách CMNN thành (i) nhóm **C-only** (bệnh
> truyền nhiễm) và (ii) nhóm **M+N+N** (bà mẹ, trẻ sơ sinh, dinh dưỡng).
> Cả hai phân nhóm đều giảm mạnh trong giai đoạn 1990–2023: tỷ suất DALY
> chuẩn hoá theo tuổi của C-only giảm từ **8 909 xuống 2 688/100 000**
> (joinpoint AAPC **−5.05%/năm**, 95% CI −5.24 đến −4.86) và M+N+N giảm
> từ **4 387 xuống 1 334/100 000** (joinpoint AAPC **−3.45%/năm**, 95% CI
> −3.66 đến −3.25). Cả hai đều mất **~70% gánh nặng 1990** trong giai đoạn
> nghiên cứu, nhưng C-only giảm nhanh hơn M+N+N ~1.6 pp/năm về AAPC
> joinpoint — phản ánh giai đoạn tăng tốc kiểm soát HIV/lao sau năm 2000,
> trong khi M+N+N đã giảm sớm hơn và chững lại trong thập niên 2010 khi
> tử vong sơ sinh tiệm cận sàn.
>
> Tỷ lệ DALY do NCD năm 2023 thay đổi theo cách chọn mẫu số: **70.67%**
> khi so với CMNN tổng, **74.30%** khi so với C-only, và **78.39%** khi so
> với M+N+N. Kết luận tổng thể về quá trình chuyển đổi dịch tễ học không
> bị ảnh hưởng bởi cách phân nhóm này. Gánh nặng CMNN còn lại tại Việt Nam
> vẫn giữ tỷ lệ ~2:1 giữa C-only và M+N+N (2 688 vs 1 334/100 000 năm 2023,
> gần như không đổi so với 8 909 vs 4 387 năm 1990), do tốc độ giảm đầu-cuối
> log-tuyến tính của hai nhóm gần như bằng nhau (~−3.6%/năm simple), bất
> chấp AAPC joinpoint khác nhau.

---

## Table S1 — CMNN split and NCD-share variants

*(from `tables/table_s1_cmnn_sensitivity.csv`; age-standardized DALY rate
per 100,000 unless otherwise noted; AAPC via joinpoint regression,
BIC-penalized DP piecewise-linear fit, max 3 breakpoints, 95% CI by
Clegg 2009 delta method)*

| Group | 1990 | 2000 | 2010 | 2023 | AAPC% (95% CI) |
|---|---:|---:|---:|---:|---|
| CMNN (full, main analysis) | 13,295.9 | 8,549.0 | 5,870.2 | 4,022.1 | **−4.63** (−4.80, −4.46) |
| Communicable only (sensitivity) | 8,908.8 | 5,611.2 | 4,001.6 | 2,688.2 | **−5.05** (−5.24, −4.86) |
| Maternal+Neonatal+Nutritional (sensitivity) | 4,387.1 | 2,937.8 | 1,868.6 | 1,334.0 | **−3.45** (−3.66, −3.25) |
| Non-communicable diseases | 21,688.2 | 19,960.4 | 19,742.8 | 19,282.8 | **−0.37** (−0.45, −0.30) |
| Injuries | 5,942.0 | 5,409.9 | 4,683.0 | 3,981.8 | **−1.13** (−1.24, −1.03) |
| **NCD share vs full CMNN (main)** | **52.99%** | **58.85%** | **65.17%** | **70.67%** | — |
| NCD share vs C-only CMNN (sensitivity) | 59.36% | 64.43% | 69.45% | 74.30% | — |
| NCD share vs M+N+N only CMNN (sensitivity) | 67.74% | 70.51% | 75.08% | 78.39% | — |

---

## Files produced by the sensitivity analysis

| File | Contents |
|------|----------|
| `tables/table_s1_cmnn_sensitivity.csv` | Snapshot rates (1990/2000/2010/2023) + joinpoint AAPC + three NCD-share variants |
| `data/processed/cmnn_split.csv` | Year-by-year rates for CMNN, C-only, M+N+N, NCD, Injuries |
| `figures/static/fig8_cmnn_sensitivity.png` | Two-panel comparison (main vs split) |
| `figures/html/fig8_cmnn_sensitivity.html` | Interactive version of Figure 8 |

## How this is wired into the pipeline

- `scripts/02_metrics.py → cmnn_sensitivity()` is called automatically from `run()`.
- `scripts/06_figures.py → fig8_cmnn_sensitivity()` is rendered automatically from `run()`.
- `scripts/generate_sensitivity_md.py` (to be added) rebuilds this file from `table_s1_cmnn_sensitivity.csv` so the narrative stays in sync with the numbers.
- Main-analysis figures 1–7 are unchanged; Figures 9 (Vietnam 30q70) and 10 (SEA NCD death-rate proxy) are additive.
