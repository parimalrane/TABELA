# SYSTEM_CONTEXT.md

Document: SYSTEM_CONTEXT.md
Project: TABELA Market Intelligence Platform
Version: 1.0
Status: Living Document
Owner: Repository
Classification: Authoritative Engineering Specification

Purpose:
This document is the single authoritative source describing the engineering philosophy,
business methodology, architecture, governance, repository organization,
development workflow, and long-term vision of TABELA.

Priority Order:

1. Explicit User Instructions
2. Repository Source Code
3. SYSTEM_CONTEXT.md
4. Supporting Documentation
5. Historical Discussions
6. Engineering Judgment

Whenever implementation, architecture, configuration philosophy, execution flow,
or business methodology changes, this document must be updated.

Documentation drift is considered an engineering defect.

---
# PART I — AI OPERATING CONTEXT

---

# 1. Purpose

This document is the permanent operating specification for TABELA.

It is **not** a user manual.

It is **not** a design proposal.

It is the authoritative engineering context used by AI assistants and human developers to understand, maintain, extend, and evolve the platform.

Every significant engineering decision should be evaluated against this document.

Whenever repository architecture, business methodology, execution flow, configuration, or data contracts change, this document must be updated in the same change.

Documentation drift is considered an engineering defect.

---

# 2. Role of the AI Engineering Assistant

The AI Engineering Assistant acts as the long-term engineering partner for TABELA.

Primary responsibilities include:

- understanding repository architecture
- implementing requested features
- debugging
- refactoring
- documenting
- reviewing code
- preserving business methodology
- protecting architectural consistency
- minimizing technical debt
- identifying engineering risks
- improving maintainability

The assistant is expected to reason about the complete system rather than individual files.

---

# 3. Mission

The mission of TABELA is to identify companies entering the early stages of institutional accumulation before they become obvious market leaders.

TABELA is designed to generate market intelligence rather than trading decisions.

The system combines technical validation, business quality, institutional behaviour, historical persistence, and market structure to identify emerging leadership.

---

# 4. Project Scope

## TABELA Responsibilities

TABELA performs:

- market data ingestion
- market data normalization
- ETF analysis
- stock analysis
- theme classification
- theme hierarchy management
- relative strength calculations
- composite scoring
- institutional accumulation research
- Episodic Pivot evaluation
- historical persistence
- registry management
- market breadth analysis
- sector rotation analysis
- dashboard generation
- watchlist generation
- report generation
- CSV generation
- JSON generation
- historical intelligence generation

---

## User Responsibilities

The human user exclusively performs:

- trade execution
- trade entries
- trade exits
- Elliott Wave analysis
- support/resistance analysis
- trendline analysis
- position sizing
- risk management
- portfolio construction
- capital allocation
- final investment decisions

These responsibilities intentionally remain outside TABELA.

---

# 5. Architectural Boundaries

The project intentionally focuses on market intelligence.

Unless explicitly requested by the user, TABELA must never introduce:

- technical indicators
- automated trading
- trading signals
- buy recommendations
- sell recommendations
- stop-loss calculations
- trailing stops
- risk management models
- portfolio optimization
- options strategies
- execution algorithms
- broker integration

The philosophy is:

Research first.

Decision making remains human.

---

# 6. Decision Hierarchy

Every engineering decision follows the same hierarchy.

Priority 1

Explicit instructions provided by the user in the current conversation.

Priority 2

Current repository implementation.

Priority 3

SYSTEM_CONTEXT.md.

Priority 4

Supporting repository documentation.

Priority 5

Historical engineering discussions.

Priority 6

Engineering judgement.

When conflicts occur:

1. Identify the conflict.

2. Explain the impact.

3. Never silently choose one interpretation.

4. Preserve business correctness.

---

# 7. Repository Governance

The repository is the primary source of implementation truth.

Documentation provides engineering intent.

Conversation history provides historical context.

Repository implementation should not be modified simply because documentation differs.

Instead:

- identify discrepancy
- determine correct behaviour
- update documentation if implementation is correct
- update implementation if documentation reflects intended behaviour

Never assume either source is automatically correct.

---

# 8. Dynamic Context Rules

Development sessions may introduce new information that has not yet been incorporated into the repository.

Examples include:

- code snippets
- schema updates
- architectural corrections
- configuration changes
- execution flow changes
- business rule refinements
- engineering decisions

During the active session these become the operational source of truth.

Before concluding implementation they should be incorporated into:

- repository implementation
- SYSTEM_CONTEXT.md
- any affected documentation

No important engineering decision should remain exclusively inside a conversation.

---

# 9. AI Behaviour Expectations

The AI Engineering Assistant should:

- understand before modifying
- preserve architecture
- minimize maintenance
- avoid unnecessary abstractions
- reason across the entire repository
- document structural changes
- explain architectural risks
- identify technical debt
- protect business methodology

The assistant should never optimize only for shorter code.

Maintainability has higher priority than reducing line count.

Engineering clarity has higher priority than clever implementations.

Long-term ownership always takes precedence over short-term convenience.

---

# 10. Definition of Success

A successful engineering contribution:

- preserves architectural consistency
- preserves business correctness
- improves maintainability
- minimizes future complexity
- introduces no unnecessary coupling
- remains deterministic
- is well documented
- is understandable by another engineer without historical conversations

Every change should leave the repository easier to maintain than before.

---

# PART II — PROJECT OVERVIEW

---

# 11. Project Overview

## 11.1 What is TABELA

TABELA (Theme Analysis, Breadth, Accumulation & Leadership Analytics) is a modular Python-based market intelligence platform designed to identify companies entering the earliest stages of institutional leadership.

The platform integrates:

- ETF relative strength
- Sector and theme leadership
- Stock relative strength
- Fundamental quality
- Historical persistence
- Market breadth
- Institutional accumulation
- Episodic Pivot methodology

to produce a research-oriented view of market leadership.

TABELA is intentionally designed as a research platform rather than a trading platform.

Its purpose is to answer one primary question:

> Which companies are most likely to become future institutional leaders before broad market recognition?

---

# 11.2 Primary Objectives

The objectives of TABELA are:

1. Identify emerging market leaders.

2. Identify institutional accumulation.

3. Detect deteriorating leadership.

4. Track leadership transitions over time.

5. Identify strengthening investment themes.

6. Rank candidates using objective scoring.

7. Produce repeatable daily market intelligence.

8. Preserve historical market state.

9. Generate high-quality watchlists.

10. Minimize subjective interpretation.

---

# 11.3 Research Philosophy

Research should always precede interpretation.

Every conclusion should be supported by objective evidence.

Whenever possible, conclusions should be reproducible from the available data.

Preference should be given to:

- measurable evidence
- persistent behaviour
- multi-factor confirmation

rather than:

- opinions
- narratives
- isolated events

---

# 11.4 System Characteristics

The platform is designed around several permanent characteristics.

## Modular

Independent engines perform specialized responsibilities.

## Deterministic

Identical inputs produce identical outputs.

## Historical

Market state is preserved rather than overwritten.

## Extensible

New capabilities should integrate without disrupting existing architecture.

## Configuration Driven

Business parameters belong in configuration rather than implementation.

## Explainable

Scores and classifications should be understandable and traceable.

---

# 12. Long-Term Vision

The long-term objective is to build a professional-grade market intelligence platform that can continue evolving independently of any individual AI assistant.

Knowledge should live inside:

- the repository
- documentation
- configuration
- historical data

—not inside conversations.

Future AI assistants should be able to understand the complete project by reading the repository and SYSTEM_CONTEXT.md without requiring historical chat context.

---

# 13. Success Criteria

The success of TABELA is measured by:

## Engineering Quality

- maintainable architecture
- modular implementation
- deterministic execution
- low coupling
- clear responsibilities

---

## Business Quality

- accurate theme identification
- meaningful composite scoring
- reliable leadership detection
- robust transition tracking
- objective market intelligence

---

## Operational Quality

- repeatable execution
- historical persistence
- configuration-driven behaviour
- reproducible outputs

---

## Documentation Quality

Documentation should remain synchronized with implementation.

The repository should always be understandable without relying on historical conversations.

---

# 14. Core Functional Domains

The project is organized into several functional domains.

## Market Data

Responsible for:

- ingesting daily market data
- validating input
- normalizing datasets

---

## Theme Intelligence

Responsible for:

- ETF processing
- theme normalization
- theme hierarchy
- theme strength
- sector leadership

---

## Stock Intelligence

Responsible for:

- stock mapping
- relative strength
- composite scoring
- candidate identification
- institutional leadership

---

## Historical Intelligence

Responsible for:

- snapshots
- transition registry
- rotation history
- persistence
- multi-day analysis

---

## Presentation

Responsible for:

- reports
- dashboards
- watchlists
- console output
- CSV
- JSON

Presentation engines should never modify business logic.

---

# 15. Core Business Concepts

The following concepts are fundamental throughout the repository.

---

## Theme

A standardized investment concept representing one or more related industries.

Themes are normalized and may participate in hierarchical relationships.

---

## Relative Strength

Relative price performance used as one component of stock evaluation.

Relative strength is an input into scoring.

It is not a standalone ranking system.

---

## Composite Score

Composite Score represents a weighted evaluation using multiple independent dimensions.

The exact weights are implementation details stored in configuration.

SYSTEM_CONTEXT.md intentionally avoids duplicating numerical values to prevent documentation drift.

---

## Long Candidate

A stock satisfying the platform's long-side evaluation methodology.

Long Candidates are research candidates, not trade recommendations.

---

## Observation

Temporary monitoring state assigned after a leadership candidate weakens.

Observation is an intermediate lifecycle stage.

---

## Distribution

Evidence suggesting deterioration of prior leadership.

Distribution is determined through repeated objective evidence rather than isolated daily weakness.

---

## Recovering Leader

A previously weakening candidate demonstrating renewed institutional strength.

Recovery requires objective confirmation.

---

## Theme Breadth

Measures participation within a theme rather than simply measuring theme performance.

Breadth evaluates leadership quality across constituents.

---

## Institutional Leadership

Institutional Leadership represents sustained characteristics associated with institutional accumulation.

Leadership is expected to develop gradually rather than appear from isolated events.

---

# 16. Core Business Rules

The following business rules should remain stable unless explicitly changed by the user.

## Rule 1

Multiple independent factors should confirm leadership.

No single metric should dominate evaluation.

---

## Rule 2

Historical persistence is more valuable than isolated daily behaviour.

---

## Rule 3

Institutional accumulation should be evaluated through multiple forms of evidence.

---

## Rule 4

Research outputs must remain deterministic.

---

## Rule 5

Business methodology has higher priority than engineering convenience.

---

## Rule 6

Configuration values belong in configuration files.

Business methodology belongs in documentation.

Implementation belongs in source code.

These responsibilities should remain separated.

---

# 17. Non-Goals

The following are intentionally outside the scope of TABELA.

- Price prediction
- Trade recommendation
- Automated execution
- Portfolio optimization
- Position sizing
- Risk management
- Stop-loss generation
- Profit target generation
- Technical indicator libraries
- Chart pattern detection unless explicitly requested
- Elliott Wave analysis
- Broker connectivity

Adding these capabilities requires explicit user direction.

---

# 18. Design Philosophy

Every new feature should answer a question that TABELA cannot currently answer.

New engines should not be introduced simply because functionality can be separated.

A new engine should exist only when it provides a genuinely independent responsibility and improves maintainability.

Whenever functionality can reasonably extend an existing engine without violating the Single Responsibility Principle, extension is preferred over creating another engine.

The long-term objective is not to maximize the number of engines.

The objective is to maximize architectural clarity, maintainability, and business value.


---

# PART III — ENGINEERING PHILOSOPHY

---

# 19. Engineering Philosophy

The engineering philosophy of TABELA is intended to maximize long-term maintainability rather than short-term implementation speed.

Every engineering decision should improve the repository for the next engineer.

The preferred characteristics of the codebase are:

- Simple
- Predictable
- Deterministic
- Modular
- Well documented
- Easy to debug
- Easy to extend
- Easy to review

Engineering elegance is measured by maintainability rather than cleverness.

---

# 20. Core Engineering Principles

The following principles are mandatory throughout the repository.

---

## 20.1 Simplicity First

Complexity is treated as technical debt.

Whenever multiple solutions satisfy the same requirement:

Choose the simplest solution.

Simple code is:

- easier to debug
- easier to review
- easier to extend
- easier for future AI assistants to understand

Avoid unnecessary abstraction.

Avoid engineering for hypothetical future requirements.

---

## 20.2 Deterministic Behaviour

Identical inputs must always produce identical outputs.

Avoid:

- random behaviour
- hidden state
- execution-order dependencies
- non-repeatable calculations

Deterministic behaviour is mandatory for:

- scoring
- rankings
- watchlists
- reports
- historical intelligence

---

## 20.3 Single Responsibility Principle

Every engine should perform one clearly defined responsibility.

Good examples:

- ETF processing
- Theme normalization
- Composite scoring
- Breadth analysis
- Stock transitions
- Presentation

Poor examples:

One engine performing:

- scoring
- persistence
- reporting
- filtering
- watchlist generation

Responsibilities should remain separated.

---

## 20.4 Separation of Concerns

The repository separates responsibilities into distinct layers.

### Configuration

Defines business constants.

---

### Core

Coordinates execution.

---

### Engines

Perform business logic.

---

### Market Data

Stores historical data.

---

### Presentation

Produces outputs.

Presentation must never contain business logic.

---

### Documentation

Explains architecture and methodology.

Documentation must not become implementation.

---

# 21. Architecture Philosophy

Architecture should evolve conservatively.

The objective is stability rather than continual redesign.

Preferred evolution:

Small improvements

↓

Incremental refactoring

↓

Improved maintainability

↓

Reduced complexity

Avoid:

Large architectural rewrites without clear business value.

---

## 21.1 Modular Architecture

Modules should have:

- clear ownership
- limited dependencies
- explicit interfaces

Avoid implicit communication.

---

## 21.2 Low Coupling

Engines should communicate through well-defined data contracts.

An engine should not depend upon another engine's internal implementation.

Dependencies should remain explicit.

---

## 21.3 High Cohesion

Each engine should solve one coherent business problem.

When an engine begins solving unrelated problems, it should be refactored.

---

## 21.4 Linear Pipeline

Execution follows a predictable order.

Configuration

↓

Runtime Context

↓

Input Processing

↓

Business Engines

↓

Aggregation

↓

Presentation

↓

Persistence

↓

Reports

Execution order is part of the architecture.

Changing execution order requires architectural review.

---

# 22. Configuration Philosophy

Configuration belongs in configuration.

Implementation belongs in source code.

Business methodology belongs in documentation.

Do not mix these responsibilities.

---

## Configuration Should Contain

- thresholds
- weights
- limits
- switches
- paths
- feature flags

---

## Configuration Should Not Contain

Business algorithms.

Architecture decisions.

Repository structure.

---

## Documentation Should Not Duplicate Configuration

Avoid copying numerical configuration values into SYSTEM_CONTEXT.md.

Instead reference:

core/config.py

This prevents documentation drift.

---

# 23. Business Logic Philosophy

Business methodology should remain independent from implementation.

Changing code should not change business methodology unless explicitly intended.

Examples:

Changing implementation for performance:

Allowed.

Changing composite score methodology:

Requires explicit business approval.

Changing scanner methodology:

Requires explicit business approval.

Changing transition methodology:

Requires explicit business approval.

---

# 24. Data Ownership Philosophy

Every important dataset should have one owning component.

Examples:

Theme strength

↓

Theme engine.

Transition registry

↓

Transition engine.

Presentation tables

↓

Presentation engine.

Avoid multiple engines modifying the same dataset.

---

# 25. Historical Data Philosophy

Historical information is a strategic asset.

Historical records should be preserved.

Avoid:

Overwriting historical data.

Editing historical snapshots.

Deleting historical intelligence.

Historical persistence enables:

- trend analysis
- transition analysis
- recovery analysis
- distribution analysis
- future research

---

# 26. Error Handling Philosophy

Errors should be classified.

Recoverable errors:

- continue execution
- log warning
- preserve output where practical

Critical errors:

- stop execution
- explain cause
- avoid partial corruption

Never silently ignore structural failures.

---

# 27. Refactoring Philosophy

Refactoring should improve:

- readability
- maintainability
- modularity
- testability

Refactoring should not change business behaviour.

Whenever behaviour changes, treat the work as a feature rather than refactoring.

---

# 28. Code Quality Standards

Every new implementation should satisfy the following questions.

Can another engineer understand this without conversation history?

Can another AI assistant understand this from repository context alone?

Is the behaviour deterministic?

Is ownership obvious?

Is the implementation modular?

Does it introduce unnecessary coupling?

Does it preserve business methodology?

If any answer is "No", reconsider the implementation.

---

# 29. Documentation Philosophy

