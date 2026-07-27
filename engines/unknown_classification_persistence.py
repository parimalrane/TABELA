import os
import json

from core.config import *
from core.runtime_context import context


UNKNOWN_DIR = "market_data/unknown_classification"
os.makedirs(UNKNOWN_DIR, exist_ok=True)


def save_unknown_classification(stocks):

    unknown_stocks = stocks[
        stocks["Is_Unclassified_Leader"]
    ].copy()

    unknown_stocks = unknown_stocks.sort_values(
        by=["RS_Rating", "Long_Score"],
        ascending=False
    )

    unknown_data = []

    for _, row in unknown_stocks.iterrows():

        unknown_data.append({

            "ticker": row["Ticker"],
            "company_name": row["Company Name"],

            "mapped_theme": row["Mapped_Theme"],
            "theme_class": row["Theme_Class"],

            "sector": row["Sector"],
            "industry": row["Industry"],

            "rs_rating": int(row["RS_Rating"]),
            "long_score": float(row["Long_Score"]),

            "last_close": float(row["Last Close"]),
            "price_position": float(
                row["Price as a % of 52 Wk H-L Range"]
            ),
            "market_cap_mil": float(
                row["Market Cap (mil)"]
            )

        })

    today = context.market_date

    output = {

        "date": str(today),
        "unknown_leaders": unknown_data

    }

    filename = os.path.join(
        UNKNOWN_DIR,
        f"{context.market_date}_unknown_classification.json"
    )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print()
    print("UNKNOWN CLASSIFICATION SAVED:", filename)