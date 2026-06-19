# THEMEPULSE SYSTEM ARCHITECTURE

**Current Version:** ThemePulse V1 (Updated)  
**Architecture Status:** Active Development  
**Last Updated:** 2026-06-16

**Purpose:** Document exact system architecture, execution flow, and component responsibilities for continuous development.

---

## PROJECT FILE STRUCTURE

### Core Pipeline
**main.py**
- Master execution orchestrator
- Controls end-to-end daily market scan workflow
- Imports and calls all engine modules sequentially
- Manages intermediate data structures and final output formatting

### ETF Analysis & Validation
**etf_engine.py**
- Loads and validates ETF universe
- Filters to curated whitelist (via allowed_etfs.py)
- Excludes non-equity products (Bonds, Leveraged, Inverse, Currency, etc.)
- Parses investment strategy text to extract themes
- Calculates ETF Relative Strength (RS) rankings
- Maps ETFs to canonical themes
- Assigns theme classification and theme scores

**allowed_etfs.py**
- Curated whitelist of equity ETFs for analysis
- Currently ~45 ETFs covering major market themes
- Updated periodically to reflect market evolution
- Prevents analysis of bonds, leveraged, or currency products

### Stock-to-Theme Mapping
**stock_mapper.py**
- Primary automated stock-to-theme mapping engine
- Uses industry classification and sector data
- Applies broad market classification logic
- Maps stocks to standardized themes
- Examples: NKE → Consumer, HON → Infrastructure, GM → Autonomous Mobility

**company_theme_engine.py**
- Manual override system for high-conviction mappings
- Used when automated mapping is too generic
- Priority 1 in mapping hierarchy (checked before stock_mapper)
- Examples: CRDO → AI Infrastructure, LITE → Optical Networking, MRVL → AI ASIC

**theme_translation_engine.py**
- Bridges company narrative themes to ETF-recognized themes
- Ensures consistency across mapping pipeline
- Examples: "AI Infrastructure" → "Artificial Intelligence", "Optical Networking" → "Semiconductors"
- Prevents theme fragmentation in final output

### Configuration & Reference
**config.py**
- ETF_THEME_RULES mapping for theme classification
- Scoring parameters and thresholds
- Theme taxonomy definitions

**theme_parser.py**
- Parses ETF investment strategy text
- Extracts sector, theme, and subtheme components
- Handles natural language variations in ETF naming

**theme_dictionary.py**
- Reference taxonomy for all themes
- Theme hierarchies and relationships

### Stock Scoring Engines
**scoring_engine.py**
- Calculates RS Raw (price momentum score)
- Calculates RS Rating (0-100 normalized momentum)
- Calculates Sales Score (sales growth relative to market)
- Calculates Zacks Score (earnings estimate quality/revisions)
- Calculates margin score inputs

**composite_engine.py**
- Combines individual scoring components
- Weighted formula: RS_Rating(30%) + Sales_Score(25%) + Zacks_Score(30%) + Margin_Score(15%)
- Produces final composite score (0-100)

### Watchlist & Ranking Engines
**watchlist_engine.py**
- Builds long watchlist candidates
- Selection criteria:
  - Theme classification: Leading or Emerging
  - Composite Score >= 75
  - RS Rating >= 70
  - Strong sales and Zacks indicators
- Produces ranked long candidate list

**short_engine.py**
- Builds short watchlist candidates
- Selection criteria:
  - Theme classification: Weakening or Lagging
  - RS Rating < 40
  - Composite Score < 40
  - Weak technical and fundamental signals
- Produces ranked short candidate list

### Specialized Analysis
**breadth_engine.py**
- Calculates theme participation breadth
- Breadth Metric = (Strong Stocks / Total Stocks in Theme) × 100
- Strong Stock Definition: RS Rating >= 80 AND Composite Score >= 75
- Weighted breadth score accounts for theme size
- Identifies themes with deepest participation

**institutional_leaders_engine.py** *(NEW)*
- Selects top institutional leader candidates (max 20)
- Two-stage selection process:
  - Stage 1: Best stocks from Leading/Emerging themes with Composite Score >= 90 OR RS Rating >= 95
  - Stage 2: Fill remaining slots from top stocks overall sorted by Composite Score
- Provides alternative candidate source for theme-agnostic institutional ideas

### Input Data Files
**ETF.csv**
- Daily ETF universe (ticker, fund name, category, strategy, performance metrics)
- Source for market leadership identification
- Primary input for theme strength ranking