Documentation is part of the software system.

Every significant engineering decision should eventually exist inside the repository.

Knowledge should migrate from conversations into documentation.

Conversation history is temporary.

Repository documentation is permanent.

---

## 29.1 Documentation Synchronization

Whenever changes affect:

- architecture
- configuration
- execution flow
- schemas
- engine responsibilities
- repository structure

Update:

- SYSTEM_CONTEXT.md
- affected documentation
- change log

The implementation is not considered complete until documentation has been synchronized.

---

# 30. AI Engineering Philosophy

AI assistants should optimize for repository quality rather than response quality.

Good responses produce:

- better architecture
- clearer code
- improved documentation
- lower maintenance cost

Not merely:

- shorter code
- faster implementation
- clever solutions

The repository should become progressively easier to understand after every engineering session.

---

# 31. Decision-Making Framework

Engineering decisions should follow this sequence.

Step 1

Understand the business objective.

↓

Step 2

Understand existing implementation.

↓

Step 3

Determine whether architecture already supports the requirement.

↓

Step 4

Choose the simplest solution.

↓

Step 5

Evaluate long-term maintenance impact.

↓

Step 6

Implement.

↓

Step 7

Validate.

↓

Step 8

Update documentation.

This workflow should be followed consistently regardless of implementation size.

---

# 32. Engineering Success Criteria

An engineering change is considered successful when it:

- preserves business correctness
- improves maintainability
- reduces complexity
- avoids unnecessary coupling
- remains deterministic
- documents architectural changes
- remains understandable without historical conversations

The long-term quality of the repository has higher priority than the convenience of any individual implementation.


---

# PART IV — BUSINESS METHODOLOGY

---

# 33. Business Methodology

TABELA is fundamentally a market intelligence platform.

The platform does **not** attempt to predict price.

The platform attempts to identify the characteristics commonly observed during the early stages of institutional leadership.

The philosophy is based on evidence accumulation rather than prediction.

Every classification should be supported by multiple independent forms of evidence.

---

# 34. Research Philosophy

Research follows a layered methodology.

Market

↓

Theme

↓

Industry

↓

Company

↓

Historical Context

↓

Institutional Behaviour

↓

Candidate Classification

↓

Watchlists

The objective is to progressively reduce uncertainty rather than maximize prediction.

---

# 35. Market Intelligence Philosophy

TABELA attempts to answer questions such as:

- Which themes are strengthening?
- Which industries are weakening?
- Which stocks are becoming institutional leaders?
- Which leaders are deteriorating?
- Which companies are emerging before broad recognition?
- Which transitions are occurring beneath the surface of the market?

The objective is understanding.

Not forecasting.

---

# 36. Multi-Factor Evaluation

No single metric determines candidate quality.

Evaluation combines multiple independent dimensions.

Representative dimensions include:

- Relative Strength
- Theme Leadership
- Fundamental Momentum
- Revenue Growth
- Earnings Growth
- Sales Acceleration
- Profitability
- Institutional Behaviour
- Historical Persistence
- Episodic Pivot Evidence
- Theme Participation
- Breadth
- Market Context

Each contributes evidence.

No individual factor should dominate unless explicitly designed to do so.

---

# 37. Theme Methodology

Themes represent the primary organizational structure for market intelligence.

Every stock should ultimately participate within a normalized investment theme.

Theme normalization exists to eliminate duplicate terminology.

Theme hierarchy exists to consolidate related investment concepts.

Examples include:

Industry

↓

Theme

↓

Parent Theme

↓

Strategic Theme

This hierarchy allows broader market intelligence while preserving detailed classifications.

---

# 38. Theme Strength Philosophy

Theme strength measures the relative quality of an investment theme.

Theme strength is determined through objective evaluation rather than narrative interpretation.

Theme strength should remain:

- repeatable
- explainable
- configuration driven

Theme strength influences stock evaluation.

It does not replace stock evaluation.

---

# 39. Relative Strength Philosophy

Relative Strength is one important input.

It is intentionally **not** treated as the sole determinant of leadership.

High Relative Strength alone does not imply:

- institutional accumulation
- business quality
- future leadership

Relative Strength gains significance when confirmed by additional evidence.

---

# 40. Composite Scoring Philosophy

Composite scoring exists to combine multiple independent dimensions into a single research-oriented evaluation.

The purpose is prioritization.

Not prediction.

The scoring methodology should remain:

- objective
- deterministic
- configuration driven
- explainable

Implementation details belong in the repository.

Business philosophy belongs in this document.

---

# 41. Candidate Classification Philosophy

Every stock ultimately belongs to one research classification.

Examples include:

- Long Candidate
- Observation
- Recovering Leader
- Distribution
- Unknown
- Unclassified Leader

Classification represents current research state.

It does not represent a trading recommendation.

---

# 42. Leadership Philosophy

Institutional leadership develops progressively.

Leadership is expected to emerge through repeated evidence rather than isolated events.

Examples of supporting evidence include:

- sustained Relative Strength
- improving business quality
- strong industry participation
- theme leadership
- historical persistence
- institutional accumulation

Leadership should rarely be determined from one trading session.

---

# 43. Leadership Lifecycle

A typical leadership progression is expected to resemble:

Emerging

↓

Institutional Accumulation

↓

Leadership

↓

Mature Leadership

↓

Weakening Leadership

↓

Observation

↓

Distribution

↓

Recovery (optional)

↓

Leadership

The exact implementation may evolve, but the conceptual lifecycle should remain stable.

---

# 44. Transition Methodology

Transition analysis is one of the distinguishing characteristics of TABELA.

Rather than evaluating only today's strongest stocks, TABELA evaluates:

- improving candidates
- weakening candidates
- recovering candidates
- deteriorating leaders

The objective is identifying change.

Transitions are generally more informative than static rankings.

---

# 45. Registry Philosophy

Persistent registries provide longitudinal intelligence.

Registries should preserve state across executions.

Registry information enables:

- transition analysis
- persistence analysis
- recovery analysis
- leadership evolution
- historical comparisons

Registries are strategic assets.

Avoid resetting registry history without explicit user approval.

---

# 46. Observation Philosophy

Observation represents uncertainty.

A stock in Observation is neither:

confirmed leadership

nor

confirmed deterioration.

Observation exists to collect additional evidence before a stronger classification is assigned.

Observation should never be treated as a failure.

---

# 47. Distribution Philosophy

Distribution represents deterioration of prior leadership.

Distribution should require objective evidence accumulated across multiple observations.

Avoid assigning Distribution based solely on:

- one weak day
- one earnings event
- one Relative Strength decline

Distribution represents a process rather than an event.

---

# 48. Recovery Philosophy

Recovery identifies companies regaining institutional sponsorship.

Recovery is valuable because institutional leadership often develops through multiple accumulation phases.

Recovery should require objective confirmation.

Avoid declaring recovery prematurely.

---

# 49. Unknown Classification Philosophy

Unknown classifications should not be treated as errors.

Instead they represent opportunities for further research.

Unknown candidates may include:

- emerging companies
- newly listed companies
- companies with incomplete mappings
- companies requiring additional classification

Unknown should initiate investigation rather than exclusion.

---

# 50. Scanner Methodology

Finviz scanners provide discovery.

Scanners identify candidates worthy of additional research.

Scanners do **not** determine rankings.

Multiple scanner appearances indicate increased institutional attention but should never directly increase candidate scores.

Each candidate must be evaluated independently after discovery.

---

# 51. Technical Validation Philosophy

Technical analysis exists solely to validate institutional behaviour.

Primary validation may include:

- Moving Averages
- Relative Strength
- Price Structure
- Volume Behaviour
- Institutional Accumulation
- Trend Quality
- Gap Quality

Unless explicitly instructed by the user, TABELA should not expand into broader technical analysis methodologies.

---

# 52. Fundamental Methodology

Business quality remains an essential component of candidate evaluation.

Representative dimensions include:

- Revenue Growth
- EPS Growth
- Revenue Acceleration
- EPS Acceleration
- Margins
- Free Cash Flow
- Earnings Quality
- Guidance
- Analyst Revisions

Business quality should complement technical validation rather than replace it.

---

# 53. Episodic Pivot Methodology

Episodic Pivot (EP) analysis represents one of the highest-priority research methodologies.

Potential EP categories include:

- Growth EP
- Turnaround EP
- Story EP
- Government / Regulatory EP
- Large Order EP
- Delayed Reaction EP

Evaluation may consider:

- earnings surprises
- raised guidance
- analyst upgrades
- contracts
- FDA decisions
- regulatory actions
- partnerships
- revenue acceleration
- EPS acceleration
- institutional sponsorship

A confirmed Episodic Pivot receives independent priority regardless of Future Leader score.

EP status and overall candidate quality should remain independent assessments.

---

# 54. Market Context Philosophy

Individual stocks should never be evaluated completely in isolation.

Market context provides supporting evidence through:

- ETF leadership
- Theme leadership
- Sector rotation
- Market breadth
- Institutional participation

Context strengthens interpretation.

It should not replace company-specific evidence.

---

# 55. Business Methodology Stability

The methodologies defined in this section are considered core business rules.

Changes require explicit user approval.

Implementation improvements are encouraged.

Methodology changes are not.

Engineering convenience must never become the reason for altering business methodology.

Business methodology has higher priority than implementation preference.

---

# PART V — SYSTEM ARCHITECTURE

---

# 56. Architectural Philosophy

The architecture of TABELA exists to maximize:

- maintainability
- deterministic execution
- modularity
- extensibility
- debuggability
- historical continuity

Architecture should evolve conservatively.

The preferred architecture is one that remains understandable after years of incremental development.

The objective is not architectural novelty.

The objective is architectural longevity.

---

# 57. Architectural Principles

Every architectural decision should satisfy the following principles.

## Principle 1

One business responsibility should have one primary owner.

---

## Principle 2

Business logic should not be duplicated.

---

## Principle 3

Data should move forward through the pipeline.

Avoid backward dependencies.

---

## Principle 4

Presentation should never influence business logic.

---

## Principle 5

Configuration should remain external to implementation.

---

## Principle 6

Historical state should be preserved rather than recomputed whenever practical.

---

## Principle 7

Every architectural component should answer a business question.

Components without clear business value should not exist.

---

# 58. Layered Architecture

The repository follows a layered architecture.

```
Presentation Layer

↓

Historical Intelligence

↓

Business Engines

↓

Core Pipeline

↓

Configuration

↓

Input Data
```

Responsibilities should never leak across layers.

---

# 59. Architectural Layers

## 59.1 Input Layer

Responsible for:

- CSV ingestion
- data validation
- runtime discovery
- schema validation

The Input Layer should never perform business analysis.

---

## 59.2 Configuration Layer

Responsible for:

- thresholds
- weights
- feature switches
- runtime options
- file locations

Configuration defines behaviour.

It should never contain implementation.

---

## 59.3 Core Layer

Responsible for:

- orchestration
- execution order
- engine coordination
- runtime context
- dependency management

The Core Layer coordinates.

It should not become a business engine.

---

## 59.4 Business Engine Layer

Responsible for all market intelligence.

Examples include:

- scoring
- breadth
- transitions
- rotation
- institutional leadership
- historical intelligence
- market context
- watchlists

Business logic belongs here.

---

## 59.5 Historical Layer

Responsible for preserving intelligence across executions.

Examples include:

- snapshots
- registries
- transition history
- historical queries
- weekly intelligence

Historical information should remain immutable whenever possible.

---

## 59.6 Presentation Layer

Responsible for:

- console output
- markdown
- JSON
- CSV
- reports
- dashboards

Presentation should consume intelligence.

It should never create intelligence.

---

# 60. Repository Organization

The repository is organized around responsibilities rather than technologies.

Representative areas include:

## core/

Repository coordination.

---

## engines/

Business intelligence.

---

## data/

Reference datasets.

---

## market_data/

Persistent generated artifacts.

---

## docs/

Engineering knowledge.

---

This organization should remain stable.

---

# 61. Pipeline Philosophy

The pipeline is intentionally linear.

Representative execution sequence:

Runtime Context

↓

Input Discovery

↓

ETF Processing

↓

Theme Intelligence

↓

Stock Intelligence

↓

Scoring

↓

Classification

↓

Historical Intelligence

↓

Presentation

↓

Persistence

↓

Reports

The pipeline should remain deterministic.

---

# 62. Pipeline Responsibilities

The pipeline exists to coordinate execution.

It should not become another business engine.

Pipeline responsibilities include:

- execution order
- dependency management
- runtime initialization
- engine invocation
- final aggregation

Avoid embedding business methodology inside the pipeline.

---

# 63. Runtime Context

Runtime Context provides shared execution information.

Representative responsibilities include:

- trading date
- input files
- output locations
- execution environment

Runtime Context should remain lightweight.

Avoid turning Runtime Context into a general data store.

---

# 64. Engine Architecture

Every engine should satisfy the following characteristics.

## Independent

An engine should perform its work without knowledge of unrelated engines.

---

## Predictable

Identical inputs produce identical outputs.

---

## Stateless

Prefer stateless execution.

Persistent state belongs in registries and historical storage.

---

## Reusable

Business logic should be reusable outside the pipeline whenever practical.

---

## Explainable

The responsibility of every engine should be understandable from its name.

---

# 65. Engine Ownership

Each important business concept should have one primary owner.

Examples include:

Theme Strength

↓

Theme engine.

Composite Scores

↓

Scoring engine.

Transition Registry

↓

Transition engine.

Market Breadth

↓

Breadth engine.

Presentation

↓

Presentation engine.

Avoid multiple engines owning the same business concept.

---

# 66. Engine Communication

Engines communicate through structured datasets.

Engines should not:

- inspect internal variables
- depend on hidden implementation
- modify another engine's internal state

Communication should occur through explicit data contracts.

---

# 67. Data Flow Philosophy

Data flows in one direction.

Input

↓

Transformation

↓

Enrichment

↓

Classification

↓

Aggregation

↓

Presentation

↓

Persistence

Avoid circular data movement.

---

# 68. Transformation Philosophy

Each processing stage should increase information value.

Typical transformations include:

Raw Data

↓

Validated Data

↓

Normalized Data

↓

Enriched Data

↓

Scored Data

↓

Classified Data

↓

Historical Intelligence

↓

Presentation Output

Every stage should have a clear purpose.

---

# 69. Historical Intelligence Architecture

Historical intelligence is a first-class architectural component.

Historical systems should answer questions unavailable from a single trading session.

Examples include:

- transition analysis
- persistence analysis
- recovery analysis
- leadership evolution
- trend analysis

Historical engines extend daily intelligence.

They do not replace it.

---

# 70. Registry Architecture

Registries provide persistent operational state.

Representative registry characteristics:

- deterministic
- append-oriented
- historically meaningful
- business driven

Registries should never become general-purpose databases.

Their purpose is preserving longitudinal business intelligence.

---

# 71. Presentation Architecture

Presentation is intentionally separated from analysis.

Presentation responsibilities include:

- formatting
- ordering
- rendering
- exporting

Presentation should never:

- calculate scores
- modify rankings
- change classifications
- alter business logic

---

# 72. Configuration Architecture

Configuration is centralized.

Configuration should define:

- weights
- thresholds
- feature flags
- limits
- runtime options

Configuration should not define:

- business methodology
- architectural philosophy
- implementation logic

Avoid duplicating configuration values throughout the repository.

---

# 73. Architectural Stability

The following architectural characteristics are considered stable.

- Linear pipeline
- Modular engines
- Configuration-driven behaviour
- Registry-based persistence
- Historical intelligence
- Layered architecture
- Presentation separation
- Deterministic execution

Changes to these characteristics require architectural review.

---

# 74. Architectural Evolution Rules

Architecture should evolve through:

small improvements

↓

incremental refactoring

↓

improved maintainability

↓

reduced complexity

Avoid architecture changes driven solely by:

- personal preference
- framework trends
- AI recommendations
- implementation convenience

Architecture changes should produce measurable long-term engineering value.

---

# 75. Architecture Success Criteria

The architecture is considered successful when:

- responsibilities are obvious
- ownership is unambiguous
- execution is deterministic
- extensions are straightforward
- debugging is simple
- business methodology remains protected
- documentation accurately reflects implementation

Architecture should become easier to understand after every major development cycle.


---

# PART VI — REPOSITORY & MODULE ORGANIZATION

---

# 76. Repository Philosophy

The repository is the permanent source of engineering knowledge.

Conversations are temporary.

Engineering knowledge should continuously migrate from conversations into:

- source code
- documentation
- configuration
- repository history

The repository should eventually become self-explanatory.

---

# 77. Repository Organization Principles

The repository is organized around responsibilities rather than technologies.

Each directory should answer one question:

"What responsibility does this directory own?"

Examples:

core/

↓

System coordination

engines/

↓

Business intelligence

market_data/

↓

