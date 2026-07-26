

# SYSTEM CONTEXT & TECHNICAL SPECIFICATION

# TABELA Market Intelligence Platform

**Version:** 1.0

**Last Updated:** 2026-07-25

**Primary Source:** Active Codebase (`C:\TABELA`)

---

## 1. EXECUTIVE SUMMARY

TABELA is a modular, Python-based financial market intelligence platform that processes daily ETF and stock data to identify investment themes, calculate composite strength scores, and generate actionable market insights. The system employs a linear pipeline architecture with specialized engines performing single responsibilities, ensuring deterministic execution and easy extensibility.

### Core Value Proposition

* **Theme Identification:** Automatically maps industries and companies to standardized investment themes.
* **Strength Scoring:** Calculates composite scores for themes and individual securities.
* **Market Intelligence:** Identifies institutional leaders, distribution patterns, and structural weaknesses.
* **Historical Analysis:** Maintains comprehensive market state history for trend analysis.
* **Weekly Intelligence:** Generates consolidated weekly reports with persistence tracking.

### System Characteristics

* **Modular Architecture:** 30+ specialized engines with single responsibilities.
* **Linear Data Flow:** Deterministic execution pipeline with no circular dependencies.
* **Configuration-Driven:** Centralized configuration enabling parameter tuning.
* **Historical Persistence:** Daily snapshots with immutable historical records.
* **Extensible Design:** Plug-and-play engine architecture for new analysis types.

---

## 2. ARCHITECTURE & DESIGN PATTERNS

### 2.1 Layered Architecture

```
Presentation Layer (Reports, Console Output)
         ↑
Historical Intelligence Layer (Multi-day Analysis)
         ↑
Business Engine Layer (30+ Specialized Engines)
         ↑
Core Pipeline Layer (Orchestration, Configuration)
         ↑
Input Data Layer (CSV Files, Mapping Tables)

```

### 2.2 Design Patterns

#### Modular Engine Pattern

* Each engine performs exactly one primary responsibility.
* Engines communicate through structured data contracts.
* No engine modifies upstream data or reads another engine's internal state.
* Independent testability and deterministic outputs.

#### Linear Pipeline Pattern

* Sequential execution with clear dependencies.
* Output of one engine becomes input to the next.
* Execution order is significant and documented.
* Pipeline can be extended by inserting new engines at defined points.

#### Configuration Singleton Pattern

* Centralized configuration in `core/config.py`.
* All thresholds, weights, and paths defined in one location.
* Engines consume configuration rather than hard-coding values.
* Enables parameter tuning without code changes.

#### Registry Pattern (Stock Transition)

* Persistent tracking of stock state transitions.
* Maintains historical persistence across runs.
* Enables detection of emerging patterns over time.

### 2.3 Architectural Principles

1. **Single Responsibility:** Each engine has one clearly defined responsibility.
2. **Minimal Coupling:** Engines communicate only through defined interfaces.
3. **Deterministic Execution:** Same inputs produce same outputs.
4. **Historical Immutability:** Daily snapshots are never modified.
5. **Extensibility:** New engines integrate at defined pipeline points.
6. **Configuration-Driven:** Business logic parameters externalized.
7. **Data Ownership:** Each data type has exactly one owning engine.

---

## 3. CONFIGURATION & DEPENDENCIES

### 3.1 Runtime Environment

* **Platform:** Windows / Linux / macOS
* **Python Version:** 3.10+
* **Package Manager:** pip
* **Version Control:** Git

### 3.2 Core Dependencies

* `pandas>=1.0.0`

### 3.3 Standard Library Usage

* `datetime`: Date parsing and manipulation
* `pathlib`: Cross-platform path handling
* `json`: Data serialization
* `re`: Pattern matching for file discovery
* `dataclasses`: Structured data containers
* `io`: Output capture and redirection
* `contextlib`: Resource management
* `math`: Mathematical operations
* `typing`: Type hints
* `csv`: Reference data parsing
* `enum`: Status enumerations
* `collections`: Data structure utilities
* `textwrap`: Text formatting

