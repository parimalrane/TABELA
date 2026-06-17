PROJECT RULE — DYNAMIC NARRATIVE CLASSIFICATION

Stocks are NOT classified by traditional accounting sector definitions.

Stocks are classified by the dominant institutional narrative currently driving capital flows.

Principle:

Institutional money buys future narratives, not historical business categories.

Examples:

TSLA

2023 → EV Growth

2026 → Autonomous Driving AI / Robotics

META

Traditional → Social Media

Current Narrative → AI Infrastructure

COIN

Traditional → Crypto Exchange

Current Narrative → Digital Assets Infrastructure

Rule:

company_theme_engine.py must remain dynamic and periodically updated based on current institutional market narratives.

Static business classifications are intentionally avoided.

Objective:

Track where institutional capital is flowing NOW.

Future Development Philosophy

Current project goal is completion, not perfection.

Potential enhancements must be documented in FUTURE_ENHANCEMENTS.md and NOT added immediately.

Rule:

Do not continuously modify core architecture after production stability is achieved.

New features must be validated against real market behavior first.


NEW ARCHITECTURE DECISIONS

Decision 14

Allowed ETF whitelist is mandatory.

Reason

Broad ETF universe introduces country and non-actionable theme contamination.

Decision 15

Tabela output will use a single Long Candidate Universe.

Reason

Separate Long Watchlist and Institutional Leaders created unnecessary duplication.

Decision 16

Institutional flow candidates not selected by primary long rules will be marked with *.

Reason

Provides visual distinction during manual chart review.

Decision 17

Breadth scoring must reward large institutional participation.

Reason

Themes with 1 stock should not outrank dominant institutional themes such as Semiconductors.




SCORING PRINCIPLE

ThemePulse scoring models must prioritize recent institutional behavior over historical performance.

Recent timeframes should carry higher weight than older timeframes.

However, very short-term periods (1 week) must have limited influence to avoid noise and temporary profit booking distortion.




GLOBAL SCORING RULE

Recent market behavior must carry more weight than historical performance.

Tabela prioritizes recent institutional rotation over legacy performance.


