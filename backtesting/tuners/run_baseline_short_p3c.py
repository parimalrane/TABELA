"""
TABELA SHORT ENGINE - P3-C BASELINE WITH LIQUIDITY FILTERS
============================================================
Locks the winning P3-C configuration (YTD Reversal + RS Heavy + Fall From Grace)
and applies real-world institutional liquidity filters:
  - Min Price: $10
  - Min Avg Volume: 1,000,000

Outputs:
  1. Terminal summary (trades, win rate, avg return)
  2. short_trade_detail_YYYYMMDD.csv with every individual trade
     - Sort by "Win" and "Return %" to see anatomy of best short setups
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
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_p3c_baseline.py"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
TODAY = datetime.now().strftime("%Y%m%d")
DETAIL_FILE = RESULTS_DIR / f"short_trade_detail_{TODAY}.csv"
os.makedirs(RESULTS_DIR, exist_ok=True)

# =============================================
# P3-C WINNING CONFIGURATION (LOCKED)
# YTD Reversal + RS Heavy + Fall From Grace
# 70.50% WR | +4.35% Avg Return (pre-liquidity)
# =============================================
P3C_RS_WEIGHTS = {
    "% Price Change (4 Weeks)": 0.30,
    "% Price Change (12 Weeks)": 0.20,
    "% Price Change (1 Week)": 0.10,
    "Relative Price Change (YTD)": 0.40,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
P3C_COMPOSITE = {
    "RS_WEIGHT": 0.65,
    "THEME_WEIGHT": 0.20,
    "ZACKS_WEIGHT": 0.10,
    "GROWTH_WEIGHT": 0.05,
}
P3C_ZACKS = {1: -100.0, 2: -50.0, 3: 20.0, 4: 80.0, 5: 100.0}
P3C_GROWTH = {'A': -50.0, 'B': 0.0, 'C': 50.0, 'D': 80.0, 'F': 100.0}
P3C_ENTRY = {
    "MIN_SHORT_RS": 40.0,
    "MAX_SHORT_RS": 75.0,
    "MAX_SHORT_SCORE": 65.0,
    "THEMES": ["Lagging", "Micro Laggard", "Neutral", "Unknown"],
    "BLOCKED_ZACKS": [1, 2],
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 1_000_000,
}


def write_p3c_config():
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        content = f.read()

    rs_block = (
        'SHORT_RS_RAW_WEIGHTS = {\n'
        f'    "% Price Change (4 Weeks)": {P3C_RS_WEIGHTS["% Price Change (4 Weeks)"]},\n'
        f'    "% Price Change (12 Weeks)": {P3C_RS_WEIGHTS["% Price Change (12 Weeks)"]},\n'
        f'    "% Price Change (1 Week)": {P3C_RS_WEIGHTS["% Price Change (1 Week)"]},\n'
        f'    "Relative Price Change (YTD)": {P3C_RS_WEIGHTS["Relative Price Change (YTD)"]},\n'
        f'    "Price as a % of 52 Wk H-L Range": {P3C_RS_WEIGHTS["Price as a % of 52 Wk H-L Range"]},\n'
        '}'
    )
    comp_block = (
        'SHORT_COMPOSITE_WEIGHTS = {\n'
        f'    "RS_WEIGHT": {P3C_COMPOSITE["RS_WEIGHT"]},\n'
        f'    "THEME_WEIGHT": {P3C_COMPOSITE["THEME_WEIGHT"]},\n'
        f'    "ZACKS_WEIGHT": {P3C_COMPOSITE["ZACKS_WEIGHT"]},\n'
        f'    "GROWTH_WEIGHT": {P3C_COMPOSITE["GROWTH_WEIGHT"]},\n'
        '}'
    )
    zacks_items = ", ".join(f"{k}: {v}" for k, v in P3C_ZACKS.items())
    growth_items = ", ".join(f"'{k}': {v}" for k, v in P3C_GROWTH.items())
    themes_str = str(P3C_ENTRY["THEMES"]).replace("'", '"')
    entry_block = (
        'SHORT_ENTRY = {\n'
        f'    "MIN_SHORT_RS": {P3C_ENTRY["MIN_SHORT_RS"]},\n'
        f'    "MAX_SHORT_RS": {P3C_ENTRY["MAX_SHORT_RS"]},\n'
        f'    "MAX_SHORT_SCORE": {P3C_ENTRY["MAX_SHORT_SCORE"]},\n'
        f'    "THEMES": {themes_str},\n'
        f'    "BLOCKED_ZACKS": [1, 2],\n'
        f'    "MIN_PRICE": {P3C_ENTRY["MIN_PRICE"]},\n'
        f'    "MIN_VOLUME": {P3C_ENTRY["MIN_VOLUME"]},\n'
        '}'
    )

    content = re.sub(r'SHORT_RS_RAW_WEIGHTS\s*=\s*\{.*?\}', rs_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_COMPOSITE_WEIGHTS\s*=\s*\{.*?\}', comp_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_ZACKS_SCORE_MAP\s*=\s*\{.*?\}', f'SHORT_ZACKS_SCORE_MAP = {{{zacks_items}}}', content)
    content = re.sub(r'SHORT_GROWTH_SCORE_MAP\s*=\s*\{.*?\}', f'SHORT_GROWTH_SCORE_MAP = {{{growth_items}}}', content)
    content = re.sub(r'SHORT_ENTRY\s*=\s*\{.*?\}', entry_block, content, flags=re.DOTALL)
    return content


def run_regression_silent():
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def main():
    print("=" * 80)
    print("  TABELA SHORT ENGINE — P3-C BASELINE + LIQUIDITY FILTER TEST")
    print(f"  Config: YTD Reversal + RS Heavy | Gate: RS 40-75 | Vol > 1M | Price > $10")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print("\n[SAFETY] config.py backed up. Long engine will NOT be modified.")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(write_p3c_config())
    print("[1/3] P3-C SHORT_* config written.")

    print("[2/3] Running regression...")
    reg_ok = run_regression_silent()
    if not reg_ok:
        shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
        os.remove(CONFIG_BACKUP)
        print("[ERROR] Regression failed. Config restored.")
        return

    print("[3/3] Running short backtest with liquidity filters...")

    sys.path.insert(0, str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR / "backtesting"))
    import importlib
    for mod in list(sys.modules.keys()):
        if any(x in mod for x in ["config", "backtest", "scoring"]):
            try:
                importlib.reload(sys.modules[mod])
            except Exception:
                pass

    import backtest_engine
    importlib.reload(backtest_engine)
    bt = backtest_engine.run_backtest(mode="short", silent=False)

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print("\n[SAFETY] Original config.py fully restored.")

    if bt and bt["total_trades"] > 0:
        detail_df = bt.get("_detail_df")
        if detail_df is not None and not detail_df.empty:
            # Sort: Winners first, then by best return
            detail_df = detail_df.sort_values(["Win", "Return %"], ascending=[False, False])
            detail_df.to_csv(DETAIL_FILE, index=False)
            print(f"\n[DETAIL] Trade-level CSV saved: {DETAIL_FILE.name}")
            print(f"         Open it and sort by 'Win' or 'Return %' to study the anatomy of your best shorts.\n")

        print(f"\n{'='*80}")
        print(f"  SUMMARY (P3-C + Liquidity Filters)")
        print(f"{'='*80}")
        print(f"  Total Trades : {bt['total_trades']}")
        print(f"  Win Rate     : {bt['win_rate']}%")
        print(f"  Avg Return   : {bt['avg_return']}%")
        print(f"  Lagging      : {bt['lagging_trades']} trades | {bt['lagging_win_rate']}% WR | {bt['lagging_avg_return']}% avg")
        print(f"  Neutral      : {bt['neutral_trades']} trades | {bt['neutral_win_rate']}% WR | {bt['neutral_avg_return']}% avg")
        print(f"{'='*80}\n")
    else:
        print("\nNo trades triggered. Check gate parameters or data availability.")


if __name__ == "__main__":
    main()
