# TABELA FUTURE ENHANCEMENTS

## CORE IDENTITY

TABELA is an Institutional Capital Rotation Intelligence Engine.

TABELA is NOT a stock scanner.

TABELA does NOT generate trade signals.

Primary objectives:

* Detect institutional capital accumulation
* Detect institutional capital rotation between themes
* Detect unusual market behavior requiring investigation
* Surface highest quality opportunity universe for discretionary review
* Build proprietary historical market intelligence database
* Learn recurring institutional behavior before future market leaders emerge

Core philosophy:

Capital Flow Detection First
Stock Selection Second
Historical Intelligence Compounds Over Time
Chart Review Always Mandatory
TABELA Surfaces Opportunity — Human Executes Decision

---

# CURRENT STABLE MODULES

Production stable architecture:

* ETF ingestion engine
* Stock ingestion engine
* ETF signal quality filter
* Theme classification engine
* Relative Strength engine
* Composite scoring engine
* Institutional Leaders engine
* Weakness engine (temporary architecture)
* TradingView export engine
* Snapshot persistence engine
* Stock history engine
* Rotation Delta engine
* Historical intelligence engine V0

Protected modules:

* Long engine
* Composite engine
* Snapshot architecture
* Historical logs
* ETF ranking logic

---

# ACTIVE PRIORITIES

## P0 — LIVE OBSERVATION PHASE

Observe 10–20 live sessions.

Validate:

* Theme persistence
* Long quality consistency
* Weakness quality consistency
* Rotation behavior stability
* Historical logging consistency

Rule:

No architecture redesign during observation.

Status:

ACTIVE

---

## P1 — THEME CLASSIFICATION EXPANSION

Goal:

Reduce unknown mapping.

Focus:

* ETF mapping improvement
* Unknown stock reduction
* Better theme coverage

Priority:

HIGH

---

## P2 — THEME STABILITY ENGINE

Goal:

Measure trustworthiness of theme movement.

Metrics:

* Days in leadership
* Theme persistence score
* Leadership consistency score
* Theme acceleration score

Priority:

HIGH

---

# MARKET OPPORTUNITY ENGINE (NEW ARCHITECTURE)

Important principle:

Long and Weakness behavior are NOT symmetrical.

Weakness does NOT automatically imply short opportunity.

TABELA identifies interesting market behavior.

Final trade direction decided only after chart review.

---

## P3A — BEHAVIORAL ANOMALY ENGINE

Goal:

Detect stocks behaving differently than expected.

Examples:

* Strong theme + weak stock
* Strong fundamentals + weak price behavior
* Stock underperforming peers inside strong theme

Interpretation:

Possible:

* Distribution
* Failed breakout
* Temporary weakness
* Rotation
* Opportunity reversal

Final decision:

Chart review mandatory.

Purpose:

Highest priority opportunity discovery engine.

Priority:

CRITICAL

---

## P3B — STRUCTURAL WEAKNESS ENGINE

Goal:

Detect persistently weak stocks inside weak themes.

Conditions:

* Low RS
* Low Composite Score
* Weakening or Lagging Theme

Interpretation:

Possible:

* Continuation downside
* Long term weakness
* Base formation
* Reversal opportunity

Final decision:

Chart review mandatory.

Important:

Structural weakness ≠ automatic short candidate

Priority:

VERY HIGH

---

## P3C — INTERNAL ROTATION ENGINE

Goal:

Detect unusual internal sector divergence.

Example:

Semiconductors strong

MU strong

AMD weak

CRDO weak

Interpretation:

Capital rotating internally.

Possible opportunity emerging.

Priority:

VERY HIGH

---

## P3D — LEADERSHIP DETERIORATION ENGINE

Goal:

Detect former leaders beginning to weaken.

Example:

Composite Score deterioration over multiple sessions.

Example:

95 → 88 → 79 → 67

Interpretation:

Leadership weakening.

Could indicate:

* Distribution
* Consolidation
* Failed breakout
* Temporary weakness

Requires historical intelligence.

Priority:

VERY HIGH

---

# HISTORICAL INTELLIGENCE LAYER

Important rule:

History enhances confidence.

History never creates candidates.

Core system must always function without history.

---

## P4 — STOCK EVOLUTION HISTORY ENGINE

Store daily stock universe history.

Store:

* Ticker
* Last Close
* Avg Volume
* 52 Week High
* 52 Week Low
* Price Position
* Theme
* Theme Class
* RS Rating
* Composite Score
* Sales Score
* Zacks Score

Rules:

Overwrite same trading day.

Purpose:

Future intelligence research.

Status:

ACTIVE

---

## P5 — THEME BREADTH EXPANSION ENGINE

Goal:

Measure internal theme participation.

Questions:

* Is theme strengthening internally?
* Are more stocks joining leadership?
* Is breadth expanding?

Metrics:

* Strong stock count
* Average composite score
* Breadth expansion trend

Priority:

EXTREMELY HIGH

---

## P6 — COMPOSITE VELOCITY ENGINE

Goal:

Measure acceleration and deterioration speed.

Example:

58 → 64 → 72 → 83

Questions:

* Which stocks strengthen fastest?
* Which stocks weaken fastest?
* Which former leaders are deteriorating rapidly?

Priority:

VERY HIGH

---

# FUTURE RESEARCH ENGINES

## P7 — QUIET ACCUMULATION ENGINE

Detect silent accumulation before obvious breakout.

Priority:

EXTREMELY HIGH

---

## P8 — PRE BREAKOUT FINGERPRINT ENGINE

