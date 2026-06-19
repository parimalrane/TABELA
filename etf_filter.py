# ==========================================
# ETF FILTER ENGINE
# ThemePulse V2
# ==========================================

EXCLUDE_KEYWORDS = [

    # Fixed income

    "bond",
    "treasury",
    "municipal",
    "mortgage",
    "mbs",
    "fixed income",
    "preferred",

    # Income / yield products

    "income",
    "dividend",
    "covered call",
    "buffer",
    "target date",
    "allocation",

    # Leveraged / inverse

    "inverse",
    "bear",
    "ultra",
    "2x",
    "3x",
    "leveraged",

    # Currency

    "currency",
    "forex",
    "yen",
    "euro",

    # Volatility

    "volatility",
    "vix",

    # Geography / country

    "china",
    "japan",
    "canada",
    "europe",
    "latin america",
    "asia",
    "africa",
    "middle east",
    "israel",
    "vietnam",
    "argentina",
    "colombia",
    "thailand",
    "south africa",
    "global ex",
    "eafe",
    "emerging markets",
    "developed markets",
    "world",

    # Factor products

    "alpha",
    "beta",
    "momentum",
    "growth",
    "value",
    "blend",
    "quality",
    "multi factor",
    "factor",
    "low volatility",

    # Portfolio strategy wrappers

    "transparent",
    "long/short",
    "130/30",
    "absolute return",
    "absolute returns",
    "conservative",
    "target outcome",
    "derivative",
    "asset allocation",

    # Commodities (remove for now)

    "corn",
    "wheat",
    "sugar",
    "platinum",
    "palladium",
    "silver",
    "gold",

    "nanotech",
    "services",
    "asset",
    "global total market",
    "digital economy",
    "marijuana",
    "bdcs",
    "private equity",
    "m&a",
    "inflation",
    "water",
    "softs"

]

def filter_valid_etfs(etf_df):

    # Combine searchable text columns

    combined_text = (

        etf_df["Company Name"].fillna("").astype(str) + " " +

        etf_df["Investment Category"].fillna("").astype(str) + " " +

        etf_df["Investment Strategy"].fillna("").astype(str)

    ).str.lower()


    # Start with all ETFs

    valid_mask = ~combined_text.str.contains(

        "|".join(EXCLUDE_KEYWORDS),

        na=False

    )


    filtered_etfs = etf_df[valid_mask].copy()

    return filtered_etfs