# TABELA — ARCHITECTURE RULES

## PURPOSE

TABELA is a proprietary institutional capital rotation intelligence system.

Primary objective:

Detect institutional capital movement.

Everything else is secondary.

Architecture quality is more important than speed of development.

Signal quality is more important than feature quantity.

No feature should be added simply because idea sounds interesting.

---

# RULE 1 — THREE LAYER ARCHITECTURE

Every module must belong to one of three layers.

## LAYER A — CORE ENGINE (PROTECTED)

Core engine is mandatory.

Core engine must always run successfully.

Core engine must depend ONLY on mandatory daily input files.

Mandatory files:

• ETF.csv
• stocks.csv

Core engine modules:

• ETF Engine
• Theme Parser
• Theme Classification Engine
• Stock Mapper
• Scoring Engine
• Long Engine
• Short Engine
• Rotation Engine

Core engine must never depend on optional modules.

Core engine is production protected.

---

## LAYER B — INTELLIGENCE LAYER (OPTIONAL)

Intelligence layer improves output quality.

Intelligence layer must never become mandatory dependency.

If intelligence layer fails or disappears:

Core engine must continue working normally.

Examples:

• Snapshot Engine
• History Engine
• Persistence Engine
• Weekly Review Engine
• Future Deterioration Engine
• Future Rotation Intelligence

Intelligence layer enhances system.

It must never control system stability.

---

## LAYER C — EXPERIMENTAL LAYER (RESEARCH)

Experimental layer is research only.

Experimental layer may fail.

Experimental layer may be deleted anytime.

Experimental layer must never affect production architecture.

Examples:

• Behavioral Anomaly Engine
• AI Analysis Engine
• Machine Learning Engine
• Future Prediction Models

Experimental ideas must prove signal quality before promotion.

---

# RULE 2 — NO OPTIONAL DEPENDENCIES

Core engine must never require:

• Historical data
• JSON snapshots
• AI models
• Experimental outputs
• Future analytics layers

If optional files disappear:

TABELA must still run successfully.

Bad design example:

Core engine failing because history folder is empty.

This is prohibited.

---

# RULE 3 — HARD CODING CONTROL

Hard coding should be minimized.

Permanent business logic must not be buried inside engine files.

Research assumptions should not be hardcoded directly in production code.

Move assumptions to:

• config.py
• research_config.py
• CSV configuration files

Examples:

Do NOT hardcode:

• Scoring weights
• ETF ranking weights
• Threshold values
• Theme mappings
• Classification rules

Hardcoded logic should be externally maintainable.

---

# RULE 4 — CONFIGURATION FIRST DESIGN

Every configurable assumption must live outside engine files.

Examples:

Allowed:

config.py

research_config.py

company_theme_mapping.csv

Not allowed:

Hardcoded thresholds inside engine logic.

Example:

Bad:

if rs > 80

Good:

if rs > RS_THRESHOLD

Engine files should contain logic.

Config files should contain assumptions.

---

# RULE 5 — MARKET OUTPUT IS FINAL TRUTH

Elegant code has no value if output quality is poor.

Always trust real market output over theoretical design.

Before approving any feature ask:

Would professional traders care about this output?

Would institutional traders care about this output?

Would I personally open the chart for this output?

If output quality is poor:

Reject feature immediately.

Never defend weak logic because code works.

---

# RULE 6 — PRESERVE STABLE MODULES

Never casually modify stable production modules.

Protected modules:

• Long Engine
• ETF Engine
• Scoring Engine (until reviewed)
• Rotation Engine

Before changing stable code:

Challenge architecture first.

Preserve backup copy first.

Avoid unnecessary redesign.

Minimal code change preferred.

Backward compatibility preferred.

---

# RULE 7 — NO FORCED FEATURES

Never build features unsupported by available data.

Data capability defines intelligence capability.

Do NOT force elegant market theory into code.

Example:

Behavioral anomaly detection requires historical data.

Single-day ETF.csv and stocks.csv do not support anomaly detection.

If data cannot support feature:

Do not build feature.

---

# RULE 8 — SIGNAL QUALITY DOMINATES

Always prefer fewer high quality signals over many weak signals.

Low quality output damages system credibility.

Never optimize for feature count.

Never build features producing noisy outputs.

Signal quality > feature quantity.

---
# RULE 9 — MAINTENANCE PROCESS

TABELA maintenance must remain lightweight.

Maintenance should never become operational burden.

Goal:

Keep architecture healthy without creating process friction.

There will be ONLY ONE maintenance cycle.

Frequency:

Once every week.

Maximum time:

30 minutes.

No separate monthly or quarterly maintenance process.

Monthly and quarterly checks will be absorbed inside weekly review.

---

## WEEKLY MAINTENANCE (EVERY WEEK)

Time required:

15–30 minutes maximum.

Regular weekly checks:

Review:

• New emerging market themes
• Company theme mapping accuracy
• New stocks requiring theme mapping
• Obsolete or outdated theme classifications
• Hardcoded ticker mappings
• Failed or unclassified stock mappings

Question:

Is TABELA still correctly understanding current market structure?

---

## EVERY 4TH WEEK (MONTHLY CHECK INSIDE WEEKLY REVIEW)

Additional review required only once every 4 weeks.

Review:

• Scoring engine weights
• ETF ranking weights
• Long engine output quality
• Short engine output quality
• Quality of top ranked long candidates
• Quality of short weakness candidates
• Whether scoring assumptions still make sense

Questions:

Are strongest stocks being ranked correctly?

Are weak stocks genuinely weak?

Is analyst-based scoring overweighted?

Is market behavior being prioritized correctly?

---

## EVERY 12TH WEEK (QUARTERLY CHECK INSIDE WEEKLY REVIEW)

Additional deep review required only once every 12 weeks.

Review:

• Entire architecture design
• Dependency structure
• Core vs optional module separation
• Scalability of codebase
• New feature creep
• Whether optional modules are accidentally becoming dependencies
• Whether TABELA still reflects current market regime

Questions:

Is architecture becoming fragile?

Has unnecessary complexity been introduced?

Are new features improving signal quality?

Are low quality signals creeping into system?

Is project still aligned with institutional capital flow detection?

---

## MAINTENANCE GOLDEN RULE

Maintenance should improve architecture quality.

Maintenance must never become operational burden.

If maintenance process becomes difficult:

Simplify process immediately.

TABELA must remain scalable.

Low friction architecture is mandatory.


Zacks column "Avg Volume" shall be interpreted by TABELA as Daily Traded Volume.

For all internal calculations and historical logging, this field represents current session traded volume, not average historical volume.