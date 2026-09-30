"""
TABELA AUTO-TUNER PHASE 3: Targeted Missing Combos
====================================================
Fills the gaps from Phase 1+2 results. Only runs the specific
combinations we haven't tested yet.
"""

import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("c:/TABELA")
CONFIG_PATH = BASE_DIR / "config" / "config.py"
CONFIG_BACKUP = BASE_DIR / "config" / "config_backup_tuner.py"
RESULTS_FILE = BASE_DIR / "optimization_results_phase3.csv"

# --- Reusable building blocks ---
RS_CURRENT = {
    "% Price Change (4 Weeks)": 0.50, "% Price Change (12 Weeks)": 0.40,
    "% Price Change (1 Week)": 0.10, "Relative Price Change (YTD)": 0.00,
    "Price as a % of 52 Wk H-L Range": 0.00,
}
THEME_CURRENT = {
    "Performance 1M (%)": 0.40, "Performance 1W (%)": 0.35,
    "Performance 3M (%)": 0.25, "Performance 6M (%)": 0.00,
    "Performance 1Y (%)": 0.00, "Performance 1D (%)": 0.00,
}

COMP_CURRENT = {"RS_WEIGHT": 0.50, "THEME_WEIGHT": 0.25, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}
COMP_THEME_HEAVY = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.35, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.10}
COMP_EQUAL = {"RS_WEIGHT": 0.40, "THEME_WEIGHT": 0.30, "ZACKS_WEIGHT": 0.15, "GROWTH_WEIGHT": 0.15}

ZACKS_BINARY = {1: 100.0, 2: 100.0, 3: 0.0, 4: -50.0, 5: -100.0}
GROWTH_FLAT = {"A": 100.0, "B": 95.0, "C": 90.0, "D": 20.0, "F": -50.0}
GROWTH_FIBONACCI = {"A": 100.0, "B": 78.6, "C": 61.8, "D": 38.2, "F": 0.0}


def make_combo(name, hypothesis, comp, zacks, growth, min_rs, min_score):
    return {
        "name": name, "hypothesis": hypothesis,
        "RS_RAW_WEIGHTS": RS_CURRENT, "PERIOD_WEIGHTS": THEME_CURRENT,
        "LONG_WEIGHTS": comp, "ZACKS_SCORE_MAP": zacks, "GROWTH_SCORE_MAP": growth,
        "MIN_RS": min_rs, "MIN_LONG_SCORE": min_score,
        "CLASSIFICATION_PERCENTAGE_LEADING": 0.30,
        "CLASSIFICATION_PERCENTAGE_LAGGING": 0.30,
        "BLOCKED_ZACKS": [4, 5],
    }


EXPERIMENTS = [
    # GAP 1: The obvious missing piece
    make_combo("90/85 + Binary Zacks + Fibonacci Growth",
               "The missing link: Binary Zacks + Fibonacci Growth at the wider 90/85 gate.",
               COMP_CURRENT, ZACKS_BINARY, GROWTH_FIBONACCI, 90.0, 85.0),

    # GAP 2: Binary Zacks + Theme Heavy
    make_combo("90/85 + Binary Zacks + Theme Heavy",
               "Does Theme Heavy composite amplify Binary Zacks at 90/85?",
               COMP_THEME_HEAVY, ZACKS_BINARY, GROWTH_FLAT, 90.0, 85.0),

    # GAP 3: Binary Zacks + Theme Heavy + Fibonacci Growth (Ultimate MEGA)
    make_combo("90/85 + Binary Zacks + Theme Heavy + Fib Growth",
               "The ultimate stack: Binary + Theme Heavy + Fibonacci at 90/85.",
               COMP_THEME_HEAVY, ZACKS_BINARY, GROWTH_FIBONACCI, 90.0, 85.0),

    # GAP 4: Binary Zacks + Equal Split  
    make_combo("90/85 + Binary Zacks + Equal Split",
               "Does Equal Split composite work with Binary Zacks?",
               COMP_EQUAL, ZACKS_BINARY, GROWTH_FLAT, 90.0, 85.0),

    # GAP 5: Binary Zacks + Equal Split + Fibonacci
    make_combo("90/85 + Binary Zacks + Equal Split + Fib Growth",
               "Equal Split + full fundamental strictness at 90/85.",
               COMP_EQUAL, ZACKS_BINARY, GROWTH_FIBONACCI, 90.0, 85.0),

    # GAP 6: Isolate Fibonacci at 90/90 (was it Binary or Fib that made #25 win?)
    make_combo("90/90 + Binary Zacks + Flat Growth",
               "Isolate: Did Fibonacci Growth actually help the Sniper, or was it all Binary Zacks?",
               COMP_CURRENT, ZACKS_BINARY, GROWTH_FLAT, 90.0, 90.0),
]


