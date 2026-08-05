import json
import pandas as pd
from pathlib import Path

def run():
    print("= REGISTRY =")
    try:
        with open('market_data/stock_transition/registry.json', 'r') as f:
            reg = json.load(f)
            print("EXTR state:", reg.get("EXTR"))
    except Exception as e:
        print("No registry:", e)
    
    print("\n= REPORTS =")
    for f in sorted(Path('market_data/daily_reports').glob('*.txt'))[-3:]:
        lines = f.read_text(encoding='utf-8', errors='ignore').splitlines()
        extr_lines = [l for l in lines if 'EXTR ' in l or l.startswith('  EXTR')]
        print(f.name, extr_lines)

run()
