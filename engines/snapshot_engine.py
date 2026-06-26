import os
import json
from datetime import datetime


SNAPSHOT_DIR = "market_data/snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def save_daily_snapshot(
    leading_themes,
    emerging_themes,
    weakening_themes,
    lagging_themes,
    total_stock_count,
    classified_stock_count,
    unclassified_stock_count,
    theme_breadth
):

    today = datetime.today().strftime("%Y-%m-%d")

    snapshot = {

        "date": today,

        "metadata": {

            "total_stock_count": total_stock_count,

            "classified_stock_count": classified_stock_count,

            "unclassified_stock_count": unclassified_stock_count,

            "total_themes_detected": len(theme_breadth)

        },

       "leading_themes": [
    {
        "theme": t["Theme"],
        "rank": int(t["Theme_Rank"]),
        "score": round(float(t["ETF_RS_Raw"]), 2),
        "days": 1
    }
    for t in leading_themes
],


"emerging_themes": [
    {
        "theme": t["Theme"],
        "rank": int(t["Theme_Rank"]),
        "score": round(float(t["ETF_RS_Raw"]), 2),
        "days": 1
    }
    for t in emerging_themes
],


"weakening_themes": [
    {
        "theme": t["Theme"],
        "rank": int(t["Theme_Rank"]),
        "score": round(float(t["ETF_RS_Raw"]), 2),
        "days": 1
    }
    for t in weakening_themes
],


"lagging_themes": [
    {
        "theme": t["Theme"],
        "rank": int(t["Theme_Rank"]),
        "score": round(float(t["ETF_RS_Raw"]), 2),
        "days": 1
    }
    for t in lagging_themes
],

        "theme_breadth": theme_breadth[
    [
        "Mapped_Theme",
        "Total_Stocks",
        "Strong_Stocks",
        "Breadth_Percent",
        "Weighted_Breadth_Score"
    ]
].to_dict(
    orient="records"
)

    }

    filename = os.path.join(
        SNAPSHOT_DIR,
        f"{today}_market_snapshot.json"
    )

    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=4)

    print()
    print("MARKET SNAPSHOT SAVED:", filename)