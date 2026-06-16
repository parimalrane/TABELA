def build_institutional_leaders(stocks):

    leaders = []

    selected_tickers = set()

    # ==========================================
    # STAGE 1 → BEST STOCK FROM EACH STRONG THEME
    # ==========================================

    strong_themes = stocks[

        stocks["Theme_Class"].isin(["Leading", "Emerging"])

    ]


    theme_leaders = strong_themes[

        (strong_themes["Composite_Score"] >= 90)

        |

        (strong_themes["RS_Rating"] >= 95)

    ]


    for _, row in theme_leaders.iterrows():

        leaders.append(row)

        selected_tickers.add(row["Ticker"])


    # ==========================================
    # STAGE 2 → FILL REMAINING WITH STRONGEST STOCKS
    # ==========================================

    remaining_stocks = stocks.sort_values(

        "Composite_Score",
        ascending=False
    )

    for _, row in remaining_stocks.iterrows():

        if len(leaders) >= 20:
            break

        if row["Ticker"] not in selected_tickers:

            leaders.append(row)

            selected_tickers.add(row["Ticker"])


    # ==========================================
    # FINAL OUTPUT
    # ==========================================

    import pandas as pd

    leaders_df = pd.DataFrame(leaders)

    leaders_df = leaders_df.sort_values(

        "Composite_Score",
        ascending=False
    )

    return leaders_df.head(20)