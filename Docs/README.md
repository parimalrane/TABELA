# TABELA — Market Theme Rotation Scanner

**Version 3.1** | Production-Ready Research Tool

TABELA is an intelligent market scanning system that identifies attractive long and short stock opportunities by analyzing **institutional capital flows through ETF theme rotation** combined with multi-factor stock-level scoring.

## Core Concept

Traditional stock analysis classifies companies by sector (e.g., "semiconductors"). TABELA takes a different approach: it classifies stocks by the **current institutional narrative** (e.g., META as "AI Platform" rather than "social media"). By tracking which themes attract institutional capital through ETF inflows, TABELA dynamically detects emerging market opportunities and fading trends.

---

## What It Does

### Quick Summary
1. **Analyzes 2,500+ filtered ETFs** to identify the strongest market themes
2. **Maps 5,000+ stocks** to institutional narratives driving capital flows
3. **Scores stocks** using 5 factors: momentum, theme strength, sales growth, analyst ratings, and profitability
4. **Generates watchlists** with top 40 long candidates and top 20 short candidates
5. **Tracks rotation** by comparing daily theme classifications to detect shifts in institutional focus

### Detailed Workflow

```
INPUT: stocks.csv + ETF.csv (daily market data)
          ↓
    [Step 1] ETF PROCESSING
       • Filter 5,000+ ETFs → 2,500 equity themes
       • Calculate ETF momentum (relative strength)
       • Assign theme classifications
          ↓
    [Step 2] THEME RANKING
       • Classify themes: Leading (↑), Emerging (↑↑), Weakening (↓), Lagging (↓↓)
       • Rank by institutional strength
          ↓
    [Step 3] STOCK-TO-THEME MAPPING
       • Priority 1: Manual institutional narratives (100+ expert-curated mappings)
       • Priority 2: Automated sector/industry detection
       • Priority 3: Narrative translation to ETF themes
          ↓
    [Step 4] MULTI-FACTOR SCORING
       • Relative Strength (momentum): 40%
       • Theme Strength: 25%
       • Sales Growth: 20%
       • Zacks Rating: 10%
       • Profitability: 5%
       • Result: Composite score (0-100)
          ↓
    [Step 5] WATCHLIST GENERATION
       • Long candidates: Strong themes + high scores
       • Short candidates: Weak themes + poor momentum
       • Institutional leaders: Top 20 from leading themes
          ↓
    OUTPUT: Market rotation report + daily JSON snapshot
```

---

## Key Features

| Feature | Benefit |
|---------|---------|
| **Dynamic Theme Discovery** | Automatically adapts to new market narratives (no manual ETF curation required) |
| **Institutional Flow Tracking** | Identifies where smart money is flowing through ETF inflows |
| **Multi-Factor Scoring** | Balances momentum, fundamentals, and theme strength for quality candidates |
| **Daily Snapshots** | Builds historical database for rotation analysis and trend detection |
| **Expert Overrides** | ~100+ manual narrative mappings reflect real institutional thinking (e.g., NVDA = "AI Accelerators") |
| **Theme Breadth Analysis** | Shows % of strong stocks per theme (leading themes have broader participation) |

---

## Example Institutional Narratives

The system recognizes that institutional investors think in narratives, not sectors:

| Stock | Institutional Narrative | Traditional Sector |
|-------|------------------------|-------------------|
| NVDA | AI Accelerators | Semiconductors |
| META | AI Platform | Social Media |
| TSLA | Autonomous Driving AI | Automobiles |
| PLTR | Defense Software | Enterprise Software |
| RKLB | Space Infrastructure | Aerospace |
| SNOW | Cloud Infrastructure | Data Warehouse |
| RIOT | Digital Assets Infrastructure | Tech Hardware |

This approach captures **where institutional capital is flowing**, not static business categories.

---

## Project Structure

### Core Pipeline
- **main.py** — Main orchestrator; runs all 10 steps of the analysis workflow

