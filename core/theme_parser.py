# theme_parser.py


INVALID_THEMES = [

    "Broad",
    "broad",

    "Socially Responsible",

    "China",
    "Taiwan",
    "South Korea",
    "Japan",
    "India",
    "Brazil",
    "Mexico",
    "Peru",
    "Chile",

    "Europe",
    "Emerging Markets"
]


def parse_theme(strategy):

    strategy = str(strategy).strip()


    # ---------------------------------
    # CASE 1 → Split ETF strategy
    # ---------------------------------

    if "-" in strategy:

        parts = strategy.split("-")

        sector = parts[0].strip()

        theme = parts[1].strip()

    elif "artificial intelligence" in strategy.lower():

        sector = "Technology"

        theme = "Artificial Intelligence"

    else:

        sector = "Unknown"

        theme = strategy


    # ---------------------------------
    # FILTER INVALID THEMES
    # ---------------------------------

    if theme in INVALID_THEMES:

        theme = "Filtered"


    # ---------------------------------
    # SUBTHEME
    # ---------------------------------

    if "semiconductor" in theme.lower():

        subtheme = "Chips"

    elif "robotics" in strategy.lower():

        subtheme = "Robotics"

    elif "cloud" in theme.lower():

        subtheme = "Cloud Infrastructure"

    elif "software" in theme.lower():

        subtheme = "Enterprise Software"

    else:

        subtheme = "General"


    return sector, theme, subtheme