Historical persistence

data/

↓

Reference datasets

docs/

↓

Engineering knowledge

This organization should remain stable over time.

---

# 78. Repository Ownership

Every major responsibility should have one clear owner.

Representative ownership:

Configuration

↓

core/config.py

Execution Pipeline

↓

core/pipeline.py

Business Intelligence

↓

engines/

Historical Persistence

↓

market_data/

Reference Data

↓

data/

Documentation

↓

docs/

Avoid duplicate ownership.

---

# 79. Root Directory Philosophy

The repository root should remain intentionally small.

Only place files in the root when they satisfy one of the following:

- application entry point
- repository configuration
- project metadata
- licensing
- developer tooling

Business logic should never accumulate in the repository root.

---

# 80. Core Module Philosophy

The core package defines the framework that coordinates the platform.

Representative responsibilities include:

- pipeline orchestration
- runtime coordination
- configuration
- mapping
- normalization
- execution flow

The core package should not become a business intelligence layer.

Business calculations belong in engines.

---

# 81. Engine Package Philosophy

The engines package represents the heart of TABELA.

Each engine should perform one independent business responsibility.

Representative responsibilities include:

- ETF processing
- scoring
- breadth
- market context
- rotation
- transitions
- historical intelligence
- presentation
- watchlists

Every engine should have:

- obvious ownership
- explicit inputs
- explicit outputs
- deterministic behaviour

---

# 82. Engine Design Standards

Every engine should satisfy the following standards.

## One Primary Responsibility

One engine.

One business purpose.

---

## Explicit Inputs

Inputs should be clearly defined.

Avoid implicit dependencies.

---

## Explicit Outputs

Every downstream consumer should understand what the engine produces.

---

## Configuration Driven

Business thresholds belong in configuration.

Avoid hardcoded business constants.

---

## Independent Testing

Whenever practical, engines should be executable independently of the complete pipeline.

---

## Explainable Behaviour

Another engineer should understand the purpose of the engine from:

- filename
- function names
- documentation

---

# 83. Engine Interaction Rules

Preferred interaction:

Engine A

↓

Structured Dataset

↓

Engine B

Avoid:

Engine A

↓

Reads Engine B internals

↓

Modifies Engine C state

↓

Depends on hidden variables

Communication should occur through explicit contracts.

---

# 84. Module Responsibilities

Modules should own concepts.

Functions should own operations.

Avoid modules becoming collections of unrelated utilities.

When a module begins accumulating unrelated responsibilities, refactor it.

---

# 85. Configuration Module

Configuration exists to separate implementation from policy.

Configuration defines:

- thresholds
- weights
- limits
- runtime switches
- feature flags
- file locations

Configuration should remain declarative.

Avoid embedding business algorithms inside configuration.

---

# 86. Mapping Philosophy

Mapping represents one of the foundational capabilities of TABELA.

Representative mappings include:

- company → theme
- industry → theme
- normalized theme
- parent theme

Mappings should remain:

- deterministic
- centralized
- reusable

Avoid duplicating mapping logic across engines.

---

# 87. Theme Hierarchy Philosophy

Theme hierarchy provides abstraction.

Lower-level themes should roll into broader strategic themes without losing detail.

Hierarchy enables:

- sector intelligence

- strategic reporting

- breadth aggregation

- leadership analysis

Hierarchy should remain centralized.

---

# 88. Historical Storage Philosophy

Historical storage preserves market evolution.

Representative stored artifacts include:

- daily snapshots

- rotation history

- watchlist history

- transition registry

- market context

Historical files should be treated as immutable records whenever practical.

Avoid rewriting history.

---

# 89. Market Data Philosophy

Market data represents factual observations.

Market data should never contain derived business intelligence.

Derived intelligence belongs inside generated datasets.

Separate:

Raw observations

from

Business interpretation.

---

# 90. Generated Data Philosophy

Generated datasets should be reproducible.

Given:

same inputs

same configuration

same repository version

the generated outputs should match.

Generated artifacts should not require manual editing.

---

# 91. Documentation Package

Documentation should explain:

- architecture
- business methodology
- engineering philosophy
- repository organization
- operational workflow

Documentation should not duplicate implementation details unnecessarily.

Whenever implementation changes invalidate documentation,

documentation should be updated immediately.

---

# 92. File Naming Standards

Representative naming principles:

- descriptive
- consistent
- business-oriented
- predictable

Avoid ambiguous names.

Examples of preferred naming:

market_context_engine.py

stock_transition_engine.py

presentation_engine.py

Names should communicate ownership.

---

# 93. Source Code Standards

Representative expectations:

- descriptive function names

- descriptive variables

- low nesting

- modular functions

- explicit return values

- minimal side effects

Code should optimize readability over brevity.

---

# 94. Dependency Philosophy

Dependencies should flow downward.

Example:

Configuration

↓

Pipeline

↓

Business Engines

↓

Presentation

Avoid reverse dependencies.

Avoid circular imports.

Avoid hidden runtime coupling.

---

# 95. Extension Philosophy

New functionality should first attempt to answer:

Can an existing engine own this responsibility?

If yes:

Extend existing engine.

If no:

Introduce a new engine.

Creating new engines should be a deliberate architectural decision.

---

# 96. Repository Stability

The following repository characteristics should remain stable.

- Modular organization

- Core orchestration

- Engine separation

- Historical persistence

- Configuration centralization

- Documentation-first governance

- Deterministic execution

These characteristics define the architectural identity of TABELA.

Changes require architectural justification.

---

# 97. Repository Quality Objectives

The repository should become progressively:

- easier to understand

- easier to maintain

- easier to extend

- easier to review

- easier for AI assistants to reason about

Every engineering contribution should improve at least one of these dimensions while preserving business correctness.


---

# PART VII — ENGINE SPECIFICATIONS

---

# 98. Engine Philosophy

Business intelligence within TABELA is implemented through specialized engines.

An engine represents the smallest independently maintainable business component.

Each engine should answer one business question.

If an engine begins answering multiple unrelated questions, it should be refactored.

---

# 99. Definition of an Engine

An engine is a deterministic processing unit that:

- receives structured input
- performs one business responsibility
- produces structured output
- does not own presentation
- does not own orchestration
- does not own unrelated business logic

An engine should be understandable in isolation.

---

# 100. Engine Responsibilities

Every engine should clearly define:

## Business Purpose

Why the engine exists.

---

## Inputs

What information it consumes.

---

## Outputs

What information it produces.

---

## Dependencies

Which upstream data it requires.

---

## Ownership

Which business concepts belong exclusively to this engine.

---

## Configuration

Which configuration settings influence behaviour.

---

# 101. Engine Lifecycle

Every engine follows the same lifecycle.

Input

↓

Validation

↓

Transformation

↓

Business Logic

↓

Classification

↓

Output

↓

Validation

↓

Return

Avoid hidden intermediate state.

---

# 102. Engine Categories

TABELA engines naturally fall into several categories.

---

## Data Processing Engines

Responsible for:

- validation
- normalization
- transformation
- enrichment

---

## Intelligence Engines

Responsible for:

- scoring
- classification
- breadth
- market context
- transitions
- historical intelligence

---

## Persistence Engines

Responsible for:

- snapshots
- registries
- historical storage
- dataset generation

---

## Presentation Engines

Responsible for:

- formatting
- reports
- dashboards
- exports

Presentation engines should remain consumers.

Never producers of business intelligence.

---

# 103. ETF Intelligence

ETF processing provides macro context for downstream analysis.

Representative responsibilities include:

- ETF normalization

- theme strength

- benchmark comparison

- sector leadership

- strategic ranking

ETF intelligence influences stock evaluation.

It should not directly determine stock classifications.

---

# 104. Theme Intelligence

Theme Intelligence is responsible for:

- normalization

- translation

- hierarchy

- classification

- aggregation

Theme intelligence should remain centralized.

Avoid implementing theme logic independently inside stock engines.

---

# 105. Stock Intelligence

Stock intelligence transforms normalized company data into research intelligence.

Representative responsibilities include:

- mapping

- Relative Strength

- composite scoring

- candidate identification

- leadership evaluation

- classification

Stock intelligence is one of the primary business layers of TABELA.

---

# 106. Scoring Engines

Scoring engines convert multiple independent business dimensions into standardized research scores.

Representative scoring dimensions include:

- Relative Strength

- Theme Strength

- Sales

- Margins

- Fundamental Quality

- Composite Score

The methodology should remain:

- deterministic

- configuration driven

- explainable

Implementation may evolve.

Methodology should remain stable.

---

# 107. Breadth Intelligence

Breadth measures participation.

Strong themes require:

- participation

not merely

- isolated leaders.

Breadth provides context that complements theme strength.

---

# 108. Rotation Intelligence

Rotation identifies movement of institutional capital.

Representative observations include:

- strengthening themes

- weakening themes

- improving sectors

- deteriorating sectors

Rotation represents change.

Not absolute strength.

---

# 109. Institutional Leadership Engine

Institutional Leadership attempts to identify sustained institutional sponsorship.

Evaluation should emphasize:

- persistence

- confirmation

- multiple evidence sources

Avoid assigning leadership based solely on:

- one breakout

- one earnings report

- one Relative Strength improvement

---

# 110. Transition Engine

The Transition Engine tracks changes in institutional state.

Representative states include:

- Leadership

- Observation

- Recovery

- Distribution

Transitions provide longitudinal intelligence unavailable from daily snapshots.

---

# 111. Historical Intelligence Engine

Historical Intelligence extends daily observations into longer-term understanding.

Representative analyses include:

- persistence

- recovery

- deterioration

- transition history

- historical comparisons

Historical intelligence should complement daily intelligence.

---

# 112. Market Context Engine

Market Context provides environmental intelligence.

Representative inputs include:

- ETFs

- major indexes

- market structure

- institutional activity

Market Context influences interpretation.

It should not replace company-specific evaluation.

---

# 113. Watchlist Engine

Watchlists represent curated research outputs.

Watchlists should remain:

- deterministic

- explainable

- reproducible

Watchlists are outputs of research.

They are not trading signals.

---

# 114. Presentation Engine

Presentation is responsible for communicating intelligence.

Presentation responsibilities include:

- formatting

- ordering

- rendering

- exporting

Presentation must never:

- calculate scores

- change rankings

- modify classifications

- implement business rules

---

# 115. Weekly Intelligence

Weekly intelligence aggregates multiple daily observations into higher-level research.

Weekly processing should answer questions that cannot be answered from a single trading session.

Examples include:

- persistence

- recurring leadership

- repeated transitions

- sustained deterioration

---

# 116. Engine Communication Standards

Every engine should communicate using structured datasets.

Preferred interaction:

Engine

↓

Validated Dataset

↓

Next Engine

Avoid:

Engine

↓

Internal Engine Variables

↓

Hidden State

↓

Implicit Behaviour

Communication should remain explicit.

---

# 117. Engine Dependency Rules

Dependencies should always move downstream.

Preferred:

Configuration

↓

Normalization

↓

Scoring

↓

Classification

↓

Presentation

Avoid:

Presentation

↓

Scoring

↓

Configuration

Avoid reverse dependencies.

---

# 118. Engine State

Business engines should preferably remain stateless.

Persistent state belongs in:

- registries

- snapshots

- historical datasets

Stateless engines are easier to:

- debug

- test

- extend

---

# 119. Engine Error Handling

Engines should validate inputs before processing.

Recoverable situations:

- empty datasets

- optional files

- missing optional values

Critical situations:

- invalid schemas

- corrupted data

- missing required fields

Critical failures should fail clearly.

---

# 120. Engine Extension Rules

Before creating a new engine ask:

Does an existing engine already own this responsibility?

If yes:

Extend existing engine.

If no:

Create a specialized engine.

A new engine should answer a business question that cannot currently be answered.

---

# 121. Engine Success Criteria

An engine is considered well designed when:

- responsibility is obvious

- ownership is unambiguous

- inputs are explicit

- outputs are explicit

- dependencies are minimal

- behaviour is deterministic

- configuration is externalized

- documentation explains its purpose

Every engine should remain independently understandable without requiring knowledge of unrelated engines.


---

# PART VIII — CONFIGURATION & DATA ARCHITECTURE

---

# 122. Configuration Philosophy

Configuration exists to separate business policy from implementation.

Configuration defines **how** the system behaves.

Implementation defines **how** the behaviour is executed.

Business methodology defines **why** the behaviour exists.

These three concerns should remain independent.

---

# 123. Configuration Objectives

Configuration should make the system:

- deterministic
- maintainable
- adjustable
- transparent
- centralized

Configuration should reduce code modifications required for business tuning.

---

# 124. Configuration Ownership

The primary owner of runtime configuration is:

```
core/config.py
```

This file should remain the single authoritative location for:

- thresholds
- weights
- limits
- feature switches
- runtime behaviour
- file locations
- persistence settings

Avoid duplicating configuration values elsewhere.

---

# 125. Configuration Categories

Configuration should naturally group into the following categories.

---

## Scoring Configuration

Defines:

- scoring weights
- normalization
- ranking thresholds

---

## Candidate Configuration

Defines:

- candidate filters
- minimum requirements
- qualification thresholds

---

## Theme Configuration

Defines:

- benchmark ETF
- weighting methodology
- normalization options

---

## Distribution Configuration

Defines:

- persistence windows
- deterioration thresholds
- leadership confirmation
- historical lookback periods

---

## Transition Configuration

Defines:

- observation duration
- registry behaviour
- lifecycle rules

---

## Market Context Configuration

Defines:

- benchmark indexes
- market structure
- institutional activity parameters

---

## Runtime Configuration

Defines:

- directories
- filenames
- execution environment
- output locations

---

# 126. Configuration Design Rules

Configuration should satisfy the following rules.

---

## Centralized

Business constants should exist in one location.

---

## Human Readable

Configuration should be understandable without reading implementation.

---

## Version Controlled

Configuration changes should be committed with source code.

---

## Documented

Significant configuration changes should update:

- SYSTEM_CONTEXT.md

- Appendix C

---

## Stable

Configuration names should change infrequently.

---

# 127. Configuration Change Policy

Changing configuration is considered a business change.

Whenever configuration changes:

- validate downstream effects

- update documentation

- update change log

- explain business rationale

Configuration changes should never be hidden inside unrelated commits.

---

# 128. Data Philosophy

Data is divided into four categories.

---

## Raw Data

Direct external observations.

Examples:

- ETF data

- stock data

- market data

---

## Reference Data

Static lookup information.

Examples:

- theme mappings

- hierarchy

- translation tables

---

## Generated Intelligence

Business outputs.

Examples:

- scores

- classifications

- watchlists

- rankings

---

## Historical Intelligence

Persistent longitudinal information.

Examples:

- snapshots

- registries

- historical datasets

---

# 129. Data Lifecycle

Representative lifecycle:

Raw Input

↓

Validation

↓

Normalization

↓

Enrichment

↓

Scoring

↓

Classification

↓

Historical Persistence

↓

Presentation

Each stage should increase information value.

---

# 130. Data Validation Philosophy

All externally supplied data should be validated before business processing.

Validation includes:

- required fields

- data types

- missing values

- duplicate records

- schema consistency

Business engines should assume validated inputs.

---

# 131. Data Ownership

Every important dataset should have one owner.

Examples include:

Theme Strength

↓

Theme processing.

Composite Scores

↓

Scoring.

Transition Registry

↓

Transition engine.

Watchlists

↓

Watchlist engine.

Presentation Tables

↓

Presentation engine.

Ownership should remain explicit.

---

# 132. Data Contracts

Every engine communicates using explicit data contracts.

Contracts should define:

- required fields

- optional fields

- expected data types

- ownership

- downstream consumers

Avoid undocumented implicit fields.

---

# 133. Input Data

Representative external inputs include:

- ETF datasets

- Stock datasets

- Market index datasets

- Reference mapping tables

Input datasets should remain factual.

Business interpretation occurs after ingestion.

---

# 134. Reference Data

Reference data should remain relatively stable.

Examples include:

- company mappings

- industry mappings

- theme mappings

- hierarchy definitions

Reference data should never contain calculated intelligence.

---

# 135. Generated Intelligence

Generated intelligence includes:

- Relative Strength

- Theme Strength

- Composite Scores

- Leadership classifications

- Breadth

- Rotation

- Watchlists

Generated intelligence should always be reproducible.

---

# 136. Historical Persistence

Historical persistence exists to preserve market evolution.

Historical records should answer questions impossible to answer from one trading session.

Representative examples include:

- leadership persistence

- transition history

- recovery

- deterioration

Historical data should generally be append-oriented.

---

# 137. Registry Architecture

Registries preserve operational state.

Registry responsibilities include:

- state persistence

- lifecycle tracking

- transition monitoring

Registries should remain lightweight.

Avoid using registries as general-purpose databases.

---

# 138. JSON Philosophy

