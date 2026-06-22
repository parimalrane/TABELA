# TABELA User Manual

**Easy-to-Follow Step-by-Step Guide**

---

## Table of Contents
1. [Quick Start (5 minutes)](#quick-start-5-minutes)
2. [Understanding the Concept](#understanding-the-concept)
3. [Installation & Setup](#installation--setup)
4. [Running Your First Analysis](#running-your-first-analysis)
5. [Understanding the Output](#understanding-the-output)
6. [Common Use Cases](#common-use-cases)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start (5 minutes)

### Step 1: Install Python
```bash
# Check if Python 3.9+ is installed
python --version

# If not, download from: https://www.python.org/downloads/
```

### Step 2: Install Dependencies
```bash
cd c:\TABELA
pip install -r requirements.txt
```

### Step 3: Prepare Daily Data
You need two CSV files (from Zacks):
- **stocks.csv** — Daily stock data (update daily)
- **ETF.csv** — Daily ETF data (update daily)

### Step 4: Run Analysis
```bash
python main.py
```

### Step 5: Review Output
- Console output shows market scan results
- Results automatically saved to `market_data/snapshots/YYYY-MM-DD.json`
- Check asterisks (*) for institutional flow-only plays

**Done!** Your first market scan is complete.

---

## Understanding the Concept

### The Big Picture

Traditional investing asks: *"What's the best company?"*

TABELA asks: *"Where is institutional money flowing RIGHT NOW?"*

### Why This Matters

**Institutional investors control 70-80% of market volume.** They move money in themes, not individual stocks. By tracking their capital flows through ETFs, TABELA detects:
- Where smart money is accumulating
- Where market narratives are shifting
- Which themes are gaining or losing favor

### Real-World Example

**Traditional Approach:**
```
NVIDIA is a great semiconductor company → BUY NVDA
```

**TABELA Approach:**
```
Institutional money is flowing into "AI Accelerators" ETFs
  ↓
NVIDIA classified as "AI Accelerators" narrative
  ↓
NVIDIA scores high because its theme is strong
  ↓
Institutional conviction is driving NVDA price, not just "good company" status
```

### How It Works (Simplified)

```
Step 1: Scan 2,500 ETFs to find strongest themes
        Leading: AI Accelerators, Cloud, Semiconductors
        Lagging: Retail, Consumer, Financial Services

Step 2: Map 5,000 stocks to those themes
        NVDA → AI Accelerators
        SNOW → Cloud Infrastructure
        META → AI Platform

Step 3: Score stocks on multiple factors
        • Momentum (40%)
        • Theme strength (25%)
        • Revenue growth (20%)
        • Analyst rating (10%)
        • Profitability (5%)

Step 4: Generate watchlist
        Top 40 long candidates (strong scores + strong themes)
        Top 20 short candidates (weak scores + weak themes)
        Top 20 "institutional leaders" (pure theme plays)

Result: Market rotation report + daily database entry
```

---

## Installation & Setup

### System Requirements
- **OS:** Windows, Mac, or Linux
- **Python:** 3.9 or higher
- **Disk Space:** 50MB (growing as history accumulates)
- **Internet:** Not required (uses static CSV files)

### Step-by-Step Installation

#### 1. Install Python
```bash
# Verify installation
python --version
# Should show: Python 3.9.x or higher
```

#### 2. Download TABELA
```bash
# If not already downloaded
git clone <repository_url>
cd c:\TABELA
```

#### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import pandas; print(pandas.__version__)"
# Should show version number
```

#### 4. Prepare Data Directory
```bash
# TABELA needs:
# • stocks.csv (in project root)
# • ETF.csv (in project root)
# • market_data/snapshots/ folder (auto-created if missing)

# Verify directory structure:
dir *.csv        # Should see stocks.csv and ETF.csv
dir market_data/snapshots/     # Folder for historical snapshots
```

#### 5. Test Installation
```bash
# Run a test execution
python main.py

# You should see console output with market scan results
# If successful: "✅ Analysis Complete" message
# If error: See Troubleshooting section
```

---

## Running Your First Analysis

### Preparation Checklist
- [ ] Python 3.9+ installed
- [ ] pandas installed via pip
- [ ] stocks.csv in project folder
- [ ] ETF.csv in project folder
- [ ] market_data/snapshots/ folder exists (or will be created)

### Execution

**Basic Run:**
```bash
cd c:\TABELA
python main.py
```

**What Happens:**
1. Loads stocks.csv and ETF.csv
2. Filters ETF universe (2,500 equity themes)
3. Classifies themes (Leading/Emerging/Weakening/Lagging)
4. Maps stocks to themes
5. Scores all stocks
6. Generates watchlists
7. Displays console output
8. Saves snapshot to market_data/snapshots/{YYYY-MM-DD}.json

**Expected Output Time:** <30 seconds

**Expected Console Output:**
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
  
... [more output]
```

### Automation (Optional)

**Run daily at 4 PM (after market close):**

**Windows - Task Scheduler:**
1. Open Task Scheduler
2. Create Basic Task → "TABELA Daily"
3. Trigger: Daily, 4:00 PM
4. Action: Start program `python.exe`
5. Add arguments: `C:\TABELA\main.py`
6. Run with highest privileges

**Mac/Linux - Cron:**
```bash
# Open crontab editor
crontab -e

# Add this line (runs daily at 4 PM)
0 16 * * * cd /path/to/TABELA && python main.py
```

---

## Understanding the Output

### Output Structure

The console output has **4 main sections:**

#### Section 1: Market Rotation Summary

```
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
```

**What This Means:**
- **Leading:** Strong uptrend; institutional inflows
- **Emerging:** Building momentum; institutional interest growing
- **Weakening:** Slowing momentum; institutional outflows starting
- **Lagging:** Downtrend; institutional avoidance

**How to Use It:**
```
✅ DO: Build positions in Leading/Emerging themes
❌ DON'T: Add to Weakening/Lagging theme positions
📊 TRACK: Watch themes move between categories (rotation signals)
```

#### Section 2: Theme Breadth Analysis

```
📈 THEME BREADTH ANALYSIS
════════════════════════════════════════════════════════════════
AI Accelerators: 78% of stocks scoring above 80
Cloud Infrastructure: 62% of stocks scoring above 80
Semiconductors: 71% of stocks scoring above 80
```

**What This Means:**
- Shows what % of stocks in each theme are "strong" (score ≥ 80)
- Higher % = broader institutional consensus
- Lower % = concentrated positioning

**Interpretation:**
```
AI Accelerators 78% = Strong theme conviction (78% of stocks strong)
Energy Transition 25% = Weak theme conviction (only 25% of stocks strong)
```

**How to Use It:**
```
✅ PREFER: Themes with >70% breadth (broad conviction)
⚠️ CAUTION: Themes with <40% breadth (thin conviction)
📉 AVOID: Themes with <20% breadth (concentrated, at risk of rotation)
```

#### Section 3: Top 40 Long Candidates

```
✅ TOP 40 LONG CANDIDATES
═════════════════════════════════════════════════════════════════
Rank | Ticker | Score | Theme | Theme Score | Sales | Zacks | Margin
  1  | NVDA   |  94   | AI Accelerators | 100 | 88 | 92 | 95
  2  | AVGO   |  91   | Semiconductors  | 100 | 85 | 88 | 90
  3  | CRDO   |  89   | AI Accelerators |  75 | 82 | 85 | 87
  4  | ALAB   |  87   | AI Accelerators |  75 | 80 | 83 | 85
  5  | PLTR   |  86   | Defense Software| 75 | 78 | 80 | 82
...
 40  | MCHP   |  68   | Semiconductors  |  75 | 58 | 62 | 70

(* indicates stocks in long watchlist only via institutional theme flow)
```

**Column Explanations:**
- **Score:** Composite score (0-100) — overall opportunity strength
- **Theme:** Institutional narrative driving the stock
- **Theme Score:** How strong is the theme (100=Leading, 75=Emerging, etc.)
- **Sales:** Revenue growth score
- **Zacks:** Analyst sentiment score
- **Margin:** Profitability score
- **\*:** Asterisk = strong theme but moderate fundamentals (pure institutional play)

**How to Use It:**
```
✅ RANK 1-10: Highest conviction plays (all factors strong)
✅ RANK 11-25: Solid opportunities (good balance of factors)
⚠️  RANK 26-40: Secondary ideas (theme-driven, watch fundamentals)
\* = Pure institutional flow plays (theme is primary driver)
```

#### Section 4: Top 20 Short Candidates

```
⚠️  TOP 20 SHORT CANDIDATES
════════════════════════════════════════════════════════════════
Rank | Ticker | Score | Theme | RS Rating
  1  | RETAIL |  18   | Traditional Retail | 12
  2  | STORE  |  22   | Consumer Disc | 18
  3  | OLD    |  25   | Traditional Retail | 20
...
 20  | WEAK   |  45   | Lagging Sector | 40
```

**Interpretation:**
```
Low scores + weak themes = institutional avoidance
These are stocks institutional money is exiting
```

**How to Use It:**
```
⚠️  CONSIDER: These for hedges or short positions
📊 MONITOR: Watch to confirm they don't break out (escape weakness)
```

---

## Common Use Cases

### Use Case 1: Finding Long Opportunities

**Goal:** Identify stocks to add to your portfolio

**Steps:**
1. Run `python main.py`
2. Look at **Section 1: Leading/Emerging themes**
3. Look at **Section 3: Top 40 longs**
4. Filter for themes you believe in
5. Focus on high-rank candidates (1-15) for most conviction

**Example Decision:**
```
If AI is your thesis:
  • Find "AI Accelerators" in theme list (is it Leading/Emerging?)
  • Look for AI stocks in top 40 (NVDA, CRDO, ALAB)
  • Check breadth % (78% = strong conviction)
  • Consider position sizing based on rank (1-5 = core, 6-15 = satellite)
```

### Use Case 2: Monitoring Theme Rotation

**Goal:** Detect shifts in institutional capital flows (swing trading setup)

**Steps:**
1. Save today's output to a note
2. Run again tomorrow (or next week)
3. Compare theme classifications:
   - Leading → Emerging = Distribution (prepare to exit)
   - Lagging → Emerging = Accumulation (prepare to enter)
   - Emerging → Leading = Breakout (increase position)

**Example:**
```
Yesterday: Software was Lagging
Today: Software is Emerging
Interpretation: Institutional accumulation signal
Action: Light positions for potential bounce
```

**Advanced:** Compare JSON files in market_data/snapshots/ folder for multi-day trends

### Use Case 3: Finding Short Opportunities

**Goal:** Identify stocks for shorting or avoiding

**Steps:**
1. Run `python main.py`
2. Look at **Section 4: Top 20 shorts**
3. Look at **Section 1: Lagging themes**
4. Look for stocks where both theme is weak AND fundamentals deteriorating

**Example Decision:**
```
If you see:
  • RETAIL stock in top shorts
  • Traditional Retail theme is Lagging
  • Breadth <20% (poor theme conviction)
  → Candidate for short position
```

### Use Case 4: Building a Themed Portfolio

**Goal:** Construct a thematic portfolio (e.g., "AI theme")

**Steps:**
1. Identify your theme (e.g., AI Accelerators)
2. Check if it's Leading or Emerging in Section 1
3. If yes: Filter top 40 longs for that theme
4. Build position with rank 1-15 candidates
5. Weight higher-ranked candidates more heavily
6. Re-run daily/weekly to monitor rotation

**Example Portfolio:**
```
Theme: AI Accelerators (Leading, 78% breadth)

Position Sizing:
Rank 1: NVDA    (20% of theme allocation) — highest conviction
Rank 3: CRDO    (18% of theme allocation)
Rank 4: ALAB    (15% of theme allocation)
Rank 9: MU      (12% of theme allocation)
Rank 15: ARM    (10% of theme allocation)
Others (ranked 20-30): 25% of theme allocation
```

### Use Case 5: Comparing Multiple Days (Rotation Analysis)

**Goal:** Track theme rotation across multiple weeks/months

**Steps:**
1. Check `market_data/snapshots/` folder for past snapshots
2. Compare theme classifications across dates:
   - Is AI still Leading or moved to Emerging?
   - Are any new themes appearing?
   - Any themes that disappeared?

**Example Analysis:**
```
Week 1: Leading = AI, Cloud, Semi
Week 2: Leading = AI, Cloud, Semi, Autonomous
Week 3: Leading = AI, Autonomous, Defense Software

Interpretation: Cloud/Semi losing favor; Autonomous/Defense gaining
```

---

## Tips & Best Practices

### ✅ DO

1. **Run daily** (after market close) for consistent signals
2. **Track theme changes** (Leading ↔ Emerging = key rotation signals)
3. **Focus on high-ranked candidates** (1-15 have best odds)
4. **Verify themes make sense** (does the stock really fit that narrative?)
5. **Use breadth as context** (>70% breadth = strong conviction)
6. **Combine with your research** (TABELA finds opportunities; you verify them)
7. **Build positions gradually** (don't go all-in on rank 1)
8. **Monitor marked stocks (*)** (these are pure institutional flow plays)

### ❌ DON'T

1. **Don't trade on single day's output** (confirmation needed)
2. **Don't ignore asterisks (*)** (these are theme-driven; watch for rotation)
3. **Don't fight Lagging themes** (don't try to find value in them)
4. **Don't assume Rank = absolute quality** (rank is relative to current market)
5. **Don't use 100% of scoring weights** (use as part of your process, not gospel)
6. **Don't forget to update CSV files** (stale data = stale analysis)
7. **Don't ignore theme breadth** (low breadth = high rotation risk)

### Best Practice Examples

**Before Taking Action:**
```
✅ Step 1: Run analysis
✅ Step 2: Identify theme (Leading/Emerging/Weakening/Lagging)
✅ Step 3: Check breadth % (is theme conviction strong?)
✅ Step 4: Review company fundamentals independently
✅ Step 5: Check technicals (has the stock already broken out?)
✅ Step 6: Size position appropriately
✅ Step 7: Set stop loss
✅ Step 8: Come back next week to check if theme is still strong
```

**Monitoring a Position:**
```
Day 1: Buy NVDA (Rank 1, AI Accelerators Leading, 78% breadth)
Day 7: Re-run analysis
  • AI Accelerators still Leading? Yes ✅
  • Breadth still high? Yes, 76% ✅
  • NVDA still Rank 1-3? Yes ✅
  → HOLD

Week 2: Re-run analysis
  • AI Accelerators moved to Emerging? ⚠️
  • Breadth dropped to 45%? ⚠️
  • NVDA dropped to Rank 15+? ⚠️
  → Consider taking profits / reducing position
```

---

## Troubleshooting

### Problem 1: "FileNotFoundError: stocks.csv"

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'stocks.csv'
```

**Solution:**
1. Verify stocks.csv is in c:\TABELA folder
2. Check file name spelling (case-sensitive on Mac/Linux)
3. Make sure file is not named stocks.txt or stocks.xlsx

**Command to check:**
```bash
dir *.csv        # Shows CSV files in folder
ls *.csv         # Mac/Linux version
```

### Problem 2: "ModuleNotFoundError: No module named 'pandas'"

**Error Message:**
```
ModuleNotFoundError: No module named 'pandas'
```

**Solution:**
1. Install pandas:
   ```bash
   pip install pandas
   ```
2. Verify installation:
   ```bash
   python -c "import pandas; print(pandas.__version__)"
   ```

### Problem 3: Empty or Invalid Output

**Symptom:** Program runs but produces no watchlist results

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| No stocks pass filters | Check that stock data has valid RS, sales, Zacks scores |
| All stocks weak | Possible market environment; try next day |
| CSV files corrupt | Try exporting fresh files from Zacks |
| Date mismatch | Ensure stocks.csv and ETF.csv are same date |

**Debug Command:**
```bash
# Check data format
python -c "import pandas as pd; print(pd.read_csv('stocks.csv').head())"
```

### Problem 4: "Permission Denied" Error

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: 'market_data/snapshots/2026-06-19.json'
```

**Solution:**
1. Close JSON files if open in other programs
2. Check folder permissions
3. Run as administrator:
   ```bash
   # Windows
   python main.py  # Run in elevated command prompt
   ```

### Problem 5: Script Runs Slow or Times Out

**Symptom:** Takes >1 minute or doesn't complete

**Causes & Solutions:**

| Issue | Solution |
|-------|----------|
| ETF.csv has >10,000 rows | Filter to recent date only |
| stocks.csv has >10,000 rows | Filter to active stocks only |
| Computer slow | Close other programs; try again |
| Hard drive slow | Consider moving to SSD |

**Performance Check:**
```bash
# Check CSV sizes
wc -l *.csv           # Line count
# If > 10,000 lines, consider filtering down
```

### Problem 6: "KeyError: Expected Column 'X'"

**Error Message:**
```
KeyError: 'RS' or KeyError: 'expected_column'
```

**Solution:**
1. Verify CSV column names match expected format
2. Check that all required columns are present:
   - stocks.csv: ticker, industry, sector, RS, sales, Zacks, margin
   - ETF.csv: name, strategy, performance data
3. Export fresh files from Zacks with correct format

**Debug Command:**
```bash
python -c "import pandas as pd; print(pd.read_csv('stocks.csv').columns.tolist())"
```

### Problem 7: Historical Folder Issues

**Issue:** market_data/snapshots/ folder won't create or can't write files

**Solution:**
```bash
# Create folder manually
mkdir history

# Verify permissions
dir history

# If needed, change folder permissions
```

### Problem 8: Different Results Each Day?

**Question:** Why do watchlist positions change day-to-day?

**Answer:** This is normal! Reasons include:
- Stock prices/RS updated daily
- ETF performance changes
- New stocks may enter/exit watchlist
- Theme strength adjusts as themes rank differently

**This is NOT a bug.**

---

## Advanced Topics

### Customizing Configuration

Edit `config.py` to adjust:

```python
# Scoring weights (must sum to 1.0)
COMPOSITE_WEIGHTS = {
    'rs_rating': 0.40,      # ← Increase for momentum focus
    'theme_score': 0.25,    # ← Increase for theme focus
    'sales_score': 0.20,
    'zacks_score': 0.10,
    'margin_score': 0.05
}

# Long watchlist filters
LONG_MIN_COMPOSITE = 80     # ← Increase for more selective
LONG_MIN_RS_RATING = 80

# Short watchlist filters
SHORT_MAX_COMPOSITE = 45    # ← Adjust short criteria
```

### Analyzing Historical Data

```python
# Load and compare snapshots
import json
from datetime import datetime, timedelta

# Load yesterday's snapshot
with open('market_data/snapshots/2026-06-18.json') as f:
    yesterday = json.load(f)

# Load today's snapshot
with open('market_data/snapshots/2026-06-19.json') as f:
    today = json.load(f)

# Compare themes
print("Today's Leading:", today['leading_themes'])
print("Yesterday's Leading:", yesterday['leading_themes'])

# Detect rotation
rotation = set(today['leading_themes']) - set(yesterday['leading_themes'])
if rotation:
    print("New Leading themes:", rotation)
```

### Creating Custom Reports

You can extract data from market_data/snapshots/ JSON files to create custom analyses:

```python
# Example: Track a specific stock over time
import json
import glob

stock_history = {}
for file in sorted(glob.glob('market_data/snapshots/*.json')):
    with open(file) as f:
        snapshot = json.load(f)
        date = snapshot['date']
        for stock in snapshot['top_20_longs']:
            if stock['ticker'] == 'NVDA':
                stock_history[date] = stock['score']

print("NVDA Score Over Time:", stock_history)
```

---

## Getting More Help

### Documentation Files
- **README.md** — Overview and features
- **PROJECT_ARCHITECTURE.md** — Technical details
- **FUTURE_ENHANCEMENTS.md** — Planned features
- **VERSION_HISTORY.md** — What changed and why

### Common Questions

**Q: How often should I run analysis?**
A: Daily (after market close) for consistent signals. Weekly minimum.

**Q: Can I use this for day trading?**
A: Possible, but designed for swing trading (days to weeks). Not for minute-level scalping.

**Q: Should I blindly follow the rankings?**
A: No. Use as part of your process. Always verify with your own research.

**Q: What if all themes are weak?**
A: Normal during market downturns. System adapts to relative rankings.

**Q: Can I modify the code?**
A: Yes. It's MIT licensed. Modify freely; test thoroughly.

---

## Version & Updates

**Current Version:** 3.1 (Stable Production)

**Last Updated:** 2026-06-19

**For Updates:** Check FUTURE_ENHANCEMENTS.md for planned features

---

**Happy Analyzing! 📊**

For questions or issues, refer to the Troubleshooting section or PROJECT_ARCHITECTURE.md for technical details.