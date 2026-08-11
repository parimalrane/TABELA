import json
from pathlib import Path

import pandas as pd

MARKET_ETFS = ["SPY", "QQQ", "IWM", "DIA"]
MARKET_CONTEXT_FOLDER = Path("market_data/market_context")


def save_market_context_json(context):
    """
    Save Market Context JSON.
    """

    MARKET_CONTEXT_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = (
        MARKET_CONTEXT_FOLDER
        / f"{context['latest_market_snapshot']['market_date']}_market_context.json"
    )

    with open(filename, "w") as f:
        json.dump(
            context,
            f,
            indent=4,
        )

    return filename


def run_market_context_engine(market_date):
    """
    Entry point for the Market Context Engine.

    Reads pre-calculated market metrics directly from the date-stamped
    Market_YYYYMMDD.csv file (located in market_data/input_files/).

    CSV columns consumed:
        Market Date  — trading date (YYYY-MM-DD)
        ETF          — ticker symbol
        Derived Price
        Volume
        5D Perf %    → returns.1w
        20D Perf %   → returns.4w
        50D Perf %   → returns.10w
        200D Perf %  → returns.40w
        RV 20D %     → relative_volume.20d
        RV 50D %     → relative_volume.50d
        5D Dist %    → moving_average_extension.5dma  (not currently output)
        20D Dist %   → moving_average_extension.20dma
        50D Dist %   → moving_average_extension.50dma
        200D Dist %  → moving_average_extension.200dma

    No internal rolling calculations are performed.
    """
    from core.runtime_context import context

    market_file = context.market_file

    if not market_file.exists():
        print(f"Market file not found: {market_file}. Skipping Market Context.")
        return None

    df = pd.read_csv(market_file)
    df["ETF"] = df["ETF"].astype(str).str.upper().str.strip()

    required = [
        "Market Date", "ETF", "Volume",
        "5D Perf %", "20D Perf %", "50D Perf %", "200D Perf %",
        "RV 20D %", "RV 50D %",
        "20D Dist %", "50D Dist %", "200D Dist %",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"Market_{market_file.stem} missing required columns: "
            f"{', '.join(missing)}"
        )

    # Build market_statistics from pre-calculated values
    market_statistics = {}

    for _, row in df.iterrows():
        ticker = row["ETF"]

        market_statistics[ticker] = {
            "day_type": "Neutral",
            "relative_volume": {
                "20d": round(float(row["RV 20D %"]), 2),
                "50d": round(float(row["RV 50D %"]), 2),
            },
            "returns": {
                "1w":  round(float(row["5D Perf %"]),   2),
                "4w":  round(float(row["20D Perf %"]),  2),
                "10w": round(float(row["50D Perf %"]),  2),
                "40w": round(float(row["200D Perf %"]), 2),
            },
            "moving_average_extension": {
                "20dma":  round(float(row["20D Dist %"]),  2),
                "50dma":  round(float(row["50D Dist %"]),  2),
                "200dma": round(float(row["200D Dist %"]), 2),
            },
        }

    # Relative performance matrix — pairwise differences from pre-calculated returns
    periods = [
        ("1w",  "5D Perf %"),
        ("4w",  "20D Perf %"),
        ("10w", "50D Perf %"),
        ("40w", "200D Perf %"),
    ]
    relative_performance = {key: {} for key, _ in periods}

    for i in range(len(MARKET_ETFS)):
        for j in range(i + 1, len(MARKET_ETFS)):
            etf_a = MARKET_ETFS[i]
            etf_b = MARKET_ETFS[j]

            row_a = df[df["ETF"] == etf_a]
            row_b = df[df["ETF"] == etf_b]

            if row_a.empty or row_b.empty:
                continue

            for out_key, csv_col in periods:
                p_a = float(row_a.iloc[0][csv_col])
                p_b = float(row_b.iloc[0][csv_col])
                relative_performance[out_key][f"{etf_a}_vs_{etf_b}"] = round(p_a - p_b, 2)

    market_context = {
        "latest_market_snapshot": {
            "market_date": pd.to_datetime(market_date).strftime("%Y-%m-%d"),
            "market_statistics": {
                etf: market_statistics[etf]
                for etf in MARKET_ETFS
                if etf in market_statistics
            },
            "relative_performance": relative_performance,
        }
    }

    save_market_context_json(market_context)

    return market_context