JSON files represent structured generated intelligence.

JSON outputs should satisfy:

- deterministic ordering

- stable schema

- backwards compatibility where practical

JSON should remain machine-friendly.

---

# 139. CSV Philosophy

CSV outputs primarily support:

- interoperability

- manual inspection

- spreadsheet analysis

CSV exports should remain simple.

Avoid embedding nested structures.

---

# 140. Output Philosophy

Every generated output should answer a business question.

Examples include:

"What themes are leading?"

"What stocks are emerging?"

"What leaders are deteriorating?"

"What changed since yesterday?"

Outputs should emphasize business value rather than implementation detail.

---

# 141. Data Stability Rules

The following are considered stable concepts.

- Theme hierarchy

- Composite scoring architecture

- Registry philosophy

- Historical persistence

- Data lifecycle

- Engine communication contracts

Implementation may evolve.

These concepts should remain stable.

---

# 142. Configuration Success Criteria

The configuration architecture is considered successful when:

- all business constants are centralized

- configuration names are understandable

- implementation contains minimal hardcoded values

- configuration changes require no architectural changes

- documentation remains synchronized

Configuration should simplify business evolution without increasing engineering complexity.

---

# PART IX — DEVELOPMENT WORKFLOW & AI ENGINEERING WORKFLOW

---

# 143. Development Philosophy

Development within TABELA follows an engineering-first methodology.

The objective is not rapid implementation.

The objective is sustainable evolution.

Every development session should leave the repository:

- more understandable
- better documented
- easier to maintain
- easier to extend
- more deterministic

Engineering quality has higher priority than implementation speed.

---

# 144. Standard Development Lifecycle

Every feature should follow the same lifecycle.

Business Requirement

↓

Research

↓

Architecture Review

↓

Design

↓

Implementation

↓

Validation

↓

Documentation

↓

Git Commit

↓

Repository Synchronization

↓

Knowledge Base Update

Skipping stages should be avoided.

---

# 145. Engineering Decision Process

Before implementing any change, evaluate:

## Step 1

Understand the business objective.

---

## Step 2

Identify the current implementation.

---

## Step 3

Determine ownership.

Which engine should own this responsibility?

---

## Step 4

Determine whether architecture already supports the change.

---

## Step 5

Identify the smallest maintainable implementation.

---

## Step 6

Evaluate downstream impact.

---

## Step 7

Implement.

---

## Step 8

Validate.

---

## Step 9

Synchronize documentation.

---

# 146. Code Change Categories

All changes should fall into one of the following categories.

---

## Bug Fix

Corrects incorrect behaviour.

Business methodology remains unchanged.

---

## Enhancement

Adds functionality while preserving architecture.

---

## Refactoring

Improves implementation without changing behaviour.

---

## Architecture Change

Changes repository structure or execution flow.

Requires architectural review.

---

## Business Methodology Change

Changes business rules.

Requires explicit user approval.

---

# 147. Change Impact Assessment

Before implementing any modification determine whether it affects:

- business methodology
- architecture
- execution order
- configuration
- persistence
- outputs
- data contracts
- historical intelligence

If yes:

Document the impact.

---

# 148. OpenCode Engineering Workflow

Development is performed using OpenCode inside VS Code.

OpenCode serves as the orchestration layer for multiple specialized AI models.

The objective is to use the best model for each engineering task rather than relying on a single general-purpose model.

---

# 149. OpenRouter Model Routing

Model selection is intentional.

Each model has clearly defined responsibilities.

Avoid assigning work outside its specialization.

---

## architect_sonnet

Primary responsibilities:

- architecture
- system design
- pipeline analysis
- dependency analysis
- multi-engine refactoring
- repository organization
- design review
- engineering trade-off analysis

Do not use for:

small formatting fixes.

---

## architect_kimi

Primary responsibilities:

- alternative architectural analysis
- repository reasoning
- structural optimization
- engineering brainstorming
- large-scale planning
- architecture validation

Often used as a second architectural opinion.

---

## coder_glm

Primary responsibilities:

- implementing specialized engines
- business logic
- scoring algorithms
- data transformation
- feature implementation
- pipeline-compatible code

Focus:

Business implementation.

---

## coder_qwen

Primary responsibilities:

- feature development
- engine implementation
- repository enhancements
- refactoring
- structured Python development

Focus:

Reliable implementation.

---

## patcher_flash

Reserved exclusively for:

- formatting fixes
- localized patches
- docstrings
- comments
- small bug fixes
- syntax corrections

Never assign:

- architecture
- large refactoring
- business methodology
- multi-engine work

to patcher_flash.

---

# 150. Model Collaboration Strategy

Large engineering work should follow a structured workflow.

Example:

Architecture

↓

architect_sonnet

↓

Architecture Review

↓

architect_kimi

↓

Implementation

↓

coder_glm or coder_qwen

↓

Small Corrections

↓

patcher_flash

This workflow minimizes architectural mistakes.

---

# 151. AI Assistant Responsibilities

An AI assistant is expected to:

understand

before

implementing.

Representative responsibilities include:

- repository comprehension
- architecture preservation
- debugging
- implementation
- documentation
- validation
- technical review

Avoid acting as a code generator without understanding the system.

---

# 152. AI Assistant Limitations

The AI assistant should never:

invent business methodology

guess missing architecture

fabricate implementation details

silently change business rules

silently redesign architecture

When evidence is unavailable, explicitly state:

> Not recoverable from repository.

---

# 153. Validation Workflow

Every implementation should be validated.

Validation includes:

Repository integrity

↓

Compilation

↓

Execution

↓

Output verification

↓

Business verification

↓

Documentation synchronization

Validation is mandatory before considering work complete.

---

# 154. Git Workflow

Representative workflow:

Implement

↓

Validate

↓

Update Documentation

↓

Commit

↓

Push

↓

Synchronize

Commits should remain logically grouped.

Avoid unrelated changes within the same commit.

---

# 155. Documentation Workflow

Documentation updates are part of implementation.

Representative workflow:

Implementation

↓

Architecture review

↓

SYSTEM_CONTEXT.md update

↓

Related document updates

↓

Appendix C update

↓

Commit

Documentation should never become an afterthought.

---

# 156. Knowledge Migration Philosophy

Knowledge should progressively migrate from conversations into the repository.

Permanent knowledge belongs in:

- source code
- documentation
- configuration
- repository history

Conversation history should never become the primary knowledge source.

---

# 157. Review Workflow

Major work should be reviewed at multiple levels.

Representative review sequence:

Business correctness

↓

Architecture

↓

Implementation

↓

Outputs

↓

Documentation

↓

Maintainability

Each review asks a different question.

---

# 158. Definition of Complete

A task is complete only when:

✓ implementation is finished

✓ outputs are validated

✓ documentation updated

✓ architecture preserved

✓ business methodology preserved

✓ repository synchronized

Code completion alone does not constitute completion.

---

# 159. Development Success Criteria

The development workflow is considered successful when:

- implementation remains deterministic

- repository quality improves

- documentation stays synchronized

- architecture remains coherent

- business methodology is preserved

- future engineers require less historical context than before

Every development session should reduce future engineering uncertainty rather than increase it.

---

# PART X — AI COLLABORATION, GOVERNANCE & DOCUMENTATION

---

# 160. AI Collaboration Philosophy

TABELA is intended to be maintainable by multiple AI engineering assistants over many years.

The repository should never become dependent upon one particular AI model.

Instead, knowledge should reside inside:

- source code
- documentation
- configuration
- repository history

Every AI assistant should be able to continue development using only the repository.

---

# 161. AI Operating Principles

Every AI engineering assistant should:

Understand before implementing.

Preserve before redesigning.

Extend before replacing.

Document before finishing.

Repository quality is more important than response quality.

---

# 162. AI Objectives

The primary objective of the AI assistant is to improve the repository.

Success is measured by:

- improved maintainability

- architectural consistency

- preserved business methodology

- lower technical debt

- better documentation

The objective is not maximizing code generation.

---

# 163. Repository First Philosophy

The repository represents the permanent memory of the project.

Conversation history is temporary.

Whenever important knowledge appears inside a conversation, it should eventually migrate into:

- source code

- documentation

- configuration

- repository history

No critical engineering knowledge should remain conversation-only.

---

# 164. Understanding Before Implementation

Before making any modification an AI assistant should understand:

- repository architecture

- business objective

- engine ownership

- execution flow

- configuration impact

- downstream effects

Implementation without understanding is discouraged.

---

# 165. Business Rule Protection

Business methodology has the highest protection level.

Never silently change:

- scanner methodology

- scoring methodology

- candidate qualification

- transition logic

- Episodic Pivot methodology

- registry philosophy

- historical persistence

Business methodology changes require explicit user approval.

---

# 166. Architecture Protection

Architecture should evolve conservatively.

Avoid changing:

- pipeline execution

- layer responsibilities

- ownership boundaries

- repository organization

without architectural justification.

Architecture changes should improve long-term maintainability.

---

# 167. Documentation Synchronization

Documentation is considered part of implementation.

Whenever changes affect:

- architecture

- configuration

- execution flow

- schemas

- business methodology

- repository organization

the following are mandatory:

Update:

- SYSTEM_CONTEXT.md

- affected documentation

- Appendix C (Change Log)

Implementation is incomplete until documentation is synchronized.

---

# 168. SYSTEM_CONTEXT.md Governance

SYSTEM_CONTEXT.md is the permanent operating specification for the project.

It should contain:

- engineering philosophy

- business methodology

- architecture

- governance

- development workflow

- repository organization

It should not duplicate:

- implementation details

- configuration values

- temporary experiments

Those belong elsewhere.

---

# 169. Configuration Governance

Configuration belongs in:

core/config.py

SYSTEM_CONTEXT.md should describe:

configuration philosophy

not

configuration values.

Avoid documentation drift caused by duplicated constants.

---

# 170. Dynamic Session Context

During active engineering sessions the user may provide:

- code snippets

- configuration updates

- schema modifications

- architectural corrections

- repository restructuring

These become the temporary operational source of truth.

Before concluding implementation they should migrate into:

- repository

- documentation

- SYSTEM_CONTEXT.md

---

# 171. Documentation Hierarchy

Documentation should follow the same hierarchy as engineering decisions.

Level 1

SYSTEM_CONTEXT.md

↓

Level 2

Architecture Documentation

↓

Level 3

Module Documentation

↓

Level 4

Code Comments

Avoid storing architectural knowledge only in comments.

---

# 172. Engineering Decision Hierarchy

Every engineering decision should follow:

Explicit User Instruction

↓

Repository Implementation

↓

SYSTEM_CONTEXT.md

↓

Supporting Documentation

↓

Historical Discussions

↓

Engineering Judgement

Never bypass a higher-priority source.

---

# 173. Handling Missing Information

If required information cannot be verified:

State:

> Not recoverable from repository.

Do not:

- invent behaviour

- assume methodology

- fabricate architecture

Continue analysis using verified information only.

---

# 174. Conflict Resolution

If conflicts exist between:

repository

documentation

conversation

configuration

the AI assistant should:

Step 1

Identify conflict.

↓

Step 2

Determine authoritative source.

↓

Step 3

Explain impact.

↓

Step 4

Recommend resolution.

Never silently ignore inconsistencies.

---

# 175. Documentation Quality Standards

Documentation should be:

- technically accurate

- concise

- architecture focused

- implementation independent

- version controlled

- easy for AI assistants to retrieve

Avoid:

duplicated content

contradictory guidance

hardcoded configuration values

implementation-specific explanations.

---

# 176. Repository Knowledge Base

The long-term repository knowledge base consists of:

Source Code

+

SYSTEM_CONTEXT.md

+

Architecture Documents

+

Configuration

+

Historical Data

No single component is sufficient.

Together they represent the permanent engineering memory of TABELA.

---

# 177. AI Review Checklist

Before completing any task the AI assistant should verify:

✓ Business methodology preserved

✓ Architecture preserved

✓ Repository organization maintained

✓ Configuration centralized

✓ Documentation updated

✓ No unnecessary coupling introduced

✓ Outputs remain deterministic

✓ Historical behaviour preserved

---

# 178. Engineering Anti-Patterns

Avoid introducing:

- duplicated business logic

- duplicated configuration

- hidden dependencies

- circular imports

- presentation logic inside business engines

- business logic inside pipeline orchestration

- undocumented architectural changes

- undocumented configuration changes

These increase long-term maintenance cost.

---

# 179. Long-Term Governance

The long-term objective is to ensure that TABELA remains:

- AI independent

- maintainable

- deterministic

- modular

- well documented

- architecturally consistent

Future AI assistants should require progressively less conversational context because the repository itself continuously improves.

---

# 180. Definition of Engineering Excellence

Engineering excellence within TABELA is achieved when:

The repository explains itself.

Business methodology is preserved.

Architecture remains coherent.

Documentation remains synchronized.

Configuration remains centralized.

Historical intelligence remains intact.

Future development becomes progressively easier rather than progressively more complex.


---

# PART XI — MAINTENANCE, EVOLUTION & LONG-TERM GOVERNANCE

---

# 181. Long-Term Maintenance Philosophy

TABELA is expected to evolve over many years.

The architecture should support continuous incremental improvement without requiring periodic redesign.

Long-term maintainability has higher priority than short-term implementation speed.

Every engineering decision should reduce future maintenance effort.

---

# 182. Repository Evolution

Repository evolution should be intentional.

Preferred evolution:

Business Requirement

↓

Engineering Analysis

↓

Architectural Review

↓

Implementation

↓

Validation

↓

Documentation

↓

Knowledge Preservation

Avoid uncontrolled architectural drift.

---

# 183. Incremental Evolution

The preferred development model is continuous incremental improvement.

Small improvements accumulated over time are preferred over large disruptive rewrites.

Incremental improvements should preserve:

- architecture

- business methodology

- execution flow

- repository organization

---

# 184. Refactoring Governance

Refactoring exists to improve implementation.

Refactoring should improve:

- readability

- maintainability

- modularity

- testability

Refactoring should not alter business methodology.

If business behaviour changes, the work should be classified as a feature rather than refactoring.

---

# 185. Technical Debt Philosophy

Technical debt should be consciously managed.

Not all technical debt requires immediate resolution.

Prioritize debt that:

- increases maintenance cost

- creates architectural inconsistency

- duplicates business logic

- reduces determinism

- complicates debugging

Avoid refactoring solely for stylistic preference.

---

# 186. Engineering Debt Categories

Technical debt should be classified.

Representative categories:

Architecture Debt

Configuration Debt

Documentation Debt

Implementation Debt

Performance Debt

Testing Debt

Dependency Debt

Operational Debt

Different categories require different remediation strategies.

---

# 187. Risk Management Philosophy

Engineering risk should be minimized through architecture rather than reactive fixes.

Representative risk areas include:

- duplicated business logic

- hidden dependencies

- undocumented behaviour

- configuration drift

- documentation drift

- circular dependencies

- historical data corruption

Every major implementation should consider downstream risks.

---

# 188. Stability Classification

Repository components naturally fall into three stability categories.

---

## Stable

Core architectural concepts expected to change infrequently.

Examples include:

- pipeline philosophy

- layered architecture

- engine separation

- configuration philosophy

---

## Active Development

Business intelligence continually refined through research.

Examples include:

- scoring

- historical intelligence

- transition analysis

- market context

---

## Experimental

Research features under evaluation.

Experimental features should remain isolated until validated.

---

# 189. Backward Compatibility

Backward compatibility should be preserved whenever practical.

Breaking changes require:

- engineering justification

- documentation updates

- migration guidance

Avoid breaking downstream workflows unnecessarily.

---

# 190. Extension Philosophy

Every new capability should answer a business question that TABELA cannot currently answer.

Avoid creating new engines solely to:

- increase modularity

- satisfy architectural preferences

- separate trivial functionality

Extension should increase business value.

---

# 191. Engine Creation Criteria

Before introducing a new engine verify:

Does an existing engine already own this responsibility?

Would extending an existing engine violate Single Responsibility?

Does the new engine answer a genuinely independent business question?

Will the new engine improve long-term maintainability?

If the answer to these questions is "No", prefer extending the existing engine.

---

# 192. Feature Acceptance Criteria

A feature should satisfy all of the following.

Business value.

Architectural consistency.

Deterministic behaviour.

Maintainability.

Documentation.

Configuration compatibility.

Minimal coupling.

If one or more criteria are not satisfied, reconsider the implementation.

---

# 193. Performance Philosophy

Performance optimization should follow correctness.

Priority order:

Correctness

↓

Business methodology

↓

Maintainability

↓

Performance

Avoid sacrificing clarity for marginal performance improvements.

---

# 194. Testing Philosophy

Testing should verify:

Business correctness.

Architectural consistency.

Historical compatibility.

Deterministic outputs.

Regression prevention.

Testing should focus on behaviour rather than implementation details.

