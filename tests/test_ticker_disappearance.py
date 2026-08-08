"""
Regression tests for the silent ticker disappearance bug.

Root cause (fixed):
  stock_transition_engine.pre_distribution_update() silently:
    1. deleted LONG-state tickers from the registry when they vanished from
       the stocks CSV (del registry[ticker])
    2. ignored tickers that left LONG AND were absent from the stocks CSV
       (continue without registering)

  Both paths meant the ticker would never appear in OBSERVATION/DISTRIBUTION
  output and would fire no alert — a completely silent disappearance.

  Additionally, compare_watchlists only checked LONG→OBSERVATION transitions;
  it never audited OBSERVATION or DISTRIBUTION origin tickers.

Fix:
  1. LONG ghost → demote to OBSERVATION + warn
  2. removed_today ghost → OBSERVATION Day 1 + warn
  3. OBSERVATION/DISTRIBUTION ghost → retain in registry + warn
  4. compare_watchlists full reconciliation across all 3 states
  5. get_distribution_watchlist → warn when registry ticker absent from stocks

Test fixture:
  Exact 11 tickers from the confirmed incident (confirmed present in one
  state on 2026-07-31 or earlier, absent from all states on 2026-08-03+):
    DISTRIBUTION-origin: ALGM, CRDO, MRVL, ARM, KLIC, MKSI, NBIS, OUST, SYNA, RBRK
    LONG-origin: PENG
"""

import sys
import os
import types

import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Minimal stubs so we can import the engines without the full project config.
# ---------------------------------------------------------------------------

# Stub core.runtime_context
runtime_context_mod = types.ModuleType("core.runtime_context")
ctx_obj = types.SimpleNamespace(market_date="2026-08-08")
runtime_context_mod.context = ctx_obj
sys.modules["core"] = types.ModuleType("core")
sys.modules["core.runtime_context"] = runtime_context_mod

# Stub core.config
config_mod = types.ModuleType("core.config")
config_mod.STOCK_TRANSITION_CONFIG = {
    "REGISTRY_DIR": "market_data/stock_transition",
    "OBSERVATION_MIN_RUNS": 7,
    "OBSERVATION_MAX_RUNS": 7,
}
config_mod.OBSERVATION_FALLBACK_SCORE_THRESHOLD = 80.0
config_mod.OBSERVATION_FALLBACK_RS_THRESHOLD = 80.0
sys.modules["core.config"] = config_mod

# Patch the watchlist delta engine's file-based dependency
watchlist_delta_mod = types.ModuleType("engines.watchlist_delta_engine")
watchlist_delta_mod.load_previous_long_watchlist = lambda: pd.DataFrame(columns=["Ticker"])
sys.modules["engines"] = types.ModuleType("engines")
sys.modules["engines.watchlist_delta_engine"] = watchlist_delta_mod

# Now import the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from engines.stock_transition_engine import (  # noqa: E402
    pre_distribution_update,
    get_distribution_watchlist,
    OBSERVATION,
    DISTRIBUTION,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stocks_df(*tickers, long_score=85.0, rs_rating=85.0):
    """Minimal stocks DataFrame with only the named tickers present."""
    return pd.DataFrame({
        "Ticker": list(tickers),
        "Long_Score": [long_score] * len(tickers),
        "RS_Rating": [rs_rating] * len(tickers),
    })


def _empty_df():
    return pd.DataFrame(columns=["Ticker", "Long_Score", "RS_Rating"])


# ---------------------------------------------------------------------------
# Fix 1 — LONG ghost: ticker in LONG registry vanishes from stocks CSV
#          Must demote to OBSERVATION (not silently purge).
# ---------------------------------------------------------------------------

