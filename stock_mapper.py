# stock_mapper.py


def map_stock_theme(industry, sector):

    industry = str(industry).lower().strip()
    sector = str(sector).lower().strip()

    # ==========================================
    # SEMICONDUCTORS / AI / SOFTWARE
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
        return "Software"

    elif "cloud" in industry:
        return "Cloud Computing"

    elif "software" in industry:
        return "Software"

    elif "internet - software" in industry:
        return "Software"

    elif "computer - software" in industry:
        return "Software"

    # ==========================================
    # HEALTHCARE
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

    elif "drug manufacturers" in industry:
        return "Pharma"

    # ==========================================
    # FINANCIALS
    # ==========================================

    elif "insurance" in industry:
        return "Insurance"

    elif "bank" in industry:
        return "Banking"

    elif "financial services" in industry:
        return "Banking"

    elif "capital markets" in industry:
        return "Brokers/ Capital markets"

    elif "asset management" in industry:
        return "Brokers/ Capital markets"

    # ==========================================
    # ENERGY
    # ==========================================

    elif "pipeline" in industry:
        return "Infrastructure"

    elif "oil services" in industry:
        return "Equipment and services"

    elif "oil equipment" in industry:
        return "Equipment and services"

    elif "oil" in industry:
        return "Exploration"

    elif "gas" in industry:
        return "natural gas"

    elif "solar" in industry:
        return "Infrastructure"

    elif "uranium" in industry:
        return "Uranium Mining"

    elif "coal" in industry:
        return "Exploration"

    elif "renewable energy" in industry:
        return "Infrastructure"

    # ==========================================
    # MATERIALS / MINING
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
        return "Copper Mining"

    elif "aluminum" in industry:
        return "Copper Mining"

    elif "mining" in industry:
        return "Gold Mining"

    # ==========================================
    # INDUSTRIALS / DEFENSE / TRANSPORT
    # ==========================================

    elif "aerospace" in industry:
        return "Aerospace & Defense"

    elif "defense" in industry:
        return "Aerospace & Defense"

    elif "airline" in industry:
        return "Transportation/Shipping"

    elif "transportation" in industry:
        return "Transportation/Shipping"

    elif "shipping" in industry:
        return "Transportation/Shipping"

    elif "logistics" in industry:
        return "Transportation/Shipping"

    elif "construction" in industry:
        return "Infrastructure"

    elif "engineering" in industry:
        return "Infrastructure"

    # ==========================================
    # CONNECTIVITY / NETWORKING
    # ==========================================

    elif "communications equipment" in industry:
        return "Optical Networking"

    elif "networking" in industry:
        return "Optical Networking"

    elif "telecommunications" in industry:
        return "Telecom"

    elif "wireless communications" in industry:
        return "Telecom"

# ==========================================
# CONSUMER / RETAIL
# ==========================================

    elif "apparel" in industry:
        return "Footwear/Apparel"

    elif "footwear" in industry:
        return "Footwear/Apparel"

    elif "luxury goods" in industry:
        return "Footwear/Apparel"

    elif "department stores" in industry:
        return "Discount Retail"

    elif "discount stores" in industry:
        return "Discount Retail"

    elif "specialty retail" in industry:
        return "Consumer Retail"

    elif "internet retail" in industry:
        return "E Commerce"

    elif "restaurants" in industry:
        return "Restaurants"

    elif "food distribution" in industry:
        return "Consumer Staples"

    elif "beverages" in industry:
        return "Consumer Staples"

    elif "packaged foods" in industry:
        return "Consumer Staples"

    elif "household products" in industry:
        return "Consumer Staples"

# ==========================================
# HOUSING / CONSTRUCTION
# ==========================================

    elif "building products" in industry:
        return "Building Materials"

    elif "homebuilding" in industry:
        return "Homebuilders"

    elif "residential construction" in industry:
        return "Homebuilders"

    elif "construction materials" in industry:
        return "Building Materials"

    elif "engineering & construction" in industry:
        return "Infrastructure"
    
    # ==========================================
# INDUSTRIALS
# ==========================================

    elif "electrical equipment" in industry:
        return "Electrical Infrastructure"

    elif "industrial products" in industry:
        return "Industrial Automation"

    elif "industrial machinery" in industry:
        return "Industrial Automation"

    elif "manufacturing" in industry:
        return "Industrial Automation"

    elif "farm machinery" in industry:
        return "Industrial Automation"
    
    # ==========================================
# TELECOM / MEDIA
# ==========================================

    elif "telecom services" in industry:
        return "Telecom Infrastructure"

    elif "wireless services" in industry:
        return "Telecom Infrastructure"

    elif "broadcasting" in industry:
        return "Media Distribution"

    elif "entertainment" in industry:
        return "Media Distribution"
    
    # ==========================================
# TRAVEL / PLATFORM
# ==========================================

    elif "travel services" in industry:
        return "Travel Platform"

    elif "online travel" in industry:
        return "Travel Platform"

    elif "ridesharing" in industry:
        return "Transportation Platform"
    
    

    # ==========================================
    # REAL ESTATE
    # ==========================================

    elif "reit" in industry:
        return "REITs"

    elif "real estate" in industry:
        return "REITs"

    # ==========================================
    # UTILITIES
    # ==========================================

    elif "electric utilities" in industry:
        return "Infrastructure"

    elif "power generation" in industry:
        return "Infrastructure"

    elif "renewable utilities" in industry:
        return "Infrastructure"

    # ==========================================
    # SECTOR FALLBACK (MINIMAL)
    # ==========================================

    elif "medical" in sector:
        return "Healthcare"

    elif "utilities" in sector:
        return "Infrastructure"

    elif "energy" in sector:
        return "Exploration"

    elif "real estate" in sector:
        return "REITs"

    # ==========================================
    # UNKNOWN
    # ==========================================

    else:
        return "Unknown"