**stocks.csv**
- Daily stock universe (ticker, industry, sector, fundamentals, technicals)
- Individual stock scoring data
- Primary input for watchlist generation

---

## SYSTEM EXECUTION FLOW

### Phase 1: ETF Universe Analysis (Steps 1-5)

**STEP 1:** Load ETF.csv into memory

**STEP 2:** Apply allowed_etfs whitelist filter
- Only keep ETFs in curated list

**STEP 3:** Filter invalid ETFs
- Exclude by keyword (Bond, Treasury, Leveraged, Inverse, etc.)
- Validate investment category
- Remove low-quality products

**STEP 4:** Parse theme from Investment Strategy text
- Extract Sector, Theme, Subtheme components
- Examples: "Semiconductors", "Artificial Intelligence", "Cloud Computing"

**STEP 5:** Calculate ETF Relative Strength
- Compute RS_Raw (momentum metric)
- Rank ETFs by RS_Raw within each theme

**STEP 6:** Classify themes by percentile
- Top 25%: "Leading" (score: 100)
- 25-50%: "Emerging" (score: 75)
- 50-75%: "Weakening" (score: 40)
- Bottom 25%: "Lagging" (score: 20)

### Phase 2: Stock Universe Analysis (Steps 7-16)

**STEP 7:** Load stocks.csv into memory

**STEP 8:** Map stocks to company narratives
- Check COMPANY_THEME override dictionary
- If not found, use stock_mapper (industry/sector based)

**STEP 9:** Translate to ETF-recognized themes
- Check THEME_TRANSLATION mapping
- Ensure consistency with ETF universe

**STEP 10:** Inherit theme classification from ETF engine
- Lookup theme in theme_class_map
- Assign Theme_Class (Leading/Emerging/Weakening/Lagging)
- Assign Theme_Score (100/75/40/20)
- Handle unclassified stocks with special logic

**STEP 11:** Calculate RS_Raw score
- Technical momentum metric
- Price-based relative strength

**STEP 12:** Calculate RS_Rating
- Normalize RS_Raw to 0-100 scale
- Rank-ordered percentile score

**STEP 13:** Calculate Sales_Score
- Sales growth relative to market average
- 0-100 scale, 50 = market average

**STEP 14:** Calculate Zacks_Score
- Earnings estimate quality
- Earnings revision momentum
- 0-100 scale

**STEP 15:** Calculate Margin_Score
- Profit margin trends
- Relative margin strength

**STEP 16:** Calculate Composite_Score
- Weighted combination of all scores
- Formula: RS_Rating(30%) + Sales_Score(25%) + Zacks_Score(30%) + Margin_Score(15%)
- Final 0-100 ranking metric

### Phase 3: Watchlist Generation (Steps 17-21)

**STEP 17:** Build Long Watchlist
- Filter: Theme_Class in ["Leading", "Emerging"]
- Filter: Composite_Score >= 75 AND RS_Rating >= 70
- Additional quality gates on Sales/Zacks scores
- Sort by Composite_Score descending
- Output: Long candidate list

**STEP 18:** Build Short Watchlist
- Filter: Theme_Class in ["Weakening", "Lagging"]
- Filter: RS_Rating < 40 AND Composite_Score < 40
- Sort by Composite_Score ascending
- Output: Short candidate list

**STEP 19:** Build Institutional Leaders
- Select top 20 candidates from strong themes
- Stage 1: Best from Leading/Emerging with Composite >= 90 OR RS >= 95
- Stage 2: Fill remaining from overall strongest stocks
- Output: Institutional leader list

**STEP 20:** Build Theme Breadth Analysis
- Group stocks by Mapped_Theme
- Count total and strong stocks per theme
- Calculate breadth % and weighted breadth score
- Sort by participation strength
- Output: Theme breadth ranking

**STEP 21:** Merge Long Candidate Universe
- Combine Long Watchlist + Institutional Leaders
- Remove duplicates (keep first occurrence)
- Mark institutional-only picks with asterisk (*)
- Sort by Composite_Score descending
- Limit output to top 40

### Phase 4: Output & Reporting (Step 22)

**STEP 22:** Generate ThemePulse Daily Scan Report

*Section 1: Market Rotation Summary*
- Lists Leading themes
- Lists Emerging themes
- Lists Weakening themes
- Lists Lagging themes

