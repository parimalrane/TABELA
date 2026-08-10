from pathlib import Path
from core.config import MARKET_CONTEXT_CONFIG
import pandas as pd
import json


MARKET_FILE = Path("market_data/Market.csv")
MARKET_CONTEXT_FOLDER = Path("market_data/market_context")
MARKET_ETFS = MARKET_CONTEXT_CONFIG["MARKET_ETFS"]
PERFORMANCE_LOOKBACKS = MARKET_CONTEXT_CONFIG["PERFORMANCE_LOOKBACKS"]
RELATIVE_VOLUME_LOOKBACKS = MARKET_CONTEXT_CONFIG[
    "RELATIVE_VOLUME_LOOKBACKS"
]


REQUIRED_COLUMNS = [
    "Date",
    "ETF",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def load_market_data():
    """Load Market.csv."""

    if not MARKET_FILE.exists():
        raise FileNotFoundError(f"Market file not found: {MARKET_FILE}")

    df = pd.read_csv(MARKET_FILE)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Market.csv missing required columns: {', '.join(missing)}"
        )

    df["Date"] = pd.to_datetime(df["Date"])
    df["ETF"] = df["ETF"].astype(str).str.upper().str.strip()

    df = df.sort_values(["Date", "ETF"]).reset_index(drop=True)

    return df


def validate_market_data(df):
    """Validate Market.csv integrity."""

    duplicates = df[df.duplicated(["Date", "ETF"], keep=False)]

    if not duplicates.empty:
        raise ValueError(
            "Duplicate Date/ETF records found:\n"
            + duplicates[["Date", "ETF"]].to_string(index=False)
        )
    invalid = set(df["ETF"]) - set(MARKET_ETFS)
    if invalid:
        raise ValueError(
            f"Unexpected ETF(s) found: {sorted(invalid)}"
        )

    for date, group in df.groupby("Date"):

        tickers = sorted(group["ETF"].tolist())

        if tickers != sorted(MARKET_ETFS):
            raise ValueError(
                f"{date.date()} does not contain exactly "
                f"{MARKET_ETFS}"
            )

        duplicates = group["ETF"].duplicated()

        if duplicates.any():
            dup = group.loc[duplicates, "ETF"].tolist()
            raise ValueError(
                f"Duplicate ETF(s) on {date.date()}: {dup}"
            )


def build_market_snapshot(
    df,
    market_date,
):
    """
    Return market snapshot for the requested market date.
    """

    target_date = pd.to_datetime(market_date)

    snapshot = (
        df[df["Date"] == target_date]
        .set_index("ETF")
        .loc[MARKET_ETFS]
        .reset_index()
    )

    if snapshot.empty:
        raise ValueError(
            f"Market.csv does not contain market date {market_date}"
        )

    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "market": snapshot,
    }

def build_market_context_json(
    snapshot,
    relative_volume,
    lookback_performance,
    relative_performance,
    market_structure,
    institutional_activity,
):
    """
    Build the daily Market Context JSON.

    This JSON is the canonical Market Context consumed by
    the Weekly Intelligence pipeline.
    """

   

    market_statistics = {}

    for _, row in snapshot["market"].iterrows():

        ticker = row["ETF"]

        day_type = institutional_activity[ticker]["day_type"]


        market_statistics[ticker] = {

            "day_type": day_type,

            "relative_volume": {
                f"{lookback}d": relative_volume[f"{lookback}d"][ticker]
                for lookback in RELATIVE_VOLUME_LOOKBACKS
            },

            "returns": {
                "1w": lookback_performance["5d"][ticker],
                "4w": lookback_performance["20d"][ticker],
                "10w": lookback_performance["50d"][ticker],
                "40w": lookback_performance["200d"][ticker],
            },

            "moving_average_extension": {
                "20dma": market_structure[ticker]["distance_to_20sma_pct"],
                "50dma": market_structure[ticker]["distance_to_50sma_pct"],
                "200dma": market_structure[ticker]["distance_to_200sma_pct"],
            },
        }

    return {

        "latest_market_snapshot": {

            "market_date": snapshot["date"],

            "market_statistics": {
                "SPY": market_statistics["SPY"],
                "QQQ": market_statistics["QQQ"],
                "IWM": market_statistics["IWM"],
                "DIA": market_statistics["DIA"],
            },

            "relative_performance": {
                "1w": relative_performance["5d"],
                "4w": relative_performance["20d"],
                "10w": relative_performance["50d"],
                "40w": relative_performance["200d"],
            },
        },
    }

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