### 3.4 Configuration Files

#### `core/config.py` - Primary Configuration

```python
# Composite Score Weights
COMPOSITE_WEIGHTS = {
    "RS_WEIGHT": 0.40,      # Relative Strength weight
    "THEME_WEIGHT": 0.25,   # Theme strength weight
    "MARGIN_WEIGHT": 0.05,  # Margin score weight
    "ZACKS_WEIGHT": 0.10    # Zacks rank weight
}

# Long Scoring Weights
LONG_WEIGHTS = {
    "RS_WEIGHT": 0.55,
    "THEME_WEIGHT": 0.25,
    "SALES_WEIGHT": 0.12,
    "ZACKS_WEIGHT": 0.05,
    "MARGIN_WEIGHT": 0.03
}

# Short Scoring Weights
SHORT_WEIGHTS = {
    "RS_WEIGHT": 0.45,
    "THEME_WEIGHT": 0.42,
    "SALES_WEIGHT": 0.00,
    "ZACKS_WEIGHT": 0.10,
    "MARGIN_WEIGHT": 0.03
}

# Long Candidate Filters
LONG_FILTERS = {
    "MIN_RS": 90,
    "MIN_LONG_SCORE": 85
}

# Short Candidate Filters
SHORT_FILTERS = {
    "MIN_SHORT_SCORE": 70,
    "USE_LEGACY_WEAKNESS_FILTER": True
}

# Theme Strength Configuration
THEME_STRENGTH_CONFIG = {
    "BENCHMARK_TICKER": "SPY",
    "PERIOD_WEIGHTS": {
        "Performance 1M (%)": 0.45,
        "Performance 1W (%)": 0.30,
        "Performance 3M (%)": 0.20,
        "Performance 1D (%)": 0.05,
    },
    "AGGREGATION_MODE": "aum_weighted",  # or "equal_weight"
    "ENABLE_NORMALIZATION": True,
    "DEBUG_THEME_STRENGTH": True
}

# Distribution Engine Configuration
DISTRIBUTION_ENGINE_CONFIG = {
    "DEFAULT_TOP_N": 50,
    "MAX_HISTORY_DAYS": 21,
    "SNAPSHOT_MAX_DAYS": 21,
    "ROTATION_MAX_FILES": 3,
    "RECENT_BASELINE_LOOKBACK_DAYS": 5,
    "DOWNTREND_WINDOW_DAYS": 5,
    "MIN_RS_DROP_1D": 0.0,
    "MIN_RS_DROP_RECENT": 0.0,
    "MIN_COMPOSITE_DROP_1D": -0.001,
    "MIN_COMPOSITE_DROP_RECENT": -0.001,
    "MIN_RS_PERSISTENCE_DAYS": 2,
    "MIN_COMPOSITE_PERSISTENCE_DAYS": 2,
    "MIN_RS_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_COMPOSITE_DOWN_DAYS_IN_WINDOW": 2,
    "MIN_RS_DROP_RECENT_FOR_DOWN_DAYS": 25.0,
    "MIN_COMPOSITE_DROP_RECENT_FOR_DOWN_DAYS": 0.0,
    "SPARSE_COMPOSITE_HISTORY_MAX_POINTS": 1,
    "USE_COMPOSITE_MEDIAN_CONFIRMATION_WHEN_HISTORY_SPARSE": True,
    "MIN_COMPOSITE_MEDIAN_CONFIRMATION_GAP": 0.0,
    "LEADERSHIP_RS_THRESHOLD": 80.0,
    "USE_LEADERSHIP_AS_HISTORY_CONFIRMATION": True,
    "MIN_RS_DROP_RECENT_FOR_LEADERSHIP_CONFIRMATION": 25.0,
    "MIN_THEME_LAGGING_STREAK_DAYS": 3,
    "MIN_THEME_WEAKENING_TRANSITIONS": 2,
    "MAX_REASON_TOKENS": 6,
    "EVIDENCE_MIN_ABS_DELTA": 0.05,
    "SORT_LEADERSHIP_MISSING_SENTINEL": 9999,
}

# ETF Filters
ETF_FILTERS = {
    "MIN_MARKET_VALUE": 200  # Minimum AUM in millions
}

# Stock Transition Configuration
STOCK_TRANSITION_CONFIG = {
    "REGISTRY_DIR": "market_data/stock_transition",
    "OBSERVATION_MIN_RUNS": 7,
    "OBSERVATION_MAX_RUNS": 7,
}

# Market Context Configuration
MARKET_CONTEXT_CONFIG = {
    "PERFORMANCE_LOOKBACKS": [5, 20, 50, 200],
    "RELATIVE_VOLUME_LOOKBACKS": [5, 20],
    "MARKET_ETFS": ["SPY", "QQQ", "IWM", "DIA"],
    "MARKET_STRUCTURE": {
        "SMA_PERIODS": [20, 50, 200],
    },
    "INSTITUTIONAL_ACTIVITY": {
        "ADR_LOOKBACK": 20,
        "CONSOLIDATION_RANGE_FACTOR": 0.50,
        "ACCUMULATION_LOGIC": "OR",
        "DISTRIBUTION_LOGIC": "OR",
        "CONSOLIDATION_LOGIC": "AND",
        "ACCUMULATION_VOLUME_THRESHOLD": 0.90,
        "DISTRIBUTION_VOLUME_THRESHOLD": 0.90,
        "CONSOLIDATION_VOLUME_THRESHOLD": 1.00,
    },
}

# Minimum History Days
MIN_HISTORY_DAYS = 20

# Unknown Emerging Leaders Thresholds
UNKNOWN_RS_THRESHOLD = 85
UNKNOWN_LONG_SCORE_THRESHOLD = 80
UNKNOWN_PRICE_POSITION_THRESHOLD = 80
UNKNOWN_MARKET_CAP_THRESHOLD = 500

# Weekly Review Parameters
MIN_MARKET_CAP = 300
MIN_PRICE_FILTER = 5
MIN_VOLUME_FILTER = 300000

```

