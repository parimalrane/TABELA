# Thematic ETF Mapping Guide & TradingView Watchlist Protocol

## 1. Overview & TradingView Utility
TABELA displays top-weighted, pure-play thematic ETFs directly alongside stock breadth leaders in the **THEME BREADTH ANALYSIS** terminal table and exports them deterministically into the **TRADINGVIEW WATCHLIST EXPORTS** (`###leading_ETF,...` and `###lagging_ETF,...`).

### Primary Purpose:
* **Top-Down Sector Context**: Identifies the parent sector ETF (e.g. `[XLK]`, `[XLE]`, `[XLV]`, `[XLF]`, `[XLU]`, `[XLI]`, `[XLB]`, `[XLY]`, `[XLP]`, `[XLRE]`).
* **Sub-Industry Pure-Play Charting**: Provides the primary and secondary institutional charting vehicles (e.g. `SMH, SOXX` for Semis, `COPX` for Copper Mining, `SIL, SILJ` for Silver Mining, `GDX, GDXJ` for Gold Mining, `CIBR, BUG` for Cybersecurity, `XLU, VPU` for Utilities) for immediate cross-referencing on TradingView.
* **Granular Watchlist Segmentation**: In the TradingView Watchlist Export, stocks appear once under their single most granular active pure-play ETF. Secondary ETFs join the header string for macro tracking.

---

## 2. File Locations & Data Structures
The thematic mapping architecture spans four relational CSV files in `data/`:

| File | Purpose | Key Columns |
| :--- | :--- | :--- |
| `data/theme_etf_mapping.csv` | Maps Theme to SPDR sector and pure-play ETFs | `Theme`, `Top_ETFs`, `Description` |
| `data/macro_theme_mapping.csv` | Maps Micro/Narrative Themes to Macro Themes | `Narrative_Theme`, `Benchmark_ETF_Theme` |
| `data/industry_theme_mapping.csv` | Maps raw Zacks Industries to Micro/Macro Themes | `Industry`, `Theme` |
| `data/stock_theme_mapping.csv` | Explicit ticker-level overrides for dominant narratives | `Ticker`, `Theme` |

### `theme_etf_mapping.csv` Schema:
| Column | Description | Example |
| :--- | :--- | :--- |
| `Theme` | Micro Theme or Macro Theme name | `Cybersecurity`, `Utilities`, `Copper Mining` |
| `Top_ETFs` | Formatted string: `[SECTOR] PURE_PLAY_1, PURE_PLAY_2` | `[XLK] CIBR, BUG` or `[XLB] COPX` |
| `Description` | Human-readable explanation of theme scope | `Cybersecurity Pure-Plays` |

### Fallback Hierarchy:
When rendering rows in the Theme Breadth table or assigning stocks to TradingView export buckets:
1. Exact match on **Micro Theme** (e.g., `Memory` $\rightarrow$ `[XLK] DRAM`).
2. If no micro entry exists, automatically falls back to **Macro Theme** (e.g., `Optical Networking` $\rightarrow$ parent `Semiconductors` $\rightarrow$ `[XLK] SMH, SOXX`).
3. If unmapped, gracefully outputs blank.

---

## 3. TradingView Watchlist Export Rules
The TradingView export engine enforces strict quantitative rules:
1. **All Active Table ETFs Included**: Every ETF displayed in the Theme Breadth Analysis table is extracted (both primary and secondary tokens).
2. **Individual Multi-Timeframe Scoring vs SPY**: Every ETF is scored individually against `SPY` using unified weights ($20\%\text{ 1W} + 40\%\text{ 1M} + 40\%\text{ 3M}$).
3. **Dual-Gate Structural Health Filter (52-Week Range Position)**:
   - **Leading ETF Gate (Long Header `###leading_ETF,`)**: An ETF must be outperforming `SPY` ($\text{Relative Score} \ge 0.0\%$) **AND** holding the upper half of its annual range ($\text{52W Range} \ge 50.0\%$). This prevents defensive, counter-trend cushions near 52-week lows (e.g., `VOX`) from masquerading as market leaders.
   - **Lagging ETF Gate (Short Header `###lagging_ETF,`)**: An ETF must be underperforming `SPY` ($\text{Relative Score} < 0.0\%$) **AND** breaking down in the lower half of its annual range ($\text{52W Range} \le 50.0\%$). This prevents routine pullbacks in secular bull uptrends (e.g., `CLOU`, `SKYY`, `IGV`) from triggering premature short watches.
   - **Neutral Zone**: ETFs with conflicting signals (e.g. falling slower than SPY while near lows, or pulling back while holding above 50% range) are excluded from both watchlists.
   - ETFs without pricing data in the input files (e.g., unpriced or defunct funds) are excluded.
