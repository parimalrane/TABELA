import os
import json

from core.config import *
from engines.runtime_context import context


UNKNOWN_DIR = "market_data/unknown_classification"
os.makedirs(UNKNOWN_DIR, exist_ok=True)


def save_unknown_classification(stocks):

    unknown_stocks = stocks[
        (stocks["Mapped_Theme"] == "Unknown")
        &
        (stocks["RS_Rating"] >= UNKNOWN_RS_THRESHOLD)
        &
        (stocks["Long_Score"] >= UNKNOWN_LONG_SCORE_THRESHOLD)
        &
        (
            stocks["Price as a % of 52 Wk H-L Range"]
            >=
            UNKNOWN_PRICE_POSITION_THRESHOLD
        )
        &
        (
            stocks["Market Cap (mil)"]
            >=
            UNKNOWN_MARKET_CAP_THRESHOLD
        )
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