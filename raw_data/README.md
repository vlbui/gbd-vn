# raw_data/

Immutable IHME Global Burden of Disease downloads. Not redistributable;
`.gitignored`. Re-download from the IHME GBD Results Tool if missing.

## Layout

```
raw_data/
├── burden/                 GBD Results Tool CSV queries
├── covariates/             SDI + cause hierarchy
└── air_pollution/
    ├── exposure/           PM2.5 / HAP / NO2 / ozone
    ├── rr_curves/          cause-specific relative-risk curves
    └── codebook/           variable definitions
```

## burden/

Seven IHME GBD Results Tool CSV extracts (GBD 2023 round). All filtered
to the SEA region (11 countries) + Vietnam national data, 1990-2023.

| File | Contents |
|------|----------|
| `query1_level1.csv` | Level-1 cause groups (CMNN / NCD / Injuries), 10 SEA countries |
| `query1_level1_timor.csv` | Same schema, Timor-Leste only (separate query because TL wasn't in the SEA group list at extraction time) |
| `query2a_cmnn.csv` | Vietnam level-2 CMNN detail |
| `query2b_ncd.csv` | Vietnam level-2 NCD detail |
| `query3_age.csv` | Vietnam age-specific burden, 17 age groups |
| `query4_pop.csv` | Vietnam population by age and sex |
| `query5_yll_yld.csv` | YLLs + YLDs, Vietnam + SEA |
| `query6_30q70.csv` | Strict SDG 3.4.1 NCD deaths by 5-year age band, SEA (11 countries) |

Download via <https://vizhub.healthdata.org/gbd-results/>.

## covariates/

| File | Contents |
|------|----------|
| `SDI.csv` | Socio-demographic Index, all GBD locations 1950-2023 |
| `hierarchy.XLSX` | GBD cause hierarchy (levels 1-4) |

## air_pollution/

See [air_pollution/README.md](air_pollution/README.md) for file inventory.
