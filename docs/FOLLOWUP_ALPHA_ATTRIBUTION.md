# Strategic Follow-Up: The Alpha Attribution Engine

**Date Documented:** October 1, 2026

## Objective
Evolve the TABELA pipeline from a binary filter (90/90 pass/fail) into a probabilistic stock-picking engine optimized for Swing Trading (hold times of 3 days to 3 weeks).

## The Concept: Alpha Attribution
Instead of stopping at aggregate win rates, we need an engine to perform micro-attribution on the winning setups to find compounding variables that isolate high-probability trades (e.g., separating a 45% standard breakout from a 62% elite breakout).

## Required Architectural Features
1. **MFE / MAE Tracking:** (Maximum Favorable / Adverse Excursion). Track the forward trajectory of trades to establish optimal swing-trading stop-loss parameters and understand the pain threshold of winning trades.
2. **Multi-Variate Correlation:** Identify compounding variables (e.g., Zacks Rank + Volume Surges + Specific Theme standings) that dramatically increase the default 90/90 win rate.
3. **Probability Classifier Output:** The daily `distribution_watchlist` / `long_candidates` should not just list stocks, but assign them a Conviction Tier (e.g., A+, B) based on historical probability correlation.

## Status
Parked for future implementation. System architecture is currently locked and stabilized. Review this document when ready to commence Phase 4 (Probabilistic Stock Picking).
