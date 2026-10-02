"""
TABELA QUARTERLY AUTO-TUNER (MASTER EXECUTION)
===================================================
Run this once a quarter to execute the full state-space
grid search across both the Long and Short pipelines.

It executes the 30 Long experiments, restores the config,
then executes the 14 Short V2 experiments, and produces
a unified Quarterly Report in `backtesting/results`.

Usage: python run_quarterly_tuner.py
"""

import sys
import os
import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
import glob

BASE_DIR = Path("c:/TABELA")
TUNER_DIR = BASE_DIR / "backtesting" / "tuners"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"

LONG_SCRIPT = TUNER_DIR / "run_tuner.py"
SHORT_SCRIPT = TUNER_DIR / "run_tuner_short_v2.py"
PULLBACK_SCRIPT = BASE_DIR / "backtesting" / "attribution" / "run_pullback_tuner.py"
ATTRIBUTION_SCRIPT = BASE_DIR / "backtesting" / "attribution" / "run_alpha_attribution.py"

def inject_golden_configs():
    print("\n>>> STEP 2: INJECTING GOLDEN CONFIGURATION")
    # Read Long Winners
    long_csv = RESULTS_DIR / "optimization_results.csv"
    if not long_csv.exists():
        print("[ERROR] Long results missing.")
        return False
        
    long_df = pd.read_csv(long_csv, skipinitialspace=True)
    if "Win Rate (%)" in long_df.columns:
        long_df = long_df.sort_values(by=["Win Rate (%)", "Avg Return (%)"], ascending=[False, False])
    else:
        long_df = long_df.sort_values(by=["WR%", "AvgReturn%"], ascending=[False, False])
        
    best_long_name = str(long_df.iloc[0]["Name"]).strip()
    
    # Read Short Winners (most recent)
    short_csvs = glob.glob(str(RESULTS_DIR / "optimization_results_short_v2_*.csv"))
    if not short_csvs:
        print("[ERROR] Short results missing.")
        return False
        
    latest_short_csv = max(short_csvs, key=os.path.getctime)
    short_df = pd.read_csv(latest_short_csv, skipinitialspace=True)
    short_df = short_df.sort_values(by=["WR%", "AvgReturn%"], ascending=[False, False])
    best_short_name = str(short_df.iloc[0]["Name"]).strip()

    print(f"  [+] Absolute Long Winner: {best_long_name}")
    print(f"  [+] Absolute Short Winner: {best_short_name}")
    print("  [+] Overwriting production config.py...")

    sys.path.insert(0, str(TUNER_DIR))
    import run_tuner as rt
    import run_tuner_short_v2 as rts
    import re
    
    # 1. Generate and Write the Winning Long Config (contains baseline short vars internally)
    long_exp = next((e for e in rt.EXPERIMENTS if e["name"] == best_long_name), rt.EXPERIMENTS[0])
    config_content = rt.generate_config_content(long_exp)
    
    CONFIG_PATH = BASE_DIR / "config" / "config.py"
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(config_content)
        
    # 2. Extract the Winning Short Config parameters
    short_exp = next((e for e in rts.EXPERIMENTS if e["name"] == best_short_name), rts.EXPERIMENTS[0])
    rs = short_exp["rs_weights"]
    comp = short_exp["comp"]
    zacks = short_exp["zacks"]
    growth = short_exp["growth"]
    gate = short_exp["gate"]

    # 3. Read the injected Long Config, and regex replace the Short variables block
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    rs_block = (f'SHORT_RS_RAW_WEIGHTS = {{\n' + "".join(f'    "{k}": {v},\n' for k,v in rs.items()) + f'}}')
    comp_block = (f'SHORT_COMPOSITE_WEIGHTS = {{\n' + "".join(f'    "{k}": {v},\n' for k,v in comp.items()) + f'}}')
    zacks_str = ", ".join(f"{k}: {v}" for k, v in zacks.items())
    growth_str = ", ".join(f"'{k}': {v}" for k, v in growth.items())
    
    entry_block = (
        f'SHORT_ENTRY = {{\n'
        f'    "MIN_SHORT_RS": {gate["MIN_SHORT_RS"]},\n'
        f'    "MAX_SHORT_RS": {gate["MAX_SHORT_RS"]},\n'
        f'    "MAX_SHORT_SCORE": {gate["MAX_SHORT_SCORE"]},\n'
        f'    "THEMES": ["Lagging", "Micro Laggard"],\n'
        f'    "BLOCKED_ZACKS": [1, 2],\n'
        f'    "MIN_PRICE": 10.0,\n'
        f'    "MIN_VOLUME": 1000000\n'
        f'}}'
    )

    content = re.sub(r'SHORT_RS_RAW_WEIGHTS\s*=\s*\{.*?\}', rs_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_COMPOSITE_WEIGHTS\s*=\s*\{.*?\}', comp_block, content, flags=re.DOTALL)
    content = re.sub(r'SHORT_ZACKS_SCORE_MAP\s*=\s*\{.*?\}', f"SHORT_ZACKS_SCORE_MAP = {{{zacks_str}}}", content, flags=re.DOTALL)
    content = re.sub(r'SHORT_GROWTH_SCORE_MAP\s*=\s*\{.*?\}', f"SHORT_GROWTH_SCORE_MAP = {{{growth_str}}}", content, flags=re.DOTALL)
    content = re.sub(r'SHORT_ENTRY\s*=\s*\{.*?\}', entry_block, content, flags=re.DOTALL)
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    
    return True

def run_quarterly_master():
    # Setup dual-logging to capture all stdout for analysis while still displaying to user
    log_file = BASE_DIR / "backtesting" / "results" / "master_execution_log.txt"
    
    class DualLogger:
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "w", encoding="utf-8")
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
            self.log.flush()
        def flush(self):
            self.terminal.flush()
            self.log.flush()
            
    sys.stdout = DualLogger(log_file)
    sys.stderr = sys.stdout

    print("=" * 80)
    print(f"    TABELA QUARTERLY MASTER BACKTEST SUITE (PHASE 1-4)")
    print(f"    Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. Execute Long & Short Tests
    print("\n>>> STEP 1: LONG & SHORT GRID SEARCH")
    try:
        subprocess.run([sys.executable, str(LONG_SCRIPT)], cwd=str(BASE_DIR), check=True)
        subprocess.run([sys.executable, str(SHORT_SCRIPT)], cwd=str(BASE_DIR), check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] Base Grid Search Failed.")
        sys.exit(1)

    # 2. Extract Win Rates and Overwrite Live Config mathematically
    try:
        if not inject_golden_configs():
            sys.exit(1)
    except Exception as e:
        import traceback
        print("\n\n[FATAL ERROR IN STEP 2]")
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)

    # 3. Re-run historical memory baseline (Golden Run)
    print("\n>>> STEP 3: EXECUTING GOLDEN HISTORICAL REGRESSION")
    try:
        subprocess.run([sys.executable, str(BASE_DIR / "runners" / "run_historical.py")], cwd=str(BASE_DIR), check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] Golden Regression Failed.")
        sys.exit(1)

    # 4. Pullback MFE Tuning & Attribution Profiling
    print("\n>>> STEP 4: ALPHA ATTRIBUTION & MFE PROFILING")
    
    try:
        print("\n--- PULLBACK & RELIEF RALLY TIMING ---")
        subprocess.run([sys.executable, str(PULLBACK_SCRIPT)], cwd=str(BASE_DIR), check=True)
        
        print("\n--- FUNDAMENTAL EDGE ATTRIBUTION ---")
        subprocess.run([sys.executable, str(ATTRIBUTION_SCRIPT)], cwd=str(BASE_DIR), check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] Attribution Profiling Failed.")

    print("\n\n======================================================================")
    print("   QUARTERLY ENGINE SUPER-CYCLE COMPLETE.")
    print("   The system is now fully tuned, loaded with Golden Memory,")
    print("   and armed for tomorrow's main.bat execution.")
    print(f"   Execution Log Saved: {log_file}")
    print("======================================================================")
    
    # Restore stdout
    sys.stdout = sys.stdout.terminal

if __name__ == "__main__":
    run_quarterly_master()