### Engine Modules
- **etf_filter.py** — Filters 5,000+ ETFs to 2,500 equity themes
- **etf_engine.py** — Calculates ETF momentum and classifies theme strength
- **theme_parser.py** — Extracts themes from ETF strategy descriptions
- **stock_mapper.py** — Automated stock-to-theme mapping via industry/sector
- **company_theme_engine.py** — Manual institutional narrative overrides (~100+ mappings)
- **theme_translation_engine.py** — Translates internal narratives to ETF theme names
- **theme_hierarchy.py** — Theme parent-child relationships (e.g., "AI Platform" → "Artificial Intelligence")
- **scoring_engine.py** — Calculates RS, Sales, Zacks, Margin scores
- **composite_engine.py** — Weighted composite score (40/25/20/10/5 split)
- **watchlist_engine.py** — Selects long candidates
- **short_engine.py** — Selects short candidates
- **institutional_leaders_engine.py** — Top 20 institutional leader candidates
- **breadth_engine.py** — Theme participation analysis (% of strong stocks)
- **snapshot_engine.py** — Saves daily snapshots to market_data/snapshots
- **rotation_engine.py** — Compares daily snapshots for theme rotation deltas
- **stock_history_engine.py** — Saves daily stock universe history to market_data/stock_universe
- **persistence_engine.py** — Prints repeated long/short and theme persistence reports

### Configuration & Data
- **config.py** — Scoring weights, filter thresholds, ETF parameters
- **theme_dictionary.py** — Theme taxonomy reference
- **stocks.csv** — Daily input: ticker, industry, sector, RS, sales, Zacks, margin
- **ETF.csv** — Daily input: 5,000+ ETFs with names, strategies, performance data


---

## Installation & Usage

### Requirements
- **Python 3.9+**
- **pandas** (only dependency)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Verify setup
python main.py  # First run
```

### Run Analysis
```bash
# Daily market scan
python main.py

# Output includes:
# • Market rotation summary (Leading/Emerging/Weakening/Lagging themes)
# • Theme breadth analysis
# • Top 40 long candidates (with * for institutional flow only)
# • Top 20 short candidates
# • Snapshot saved to: market_data/snapshots/YYYY-MM-DD.json
```

### Historical Analysis
```bash
# Compare rotation across multiple days
python main.py  # Auto-generates snapshots

# View snapshots
ls market_data/snapshots/  # See daily JSON files
```

---

## Output Example

```
╔════════════════════════════════════════════════════════════════╗
║                   TABELA MARKET SCAN                       ║
║                      2026-06-19                                ║
╚════════════════════════════════════════════════════════════════╝

📊 MARKET ROTATION SUMMARY
═════════════════════════════════════════════════════════════════
Leading Themes:
  • AI Accelerators (RS: 89 | Strength: Strong)
  • Cloud Infrastructure (RS: 76 | Strength: Strong)
  • Semiconductors (RS: 72 | Strength: Strong)
  
Emerging Themes:
  • Autonomous Driving (RS: 68 | Strength: Gaining)
  • Defense Software (RS: 65 | Strength: Gaining)

Weakening Themes:
  • Traditional Retail (RS: 42 | Strength: Declining)
  • Energy Transition (RS: 38 | Strength: Declining)

Lagging Themes:
  • Financial Services (RS: 25 | Strength: Weak)
  • Consumer Discretionary (RS: 22 | Strength: Weak)

════════════════════════════════════════════════════════════════
📈 THEME BREADTH ANALYSIS
════════════════════════════════════════════════════════════════
AI Accelerators: 78% of stocks scoring above 80
Cloud Infrastructure: 62% of stocks scoring above 80
Semiconductors: 71% of stocks scoring above 80

════════════════════════════════════════════════════════════════
✅ TOP 40 LONG CANDIDATES
════════════════════════════════════════════════════════════════
Rank | Ticker | Score | Theme | Theme Score | Sales | Zacks | Margin
  1  | NVDA   |  94   | AI Accelerators | 100 | 88 | 92 | 95
  2  | AVGO   |  91   | Semiconductors  | 100 | 85 | 88 | 90
  3  | CRDO   |  89   | AI Accelerators |  75 | 82 | 85 | 87
