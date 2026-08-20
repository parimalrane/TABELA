import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
import shutil
import subprocess
from pathlib import Path
import re

def main():
    script_dir = Path(os.path.abspath(__file__)).parent
    base_dir = script_dir.parent
    data_dir = base_dir / "market_data"
    input_dir = data_dir / "input_files"
    backup_dir = data_dir / "input_files_all"

    count = 0
    for json_file in data_dir.rglob("*.json"):
        try:
            os.remove(json_file)
            count += 1
        except:
            pass
    
    for txt_file in (base_dir / "market_data" / "daily_reports").rglob("*.txt"):
        try:
            os.remove(txt_file)
        except:
            pass

    print(f"Removed {count} JSON files (including registry).")

    if backup_dir.exists():
        for f in input_dir.glob("*.*"):
            dest = backup_dir / f.name
            if dest.exists():
                os.remove(dest)
            shutil.copy2(f, dest)
        for f in input_dir.glob("*"):
            os.remove(f)
    else:
        os.rename(input_dir, backup_dir)
        os.makedirs(input_dir)

    etf_files = sorted(backup_dir.glob("*_ETF.csv"))
    if not etf_files:
        etf_files = sorted(backup_dir.glob("*_etf.csv")) # fallback for lowercase

    dates = []
    for f in etf_files:
        match = re.match(r"(\d{8})_ETF\.csv$", f.name, re.IGNORECASE)
        if match:
            dates.append(match.group(1))

    if not dates:
        print(f"WARNING: No matching CSV date files found in {backup_dir}.")
        shutil.rmtree(input_dir)
        os.rename(backup_dir, input_dir)
        return

    dates = sorted(list(set(dates)))

    for d in dates:
        print(f"Running pipeline for date: {d}")
        # Clear input_dir for this specific date
        for f in input_dir.glob("*"):
            try:
                os.remove(f)
            except:
                pass

        etf_src = backup_dir / f"{d}_ETF.csv"
        if not etf_src.exists():
            etf_src = backup_dir / f"{d}_etf.csv"

        stock_src = backup_dir / f"{d}_stocks.csv"
        market_src = backup_dir / f"{d}_Market.csv"

        
        if etf_src.exists(): shutil.copy2(etf_src, input_dir / etf_src.name)
        if stock_src.exists(): shutil.copy2(stock_src, input_dir / stock_src.name)
        if market_src.exists(): shutil.copy2(market_src, input_dir / market_src.name)

        try:
            main_script = base_dir / "runners" / "main.py"
            subprocess.run(["python", str(main_script)], cwd=base_dir, check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR running pipeline on {d}:\n{e}")
            break

    print("Historical pipeline run complete.")
    
    if input_dir.exists():
        shutil.rmtree(input_dir)
    if backup_dir.exists():
        os.rename(backup_dir, input_dir)

if __name__ == "__main__":
    main()
