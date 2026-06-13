# ARCHITECTURE_MAP.md

============================================================
THEMEPULSE SYSTEM ARCHITECTURE
==============================

Current Version:

ThemePulse V1

Architecture Status:

Frozen

Purpose:

Document exact system architecture and execution flow.

This file allows future development to resume without re-learning the codebase.

############################################################
PROJECT FILE STRUCTURE
############################################################

main.py

Main execution engine.

Controls full execution pipeline.

Runs entire daily market scan.

etf_mapper.py

Maps ETF tickers to market themes.

Examples:

SOXX → Semiconductors

SMH → Semiconductors

IGV → Software

BUG → Cybersecurity

stock_mapper.py

Maps stocks to themes using:

Industry column

Sector column

Business model interpretation

Broad market classification

Examples:

NKE → Consumer

HON → Infrastructure

GM → Autonomous Mobility

company_theme_engine.py

Manual high conviction override engine.

Used when stock mapper is too generic.

Examples:

CRDO → AI Infrastructure

LITE → Optical Networking

MRVL → AI ASIC

VRT → AI Power Infrastructure

Purpose:

Override sector classification when institutional narrative differs from textbook classification.

theme_translation.py

Converts company narrative themes into ETF-recognized themes.

Example:

AI Infrastructure → Artificial Intelligence

Optical Networking → Semiconductors

Purpose:

Ensure company-specific narratives map correctly into ETF universe.

long_engine.py

Builds Long Watchlist.

Logic:

Leading or Emerging theme

High Composite Score

High Relative Strength

Strong Sales Growth

Good Zacks Rank

Purpose:

Find strongest institutional accumulation candidates.

short_engine.py

Builds Short Watchlist.

Logic:

Weakening or Lagging theme

Weak Relative Strength

Weak Composite Score

Purpose:

Detect stocks experiencing institutional capital exit.

breadth_engine.py

Calculates theme breadth.

Formula:

Strong Stocks / Total Stocks

Strong Stock Definition:

RS Rating >= 80

AND

Composite Score >= 75

Purpose:

Measure internal participation strength inside themes.

ETF.csv

Daily ETF universe input file.

Purpose:

Determine market leadership.

Classify themes.

Calculate ETF relative strength rankings.

stocks.csv

Daily stock universe input file.

Purpose:

Calculate stock rankings.

Build long and short watchlists.

############################################################
SYSTEM EXECUTION ORDER
############################################################

STEP 1

Load ETF.csv

STEP 2

Map ETFs to themes

STEP 3

Calculate ETF relative strength

STEP 4

Rank ETF universe

STEP 5

Assign theme classifications

Leading

Emerging

Weakening

Lagging

STEP 6

Load stocks.csv

STEP 7

Map stocks to themes using stock_mapper.py

STEP 8

Apply company_theme_engine overrides

STEP 9

Apply theme_translation mapping

STEP 10

Inherit theme classification from ETF engine

STEP 11

Calculate stock RS Raw Score

STEP 12

Calculate RS Rating

STEP 13

Calculate Sales Score

STEP 14

Calculate Zacks Score

STEP 15

Calculate Margin Score

STEP 16

Calculate Composite Score

STEP 17

Build Long Watchlist

STEP 18

Build Short Watchlist

STEP 19

Build Theme Breadth Analysis

STEP 20

Generate final production output

############################################################
DEPENDENCY CHAIN
############################################################

ETF.csv

↓

ETF Relative Strength Engine

↓

Theme Classification Engine

↓

Stocks.csv

↓

Stock Mapper Engine

↓

Company Theme Override Engine

↓

Theme Translation Engine

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
