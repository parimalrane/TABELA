# TABELA PROJECT INSTRUCTIONS

Version: Production
Status: Active Development

---

# 1. Project Identity

Project Name:

TABELA

Meaning:

Institutional Capital Rotation Intelligence Engine

Primary Objective:

Detect institutional capital rotation before it becomes obvious.

TABELA is not designed to predict markets.

Its purpose is to continuously answer one question:

> "Where is institutional money moving?"

---

# 2. Core Philosophy

Everything in TABELA exists to improve one capability:

Understand institutional capital flow.

Always prioritize:

Market Structure
↓

Theme Strength
↓

Institutional Rotation
↓

Stock Leadership

Never reverse this hierarchy.

Price moves first.
Narratives follow.

---

# 3. Primary Goals

The engine should:

• Detect strongest themes
• Detect weakest themes
• Identify institutional leaders
• Identify structural deterioration
• Detect emerging leadership
• Build historical market intelligence
• Explain why market leadership changes
• Produce actionable research

The engine does NOT:

• Generate buy/sell signals
• Replace technical analysis
• Replace discretionary trading
• Recommend entries or exits

---

# 4. Long-Term Vision

TABELA should become an institutional-grade market intelligence engine capable of answering questions such as:

• Which themes are strengthening?
• Which themes are weakening?
• Where is capital rotating?
• Which stocks consistently lead?
• Which leaders are emerging?
• Which themes are broadening?
• Which themes are narrowing?
• What changed today?
• Why did it change?
• Is today's move structural or temporary?

Every future enhancement should answer a market question that TABELA cannot currently answer.

Never add features simply because they are interesting.

---

# 5. Input Data

Current required inputs only:

ETF.csv
stocks.csv

No other files should be required for a normal daily run.

Removed dependency:

etf_master.csv

---

# 6. Daily Pipeline

Expected execution order:

1. ETF Engine

2. Theme Classification

3. Composite Engine

4. Breadth Engine

5. Long Engine

6. Distribution Engine

7. Short Engine

8. Rotation Engine

9. Snapshot Engine

10. Historical Intelligence Engine

11. Report Generation

Pipeline order is important.

Do not reorder without strong justification.

---

# 7. Stable Architecture

These modules are considered production stable.

Avoid unnecessary redesign.

ETF Engine

Theme Engine

Composite Engine

Breadth Engine

Institutional Leader Engine

Long Engine

Snapshot Engine

Historical Intelligence Engine

Theme Classification Engine

Unknown Classification Engine

TradingView Export

Only modify when objective evidence justifies it.

---

# 8. Historical Intelligence Principles

Historical data is a competitive advantage.

Never lose history.

History must continue growing every market day.

Historical reports should explain:

Rotation

Trend persistence

Leadership persistence

Breadth evolution

Capital flow

Never overwrite historical market intelligence.

---

# 9. JSON Philosophy

Snapshot JSON stores market state.

Never store presentation data.

Avoid storing:

Descriptions

Long text

Narratives

Generated summaries

Diagnostic output

Store only structured facts.

Derived intelligence belongs in reports.

---

# 10. Rotation Philosophy

Rotation Delta is diagnostic.

Snapshot is truth.

Historical Intelligence consumes:

Snapshots

Rotation Delta

Historical stock history

Never use Rotation Delta as the primary source of truth.

---

# 11. Breadth Philosophy

Breadth validates theme quality.

Theme strength alone is insufficient.

Always consider:

Number of strong stocks

Breadth %

Leadership concentration

Participation

Broad participation is healthier than isolated leadership.

---

# 12. Theme Philosophy

Themes drive the market.

Stocks belong to themes.

Themes belong to capital rotation.

Never evaluate stocks independently of themes.

Every stock should inherit context from:

Sector

Theme

Sub-theme

Institutional leadership

---

# 13. Long Engine Principles

Long Engine is one of the most important modules.

Protect its logic.

Institutional leaders should satisfy:

Strong composite score

Healthy trend

Relative strength

Institutional accumulation

Broad theme support

Avoid unnecessary complexity.

---

# 14. Short Engine Principles

Never short strong companies.

Short candidates should come from:

Structural weakness

Distribution

Persistent deterioration

Weak themes

Avoid:

Shorting market leaders

Shorting temporary pullbacks

Counter-trend ideas

---

# 15. Theme Evolution

Themes evolve.

The engine should detect:

New themes

Emerging themes

Expanding themes

Weakening themes

Retired themes

Theme evolution is a core competitive advantage.

---

# 16. Weekly Review Philosophy

Weekly Review analyzes:

Historical market behavior.

It is NOT for:

Code development

Architecture redesign

Trading psychology

Trade review

Weekly Review ends with:

Pass 6

Narrative & Theme Evolution Audit

This determines whether:

Theme mappings

Narratives

Sub-themes

require updating.

---

# 17. Output Principles

Outputs should explain:

What changed

Why it changed

Whether change is structural

Whether change is temporary

Outputs should minimize noise.

---

# 18. Future Enhancements

Every enhancement must satisfy:

Does this answer a new market question?

If not:

Do not add it.

Avoid feature creep.

---

# 19. Engineering Principles

Prefer simple architecture.

Prefer deterministic logic.

Prefer explainable outputs.

Avoid hidden heuristics.

Avoid unnecessary machine learning.

Favor transparent calculations.

---

# 20. Code Modification Rules

Small files (≤250 lines)

1–2 logical changes:

Provide patches only.

3 or more logical changes:

Provide entire replacement file.

Large files (>250 lines)

1–2 logical changes:

Provide patches.

3+ logical changes:

Provide complete replacement functions.

Replace entire large files only when explicitly requested.

Optimize for implementation speed.

---

# 21. Development Priorities

Priority 1

Reliability

Priority 2

Historical intelligence

Priority 3

Institutional rotation detection

Priority 4

Theme evolution

Priority 5

Presentation polish

Never sacrifice correctness for appearance.

---

# 22. Quality Rules

Never fabricate market explanations.

Never invent catalysts.

Always distinguish:

Observed facts

Derived conclusions

Speculation

Unknowns should remain unknown.

---

# 23. Design Principles

Every engine should answer one question.

Every report should improve decision quality.

Every historical record should compound knowledge.

Every enhancement should increase institutional insight.

If a feature does not improve institutional capital rotation intelligence, it does not belong in TABELA.

---

# 24. Ultimate Mission

Build the best institutional capital rotation intelligence engine possible.

The engine should become progressively smarter every market day because its historical intelligence continuously compounds.

Historical knowledge is TABELA's moat.

Protect it.