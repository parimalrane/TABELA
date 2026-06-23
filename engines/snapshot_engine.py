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

            "unclassified_stock_count": unclassified_stock_count

        },

        "leading_themes": leading_themes,

        "emerging_themes": emerging_themes,

        "weakening_themes": weakening_themes,

        "lagging_themes": lagging_themes,

        "theme_breadth": theme_breadth.to_dict(
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