def calculate_relative_volume(df, latest_date, lookback_days):
    """
    Calculate relative volume for each ETF.

    Relative Volume =
        Today's Volume /
        Average Volume of previous N trading days
    """

    relative_volume = {}

    for etf in MARKET_ETFS:

        etf_df = (
            df[df["ETF"] == etf]
            .sort_values("Date")
            .reset_index(drop=True)
        )

        latest_idx = etf_df.index[
            etf_df["Date"] == latest_date
        ]

        if len(latest_idx) == 0:
            raise ValueError(
                f"{etf}: latest trading day not found."
            )

        latest_idx = latest_idx[0]
        

        if latest_idx < lookback_days:
            relative_volume[etf] = None
            continue

        previous = etf_df.iloc[
            latest_idx - lookback_days: latest_idx
        ]

        avg_volume = previous["Volume"].mean()

        if avg_volume <= 0:
            relative_volume[etf] = None
            continue

        today_volume = etf_df.iloc[latest_idx]["Volume"]

        relative_volume[etf] = round(
            today_volume / avg_volume,
            2,
        )

    return relative_volume


def calculate_lookback_performance(
    df,
    latest_date,
    lookback_days,
):
    """
    Calculate percentage performance over the specified lookback.
    """

    performance = {}

    for etf in MARKET_ETFS:

        etf_df = (
            df[df["ETF"] == etf]
            .sort_values("Date")
            .reset_index(drop=True)
        )

        latest_idx = etf_df.index[
            etf_df["Date"] == latest_date
        ]

        if len(latest_idx) == 0:
            raise ValueError(
                f"{etf}: latest trading day not found."
            )

        latest_idx = latest_idx[0]

        required = lookback_days - 1

        if latest_idx < required:
            performance[etf] = None
            continue

        start_close = etf_df.iloc[
            latest_idx - required
        ]["Close"]

        end_close = etf_df.iloc[
            latest_idx
        ]["Close"]

        performance[etf] = round(
            ((end_close / start_close) - 1) * 100,
            2,
        )

    return performance


def calculate_relative_performance_matrix(performance):
    """
    Calculate pairwise relative performance between the market ETFs.

    Relative Performance =
        ETF_A_Performance - ETF_B_Performance
    """

    matrix = {}

    for i in range(len(MARKET_ETFS)):
        for j in range(i + 1, len(MARKET_ETFS)):

            etf_a = MARKET_ETFS[i]
            etf_b = MARKET_ETFS[j]

            perf_a = performance.get(etf_a)
            perf_b = performance.get(etf_b)

            if perf_a is None or perf_b is None:
                value = None
            else:
                value = round(perf_a - perf_b, 2)

            matrix[f"{etf_a}_vs_{etf_b}"] = value

    return matrix

def calculate_market_structure(
    df,
    latest_date,
):
    """
    Calculate distance from the 20, 50 and 200 SMA
    for each market ETF.
    """

    sma_periods = MARKET_CONTEXT_CONFIG[
        "MARKET_STRUCTURE"
    ]["SMA_PERIODS"]

    market_structure = {}

    for etf in MARKET_ETFS:

        etf_df = (
            df[df["ETF"] == etf]
            .sort_values("Date")
            .reset_index(drop=True)
            .copy()
        )

        latest_row = etf_df.loc[
            etf_df["Date"] == latest_date
        ]

        if latest_row.empty:
            raise ValueError(
                f"{etf}: latest trading day not found."
            )

        latest_idx = latest_row.index[0]

        close = float(
            etf_df.loc[latest_idx, "Close"]
        )

        structure = {}

        for period in sma_periods:

            if latest_idx < (period - 1):

                structure[
                    f"distance_to_{period}sma_pct"
                ] = None

                continue

            sma = (
                etf_df.iloc[
                    latest_idx - period + 1:
                    latest_idx + 1
                ]["Close"]
                .mean()
            )

            distance = (
                (close - sma)
                / sma
            ) * 100

            structure[
                f"distance_to_{period}sma_pct"
            ] = round(
                distance,
                2,
            )

        market_structure[etf] = structure

    return market_structure