Study historical leaders.

Examples:

* ARM
* NVDA
* PLTR
* APP

Question:

What recurring behavior appears before explosive moves?

Priority:

MAXIMUM

---

## P9 — EMERGING MONSTER DETECTOR

Detect future explosive winners early.

Focus:

Acceleration before breakout.

Priority:

MAXIMUM

---

## P10 — BEHAVIOR CHANGE EARLY WARNING ENGINE

Goal:

Detect major behavioral change before obvious market recognition.

Focus:

* Former leaders weakening
* Unexpected relative weakness
* Rotation divergence

Priority:

EXTREMELY HIGH

---

## P11 — ETF LEADERSHIP PREDICTIVE ENGINE

Question:

Can stock behavior predict ETF leadership before ETF ranking changes?

Priority:

VERY HIGH

---

## P12 — MARKET REGIME PREDICTOR

Detect:

* Risk on
* Risk off
* Leadership narrowing
* Structural weakness
* Breadth deterioration

Priority:

HIGH

---

## P13 — HISTORICAL INSTITUTIONAL INTELLIGENCE ENGINE

Final intelligence brain.

Learn:

* recurring accumulation patterns
* recurring weakness patterns
* recurring anomaly patterns
* recurring breakout fingerprints
* recurring rotation behavior

Ultimate objective:

Understand institutional behavior before market recognizes it.

Priority:

ULTIMATE DESTINATION

---

# PERMANENT ARCHITECTURE RULES

Rule 1

TABELA never generates trade signals.

Rule 2

Final execution always requires discretionary chart review.

Rule 3

System must function without history.

Rule 4

History enhances ranking and confidence.

History never creates candidates.

Rule 5

Protect Long Engine aggressively.

Do not modify casually.

Rule 6

TABELA detects opportunity.

Human decides trade direction.

Rule 7

Recent market behavior always carries more weight than historical behavior.

Rule 8

Automation first.

No manual logging.

Rule 9

Capital flow detection first.

Stock selection second.

Rule 10

Never redesign stable architecture without strong reason.





# ADDITIONAL FUTURE ENHANCEMENTS (POST ANOMALY ENGINE REVIEW)

## LESSONS LEARNED — ANOMALY ENGINE V1 EXPERIMENT

Behavioral Anomaly Engine V1 experiment was intentionally paused.

Key learning:

Single day snapshot data from ETF.csv and stocks.csv is insufficient for reliable anomaly detection.

Attempting anomaly detection using only present-day weakness created low quality outputs.

Conclusion:

Do not force advanced market behavior detection on insufficient data.

Future anomaly intelligence should only be built when sufficient historical data exists.

Status:

ON HOLD

---

## P14 — BEHAVIORAL ANOMALY ENGINE V2

Goal:

Detect unusual behavior in institutionally relevant stocks.

Important rule:

Do NOT scan entire stock universe.

Focus only on historically important stocks.

Possible anomaly signals:

* Leadership deterioration
* Relative strength decay
* Composite score deterioration
* Sudden exit from leadership universe
* Internal theme divergence

Data dependency:

Requires minimum 5–10 days historical stock snapshots.

Priority:

HIGH (Future)

Status:

WAITING FOR SUFFICIENT HISTORY

---

## P15 — LEADERSHIP DETERIORATION ENGINE

Goal:

Detect strong stocks beginning to lose leadership characteristics.

Example:

Composite score deterioration across multiple sessions.

Example pattern:

95 → 89 → 81 → 72 → 61

Signals:

* Institutional distribution
* Failed breakout
* Momentum exhaustion
* Leadership weakening

Output example:

HIGH ATTENTION WATCHLIST

Purpose:

Surface high quality stocks requiring immediate chart review.

Priority:

VERY HIGH

---

## P16 — RELATIVE STRENGTH DECAY ENGINE

Goal:

Track gradual deterioration in relative strength over multiple sessions.

Example:

RS Rating

96 → 91 → 83 → 74 → 66

Purpose:

Detect weakening momentum before market consensus recognizes weakness.

Signals:

* Early distribution
* Capital rotation
* Institutional exit behavior

Priority:

VERY HIGH

---

## P17 — LEADER EXIT DETECTION ENGINE

Goal:

Track stocks repeatedly appearing in Institutional Leaders universe.

Detect sudden disappearance.

Example:

PLTR appears in leadership universe for 7 consecutive sessions.

Day 8 disappears.

Possible interpretation:

* Distribution
* Failed breakout
* Leadership transfer
* Temporary weakness

Purpose:

Identify important stocks changing character.

Priority:

EXTREMELY HIGH

---

## P18 — INTERNAL THEME DIVERGENCE ENGINE

Goal:

Detect divergence inside strong themes.

Example:

Semiconductors remains leading theme.

NVDA stable.

MU stable.

AMD weakening consistently.

Possible interpretation:

Institutional rotation happening inside theme.

Purpose:

Detect non-consensus internal capital movement.

Priority:

HIGH

---

## PERMANENT ARCHITECTURE RULE

Do not force advanced intelligence layers on insufficient data.

Single day snapshot data supports:

* Capital flow detection
* Theme rotation detection
* Institutional leader detection
* Weakness detection

Single day snapshot data does NOT reliably support:

* Behavioral anomaly detection
* Distribution detection
* Leadership deterioration detection
* Character change detection

Advanced intelligence layers must be supported by sufficient historical data.

Architecture principle:

Data capability defines intelligence capability.

Never force philosophy beyond available data.
