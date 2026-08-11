import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "macro_theme_mapping.csv"

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