def calculate_institutional_activity(
    df,
    latest_date,
):
    """
    Classify the latest trading day as:

    - Accumulation
    - Distribution
    - Consolidation
    - Neutral
    """

    config = MARKET_CONTEXT_CONFIG["INSTITUTIONAL_ACTIVITY"]

    adr_lookback = config["ADR_LOOKBACK"]
    consolidation_factor = config["CONSOLIDATION_RANGE_FACTOR"]

    acc_logic = config["ACCUMULATION_LOGIC"]
    dist_logic = config["DISTRIBUTION_LOGIC"]
    cons_logic = config["CONSOLIDATION_LOGIC"]

    accumulation_threshold = config["ACCUMULATION_VOLUME_THRESHOLD"]
    distribution_threshold = config["DISTRIBUTION_VOLUME_THRESHOLD"]
    consolidation_threshold = config["CONSOLIDATION_VOLUME_THRESHOLD"]

    rv_periods = MARKET_CONTEXT_CONFIG[
        "RELATIVE_VOLUME_LOOKBACKS"
    ]

    activity = {}

    for etf in MARKET_ETFS:

        etf_df = (
            df[df["ETF"] == etf]
            .sort_values("Date")
            .reset_index(drop=True)
            .copy()
        )

        latest_row = etf_df.loc[
            etf_df["Date"] == latest_date
        ]

        if latest_row.empty:
            raise ValueError(
                f"{etf}: latest trading day not found."
            )

        latest_idx = latest_row.index[0]

        if latest_idx < max(
            max(rv_periods),
            adr_lookback,
        ):
            activity[etf] = {
                "day_type": None
            }
            continue

        today = etf_df.iloc[latest_idx]
        previous = etf_df.iloc[latest_idx - 1]

        today_volume = today["Volume"]

        average_volumes = {}

        for period in rv_periods:

            average_volumes[period] = (
                etf_df.iloc[
                    latest_idx - period:latest_idx
                ]["Volume"].mean()
            )

        accumulation_checks = [
            today_volume >= (
                average_volumes[p]
                * accumulation_threshold
            )
            for p in rv_periods
        ]

        distribution_checks = [
            today_volume >= (
                average_volumes[p]
                * distribution_threshold
            )
            for p in rv_periods
        ]

        consolidation_checks = [
            today_volume <= (
                average_volumes[p]
                * consolidation_threshold
            )
            for p in rv_periods
        ]

        accumulation_volume = (
            all(accumulation_checks)
            if acc_logic == "AND"
            else any(accumulation_checks)
        )

        distribution_volume = (
            all(distribution_checks)
            if dist_logic == "AND"
            else any(distribution_checks)
        )

        consolidation_volume = (
            all(consolidation_checks)
            if cons_logic == "AND"
            else any(consolidation_checks)
        )

        today_range = (
            today["High"]
            - today["Low"]
        )

        adr = (
            (
                etf_df["High"]
                - etf_df["Low"]
            )
            .iloc[
                latest_idx - adr_lookback:
                latest_idx
            ]
            .mean()
        )

        if (
            today["Close"] > previous["Close"]
            and accumulation_volume
        ):

            day_type = "Accumulation"

        elif (
            today["Close"] < previous["Close"]
            and distribution_volume
        ):

            day_type = "Distribution"

        elif (
            today_range <= adr * consolidation_factor
            and consolidation_volume
        ):

            day_type = "Consolidation"

        else:

            day_type = "Neutral"

        activity[etf] = {
            "day_type": day_type
        }

    return activity

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