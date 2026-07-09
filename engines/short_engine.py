from engines.distribution_engine import build_distribution_watchlist


def build_short_watchlist(stocks):
    # Backward-compatible wrapper for existing imports.
    # The short universe is now sourced from the distribution engine.
    return build_distribution_watchlist(stocks)