import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "macro_theme_mapping.csv"
ETF_CSV_PATH = BASE_DIR / "data" / "theme_etf_mapping.csv"

try:
    mapping_df = pd.read_csv(CSV_PATH)
    THEME_TRANSLATION = dict(
        zip(
            mapping_df["Narrative_Theme"].astype(str).str.strip(),
            mapping_df["Benchmark_ETF_Theme"].astype(str).str.strip()
        )
    )
except Exception as e:
    print(f"WARNING: Could not load data/macro_theme_mapping.csv: {e}")
    THEME_TRANSLATION = {}

try:
    etf_mapping_df = pd.read_csv(ETF_CSV_PATH)
    THEME_ETF_MAPPING = dict(
        zip(
            etf_mapping_df["Theme"].astype(str).str.strip(),
            etf_mapping_df["Top_ETFs"].astype(str).str.strip()
        )
    )
except Exception as e:
    THEME_ETF_MAPPING = {}