---

# 195. Regression Prevention

Every significant change should consider:

Could this affect scoring?

Could this affect transitions?

Could this affect watchlists?

Could this affect historical intelligence?

Could this affect presentation?

Potential regressions should be identified before implementation.

---

# 196. Historical Compatibility

Historical datasets represent accumulated market intelligence.

Historical compatibility should be preserved whenever practical.

Avoid introducing changes that invalidate historical analysis without explicit user approval.

---

# 197. Migration Philosophy

TABELA should remain portable across:

AI assistants

Development environments

Operating systems

Repository hosts

Knowledge should remain repository-centric rather than AI-centric.

---

# 198. Repository Independence

The repository should never depend upon:

one AI model

one development environment

one IDE

one operating system

one engineer

The repository should remain self-sufficient.

---

# 199. Future AI Assistants

Future AI assistants should be able to:

Understand repository organization.

Understand architecture.

Understand business methodology.

Continue development.

Review previous work.

Maintain documentation.

without access to historical conversations.

This document exists primarily to enable that capability.

---

# 200. Definition of Repository Maturity

A mature repository exhibits the following characteristics.

Architecture explains itself.

Responsibilities are obvious.

Business methodology is documented.

Configuration is centralized.

Historical intelligence is preserved.

Documentation remains synchronized.

Future development requires minimal onboarding.

The long-term objective of TABELA is to reach this state and maintain it indefinitely.

---

# END OF CORE SPECIFICATION

The remaining appendices provide reference material.

They are informative rather than normative.

The sections above define the operational rules governing TABELA.


---

# APPENDIX A — COMPLETE REPOSITORY DIRECTORY REFERENCE

> **Purpose**
>
> This appendix documents the intended responsibilities of repository directories.
>
> It intentionally documents **ownership**, not implementation details.
>
> Individual files may evolve over time while directory responsibilities should remain relatively stable.

---

# A.1 Repository Philosophy

The repository is organized around **business responsibilities**, not programming language features.

Every top-level directory should answer one question:

> **What responsibility does this directory own?**

A developer should understand the repository structure before reading any implementation.

---

# A.2 High-Level Repository Layout

```
TABELA/

├── core/
├── engines/
├── market_data/
├── data/
├── docs/
├── scripts/
├── tests/
├── output/
├── logs/
├── cache/
├── config/
├── tools/
└── main.py
```

Individual folders may evolve.

Their responsibilities should remain stable.

---

# A.3 Root Directory

The repository root should remain intentionally lightweight.

Only place files here that satisfy one of the following:

- application entry point

- repository configuration

- project metadata

- developer tooling

- licensing

Avoid placing business logic in the repository root.

---

# A.4 core/

## Responsibility

Repository orchestration.

Core coordinates the platform.

Core does **not** perform business intelligence.

Representative responsibilities:

- execution pipeline

- runtime initialization

- configuration loading

- dependency coordination

- shared utilities

- execution context

Representative files:

- main.py

- pipeline.py

- config.py

- runtime_context.py

The exact filenames may evolve.

The responsibilities should not.

---

# A.5 engines/

## Responsibility

Business Intelligence.

This is the primary business layer of TABELA.

Representative engine categories include:

Market

↓

Theme

↓

ETF

↓

Stock

↓

Scoring

↓

Breadth

↓

Rotation

↓

Transition

↓

Presentation

↓

Historical Intelligence

Each engine should own one business responsibility.

Avoid cross-engine ownership.

---

# A.6 market_data/

## Responsibility

Persistent generated intelligence.

Representative contents include:

- historical snapshots

- transition registry

- watchlist history

- historical outputs

- weekly intelligence

This directory represents accumulated market knowledge.

Avoid deleting historical information.

---

# A.7 data/

## Responsibility

Reference data.

Examples include:

- mappings

- normalization tables

- industry information

- ETF relationships

- static lookup tables

Reference data should change infrequently.

Avoid placing generated intelligence here.

---

# A.8 docs/

## Responsibility

Permanent engineering knowledge.

Representative documentation:

SYSTEM_CONTEXT.md

Architecture

Business methodology

Engineering standards

Migration guides

Repository documentation should become the long-term memory of the project.

---

# A.9 scripts/

## Responsibility

Operational utilities.

Examples include:

- migrations

- maintenance

- repair

- validation

- one-time conversion

Scripts should not become permanent business engines.

---

# A.10 tests/

## Responsibility

Repository validation.

Representative responsibilities:

- regression testing

- integration testing

- business validation

- configuration validation

Testing should verify behaviour rather than implementation.

---

# A.11 output/

## Responsibility

Generated reports.

Representative artifacts:

- markdown

- CSV

- JSON

- watchlists

- presentations

Outputs should be reproducible.

Avoid manual editing.

---

# A.12 logs/

## Responsibility

Operational diagnostics.

Representative contents:

- execution logs

- validation logs

- debugging information

Logs should assist troubleshooting.

They should not become business data.

---

# A.13 cache/

## Responsibility

Temporary execution artifacts.

Cache contents should always be regenerable.

Business intelligence should never depend upon cache persistence.

---

# A.14 config/

## Responsibility

Optional external configuration.

The primary business configuration remains:

core/config.py

This directory may contain:

- environment configuration

- deployment configuration

- optional runtime configuration

Avoid duplicating business constants.

---

# A.15 tools/

## Responsibility

Developer productivity.

Representative examples:

- documentation generators

- maintenance utilities

- repository analysis

- migration tools

Tools should support development.

They should not implement business methodology.

---

# A.16 Repository Layer Responsibilities

```
Input Data
        │
        ▼
Configuration
        │
        ▼
Core
        │
        ▼
Business Engines
        │
        ▼
Historical Intelligence
        │
        ▼
Presentation
        │
        ▼
Outputs
```

Responsibilities should remain unidirectional.

---

# A.17 Module Ownership Matrix

| Module | Owns |
|----------|----------------------------------|
| core | orchestration |
| engines | business intelligence |
| market_data | historical persistence |
| data | reference datasets |
| docs | engineering knowledge |
| tests | validation |
| output | generated artifacts |
| logs | diagnostics |
| cache | temporary execution state |
| scripts | maintenance |
| tools | developer productivity |

Ownership should remain unique.

---

# A.18 Repository Dependency Rules

Allowed dependency direction:

```
Configuration

↓

Core

↓

Business Engines

↓

Historical Intelligence

↓

Presentation

↓

Outputs
```

Avoid:

Presentation

↓

Business Logic

Avoid:

Historical Intelligence

↓

Configuration

Avoid circular dependencies.

---

# A.19 File Organization Rules

Each file should satisfy:

One responsibility.

Clear ownership.

Obvious purpose.

Minimal dependencies.

Representative naming examples:

theme_engine.py

stock_transition_engine.py

market_context_engine.py

Avoid generic names such as:

utils2.py

helper_new.py

misc.py

---

# A.20 Repository Growth Rules

As the repository grows:

Prefer:

Improving existing modules

↓

Extracting reusable components

↓

Creating new engines only when ownership changes

Avoid creating modules simply because a file becomes large.

File size alone is not justification for architectural change.

---

# A.21 Repository Documentation Requirements

Every major directory should eventually contain documentation explaining:

Purpose

Responsibilities

Inputs

Outputs

Dependencies

Business ownership

The objective is for another engineer to understand repository organization without reading implementation.

---

# A.22 Repository Success Criteria

Repository organization is considered successful when:

- directory ownership is obvious

- module responsibilities are clear

- dependencies remain simple

- navigation is intuitive

- architecture scales naturally

- business methodology remains easy to locate

- AI assistants can understand ownership without historical conversations

The repository structure should become progressively easier to navigate as TABELA evolves.

---

# APPENDIX B — ENGINE INVENTORY & RESPONSIBILITY SPECIFICATION

> **Purpose**
>
> This appendix defines the architectural responsibilities of every major engine category within TABELA.
>
> It intentionally documents **responsibilities**, **ownership**, and **interaction rules** rather than implementation details.
>
> Engine names may evolve.
>
> Business responsibilities should remain stable.

---

# B.1 Engine Philosophy

An engine is the smallest independently maintainable business component within TABELA.

Every engine exists because it answers one business question.

If an engine cannot clearly answer:

> "Why does this engine exist?"

its responsibility is not sufficiently defined.

---

# B.2 Engine Design Principles

Every engine should satisfy the following principles.

## Single Responsibility

One engine.

One business responsibility.

---

## Explicit Inputs

Inputs should be obvious.

Hidden dependencies should not exist.

---

## Explicit Outputs

Every downstream engine should understand exactly what is produced.

---

## Deterministic

Identical inputs produce identical outputs.

---

## Configuration Driven

Business constants belong in configuration.

---

## Independently Testable

Whenever practical, engines should be executable independently.

---

## Explainable

Another engineer should understand an engine from:

- filename
- documentation
- public functions

without reading the implementation.

---

# B.3 Engine Lifecycle

Every engine follows the same logical processing model.

```
Input

↓

Validation

↓

Normalization

↓

Business Logic

↓

Classification

↓

Validation

↓

Output
```

No engine should bypass this lifecycle without architectural justification.

---

# B.4 Engine Categories

The repository naturally organizes engines into several categories.

```
Input Processing

↓

Market Intelligence

↓

Theme Intelligence

↓

Stock Intelligence

↓

Historical Intelligence

↓

Presentation
```

Each category owns a different business layer.

---

# B.5 Input Processing Engines

## Purpose

Convert raw market information into validated structured datasets.

Representative responsibilities include:

- schema validation

- normalization

- duplicate removal

- missing value handling

- identifier standardization

Input engines should never perform business analysis.

---

# B.6 ETF Intelligence Engines

## Business Question

What are institutions buying at the ETF level?

Representative responsibilities:

- ETF ranking

- benchmark comparison

- ETF normalization

- sector leadership

- macro trend identification

Outputs provide context for downstream stock analysis.

---

# B.7 Theme Intelligence Engines

## Business Question

Which investment themes are strengthening or weakening?

Representative responsibilities:

- theme normalization

- theme hierarchy

- parent theme mapping

- theme aggregation

- strategic theme classification

Theme intelligence should remain centralized.

Avoid duplicating theme logic elsewhere.

---

# B.8 Market Breadth Engine

## Business Question

How broad is participation within a theme or market?

Representative responsibilities:

- participation measurement

- advancing vs declining constituents

- leadership concentration

- market participation

Breadth complements strength.

It does not replace it.

---

# B.9 Rotation Engine

## Business Question

Where is institutional capital moving?

Representative responsibilities:

- sector rotation

- theme rotation

- improving leadership

- weakening leadership

Rotation measures change.

Not absolute strength.

---

# B.10 Market Context Engine

## Business Question

What is the current market environment?

Representative responsibilities:

- benchmark evaluation

- ETF context

- macro participation

- institutional environment

Market Context provides environmental interpretation.

It should not determine company classifications.

---

# B.11 Stock Intelligence Engine

## Business Question

How strong is an individual company?

Representative responsibilities:

- company normalization

- mapping

- Relative Strength

- business evaluation

- leadership assessment

- candidate preparation

Stock Intelligence is the central research layer.

---

# B.12 Composite Scoring Engine

## Business Question

How should multiple business dimensions be combined?

Representative responsibilities:

- weighted scoring

- normalization

- score calculation

- ranking

Business methodology belongs here.

Presentation does not.

---

# B.13 Fundamental Intelligence Engine

## Business Question

Is the company's business improving?

Representative evaluation includes:

- Revenue

- EPS

- Margins

- Free Cash Flow

- Guidance

- Earnings Quality

Business quality complements technical validation.

---

# B.14 Institutional Leadership Engine

## Business Question

Is institutional sponsorship increasing?

Representative evidence:

- persistence

- accumulation

- Relative Strength

- historical behaviour

Leadership should require multiple confirming observations.

---

# B.15 Episodic Pivot Engine

## Business Question

Has a major business event fundamentally changed company prospects?

Representative evidence includes:

- earnings

- guidance

- contracts

- analyst upgrades

- partnerships

- regulatory actions

- FDA

- delayed reactions

Episodic Pivot remains an independent evaluation.

---

# B.16 Transition Engine

## Business Question

How is institutional state changing over time?

Representative responsibilities:

- Observation

- Recovery

- Distribution

- Leadership transitions

Transition intelligence extends daily analysis into longitudinal analysis.

---

# B.17 Registry Engine

## Business Question

Which information must persist across executions?

Representative responsibilities:

- registry updates

- state persistence

- lifecycle tracking

Registries preserve operational memory.

They are not general databases.

---

# B.18 Historical Intelligence Engine

## Business Question

What can only be understood by looking across multiple trading sessions?

Representative responsibilities:

- persistence

- recovery

- deterioration

- leadership evolution

- historical comparisons

Historical Intelligence transforms observations into trends.

---

# B.19 Watchlist Engine

## Business Question

Which candidates deserve continued attention?

Representative outputs:

- Long Candidates

- Observation

- Distribution

- Recovering Leaders

Watchlists are research outputs.

They are not trading recommendations.

---

# B.20 Presentation Engine

## Business Question

How should intelligence be communicated?

Representative responsibilities:

- report formatting

- markdown

- CSV

- JSON

- dashboards

Presentation consumes intelligence.

It never creates business intelligence.

---

# B.21 Reporting Engine

Reporting combines outputs into coherent research deliverables.

Reports should remain:

- deterministic

- reproducible

- business focused

Reports should not introduce new calculations.

---

# B.22 Engine Dependency Matrix

```
Input Processing

↓

ETF Intelligence

↓

Theme Intelligence

↓

Market Context

↓

Stock Intelligence

↓

Composite Scoring

↓

Transition Analysis

↓

Historical Intelligence

↓

Presentation

↓

Reports
```

Dependencies should always move downward.

---

# B.23 Engine Communication Rules

Communication occurs only through structured datasets.

Never through:

- global variables

- hidden state

- engine internals

- undocumented assumptions

Every downstream dependency should be explicit.

---

# B.24 Engine Ownership Rules

Every important business concept should have exactly one owner.

Examples:

Theme Hierarchy

↓

Theme Engine

Composite Score

↓

Scoring Engine

Transition Registry

↓

Transition Engine

Presentation Tables

↓

Presentation Engine

Avoid duplicate ownership.

---

# B.25 Engine Error Handling

Recoverable situations:

- empty datasets

- optional inputs

- missing optional files

Critical situations:

- schema violations

- corrupted datasets

- missing required inputs

Critical failures should fail clearly.

Never silently continue after structural failures.

---

# B.26 Engine Extension Rules

Before creating a new engine ask:

1. Does an existing engine already own this responsibility?

2. Would extending it violate Single Responsibility?

3. Does the new engine answer a genuinely new business question?

Only create a new engine when the answer to Question 3 is **Yes**.

---

# B.27 Engine Success Criteria

A well-designed engine exhibits:

- one clear responsibility

- deterministic behaviour

- explicit ownership

- minimal dependencies

- configuration-driven behaviour

- reusable business logic

- complete documentation

- independent testability

Engine quality should be evaluated by long-term maintainability rather than implementation size.

---

# B.28 Future Engine Policy

Future engines should only be introduced when they answer a question that TABELA cannot currently answer.

This principle overrides preferences for additional modularity.

The objective is not to maximize the number of engines.

The objective is to maximize business capability while preserving architectural simplicity.

Every proposed engine should justify its existence in terms of business value rather than software structure.


---

# APPENDIX C — DATA CONTRACTS, DATA MODELS & SCHEMA GOVERNANCE

> **Purpose**
>
> This appendix defines the architectural rules governing data movement throughout TABELA.
>
> It intentionally specifies **contracts**, **ownership**, and **lifecycle** rather than implementation details.
>
> Individual columns, fields, and schemas may evolve.
>
> The governing principles described here should remain stable.

---

# C.1 Data Philosophy

Data is one of the primary architectural assets of TABELA.

Every dataset should satisfy the following characteristics:

- deterministic
- reproducible
- explainable
- version controlled
- well documented

Business intelligence should emerge from data processing.

It should never be manually inserted.

---

# C.2 Data Categories

The repository contains four primary categories of data.

## Raw Data

External observations.

Examples:

- ETF prices
- Stock prices
- Market indexes
- Volume
- Corporate fundamentals

Raw data should remain factual.

---

## Reference Data

Static lookup information.

Examples:

- Theme mappings
- Industry mappings
- Sector mappings
- Parent themes
- Translation tables

Reference data changes infrequently.

---

## Generated Intelligence

Derived information.

Examples:

- Composite Scores
- Relative Strength
- Theme Strength
- Rankings
- Watchlists
- Breadth

Generated intelligence must always be reproducible.

---

## Historical Intelligence

Persistent longitudinal information.

Examples:

- Daily snapshots
- Weekly summaries
- Transition registries
- Historical rankings
- Leadership evolution