#### `engines/runtime_context.py` - Execution Environment

```python
@dataclass(frozen=True)
class RuntimeContext:
    market_date: str      # Trading date (YYYY-MM-DD)
    etf_file: Path        # Path to latest ETF.csv
    stocks_file: Path     # Path to latest stocks.csv

```

### 3.5 File Structure Conventions

```
market_data/
├── zacks_input_data/           # Daily input files
│   ├── YYYYMMDD_ETF.csv
│   └── YYYYMMDD_stocks.csv
├── snapshots/                  # Daily market state
│   └── YYYY-MM-DD_market_snapshot.json
├── rotation_delta/             # Daily rotation changes
│   └── YYYY-MM-DD_rotation_delta.json
├── stock_universe/             # Daily stock history
│   └── YYYY-MM-DD_stock_history.json
├── watchlist_history/          # Daily watchlist state
│   └── watchlist_YYYY-MM-DD.json
├── daily_reports/              # Formatted console output
│   └── YYYY-MM-DD.txt
├── market_context/             # Market context data
│   └── YYYY-MM-DD_market_context.json
├── weekly_intelligence/        # Weekly consolidated data
│   ├── summary_report/
│   └── YYYY-MM-DD_to_YYYY-MM-DD_weekly_intelligence.json
├── stock_transition/           # Stock transition registry
│   └── YYYY-MM-DD_registry.json
└── unknown_classification/     # Unknown classification data
    └── YYYY-MM-DD_unknown_classification.json

```

---

## 4. DIRECTORY & FILE INDEX

### 4.1 Root Directory

```
├── AGENTS.md                    # Agent configuration
├── ARCHITECTURAL_ANALYSIS.md    # Architecture documentation
├── LICENSE                      # MIT License
├── README.md                    # Project overview
├── main.py                      # Primary entry point (27 lines)
├── weekly_run.py                # Weekly intelligence generator (18 lines)
├── requirements.txt             # Python dependencies (pandas)
├── .env                         # Environment variables
├── .gitignore                   # Git exclusion patterns
├── .ignore                      # Additional ignore patterns
└── opencode.json                # Development tool configuration

```

