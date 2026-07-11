# TABELA - Future Enhancements

---

# STATUS

Current Version
- Production Pipeline
- Historical Database
- Historical Query Engine
- Historical Intelligence Engine
- Weekly Intelligence (Foundation)

---

# PRIORITY 1 - CORE INTELLIGENCE

## 1. Weekly Intelligence Completion
Status: In Progress

Remaining
- Weekly narrative
- Theme winners/losers
- Leadership changes
- Sector rotation summary
- Institutional observations
- Markdown/PDF report polishing

Priority: HIGH

---

## 2. Dashboard

Historical dashboards

- Theme trends
- Breadth trends
- Long candidates
- Unknown leaders
- Rotation timeline
- Historical queries

Priority: HIGH

---

## 3. Explainability Engine (NEW)

Purpose

Explain every TABELA decision without modifying production logic.

Requirements

- Read-only
- Uses Historical Query Engine
- Uses historical JSON database
- No scoring
- No ranking
- No filtering

Capabilities

- explain(TICKER)
- why_not(TICKER)
- why_added(TICKER)
- why_removed(TICKER)
- compare(TICKER1, TICKER2)
- explain_theme(TICKER)
- explain_scores(TICKER)
- explain_history(TICKER)

Future

Natural language interface

Example

> Why isn't CAT a Long Candidate?

Output

- Theme
- Theme Class
- RS
- Composite Score
- Long Score
- Threshold comparison
- Exact exclusion reason

Priority: HIGH

---

# PRIORITY 2 - MARKET INTELLIGENCE

## Narrative Detection Engine

Detect

- AI
- Nuclear
- Defense
- Robotics
- Power
- Data Centers

Track

- Emerging narratives
- Weakening narratives
- New institutional themes

---

## Theme Evolution Engine

Automatically

- Create themes
- Merge themes
- Split themes
- Retire obsolete themes

Includes

Theme → Sub-theme hierarchy

---

## Theme Health Score

Combine

- ETF strength
- Breadth
- Leadership
- Relative strength
- Historical persistence

---

## Institutional Rotation Timeline

Historical visualization

- Daily
- Weekly
- Monthly

---

# PRIORITY 3 - STOCK INTELLIGENCE

## Stock Contribution Engine

Questions

- Which stocks drive a theme?
- Which stocks weaken a theme?

---

## Leader Lifecycle

Track

Emerging
↓

Leader
↓

Mature Leader
↓

Weakening
↓

Distribution

---

## Unknown Leader Evolution

Improve

- Classification
- Tracking
- Promotion to permanent themes

---

## Episodic Pivot Detection

Historical EP detection

Track

- Earnings
- Guidance
- Contracts
- FDA
- Government
- Delayed EP

---

# PRIORITY 4 - RESEARCH

## Finviz Scanner Integration

Daily

- Import
- Store
- Historical queries

---

## DeepVue Theme Tracker Integration

Historical storage

Weekly comparison

---

## Catalyst Database

Store

- Earnings
- Contracts
- FDA
- Partnerships
- Analyst upgrades

---

# PRIORITY 5 - VISUALIZATION

Interactive Dashboard

Pages

- Market Overview
- Theme Explorer
- Stock Explorer
- Historical Timeline
- Weekly Intelligence
- Explainability

---

# PRIORITY 6 - AI ASSISTANT

Natural language

Examples

Why CAT?

Why not CAT?

Compare MU STX

Show leaders in AI

Which theme improved most?

What changed since last week?

Explain today's market.

---

# PRIORITY 7 - OPTIMIZATION

ETF Universe Review

After

3–4 weeks of production history

Evaluate

- False positives
- Missing themes
- ETF redundancy
- Coverage

No changes before sufficient evidence.

---

# ENGINEERING

Future improvements

- Unit tests
- Regression tests
- Performance profiling
- Data validation
- Automatic integrity checks

---

# DESIGN PRINCIPLES

Never duplicate business logic.

Historical JSON remains the single source of truth.

Explanation engines are read-only.

Production engines never depend on explainability.

Dashboard consumes JSON only.

Every decision should be explainable.

Root-cause fixes preferred over parallel engines.

Evidence before calibration changes.




=====







I want to reuse the generated output as much as possible instead of recalculate , build incremental intelligence 

1) daily I generate several json files 
2) Weekly report read daily jason files , 2 csv mapping files
3) monthly report should read only weekly reports - and daily json files for last 1 month market data i.e. approximately 21 market days
4) No quarterly or monthly reports , My monthly reports should be exahustive enough
5) I will clean up my json files as soon as monthly reports are generated (not today , but this is the plan)

Any pros / cons?

Why I want this way is daily json will be growing , daily 10 files , and I will end up with 3600 files in a yeay and most of the information will be already available in weekly / montly files so will be duplicate

Also, I don't want to merge my weekly or monthly reports generation in main.py daily execution. 

I will run weekly process every friday after market close and after all json  files are generated or  of saturday or Sunday
I will run monthly process any day in 1st week of the month , mostly 1st day of month or max 2nd day if any weekend holiday on 1st 

I don't want to add any calendar or complexity , It is my responsibility to run weekly report post froday close and monthly report post month end

