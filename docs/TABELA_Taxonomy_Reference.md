# TABELA Taxonomy & Narrative Reference

**Purpose:** Running, compounding record of taxonomy decisions and narrative-drift observations across weekly TABELA reports.

**Important — mapping tables live elsewhere:** as of 2026-07-18, the actual Industry→Theme and Stock→Theme mappings are maintained in two separate files in Project Knowledge:
- `industry_theme_mapping.csv`
- `stock_theme_mapping.csv`

This document does **not** duplicate those tables. It tracks the *reasoning trail* around them — open questions, narrative-drift flags, confirmed changes (with dates, for history), and the rotating sweep log. Any time a mapping is proposed or changed, the actual edit happens in the CSVs; this file just records that it happened and why.

**How to use this file:**
- At the start of each weekly review, check the Narrative Drift Watchlist and Sweep Log below before treating anything as new.
- After each weekly review, update the relevant section(s). Don't delete resolved entries — move them to the Resolved Log so the reasoning history is preserved.

---

## 1. Narrative Drift Watchlist (Longs & Unknowns only)

Names whose current external narrative may have moved past their taxonomy label. A ticker moves here when flagged, and moves to Section 3 (Confirmed Changes) once verified and the CSV is updated — it should not sit in both places at once.

| Ticker | Current CSV label | Observed narrative concern | Evidence | Status | First flagged |
|---|---|---|---|---|---|
| INTC | AI Compute | Dominant current narrative centers on foundry turnaround (18A process) rather than AI compute leadership, where it trails NVDA/AMD | Not yet independently verified — flagged during GE/PLTR pass, needs its own check | **Open — needs verification** | 2026-07-18 |
| HOOD | Retail Trading Platform | Business has expanded into crypto, prediction markets, banking/wealth — label may now be narrower than the business | Not yet independently verified | **Open — needs verification** | 2026-07-18 |
| NOW | Enterprise Cloud | Narrative increasingly centers on agentic AI (Agentforce-style positioning) rather than generic cloud software | Not yet independently verified | **Open — needs verification** | 2026-07-18 |
| CRM | Enterprise Cloud | Same concern as NOW — agentic AI framing vs. generic enterprise cloud label | Not yet independently verified | **Open — needs verification** | 2026-07-18 |

---

## 2. Known Pipeline / Taxonomy Contradictions

Cases where the live JSON's `maintenance.unknown` module disagrees with itself or with the CSVs — tracked separately from narrative drift since the fix is usually a data-propagation issue, not a research question.

| Issue | Description | Status | Weeks observed |
|---|---|---|---|
| Industry-level vs. ticker-level mapping gap | Industry-level approvals (e.g., "Financial - Miscellaneous Services → Financial Services") existed in `industry_theme_mapping.csv` without corresponding rows for individual tickers (MRX, VIRT, ABX) in `stock_theme_mapping.csv`, causing repeated "unknown" flags at the ticker level despite an approved industry rule | **Resolved 2026-07-18** — ticker rows added directly to the CSV (see Section 3) | 2 (07-07 to 07-11, 07-13 to 07-17) |

---

## 3. Confirmed Mapping Changes (Log)

Dated record of edits made directly in the CSV files, for history and auditability. The CSVs are the source of truth going forward — this is just the "why and when."

| Date | Ticker/Industry | Change | Reason |
|---|---|---|---|
| 2026-07-18 | GE | Remapped: Industrial Automation → **Aerospace & Defense** | Post-2024 breakup, GE trades solely as GE Aerospace (pure-play aviation); GE Vernova and GE HealthCare are separate tickers. Old label described a company that no longer exists. |
| 2026-07-18 | PLTR | Remapped: Defense Software → **AI Platform** | Commercial AI (AIP) revenue overtook government revenue in 2026 and is forecast to reach 61% of total by 2030; dominant narrative is enterprise AI, not defense-specific software. |
| 2026-07-18 | MRX, VIRT, ABX | Added: → **Financial Services** | Resolved the industry/ticker propagation gap (Section 2) — industry-level mapping was already approved, ticker rows were simply missing. |
| 2026-07-18 | LINC, UTI | Added: → **Education** | Consistent with already-approved (LOW confidence) "Schools → Education" industry mapping. |
| 2026-07-18 | VCTR | Added: → **Financial Services** | Identified as Victory Capital Holdings, an asset management firm; mapped under new "Financial - Investment Management" industry rule below. |
| 2026-07-18 | Financial - Investment Management (industry) | Added: → **Financial Services**, MEDIUM confidence | New industry cluster surfaced via VCTR + repeat unknown-industry occurrences; MEDIUM (not HIGH) pending a second week of supporting names. |

---

## 4. Extended Taxonomy Sweep Log

Tracks progress of the rotating, calendar-triggered full-file sweep (runs when a weekly report's `end_date` falls in the last 7 days of the month). Each sweep covers roughly 1/3 of `stock_theme_mapping.csv`, cycling through the full file about once per quarter. Read this table before starting a new sweep — treat it as authoritative over conversation memory.

| Date | Rows/Tickers Covered | Confirmed Drift Found | Flagged (Unverified) |
|---|---|---|---|
| 2026-07-18 | Ad hoc initial pass — not a full rotating slice, prompted by a user example rather than the calendar trigger | GE → Aerospace & Defense; PLTR → AI Platform (see Section 3) | INTC, HOOD, NOW, CRM (see Section 1) |

**Next sweep should start from row 1 of `stock_theme_mapping.csv`** — the entry above was a targeted ad hoc pass, not slice 1 of the systematic rotation, so it doesn't count toward first-slice coverage.

---

## 5. Resolved / Historical Log

Fully closed items (mapped, drift confirmed-and-remapped, or drift confirmed-as-noise-and-dismissed) move here once done, preserving the reasoning trail.

| Date resolved | Item | Resolution |
|---|---|---|
| 2026-07-18 | MRX/VIRT/ABX taxonomy contradiction (2-week open item) | Resolved by adding missing ticker-level CSV rows — see Sections 2 and 3 |

---

## Maintenance notes
- This file, `industry_theme_mapping.csv`, and `stock_theme_mapping.csv` should be re-uploaded to Project Knowledge whenever edited — I don't have write access to Project Knowledge directly.
- If Section 1 (Narrative Drift Watchlist) or Section 4 (Sweep Log) grow large over time, they can be split by year without losing the format.