...
 40  | MCHP   |  68   | Semiconductors  |  75 | 58 | 62 | 70

(* indicates stocks in long watchlist only via institutional theme flow)

════════════════════════════════════════════════════════════════
⚠️  TOP 20 SHORT CANDIDATES
════════════════════════════════════════════════════════════════
Rank | Ticker | Score | Theme | RS Rating
  1  | RETAIL |  18   | Traditional Retail | 12
  2  | STORE  |  22   | Consumer Disc | 18
...
```

---

## Filtering Logic

### Long Watchlist (High-Conviction Candidates)
- **Min Composite Score:** 80
- **Min RS Rating:** 80
- **Min Sales Growth:** 60
- **Min Zacks Rating:** 60
- **Theme Class:** Leading or Emerging themes (OR exceptional "Unclassified Leaders")

### Short Watchlist (Decline Candidates)
- **Max Composite Score:** 45
- **Max RS Rating:** 40
- **Weak Fundamentals:** Sales ≤ 40 OR Zacks ≤ 40

### ETF Filters (Automatic Exclusions)
- Bonds, Treasury products
- Inverse & Leveraged ETFs
- Currency & Commodity ETFs
- Country/Geographic ETFs
- Factor & Strategy wrapper ETFs
- Min Market Value: $200M

---

## Data & Performance

| Metric | Value |
|--------|-------|
| **ETF Universe** | 5,000+ → 2,500 filtered |
| **Stock Universe** | ~5,000 stocks analyzed daily |
| **Manual Mappings** | 100+ high-conviction narrative overrides |
| **Composite Weights** | 40% momentum + 25% theme + 20% sales + 10% ratings + 5% margins |
| **Execution Time** | <30 seconds per daily run |
| **Daily Snapshots** | Stored as JSON in market_data/snapshots folder |

---

## Understanding the Asterisk (*)

In the watchlist output, asterisks indicate stocks selected **primarily through institutional narrative strength**:

- **With \*:** Stock appeared in long watchlist because its theme is strong (institutional capital flowing in), even if individual fundamentals are moderate
- **Without \*:** Stock scored high on composite factors; theme strength was supporting factor

**Interpretation:** \* signals pure institutional conviction plays; non-\* signals balanced opportunities.

---

## Use Cases

### Portfolio Managers
Identify emerging themes gaining institutional capital flows for thematic portfolio construction.

### Traders
Detect theme rotation turning points and capitalize on breadth shifts.

### Researchers
Analyze historical theme performance through daily snapshots and rotation deltas.

### Analysts
Find stocks aligned with institutional narratives before broader market recognition.

---

## Important Notes

- **Research Tool, Not Trading Signal** — TABELA identifies opportunities for analysis; not a trading system
- **Daily Updates Required** — Requires fresh stocks.csv and ETF.csv files from Zacks daily
- **No Real-Time Feed** — Uses static daily exports; not suitable for intraday trading
- **Prototype Status** — ~90% complete; gaps include real-time data integration and enhanced error handling
- **Research Grade** — Designed for professional investors and researchers

---

## Version History

| Version | Focus | Status |
|---------|-------|--------|
| 1.0 | Manual ETF curation | Deprecated |
| 2.0 | Taxonomy expansion | Partially active |
| 3.0 | Full ETF universe (~5,000) | Current |
| 3.1 | ETF filtering refinement (→2,500) | **Current Production** |

See [FUTURE_ENHANCEMENTS.md](FUTURE_ENHANCEMENTS.md) for roadmap.

---

## License

MIT License — See [LICENSE](../LICENSE) for details.

---

## Questions?

Refer to [USER_MANUAL.md](USER_MANUAL.md) for detailed step-by-step guidance or [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for technical specifications.
