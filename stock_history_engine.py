import os
import json
from datetime import datetime


def save_stock_history(stocks):

    # Create folder if missing
    if not os.path.exists("stock_history"):
        os.makedirs("stock_history")

    today = datetime.today().strftime("%Y-%m-%d")

    stock_data = []

    for _, row in stocks.iterrows():

        stock_data.append({

            "ticker": row["Ticker"],

            "last_close": round(
                row["Last Close"], 2
            ),

            "avg_volume": int(
                row["Avg Volume"]
            ),

            "52_week_high": round(
                row["52 Week High"], 2
            ),

            "52_week_low": round(
                row["52 Week Low"], 2
            ),

            "price_position": round(
                row["Price as a % of 52 Wk H-L Range"], 2
            ),

            "theme": row["Mapped_Theme"],

            "theme_class": row["Theme_Class"],

            "rs_rating": int(
                row["RS_Rating"]
            ),

            "composite_score": round(
                row["Composite_Score"], 2
            ),

            "sales_score": int(
                row["Sales_Score"]
            ),

            "zacks_score": int(
                row["Zacks_Score"]
            )

        })

    filename = f"stock_history/{today}.json"

    # overwrite same day
    with open(filename, "w") as f:

        json.dump(stock_data, f, indent=4)

    print()
    print("STOCK HISTORY SAVED:", filename)