### 4.2 Core Modules (`core/`)

```
├── __init__.py                  # Package marker
├── pipeline.py                  # Main orchestration pipeline (754 lines)
├── config.py                    # Centralized configuration (257 lines)
├── stock_mapper.py              # Stock-to-theme mapping (346 lines)
├── theme_dictionary.py          # Theme definitions (111 lines)
├── theme_hierarchy.py           # Theme parent-child relationships (37 lines)
├── theme_normalizer.py          # Theme name normalization (24 lines)
├── theme_parser.py              # Theme parsing utilities (87 lines)
├── theme_translation_engine.py  # Theme translation mappings (132 lines)
├── company_theme_engine.py      # Company-specific theme assignments (23 lines)
└── industry_theme_engine.py     # Industry-to-theme mappings (30 lines)

```

### 4.3 Engine Modules (`engines/`)

```
├── __init__.py                  # Package marker
├── runtime_context.py           # Execution environment (47 lines)
├── etf_engine.py                # ETF processing and scoring (90 lines)
├── etf_filter.py                # ETF filtering logic (178 lines)
├── composite_engine.py          # Composite score calculation (33 lines)
├── breadth_engine.py            # Theme participation analysis (289 lines)
├── scoring_engine.py            # Core scoring algorithms (198 lines)
├── long_scoring_engine.py       # Long candidate scoring (22 lines)
├── short_scoring_engine.py      # Short candidate scoring (29 lines)
├── institutional_leaders_engine.py    # Institutional leader identification (73 lines)
├── watchlist_engine.py          # Watchlist generation (37 lines)
├── distribution_engine.py       # Distribution pattern detection (730 lines)
├── short_engine.py              # Short candidate identification wrapper (7 lines)
├── rotation_engine.py           # Market rotation analysis (324 lines)
├── snapshot_engine.py           # Daily snapshot persistence (91 lines)
├── stock_history_engine.py      # Stock history persistence (211 lines)
├── stock_transition_engine.py   # Stock state transition tracking (359 lines)
├── watchlist_delta_engine.py    # Watchlist change detection (291 lines)
├── market_context_engine.py     # Market context analysis (670 lines)
├── presentation_engine.py       # Report formatting and output (790 lines)
├── historical_query_engine.py   # Historical data query gateway (447 lines)
├── historical_queries.py        # Historical query implementations (244 lines)
├── historical_intelligence_engine.py  # Multi-day trend analysis (618 lines)
├── unknown_classification_engine.py   # Unknown company classification (69 lines)
├── weekly_dataset_builder.py    # Weekly dataset construction (1189 lines)
├── weekly_intelligence_engine.py       # Weekly report generation (105 lines)
├── weekly_json_writer.py        # Weekly JSON output writer (182 lines)
└── weekly_markdown_writer.py    # Weekly markdown report writer (141 lines)

```

### 4.4 Data Directory (`data/`)

```
├── industry_theme_mapping.csv   # Industry-to-theme reference mappings
└── stock_theme_mapping.csv      # Stock-to-theme reference mappings

```

### 4.5 Documentation (`docs/`)

```
├── ARCHITECTURE.md              # System architecture overview
├── CODE_PRACTICES.txt           # Coding standards and practices
├── CODEBASE_REFERENCE.md        # Codebase reference guide
├── CURRENT_STATE.md             # Current system state
├── DATA_MODEL.md                # Data structures and schemas
├── DEVELOPER_GUIDE.md           # Development guide
├── JSON_FIELD_GLOSSARY.md       # JSON output field definitions
├── LESSONS_LEARNED.md           # Development lessons
├── PROJECT_OVERVIEW.md          # Project overview
├── REBUILD_GUIDE.md             # System rebuild guide
├── ROADMAP.md                   # Development roadmap
├── SESSION_HISTORY.md           # Session history log
├── TABELA_HANDBOOK.md           # User handbook
├── TABELA_MASTER_CONTEXT.md     # Master context document
├── TABELA_PROJECT_INSTRUCTIONS.md  # Project-specific instructions
├── TABELA_Taxonomy_Reference.md # Taxonomy reference
├── TECHNICAL_SPECIFICATION.md   # Technical specifications
└── WEEKLY_PROJECT_INSTRUCTIONS.md   # Weekly instructions

```

