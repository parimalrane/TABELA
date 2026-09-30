import os
import sys
import subprocess
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
BACKTEST_DIR = BASE_DIR / "backtesting"
TUNERS_DIR = BACKTEST_DIR / "tuners"
RESULTS_DIR = BACKTEST_DIR / "results"

def run_all_tuners():
    """
    Executes every historical Tuner sequentially (Long grid search, combis, and shorts),
    then aggregates all of their separate output CSVs into a single master file.
    """
    print("=" * 80)
    print("      TABELA QUARTERLY MASTER AUTO-TUNER")
    print("=" * 80)
    
    tuners = [
        "run_tuner.py",
        "run_tuner_phase2.py",
        "run_tuner_phase3.py",
        "run_tuner_short.py",
        "run_tuner_short_floor.py"
    ]
    
    # 1. Execute all Python tuner scripts
    for tuner in tuners:
        tuner_path = TUNERS_DIR / tuner
        if tuner_path.exists():
            print(f"\n[EXECUTING]: {tuner}")
            subprocess.run([sys.executable, str(tuner_path)], cwd=str(BASE_DIR))
        else:
            print(f"\n[NOT FOUND]: {tuner}")
            
    # 2. Automatically consolidate results
    consolidate_only()

def consolidate_only():
    """
    Gathers any optimization result CSVs in the results directory,
    combines them into one master date-stamped file, and deletes the fragments.
    """
    today = datetime.now().strftime("%Y%m%d")
    
    # Find all CSVs that aren't already a master file
    csv_files = [f for f in glob.glob(str(RESULTS_DIR / "*.csv")) if "master_optimization" not in os.path.basename(f)]
    
    if not csv_files:
        print("\nNo fragmented CSV files found to merge.")
        return

    dfs = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            # Add a column indicating which tuner generated this row
            source_name = os.path.basename(file).replace(".csv", "").replace(f"_{today}", "")
            df.insert(0, "Tuner_Source", source_name)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if dfs:
        # Merge all dataframes (handles differing columns automatically with NaN for missing)
        master_df = pd.concat(dfs, ignore_index=True)
        
        # Pull the most important columns to the very front for easy reading
        cols = list(master_df.columns)
        priority_cols = ["Tuner_Source", "Experiment", "Name", "Total Trades", "Win Rate (%)", "Avg Return (%)"]
        
        # Re-arrange
        for c in reversed(priority_cols):
            if c in cols:
                cols.insert(0, cols.pop(cols.index(c)))
        master_df = master_df[cols]
        
        # Save to single master file
        master_name = RESULTS_DIR / f"master_optimization_results_{today}.csv"
        master_df.to_csv(master_name, index=False)
        
        print(f"\n[SUCCESS] Merged {len(csv_files)} test files into: {master_name.name}")
        
        # Clean up the individual fragments
        for file in csv_files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Could not delete {file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--merge-only":
        consolidate_only()
    else:
        run_all_tuners()
