# Thematic ETF Mapping Guide & Review Protocol

## 1. Overview & TradingView Utility
TABELA displays top-weighted, pure-play thematic ETFs directly alongside stock breadth leaders in the **THEME BREADTH ANALYSIS** terminal table.

### Primary Purpose:
* **Top-Down Sector Context**: Identifies the parent sector ETF (e.g. `[XLK]`, `[XLE]`, `[XLV]`, `[XLF]`, `[XLU]`).
* **Sub-Industry Pure-Play Charting**: Provides the primary 1–2 institutional charting vehicles (e.g. `SMH, SOXX` for Semis, `CRAK` for Refiners, `DRAM` for Memory, `CIBR, BUG` for Cybersecurity) for immediate cross-referencing on TradingView.

---

## 2. File Location & Data Structure
The mapping lives at:
`data/theme_etf_mapping.csv`

### Schema:
| Column | Description | Example |
| :--- | :--- | :--- |
| `Theme` | Micro Theme or Macro Theme name | `Cybersecurity` or `Semiconductors` |
| `Top_ETFs` | Formatted string: `[SECTOR] PURE_PLAY_1, PURE_PLAY_2` | `[XLK] CIBR, BUG` |
| `Description` | Human-readable explanation of theme scope | `Cybersecurity Pure-Plays` |

### Fallback Hierarchy:
When rendering each row in the terminal:
1. Exact match on **Micro Theme** (e.g., `Memory` $\rightarrow$ `[XLK] DRAM`).
2. If no micro entry exists, automatically falls back to **Macro Theme** (e.g., `Optical Networking` $\rightarrow$ parent `Semiconductors` $\rightarrow$ `[XLK] SMH, SOXX`).
3. If unmapped, gracefully outputs blank.

---

## 3. Formatting Rules
To maintain crisp terminal table alignment without truncation or excessive line-wrapping:
1. **Always prefix with parent Sector SPDR tag**: `[XLK]`, `[XLE]`, `[XLV]`, `[XLF]`, `[XLI]`, `[XLB]`, `[XLU]`, `[XLY]`, `[XLP]`, `[XLRE]`.
2. **Cap pure-play ETFs at 1 or 2 tickers**: Maximum string length must stay $\le 18$ characters (e.g., `[XLK] CIBR, BUG` is 15 chars).
3. **NO broad market index ETFs**: Never use `SPY`, `QQQ`, `IWM`—the screener is strictly thematic.
4. **NO generic sector SPDRs as the pure-play target**: `XLK` goes in brackets `[XLK]`, followed by the specific sub-industry ticker (e.g. `SMH`).

---

## 4. Quarterly & Yearly Review Protocol

As financial markets evolve, ETF issuers regularly launch new thematic pure-plays (e.g., `DRAM` in 2026 for memory/storage) or close underperforming funds. 

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

## 5. Audit Helper Command
To quickly verify that all mapped themes in `data/theme_etf_mapping.csv` are properly formatted and valid, run:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/theme_etf_mapping.csv'); print('Entries:', len(df)); print('Max length:', df['Top_ETFs'].str.len().max()); print('Over 18 chars:', df[df['Top_ETFs'].str.len() > 18])"
```
Ensure `Over 18 chars` returns 0 rows.
