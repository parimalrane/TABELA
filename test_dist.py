import pandas as pd
from pipeline.pipeline import get_distribution_candidates
from config.config import DIST_ENTRY, DIST_MAINTAIN

stocks = pd.read_csv("market_data/stock_universe/2026-08/2026-08-28.csv")
print("Total stocks:", len(stocks))
dal = stocks[stocks["Ticker"] == "DAL"]
print("DAL data:", dal[["Ticker", "RS_Rating", "Long_Score", "Theme_Class"]])

print("DIST_ENTRY:", DIST_ENTRY)

eligible = get_distribution_candidates({}, stocks)
print("Eligible:", len(eligible))
if len(eligible) > 0:
    print(eligible[["Ticker", "RS_Rating", "Theme_Class"]].head())