class TestLongGhostDemotion:
    def test_long_ghost_demoted_to_observation(self, capsys):
        """LONG ticker absent from stocks → OBSERVATION, never silently purged."""
        registry = {
            "GHOST": {
                "tracking_state": "LONG",
                "state_days": 3,
                "last_market_date": "2026-08-07",
            }
        }
        # stocks DataFrame does NOT contain GHOST
        stocks = _stocks_df("OTHER")
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        assert "GHOST" in result_registry, (
            "LONG ghost ticker must remain in registry after vanishing from stocks"
        )
        assert result_registry["GHOST"]["tracking_state"] == OBSERVATION, (
            "LONG ghost ticker must be demoted to OBSERVATION, not purged"
        )

    def test_long_ghost_warning_printed(self, capsys):
        """LONG ghost produces a [TRANSITION WARNING] log line."""
        registry = {
            "GHOOSTIE": {
                "tracking_state": "LONG",
                "state_days": 1,
                "last_market_date": "2026-08-07",
            }
        }
        stocks = _stocks_df("UNRELATED")
        long_candidates = pd.DataFrame({"Ticker": ["UNRELATED"]})

        pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )
        out = capsys.readouterr().out
        assert "TRANSITION WARNING" in out
        assert "GHOOSTIE" in out


# ---------------------------------------------------------------------------
# Fix 2 — removed_today ghost: ticker left LONG AND absent from stocks CSV
#          Must enter OBSERVATION Day 1 (not silently skip).
# ---------------------------------------------------------------------------

class TestRemovedTodayGhost:
    def _make_watchlist_for_removed_today(self, ticker, monkeypatch):
        """Arrange for ticker to appear in previous LONG but not current."""
        prev_df = pd.DataFrame({"Ticker": [ticker]})
        monkeypatch.setattr(
            "engines.stock_transition_engine.load_previous_long_watchlist",
            lambda: prev_df,
        )

    def test_removed_long_ghost_enters_observation(self, monkeypatch):
        """Ticker removed from LONG, absent from universe → OBSERVATION Day 1."""
        ticker = "VANISH"
        prev_df = pd.DataFrame({"Ticker": [ticker]})
        import engines.stock_transition_engine as ste
        original_loader = ste.load_previous_long_watchlist
        ste.load_previous_long_watchlist = lambda: prev_df

        registry = {}  # empty: ticker not yet tracked
        stocks = _stocks_df("OTHER")  # ticker absent
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        ste.load_previous_long_watchlist = original_loader

        assert ticker in result_registry, (
            "Ticker removed from LONG while absent from universe must be "
            "entered into registry as OBSERVATION"
        )
        assert result_registry[ticker]["tracking_state"] == OBSERVATION, (
            "Such a ticker must be in OBSERVATION state"
        )
        assert result_registry[ticker]["state_days"] == 1

    def test_removed_long_ghost_warning_printed(self, monkeypatch, capsys):
        """Removed LONG ghost produces a [TRANSITION WARNING] log line."""
        ticker = "GHOSTOUT"
        prev_df = pd.DataFrame({"Ticker": [ticker]})
        import engines.stock_transition_engine as ste
        original_loader = ste.load_previous_long_watchlist
        ste.load_previous_long_watchlist = lambda: prev_df

        registry = {}
        stocks = _stocks_df("OTHER")
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        ste.load_previous_long_watchlist = original_loader
        out = capsys.readouterr().out
        assert "TRANSITION WARNING" in out
        assert ticker in out


# ---------------------------------------------------------------------------
# Fix 3 — OBSERVATION/DISTRIBUTION ghost: ticker in registry but absent from
#          stocks CSV must NOT be silently dropped; must retain in registry
#          with incremented state_days.
# ---------------------------------------------------------------------------

