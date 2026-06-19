# THEMEPULSE ENGINEERING CONTINUITY CONTEXT

============================================================
PROJECT IDENTITY
================

ThemePulse is a proprietary institutional capital rotation research engine.

Primary Objective:

Detect where institutional money is flowing.

Trade LONG strongest themes.

Trade SHORT weakest themes.

Core Philosophy:

Institutional Capital Flow First.

Institutional Narrative > Traditional Sector Classification.

============================================================
CURRENT PROJECT STATUS
======================

Version:

ThemePulse V1

Status:

Production Ready

Architecture Status:

Frozen

Development Status:

Observation Phase

No immediate architecture modifications allowed until sufficient live market observations collected.

============================================================
CURRENT SYSTEM ARCHITECTURE
===========================

ThemePulse operates as a unified production system.

Architecture evolved from:

Theme Rotation Scan (Prompt Based CSV Analysis)

↓

ThemePulse Python Engine

Current architecture is fully modular.

Main Components:

ETF Relative Strength Engine

Theme Classification Engine

Stock Theme Mapping Engine

Company Theme Override Engine

Theme Translation Engine

Composite Scoring Engine

Long Watchlist Engine

Short Watchlist Engine

Breadth Engine

Production Output Engine

============================================================
CORE SCORING MODEL
==================

Composite Score Formula

Theme Strength = 40%

Stock RS Rating = 30%

Sales Growth = 20%

Zacks Rank = 7%

Profit Margin = 3%

============================================================
KEY IMPLEMENTED SYSTEMS
=======================

Custom Stock RS Rating

(IBD / DeepVue approximation)

ETF RS Rating Engine

(Objective theme strength classification)

Stock → ETF → Theme Mapping Engine

Relative Weakness Shorts Engine

Long Logic:

Allow Rank 3 stocks in Emerging themes

Short Logic:

Allow Rank 3 stocks in Weakening / Lagging themes

Short Protection Rule:

Exclude Zacks Rank 1 and Rank 2 from Relative Weakness Shorts

============================================================
CRITICAL ARCHITECTURE DECISIONS
===============================

Decision 1

Unknown stocks must NEVER be automatically discarded.

Reason:

A stock may have strong institutional sponsorship even if theme mapping is incomplete.

Real examples observed during development:

LITE

BE

Principle:

Institutional Narrative > Classification Accuracy

---

Decision 2

ThemePulse V1 architecture is frozen.

Reason:

Stable production systems must be observed under real market conditions before continuous code modification.

Principle:

Observe market behavior first.

Modify code later.

---

Decision 3

Development discipline rules.

Rules:

Modify one module at a time.

Never modify multiple files simultaneously.

Test after every isolated change.

Documentation before coding.

Protect architecture stability.

---

Decision 4

Single unified ThemePulse architecture is superior to splitting ETF + Stock engines separately.

============================================================
KNOWN LIVE PRODUCTION OBSERVATIONS
==================================

Observation 1

Breadth calculation flaw.

Problem:

Themes with one stock can show 100% breadth and incorrectly appear stronger than larger institutional themes.

Example:

AI ASIC = 100%

Semiconductors = 73%

Issue:

Mathematically correct but intellectually misleading.

---

Observation 2

ETF universe pollution.

Problem:

Country and regional ETFs currently dominate market rotation output.

Examples:

EWY

EWT

EPI

Peru

South Korea

Taiwan

Issue:

User trades US market only.

Global geographic ETFs reduce signal quality.

---

Observation 3

Institutional Leaders output duplication.

Problem:

TOP LONG WATCHLIST and TOP 20 INSTITUTIONAL LEADERS currently produce nearly identical output.

Issue:

Institutional Leaders section adds limited additional information.

============================================================
KNOWN PENDING IMPROVEMENTS
==========================

Priority 1

ETF Universe Purification Engine

Goal:

Remove country and regional ETFs.

Examples:

EWY

EWT

EPI

Country specific ETFs

---

Priority 2

Breadth Quality Engine

Goal:

Prevent tiny themes from ranking artificially high.

Incorporate:

Breadth %

Theme Size

Average Composite Score

---

Priority 3

Institutional Leaders Redesign

Goal:

Remove duplicate output overlap with Long Watchlist.

Future options:

Remove section completely

OR

Redesign around true institutional accumulation logic

============================================================
FUTURE DEVELOPMENT ROADMAP
==========================

Next Major Project:

Project 3 = Technical Setup Engine

Purpose:

Determine WHEN to enter after ThemePulse identifies candidates.

Will Analyze:

EMA Alignment

Breakout Detection

Volume Expansion

Consolidation Patterns

Short Setup Quality

Long Term High Priority Modules

Institutional Behavior Engine

Volume Dry Up Detection

Distribution Day Detection

Accumulation Day Detection

Breadth Trend Engine

Theme Quality Engine

============================================================
ENGINEERING WORKFLOW RULE
=========================

All future ThemePulse discussions happen ONLY in this single chat.

Allowed Discussions:

Development

Debugging

Architecture Decisions

Refactoring

Future Enhancements

Version Upgrades

Module Development

Not Allowed:

Trading Journal

Weekly Market Review

Trading Psychology

General Stock Discussions

Rule:

Avoid multiple ThemePulse chats.

Preserve single engineering continuity.

============================================================
RESUME PROTOCOL
===============

If returning after long break:

Start with:

Continue ThemePulse.

Then specify:

Current Focus:

Bug Fix

New Module

Architecture Discussion

Future Enhancement

No warmup needed.

This chat contains full project continuity.

============================================================
END OF CONTINUITY STATE
=======================


Current Stable State

Tabela V1.3 Stable

Core Philosophy

Tabela is not a stock screener.

Tabela is an institutional capital flow engine.

Primary Objective

Detect strongest institutional themes in US market.

Generate long and short candidate universe for manual chart review.

Current Output Structure

1. Market Rotation Summary

2. Theme Breadth Analysis

3. Long Candidate Universe

4. Short Candidate Universe

Engineering Principle

Do not optimize based on intuition.

Always trace output backward:

Stock
→ Theme Mapping
→ Theme Classification
→ RS Rating
→ Composite Score
→ Output Rule
