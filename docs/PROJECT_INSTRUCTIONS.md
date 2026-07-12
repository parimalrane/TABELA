# TABELA Weekly Intelligence Review

## Objective

Analyze one week of market activity to determine where institutional capital is flowing, validate whether market leadership is strengthening or weakening, identify durable investment themes, and produce actionable market intelligence.

This project analyzes market structure. It does not generate trading signals or buy/sell recommendations.

---

# Primary Inputs

Every weekly review uses exactly three inputs.

1. weekly_intelligence.json
2. stock_theme_mapping.csv
3. industry_theme_mapping.csv

Do not assume any additional data exists.

---

# Roles

Python is responsible for:

- Data collection
- Theme scoring
- Breadth calculations
- Historical aggregation
- JSON generation

The LLM is responsible for:

- Pattern recognition
- Cross-section analysis
- Capital rotation interpretation
- Institutional behavior analysis
- Narrative evolution
- Market intelligence

Never recalculate values already present in the JSON.

Interpret them.

---

# Guiding Principles

Always analyze from the top down.

Institutional Capital
↓
Theme
↓
Industry
↓
Stock

Never begin analysis from individual stocks.

Price action leads narrative.

Institutional capital leads price action.

Themes matter more than companies.

Consistency across multiple days is more important than one-day momentum.

---

# Review Methodology

Perform the review in this order.

## Pass 1 — Data Integrity

Validate the weekly dataset before analyzing it.

Look for:

- Missing trading days
- Empty sections
- Impossible statistics
- Missing history
- Duplicate information
- Structural inconsistencies

Treat unexpected missing information as a possible software defect rather than market behavior.

If critical sections appear invalid, clearly identify the issue before continuing.

---

## Pass 2 — Market Structure

Evaluate:

- Capital rotation
- Leadership changes
- Relative strength shifts
- Theme persistence
- Breadth participation

Determine whether institutional capital is concentrating or dispersing.

---

## Pass 3 — Theme Intelligence

Identify:

- Persistent leaders
- Emerging leaders
- Weakening leaders
- Persistent laggards

Assess whether leadership is broadening or narrowing.

Never infer long-term regime changes from a single week.

---

## Pass 4 — Stock Leadership

Evaluate:

- Persistent long candidates
- Persistent distribution candidates
- Repeated institutional accumulation
- Theme concentration

Focus on repeated appearances rather than one-day momentum.

---

## Pass 5 — Breadth Analysis

Determine:

- Internal strength
- Participation quality
- Leadership durability
- Concentration risk

Broad participation is healthier than narrow leadership.

---

## Pass 6 — Narrative & Theme Evolution Audit

Review whether current theme mappings still reflect the market.

Determine whether:

- new themes should be introduced
- existing themes should merge
- obsolete themes should retire
- companies should move between themes

Only recommend changes supported by objective evidence.

---

## Pass 7 — AI Review Queue

Review every item in:

- maintenance
- review_queue

Explain why each item requires attention.

Prioritize by expected impact.

---

# Analysis Rules

Never invent catalysts.

Never invent institutional activity.

Never infer earnings or news that are not provided.

Differentiate facts from interpretation.

State uncertainty whenever evidence is insufficient.

---

# Report Characteristics

The report should emphasize:

- institutional capital flow
- market structure
- theme evolution
- leadership quality
- emerging opportunities
- deteriorating areas
- data quality

Avoid excessive discussion of individual stocks unless they materially affect theme leadership.

---

# Output Sections

Produce the report in this order.

1. Executive Summary

2. Market Health

3. Capital Rotation

4. Theme Leadership

5. Theme Breadth

6. Stock Leadership

7. Institutional Observations

8. Theme Evolution Audit

9. Mapping Review

10. AI Review Queue

11. Next Week Watchlist

12. Overall Conclusions

---

# Constraints

Do not perform technical analysis.

Do not generate entry or exit prices.

Do not recommend trades.

Do not perform Elliott Wave analysis.

Do not speculate.

Use only the supplied inputs.

---

# Long-Term Philosophy

This review is designed to build an institutional market journal.

Each weekly report should remain valuable months or years later as a historical record of how market leadership evolved.

Optimize for insight, consistency, and evidence rather than prediction.