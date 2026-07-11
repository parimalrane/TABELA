# WEEKLY_INTELLIGENCE.md

## Dataset Inventory

| Dataset | Files |
|---------|------:|
| Market Snapshots | 4 |
| Rotation Delta | 4 |
| Stock Universe History | 4 |
| Watchlist History | 4 |
| Unknown Classification | 4 |
| Scanner History | 3 |
| Daily Reports | 4 |

Additional reference datasets present:

- ETF.csv
- stocks.csv
- stock_theme_mapping.csv
- industry_theme_mapping.csv

---

# Data Integrity

## JSON Cross Validation

Result: PASS

Observations:

- Snapshot JSONs present for every trading day.
- Rotation Delta JSONs present for every trading day.
- Watchlist history present for every trading day.
- Unknown Classification present for every trading day.
- Daily reports available for every trading day.
- Scanner history begins on 2026-07-08 (no 2026-07-07 scanner CSV).

Unknown Classification datasets contain zero unknown stocks throughout the week.

No structural inconsistencies were detected between available structured datasets.

---

# Weekly Theme Evolution

Daily leading themes (Top 5):

| Date | Top Themes |
|------|------------|
| 2026-07-07 | Biotech, Semiconductors, Healthcare, Insurance, Artificial Intelligence |
| 2026-07-08 | Biotech, Healthcare, Insurance, Pharma, Banking |
| 2026-07-09 | Biotech, Healthcare, Pharma, Insurance, Semiconductors |
| 2026-07-10 | Biotech, Semiconductors, Cloud Computing, Healthcare, Artificial Intelligence |

Computed observations:

- Biotech remained Rank 1 throughout the week.
- Healthcare appeared in the weekly Top 5 every day.
- Insurance remained a recurring leadership theme.
- Semiconductors exited and re-entered the Top 5.
- Artificial Intelligence appeared at both beginning and end of week.
- Cloud Computing entered the Top 5 on 2026-07-10.
- Banking appeared only on 2026-07-08.
- Pharma strengthened during the middle of the week.

---

# Weekly Breadth Evolution

Breadth data available for all four trading sessions.

Breadth metrics computed from:

- Total Stocks
- Strong Stocks
- Breadth %
- Weighted Breadth Score

Weekly comparison is fully supported by the snapshot datasets.

---

# Weekly Rotation Evolution

Rotation Delta datasets available:

- 2026-07-07
- 2026-07-08
- 2026-07-09
- 2026-07-10

Daily rotation history is continuous with no missing JSON files.

---

# Leadership Persistence

Watchlist history available for all four sessions.

Highest persistence (present all four days):

- VSH
- MXL
- VIRT
- AMBQ
- MRX
- SIMO
- ASX
- ALGM
- SNDK
- ICHR
- ACMR
- UMC
- MU
- STM
- MKSI

Persistence counts computed directly from watchlist JSON files.

---

# Distribution Persistence

Persistent short-watch names identified:

| Symbol | Days Present |
|--------|-------------:|
| RKLB | 3 |
| IONQ | 2 |
| RDNT | 2 |
| LEGN | 2 |

All remaining symbols appeared once.

---

# Unknown Persistence

Unknown Classification results:

| Date | Unknown Stocks |
|------|---------------:|
| 2026-07-07 | 0 |
| 2026-07-08 | 0 |
| 2026-07-09 | 0 |
| 2026-07-10 | 0 |

No persistence detected.

---

# Scanner Persistence

Scanner CSVs available for:

- 2026-07-08
- 2026-07-09
- 2026-07-10

No ticker appeared in more than one daily scanner file during the available period.

---

# ETF Observations

ETF reference dataset present.

Weekly snapshots contain theme rankings derived from ETF/theme scoring.

Theme leadership remained internally consistent with snapshot rankings across the week.

---

# Mapping Observations

Reference mapping datasets present:

- stock_theme_mapping.csv
- industry_theme_mapping.csv

Snapshot classifications are consistent with mapped theme outputs.

No mapping inconsistencies were identified from structured data validation.

---

# Engine Observations

Structured engine outputs generated successfully for:

- Theme Engine
- Breadth Engine
- Rotation Engine
- Watchlist Engine
- Unknown Classification Engine
- Historical Snapshot Engine

No missing engine outputs were detected for the available trading sessions.

---

# Evidence Tables

## Dataset Counts

| Dataset | Count |
|---------|------:|
| Snapshots | 4 |
| Rotation Delta | 4 |
| Watchlists | 4 |
| Unknown Classification | 4 |
| Scanner History | 3 |
| Daily Reports | 4 |
| Stock Universe History | 4 |

---

## Theme Presence

| Theme | Days in Top 5 |
|------|--------------:|
| Biotech | 4 |
| Healthcare | 4 |
| Insurance | 3 |
| Semiconductors | 3 |
| Artificial Intelligence | 2 |
| Pharma | 2 |
| Cloud Computing | 1 |
| Banking | 1 |

---

## Persistent Long Candidates

Present all four sessions:

- VSH
- MXL
- VIRT
- AMBQ
- MRX
- SIMO
- ASX
- ALGM
- SNDK
- ICHR
- ACMR
- UMC
- MU
- STM
- MKSI

---

## Persistent Short Candidates

| Symbol | Sessions |
|--------|---------:|
| RKLB | 3 |
| IONQ | 2 |
| RDNT | 2 |
| LEGN | 2 |

---

# Data Quality Notes

- JSON datasets were treated as the authoritative source.
- Daily reports are available for cross-checking.
- Scanner history is incomplete for the first trading day (2026-07-07).
- Unknown Classification remained empty throughout the week.
- No structural data corruption or missing JSON collections were detected.
- All findings above are computed directly from the available structured datasets without narrative interpretation or speculation.