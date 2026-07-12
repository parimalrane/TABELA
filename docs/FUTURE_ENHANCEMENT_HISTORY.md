# FUTURE_ENHANCEMENT_HISTORY.md

# TABELA Roadmap
### Institutional Capital Rotation Intelligence Engine

---

# VISION

Build TABELA into a self-contained market intelligence platform that continuously accumulates institutional market knowledge.

The guiding principle is:

> Generate once.
> Reuse forever.
> Build incremental intelligence instead of recalculating history.

---

# CORE ARCHITECTURE

```
Daily Intelligence
        │
        ▼
Weekly Intelligence
        │
        ▼
Monthly Intelligence
        │
        ▼
Historical Intelligence
        │
        ▼
Dashboard / Explainability / AI Assistant
```

---

# DESIGN PRINCIPLES

## Intelligence Hierarchy

Daily
- Raw market state

Weekly
- Operational intelligence

Monthly
- Permanent historical intelligence

Everything above Daily must reuse previously generated intelligence whenever possible.

---

## Single Source of Truth

Daily JSON files are the production database.

Weekly consumes Daily.

Monthly consumes Weekly plus current month's Daily JSON.

Future engines consume Monthly intelligence whenever possible.

---

## Manual Execution

Daily
- Executed from main.py

Weekly
- Manual execution after Friday market close

Monthly
- Manual execution during the first week of each month

No scheduling.

No calendar logic.

No holiday management.

---

## Archive Strategy

Daily JSON files remain available until Monthly Intelligence has been successfully generated.

After verification:

- Archive daily JSON files
- Never permanently delete unless explicitly requested

Archives become cold storage.

---

# PROJECT PHASES

---

# PHASE 1
## Production Foundation

Status
- Nearly Complete

Objectives

- Stable production pipeline
- Historical database
- Daily snapshot generation
- Rotation engine
- Theme intelligence
- Historical intelligence
- Weekly intelligence

Deliverables

- Production-ready daily pipeline
- Stable JSON database
- Weekly intelligence report

---

# PHASE 2
## Weekly Intelligence

Status
- Current Priority

Objectives

Complete Weekly Intelligence.

Deliverables

- Executive Summary
- Weekly Theme Intelligence
- Weekly Stock Intelligence
- Leadership Analysis
- Breadth Analysis
- Rotation Summary
- Historical Comparison
- Institutional Observations
- Weekly Intelligence JSON
- Weekly Markdown Report

Success Criteria

Weekly report fully explains one trading week without requiring daily terminal output.

---

# PHASE 3
## Monthly Intelligence

Objectives

Build the permanent monthly market intelligence report.

Inputs

- Weekly Intelligence JSON
- Current month's Daily JSON
- Theme mapping
- Company mapping

Outputs

- Monthly Intelligence JSON
- Monthly Markdown Report

Monthly Report Sections

- Executive Summary
- Market Regime
- Theme Evolution
- Theme Rotation
- Theme Health
- Institutional Leadership
- Persistent Leaders
- Persistent Shorts
- Breadth Trends
- Unknown Leader Evolution
- Episodic Pivot Summary
- Historical Comparison
- Market Narrative
- Lessons Learned

Success Criteria

Monthly report contains sufficient historical intelligence that daily JSON files can be archived.

---

# PHASE 4
## Historical Intelligence

Objectives

Build cumulative market memory.

Capabilities

- Multi-month comparison
- Leadership persistence
- Theme lifecycle
- Rotation persistence
- Breadth evolution
- Institutional behavior changes

Outputs

Historical intelligence consumed by every future engine.

---

# PHASE 5
## Explainability Engine

Purpose

Explain every decision made by TABELA.

Capabilities

- explain()
- why_added()
- why_removed()
- why_not()
- compare()
- explain_theme()
- explain_history()

Read-only.

No production logic.

---

# PHASE 6
## Dashboard

Objectives

Interactive visualization.

Pages

- Market Overview
- Theme Explorer
- Stock Explorer
- Rotation Timeline
- Weekly Intelligence
- Monthly Intelligence
- Historical Explorer

Dashboard reads JSON only.

---

# PHASE 7
## Advanced Intelligence

Projects

### Theme Health Engine

Combine

- ETF strength
- Breadth
- Leadership
- Relative Strength
- Historical persistence

---

### Leader Lifecycle Engine

Track

Emerging

↓

Leader

↓

Institutional Leader

↓

Weakening

↓

Distribution

---

### Unknown Leader Evolution

Automatically

Unknown

↓

Candidate Theme

↓

Permanent Theme

---

### Stock Contribution Engine

Determine

- Theme contributors
- Theme detractors

---

### Episodic Pivot Engine

Historical EP detection.

---

### Narrative Detection

Automatically identify

- AI
- Robotics
- Defense
- Nuclear
- Power
- Data Centers
- Emerging institutional narratives

---

### Theme Evolution

Automatically

- Merge themes
- Split themes
- Retire obsolete themes
- Create new themes

---

# PHASE 8
## Research Integration

Future

- Finviz Scanner History
- DeepVue History
- Catalyst Database

---

# PHASE 9
## AI Assistant

Natural language interface.

Examples

- Why NVDA?
- Why not CAT?
- Compare MU vs STX
- Explain today's market
- Explain this month's rotation
- Show strongest themes
- Show weakening leaders

---

# PHASE 10
## Engineering Excellence

Objectives

- Unit Tests
- Regression Tests
- Performance Profiling
- Data Validation
- Integrity Checks
- Automatic Consistency Audits

---

# LONG-TERM DATA FLOW

```
Daily CSV
        │
        ▼
Daily JSON
        │
        ▼
Weekly Intelligence
(JSON + Markdown)
        │
        ▼
Monthly Intelligence
(JSON + Markdown)
        │
        ▼
Archive Daily JSON
        │
        ▼
Dashboard
Explainability
Historical Queries
AI Assistant
```

---

# IMPLEMENTATION PRIORITY

## Priority 1

- Complete Weekly Intelligence
- Weekly Intelligence JSON
- Complete Monthly Intelligence
- Monthly Intelligence JSON

---

## Priority 2

- Historical Intelligence Expansion
- Dashboard
- Explainability Engine

---

## Priority 3

- Leader Lifecycle
- Unknown Leader Evolution
- Theme Health
- Stock Contribution

---

## Priority 4

- Narrative Detection
- Theme Evolution
- Episodic Pivot Engine

---

## Priority 5

- Research Integrations

---

## Priority 6

- AI Assistant

---

## Priority 7

- Engineering Improvements

---

# SUCCESS METRICS

Daily

- Stable production pipeline
- Reliable JSON generation

Weekly

- Complete explanation of one trading week

Monthly

- Permanent historical intelligence
- Daily JSON safely archived after validation

Historical

- Multi-year institutional market memory

Ultimate Goal

TABELA answers:

"What is institutional capital doing, why is it happening, how has it evolved over time, and what similar situations has the market experienced before?"




======================


Updated Top Priority Order
Phase 1
✅ Production Pipeline
✅ Historical Database
✅ Weekly Intelligence
⏳ Monthly Intelligence

Phase 2 (Highest Value)
Market Memory Engine
Theme Health Engine
Leader Lifecycle Engine

Phase 3
Dashboard
Explainability Engine
Unknown Leader Evolution
Stock Contribution Engine

Phase 4
Episodic Pivot Detection
Finviz Historical Integration
DeepVue Historical Integration
Catalyst Database

Phase 5
AI Assistant
Theme Evolution (manual-assisted, not automatic)
Engineering improvements