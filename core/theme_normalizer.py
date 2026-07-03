# core/theme_normalizer.py

def normalize_theme(theme):

    if not theme:
        return "Unknown"

    mapping = {

        "natural gas": "Natural Gas",
        "Natural Gas": "Natural Gas",

        "broad": "Broad",
        "Broad": "Broad",

        "semiconductors": "Semiconductors",
        "Semiconductors": "Semiconductors",

        "software": "Software",
        "Software": "Software"

    }

    return mapping.get(str(theme).strip(), str(theme).strip())