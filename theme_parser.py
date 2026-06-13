# theme_parser.py


def parse_theme(strategy):

    strategy = str(strategy).strip()


    # CASE 1
    # Format: Technology - Semiconductors

    if "-" in strategy:

        parts = strategy.split("-")

        sector = parts[0].strip()

        theme = parts[1].strip()


    # CASE 2
    # AI / Robotics ETF

    elif "artificial intelligence" in strategy.lower():

        sector = "Technology"

        theme = "Artificial Intelligence"


    # CASE 3
    # fallback

    else:

        sector = "Unknown"

        theme = strategy


    # --------------------------
    # Subtheme logic
    # --------------------------

    if "semiconductor" in theme.lower():

        subtheme = "Chips"

    elif "robotics" in strategy.lower():

        subtheme = "Robotics"

    elif "south korea" in theme.lower():

        subtheme = "Country Rotation"

    elif "taiwan" in theme.lower():

        subtheme = "Country Rotation"

    elif "cloud" in theme.lower():

        subtheme = "Cloud Infrastructure"

    elif "software" in theme.lower():

        subtheme = "Enterprise Software"

    else:

        subtheme = "General"


    return sector, theme, subtheme