Historical intelligence provides context unavailable from a single execution.

---

# C.3 Data Lifecycle

Every dataset follows the same conceptual lifecycle.

```
Raw Input

↓

Validation

↓

Normalization

↓

Enrichment

↓

Scoring

↓

Classification

↓

Historical Persistence

↓

Presentation

↓

Reports
```

Every stage should increase information value.

---

# C.4 Input Data Contracts

Every external dataset should define:

Required fields

↓

Optional fields

↓

Primary identifier

↓

Expected data types

↓

Validation rules

↓

Ownership

↓

Consumers

Business engines should rely on validated contracts rather than defensive parsing.

---

# C.5 Schema Validation

Before entering business processing every dataset should be validated.

Validation includes:

- required columns

- duplicate identifiers

- missing values

- datatype consistency

- structural integrity

Business logic should never compensate for malformed input.

---

# C.6 Canonical Identifier Philosophy

Every business entity should have one canonical identifier.

Examples:

Ticker

ETF

Theme

Industry

Sector

Company

Avoid maintaining multiple identifiers representing the same concept.

Normalization should occur before business processing.

---

# C.7 Theme Data Model

Representative hierarchy:

```
Company

↓

Industry

↓

Theme

↓

Parent Theme

↓

Strategic Theme
```

This hierarchy enables:

- aggregation

- reporting

- breadth

- rotation

- strategic analysis

Hierarchy ownership belongs to Theme Intelligence.

---

# C.8 Market Data Model

Representative conceptual structure:

```
Market

↓

ETF

↓

Sector

↓

Industry

↓

Company
```

Each level provides context for the next.

Lower levels should not ignore higher-level context.

---

# C.9 Composite Score Model

Composite Score represents a business object.

It combines multiple independent dimensions.

Representative contributors include:

- Relative Strength

- Theme Strength

- Fundamentals

- Institutional Behaviour

- Historical Persistence

Weighting methodology belongs in configuration.

Business philosophy belongs in SYSTEM_CONTEXT.md.

---

# C.10 Candidate State Model

Representative lifecycle:

```
Unknown

↓

Candidate

↓

Leadership

↓

Observation

↓

Distribution

↓

Recovery

↓

Leadership
```

The implementation may evolve.

The conceptual lifecycle should remain stable.

---

# C.11 Registry Data Model

Registries preserve longitudinal operational state.

Representative fields include:

- Identifier

- Current State

- Previous State

- Observation Count

- Transition History

- First Observation

- Last Observation

Exact schemas belong to implementation.

Registry philosophy belongs here.

---

# C.12 Historical Snapshot Model

Snapshots represent immutable observations.

Representative contents include:

- rankings

- scores

- classifications

- breadth

- market context

Snapshots should not be rewritten after creation.

---

# C.13 Watchlist Model

Watchlists represent research outputs.

Representative watchlists include:

- Long Candidates

- Observation

- Distribution

- Recovering Leaders

Watchlists should remain deterministic.

Manual editing should be avoided.

---

# C.14 Output Contracts

Every output should define:

Purpose

↓

Producer

↓

Consumers

↓

Schema

↓

Version

↓

Generation Frequency

Outputs should remain predictable.

---

# C.15 CSV Standards

CSV outputs should satisfy:

- flat structure

- deterministic ordering

- UTF-8 encoding

- reproducible generation

Avoid nested structures.

---

# C.16 JSON Standards

JSON outputs should satisfy:

- stable schema

- deterministic ordering

- machine readability

- backwards compatibility where practical

Avoid unnecessary nesting.

---

# C.17 Markdown Output Standards

Markdown reports should prioritize:

- readability

- traceability

- reproducibility

Presentation should not introduce new business logic.

---

# C.18 Engine Data Contracts

Every engine should explicitly document:

Input datasets

↓

Output datasets

↓

Required fields

↓

Optional fields

↓

Ownership

↓

Downstream consumers

Implicit contracts should be avoided.

---

# C.19 Data Ownership Matrix

| Business Object | Primary Owner |
|-----------------|---------------|
| Market Context | Market Context Engine |
| Theme Hierarchy | Theme Intelligence |
| Theme Strength | Theme Intelligence |
| Relative Strength | Stock Intelligence |
| Composite Score | Scoring Engine |
| Candidate Classification | Classification Engine |
| Transition Registry | Transition Engine |
| Historical Snapshots | Historical Intelligence |
| Watchlists | Watchlist Engine |
| Reports | Presentation Engine |

Ownership should remain unique.

---

# C.20 Data Integrity Rules

Data integrity has higher priority than execution continuity.

If required business data is invalid:

Fail clearly.

Do not silently fabricate values.

Do not silently discard critical records.

Recoverable situations should remain recoverable.

Structural failures should terminate processing.

---

# C.21 Schema Evolution

Schemas may evolve over time.

Schema evolution should satisfy:

Backward compatibility whenever practical.

Migration documentation.

Change log update.

Validation updates.

Avoid unnecessary schema churn.

---

# C.22 Derived Data Rules

Derived values should:

be reproducible

↓

be deterministic

↓

have documented ownership

↓

be traceable to source data

Never manually edit generated intelligence.

---

# C.23 Data Persistence Philosophy

Persist only information providing future analytical value.

Examples:

Transition history

Persistence metrics

Historical rankings

Leadership evolution

Avoid persisting temporary calculations.

---

# C.24 Data Retention Philosophy

Historical market intelligence is a strategic asset.

Prefer retaining historical information.

Deletion should be exceptional rather than routine.

Historical analysis depends upon continuity.

---

# C.25 Data Quality Standards

Every major dataset should satisfy:

Completeness

Consistency

Determinism

Traceability

Validation

Reproducibility

Business Correctness

These qualities define trustworthy market intelligence.

---

# C.26 Future Data Model Evolution

Future schema evolution should preserve:

- conceptual ownership

- deterministic behaviour

- business methodology

- historical compatibility

Implementation details may evolve.

The architectural data philosophy should remain stable.

---

# C.27 Data Architecture Success Criteria

The data architecture is considered successful when:

- ownership is obvious

- schemas are documented

- validation occurs before processing

- generated intelligence is reproducible

- historical intelligence remains consistent

- downstream engines rely on explicit contracts

- future engineers can understand data flow without reading implementation

Data should become progressively easier to understand as the repository evolves.


---

# APPENDIX D — OPENCODE, OPENROUTER & AI ENGINEERING OPERATIONS

> **Purpose**
>
> This appendix defines how AI models are operationally integrated into TABELA development.
>
> It specifies responsibilities, delegation rules, collaboration workflows, review procedures, and engineering governance.
>
> It intentionally documents **process**, not model-specific prompt engineering.

---

# D.1 Philosophy

TABELA intentionally adopts a **multi-model engineering strategy**.

Different AI models possess different strengths.

Instead of expecting one model to perform every engineering task equally well, work is delegated according to specialization.

This improves:

- engineering quality
- architectural consistency
- implementation reliability
- review quality

---

# D.2 Objectives

The OpenCode workflow exists to:

- improve engineering quality
- reduce architectural mistakes
- separate design from implementation
- leverage specialized models
- minimize rework
- maintain repository consistency

The objective is not maximizing AI usage.

The objective is maximizing repository quality.

---

# D.3 Development Environment

Representative development stack:

- VS Code
- OpenCode
- OpenRouter
- Python
- Git
- GitHub

OpenCode acts as the engineering orchestration layer.

OpenRouter provides access to specialized models.

---

# D.4 Engineering Workflow

Typical workflow:

```
Business Requirement

↓

Architecture

↓

Architecture Review

↓

Implementation

↓

Validation

↓

Documentation

↓

Commit

↓

Repository Synchronization
```

The workflow intentionally separates thinking from coding.

---

# D.5 Model Responsibilities

Each model owns specific engineering responsibilities.

Avoid assigning work outside those responsibilities.

---

# D.6 architect_sonnet

Primary responsibilities:

- repository architecture
- pipeline analysis
- dependency analysis
- system design
- large refactoring
- multi-engine coordination
- maintainability review
- engineering trade-off analysis

Typical work:

- repository redesign
- architectural review
- engine ownership
- execution flow
- dependency restructuring

Not intended for:

- formatting
- isolated bug fixes
- documentation polishing

---

# D.7 architect_kimi

Primary responsibilities:

- architectural brainstorming
- alternative designs
- structural validation
- engineering review
- repository-wide reasoning
- long-term planning

Typical work:

- second architectural opinion
- challenging assumptions
- identifying simplification opportunities
- validating proposed designs

This model complements architect_sonnet rather than replacing it.

---

# D.8 coder_glm

Primary responsibilities:

- implementing business engines
- composite scoring
- data transformation
- business rules
- processing pipelines
- algorithm implementation

Typical work:

- new engines
- scoring logic
- transformation functions
- historical processing

Focus:

Business implementation.

---

# D.9 coder_qwen

Primary responsibilities:

- feature implementation
- repository enhancements
- engine development
- structured Python programming
- incremental refactoring

Typical work:

- implementation
- enhancement
- maintenance
- modularization

Focus:

Reliable engineering.

---

# D.10 patcher_flash

Reserved exclusively for:

- formatting
- comments
- docstrings
- syntax corrections
- localized bug fixes
- import cleanup
- small maintenance patches

Avoid assigning:

- architecture
- business methodology
- pipeline redesign
- repository restructuring
- multi-engine refactoring

---

# D.11 Model Selection Rules

Choose the model according to task complexity.

Small localized fix

↓

patcher_flash

Business implementation

↓

coder_glm

General implementation

↓

coder_qwen

Architecture

↓

architect_sonnet

Architecture review

↓

architect_kimi

---

# D.12 Multi-Model Collaboration

Complex engineering should follow this sequence.

```
Business Requirement

↓

architect_sonnet

↓

architect_kimi

↓

coder_glm / coder_qwen

↓

patcher_flash

↓

Human Review
```

Each stage answers a different engineering question.

---

# D.13 AI Review Philosophy

AI-generated code should not automatically be accepted.

Review should verify:

- business correctness
- architecture
- ownership
- maintainability
- determinism
- documentation

The objective is engineering quality rather than AI productivity.

---

# D.14 AI Decision Rules

Before suggesting implementation an AI assistant should determine:

Does architecture already support this?

Does an existing engine own it?

Will implementation increase maintenance?

Will documentation require updating?

Should configuration change?

Engineering should begin only after these questions are answered.

---

# D.15 Prompt Philosophy

Prompts should describe:

Business objective

↓

Constraints

↓

Expected ownership

↓

Required outputs

Avoid vague implementation requests.

The better the engineering specification, the better the implementation.

---

# D.16 AI Collaboration Rules

Multiple AI assistants should collaborate rather than compete.

Examples:

Architecture

↓

Implementation

↓

Review

↓

Validation

↓

Documentation

Different assistants may specialize in different stages.

---

# D.17 Human Responsibilities

The human developer remains responsible for:

- business decisions
- architectural approval
- repository ownership
- Git history
- production deployment
- final code acceptance

AI assistants provide engineering assistance.

They do not own the repository.

---

# D.18 AI Responsibilities

AI assistants are expected to:

- understand before coding
- preserve architecture
- preserve business methodology
- minimize technical debt
- document structural changes
- identify engineering risks
- recommend simplifications

AI assistants should not optimize merely for shorter code.

---

# D.19 Validation Workflow

Every AI-generated implementation should verify:

Repository integrity

↓

Compilation

↓

Execution

↓

Business outputs

↓

Documentation

↓

Repository consistency

Validation precedes acceptance.

---

# D.20 Documentation Requirements

Whenever an AI assistant modifies:

- architecture
- configuration
- pipeline
- engine ownership
- schemas
- repository structure

the assistant should recommend updating:

- SYSTEM_CONTEXT.md
- related documentation
- Appendix G (Change Log)
- Architecture Decision Record (ADR), if applicable

---

# D.21 Repository Synchronization

Repository synchronization should occur after:

Validated implementation

↓

Documentation update

↓

Git commit

↓

Push

↓

Knowledge synchronization

Avoid repository states where implementation and documentation diverge.

---

# D.22 AI Independence

The repository should remain independent of:

- ChatGPT
- Gemini
- Claude
- Qwen
- GLM
- Kimi
- future models

The documented engineering process should remain valid regardless of which AI assistant performs the work.

---

# D.23 Operational Success Criteria

The AI engineering workflow is considered successful when:

- architecture remains coherent

- business methodology remains unchanged unless explicitly approved

- documentation stays synchronized

- implementation remains deterministic

- repository quality continuously improves

- future AI assistants require progressively less conversational context

The ultimate objective is an AI-agnostic engineering process where repository knowledge becomes the primary source of truth.


---

# APPENDIX E — FIELD GLOSSARY & CANONICAL TERMINOLOGY

> **Purpose**
>
> This appendix establishes the canonical business vocabulary used throughout TABELA.
>
> Every business term should have one consistent definition.
>
> Avoid using multiple names for the same concept.
>
> Consistent terminology improves:
>
> - documentation
> - implementation
> - AI reasoning
> - maintainability
> - onboarding

---

# E.1 Canonical Terminology

Whenever possible:

One concept

↓

One name

Avoid:

One concept

↓

Multiple names

Terminology consistency reduces engineering ambiguity.

---

# E.2 Market

The complete collection of securities being analyzed.

Market represents the highest contextual layer.

---

# E.3 ETF

Exchange Traded Fund.

Within TABELA, ETFs primarily represent:

- sectors
- industries
- investment themes
- market leadership

ETF intelligence provides macro context.

---

# E.4 Sector

Broad economic classification.

Sectors contain multiple industries.

Sectors provide structural organization.

---

# E.5 Industry

Subclassification within a sector.

Industries contain related companies.

Industries contribute to Theme Intelligence.

---

# E.6 Theme

A normalized investment concept.

Themes may represent:

- technology trends

- commodities

- macro themes

- strategic investment narratives

Themes are one of the primary organizational structures within TABELA.

---

# E.7 Parent Theme

Higher-level grouping of related themes.

Examples:

Cybersecurity

↓

Software

↓

Technology

Parent Themes enable strategic reporting.

---

# E.8 Strategic Theme

Highest conceptual investment grouping.

Strategic themes support:

- market intelligence

- long-term reporting

- macro analysis

---

# E.9 Company

Individual publicly traded business.

Company analysis combines:

- fundamentals

- technical validation

- historical intelligence

- institutional behaviour

---

# E.10 Relative Strength (RS)

Relative price performance compared with an appropriate benchmark.

Relative Strength represents one evaluation dimension.

It is not a complete ranking methodology.

---

# E.11 Theme Strength

Strength of a normalized investment theme.

Theme Strength measures:

theme quality

not

individual stock quality.

---

# E.12 Breadth

Participation within a theme or market.

Breadth measures:

How many constituents are contributing?

Strong breadth generally indicates healthier leadership.

---

# E.13 Rotation

Movement of institutional capital.

Rotation measures:

Change

rather than

absolute strength.

---

# E.14 Composite Score

Weighted evaluation combining multiple independent business dimensions.

Composite Score exists to prioritize research.

It is not intended as a trading signal.

Weights belong in configuration.

---

# E.15 Institutional Leadership

Evidence suggesting sustained institutional sponsorship.

Leadership should require multiple independent confirmations.

Leadership should not be assigned from isolated observations.

---

# E.16 Candidate

Company currently under evaluation.

Candidate status does not imply investment recommendation.

It simply indicates research interest.

---

# E.17 Long Candidate

Company satisfying the platform's long-side research methodology.

Long Candidate represents a research classification.

Not a trade recommendation.

---

# E.18 Observation

Intermediate monitoring state.

Observation indicates:

additional evidence required.

Observation should not be interpreted as weakness.

---

# E.19 Distribution

Evidence suggesting deterioration of previous institutional leadership.

Distribution represents a process.

Not a single event.

---

# E.20 Recovery

Evidence suggesting renewed institutional sponsorship.

Recovery should require confirmation.

Avoid premature recovery classification.

---

# E.21 Transition

Movement between business states.

Examples:

Observation

↓

Recovery

↓

Leadership

↓

Distribution

Transitions provide longitudinal intelligence.

---

# E.22 Registry

Persistent storage of operational state.

Registries preserve historical business intelligence.

Registries are not general-purpose databases.

---

# E.23 Historical Intelligence

Knowledge derived from multiple executions.

Examples:

- persistence

- recovery

- deterioration

- transition history

Historical Intelligence extends daily observations.

---

# E.24 Market Context

Environmental information describing current market conditions.

Representative components:

- ETFs

- Breadth

- Rotation

- Market participation

Market Context provides interpretation.

---

# E.25 Watchlist

Curated collection of research candidates.

Watchlists are deterministic outputs.

They are not trading signals.

---

# E.26 Snapshot

Immutable historical record.

