# TABELA Codebase Housekeeping & Technical Debt Audit

**Date:** October 29, 2026  
**Status:** Audit & Recommendations (No code changes executed per user instruction)

---

## 1. Executive Summary

This housekeeping document provides a comprehensive audit of all source modules, configuration files, and documentation across the TABELA codebase. It catalogues dead code, structural anti-patterns, import-time side effects, monolithic modules, and opportunities for performance optimization to be tackled in planned maintenance sessions.

---

## 2. Module-by-Module Code Cleanup Flags

### 1. `reporting/presentation_engine.py` (🔴 High Priority)
* **Monolithic File Size (1,813 lines):**  
  This file combines terminal presentation, stdout capturing, string parsing/slicing, accumulator persistence, CSV ledger writing, and TradingView formatting into a single script.
  - *Recommendation:* Decompose into 3 focused engines:
    1. `reporting/presentation_formatter.py` (pure terminal rendering)
    2. `reporting/export_engine.py` (TradingView and dropped watchlist string generation)
    3. `reporting/reentry_engine.py` (re-entry scanning, tracking, and hold evaluation)
* **Top-Level Monkey-Patching (Line 12):**  
  `scoring.rotation_engine.print_rotation_report = lambda *args, **kwargs: None` suppresses terminal rotation reports by monkey-patching another module at import time.
  - *Recommendation:* Replace with a clean configuration flag (`ENABLE_ROTATION_CONSOLE_OUTPUT = False` in `config.py`) or remove the legacy call site.
* **Dead Code / Dormant Blocks (Lines 1519–1539):**  
  Contains orphaned `if False:` blocks and commented-out legacy JSON/TXT dropped exports (`dropped_list.json`, `dropped_list.txt`).
  - *Recommendation:* Safely delete these dormant dead-code blocks.
* **Regex / Stdout Capture Slicing:**  
  The scan captures terminal stdout into an `OutputCapturer` and uses `find_section_start()` and regex string searching to reorder sections in `print_scan_epilogue()`.
  - *Recommendation:* Transition to a structured render pipeline where sections are returned as strings or dataclasses, assembled in order, and printed once.

---

### 2. `data_layer/historical_intelligence_engine.py` (🟡 Medium Priority)
* **Top-Level Side Effects at Import Time (Lines 4–5):**  
  ```python
  history = load_history()
  queries = HistoricalQueries(history)
  ```
  Every time `historical_intelligence_engine` is imported (even for unit tests or utility scripts), it immediately scans and reads the filesystem for historical JSON files.
  - *Recommendation:* Encapsulate inside a lazy singleton or instantiate `HistoricalQueries` explicitly when required.

---

### 3. `themes/stock_mapper.py` (🟡 Medium Priority)
* **Extensive Hardcoded `if/elif` Chains (346 lines):**  
  Contains over 300 lines of sequential `if "..." in industry: return "..."` string matching.
  - *Recommendation:* Refactor into a dictionary lookup mapping keywords to theme categories. This simplifies maintenance and accelerates string lookup performance.

---

### 4. `scoring/scoring_engine.py` (🟢 Low Priority)
* **Inline Module Import (Line 128):**  
  `import numpy as np` is executed inside `calculate_short_rs_rating()`.
  - *Recommendation:* Move `import numpy as np` to the top-level module imports.

---

### 5. `runners/main.py` vs Root Scripts (🟢 Low Priority)
* **Duplicate / Legacy Run Scripts:**  
  `runners/main.py` is the primary entry point, but root-level runners (`run_cartesian_long.py`, `run_cartesian_short.py`) exist alongside batch files.
  - *Recommendation:* Standardize runners into `runners/` with clear CLI flags or entry scripts.

---

### 6. Documentation Gaps (🟡 Medium Priority)
* **Missing `docs/BACKTESTING_HANDOVER.md`:**  
  `AGENTS.md` line 10 lists `docs/BACKTESTING_HANDOVER.md` as mandatory reading, but the file does not exist on disk.
  - *Recommendation:* Consolidate historical handover notes and create `docs/BACKTESTING_HANDOVER.md` or update `AGENTS.md` reference.
* **`docs/ARCHITECTURE.md` Synchronization:**  
  *Completed:* Updated Section 3, Section 5, and Section 9 to reflect bidirectional theme breadth, the `dropped_history.csv` audit ledger, `reentry_tracker.json`, and the removal of the legacy 3-per-theme cap.

---

## 3. Prioritized Cleanup Plan

| Priority | Component | Item | Estimated Effort |
| :--- | :--- | :--- | :--- |
| **High** | `presentation_engine.py` | Remove dormant `if False:` blocks (Lines 1519–1539) | 15 mins |
| **High** | `presentation_engine.py` | Remove monkey-patch on `print_rotation_report` | 15 mins |
| **Medium** | `historical_intelligence_engine.py` | Remove import-time `load_history()` side effects | 30 mins |
| **Medium** | Documentation | Create or re-link `docs/BACKTESTING_HANDOVER.md` | 30 mins |
| **Medium** | `themes/stock_mapper.py` | Refactor 346-line if/elif chain to keyword dictionary | 1 hour |
| **Low** | `scoring_engine.py` | Hoist inline `import numpy` to top of file | 5 mins |
| **Low** | `presentation_engine.py` | Decompose monolithic 1,800+ line presentation file | 2–3 hours |

