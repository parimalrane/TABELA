# stock_mapper.py


def map_stock_theme(industry, sector):

    industry = str(industry).lower().strip()
    sector = str(sector).lower().strip()

    # ==========================================
    # LEVEL 1 — AI / SEMICONDUCTORS / SOFTWARE
    # ==========================================

    if "semiconductor" in industry:
        return "Semiconductors"

    elif "chip" in industry:
        return "Semiconductors"

    elif "artificial intelligence" in industry:
        return "Artificial Intelligence"

    elif "machine learning" in industry:
        return "Artificial Intelligence"

    elif "security software" in industry:
        return "Software"

    elif "internet - security" in industry:
        return "Software"

    elif "cybersecurity" in industry:
        return "Cybersecurity"

    elif "cloud" in industry:
        return "Cloud Infrastructure"

    elif "software" in industry:
        return "Software"

    elif "internet - software" in industry:
        return "Software"

    elif "computer - software" in industry:
        return "Software"

    # ==========================================
    # LEVEL 2 — HEALTHCARE
    # ==========================================

    elif "medical" in industry:
        return "Medical Devices"

    elif "biomedical" in industry:
        return "Biotech"

    elif "genetics" in industry:
        return "Biotech"

    elif "pharmaceutical" in industry:
        return "Pharma"

    elif "pharma" in industry:
        return "Pharma"

    elif "biotech" in industry:
        return "Biotech"

    # ==========================================
    # LEVEL 3 — FINANCIALS
    # ==========================================

    elif "insurance" in industry:
        return "Insurance"

    elif "bank" in industry:
        return "Banking"

    elif "financial" in industry:
        return "Banking"

    elif "capital markets" in industry:
        return "Brokers"

    # ==========================================
    # LEVEL 4 — REAL ESTATE
    # ==========================================

    elif "reit" in industry:
        return "REITs"

    # ==========================================
    # LEVEL 5 — ENERGY (MAJOR REBUILD)
    # ==========================================

    elif "solar" in industry:
        return "Solar Infrastructure"

    elif "fuel cell" in industry:
        return "Alternative Energy"

    elif "renewable" in industry:
        return "Alternative Energy"

    elif "pipeline" in industry:
        return "Energy Infrastructure"

    elif "oil services" in industry:
        return "Oil Services"

    elif "oil equipment" in industry:
        return "Oil Services"

    elif "oil" in industry:
        return "Exploration"

    elif "gas" in industry:
        return "Natural Gas"

    elif "uranium" in industry:
        return "Uranium Mining"

    elif "nuclear" in industry:
        return "Nuclear Infrastructure"

    # ==========================================
    # LEVEL 6 — MATERIALS
    # ==========================================

    elif "rare earth" in industry:
        return "Rare Earth/Lithium"

    elif "lithium" in industry:
        return "Rare Earth/Lithium"

    elif "copper" in industry:
        return "Copper Mining"

    elif "gold" in industry:
        return "Gold Mining"

    elif "silver" in industry:
        return "Silver Mining"

    elif "steel" in industry:
        return "Steel Production"

    elif "aluminum" in industry:
        return "Aluminum Production"

    elif "mining" in industry:
        return "Gold Mining"

    # ==========================================
    # LEVEL 7 — INDUSTRIAL / DEFENSE
    # ==========================================

    elif "aerospace" in industry:
        return "Aerospace & Defense"

    elif "defense" in industry:
        return "Aerospace & Defense"

    elif "airline" in industry:
        return "Transportation Platform"

    elif "transportation" in industry:
        return "Transportation Platform"

    elif "agriculture" in industry:
        return "Agribusiness"

    elif "engineering" in industry:
        return "Infrastructure"

    # ==========================================
    # LEVEL 8 — INTERNET / TELECOM
    # ==========================================

    elif "internet - services" in industry:
        return "Internet"

    elif "communications equipment" in industry:
        return "Telecom"

    elif "networking" in industry:
        return "AI Networking"

    elif "internet" in industry:
        return "Internet"

    # ==========================================
    # SAFE SECTOR FALLBACK ONLY
    # ==========================================

    elif "finance" in sector:
        return "Banking"

    elif "industrial" in sector:
        return "Infrastructure"

    # ==========================================
    # UNKNOWN
    # ==========================================

    else:
        return "Unknown"