---

## 5. DATA SCHEMAS & DOMAIN MODELS

### 5.1 Input Data Schemas

#### ETF Input Schema (`YYYYMMDD_ETF.csv`)

```
Required Columns:
- Ticker: str                    # ETF ticker symbol
- Company Name: str              # ETF full name
- Investment Category: str       # High-level category
- Investment Strategy: str       # Theme/strategy description
- Market Value (mil): float      # AUM in millions
- Performance 1D (%): float      # 1-day performance
- Performance 1W (%): float      # 1-week performance
- Performance 1M (%): float      # 1-month performance
- Performance 3M (%): float      # 3-month performance
- Performance 6M (%): float      # 6-month performance
- Performance 1Y (%): float      # 1-year performance

```

#### Stock Input Schema (`YYYYMMDD_stocks.csv`)

```
Required Columns:
- Ticker: str                    # Stock ticker symbol
- Company Name: str              # Company name
- Sector: str                    # Market sector
- Industry: str                  # Industry classification
- Zacks Rank: int                # Zacks rank (1-5)
- Last Close: float              # Latest closing price
- Market Cap (mil): float        # Market capitalization
- Volume: int                    # Trading volume
- % Price Change (1 Week): float
- % Price Change (4 Weeks): float
- % Price Change (12 Weeks): float
- Relative Price Change (YTD): float
- Price as a % of 52 Wk H-L Range: float
- Sales Growth F(0)/F(-1): float
- Operating Margin 12 Mo %: float
- Net Margin %: float

```

#### Market Input Schema (`market_data/Market.csv`)

```
Required Columns:
- Date: datetime                 # Trading date
- ETF: str                       # ETF ticker (SPY, QQQ, IWM, DIA)
- Open: float                    # Opening price
- High: float                    # Daily high
- Low: float                     # Daily low
- Close: float                   # Closing price
- Volume: int                    # Trading volume

```

### 5.2 Internal Data Entities

#### Stock Entity (Post-Processing)

```python
{
    "Ticker": str,
    "Company Name": str,
    "Sector": str,
    "Industry": str,
    "Mapped_Theme": str,           # Original mapped theme
    "ETF_Theme": str,              # Normalized ETF theme
    "Theme_Class": str,            # Leading/Neutral/Lagging/Unknown/Unclassified Leader
    "Theme_State": str,            # Classification state
    "Theme_Rank": int,             # Theme rank position
    "Theme_Score": float,          # Theme strength score
    "ETF_Raw_Score": float,        # Raw ETF score
    "Is_Unclassified_Leader": bool,
    "RS_Raw": float,               # Raw relative strength
    "RS_Rating": int,              # Normalized RS (1-99)
    "Weakness_Score": float,       # Inverse percentile for shorts
    "Sales_Score": float,          # Sales growth score
    "Zacks_Score": float,          # Zacks rank score
    "Margin_Score": float,         # Margin score
    "Composite_Score": float,      # Overall composite
    "Long_Score": float,           # Long candidate score
    "Short_Score": float,          # Short candidate score
    "Is_Long_Candidate": bool,
    "Is_Short_Candidate": bool,
    "Long_Rank": Optional[int],
    "Short_Rank": Optional[int],
    "Tracking_State": str          # UNTRACKED/LONG/OBSERVATION/DISTRIBUTION
}

```

#### Theme Strength Entity

