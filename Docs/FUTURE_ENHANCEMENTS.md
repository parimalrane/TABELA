# TABELA FUTURE ROADMAP

## CORE IDENTITY

TABELA is an Institutional Capital Rotation Intelligence Engine.

Primary purpose:

* Detect institutional capital flow
* Identify strongest themes for LONG trades
* Identify weakest themes for SHORT trades
* Track capital rotation between themes over time
* Build long-term historical market intelligence database

Important principle:

Capital Rotation Detection First
Stock Selection Second

---

# CURRENT STATUS

Stable Production Architecture

Modules completed:

* ETF ingestion engine
* Stock ingestion engine
* ETF signal quality filter
* Theme classification engine
* Relative Strength engine
* Composite scoring engine
* Long candidate engine
* Short candidate engine
* TradingView export engine
* Snapshot history engine
* Rotation Delta Report
* Stock History Engine

Current phase:

P0 Observation Phase

No unnecessary architecture modifications.

---

# ACTIVE PRIORITY ROADMAP

## P0 — LIVE OBSERVATION PHASE

Objective:

Observe 5–10 live market sessions.

Focus:

* Theme persistence
* Long candidate stability
* Short candidate quality
* Rotation report quality
* Unexpected ranking behavior

Rules:

No architecture redesign.

---

## P1 — THEME CLASSIFICATION EXPANSION

Objective:

Reduce Unknown stock classification.

Goals:

* Improve ETF to stock mapping
* Reduce unclassified leaders
* Improve theme coverage

Priority:

HIGH

Status:

Pending

---

## P2 — THEME STABILITY VALIDATION ENGINE

Objective:

Measure trustworthiness of theme movement.

Questions:

* Is leadership persistent?
* Is strength temporary?
* Is weakness structural?
* Is theme movement random noise?

Future metrics:

* Days in leading themes
* Days in weakening themes
* Leadership persistence score

Priority:

HIGH

Status:

Pending

---

## P3 — SHORT ENGINE QUALITY REVIEW

Objective:

Improve short candidate reliability.

Research:

* False weakness detection
* Temporary pullback detection
* Mean reversion contamination

Questions:

* Are short candidates structurally weak?
* Are short candidates just temporarily weak?

Priority:

HIGH

Status:

Pending

---

## P4 — ETF SIGNAL QUALITY AUDIT V2

Objective:

Improve ETF quality.

Possible improvements:

* Remove synthetic ETFs
* Remove duplicate ETF exposure
* Improve liquidity filter
* Improve ETF quality scoring

Priority:

MEDIUM

Status:

Pending

---

## P5 — RS FORMULA REVIEW

Objective:

Review current Relative Strength calculation logic.

Questions:

* Does recent market behavior carry enough weight?
* Does RS detect true leadership properly?

Rules:

Do NOT modify unless enough live evidence exists.

Priority:

MEDIUM

Status:

Delayed

---

# NEW FUTURE INTELLIGENCE LAYER

## P6 — STOCK EVOLUTION HISTORY ENGINE

Objective:

Store full stock universe history daily.

Purpose:

Track changes before stocks become obvious leaders.

Daily overwrite allowed.

Store:

* Ticker
* Last Close
* Avg Volume
* 52 Week High
* 52 Week Low
* Price Position in 52 Week Range
* Theme
* Theme Class
* RS Rating
* Composite Score
* Sales Score
* Zacks Score

Purpose:

Historical research.

Priority:

HIGH

Status:

Newly added

---

## P7 — COMPOSITE SCORE VELOCITY ENGINE

Objective:

Measure acceleration of stock strength.

Example:

ARM

Day 1 → 58
Day 2 → 63
Day 3 → 72
Day 4 → 81

Questions:

* Which stocks are strengthening fastest?
* Which stocks are deteriorating fastest?

Future metrics:

* 5 day score change
* 10 day score change
* Score acceleration rate

Priority:

HIGH

Status:

Future

---

## P8 — FIRST APPEARANCE ENGINE

Objective:

Track when stocks first enter institutional leadership.

Questions:

* Which stocks recently entered top candidates?
* Which stocks are fresh leaders?

Metrics:

* First appearance date
* Days since first appearance
* Rank progression

Example:

Day 1 → Rank 42
Day 4 → Rank 18
Day 7 → Rank 4

Priority:

HIGH

Status:

Future

---

## P9 — QUIET ACCUMULATION ENGINE

Objective:

Detect silent institutional accumulation before breakout.

Example:

RS Rating

72 → 76 → 81 → 89 → 94

Without stock entering top candidates.

Questions:

* Which stocks improve consistently?
* Which stocks are strengthening quietly?

Priority:

HIGH

Status:

Future

---

## P10 — THEME BREADTH EXPANSION ENGINE

Objective:

Measure internal strength inside themes.

Example:

Semiconductors

Day 1 → 4 strong stocks
Day 10 → 9 strong stocks
Day 20 → 16 strong stocks

Questions:

* Is theme internally strengthening?
* Is breadth expanding before leadership becomes obvious?

Metrics:

* Strong stock count
* Average composite score by theme
* Theme breadth trend

Priority:

VERY HIGH

Status:

Future

---

## P11 — PRE BREAKOUT FINGERPRINT ENGINE

Objective:

Learn what happens before explosive moves.

Research examples:

ARM
NVDA
PLTR
CRDO

Questions:

What changes happened 10–20 days before explosive breakout?

Possible signals:

* Composite score rising continuously
* RS above 90
* Price position near 52 week high
* Theme entering leadership
* First appearance in long candidates

Goal:

Detect tomorrow’s explosive stocks.

Priority:

VERY HIGH

Status:

Long term research

---

## P12 — HISTORICAL INSTITUTIONAL INTELLIGENCE ENGINE

Objective:

Build long term market intelligence database.

Questions:

* Which themes lead repeatedly?
* Which sectors consistently weaken?
* Which market structures repeat over time?
* Which stocks repeatedly attract institutions?

Purpose:

Long term institutional pattern recognition.

Priority:

VERY HIGH

Status:

Delayed until enough historical data exists

---

# ENGINEERING RULES

Do not redesign architecture casually.

Historical logs are critical.

Recent market behavior always carries more weight than historical behavior.

Protect stable modules aggressively.

Long Engine is protected and should not be modified without strong reason.

Snapshot JSON stores raw market state only.

Rotation Delta Report remains diagnostic only.

Detect institutional capital flow first.

Stock selection is secondary.

Avoid feature creep.

Never optimize without observing enough live market data.

Automation first.

No manual logging.

---

# LONG TERM VISION

Current TABELA

Institutional Capital Rotation Engine

Future TABELA

Institutional Capital Intelligence Platform

Possible future capability

Detect institutional accumulation BEFORE explosive stock breakouts.

Ultimate goal

Understand what institutions are accumulating before the market recognizes it.
