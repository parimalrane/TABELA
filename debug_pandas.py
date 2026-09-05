import pandas as pd
from config.config import LONG_ENTRY

df = pd.DataFrame({
    "Ticker": ["AA"],
    "Mapped_Theme": ["ThemeA"],
    "Theme_Class": ["Leading"],
    "RS_Rating": [100],
    "Long_Score": [100],
    "Zacks Rank": [1],
    "Movement": ["NA"],
    "Days": [1]
})

display_df = df[
    [
        "Ticker",
        "Mapped_Theme",
        "Theme_Class",
        "RS_Rating",
        "Long_Score",
        "Zacks Rank"
    ]
].copy()

display_df = display_df.rename(
    columns={
        "Theme_Class": "Theme Classification",
    }
)

print(display_df.to_string(index=False))