```python
{
    "Theme": str,                          # Theme name
    "ETF_RS_Raw": float,                   # Raw theme strength
    "Theme_Strength_Normalized": float,    # Normalized 0-100
    "Theme_Rank": int,                     # Rank position
    "Rel_1D": float,                       # 1-day relative vs SPY
    "Rel_1W": float,                       # 1-week relative vs SPY
    "Rel_1M": float,                       # 1-month relative vs SPY
    "Rel_3M": float,                       # 3-month relative vs SPY
    "WgtContr_1D": float,                  # 1-day weighted contribution
    "WgtContr_1W": float,                  # 1-week weighted contribution
    "WgtContr_1M": float,                  # 1-month weighted contribution
    "WgtContr_3M": float                   # 3-month weighted contribution
}

```

---

## 6. API SPECIFICATIONS

### Core Engine APIs

#### `core/pipeline.py` - Main Pipeline API

```python
def run_tabela_pipeline() -> None:
    """Execute complete TABELA processing pipeline."""

def build_theme_strength(
    etf_master: pd.DataFrame,
    benchmark_returns: dict,
    theme_strength_settings: dict
) -> pd.DataFrame:
    """Calculate theme strength scores from ETF data."""

def map_stock_themes(stocks: pd.DataFrame) -> pd.DataFrame:
    """Map stocks to themes using priority rules (Stock -> Industry -> Auto)."""

def score_stocks(stocks: pd.DataFrame) -> pd.DataFrame:
    """Execute complete stock scoring pipeline."""

```

#### `engines/scoring_engine.py` - Core Scoring API

```python
def calculate_rs_raw(stocks: pd.DataFrame) -> pd.DataFrame:
    """Calculate raw relative strength score."""

def calculate_rs_rating(stocks: pd.DataFrame) -> pd.DataFrame:
    """Convert raw RS scores to percentile ratings (1-99)."""

def calculate_sales_score(stocks: pd.DataFrame) -> pd.DataFrame:
    """Calculate sales growth score."""

def calculate_zacks_score(stocks: pd.DataFrame) -> pd.DataFrame:
    """Calculate Zacks rank score."""

def calculate_margin_score(stocks: pd.DataFrame) -> pd.DataFrame:
    """Calculate margin score based on percentile."""

```

---

## 7. EXECUTION FLOWS

### 7.1 Daily Execution Flow (`main.py`)

```
START main.py
    │
    ▼
Load Runtime Context (Discover YYYYMMDD_ETF.csv & YYYYMMDD_stocks.csv)
    │
    ▼
Execute Market Context Engine (Process Market.csv & macro indicators)
    │
    ▼
Process ETF Data & Build Theme Strength (AUM-weighted / Relative vs SPY)
    │
    ▼
Map Stocks & Apply Theme Hierarchy (Stock Mapping > Industry > Auto)
    │
    ▼
Score Stocks (RS, Sales, Zacks, Margin, Composite, Long/Short)
    │
    ▼
Build Candidate Lists & Transition Registry (Long, Short, Observation, Distribution)
    │
    ▼
Calculate Theme Breadth & Performance Table
    │
    ▼
Persist Outputs (Daily Snapshot, Rotation Delta, Stock History, Reports)
    │
    ▼
END

```

### 7.2 Error Recovery Flow

```
Processing Error
    │
    ▼
Check Error Type
    ├── Recoverable (missing optional file, empty data)
    │   └── Log warning, continue with defaults
    │
    ├── Configuration Error (missing required config)
    │   └── Raise RuntimeError, stop execution
    │
    └── Data Corruption (invalid schema, corrupt JSON)
        └── Attempt recovery, log error, skip affected component

```

### 7.3 Stock Transition Lifecycle Flow

```
LONG CANDIDATE
      │
      │ (Removed from long list)
      ▼
OBSERVATION (Day 1-7)
      │
      │ (After OBSERVATION_MAX_RUNS days)
      ▼
DISTRIBUTION CANDIDATE
      │
      │ (Qualifies via distribution engine)
      ▼
DISTRIBUTION
      │
      │ (Returns to long list)
      ▼
RECOVERED → LONG CANDIDATE
      │
      │ (Observation expires without qualification)
      ▼
REMOVED FROM TRACKING

```

