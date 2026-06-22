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
    long_candidates,
    short_candidates
):

    today = datetime.today().strftime("%Y-%m-%d")

    snapshot = {

        "date": today,

        "leading_themes": leading_themes,

        "emerging_themes": emerging_themes,

        "weakening_themes": weakening_themes,

        "lagging_themes": lagging_themes,

        "top_longs": [
            {
                "ticker": row["Ticker"],
                "score": round(row["Composite_Score"], 2)
            }
            for _, row in long_candidates.head(20).iterrows()
        ],

        "top_shorts": [
            {
                "ticker": row["Ticker"],
                "score": round(row["Composite_Score"], 2)
            }
            for _, row in short_candidates.head(20).iterrows()
        ]

    }

    filename = os.path.join(
        SNAPSHOT_DIR,
        f"{today}.json"
    )

    with open(filename, "w") as f:
        json.dump(snapshot, f, indent=4)

    print()
    print("SNAPSHOT SAVED:", filename)