class TestObservationDistributionGhost:
    def test_observation_ghost_retained_in_registry(self, capsys):
        """OBSERVATION ticker vanished from stocks → stays in registry."""
        registry = {
            "OBSVANISH": {
                "tracking_state": OBSERVATION,
                "state_days": 3,
                "last_market_date": "2026-08-07",
            }
        }
        stocks = _stocks_df("OTHER")
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        assert "OBSVANISH" in result_registry
        assert result_registry["OBSVANISH"]["tracking_state"] == OBSERVATION
        assert result_registry["OBSVANISH"]["state_days"] == 4

    def test_distribution_ghost_retained_in_registry(self, capsys):
        """DISTRIBUTION ticker vanished from stocks → stays in registry."""
        registry = {
            "DISTVANISH": {
                "tracking_state": DISTRIBUTION,
                "state_days": 5,
                "last_market_date": "2026-08-07",
            }
        }
        stocks = _stocks_df("OTHER")
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        assert "DISTVANISH" in result_registry
        assert result_registry["DISTVANISH"]["tracking_state"] == DISTRIBUTION
        # state_days advanced despite absence
        assert result_registry["DISTVANISH"]["state_days"] == 6

    def test_observation_ghost_warning_printed(self, capsys):
        """OBSERVATION ghost produces a [TRANSITION WARNING] log line."""
        registry = {
            "OBSW": {
                "tracking_state": OBSERVATION,
                "state_days": 2,
                "last_market_date": "2026-08-07",
            }
        }
        stocks = _stocks_df("OTHER")
        long_candidates = pd.DataFrame({"Ticker": ["OTHER"]})

        pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        out = capsys.readouterr().out
        assert "TRANSITION WARNING" in out
        assert "OBSW" in out


# ---------------------------------------------------------------------------
# Fix 4 — get_distribution_watchlist warns when registry ticker absent from
#          stocks universe.
# ---------------------------------------------------------------------------

class TestDistributionWatchlistWarning:
    def test_warns_for_absent_distribution_ticker(self, capsys):
        """get_distribution_watchlist must print warning for absent tickers."""
        registry = {
            "PRESENT": {"tracking_state": DISTRIBUTION, "state_days": 2, "last_market_date": "2026-08-07"},
            "ABSENT": {"tracking_state": DISTRIBUTION, "state_days": 3, "last_market_date": "2026-08-07"},
        }
        # stocks only contains PRESENT
        stocks = pd.DataFrame({
            "Ticker": ["PRESENT"],
            "RS_Rating": [60.0],
            "Composite_Score": [50.0],
            "Mapped_Theme": ["Semiconductors"],
            "Theme_Class": ["Lagging"],
        })

        get_distribution_watchlist(registry=registry, stocks=stocks)
        out = capsys.readouterr().out
        assert "DISTRIBUTION WARNING" in out
        assert "ABSENT" in out


# ---------------------------------------------------------------------------
# Fix 5 — 11-ticker incident fixture (07-31 → 08-03)
#          Given any of the 11 tickers in a tracked state on day N and absent
#          from the stocks CSV on day N+1, assert they are NOT silently dropped.
# ---------------------------------------------------------------------------

INCIDENT_DISTRIBUTION_TICKERS = [
    "ALGM", "CRDO", "MRVL", "ARM", "KLIC", "MKSI", "NBIS", "OUST", "SYNA", "RBRK"
]
INCIDENT_LONG_TICKERS = ["PENG"]
ALL_INCIDENT_TICKERS = INCIDENT_DISTRIBUTION_TICKERS + INCIDENT_LONG_TICKERS