---

## 8. KNOWN CONSTRAINTS & TRADE-OFFS

| Risk | Mitigation |
| --- | --- |
| Data corruption | Immutable snapshots, schema validation |
| Configuration errors | Validation in `load_runtime_context()` |
| Missing input files | Graceful degradation, empty dataset handling |
| Performance degradation | Single-pass algorithms, dictionary lookups |
| Schema evolution | Additive changes only, default values for missing fields |
| Extension breakage | Clear interface contracts, dependency documentation |

---

## 9. STABILITY CLASSIFICATION

| Component | Status | Notes |
| --- | --- | --- |
| Configuration | **Stable** | Core weights and thresholds |
| ETF Engine | **Stable** | Processing and filtering |
| Theme Mapping | **Stable** | Priority-based mapping logic |
| Composite Engine | **Stable** | Score calculation |
| Breadth Engine | **Stable** | Participation analysis |
| Institutional Leader | **Stable** | Leader identification |
| Rotation Engine | **Stable** | Delta calculation |
| Snapshot Engine | **Stable** | Persistence layer |
| Market Context Engine | **Active Development** | Market structure analysis |
| Distribution Engine | **Active Development** | Deterioration detection |
| Short Engine | **Active Development** | Weakness identification |
| Historical Intelligence | **Active Development** | Multi-day analysis |
| Stock Transition Engine | **Active Development** | Lifecycle tracking |
| Weekly Intelligence | **Active Development** | Aggregation and reporting |
| Presentation Engine | **Active Development** | Output formatting |

---

## 10. EXTENSION GUIDELINES & EVOLUTION

### 10.1 Engine Extension Template

```python
from core.config import RELEVANT_CONFIG

def new_analysis_engine(input_data, config=None):
    """One-line description of engine purpose.
    
    Args:
        input_data: DataFrame or dict from upstream engine
        config: Optional configuration override
    
    Returns:
        Enhanced data structure for downstream consumption
    """
    processed_data = transform(input_data)
    return processed_data

```

### 10.2 Recommendations

1. **Short-term (1-3 months):** Add data caching for reference mappings, implement unit tests for core engines.
2. **Medium-term (3-6 months):** Add correlation analysis between themes, introduce plugin architecture for extensions.
3. **Long-term (6-12 months):** Database backend migration for historical state queries, REST API layer for external dashboards.

---

## APPENDIX A: FIELD GLOSSARY

* **RS_Raw:** Raw Relative Strength score (weighted price changes).
* **RS_Rating:** Normalized percentile rating (1–99).
* **Theme_Score:** Theme strength contribution (0–100).
* **Composite_Score:** Overall stock score (weighted components).
* **Long_Score / Short_Score:** Candidate scores tuned for long or short positioning.
* **Leading / Neutral / Lagging:** Theme classifications based on performance relative to SPY and peer quartiles.

---

## APPENDIX B: THEME HIERARCHY

```python
THEME_PARENT_MAP = {
    "AI Platform": "Artificial Intelligence",
    "AI Accelerators": "Semiconductors",
    "Defense Software": "Software",
    "Optical Infrastructure": "Semiconductors",
    "Electronics Manufacturing": "Infrastructure",
    "Footwear/Apparel": "Broad",
    "Restaurants": "Broad",
    "Discount Retail": "Broad",
    "Consumer Staples": "Broad",
    "Homebuilders": "Infrastructure",
    "Building Materials": "Infrastructure",
    "Electrical Infrastructure": "Infrastructure",
    "Industrial Automation": "Equipment and services",
    "Telecom Infrastructure": "Telecom",
    "Media Distribution": "Broad",
    "Travel Platform": "Transportation/Shipping"
}

```

---

## APPENDIX C: CHANGE LOG

### Version 1.0 (2026-07-25)

* Consolidated duplicate specifications into a single `SYSTEM_CONTEXT.md` document.
* Standardized runtime parameters (Python 3.10+).
* Integrated lifecycle flows, error handling diagrams, and module indices.