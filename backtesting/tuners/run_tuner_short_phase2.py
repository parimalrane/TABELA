"""
TABELA SHORT ENGINE - PHASE 2: THEME PRECISION + SCORE TIGHTENING
==================================================================
Locked config: P3-C (YTD Reversal + RS Heavy + Fall From Grace)
Fixed filters: Min Price $10 | Min Volume 1,000,000

Phase 2 tests ONLY two variables:
  1. Theme inclusion (Neutral-only vs Neutral+Lagging)
  2. Score ceiling tightening (< 65, < 55, < 50, < 45, < 40)

Goal: Find the sweet spot where Win Rate > 70% with
      50-300 high-conviction trades per quarter.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_phase2.py"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
TODAY = datetime.now().strftime("%Y%m%d")
RESULTS_FILE = RESULTS_DIR / f"optimization_results_short_phase2_{TODAY}.csv"
os.makedirs(RESULTS_DIR, exist_ok=True)

# P3-C scoring formula — LOCKED, never changes
P3C_RS_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.20,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.40,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
P3C_COMPOSITE = {"RS_WEIGHT": 0.65, "THEME_WEIGHT": 0.20, "ZACKS_WEIGHT": 0.10, "GROWTH_WEIGHT": 0.05}
P3C_ZACKS = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}
P3C_GROWTH = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}

THEMES_NEUTRAL_ONLY = ["Neutral", "Unknown"]
THEMES_NEUTRAL_LAG  = ["Lagging", "Micro Laggard", "Neutral", "Unknown"]

EXPERIMENTS = [
    # Benchmark: current P3-C baseline (Neutral+Lagging, Score < 65) — already known
    {"name": "Baseline: Neutral+Lagging  | Score < 65 | RS 40-75", "themes": THEMES_NEUTRAL_LAG,  "max_score": 65.0, "min_rs": 40.0, "max_rs": 75.0},

    # Test 1: Remove Lagging — does Neutral-only improve WR?
    {"name": "T1: Neutral-Only          | Score < 65 | RS 40-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 65.0, "min_rs": 40.0, "max_rs": 75.0},

    # Test 2: Neutral-only + tighter score ceiling
    {"name": "T2: Neutral-Only          | Score < 55 | RS 40-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 55.0, "min_rs": 40.0, "max_rs": 75.0},
    {"name": "T3: Neutral-Only          | Score < 50 | RS 40-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 50.0, "min_rs": 40.0, "max_rs": 75.0},
    {"name": "T4: Neutral-Only          | Score < 45 | RS 40-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 45.0, "min_rs": 40.0, "max_rs": 75.0},
    {"name": "T5: Neutral-Only          | Score < 40 | RS 40-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 40.0, "min_rs": 40.0, "max_rs": 75.0},

    # Test 3: Neutral-only + tighter RS window (raise floor)
    {"name": "T6: Neutral-Only          | Score < 50 | RS 45-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 50.0, "min_rs": 45.0, "max_rs": 75.0},
    {"name": "T7: Neutral-Only          | Score < 50 | RS 50-75", "themes": THEMES_NEUTRAL_ONLY, "max_score": 50.0, "min_rs": 50.0, "max_rs": 75.0},
]


def write_config(exp):
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        content = f.read()

    rs_block = (
        'SHORT_RS_RAW_WEIGHTS = {\n'
        + "".join(f'    "{k}": {v},\n' for k, v in P3C_RS_WEIGHTS.items())
        + '}'
    )
    comp_block = (
        'SHORT_COMPOSITE_WEIGHTS = {\n'
        + "".join(f'    "{k}": {v},\n' for k, v in P3C_COMPOSITE.items())
        + '}'
    )
    zacks_str = ", ".join(f"{k}: {v}" for k, v in P3C_ZACKS.items())
    growth_str = ", ".join(f"'{k}': {v}" for k, v in P3C_GROWTH.items())
    themes_str = str(exp["themes"]).replace("'", '"')

    entry_block = (
        'SHORT_ENTRY = {\n'
        f'    "MIN_SHORT_RS": {exp["min_rs"]},\n'
        f'    "MAX_SHORT_RS": {exp["max_rs"]},\n'
        f'    "MAX_SHORT_SCORE": {exp["max_score"]},\n'
        f'    "THEMES": {themes_str},\n'
        '    "BLOCKED_ZACKS": [1, 2],\n'
        '    "MIN_PRICE": 10.0,\n'
        '    "MIN_VOLUME": 1000000,\n'
        '}'
    )

    content = re.sub(r'SHORT_RS_RAW_WEIGHTS\s*=\s*\{.*?\}', rs_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_COMPOSITE_WEIGHTS\s*=\s*\{.*?\}', comp_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_ZACKS_SCORE_MAP\s*=\s*\{.*?\}',  f'SHORT_ZACKS_SCORE_MAP = {{{zacks_str}}}', content)
    content = re.sub(r'SHORT_GROWTH_SCORE_MAP\s*=\s*\{.*?\}', f'SHORT_GROWTH_SCORE_MAP = {{{growth_str}}}', content)
    content = re.sub(r'SHORT_ENTRY\s*=\s*\{.*?\}', entry_block, content, flags=re.DOTALL)
    return content


def run_regression_silent():
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def run_backtest_silent():
    sys.path.insert(0, str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR / "backtesting"))
    import importlib
    for mod in list(sys.modules.keys()):
        if any(x in mod for x in ["config", "backtest", "scoring"]):
            try: importlib.reload(sys.modules[mod])
            except Exception: pass
    import backtest_engine
    importlib.reload(backtest_engine)
    return backtest_engine.run_backtest(mode="short", silent=True)


def main():
    total = len(EXPERIMENTS)
    print("=" * 80)
    print("     TABELA SHORT ENGINE — PHASE 2: THEME PRECISION + SCORE TIGHTENING")
    print(f"     {total} Experiments | P3-C Formula Locked | Volume > 1M | Price > $10")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print("\n[SAFETY] config.py backed up. Long engine will NOT be modified.\n")

    results = []
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        print(f"  [{idx}/{total}] {name}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(write_config(exp))

        reg_ok = run_regression_silent()
        if not reg_ok:
            print(f"         >>> [ERROR] Regression failed.")
            continue

        bt = run_backtest_silent()
        if not bt:
            continue

        lag_wr  = bt.get("lagging_win_rate", 0)
        neut_wr = bt.get("neutral_win_rate", 0)
        lag_t   = bt.get("lagging_trades", 0)
        neut_t  = bt.get("neutral_trades", 0)

        print(f"         >>> Trades: {bt['total_trades']:>4} | WR: {bt['win_rate']:>5}% | Avg: {bt['avg_return']:>5}% | Neutral: {neut_t} trades {neut_wr}% WR | Lagging: {lag_t} trades {lag_wr}% WR")

        results.append({
            "Name": name,
            "Themes": ",".join(exp["themes"]),
            "Score Ceiling": exp["max_score"],
            "Min RS": exp["min_rs"],
            "Max RS": exp["max_rs"],
            "Total Trades": bt["total_trades"],
            "Win Rate (%)": bt["win_rate"],
            "Avg Return (%)": bt["avg_return"],
            "Neutral Trades": neut_t,
            "Neutral WR (%)": neut_wr,
            "Lagging Trades": lag_t,
            "Lagging WR (%)": lag_wr,
        })

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py fully restored.")

    import pandas as pd
    df = pd.DataFrame(results)
    df = df.sort_values("Win Rate (%)", ascending=False)
    df.to_csv(RESULTS_FILE, index=False)

    print(f"\n{'='*80}")
    print(f"     COMPLETE | {RESULTS_FILE.name}")
    print(f"{'='*80}")
    print("\n" + df[["Name", "Total Trades", "Win Rate (%)", "Avg Return (%)"]].to_string(index=False))


if __name__ == "__main__":
    main()