def generate_config_content(exp):
    pw = exp["PERIOD_WEIGHTS"]
    lw = exp["LONG_WEIGHTS"]
    rs = exp["RS_RAW_WEIGHTS"]
    zsm = exp["ZACKS_SCORE_MAP"]
    gsm = exp["GROWTH_SCORE_MAP"]
    blocked = exp.get("BLOCKED_ZACKS", [4, 5])

    content = f'''THEME_STRENGTH_CONFIG = {{
    "BENCHMARK_TICKER": "SPY",
    "PERIOD_WEIGHTS": {{
        "Performance 1M (%)": {pw.get("Performance 1M (%)", 0.0)},
        "Performance 1W (%)": {pw.get("Performance 1W (%)", 0.0)},
        "Performance 3M (%)": {pw.get("Performance 3M (%)", 0.0)},
        "Performance 6M (%)": {pw.get("Performance 6M (%)", 0.0)},
        "Performance 1Y (%)": {pw.get("Performance 1Y (%)", 0.0)},
        "Performance 1D (%)": {pw.get("Performance 1D (%)", 0.0)},
    }},
    "AGGREGATION_MODE": "aum_weighted",
    "ENABLE_NORMALIZATION": True,
    "CLASSIFICATION_PERCENTAGE_LEADING": {exp["CLASSIFICATION_PERCENTAGE_LEADING"]},
    "CLASSIFICATION_PERCENTAGE_LAGGING": {exp["CLASSIFICATION_PERCENTAGE_LAGGING"]}
}}

LONG_WEIGHTS = {{
    "RS_WEIGHT": {lw["RS_WEIGHT"]},
    "THEME_WEIGHT": {lw["THEME_WEIGHT"]},
    "ZACKS_WEIGHT": {lw["ZACKS_WEIGHT"]},
    "GROWTH_WEIGHT": {lw["GROWTH_WEIGHT"]}
}}

RS_RAW_WEIGHTS = {{
    "% Price Change (4 Weeks)": {rs.get("% Price Change (4 Weeks)", 0.0)},
    "% Price Change (12 Weeks)": {rs.get("% Price Change (12 Weeks)", 0.0)},
    "% Price Change (1 Week)": {rs.get("% Price Change (1 Week)", 0.0)},
    "Relative Price Change (YTD)": {rs.get("Relative Price Change (YTD)", 0.0)},
    "Price as a % of 52 Wk H-L Range": {rs.get("Price as a % of 52 Wk H-L Range", 0.0)}
}}

ZACKS_SCORE_MAP = {{{", ".join(f"{k}: {v}" for k, v in zsm.items())}}}
GROWTH_SCORE_MAP = {{{", ".join(f"'{k}': {v}" for k, v in gsm.items())}}}

LONG_ENTRY = {{
    "MIN_RS": {exp["MIN_RS"]},
    "MIN_LONG_SCORE": {exp["MIN_LONG_SCORE"]},
    "THEMES": ["Leading", "Neutral", "Unclassified Leader", "Unknown"],
    "BLOCKED_ZACKS": {blocked},
    "MIN_PRICE": 10.0,
    "MIN_VOLUME": 300000,
    "MIN_DROPPED_WATCH_SCORE": 70.0
}}

DIST_ENTRY = {{
    "MAX_RS": 10.0,
    "MAX_LONG_SCORE": 20.0,
    "THEMES": ["Lagging", "Micro Laggard"],
    "MICRO_BREAKAWAY_PERCENTILE": 0.05,
    "BLOCKED_ZACKS": [1, 2],
    "MAX_DROPPED_WATCH_SCORE": 30.0
}}
'''
    return content


