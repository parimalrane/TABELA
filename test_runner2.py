import io
import sys
from contextlib import redirect_stdout
import pandas as pd
import sys
sys.path.append('c:/TABELA')
from config.config import DIST_ENTRY, DIST_MAINTAIN
from lifecycle.stock_transition_engine import get_distribution_candidates, _meets_criteria

buffer = io.StringIO()
with redirect_stdout(buffer):
    stocks = pd.read_csv("market_data/stock_universe/2026-08/2026-08-28.csv")
    print("Total stocks:", len(stocks))
    mth = stocks[stocks["Ticker"].str.contains("MTH", na=False)]
    if mth.empty:
        print("MTH not found.")
    else:
        row = mth.iloc[0]
        print(f"MTH stats: RS={row['RS_Rating']}, Score={row['Long_Score']}, Theme={row['Theme_Class']}")
        print("Meets DIST_ENTRY?", _meets_criteria(row, DIST_ENTRY))
        print("DIST_ENTRY config:", DIST_ENTRY)

    registry = {}
    eligible = get_distribution_candidates(registry, stocks)
    print(f"Number of eligible from get_distribution_candidates (empty registry):", len(eligible))

with open('test_out.txt', 'w') as f:
    f.write(buffer.getvalue())