4. **Actionable 1:1 Header Filter (Active Stock Pruning)**:
   - To keep TradingView watchlists completely actionable and avoid opening empty charts, an ETF is printed in `###leading_ETF,` or `###lagging_ETF,` **only if it has at least 1 qualified stock candidate** in its bucket below.
   - Secondary ETFs (e.g., `SOXX`, `IAK`, `IBB`) and themes where zero stocks passed institutional filters are pruned from the header. Every ETF in the header has a direct, actionable stock bucket below it.
5. **Mutual Exclusion**: An ETF can appear in `leading_ETF` OR `lagging_ETF`, never both.
6. **Single Stock Granularity**: Each stock candidate appears **once**, under its most granular active thematic ETF (primary pure-play preferred). Secondary ETFs do not duplicate stock rows.

---

## 4. Formatting Rules
To maintain crisp terminal table alignment without truncation or excessive line-wrapping:
1. **Always prefix with parent Sector SPDR tag**: `[XLK]`, `[XLE]`, `[XLV]`, `[XLF]`, `[XLI]`, `[XLB]`, `[XLU]`, `[XLY]`, `[XLP]`, `[XLRE]`.
2. **Cap pure-play ETFs at 1 or 2 tickers**: Maximum string length should stay $\le 18$ characters where possible (e.g., `[XLK] CIBR, BUG`). For multi-ETF mappings like `Utilities,"[XLU] XLU, VPU"`, enclose strings with commas in double quotes in CSV files.
3. **NO broad market index ETFs**: Never use `SPY`, `QQQ`, `IWM`—the screener is strictly thematic.
4. **Specific Pure-Play Targets**: Sector SPDRs are prefixed in brackets `[XLI]`, followed by specific sub-industry tickers (e.g. `[XLI] IYT` or `[XLB] COPX`). For broad sector themes (e.g., `Industrials`), `[XLI] XLI` is used.

---

## 5. Quarterly & Yearly Review Protocol
As financial markets evolve, ETF issuers regularly launch new thematic pure-plays (e.g., `DRAM` for memory/storage) or close underperforming funds.

### Review Cadence:
* **Quarterly Review**: Conducted during quarterly portfolio rebalancing / backtesting (Jan, Apr, Jul, Oct).
* **Yearly Audit**: Full universe review in January.

### Checklist (Add / Update / Delete):
#### 1. ADD (New Thematic Launches)
* Inspect new thematic ETF offerings launched over the trailing quarter/year with growing institutional volume ($> \$25\text{M}$ AUM, average daily volume $> 50\text{k}$ shares).
* If a high-volume pure-play launches for a micro-theme (e.g., Quantum Computing, Nuclear SMRs, Advanced Packaging), add a dedicated micro-theme row in `data/theme_etf_mapping.csv`.

#### 2. UPDATE (Liquidity / Leadership Shifts)
* Check if a newer thematic fund has overtaken an older fund in volume, liquidity, or pure-play exposure.
* *Example*: Replacing a legacy broad tech ETF with a targeted pure-play if the pure-play becomes the consensus TradingView charting standard.

#### 3. DELETE / PRUNE (Delistings & Fund Closures)
* Check for ETF closures, liquidations, or reverse-splits.
* If a fund is discontinued, replace it with the next most liquid pure-play or remove it from the list.

---

## 6. Audit Helper Command
To quickly verify that all mapped themes in `data/theme_etf_mapping.csv` are properly formatted and valid, run:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/theme_etf_mapping.csv'); print('Entries:', len(df)); print('Sample:'); print(df.head(5))"
```
