# FUTURE_MAINTENANCE_WORKFLOW.md

## DAILY WORKFLOW

Run:

python main.py

System automatically performs:

* Market Scan
* Daily Log Generation
* Rotation Comparison
* Save Daily Snapshot

No manual action required.

---

## WEEKLY WORKFLOW

Frequency:

Every weekend

System automatically creates weekly log.

User action:

Optional review.

ChatGPT Prompt:

ThemePulse Weekly Institutional Rotation Review

Upload:

* Current week log
* Previous week log

Objective:

Analyze institutional capital rotation.

Questions:

* Which themes strengthened?
* Which themes weakened?
* Which long opportunities deserve focus?
* Which short opportunities deserve focus?

Estimated time:

5 minutes

---

## MONTHLY WORKFLOW

Frequency:

Month end

System automatically creates monthly log.

User uploads:

4 weekly logs

ChatGPT performs:

Monthly institutional review.

Questions:

* Which themes dominated month?
* Which themes deteriorated?
* Which new themes are emerging?
* What should be long focus next month?
* What should be short focus next month?

Estimated time:

10–15 minutes

---

## QUARTERLY WORKFLOW

Frequency:

Every 3 months

Review:

Classification database quality.

Tasks:

* Add missing stocks
* Remove obsolete stocks
* Improve theme coverage

Focus:

company_theme_engine.py

Estimated time:

20 minutes

---

NON NEGOTIABLE RULE

All maintenance must remain simple.

No manual data copy/paste.

Automation first.
