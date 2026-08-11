import os
import shutil
import subprocess
from pathlib import Path
import re

base_dir = Path("c:/TABELA")
data_dir = base_dir / "market_data"
input_dir = data_dir / "input_files"

etf_files = sorted(input_dir.glob("*_ETF.csv"))
print("etf_files:", len(etf_files))
for f in etf_files[:5]:
    print(" ", f.name)
    m = re.match(r"(\d{8})_ETF\.csv$", f.name)
    if m:
        print("  MATCHED:", m.group(1))
    else:
        print("  NOT MATCHED")
