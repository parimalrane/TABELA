# engines/long_scoring_engine.py

def calculate_long_score(stocks):
    # Pure filter architecture: Long_Score maps directly to RS_Rating
    stocks["Long_Score"] = stocks["RS_Rating"]
    return stocks
