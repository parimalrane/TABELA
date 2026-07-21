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


def build_market_snapshot(df):
    """Return latest market snapshot."""

    latest_date = df["Date"].max()

    snapshot = (
        df[df["Date"] == latest_date]
        .set_index("ETF")
        .loc[MARKET_ETFS]
        .reset_index()
    )

    return {
        "date": latest_date.strftime("%Y-%m-%d"),
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
    """

    market = {}

    for _, row in snapshot["market"].iterrows():

        ticker = row["ETF"]

        market[ticker] = {
            "ohlcv": {
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
            }
        }

    return {

        "date": snapshot["date"],

        "configuration": {
            "performance_lookbacks": PERFORMANCE_LOOKBACKS,
            "relative_volume_lookbacks": RELATIVE_VOLUME_LOOKBACKS,
        },

        "market": market,

        "market_analytics": {

            "relative_volume": relative_volume,

            "lookback_performance": lookback_performance,

            "relative_performance": relative_performance,

            "market_structure": market_structure,

            "institutional_activity": institutional_activity,

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
        MARKET_CONTEXT_FOLDER /
        f"{context['date']}_market_context.json"
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

    config = MARKET_CONTEXT_CONFIG[
        "INSTITUTIONAL_ACTIVITY"
    ]

    adr_lookback = config["ADR_LOOKBACK"]
    consolidation_factor = config[
        "CONSOLIDATION_RANGE_FACTOR"
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
            50,
            adr_lookback,
        ):
            activity[etf] = {
                "day_type": None
            }
            continue

        today = etf_df.iloc[latest_idx]
        previous = etf_df.iloc[latest_idx - 1]

        today_volume = today["Volume"]

        avg_volume20 = (
            etf_df.iloc[
                latest_idx - 20:
                latest_idx
            ]["Volume"]
            .mean()
        )

        avg_volume50 = (
            etf_df.iloc[
                latest_idx - 50:
                latest_idx
            ]["Volume"]
            .mean()
        )

        today_range = (
            today["High"]
            - today["Low"]
        )

        adr20 = (
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
            and today_volume > avg_volume20
            and today_volume > avg_volume50
        ):

            day_type = "Accumulation"

        elif (
            today["Close"] < previous["Close"]
            and today_volume > avg_volume20
            and today_volume > avg_volume50
        ):

            day_type = "Distribution"

        elif (
            today_range
            <= adr20 * consolidation_factor
            and today_volume < avg_volume20
            and today_volume < avg_volume50
        ):

            day_type = "Consolidation"

        else:

            day_type = "Neutral"

        activity[etf] = {
            "day_type": day_type
        }

    return activity


def run_market_context_engine():
    """Entry point."""

    df = load_market_data()

    validate_market_data(df)

    snapshot = build_market_snapshot(df)

    latest_date = df["Date"].max()

    #
    # Relative Volume
    #
    relative_volume = {}

    for lookback in RELATIVE_VOLUME_LOOKBACKS:

        relative_volume[f"{lookback}d"] = (
            calculate_relative_volume(
                df,
                latest_date,
                lookback,
            )
        )

    #
    # Lookback Performance
    #
    lookback_performance = {}

    for lookback in PERFORMANCE_LOOKBACKS:

        lookback_performance[f"{lookback}d"] = (
            calculate_lookback_performance(
                df,
                latest_date,
                lookback,
            )
        )

    #
    # Relative Performance
    #
    relative_performance = {}

    for lookback, performance in lookback_performance.items():

        relative_performance[lookback] = (
            calculate_relative_performance_matrix(
                performance
            )
        )

    #
    # Market Structure
    #
    market_structure = calculate_market_structure(
        df,
        latest_date,
    )

    #
    # Institutional Activity
    #
    institutional_activity = (
        calculate_institutional_activity(
            df,
            latest_date,
        )
    )

    market_context = build_market_context_json(
        snapshot,
        relative_volume,
        lookback_performance,
        relative_performance,
        market_structure,
        institutional_activity,
    )

    save_market_context_json(
        market_context,
    )


    return market_context