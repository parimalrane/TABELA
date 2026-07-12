# LESSONS_LEARNED.md

Version: 1.0

Purpose

This document captures important lessons learned during the development of TABELA.

Unlike technical documentation, these are practical engineering and project lessons that should influence future decisions.

Read this document before making significant architectural changes.

---

# 1. Architecture Lessons

## 1.1 Simplicity Wins

Large architectural rewrites rarely produced better results.

Small, incremental improvements were consistently more successful.

Rule

Prefer improving an existing engine over replacing it.

---

## 1.2 One Engine = One Responsibility

Engines became easier to:

- understand
- test
- debug
- replace

Avoid combining unrelated responsibilities.

---

## 1.3 The Pipeline Is the Backbone

Allowing engines to communicate directly creates hidden dependencies.

The pipeline should remain the only orchestrator.

Rule

Engine A should not directly invoke Engine B.

---

## 1.4 Stable Engines Should Stay Stable

Several engines eventually became mature enough that modifying them created more problems than benefits.

Treat mature engines as production components.

Examples

- ETF Engine
- Composite Engine
- Breadth Engine
- Snapshot Engine

---

# 2. Data Lessons

## 2.1 Historical Data Is More Valuable Than Daily Output

Daily reports are temporary.

Historical data becomes increasingly valuable over time.

Protect historical data.

---

## 2.2 JSON Is the Source of Truth

Console output is presentation.

JSON is data.

Never reconstruct history from console output.

---

## 2.3 Structured Data Ages Better Than Reports

Reports change.

Data should not.

Persist facts, not presentation.

---

## 2.4 Backward Compatibility Matters

Changing schemas creates unnecessary migration work.

Rule

Prefer adding fields rather than changing existing ones.

---

# 3. Market Intelligence Lessons

## 3.1 Themes Matter More Than Individual Stocks

Strong stocks often emerge because their themes strengthen.

Analyze themes before analyzing stocks.

---

## 3.2 Breadth Is Essential

A theme with one strong stock is very different from a theme with broad participation.

Always validate theme strength using breadth.

---

## 3.3 Historical Context Changes Everything

Single-day observations are often misleading.

Trends become clearer when viewed across multiple sessions.

---

## 3.4 Leadership Is Dynamic

Leadership changes gradually.

Historical tracking is required to understand rotation.

---

# 4. Development Lessons

## 4.1 Avoid Feature Creep

Many proposed ideas sounded useful but did not improve institutional capital analysis.

Every new feature should answer a market question that cannot already be answered.

---

## 4.2 Documentation Saves Time

Well-maintained documentation reduced repeated explanations and simplified future work.

Keep documentation synchronized with the implementation.

---

## 4.3 Refactor Only With Evidence

Do not redesign code because it "looks better."

Refactor only when there is a measurable benefit.

---

## 4.4 Test Incrementally

Large changes are difficult to debug.

Validate each change before moving to the next.

---

# 5. AI Collaboration Lessons

## 5.1 Context Is Valuable

AI performs significantly better when it understands:

- project goals
- architecture
- terminology
- constraints

Provide context before requesting changes.

---

## 5.2 Protect Stable Logic

AI tends to optimize aggressively.

Stable, validated logic should not be rewritten without clear justification.

---

## 5.3 Be Specific

Precise requirements consistently produced better results than broad requests.

Define:

- objective
- constraints
- expected output

---

## 5.4 Review AI Output

AI accelerates development.

It does not replace engineering review.

Validate:

- correctness
- architecture
- downstream effects

---

# 6. Code Quality Lessons

- Avoid duplicate calculations.
- Avoid circular dependencies.
- Avoid hidden state.
- Avoid unnecessary abstraction.
- Prefer explicit logic.
- Keep functions focused.

---

# 7. Project Management Lessons

## Preserve Knowledge

Code explains how.

Documentation explains why.

Both are necessary.

---

## Keep the Roadmap Manageable

A prioritized roadmap is more valuable than a long wish list.

Review priorities periodically.

---

## Finish Before Expanding

Complete existing modules before adding major new functionality.

---

# 8. Mistakes Worth Avoiding

- Mixing business logic with presentation.
- Reading the same data multiple times.
- Breaking historical compatibility.
- Introducing unnecessary dependencies.
- Overengineering simple solutions.
- Creating duplicate analytics.
- Redesigning stable modules without evidence.

---

# 9. Success Factors

The following decisions contributed most to TABELA's evolution:

- Modular architecture
- Linear pipeline
- Historical persistence
- Theme-first analysis
- Breadth validation
- Incremental development
- Comprehensive documentation

---

# 10. Future Development Checklist

Before implementing any significant change, ask:

1. Does this solve a real problem?
2. Does it answer a new market question?
3. Can it reuse existing data?
4. Does it preserve historical compatibility?
5. Is the architecture becoming simpler?
6. Will another developer understand it?
7. Does the benefit justify the added complexity?

If several answers are "No", reconsider the change.

---

# Final Principle

TABELA should evolve by accumulating knowledge, not complexity.

Each enhancement should make the system easier to understand, more reliable, and more useful for analyzing institutional capital rotation.