Snapshots preserve market state for future analysis.

Snapshots should not be rewritten.

---

# E.27 Persistence

Continuation of behaviour across multiple executions.

Persistence is stronger evidence than isolated observations.

---

# E.28 Episodic Pivot (EP)

A significant business event capable of fundamentally changing company prospects.

Representative categories include:

- Growth EP

- Turnaround EP

- Story EP

- Government EP

- Regulatory EP

- Large Order EP

- Delayed Reaction EP

EP status is evaluated independently of overall candidate score.

---

# E.29 Delayed Reaction EP

An Episodic Pivot whose institutional recognition occurs after the original catalyst.

Delayed Reaction EPs are important because institutional accumulation often develops gradually.

---

# E.30 Institutional Accumulation

Evidence suggesting increasing institutional ownership or sponsorship.

Accumulation should be evaluated through multiple independent forms of evidence.

---

# E.31 Technical Validation

Objective technical evidence supporting business conclusions.

Representative evidence:

- Relative Strength

- Moving Averages

- Trend Quality

- Volume

- Gap Quality

Technical validation supports business analysis.

It does not replace it.

---

# E.32 Fundamental Momentum

Improvement in business performance.

Representative dimensions:

- Revenue

- EPS

- Margins

- Guidance

- Cash Flow

Fundamental Momentum complements technical validation.

---

# E.33 Historical Persistence

Continuation of behaviour across multiple trading sessions.

Historical Persistence strengthens confidence in business conclusions.

---

# E.34 Market Breadth

Participation across the broader market.

Market Breadth differs from Theme Breadth.

Theme Breadth evaluates one investment theme.

Market Breadth evaluates the broader market.

---

# E.35 Dashboard

Aggregated presentation of market intelligence.

Dashboards summarize information.

They should not perform business calculations.

---

# E.36 Report

Formatted research output.

Reports communicate existing intelligence.

Reports should not generate new intelligence.

---

# E.37 Engine

Independent business processing component.

Each engine owns one primary responsibility.

---

# E.38 Pipeline

Deterministic execution sequence coordinating repository operations.

The pipeline orchestrates.

It does not own business methodology.

---

# E.39 Runtime Context

Shared execution information.

Examples:

- trading date

- execution environment

- output directories

Runtime Context supports orchestration.

---

# E.40 Configuration

Centralized business policy.

Configuration defines:

thresholds

weights

limits

paths

feature switches

Configuration does not define business methodology.

---

# E.41 Repository

The permanent engineering memory of TABELA.

The repository includes:

- source code

- documentation

- configuration

- historical intelligence

Repository knowledge should eventually replace conversational knowledge.

---

# E.42 Canonical Vocabulary Rules

Every important business concept should have:

One preferred name.

One preferred definition.

One primary owner.

Avoid introducing synonyms unless there is a compelling business reason.

Consistent terminology improves:

- architecture

- implementation

- documentation

- AI reasoning

- onboarding

The glossary should be updated whenever a significant new business concept is introduced.


---

# APPENDIX F — THEME HIERARCHY, MAPPING FRAMEWORK & CLASSIFICATION GOVERNANCE

> **Purpose**
>
> This appendix defines the conceptual framework governing how companies are classified into industries, themes, parent themes, and strategic themes.
>
> It documents the business methodology rather than implementation details.
>
> Mapping files and implementation may evolve.
>
> Classification philosophy should remain stable.

---

# F.1 Theme Philosophy

Themes are one of the foundational concepts within TABELA.

The purpose of Theme Intelligence is to transform thousands of individual companies into understandable market structure.

Rather than asking:

"What is Company X doing?"

TABELA first asks:

"What investment theme is strengthening?"

Themes provide market context.

Companies provide supporting evidence.

---

# F.2 Hierarchical Classification

Every company should belong to a hierarchical classification structure.

```
Company

↓

Industry

↓

Theme

↓

Parent Theme

↓

Strategic Theme
```

Each level answers a different business question.

---

# F.3 Company

Represents an individual publicly traded business.

Companies are the lowest analytical level.

Company-level intelligence includes:

- fundamentals

- technical validation

- institutional behaviour

- composite scoring

---

# F.4 Industry

Industries group companies performing similar business activities.

Industries provide the first level of aggregation.

Industries should remain factual.

Avoid creating industries based upon temporary narratives.

---

# F.5 Theme

Themes represent normalized investment concepts.

Representative examples include:

- Cybersecurity

- Cloud Computing

- Semiconductors

- Robotics

- Nuclear Energy

- Copper

- Uranium

- Defense

Themes should remain:

- stable

- normalized

- reusable

---

# F.6 Parent Theme

Parent Themes consolidate related investment themes.

Example:

```
Cybersecurity

↓

Enterprise Software

↓

Software

↓

Technology
```

Parent Themes improve:

- aggregation

- reporting

- breadth analysis

- strategic understanding

---

# F.7 Strategic Theme

Strategic Themes represent the highest conceptual investment layer.

Representative examples:

Technology

Energy

Healthcare

Financials

Industrial Automation

Artificial Intelligence

Strategic Themes support:

- macro reporting

- rotation

- market intelligence

---

# F.8 Theme Normalization

Theme normalization exists to eliminate duplicate terminology.

Representative examples:

AI

Artificial Intelligence

Generative AI

↓

Artificial Intelligence

Normalization should occur before business analysis.

---

# F.9 Mapping Philosophy

Mappings should be:

deterministic

↓

centralized

↓

version controlled

↓

documented

↓

reusable

Mapping logic should never be duplicated across engines.

---

# F.10 Mapping Ownership

Theme mapping ownership belongs to Theme Intelligence.

Other engines should consume normalized mappings.

They should not independently perform theme normalization.

---

# F.11 Theme Granularity

Themes should remain sufficiently specific to provide useful market intelligence.

Avoid:

Technology

for every software company.

Prefer:

Cybersecurity

Enterprise Software

Cloud Infrastructure

Semiconductor Equipment

Granularity improves analytical usefulness.

---

# F.12 Theme Aggregation

Aggregation enables broader market understanding.

Representative aggregation:

```
Cloud Infrastructure

↓

Enterprise Software

↓

Software

↓

Technology
```

Aggregation supports:

- strategic reporting

- breadth

- rotation

- leadership

---

# F.13 Multi-Theme Companies

Some companies legitimately participate in multiple investment themes.

Examples include:

AI + Cloud

AI + Semiconductors

Defense + Aerospace

Robotics + Industrial Automation

Multiple theme participation should be explicitly supported where justified.

Avoid assigning multiple themes merely because they are fashionable.

---

# F.14 Primary Theme

Every company should have one Primary Theme.

The Primary Theme represents the dominant investment identity.

Primary Theme drives:

- reporting

- aggregation

- leadership analysis

Additional themes provide supplementary context.

---

# F.15 Secondary Themes

Secondary Themes represent legitimate additional participation.

Secondary Themes should enrich intelligence.

They should not replace Primary Theme classification.

---

# F.16 Theme Strength

Theme Strength represents the collective quality of participating companies.

Theme Strength is influenced by:

- constituent quality

- participation

- breadth

- institutional sponsorship

Theme Strength is not determined by one exceptional company.

---

# F.17 Theme Breadth

Theme Breadth measures participation.

Questions answered include:

How many companies are strengthening?

How many companies are deteriorating?

How concentrated is leadership?

Breadth complements Theme Strength.

---

# F.18 Theme Leadership

Theme Leadership evaluates the quality of companies within a theme.

Strong themes generally contain:

- multiple leaders

- improving breadth

- institutional sponsorship

Avoid declaring theme leadership from one exceptional stock.

---

# F.19 Theme Rotation

Theme Rotation measures changing institutional preference.

Representative observations:

Emerging themes

↓

Strengthening themes

↓

Mature leadership

↓

Weakening participation

↓

Declining themes

Rotation measures change rather than absolute quality.

---

# F.20 Theme Persistence

Persistent theme leadership carries greater significance than isolated daily strength.

Historical persistence should influence interpretation.

Avoid overreacting to one trading session.

---

# F.21 Theme Quality

Representative contributors include:

- breadth

- Relative Strength

- leadership

- institutional accumulation

- historical persistence

Theme quality should be based upon objective evidence.

---

# F.22 Theme Governance

Adding a new theme requires justification.

Questions to answer:

Does this represent a genuinely distinct investment concept?

Will it improve market intelligence?

Can existing themes already represent it?

Avoid unnecessary proliferation of themes.

---

# F.23 Theme Stability

Theme names should remain stable.

Renaming themes should be exceptional.

If renaming is necessary:

Update:

- mappings

- documentation

- reports

- historical references

Consistency is more valuable than cosmetic improvements.

---

# F.24 Theme Hierarchy Maintenance

Hierarchy maintenance should remain centralized.

Avoid embedding hierarchy knowledge inside business engines.

Hierarchy should evolve through controlled updates rather than ad hoc modifications.

---

# F.25 Classification Success Criteria

The classification framework is considered successful when:

- every company has a clear investment identity

- hierarchy remains understandable

- normalization eliminates duplicate terminology

- aggregation supports meaningful reporting

- breadth accurately reflects participation

- future engineers can understand the hierarchy without historical conversations

The objective of Theme Intelligence is to transform thousands of companies into a coherent representation of institutional market structure.

---

# APPENDIX G — CHANGE LOG, ARCHITECTURAL DECISION RECORDS & EVOLUTION GOVERNANCE

> **Purpose**
>
> This appendix establishes the governance process for recording significant engineering decisions.
>
> The objective is that future developers and AI assistants understand:
>
> - what changed
> - why it changed
> - who approved it
> - what systems were affected
> - how it impacts future development
>
> Architecture should never evolve through undocumented decisions.

---

# G.1 Philosophy

The repository should preserve not only source code,

but also

engineering reasoning.

A future engineer should understand:

- why an engine exists

- why architecture changed

- why business methodology evolved

without reading historical conversations.

---

# G.2 Documentation Drift

Documentation drift is considered an engineering defect.

Whenever implementation changes,

documentation should change in the same commit whenever practical.

No architectural change is considered complete until:

- implementation

- documentation

- change log

remain synchronized.

---

# G.3 What Must Be Logged

The following require Change Log entries.

## Architecture

Examples:

- new engine

- engine removal

- repository restructuring

- dependency changes

- execution flow

---

## Business Methodology

Examples:

- scoring methodology

- transition methodology

- candidate qualification

- EP methodology

- breadth methodology

---

## Configuration

Examples:

- threshold changes

- weighting changes

- runtime defaults

- feature flags

---

## Data Contracts

Examples:

- schema changes

- field additions

- identifier changes

- persistence modifications

---

## Historical Intelligence

Examples:

- registry changes

- snapshot changes

- persistence strategy

---

## Documentation

Examples:

- SYSTEM_CONTEXT updates

- architecture updates

- methodology documentation

---

# G.4 Changes That Do NOT Require Logging

Examples include:

- formatting

- comments

- spelling

- docstrings

- variable renaming

- import ordering

- code style

unless they affect architecture or behaviour.

---

# G.5 Change Log Entry Template

Every significant change should record:

```
Date

Component

Category

Reason

Business Impact

Technical Impact

Files Modified

Configuration Modified

Documentation Updated

Backward Compatible

Approved By
```

This template should remain stable.

---

# G.6 Change Categories

Recommended categories include:

Architecture

Business Rules

Configuration

Implementation

Performance

Documentation

Testing

Migration

Infrastructure

Refactoring

Bug Fix

---

# G.7 Architectural Decision Records (ADR)

Large architectural decisions should also receive an ADR.

An ADR explains

why

rather than merely

what.

---

# G.8 ADR Template

Every ADR should contain:

```
Title

Status

Context

Problem

Options Considered

Decision

Consequences

Alternatives Rejected

Implementation Notes

Future Considerations
```

---

# G.9 When an ADR is Required

Representative examples:

- introducing a major engine

- repository restructuring

- pipeline redesign

- persistence redesign

- scoring architecture redesign

- major configuration philosophy changes

Minor bug fixes do not require ADRs.

---

# G.10 Decision Principles

Every architectural decision should satisfy:

Business Value

↓

Maintainability

↓

Deterministic Behaviour

↓

Architectural Simplicity

↓

Future Maintainability

If a proposal fails these criteria,

it should be reconsidered.

---

# G.11 Repository Evolution Rules

Repository evolution should remain:

incremental

↓

documented

↓

reviewable

↓

reversible whenever practical

Avoid irreversible architectural decisions without strong justification.

---

# G.12 Breaking Changes

Breaking changes should be exceptional.

Every breaking change should document:

- rationale

- migration

- affected components

- compatibility impact

- documentation updates

Breaking changes should never surprise downstream users.

---

# G.13 Configuration Change Governance

Whenever configuration changes:

Validate downstream impact.

Update documentation.

Update SYSTEM_CONTEXT.md if architectural behaviour changes.

Update Change Log.

Configuration should never silently drift.

---

# G.14 Pipeline Change Governance

Pipeline modifications require additional review.

Document:

- execution order

- dependency impact

- business impact

- affected engines

Pipeline stability is considered a core architectural characteristic.

---

# G.15 Engine Change Governance

Whenever an engine changes:

Record:

- ownership

- responsibilities

- inputs

- outputs

- downstream consumers

Engine responsibilities should remain explicit.

---

# G.16 Business Methodology Governance

Business methodology changes require explicit user approval.

Examples include:

- scoring philosophy

- scanner methodology

- transition methodology

- candidate classification

- registry behaviour

Engineering convenience alone is never sufficient justification.

---

# G.17 Repository Versioning Philosophy

Version numbers should represent repository evolution,

not merely implementation changes.

Architecture evolves more slowly than implementation.

Documentation should reflect architectural maturity.

---

# G.18 Historical Decision Preservation

Engineering decisions should never depend upon memory.

Every major decision should eventually exist in:

Repository

↓

Documentation

↓

ADR

↓

Change Log

Conversation history should not become the permanent archive.

---

# G.19 Future Maintainability

Future engineers should understand:

Why the repository looks the way it does.

Not merely:

How it currently works.

Good documentation explains reasoning.

---

# G.20 Governance Success Criteria

Governance is considered successful when:

- architectural decisions are documented

- business methodology remains traceable

- configuration changes are recorded

- documentation stays synchronized

- future AI assistants understand historical decisions without conversation history

The objective is a repository whose evolution is fully understandable from its own documentation.


---

# APPENDIX H — ARCHITECTURAL DECISION RECORDS (ADR)

> **Purpose**
>
> This appendix documents the most significant architectural decisions made during the evolution of TABELA.
>
> Unlike the Change Log, which records *what changed*, an ADR records **why the architecture exists in its current form**.
>
> ADRs should be updated only for major architectural decisions.

---

# H.1 ADR Philosophy

Architecture should not become the product of accumulated implementation decisions.

Instead:

Architecture

↓

Design Decision

↓

Documentation

↓

Implementation

↓

Validation

Every significant architectural decision should eventually be represented by an ADR.

---

# ADR-001 — Modular Engine Architecture

## Status

Accepted

---

## Context

As the platform expanded, business logic naturally diversified into multiple independent domains:

- ETF analysis
- Theme Intelligence
- Market Breadth
- Rotation
- Stock Analysis
- Historical Intelligence
- Presentation

A monolithic implementation would rapidly become difficult to maintain.

---

## Decision

Adopt a modular engine architecture.

Each engine owns one primary business responsibility.

---

## Consequences

Positive

- clearer ownership
- easier debugging
- simpler testing
- independent evolution

Negative

- increased coordination
- additional interfaces

Overall impact:

Strongly positive.

---

# ADR-002 — Deterministic Linear Pipeline

## Status

Accepted

---

## Context

Market intelligence should remain reproducible.

Different execution paths increase engineering complexity.

---

## Decision

Adopt a deterministic linear pipeline.

```
Configuration

↓

Pipeline

↓

Business Engines

↓

Historical Intelligence

↓

Presentation

↓

Outputs
```

---

## Consequences

Benefits:

- reproducibility

- easier debugging

- simpler dependency management

Trade-off:

Reduced runtime flexibility.

Accepted.

---

# ADR-003 — Configuration Driven Architecture

## Status

Accepted

---

## Context

Business constants were appearing throughout implementation.

This complicated maintenance.

---

## Decision

Centralize business constants within configuration.

Examples include:

- thresholds

- weights

- feature switches

- limits

Implementation should consume configuration.

Not define it.

---

## Consequences

Benefits:

- easier tuning

- cleaner implementation

- reduced duplication

---

# ADR-004 — Historical Intelligence

## Status

Accepted

---

## Context

Daily analysis alone cannot identify leadership evolution.

Historical persistence became necessary.

---

## Decision

Treat historical intelligence as a first-class architectural component.

Introduce:

- registries

- snapshots

- persistence

Historical information becomes part of the analytical model.

---

