I would actually standardize this into one weekly ritual.

## Saturday Prompt

> **Perform TABELA Weekly Knowledge Review.**
>
> Review this week's TABELA outputs and historical JSONs as TABELA's Institutional Research Analyst.
>
> Your objectives:
>
> 1. Recommend additions to `stock_theme_mapping.csv`.
> 2. Recommend theme changes for existing mapped stocks.
> 3. Recommend removals (only with very strong evidence).
> 4. Identify emerging institutional narratives.
> 5. Identify obsolete narratives.
> 6. Recommend parser improvements instead of manual mappings whenever possible.
> 7. Challenge every recommendation—do not recommend a change unless it materially improves institutional intelligence.
> 8. Produce an updated `stock_theme_mapping.csv` only if changes are recommended; otherwise explicitly state "No changes recommended."

---

# Files Required

## Mandatory

### 1. Weekly TABELA outputs

Preferably Monday–Friday.

These contain:

* Market Rotation Summary
* Breadth
* Long Universe
* Short Universe
* Historical Intelligence
* Unknown Leaders
* Rotation Delta

This is the primary research input.

---

### 2. Market Snapshot JSONs

```
market_data/snapshots/
```

Monday → Friday

Required.

---

## Optional (Recommended)

### 3. Unknown Classification JSONs

```
market_data/unknown_classification/
```

This helps answer:

* Which Unknowns persist?
* Which deserve mapping?

---

### 4. Stock History JSONs

```
market_data/stock_universe/
```

Helpful, but not required every week.

I'd probably request these only when investigating a specific company.

---

### 5. Current `stock_theme_mapping.csv`

Always include the latest version.

---

### 6. Current `industry_theme_mapping.csv`

Only if you've modified it since the last review.

Otherwise I can assume it's unchanged.

---

# Output I will produce

Every Saturday, in this exact order:

```text
1. Executive Summary

2. Mapping Additions

3. Mapping Changes

4. Mapping Removals

5. New Institutional Narratives

6. Obsolete Narratives

7. Parser Improvement Opportunities

8. Updated stock_theme_mapping.csv (if required)

9. Decision Log
```

---

# One improvement

Since you're already generating JSON every day, **don't upload 5 separate daily outputs**.

Instead, every Saturday create one folder (or ZIP) like:

```
weekly_review/
│
├── snapshots/
├── stock_universe/
├── unknown_classification/
├── monday.txt
├── tuesday.txt
├── wednesday.txt
├── thursday.txt
├── friday.txt
├── stock_theme_mapping.csv
└── industry_theme_mapping.csv
```