class TestIncidentFixture11Tickers:
    """
    Exact 11-ticker fixture from the confirmed 07-31→08-07 incident.

    For each ticker, simulate it being tracked in its known prior state,
    then absent from the next day's stocks CSV.  Assert it is never
    silently vanished.
    """

    @pytest.mark.parametrize("ticker", INCIDENT_DISTRIBUTION_TICKERS)
    def test_distribution_ticker_retained_when_absent_from_stocks(self, ticker, capsys):
        """
        Tickers in DISTRIBUTION on 07-31 that dropped from stocks CSV on 08-03
        must remain in registry and emit a warning — never silently vanish.
        """
        registry = {
            ticker: {
                "tracking_state": DISTRIBUTION,
                "state_days": 3,
                "last_market_date": "2026-07-31",
            }
        }
        stocks = _stocks_df("UNRELATED_TICKER")
        long_candidates = pd.DataFrame({"Ticker": ["UNRELATED_TICKER"]})

        import engines.stock_transition_engine as ste
        original_loader = ste.load_previous_long_watchlist
        ste.load_previous_long_watchlist = lambda: pd.DataFrame(columns=["Ticker"])

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        ste.load_previous_long_watchlist = original_loader

        assert ticker in result_registry, (
            f"{ticker} was in DISTRIBUTION but silently vanished from registry "
            f"when absent from stocks CSV"
        )
        assert result_registry[ticker]["tracking_state"] == DISTRIBUTION, (
            f"{ticker} must remain in DISTRIBUTION state"
        )
        out = capsys.readouterr().out
        assert "WARNING" in out, (
            f"A warning must be emitted when {ticker} vanishes from stocks universe"
        )

    @pytest.mark.parametrize("ticker", INCIDENT_LONG_TICKERS)
    def test_long_ticker_demoted_not_purged_when_absent_from_stocks(self, ticker, capsys):
        """
        PENG was in LONG on 07-31/08-06.  When it drops from the stocks CSV
        it must NOT be silently purged — it must be demoted to OBSERVATION.
        """
        registry = {
            ticker: {
                "tracking_state": "LONG",
                "state_days": 1,
                "last_market_date": "2026-08-06",
            }
        }
        stocks = _stocks_df("UNRELATED_TICKER")
        long_candidates = pd.DataFrame({"Ticker": ["UNRELATED_TICKER"]})

        import engines.stock_transition_engine as ste
        original_loader = ste.load_previous_long_watchlist
        ste.load_previous_long_watchlist = lambda: pd.DataFrame({"Ticker": [ticker]})

        result_registry, _ = pre_distribution_update(
            registry=registry,
            current_long_candidates=long_candidates,
            stocks=stocks,
        )

        ste.load_previous_long_watchlist = original_loader

        assert ticker in result_registry, (
            f"{ticker} was in LONG but silently disappeared from registry "
            f"when absent from stocks CSV"
        )
        assert result_registry[ticker]["tracking_state"] == OBSERVATION, (
            f"{ticker} must be demoted to OBSERVATION (not purged) "
            f"when absent from stocks CSV"
        )
        out = capsys.readouterr().out
        assert "WARNING" in out, (
            f"A [TRANSITION WARNING] must be emitted when {ticker} "
            f"vanishes from the stocks universe"
        )

    @pytest.mark.parametrize("ticker", ALL_INCIDENT_TICKERS)
    def test_no_silent_disappearance_any_ticker(self, ticker, capsys):
        """
        Meta-test: for any of the 11 tickers in any tracked state, absent
        from today's CSV, assert registry is non-empty and a warning was
        emitted.  No silent disappearance is acceptable.
        """
        for state in (OBSERVATION, DISTRIBUTION):
            registry = {
                ticker: {
                    "tracking_state": state,
                    "state_days": 2,
                    "last_market_date": "2026-08-07",
                }
            }
            stocks = _stocks_df("DUMMY")
            long_candidates = pd.DataFrame({"Ticker": ["DUMMY"]})

            import engines.stock_transition_engine as ste
            original_loader = ste.load_previous_long_watchlist
            ste.load_previous_long_watchlist = lambda: pd.DataFrame(columns=["Ticker"])

            result_registry, _ = pre_distribution_update(
                registry=registry,
                current_long_candidates=long_candidates,
                stocks=stocks,
            )

            ste.load_previous_long_watchlist = original_loader

            assert ticker in result_registry, (
                f"SILENT DISAPPEARANCE: {ticker} in {state} vanished from "
                f"registry when absent from stocks CSV — bug not fixed"
            )
            out = capsys.readouterr().out
            assert "WARNING" in out, (
                f"No warning emitted for {ticker} in {state} vanishing from "
                f"stocks universe — invariant not firing"
            )
