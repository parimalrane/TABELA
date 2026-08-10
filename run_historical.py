import os
import shutil
import subprocess
from pathlib import Path
import re

def main():
    base_dir = Path("c:/TABELA")
    data_dir = base_dir / "market_data"
    input_dir = data_dir / "input_files"
    backup_dir = data_dir / "input_files_all"

    # 1. Cleanup all generated JSON files and daily reports
    count = 0
    for json_file in data_dir.rglob("*.json"):
        os.remove(json_file)
        count += 1
    
    for txt_file in (data_dir / "daily_reports").rglob("*.txt"):
        os.remove(txt_file)

    print(f"Removed {count} JSON files (including registry).")

    # 2. Setup folders for isolated run
    if not backup_dir.exists():
        os.rename(input_dir, backup_dir)
        os.makedirs(input_dir)
    else:
        # If backup exists, clear input_dir first?
        for f in input_dir.glob("*"):
            os.remove(f)

    # 3. Find all dates
    etf_files = sorted(backup_dir.glob("*_ETF.csv"))
    dates = []
    for f in etf_files:
        match = re.match(r"(\d{8})_ETF\.csv$", f.name)
        if match:
            dates.append(match.group(1))

    # 4. Run pipeline day by day
    for d in dates:
        print(f"Running pipeline for date: {d}")
        
        # Copy files for this date
        etf_src = backup_dir / f"{d}_ETF.csv"
        stock_src = backup_dir / f"{d}_stocks.csv"
        
        shutil.copy2(etf_src, input_dir / etf_src.name)
        shutil.copy2(stock_src, input_dir / stock_src.name)

        # Run pipeline
        subprocess.run(["python", "main.py"], cwd=base_dir, check=True)

    print("Historical pipeline run complete.")
    
    # Restore fully:
    shutil.rmtree(input_dir)
    os.rename(backup_dir, input_dir)

if __name__ == "__main__":
    main()
