import os
import sys
import time
import ast
import pandas as pd
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

import config.config as cfg
from backtesting.vectorized_backtest import VectorizedBacktestEngine
from backtesting.attribution.alpha_attribution import run_alpha_attribution
from backtesting.tuners.run_tuner_short_v2 import EXPERIMENTS

RESULTS_FILE = BASE_DIR / "backtesting" / "results" / "vectorized_optimization_results_short.csv"

def apply_overrides_to_config(exp):
    """
    Temporarily overrides global cfg SHORT_ENTRY variables using the experiment dict.
    We carefully overwrite the dictionaries/variables in cfg in place 
    so the scoring_engine picks them up nicely. 
    """
    backup = {
        "SHORT_ENTRY": cfg.SHORT_ENTRY.copy()
    }
    
    gate = exp["gate"]
    
    cfg.SHORT_ENTRY["MIN_SHORT_RS"] = float(gate.get("MIN_RS", backup["SHORT_ENTRY"]["MIN_SHORT_RS"]))
    cfg.SHORT_ENTRY["MAX_SHORT_RS"] = float(gate.get("MAX_RS", backup["SHORT_ENTRY"]["MAX_SHORT_RS"]))
    cfg.SHORT_ENTRY["MAX_SHORT_SCORE"] = float(gate.get("SCORE", backup["SHORT_ENTRY"]["MAX_SHORT_SCORE"]))
    
    if "themes" in exp:
        cfg.SHORT_ENTRY["THEMES"] = exp["themes"]
        
    if "blocked_zacks" in exp:
        # Evaluate string like "[1, 2, 3]"
        if isinstance(exp["blocked_zacks"], str):
            cfg.SHORT_ENTRY["BLOCKED_ZACKS"] = ast.literal_eval(exp["blocked_zacks"])
        else:
            cfg.SHORT_ENTRY["BLOCKED_ZACKS"] = exp["blocked_zacks"]
            
    if "min_volume" in exp:
        cfg.SHORT_ENTRY["MIN_VOLUME"] = int(exp["min_volume"])
    
    return backup

def restore_config(backup):
    """Restore original config after experiment finishes."""
    cfg.SHORT_ENTRY.clear()
    cfg.SHORT_ENTRY.update(backup["SHORT_ENTRY"])

def main():
    print("=" * 80)
    print("    TABELA UNIFIED OPTIMIZATION UPGRADE (SHORT VECTORIZED IN-MEMORY)")
    print("=" * 80)
    
    t0 = time.time()
    
    # 1. Initialize Engine and Load Data
    print("\n[+] Loading Stock Universe (JSON + CSV) into Pandas Matrix...")
    engine = VectorizedBacktestEngine()
    if not engine.load_data():
        print("[-] Failed to load matrix.")
        return
        
    master_time = time.time() - t0
    print(f"    Matrix built in {master_time:.2f} seconds. Rows: {len(engine.master_matrix)}")
    
    if len(engine.all_dates) == 0:
        print("[-] No dates found.")
        return

    # 2. Setup Loop
    total = len(EXPERIMENTS)
    results = []
    baseline_df = None
    
    print(f"\n[+] Executing {total} SHORT experiments sequentially in RAM...")
    
    import importlib
    importlib.reload(cfg)

    # 3. Execution Loop
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        
        # Override config in memory
        bck = apply_overrides_to_config(exp)
        
        # Run Backtest in mode="short"
        exp_start = time.time()
        bt = engine.process(mode="short", silent=True)
        exp_time = time.time() - exp_start
        
        if "Baseline" in name:
            baseline_df = bt["_detail_df"]
            
        strong_trades = bt["strong_trades"]
        strong_wr = bt["strong_win_rate"]
        
        print(f"    {idx:02d}/{total} | {name:<45} | Trades: {strong_trades:<3} | WR: {strong_wr:>5.1f}% | ({exp_time:.2f}s)")
        
        results.append({
            "Experiment": idx,
            "Name": name,
            "Hypothesis": exp.get("hypothesis", ""),
            "Total Trades": bt["total_trades"],
            "Win Rate (%)": bt["win_rate"],
            "Avg Return (%)": bt["avg_return"],
            "Strong Trades": bt["strong_trades"],
            "Strong WR (%)": bt["strong_win_rate"],
            "Strong Avg (%)": bt["strong_avg_return"],
            "Mild Trades": bt["mild_trades"],
            "Mild WR (%)": bt["mild_win_rate"],
            "Mild Avg (%)": bt["mild_avg_return"],
            "Deep Retrace Trades": bt["deep_retrace_trades"],
            "Deep Retrace WR (%)": bt["deep_retrace_win_rate"],
            "Deep Retrace Avg (%)": bt["deep_retrace_avg_return"],
            "Exec Time (s)": round(exp_time, 2)
        })
        
        restore_config(bck)

    total_time = time.time() - t0
    print(f"\n[+] Grid Search Complete. {total} SHORT experiments simulated in {total_time:.2f}s.")
    
    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_FILE, index=False)
    print(f"    Grid results saved to: {RESULTS_FILE}")
    
    if baseline_df is not None and not baseline_df.empty:
        print("\n[+] Initializing Alpha Attribution on Baseline Short Data...")
        try:
            run_alpha_attribution(baseline_df, mode="short", silent=False)
        except TypeError:
            # Fallback if run_alpha_attribution doesn't support mode="short" yet
            run_alpha_attribution(baseline_df, silent=False)

if __name__ == "__main__":
    main()
