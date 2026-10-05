import os
import sys
import time
import pandas as pd
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
sys.path.insert(0, str(BASE_DIR))

import config.config as cfg
from backtesting.vectorized_backtest import VectorizedBacktestEngine
from backtesting.attribution.alpha_attribution import run_alpha_attribution
from backtesting.tuners.run_tuner import EXPERIMENTS

RESULTS_FILE = BASE_DIR / "backtesting" / "results" / "vectorized_optimization_results.csv"

def apply_overrides_to_config(exp):
    """
    Temporarily overrides global cfg variables using the experiment dict.
    We carefully overwrite the dictionaries/variables in cfg in place 
    so scoring_engine picks them up nicely. 
    """
    # Create a backup of the original so we can restore it easily
    backup = {
        "RS_RAW_WEIGHTS": cfg.RS_RAW_WEIGHTS.copy(),
        "PERIOD_WEIGHTS": cfg.THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"].copy(),
        "LONG_WEIGHTS": cfg.LONG_WEIGHTS.copy(),
        "ZACKS_SCORE_MAP": cfg.ZACKS_SCORE_MAP.copy(),
        "GROWTH_SCORE_MAP": cfg.GROWTH_SCORE_MAP.copy(),
        "LONG_ENTRY": cfg.LONG_ENTRY.copy(),
        "CLASSIFICATION_PERCENTAGE_LEADING": cfg.THEME_STRENGTH_CONFIG.get("CLASSIFICATION_PERCENTAGE_LEADING"),
        "CLASSIFICATION_PERCENTAGE_LAGGING": cfg.THEME_STRENGTH_CONFIG.get("CLASSIFICATION_PERCENTAGE_LAGGING")
    }
    
    if "RS_RAW_WEIGHTS" in exp:
        cfg.RS_RAW_WEIGHTS.update(exp["RS_RAW_WEIGHTS"])
    if "PERIOD_WEIGHTS" in exp:
        cfg.THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"].update(exp["PERIOD_WEIGHTS"])
    if "LONG_WEIGHTS" in exp:
        cfg.LONG_WEIGHTS.update(exp["LONG_WEIGHTS"])
    if "ZACKS_SCORE_MAP" in exp:
        cfg.ZACKS_SCORE_MAP.clear()
        cfg.ZACKS_SCORE_MAP.update(exp["ZACKS_SCORE_MAP"])
    if "GROWTH_SCORE_MAP" in exp:
        cfg.GROWTH_SCORE_MAP.clear()
        cfg.GROWTH_SCORE_MAP.update(exp["GROWTH_SCORE_MAP"])
        
    cfg.LONG_ENTRY["MIN_RS"] = exp.get("MIN_RS", backup["LONG_ENTRY"]["MIN_RS"])
    cfg.LONG_ENTRY["MIN_LONG_SCORE"] = exp.get("MIN_LONG_SCORE", backup["LONG_ENTRY"]["MIN_LONG_SCORE"])
    cfg.LONG_ENTRY["BLOCKED_ZACKS"] = exp.get("BLOCKED_ZACKS", backup["LONG_ENTRY"]["BLOCKED_ZACKS"])
    
    if "CLASSIFICATION_PERCENTAGE_LEADING" in exp:
        cfg.THEME_STRENGTH_CONFIG["CLASSIFICATION_PERCENTAGE_LEADING"] = exp["CLASSIFICATION_PERCENTAGE_LEADING"]
    if "CLASSIFICATION_PERCENTAGE_LAGGING" in exp:
        cfg.THEME_STRENGTH_CONFIG["CLASSIFICATION_PERCENTAGE_LAGGING"] = exp["CLASSIFICATION_PERCENTAGE_LAGGING"]
    
    return backup

def restore_config(backup):
    """Restore original config after experiment finishes."""
    cfg.RS_RAW_WEIGHTS.clear()
    cfg.RS_RAW_WEIGHTS.update(backup["RS_RAW_WEIGHTS"])
    
    cfg.THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"].clear()
    cfg.THEME_STRENGTH_CONFIG["PERIOD_WEIGHTS"].update(backup["PERIOD_WEIGHTS"])
    
    cfg.LONG_WEIGHTS.clear()
    cfg.LONG_WEIGHTS.update(backup["LONG_WEIGHTS"])
    
    cfg.ZACKS_SCORE_MAP.clear()
    cfg.ZACKS_SCORE_MAP.update(backup["ZACKS_SCORE_MAP"])
    
    cfg.GROWTH_SCORE_MAP.clear()
    cfg.GROWTH_SCORE_MAP.update(backup["GROWTH_SCORE_MAP"])
    
    cfg.LONG_ENTRY.clear()
    cfg.LONG_ENTRY.update(backup["LONG_ENTRY"])
    
    if backup["CLASSIFICATION_PERCENTAGE_LEADING"] is not None:
        cfg.THEME_STRENGTH_CONFIG["CLASSIFICATION_PERCENTAGE_LEADING"] = backup["CLASSIFICATION_PERCENTAGE_LEADING"]
    if backup["CLASSIFICATION_PERCENTAGE_LAGGING"] is not None:
        cfg.THEME_STRENGTH_CONFIG["CLASSIFICATION_PERCENTAGE_LAGGING"] = backup["CLASSIFICATION_PERCENTAGE_LAGGING"]

def main():
    print("=" * 80)
    print("    TABELA UNIFIED OPTIMIZATION UPGRADE (VECTORIZED IN-MEMORY)")
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
    
    print(f"\n[+] Executing {total} experiments sequentially in RAM...")
    
    # Reload config to baseline
    import importlib
    importlib.reload(cfg)

    # 3. Execution Loop
    for idx, exp in enumerate(EXPERIMENTS, 1):
        name = exp["name"]
        
        # Override config in memory
        bck = apply_overrides_to_config(exp)
        
        # Run Backtest
        exp_start = time.time()
        bt = engine.process(mode="long", silent=True)
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
            "Exec Time (s)": round(exp_time, 2)
        })
        
        # Restore configuration to baseline for next experiment
        restore_config(bck)

    total_time = time.time() - t0
    print(f"\n[+] Grid Search Complete. {total} experiments simulated in {total_time:.2f}s.")
    
    # Save Grid Search Results
    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_FILE, index=False)
    print(f"    Grid results saved to: {RESULTS_FILE}")
    
    # 4. Run Alpha Attribution on Baseline
    if baseline_df is not None:
        print("\n[+] Initializing Alpha Attribution on Baseline Data...")
        run_alpha_attribution(baseline_df, silent=False)

if __name__ == "__main__":
    main()