## Consequences

Benefits:

- transition analysis

- recovery analysis

- persistence evaluation

Trade-off:

Additional storage.

Accepted.

---

# ADR-005 — Registry-Based Transition Tracking

## Status

Accepted

---

## Context

Single-day classifications fail to capture leadership evolution.

---

## Decision

Persist transition state across executions.

Representative lifecycle:

Observation

↓

Leadership

↓

Distribution

↓

Recovery

↓

Leadership

---

## Consequences

Benefits:

- longitudinal analysis

- historical continuity

- institutional behaviour tracking

---

# ADR-006 — Separation of Presentation

## Status

Accepted

---

## Context

Presentation logic began accumulating business calculations.

---

## Decision

Presentation consumes intelligence.

Presentation never creates intelligence.

Business calculations remain inside business engines.

---

## Consequences

Benefits:

- cleaner architecture

- reusable intelligence

- multiple output formats

---

# ADR-007 — Repository as Permanent Memory

## Status

Accepted

---

## Context

Engineering knowledge should not depend upon conversation history.

---

## Decision

Repository becomes permanent memory.

Knowledge belongs inside:

- source code

- documentation

- configuration

Conversation history becomes temporary.

---

## Consequences

Benefits:

- AI independence

- easier onboarding

- long-term maintainability

---

# ADR-008 — Multi-Model AI Engineering Workflow

## Status

Accepted

---

## Context

Different AI models exhibit different engineering strengths.

---

## Decision

Use OpenCode + OpenRouter with specialized model delegation.

Representative responsibilities:

architect_sonnet

↓

Architecture

architect_kimi

↓

Architecture Review

coder_glm

↓

Business Implementation

coder_qwen

↓

Feature Implementation

patcher_flash

↓

Localized Maintenance

---

## Consequences

Benefits:

- better architecture

- improved implementation

- higher review quality

---

# ADR-009 — Documentation First

## Status

Accepted

---

## Context

Documentation drift creates engineering debt.

---

## Decision

Treat documentation as part of implementation.

Structural changes require documentation updates.

Implementation is incomplete until documentation is synchronized.

---

## Consequences

Benefits:

- repository clarity

- AI continuity

- reduced onboarding cost

---

# ADR-010 — AI Independence

## Status

Accepted

---

## Context

The repository should outlive any specific AI platform.

---

## Decision

Design engineering processes that are AI-agnostic.

Documentation references:

AI Engineering Assistant

instead of

ChatGPT

Gemini

Claude

---

## Consequences

Benefits:

- future-proof workflow

- vendor independence

- easier migration

---

# ADR-011 — Business Methodology Protection

## Status

Accepted

---

## Context

Engineering improvements should not unintentionally alter research methodology.

---

## Decision

Protect business methodology separately from implementation.

Engineering may improve implementation.

Business rules require explicit approval.

---

## Consequences

Business correctness remains stable while implementation evolves.

---

# ADR-012 — New Engine Admission Policy

## Status

Accepted

---

## Context

Growing repositories naturally accumulate unnecessary engines.

---

## Decision

A new engine may only be introduced when it answers a business question that cannot currently be answered.

File size alone is never sufficient justification.

---

## Consequences

Benefits:

- reduced architectural sprawl

- clearer ownership

- lower maintenance

---

# ADR-013 — Configuration Drift Prevention

## Status

Accepted

---

## Context

Duplicating configuration values inside documentation leads to inconsistency.

---

## Decision

SYSTEM_CONTEXT.md documents configuration philosophy.

Actual configuration values remain exclusively in:

core/config.py

---

## Consequences

Benefits:

- single source of truth

- easier maintenance

- reduced documentation drift

---

# ADR-014 — Knowledge Migration

## Status

Accepted

---

## Context

Important engineering decisions were historically made inside conversations.

---

## Decision

Every significant engineering decision should migrate into:

Repository

↓

Documentation

↓

ADR

↓

Change Log

Conversation history should never become the permanent archive.

---

## Consequences

Repository quality continuously improves.

Historical conversations become progressively less important.

---

# ADR-015 — Long-Term Repository Vision

## Status

Accepted

---

## Context

The long-term objective extends beyond implementing software.

---

## Decision

TABELA should become:

- self-documenting

- architecturally consistent

- AI-independent

- deterministic

- maintainable

Future AI assistants should understand the repository without requiring historical conversations.

---

## Consequences

This ADR defines the ultimate architectural objective for the project.

Every future architectural decision should move the repository closer to this state.

---

# ADR Governance Rules

Every future ADR should include:

- Status
- Context
- Decision
- Consequences
- Alternatives Considered (optional)
- Migration Notes (if applicable)

ADRs should be immutable historical records.

If a decision changes significantly, create a new ADR rather than rewriting history.

The ADR collection represents the architectural memory of TABELA and complements the Change Log by preserving engineering intent.


---

# APPENDIX I — KNOWN TECHNICAL DEBT, ENGINEERING RISKS & IMPROVEMENT FRAMEWORK

> **Purpose**
>
> This appendix records known engineering debt, architectural risks, implementation limitations, and future engineering considerations.
>
> Technical debt is **not** a defect list.
>
> It is a structured inventory of engineering improvements that may be addressed when they provide measurable business or architectural value.

---

# I.1 Technical Debt Philosophy

Technical debt should be managed deliberately.

Not every imperfection should be corrected.

Engineering effort should prioritize improvements that produce meaningful long-term value.

Technical debt should never be reduced simply for cosmetic reasons.

---

# I.2 Technical Debt Categories

Technical debt should be classified into one of the following categories.

## Architecture Debt

Examples:

- unclear ownership

- overlapping responsibilities

- unnecessary coupling

---

## Implementation Debt

Examples:

- duplicated code

- unnecessary complexity

- difficult-to-read logic

---

## Documentation Debt

Examples:

- missing documentation

- outdated documentation

- undocumented architecture

---

## Configuration Debt

Examples:

- duplicated constants

- inconsistent configuration

- hardcoded business values

---

## Data Debt

Examples:

- inconsistent schemas

- undocumented fields

- missing validation

---

## Testing Debt

Examples:

- missing regression coverage

- missing validation scenarios

---

## Operational Debt

Examples:

- manual maintenance

- repetitive operational tasks

- weak observability

---

# I.3 Debt Prioritization

Technical debt should be prioritized according to business impact.

Priority order:

Critical

↓

High

↓

Medium

↓

Low

↓

Cosmetic

Cosmetic improvements should rarely receive priority.

---

# I.4 High-Priority Debt Indicators

Representative indicators include:

- duplicated business methodology

- unclear ownership

- architecture inconsistencies

- documentation drift

- historical compatibility risks

- configuration duplication

- hidden dependencies

These should receive attention before cosmetic improvements.

---

# I.5 Acceptable Technical Debt

Some technical debt is acceptable.

Examples include:

- temporary workarounds

- implementation duplication during migration

- experimental features

provided they are:

documented

↓

understood

↓

scheduled for future evaluation

Undocumented technical debt is significantly more dangerous.

---

# I.6 Engineering Risks

Representative engineering risks include:

- architectural drift

- business methodology drift

- configuration drift

- documentation drift

- schema inconsistency

- hidden coupling

- duplicated ownership

- historical data corruption

Each risk should be monitored continuously.

---

# I.7 Architectural Drift

Architectural drift occurs when implementation gradually diverges from intended architecture.

Typical indicators:

- engines acquiring unrelated responsibilities

- duplicated business logic

- increasing coupling

- unclear ownership

Architectural drift should be corrected early.

---

# I.8 Business Methodology Drift

Business methodology should remain stable.

Engineering improvements should not gradually change:

- scoring

- classification

- transition logic

- EP methodology

Business methodology drift is considered a high-severity engineering risk.

---

# I.9 Documentation Drift

Documentation drift occurs when:

implementation

≠

documentation

Documentation drift should be corrected immediately.

SYSTEM_CONTEXT.md represents one of the primary controls preventing drift.

---

# I.10 Configuration Drift

Configuration drift occurs when:

Business constants exist in multiple locations.

Representative symptoms:

- duplicated thresholds

- duplicated weights

- inconsistent defaults

Configuration should remain centralized.

---

# I.11 Schema Drift

Schema drift occurs when downstream consumers begin assuming undocumented fields.

Representative prevention:

- explicit contracts

- schema validation

- documented ownership

Schema evolution should remain controlled.

---

# I.12 Dependency Risks

Dependency complexity should remain low.

Representative warning signs:

- circular imports

- bidirectional dependencies

- implicit engine communication

- global mutable state

Simple dependency graphs improve maintainability.

---

# I.13 Historical Risks

Historical intelligence is a strategic asset.

Representative risks include:

- registry corruption

- snapshot modification

- historical inconsistency

- transition loss

Historical information should be preserved whenever practical.

---

# I.14 AI Risks

AI-generated implementations may introduce:

- undocumented behaviour

- hidden assumptions

- unnecessary abstraction

- architectural inconsistency

Every AI-generated implementation should receive engineering review.

---

# I.15 Repository Health Indicators

Positive indicators include:

- modular engines

- deterministic execution

- synchronized documentation

- centralized configuration

- explicit ownership

- stable architecture

Negative indicators include:

- duplicated logic

- undocumented behaviour

- growing complexity

---

# I.16 Refactoring Guidelines

Refactoring should occur when it produces measurable improvement.

Appropriate reasons include:

- improved readability

- reduced duplication

- clearer ownership

- simplified architecture

Avoid refactoring purely for stylistic preference.

---

# I.17 Performance Considerations

Performance optimization should follow:

Correctness

↓

Business methodology

↓

Maintainability

↓

Performance

Micro-optimizations rarely justify architectural complexity.

---

# I.18 Monitoring Repository Health

Repository health should periodically evaluate:

Architecture

Configuration

Documentation

Dependencies

Historical Intelligence

Business Methodology

Each area should remain internally consistent.

---

# I.19 Engineering Review Checklist

Periodic engineering reviews should ask:

Has ownership remained clear?

Has coupling increased?

Has documentation drift occurred?

Has business methodology changed?

Has configuration remained centralized?

Has repository complexity increased?

These questions help detect gradual degradation.

---

# I.20 Continuous Improvement Philosophy

Continuous improvement should remain incremental.

Representative sequence:

Observe

↓

Measure

↓

Analyze

↓

Improve

↓

Validate

↓

Document

Improvement should be evidence-driven.

---

# I.21 Future Engineering Goals

Long-term engineering goals include:

- lower maintenance cost

- simpler architecture

- improved documentation

- improved AI onboarding

- stronger validation

- clearer ownership

The objective is continual refinement rather than periodic redesign.

---

# I.22 Success Criteria

Technical debt management is considered successful when:

- debt remains visible

- risks are documented

- improvements are prioritized objectively

- architecture remains stable

- business methodology remains protected

- repository quality improves over time

Technical debt should be actively managed rather than ignored.

The repository should become progressively easier to maintain with every development cycle.


---

# APPENDIX J — LONG-TERM ROADMAP, EVOLUTION PRINCIPLES & FUTURE ENGINEERING DIRECTION

> **Purpose**
>
> This appendix defines the long-term evolution strategy for TABELA.
>
> It intentionally describes **direction**, not implementation plans.
>
> The roadmap should evolve as business objectives evolve.
>
> It should never become a fixed project plan.

---

# J.1 Vision

The long-term vision of TABELA is to become a professional-grade, AI-independent market intelligence platform capable of identifying institutional leadership through objective, explainable, and reproducible analysis.

The platform should continuously improve without requiring architectural redesign.

Knowledge should permanently reside within:

- Repository
- Documentation
- Configuration
- Historical Intelligence

rather than within AI conversations.

---

# J.2 Guiding Principle

Every new capability should answer a question that TABELA cannot currently answer.

If a proposed feature does not increase the platform's ability to answer a new business question, it should be reconsidered.

Engineering effort should always produce measurable analytical value.

---

# J.3 Evolution Strategy

Repository evolution should occur through:

Small Improvements

↓

Incremental Refactoring

↓

Business Capability Expansion

↓

Documentation

↓

Validation

↓

Knowledge Preservation

Avoid large-scale redesign unless architecture genuinely limits future growth.

---

# J.4 Growth Philosophy

Growth should increase:

Business capability

↓

Repository quality

↓

Architectural clarity

↓

Engineering simplicity

Growth should **not** increase:

- unnecessary complexity

- duplicated logic

- undocumented behaviour

- architectural coupling

---

# J.5 Business Evolution

Business methodology should evolve cautiously.

Representative areas that may continue improving include:

- institutional accumulation detection

- leadership transitions

- historical persistence

- theme intelligence

- breadth analysis

- composite scoring

- market context

Methodology changes require explicit approval.

Implementation improvements do not.

---

# J.6 Engineering Evolution

Engineering improvements should focus on:

- simplification

- maintainability

- determinism

- documentation

- modularity

Avoid introducing complexity merely because additional abstraction is possible.

---

# J.7 Historical Intelligence Roadmap

Historical intelligence is expected to become increasingly valuable over time.

Future analytical capabilities should leverage:

- transition history

- persistence

- recovery

- leadership evolution

- historical comparisons

Historical depth should improve analytical confidence.

---

# J.8 Documentation Roadmap

Long-term documentation objectives include:

Complete repository coverage.

Architecture documentation.

Business methodology.

Engineering standards.

Configuration philosophy.

Repository governance.

Documentation should eventually eliminate dependence upon historical conversations.

---

# J.9 AI Collaboration Roadmap

The repository should support collaboration with multiple AI assistants.

Future AI assistants should require:

minimal onboarding

↓

minimal prompting

↓

minimal repository discovery

because engineering knowledge already exists inside documentation.

---

# J.10 Automation Philosophy

Automation should eliminate repetitive engineering work.

Representative candidates include:

- documentation generation

- validation

- repository analysis

- schema verification

- consistency checking

Automation should support engineers rather than replace engineering judgement.

---

# J.11 Repository Maturity Model

Representative maturity progression:

Prototype

↓

Structured Repository

↓

Modular Platform

↓

Historical Intelligence Platform

↓

Self-Documenting Repository

↓

AI-Independent Engineering Platform

TABELA should continue progressing toward the final stages.

---

# J.12 Repository Success Metrics

Long-term repository quality can be evaluated through:

- architectural consistency

- documentation completeness

- deterministic outputs

- business correctness

- maintainability

- onboarding effort

A mature repository should require progressively less explanation.

---

# J.13 Architectural Stability

The following architectural characteristics should remain stable over time.

- Layered Architecture

- Linear Pipeline

- Modular Engines

- Configuration-Driven Behaviour

- Historical Intelligence

- Registry Philosophy

- Documentation Governance

Implementation details may evolve.

These architectural characteristics should remain recognizable.

---

# J.14 Future AI Readiness

The repository should always be prepared for future AI systems.

Future AI assistants should be able to:

Understand architecture.

Understand methodology.

Continue implementation.

Review code.

Update documentation.

without requiring historical conversation context.

SYSTEM_CONTEXT.md is one of the primary mechanisms enabling this capability.

---

# J.15 Continuous Learning

Engineering knowledge should continuously migrate into the repository.

Sources of knowledge include:

Implementation

↓

Architecture Decisions

↓

Documentation

↓

Change Logs

↓

Historical Intelligence

The repository should become progressively smarter even if conversations are lost.

---

# J.16 Engineering Legacy

The objective is not merely to build software.

The objective is to build a repository capable of being understood, maintained, and extended by future engineers and future AI assistants with minimal onboarding effort.

Every engineering contribution should strengthen this legacy.

---

# J.17 Final Engineering Principles

The following principles summarize the long-term direction of TABELA.

1. Preserve business methodology.

2. Preserve architectural consistency.

3. Prefer simplicity.

4. Prefer determinism.

5. Prefer maintainability.

6. Centralize configuration.

7. Document significant decisions.

8. Preserve historical intelligence.

9. Keep business logic modular.

10. Improve repository quality with every engineering session.

---

# J.18 Repository Completion Criteria

TABELA can be considered architecturally mature when:

- business methodology is fully documented

- repository ownership is obvious

- architecture is self-explanatory

- documentation remains synchronized

- historical intelligence is preserved

- configuration is centralized

- future AI assistants require little or no onboarding

Architectural maturity is an ongoing objective rather than a final milestone.

---

# J.19 Final Statement

TABELA is intended to be significantly more than a collection of Python scripts.

It is a long-term engineering platform for market intelligence.

Every architectural decision should support:

- clarity

- reproducibility

- maintainability

- business correctness

- historical continuity

- AI independence

The repository should become progressively easier to understand, extend, and trust.

---

# END OF SYSTEM_CONTEXT.md

This document represents the authoritative operating specification for the TABELA Market Intelligence Platform.

Any future architectural evolution should preserve the principles defined herein unless explicitly superseded through documented architectural decisions.

