import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_floor.py"
RESULTS_FILE = BASE_DIR / "backtesting" / "results" / "optimization_results_short_floor.csv"


EXPERIMENTS = [
    {"name": "No Floor (Current Wide Gate)", "min_rs": 0.0},
    {"name": "Floor RS > 2 (Skip bottom 2%)", "min_rs": 2.0},
    {"name": "Floor RS > 5 (Skip bottom 5%)", "min_rs": 5.0},
    {"name": "Floor RS > 8 (Skip bottom 8%)", "min_rs": 8.0},
]


def generate_short_config(exp):
    with open(CONFIG_BACKUP, "r", encoding="utf-8") as f:
        original = f.read()
    
    import re
    # We inject MIN_RS_SHORT into DIST_ENTRY
    new_dist_entry = f'''DIST_ENTRY = {{
    "MIN_RS_SHORT": {exp["min_rs"]},
    "MAX_RS": 15.0,
    "MAX_LONG_SCORE": 25.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
}}'''
    
    modified = re.sub(r'DIST_ENTRY\s*=\s*\{.*?\}(?=\n|\Z)', new_dist_entry, original, flags=re.DOTALL)
    return modified


def run_regression_silent():
    result = subprocess.run(
        ["python", str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0

def run_backtest(mode="short", silent=True):
    # Update backtest_short to respect MIN_RS_SHORT
    backtest_path = BASE_DIR / "backtest_short.py"
    with open(backtest_path, "r", encoding="utf-8") as f:
        bt_code = f.read()
    
    # Safely inject the min_rs_short logic into backtest_short
    if "min_rs_short = DIST_ENTRY.get(\"MIN_RS_SHORT\", 0.0)" not in bt_code:
        bt_code = bt_code.replace('max_rs = DIST_ENTRY.get("MAX_RS", 10.0)', 
                                  'max_rs = DIST_ENTRY.get("MAX_RS", 10.0)\n    min_rs_short = DIST_ENTRY.get("MIN_RS_SHORT", 0.0)')
        bt_code = bt_code.replace('if long_score <= max_score and rs_rating <= max_rs and theme_class in allowed_themes:',
                                  'if long_score <= max_score and rs_rating <= max_rs and rs_rating > min_rs_short and theme_class in allowed_themes:')
        with open(backtest_path, "w", encoding="utf-8") as f:
            f.write(bt_code)

    sys.path.insert(0, str(BASE_DIR))
    import importlib
    for mod in ["config.config", "scoring.scoring_engine", "scoring.long_scoring_engine", "backtest_short"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    from backtesting.backtest_engine import run_backtest_short
    return run_backtest(silent=True)


def main():
    print("=" * 80)
    print("     SHORT ENGINE: Terminal Oversold Floor Test")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)

    results = []
    for exp in EXPERIMENTS:
        name = exp["name"]
        print(f"\n  Running: {name}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(generate_short_config(exp))

        run_regression_silent()
        bt = run_backtest(mode="short", silent=True)

        if bt:
            print(f"  >>> Trades: {bt['total_trades']} | Win Rate: {bt['win_rate']}% | Avg Profit: {bt['avg_return']}%")
            results.append({"Experiment": name, "Win Rate (%)": bt["win_rate"], "Avg Return (%)": bt["avg_return"], "Trades": bt["total_trades"]})

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    
    # Revert backtest_short to original state
    subprocess.run(["git", "restore", "backtest_short.py"], cwd=str(BASE_DIR), capture_output=True)

    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print("\n" + df.to_string(index=False))

if __name__ == "__main__":
    main()
