TABELA = institutional capital rotation engine

Primary objective:
Detect strongest themes for LONG swing trades

Secondary objective:
Detect weakest themes for SHORT swing trades

Protected modules:
long_engine.py
composite_engine.py
stock_history_engine.py

Architecture rules:
- Snapshot JSON stores raw market state only
- Historical intelligence derived later
- Do not add complexity without improving capital flow detection

Current theme engine:
Leading = top 20%
Neutral = middle 60%
Lagging = bottom 20%

Emerging and Weakening derived from history only

Never change architecture without explicit approval