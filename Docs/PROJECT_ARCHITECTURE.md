# ThemePulse Project Architecture

**Version 3.1** | Stable Production Architecture | ~90% Complete

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Data Flow](#data-flow)
3. [Core Modules](#core-modules)
4. [Scoring Algorithms](#scoring-algorithms)
5. [Theme Classification](#theme-classification)
6. [Filtering Logic](#filtering-logic)
7. [Configuration Parameters](#configuration-parameters)
8. [Version History](#version-history)
9. [Architecture Evolution](#architecture-evolution)
10. [Future Roadmap](#future-roadmap)

---

## System Overview

### Purpose
ThemePulse detects **institutional capital rotation** by analyzing which market themes are gaining strength through ETF inflows, then identifies the highest-quality stocks within those themes.

### Core Principle
**Institutional narratives drive stock selection, not traditional sectors.**

```
Example: NVDA is classified as "AI Accelerators" (not "semiconductors") because 
institutional money flows through AI-focused ETFs, not semiconductor ETFs.
```

### Key Statistics
- **ETF Universe:** 5,000+ → 2,500 filtered (bonds/inverse/leveraged/country removed)
- **Stock Universe:** ~5,000 stocks analyzed daily
- **Manual Narratives:** 100+ expert-curated institutional theme mappings
- **Scoring Factors:** 5 (Momentum 40%, Theme 25%, Sales 20%, Zacks 10%, Margin 5%)
- **Execution Time:** <30 seconds per run
- **Historical Database:** Daily JSON snapshots in history/ folder

---

## Data Flow

### Daily Execution Pipeline (10 Steps)

```
┌────────────────────────────────────────────────────────────────┐
│               INPUTS: stocks.csv + ETF.csv                     │
│       (Updated daily from Zacks; 5000+ ETFs, 5000+ stocks)     │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 1: ETF FILTERING & PROCESSING                             │
│ ────────────────────────────────────────────────────────────   │
│ • Load all ETFs from ETF.csv                                   │
│ • Filter out non-equity products:                              │
│   - Bonds, Treasury products, Currency, Commodities            │
│   - Inverse ETFs, Leveraged ETFs (2x, 3x)                      │
│   - Country/Geographic ETFs, Factor ETFs                       │
│   - Income/Dividend-specific ETFs, Strategy wrappers           │
│   - Min Market Value threshold: $200M                          │
│ • Result: ~2,500 equity-focused ETFs                           │
│ Module: etf_filter.py, etf_engine.py                           │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 2: THEME EXTRACTION                                       │
│ ────────────────────────────────────────────────────────────   │
│ • Parse ETF investment strategy text                           │
│ • Extract Sector/Theme/Subtheme taxonomy                       │
│ • Normalize theme names (e.g., "Healthcare" → "Medical")       │
│ • Identify canonical themes (AI, Cloud, Semiconductors, etc.)  │
│ Module: theme_parser.py, theme_dictionary.py                   │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 3: ETF MOMENTUM CALCULATION                               │
│ ────────────────────────────────────────────────────────────   │
│ • Calculate RS_Raw for each ETF (weighted performance metrics) │
│ • Weight recent performance higher (momentum recency)          │
│ • Identify relative strength leaders and laggards              │
│ • Result: ETF_RS_Raw, ETF_RS_Rating (percentile)               │
│ Module: scoring_engine.py                                      │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 4: THEME CLASSIFICATION                                   │
│ ────────────────────────────────────────────────────────────   │
│ • Group ETFs by theme                                          │
│ • Calculate average RS_Raw per theme                           │
│ • Classify themes into quartiles:                              │
│   - Leading:   Top 25%    (↑↑ strong momentum)                 │
│   - Emerging:  25-50%     (↑ gaining momentum)                 │
│   - Weakening: 50-75%     (↓ losing momentum)                  │
│   - Lagging:   Bottom 25% (↓↓ weak momentum)                   │
│ • Calculate Theme_Score (based on institutional ETF strength)  │
│ Result: Theme classification + strength metrics for all themes │
│ Module: etf_engine.py, config.py                               │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 5: STOCK-TO-THEME MAPPING                                 │
│ ────────────────────────────────────────────────────────────   │
│ For each stock, determine institutional narrative:             │
│                                                                 │
│ Priority 1: Manual Institutional Override                      │
│   • Check company_theme_engine.py (~100+ high-conviction)      │
│   • Example: NVDA → "AI Accelerators"                          │
│   • Used for stocks with clear institutional narratives        │
│                                                                 │
│ Priority 2: Automated Sector Detection                         │
│   • Match stock industry/sector to theme keywords              │
│   • Example: Semiconductor company → "Semiconductors" theme    │
│   • Module: stock_mapper.py                                    │
│                                                                 │
│ Priority 3: Narrative Translation                              │
│   • Convert internal company narrative to ETF theme name       │
│   • Example: "AI Platform" → "Artificial Intelligence"         │
│   • Module: theme_translation_engine.py                        │
│                                                                 │
│ Result: Each stock assigned to 1 institutional theme           │
│ Module: company_theme_engine.py, stock_mapper.py,              │
│         theme_translation_engine.py, theme_hierarchy.py        │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 6: INDIVIDUAL STOCK SCORING                               │
│ ────────────────────────────────────────────────────────────   │
│ Calculate 5 independent scores for each stock:                 │
│                                                                 │
│ Score 1: RS (Relative Strength)                                │
│   • Input: Daily RS value from stocks.csv                      │
│   • Raw value: 0-100                                           │
│   • Percentile ranking: 0-100 (RS_Rating)                      │
│                                                                 │
│ Score 2: Sales Growth Score                                    │
│   • Input: Sales growth rate from stocks.csv                   │
│   • Normalized to 0-100 scale                                  │
│                                                                 │
│ Score 3: Zacks Rank Score                                      │
│   • Input: Zacks analyst rating (1-5)                          │
│   • Conversion: 1→100, 2→80, 3→60, 4→40, 5→20                 │
│                                                                 │
│ Score 4: Margin Score                                          │
│   • Input: Profit margin from stocks.csv                       │
│   • Normalized to 0-100 scale                                  │
│                                                                 │
│ Score 5: Theme Score                                           │
│   • Inherited from assigned theme classification:              │
│   • Leading theme → 100 points                                 │
│   • Emerging theme → 75 points                                 │
│   • Weakening theme → 40 points                                │
│   • Lagging theme → 20 points                                  │
│   • Unclassified → 0 points (exception: exceptional RS)        │
│                                                                 │
│ Module: scoring_engine.py                                      │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 7: COMPOSITE SCORE CALCULATION                            │
│ ────────────────────────────────────────────────────────────   │
│ Weighted combination of 5 scores:                              │
│                                                                 │
│ Composite = (0.40 × RS_Rating) +                               │
│             (0.25 × Theme_Score) +                             │
│             (0.20 × Sales_Score) +                             │
│             (0.10 × Zacks_Score) +                             │
│             (0.05 × Margin_Score)                              │
│                                                                 │
│ Result: Final composite score (0-100) per stock                │
│ Module: composite_engine.py                                    │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 8: WATCHLIST CANDIDATE SELECTION                          │
│ ────────────────────────────────────────────────────────────   │
│ Three parallel candidate engines:                              │
│                                                                 │
│ A) LONG CANDIDATES (Long watchlist)                            │
│    Filters (must pass ALL):                                    │
│    • Composite Score ≥ 80                                      │
│    • RS Rating ≥ 80                                            │
│    • Sales Score ≥ 60                                          │
│    • Zacks Score ≥ 60                                          │
│    • Theme: Leading OR Emerging OR "Unclassified Leader"       │
│    Rationale: Strong fundamentals + strong theme              │
│    Module: watchlist_engine.py                                 │
│                                                                 │
│ B) SHORT CANDIDATES (Short watchlist)                          │
│    Filters (must pass ALL):                                    │
│    • Composite Score ≤ 45                                      │
│    • RS Rating ≤ 40                                            │
│    • (Sales Score ≤ 40 OR Zacks Score ≤ 40)                    │
│    Rationale: Weak fundamentals + weak momentum               │
│    Module: short_engine.py                                     │
│                                                                 │
│ C) INSTITUTIONAL LEADERS (Top 20 thematic stocks)              │
│    • Filter: Top 20 stocks from Leading/Emerging themes        │
│    • Rationale: Pure institutional flow plays                  │
│    • Module: institutional_leaders_engine.py                   │
│                                                                 │
│ Result: Three candidate lists to be merged                     │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 9: THEME BREADTH ANALYSIS                                 │
│ ────────────────────────────────────────────────────────────   │
│ Calculate institutional conviction per theme:                  │
│                                                                 │
│ • For each theme, count % of stocks with Composite ≥ 80       │
│ • Leading themes: 70-90% of stocks above threshold             │
│ • Emerging themes: 40-70% of stocks above threshold            │
│ • Weakening themes: 20-40% of stocks above threshold           │
│ • Lagging themes: <20% of stocks above threshold               │
│                                                                 │
│ Insight: Breadth indicates theme sustainability                │
│ Module: breadth_engine.py                                      │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│ STEP 10: OUTPUT REPORTING & SNAPSHOT GENERATION                │
│ ────────────────────────────────────────────────────────────   │
│ Generate multi-part output:                                    │
│                                                                 │
│ Report Section 1: Market Rotation Summary                      │
│   • Leading themes + average theme score                       │
│   • Emerging themes + average theme score                      │
│   • Weakening themes                                           │
│   • Lagging themes                                             │
│                                                                 │
│ Report Section 2: Theme Breadth Analysis                       │
│   • % of strong stocks (>80 composite) per leading theme       │
│   • Indicator of theme conviction & sustainability             │
│                                                                 │
│ Report Section 3: Top 40 Long Candidates                       │
│   • Sorted by composite score (descending)                     │
│   • Includes: Ticker, Score, Theme, Theme Score, Sales, Zacks │
│   • Asterisk (*) = Institutional flow only (not fundamental)   │
│                                                                 │
│ Report Section 4: Top 20 Short Candidates                      │
│   • Sorted by RS rating (ascending)                            │
│   • Includes: Ticker, Score, Theme, RS Rating                  │
│                                                                 │
│ JSON Snapshot: Saved to history/{YYYY-MM-DD}.json              │
│   • Leading/Emerging/Weakening/Lagging themes                  │
│   • Top 20 long candidates + scores                            │
│   • Top 20 short candidates + scores                           │
│   • Theme breadth percentages                                  │
│   • Timestamp & execution metadata                             │
│                                                                 │
│ Module: snapshot_engine.py, main.py                            │
└────────────────────────────────────────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────────────┐
│                    EXECUTION COMPLETE                          │
│             Daily market intelligence generated                │
└────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. **etf_filter.py** — ETF Universe Curation
**Responsibility:** Filter 5,000+ raw ETFs → 2,500 equity-focused themes

**Logic:**
- Exclude all bonds, treasuries, currencies, commodities
- Exclude inverse and leveraged products (2x, 3x, leveraged)
- Exclude country/geographic ETFs
- Exclude factor-focused ETFs (value, growth, dividend)
- Exclude strategy wrapper ETFs
- Min market value threshold: $200M
- Result: Pure equity thematic ETFs

**Key Variables:**
- `etf_list` — All ETFs after filtering
- `theme_assignments` — ETF-to-theme mapping

---

### 2. **etf_engine.py** — ETF Processing & Theme Classification
**Responsibility:** Calculate ETF strength metrics and classify themes

**Inputs:** Filtered ETFs + ETF performance data
**Outputs:** Theme classifications (Leading/Emerging/Weakening/Lagging)

**Algorithm:**
1. Calculate RS_Raw for each ETF (momentum)
2. Group by theme; average RS_Raw
3. Rank themes by RS_Raw
4. Assign quartile classifications

**Key Variables:**
- `etf_master` — All ETFs with RS calculations
- `theme_classifications` — Dict of theme → class
- `theme_scores` — Dict of theme → average RS

---

### 3. **theme_parser.py** — ETF Strategy Text Parsing
**Responsibility:** Extract institutional themes from ETF descriptions

**Example:**
```
Input:  "iShares Core S&P 500 ETF - Semiconductor focus with AI exposure"
Output: Theme = "Semiconductors", Sub-theme = "AI Accelerators"
```

**Logic:**
- Parse ETF strategy/description text
- Match against theme keyword dictionary
- Extract canonical theme assignment
- Handle multi-theme ETFs (primary theme only)

---

### 4. **stock_mapper.py** — Automated Stock Classification
**Responsibility:** Map stocks to themes using industry/sector keywords

**Logic:**
- Read industry/sector from stocks.csv
- Match against keyword dictionary
- Assign most likely theme
- Fallback: "Unclassified" if no match

**Example Mappings:**
- Industry: "Semiconductor" → Theme: "Semiconductors"
- Sector: "Information Technology" + keyword "AI" → Theme: "AI Accelerators"

---

### 5. **company_theme_engine.py** — Manual Institutional Narratives
**Responsibility:** Expert-curated stock-to-theme mappings

**~100+ High-Conviction Overrides:**
```python
COMPANY_THEME_MAPPING = {
    'NVDA': 'AI Accelerators',
    'META': 'AI Platform',
    'TSLA': 'Autonomous Driving AI',
    'PLTR': 'Defense Software',
    'SNOW': 'Cloud Infrastructure',
    'RKLB': 'Space Infrastructure',
    ...
}
```

**Rationale:** These reflect real institutional narratives, not traditional sectors

---

### 6. **theme_translation_engine.py** — Narrative Conversion
**Responsibility:** Translate internal stock narratives to ETF theme names

**Example:**
- Internal: "AI Platform" → ETF Theme: "Artificial Intelligence"
- Internal: "Cloud Infrastructure" → ETF Theme: "Cloud Computing"

**Purpose:** Consistency between stock classification and available ETF themes

---

### 7. **scoring_engine.py** — Multi-Factor Scoring
**Responsibility:** Calculate 5 independent scores for each stock

**Score 1: RS (Relative Strength)**
- Input: RS from stocks.csv (0-100)
- Output: RS_Raw + RS_Rating (percentile: 0-100)

**Score 2: Sales Score**
- Input: Sales growth rate
- Formula: Normalize to 0-100 scale
- Threshold considerations: Growth context-dependent

**Score 3: Zacks Rank Score**
- Input: Zacks rating (1-5 scale)
- Mapping: 1→100, 2→80, 3→60, 4→40, 5→20
- Rationale: Analyst consensus bullishness

**Score 4: Margin Score**
- Input: Profit margin from stocks.csv
- Formula: Normalize to 0-100 scale
- Context: Industry-relative profitability

**Score 5: Theme Score**
- Input: Theme classification (Leading/Emerging/Weakening/Lagging)
- Mapping:
  - Leading → 100 points
  - Emerging → 75 points
  - Weakening → 40 points
  - Lagging → 20 points
  - Unclassified → 0 points

---

### 8. **composite_engine.py** — Weighted Score Aggregation
**Responsibility:** Combine 5 scores into single composite ranking

**Formula:**
```
Composite = (0.40 × RS_Rating) + 
            (0.25 × Theme_Score) + 
            (0.20 × Sales_Score) + 
            (0.10 × Zacks_Score) + 
            (0.05 × Margin_Score)

Range: 0-100
```

**Weight Rationale:**
- 40% RS: Momentum drives stock performance
- 25% Theme: Institutional narrative direction
- 20% Sales: Revenue growth indicates sustainability
- 10% Zacks: Analyst consensus validation
- 5% Margin: Profitability quality check

---

### 9. **watchlist_engine.py** — Long Candidate Selection
**Responsibility:** Filter long watchlist from highest-quality opportunities

**Filters (ALL must pass):**
1. Composite Score ≥ 80
2. RS Rating ≥ 80
3. Sales Score ≥ 60
4. Zacks Score ≥ 60
5. Theme: Leading OR Emerging OR "Unclassified Leader"

**Rationale:** Only stocks with strong fundamentals + strong theme assignment

**Output:** Top 40 long candidates (sorted by composite score)

---

### 10. **short_engine.py** — Short Candidate Selection
**Responsibility:** Identify weak candidates for short positions

**Filters (ALL must pass):**
1. Composite Score ≤ 45
2. RS Rating ≤ 40
3. (Sales Score ≤ 40 OR Zacks Score ≤ 40)

**Rationale:** Technical weakness + fundamental weakness

**Output:** Top 20 short candidates (sorted by RS rating, ascending)

---

### 11. **institutional_leaders_engine.py** — Pure Narrative Plays
**Responsibility:** Top 20 stocks from strongest themes (institutional flow only)

**Logic:**
1. Filter to Leading + Emerging themes only
2. Select top 20 by composite score from each theme
3. Combine and deduplicate
4. Result: Top 20 "institutional conviction" plays

---

### 12. **breadth_engine.py** — Theme Participation Analysis
**Responsibility:** Calculate what % of stocks in each theme are strong

**Logic:**
```
For each theme:
  count_strong = # of stocks with Composite ≥ 80
  total = # of stocks in theme
  breadth_% = (count_strong / total) × 100
```

**Interpretation:**
- **Leading themes:** 70-90% breadth (broad institutional consensus)
- **Emerging themes:** 40-70% breadth (building conviction)
- **Weakening themes:** 20-40% breadth (losing conviction)
- **Lagging themes:** <20% breadth (institutional avoidance)

**Use:** Detect theme sustainability and conviction depth

---

### 13. **snapshot_engine.py** — Historical Database
**Responsibility:** Save daily market state to JSON for historical analysis

**JSON Structure:**
```json
{
  "date": "2026-06-19",
  "timestamp": "2026-06-19T14:30:00",
  "leading_themes": ["AI Accelerators", "Cloud Infrastructure"],
  "emerging_themes": ["Autonomous Driving", "Defense Software"],
  "weakening_themes": ["Traditional Retail"],
  "lagging_themes": ["Financial Services"],
  "theme_breadth": {
    "AI Accelerators": 78,
    "Cloud Infrastructure": 62
  },
  "top_20_longs": [
    {"ticker": "NVDA", "score": 94, "theme": "AI Accelerators"},
    ...
  ],
  "top_20_shorts": [
    {"ticker": "RETAIL", "score": 18, "theme": "Traditional Retail"},
    ...
  ]
}
```

**Storage:** `history/{YYYY-MM-DD}.json`

---

### 14. **rotation_engine.py** — Historical Rotation Analysis
**Responsibility:** Compare daily snapshots to detect theme rotation

**Example Output:**
```
Software:       Leading → Weakening (Distribution)
Biotech:        Lagging → Emerging (Accumulation)
Semiconductors: Leading → Emerging (Leadership rotation)
```

**Use:** Multi-day trend detection and institutional flow tracking

---

### 15. **config.py** — Configuration Parameters
**Responsibility:** Central configuration for all filtering/scoring parameters

**Key Parameters:**
```python
# Scoring weights
COMPOSITE_WEIGHTS = {
    'rs_rating': 0.40,
    'theme_score': 0.25,
    'sales_score': 0.20,
    'zacks_score': 0.10,
    'margin_score': 0.05
}

# Long watchlist filters
LONG_MIN_COMPOSITE = 80
LONG_MIN_RS_RATING = 80
LONG_MIN_SALES = 60
LONG_MIN_ZACKS = 60

# Short watchlist filters
SHORT_MAX_COMPOSITE = 45
SHORT_MAX_RS_RATING = 40
SHORT_MAX_FUNDAMENTAL = 40

# ETF filters
ETF_MIN_MARKET_VALUE = 200_000_000  # $200M
PERCENTILE_BREAKPOINTS = [25, 50, 75]  # quartiles
```

---

## Theme Classification

### Classification System

Themes are ranked into **4 tiers** based on average ETF momentum:

| Classification | Percentile | Characteristics | Investor Action |
|---|---|---|---|
| **Leading** | Top 25% | Strong uptrend, institutional inflows | **BUY** |
| **Emerging** | 25-50% | Building momentum, emerging conviction | **ACCUMULATE** |
| **Weakening** | 50-75% | Slowing momentum, distribution phase | **REDUCE** |
| **Lagging** | Bottom 25% | Downtrend, institutional outflows | **AVOID/SHORT** |

### Theme Score Mapping

When assigned to stocks:

| Theme Class | Stock Score | Meaning |
|---|---|---|
| Leading | 100 | Strong institutional tailwind |
| Emerging | 75 | Emerging institutional support |
| Weakening | 40 | Institutional headwind |
| Lagging | 20 | Institutional opposition |
| Unclassified | 0 | No theme assignment |

---

## Filtering Logic

### ETF Universe Filtering

**Starting Point:** 5,000+ ETFs from Zacks export

**Automatic Exclusions:**

```
Category          Examples              Reason
──────────────────────────────────────────────────────
Bonds             AGG, BND, TLT          Non-equity
Treasuries        SHY, IEF, TLT          Government securities
Currency          FXE, FXY, EWZ          Not equity themes
Commodities       GLD, DBC, USO          Commodity not equity
Inverse ETFs      SDS, PSQ, EUO          Inverse exposure
Leveraged ETFs    SSO, QLD, UPRO         Artificial leverage
Country ETFs      EWJ, EWG, FXI          Geographic, not thematic
Factor ETFs       RPV, IVE, VTV          Isolated factors
Income/Dividend   SCHD, VYM, DGRO       Dividend-focused
Strategy Wrappers QAI, PSLV, GLU        Strategy overlays
```

**Result:** ~2,500 pure equity thematic ETFs

**Min Market Value:** $200M (liquidity filter)

### Long Watchlist Filtering

**Candidate must pass ALL:**

| Filter | Threshold | Reason |
|--------|-----------|--------|
| Composite Score | ≥ 80 | Strong overall quality |
| RS Rating | ≥ 80 | Strong momentum |
| Sales Growth Score | ≥ 60 | Revenue acceleration |
| Zacks Rank Score | ≥ 60 | Analyst consensus positive |
| Theme Classification | Leading OR Emerging | Institutional tailwind |

**Exception:** "Unclassified Leaders" (exceptional RS despite no theme)

**Result:** ~40 high-conviction long candidates

### Short Watchlist Filtering

**Candidate must pass ALL:**

| Filter | Threshold | Reason |
|--------|-----------|--------|
| Composite Score | ≤ 45 | Overall weakness |
| RS Rating | ≤ 40 | Poor momentum |
| Fundamental Weakness | Sales ≤ 40 OR Zacks ≤ 40 | Deteriorating fundamentals |

**Result:** ~20 decline candidates

---

## Configuration Parameters

### Scoring Weights (config.py)

```python
COMPOSITE_WEIGHTS = {
    'rs_rating': 0.40,          # 40% momentum
    'theme_score': 0.25,        # 25% institutional narrative
    'sales_score': 0.20,        # 20% revenue growth
    'zacks_score': 0.10,        # 10% analyst consensus
    'margin_score': 0.05        # 5% profitability
}
```

### Theme Percentile Breakpoints

```python
LEADING_PERCENTILE = 25      # Top quartile
EMERGING_PERCENTILE = 50     # Upper-middle
WEAKENING_PERCENTILE = 75    # Lower-middle
LAGGING_PERCENTILE = 100     # Bottom quartile
```

### ETF Filtering Parameters

```python
ETF_MIN_MARKET_VALUE = 200_000_000  # $200M minimum
EXCLUDE_KEYWORDS = [
    'bond', 'treasury', 'inverse', 'leveraged', '2x', '3x',
    'country', 'factor', 'alpha', 'beta', 'dividend', 'income',
    'currency', 'commodity'
]
```

### Long Watchlist Thresholds

```python
LONG_MIN_COMPOSITE = 80
LONG_MIN_RS_RATING = 80
LONG_MIN_SALES = 60
LONG_MIN_ZACKS = 60
LONG_THEME_CLASSES = ['Leading', 'Emerging', 'Unclassified Leader']
LONG_CANDIDATE_COUNT = 40
```

### Short Watchlist Thresholds

```python
SHORT_MAX_COMPOSITE = 45
SHORT_MAX_RS_RATING = 40
SHORT_MAX_SALES_OR_ZACKS = 40  # Either condition sufficient
SHORT_CANDIDATE_COUNT = 20
```

---

## Version History

### Version 1.0 — Initial Architecture (DEPRECATED)
**Approach:** Manual ETF curation (~20 major themes)
**Problem:** Too narrow; missed emerging narratives (telecom, REITs, digital assets)
**Status:** Deprecated

### Version 2.0 — Taxonomy Expansion (PARTIALLY ACTIVE)
**Approach:** Expanded manual stock classification
**Improvements:** Fixed mapping errors (SNDK→Memory, RIOT→Digital Assets, etc.)
**Status:** Superseded by V3.0

### Version 3.0 — ETF Universe Expansion (CURRENT)
**Approach:** Full ETF universe export (~5,000 ETFs → dynamic discovery)
**Benefits:** System automatically adapts to new market narratives
**Status:** Production (replaced manual ETF curation)

### Version 3.1 — ETF Filter Engine Refinement (CURRENT PRODUCTION)
**Approach:** Aggressive ETF filtering (5,000 → 2,500 equity-focused)
**Problem Solved:** Eliminated noise from bonds, inverse, leveraged, country ETFs
**Benefit:** Institutional capital flow detection dramatically improved
**Status:** Stable production version

---

## Architecture Evolution

### Key Architectural Decisions

**Decision 1: Move from Sector to Narrative (V1→V2)**
- **Rationale:** Institutional capital flows follow narratives, not static sectors
- **Example:** NVDA classified as "AI Accelerators" (not "semiconductors")
- **Impact:** Better alignment with market structure

**Decision 2: Move from Manual ETF Curation to Dynamic Export (V2→V3)**
- **Rationale:** Manual curation creates blind spots; new themes emerge constantly
- **Approach:** Export all 5,000+ ETFs; let system discover themes automatically
- **Impact:** Coverage expanded dramatically; coverage of emerging narratives improved

**Decision 3: Add Aggressive ETF Filtering (V3→V3.1)**
- **Rationale:** Full 5,000 ETF universe introduced too much noise
- **Approach:** Automatic exclusion of bonds, inverse, leveraged, country ETFs
- **Impact:** Signal-to-noise ratio improved; institutional flow detection clearer

### Design Principles

1. **Institutional Capital ≈ Market Truth**
   - Themes ranked by ETF inflows (where money goes)
   - Stocks scored by alignment with capital flow

2. **Narrative > Sector**
   - Stocks classified by current institutional thinking
   - Not static business categories

3. **Dynamic Adaptation**
   - System discovers new narratives automatically
   - No manual redesign when market structure changes

4. **Quality > Quantity**
   - Better to miss 10% of opportunities than rank wrong candidates
   - Focus on highest-conviction candidates (40 longs, 20 shorts)

5. **Simplicity > Complexity**
   - 5-factor scoring is sufficient
   - No overfitting or unnecessary variables

---

## Current State & Stability

### Stable Components ✅
- **ETF Architecture:** Proven framework for theme discovery
- **ETF Filter Engine:** Effective noise elimination
- **Theme Classification:** Leading/Emerging/Weakening/Lagging system
- **Scoring Algorithms:** 5-factor weighted composite
- **Long Watchlist Engine:** High-quality candidate selection
- **Short Watchlist Engine:** Decline identification

### Partial Components ⚠️
- **Stock Taxonomy Coverage:** ~95% coverage (some unknown stocks remain)
- **Manual Mappings:** ~100+ implemented; room for expansion
- **Historical Snapshots:** Daily JSON storage working; rotation analysis incomplete

### Missing Components ❌
- **Real-Time Data:** Uses static daily CSVs only
- **Company Profile Engine:** (company_profile_engine.py — stub)
- **Business Narrative Engine:** (business_to_theme_engine.py — stub)
- **Enhanced Error Handling:** Minimal exception handling
- **Data Validation:** Assumes clean input CSVs

---

## Future Roadmap

### P0 — Long Engine Validation (HIGHEST PRIORITY)
**Status:** Next highest priority

**Problem:** ETF architecture changed (20 → 2,500 themes). Need to validate long candidates.

**Questions:**
- Are top 40 longs truly market leaders (NVDA, AVGO, etc.)?
- Are strongest leaders missing?
- Does theme scoring have excessive influence?

**Audit Examples:** Test against known leaders (NVDA, META, PLTR, GOOG, ARM, TSM, MU, AMD)

### P1 — Historical Snapshot Engine
**Status:** High priority

**Problem:** Daily snapshots exist but rotation analysis minimal.

**Solution:** Implement rotation_engine.py fully to detect theme deltas.

**Example Output:**
```
Software:        Leading → Weakening (Distribution signal)
Biotech:         Lagging → Emerging (Accumulation signal)
Semiconductors:  Leading → Emerging (Leadership rotation)
```

### P2 — Rotation Delta Engine
**Status:** High priority

**Purpose:** Largest future edge in ThemePulse

**Capability:** Compare snapshots to identify institutional rotation early

**Implementation:** rotation_engine.py expansion

### P3 — Stock Taxonomy Expansion
**Status:** Medium priority

**Target:** Unknown stocks < 5% of universe

**Examples Needing Mapping:** NKE, CAG, WHR, PLAY, KHC, KMB, DEO, WBD

**Approach:** Gradual maintenance (not urgent redesign)

### Deferred/Low-Priority Items
- Weekly/monthly maintenance workflows
- Separate short engine redesign
- Theme normalization engine
- Real-time data integration

---

## Core Stock Selection Philosophy

### Key Principle
ThemePulse prioritizes **accelerating institutional leaders**, not established market leaders.

### What ThemePulse Does NOT Do
- Identify the "best company"
- Rank by revenue or market cap
- Value or fundamental analysis

### What ThemePulse DOES Do
- Identify where institutional capital is rotating **right now**
- Prioritize recent acceleration over established leadership
- Focus on swing trading opportunities, not long-term hold

### Expected Behavior
```
Examples of expected ranking:
• MU may rank above NVDA
• CRDO may rank above AVGO
• ALAB may rank above META

This is CORRECT behavior, not a bug.
Rationale: Institutional capital moving INTO MU faster than into NVDA
```

### Investment Philosophy
**Recent acceleration > established leadership > company quality**

This aligns with how professional traders identify rotations.

---

## Performance & Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| **Daily Execution Time** | <30 seconds | End-to-end pipeline |
| **ETF Universe Coverage** | 2,500 themes | After filtering 5,000+ raw |
| **Stock Universe** | ~5,000 stocks | Daily from stocks.csv |
| **Manual Mappings** | 100+ | High-conviction narratives |
| **Long Watchlist Size** | ~40 candidates | After filtering |
| **Short Watchlist Size** | ~20 candidates | After filtering |
| **Historical Database** | Growing | 1 snapshot per execution |
| **Estimated Completion** | 90% | Core pipeline stable; enhancements pending |

---

## Related Documentation

- [README.md](README.md) — User-friendly overview
- [USER_MANUAL.md](USER_MANUAL.md) — Step-by-step usage guide
- [FUTURE_ENHANCEMENTS.md](FUTURE_ENHANCEMENTS.md) — Enhancement details
- [VERSION_HISTORY.md](VERSION_HISTORY.md) — Detailed change log

---

**Last Updated:** 2026-06-19
**Version:** 3.1 (Stable Production)
**Completion:** ~90%