def run_regression_silent():
    result = subprocess.run(
        ["python", str(BASE_DIR / "runners" / "run_historical.py")],
        cwd=str(BASE_DIR), capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
    )
    return result.returncode == 0


def run_backtest_silent():
    sys.path.insert(0, str(BASE_DIR))
    import importlib
    for mod in ["config.config", "scoring.scoring_engine", "scoring.long_scoring_engine", "backtest"]:
        if mod in sys.modules:
            importlib.reload(sys.modules[mod])
    from backtest import run_backtest
    return run_backtest(silent=True)


def main():
    total = len(EXPERIMENTS)
    print("=" * 80)
    print("     TABELA AUTO-TUNER PHASE 3: Targeted Missing Combos")
    print(f"     {total} Experiments | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    shutil.copy2(CONFIG_PATH, CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py backed up.")

    results = []
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        print(f"\n{'='*80}")
        print(f"  EXPERIMENT {idx}/{total}: {name}")
        print(f"  {exp['hypothesis']}")
        print(f"{'='*80}")

        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(generate_config_content(exp))
        print(f"  [1/3] Config rewritten.")

        t0 = time.time()
        print(f"  [2/3] Running regression...")
        reg_ok = run_regression_silent()
        reg_time = round(time.time() - t0, 1)

        if not reg_ok:
            print(f"  [ERROR] Regression failed.")
            results.append({"Experiment": idx, "Name": name, "Total Trades": "ERROR",
                            "Win Rate (%)": "ERROR", "Avg Return (%)": "ERROR",
                            "Leading Trades": "ERROR", "Leading WR (%)": "ERROR", "Leading Avg (%)": "ERROR",
                            "Neutral Trades": "ERROR", "Neutral WR (%)": "ERROR", "Neutral Avg (%)": "ERROR",
                            "Time (s)": reg_time})
            continue

        print(f"  [2/3] Regression complete in {reg_time}s.")
        print(f"  [3/3] Running backtest...")
        bt = run_backtest_silent()
        if bt is None:
            bt = {"total_trades": 0, "win_rate": 0.0, "avg_return": 0.0,
                  "neutral_trades": 0, "neutral_win_rate": 0.0, "neutral_avg_return": 0.0,
                  "leading_trades": 0, "leading_win_rate": 0.0, "leading_avg_return": 0.0}

        print(f"  >>> Trades: {bt['total_trades']} | Win Rate: {bt['win_rate']}% | Avg Return: {bt['avg_return']}%")
        results.append({"Experiment": idx, "Name": name,
                        "Total Trades": bt["total_trades"], "Win Rate (%)": bt["win_rate"],
                        "Avg Return (%)": bt["avg_return"],
                        "Leading Trades": bt["leading_trades"], "Leading WR (%)": bt["leading_win_rate"],
                        "Leading Avg (%)": bt["leading_avg_return"],
                        "Neutral Trades": bt["neutral_trades"], "Neutral WR (%)": bt["neutral_win_rate"],
                        "Neutral Avg (%)": bt["neutral_avg_return"],
                        "Time (s)": reg_time})

    shutil.copy2(CONFIG_BACKUP, CONFIG_PATH)
    os.remove(CONFIG_BACKUP)
    print(f"\n[SAFETY] Original config.py restored.")

    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_FILE, index=False)
    print(f"\n{'='*80}")
    print(f"     PHASE 3 COMPLETE | Results: {RESULTS_FILE}")
    print(f"{'='*80}")
    print("\n" + df.sort_values("Win Rate (%)", ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
