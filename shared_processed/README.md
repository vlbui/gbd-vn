# shared_processed/

Derived data produced by `shared/pipeline/` and consumed by two or more
papers. Regenerable (not stored in git — `.gitignored`).

## File inventory

| File | Produced by | Consumed by | Contents |
|------|-------------|-------------|----------|
| `burden_sea.csv` | `01_load_clean` | 01 (+ future papers) | Level-1 GBD burden, 11 SEA countries, 1990-2023, long format |
| `age_specific.csv` | `01_load_clean` | 01, 04 decomposition | Vietnam age-specific burden, 17 age groups |
| `population.csv` | `01_load_clean` | 01, 04 decomposition | Vietnam population by age and sex |
| `yll_yld_sea.csv` | `01_load_clean` | 01 (+ future) | YLLs + YLDs, 11 SEA countries |
| `sdi_sea.csv` | `01_load_clean` | 01 (+ future) | SDI trajectory, 11 SEA countries 1990-2023 |
| `probability_30q70.csv` | `02_metrics` | 01 table 1 | Vietnam 30q70 NCD + CMNN by year |
| `cmnn_split.csv` | `02_metrics` | 01 sensitivity | CMNN split (C-only vs M+N+N) with NCD-share variants |
| `yll_yld_ratio.csv` | `02_metrics` | 01 | Vietnam YLL + YLD + ratio by year |
| `sea_30q70.csv` | paper 01 `chiang_30q70.py` | 01 figure 4 | Strict SDG 3.4.1 30q70 long form, 11 SEA |
| `level1_sea_asr.csv` | legacy | 01 | Age-standardized rate pivot, SEA (cached for figures) |
| `level1_sea_allages.csv` | legacy | 01 | All-ages pivot, SEA |
| `level1_sea_1990_2023.csv` | legacy | 01 | Level-1 1990 + 2023 snapshot, SEA |

## Regenerating

```
python shared/pipeline/run_pipeline.py
```

Paper-01-specific extras (`sea_30q70.csv`) come from
`projects/01_epi_transition/scripts/chiang_30q70.py`.
