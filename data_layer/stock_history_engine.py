import os
import json
from pathlib import Path

import pandas as pd

from config.runtime_context import context, get_monthly_path


STOCK_HISTORY_DIR = Path("market_data/stock_universe")


def safe_float(value, default=0.0):
    if pd.isna(value):
        return default
    return float(value)


def safe_int(value, default=0):
    if pd.isna(value):
        return default
    return int(value)


def load_previous_stock_history():

    if not STOCK_HISTORY_DIR.exists():
        return {}

    files = sorted(
        STOCK_HISTORY_DIR.rglob("*.json"),
        key=lambda x: x.name
    )

    if len(files) < 2:
        return {}

    previous_file = files[-2]

    with open(previous_file, "r") as f:
        data = json.load(f)

    return {
        item["ticker"]: item
        for item in data
    }


def save_stock_history(stocks):

    today = context.market_date
    stock_data = []

    previous_data = load_previous_stock_history()

    for _, row in stocks.iterrows():

        mapped_theme = row.get("Mapped_Theme", "Unknown")

        previous = previous_data.get(
            row["Ticker"],
            {}
        )

        stock_days_long = 0
        stock_days_short = 0

        if row.get("Is_Long_Candidate", False):

            stock_days_long = previous.get(
                "stock_days_long",
                0
            ) + 1

        if row.get("Is_Short_Candidate", False):

            stock_days_short = previous.get(
                "stock_days_short",
                0
            ) + 1

        stock_data.append({

            "scan_date": str(today),

            "ticker": row["Ticker"],

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
                safe_float(
                    row["Price as a % of 52 Wk H-L Range"]
                ), 2
            ),

            "theme": mapped_theme,

            "theme_rank": row.get(
                "Theme_Rank",
                None
            ),

            "theme_class": row["Theme_Class"],

            "theme_state": row.get(
                "Theme_State",
                None
            ),

            "theme_strength_score": round(
                safe_float(row.get("Theme_Score", 0)), 2
            ),

            "etf_raw_score": round(
                safe_float(row.get("ETF_Raw_Score", 0)), 2
            ),

            "theme_days_in_state": 1,

            "long_rank": row.get(
                "Long_Rank",
                None
            ),

            "short_rank": row.get(
                "Short_Rank",
                None
            ),

            "is_long_candidate": row.get(
                "Is_Long_Candidate",
                False
            ),

            "is_short_candidate": row.get(
                "Is_Short_Candidate",
                False
            ),

            "stock_days_long": stock_days_long,

            "stock_days_short": stock_days_short,

            "is_classified": (
                False if mapped_theme in [
                    "Unknown",
                    "",
                    None
                ]
                else True
            ),

            "rs_rating": safe_int(
                row["RS_Rating"]
            ),

            "sales_growth": round(
                safe_float(
                    row["Sales Growth F(0)/F(-1)"]
                ), 2
            ),

            "operating_margin": round(
                safe_float(
                    row["Operating Margin 12 Mo %"]
                ), 2
            ),

            "zacks_rank": safe_int(
                row["Zacks Rank"]
            ),

            "long_score": round(
                safe_float(row["Long_Score"]), 2
            ),

            "composite_score": round(
                safe_float(row.get("Composite_Score", 0)), 2
            ),

            "tracking_state": row.get(
                "Tracking_State",
                "UNTRACKED"
            )

        })

    target_dir = get_monthly_path(STOCK_HISTORY_DIR, context.market_date)
    filename = os.path.join(
        target_dir,
        f"{context.market_date}_stock_history.json"
    )

    with open(filename, "w") as f:
        json.dump(stock_data, f, indent=4)

    print()
    print("STOCK HISTORY SAVED:", filename)