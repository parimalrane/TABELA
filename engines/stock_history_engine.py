import os
import json
from datetime import datetime
import pandas as pd


STOCK_HISTORY_DIR = "market_data/stock_universe"
os.makedirs(STOCK_HISTORY_DIR, exist_ok=True)


def safe_float(value, default=0.0):
    if pd.isna(value):
        return default
    return float(value)


def safe_int(value, default=0):
    if pd.isna(value):
        return default
    return int(value)


def save_stock_history(stocks):

    today = datetime.today().strftime("%Y-%m-%d")
    stock_data = []

    for _, row in stocks.iterrows():

        mapped_theme = row.get("Mapped_Theme", "Unknown")

        stock_data.append({

            "run_date": today,

            "ticker": row["Ticker"],

            "last_close": round(
                safe_float(row["Last Close"]), 2
            ),

            "avg_volume": safe_int(
                row["Avg Volume"]
            ),

            "price_change_1w": round(
                safe_float(row["% Price Change (1 Week)"]), 2
            ),

            "price_change_4w": round(
                safe_float(row["% Price Change (4 Weeks)"]), 2
            ),

            "price_change_12w": round(
                safe_float(row["% Price Change (12 Weeks)"]), 2
            ),

            "price_position_52w": round(
                safe_float(row["Price as a % of 52 Wk H-L Range"]), 2
            ),

            "market_cap": safe_float(
                row["Market Cap (mil)"]
            ),

            "sector": row["Sector"],

            "industry": row["Industry"],

            "theme": mapped_theme,

            "theme_class": row["Theme_Class"],

            "is_classified": (
                False if mapped_theme in ["Unknown", "", None]
                else True
            ),

            "rs_rating": safe_int(
                row["RS_Rating"]
            ),

            "sales_growth": round(
                safe_float(row["Sales Growth F(0)/F(-1)"]), 2
            ),

            "operating_margin": round(
                safe_float(row["Operating Margin 12 Mo %"]), 2
            ),

            "zacks_rank": safe_int(
                row["Zacks Rank"]
            ),

            "long_score": round(
                safe_float(row["Long_Score"]), 2
            ),

            "short_score": round(
                safe_float(row["Short_Score"]), 2
            )

        })

    filename = os.path.join(
        STOCK_HISTORY_DIR,
        f"{today}_stock_history.json"
    )

    with open(filename, "w") as f:
        json.dump(stock_data, f, indent=4)

    print()
    print("STOCK HISTORY SAVED:", filename)