*Section 2: Theme Breadth Analysis*
- Top 20 themes by participation strength
- Columns: Mapped_Theme, Total_Stocks, Strong_Stocks, Breadth_Percent, Weighted_Breadth_Score

*Section 3: Long Candidate Universe*
- Top 40 long candidates
- Columns: Ticker, Mapped_Theme, Theme_Class, RS_Rating, Composite_Score
- Asterisk (*) marks institutional leader-only picks

*Section 4: Short Candidate Universe*
- Top 20 short candidates
- Columns: Ticker, Mapped_Theme, Theme_Class, RS_Rating, Composite_Score

---

## DATA DEPENDENCY CHAIN

```
ETF.csv
   ↓
[etf_engine.py] → ETF Filtering & Validation
   ↓
[etf_engine.py] → ETF Theme Parsing
   ↓
[etf_engine.py] → Calculate ETF RS & Rankings
   ↓
[etf_engine.py] → Theme Classification (Leading/Emerging/Weakening/Lagging)
   ↓
stocks.csv
   ↓
[stock_mapper.py] → Automated Stock-to-Theme Mapping
   ↓
[company_theme_engine.py] → Apply Manual Overrides (Priority 1)
   ↓
[theme_translation_engine.py] → Translate to ETF Themes
   ↓
[scoring_engine.py] → Calculate RS Raw, RS Rating, Sales, Zacks, Margin
   ↓
[composite_engine.py] → Calculate Composite Score
   ↓
[watchlist_engine.py] → Build Long Watchlist
[short_engine.py] → Build Short Watchlist
[breadth_engine.py] → Calculate Theme Breadth
[institutional_leaders_engine.py] → Select Institutional Leaders
   ↓
[main.py] → Merge, Sort, Format Output
   ↓
Console Report: ThemePulse Daily Market Scan
```

---

## CRITICAL DESIGN DECISIONS

1. **ETF Whitelist Approach (allowed_etfs.py)**
   - Constrains analysis to equity-focused ETFs
   - Prevents contamination from leveraged, inverse, or bond products
   - Enables themed market rotation analysis

2. **Two-Layer Theme Mapping (stock_mapper.py + company_theme_engine.py)**
   - Automated layer for speed and consistency
   - Manual override layer for narrative capture
   - Override takes priority when institutional story diverges from textbook classification

3. **Institutional Leaders vs. Long Watchlist**
   - Long Watchlist: Theme-driven (must be in Leading/Emerging)
   - Institutional Leaders: Strength-driven (top scores regardless of theme)
   - Both merged to capture both theme rotation AND absolute quality plays

4. **Breadth Metric**
   - Measures participation depth within themes
   - Strong Stock threshold (RS >= 80 AND Composite >= 75) ensures relevance
   - Identifies themes with widespread institutional support vs. single-stock concentration

5. **Composite Score Weighting**
   - RS_Rating (30%): Technical momentum + institutional accumulation signal
   - Sales_Score (25%): Fundamental business growth
   - Zacks_Score (30%): Earnings quality + revision momentum
   - Margin_Score (15%): Profitability trends
   - Rationale: Technical + Earnings Quality weighted higher than growth/margins

↓

Theme Score Assignment

↓

Stock RS Calculation

↓

Composite Score Calculation

↓

Long Engine

↓

Short Engine

↓

Breadth Engine

↓

Final Production Output

############################################################
IMPORTANT DEVELOPMENT RULES
############################################################

Rule 1

Never change stable architecture without reason.

Rule 2

Do not modify multiple files simultaneously.

Rule 3

Always test one module at a time.

Rule 4

Protect company_theme_engine logic carefully.

Rule 5

Institutional narrative overrides generic sector classification.

Rule 6

Unknown stocks should not be automatically discarded.

Rule 7

ETF universe controls theme classification.

Rule 8

Never add random technical indicators.

Rule 9

Preserve philosophy:

Institutional Capital Flow First

############################################################
FUTURE DEVELOPMENT ENTRY POINT
############################################################

When future development resumes:

Step 1

Read VERSION_HISTORY.md

Step 2

Read FUTURE_ENHANCEMENTS.md

Step 3

Read PROJECT_MASTER_DECISIONS.md

Step 4

Read ARCHITECTURE_MAP.md

Step 5

Select one enhancement only

Step 6

Implement and test incrementally

============================================================
END OF ARCHITECTURE MAP
=======================
