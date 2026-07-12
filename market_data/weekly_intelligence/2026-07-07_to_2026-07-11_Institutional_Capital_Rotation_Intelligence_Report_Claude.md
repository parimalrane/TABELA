# Weekly Institutional Intelligence Review
**Coverage window:** 2026-07-07 to 2026-07-11 (5 trading days, 5 runs loaded)
**Non-advisory notice:** This report contains no trading recommendations, price targets, or position sizing. All content is observational and analytical.

---

## 1. Executive Summary

Two independent lines of evidence point to the same conclusion this week: the taxonomy layer has drifted ahead of the scoring layer. Four themes (Financial Services, Education, Cybersecurity, Automotive Technology) now have industry mappings defined in `taxonomy.theme_to_industries` but zero presence in `themes.details` — their industries are simultaneously "mapped" and "unknown" depending on which part of the pipeline is asked. This is a confirmed propagation defect, not a market observation, and it silently excludes at least two persistent-long candidates (MRX, VIRT) from theme-level scoring.

On the market side, the week's dominant pattern is a **broad-based unwind in financials** (Insurance, Banking, Brokers/Capital Markets, Regional Banks all declined, with a consistent mid-week peak and Thursday–Friday deterioration) running alongside **relative-strength gains in low-conviction growth/defensive themes** (Cloud Computing, Telecom, Internet, Media) whose absolute scores remain near zero. This looks more like capital vacating financials than capital convicting into the themes gaining rank — a rotation of avoidance rather than a rotation of conviction. Separately, Biotech and Healthcare — both "persistent leaders" — show a clean mid-week score peak followed by three straight days of decay even as their rank held near the top, a distribution pattern that rank-only monitoring would miss entirely. Aerospace & Defense is the week's cleanest structural break: a monotonic five-day decline with no single-day discontinuity, consistent with sustained selling rather than a headline-driven air pocket.

## 2. Institutional Intelligence

**Financials: rotation out, not rotation in.** Insurance, Banking, and Brokers/Capital Markets all peaked on 07-08 and declined every subsequent day through 07-11 (Insurance 6.93→-0.05, Banking 4.68→-0.01, Brokers 3.90→-1.22). The synchrony across three related themes, all breaking on the same day, is stronger evidence of a common driver than three independent theme-level rotations. — *Confidence: Medium.* The JSON contains no macro or catalyst data, so the trigger (rates, earnings, positioning unwind) cannot be identified from this file alone; only the pattern and its timing are observable.

**Growth/defensive "leadership" is thin.** Cloud Computing, Telecom, and Internet all show rank improvements of 6+ positions, but their end-of-week scores are barely positive (3.66, 0.85, 0.16). Compare this to Semiconductors, which improved rank while holding a score of 6.42 — an order of magnitude larger. Rank gains built on near-zero absolute scores are consistent with these themes simply losing less than the financials complex, not attracting fresh capital. — *Confidence: Medium-High.* This is a mechanical read of score magnitude vs. rank change within the same file; alternative explanation is that these themes are genuinely early-stage rotation targets and the score will build in subsequent weeks — that requires next week's data to confirm.

**Persistent leadership is decaying under the surface.** Biotech and Healthcare both peaked on 07-08 and declined for three consecutive sessions into Friday, even though Biotech held rank #1 for four of five days and Healthcare stayed inside the top 4 all week. Rank-based monitoring alone would report these as stable leaders; the score trajectory says breadth within the leadership is thinning. Semiconductors, by contrast, dipped mid-week and recovered to a fresh weekly high on Friday — the opposite shape. — *Confidence: High* on the pattern itself (directly observable in daily series); *Low* on cause, since the file cannot distinguish profit-taking, sector-specific news, or index rebalancing effects.

**Aerospace & Defense is a clean structural break, not a shock.** The theme declined every single day (rank 12→21→23→26→26; score -0.17→-0.6→-2.6→-6.39→-6.74) with no bounce and no single outsized one-day move. This monotonicity is the signature of persistent selling pressure rather than a headline-driven gap. It is also the only theme with an active short-side persistent candidate (RKLB, 4 days), which is directionally consistent with the theme-level deterioration. — *Confidence: High* on pattern; *Low* on root cause (no news/catalyst data available in this file).

**Oil complex "gains" are magnitude-only, not rank-confirmed.** Brent Oil (+6.85 score) and Crude Oil (+4.27 score) posted the two largest score gains of the week, yet Brent's rank was unchanged (33→33) and Crude's rank *worsened* (32→34) — both remain in the bottom two of 34 themes. This is a bounce off deeply oversold levels, not a leadership signal. Institutional intelligence should not conflate "largest score gain" with "most improving theme" without checking rank corroboration, which the evidence hierarchy in this workflow already prioritizes rank over score for exactly this reason.

## 3. Narrative Evolution

- **From:** broad multi-sector leadership (financials + healthcare + semis all "leading" early week) **To:** a narrower, more concentrated tape by Friday, with financials fully rotated out and only Semiconductors, Cloud Computing, and Biotech/Healthcare (decaying) still carrying leading classifications.
- **Emerging narrative:** a tentative "communications/media" cluster (Telecom, Internet, Media, Cloud Computing) gaining rank simultaneously — worth watching for whether this consolidates into a coherent theme-level rotation next week or dissipates once financials stabilize (i.e., whether the gains are relative-only or start building absolute score).
- **Fading narrative:** financials-as-leadership, which was intact through 07-09 and had fully reversed by 07-11.

## 4. Leadership Transfer

Rank-improvement evidence, cross-checked against score direction:

| Theme | Rank Δ | Score Δ | Read |
|---|---|---|---|
| Cloud Computing | +11 | +4.24 | Genuine — both rank and score improved meaningfully |
| Telecom | +6 | +1.24 | Weak — rank gain, marginal score |
| Internet | +6 | +1.31 | Weak — rank gain, marginal score |
| Media | +6 | -0.07 | Rank-only — score essentially flat/down |

Only Cloud Computing shows leadership transfer corroborated by both rank and score magnitude. The other three "emerging leaders" flagged by the deterministic layer are rank-driven, which — given the evidence hierarchy (breadth and rotation outrank raw ranking changes) — warrants treating their "emerging leader" tag with more caution than the label alone implies.

## 5. Stock Leadership Review

The long persistent-candidate list (22 tickers, 5-day duration) is overwhelmingly single-theme: 20 of 22 are Semiconductors, consistent with that theme's rank-1 Friday close and stable 5/5 "leading" days. This concentration is itself informative — it suggests the semiconductor persistence signal is broad-based within the theme (multiple names, not one or two outliers carrying it), which is a stronger form of evidence per the breadth-priority hierarchy than a single-name move would be.

The two non-Semiconductor long candidates, MRX and VIRT, are tagged theme "Financial Services" — a theme with **no scoring presence in `themes.details`** (see Section 6/7). These two names carry real 5-day persistence signals but cannot currently be evaluated against a theme-level score or rank, since the theme they're mapped to isn't being scored. This is a direct, named consequence of the taxonomy/scoring gap, not a hypothetical.

The single short persistent-candidate, RKLB (Aerospace & Defense, 4 days), is directionally consistent with that theme's monotonic five-day decline — the stock-level and theme-level signals corroborate each other here, unlike the Financial Services case.

## 6. Hidden Risks & Market Traps

1. **Silent scoring exclusion.** Financial Services, Education, Cybersecurity, and Automotive Technology are live taxonomy themes with mapped industries and (per `theme_to_companies`, though not directly counted here) member companies, but they generate zero rows in `themes.details`. Any consumer of this report who only reads theme-level rank/score tables would never know these themes exist this week — they are invisible by omission, not flagged as gaps. This is the most consequential single finding in this review because it affects what the report can and cannot see, independent of market conditions.
2. **Rank/score divergence trap in the oil complex.** Both Brent and Crude Oil show large positive score deltas while sitting in the bottom two ranks. A reader scanning only the "largest score gains" list without cross-referencing rank would misread deeply oversold bounces as emerging leadership.
3. **Leadership-label lag.** Biotech and Healthcare retain "leading" classification and top-4 ranks through Friday despite three consecutive days of score decay. The classification field (leading/neutral/lagging) is rank-derived and does not capture intra-leadership deterioration — a reader trusting the classification label alone would miss the distribution signal entirely.

## 7. Taxonomy Maintenance Review

**Confirmed propagation defect (high confidence, directly verifiable from this file):** Cross-referencing `taxonomy.theme_to_industries` against `maintenance.unknown.unknown_industries` shows that at least four "unknown" industries are in fact already mapped to themes in the taxonomy:

| Unknown industry (flagged) | Occurrences | Actually mapped to theme |
|---|---|---|
| Financial - Miscellaneous Services | 9 | Financial Services |
| Schools | 4 | Education |
| Security | 3 | Cybersecurity |
| Automotive - Original Equipment | 1 | Automotive Technology |

These four industries account for 17 of the 24 total unknown-industry occurrences this week. Their mappings exist in the taxonomy layer but are not being applied by whatever process classifies incoming tickers and builds `themes.details` — the two layers are reading from different, out-of-sync versions of the taxonomy. This is the same category of defect flagged in prior review cycles (newly-added mappings not propagating through scoring) and should be treated as a software/pipeline issue, not a market or classification judgment call, per this workflow's default attribution rule.

**Genuinely unmapped (no corresponding theme exists):** Financial - Consumer Loans (3), Food - Miscellaneous (1), Gaming (1), Internet - Delivery Services (1). These are legitimate taxonomy gaps distinct from the propagation defect above and are candidates for new mapping decisions, not bug fixes.

**Data completeness discrepancy:** `quality.completeness` reports 1.0 with zero missing days and zero warnings/errors, yet the Media theme has only 4 daily observations (missing 2026-07-07) against 5 trading days for every other theme. The top-level quality gate did not catch a theme-level gap — consistent with the previously noted blind spot in automated quality checks. This does not change Media's directional read (it still improved rank 11→5) but its 4-day average should not be compared directly to 5-day averages elsewhere without adjustment.

## 8. Taxonomy Recommendations

Per this workflow's conservative-recommendation rule, no new theme, industry, or company mapping changes are recommended this week. `maintenance.stock_mapping_candidates`, `industry_mapping_candidates`, `theme_mapping_candidates`, `possible_new_themes`, and `possible_retired_themes` are all empty, and the evidence gathered above points to a **pipeline defect requiring engineering investigation**, not a taxonomy design decision requiring analyst judgment. Recommending taxonomy edits on top of a confirmed propagation bug risks masking the underlying defect rather than fixing it.

- **Theme Updates:** None recommended. Flag for engineering: confirm why Financial Services, Education, Cybersecurity, and Automotive Technology mappings are not reaching the scoring/classification stage.
- **Industry Updates:** None recommended for the four already-mapped-but-flagged industries above (mapping exists; this is a propagation issue). The four genuinely unmapped industries (Financial - Consumer Loans, Food - Miscellaneous, Gaming, Internet - Delivery Services) are candidates for a future mapping decision but each has only 1–3 occurrences this week — below a threshold this review considers sufficient for a confident recommendation.
- **Company Updates:** None recommended. MRX and VIRT are correctly tagged to Financial Services in `theme_to_industries`/stock data; the issue is downstream propagation, not mis-mapping.

## 9. Intelligence Gap Review

- No macro, catalyst, or news context is available in this file, so root causes for the financials unwind, the Biotech/Healthcare score decay, and the Aerospace & Defense decline cannot be determined — only their shape and timing.
- Persistent-unknowns list is empty and emerging-unknowns are capped at 1–3 days each, so there is no multi-week persistence evidence yet on any currently-unmapped name; a verdict on whether they deserve new mappings should wait for additional weeks of data per the evidence hierarchy's persistence-first weighting.
- The scoring exclusion for Financial Services means this review cannot assess whether MRX/VIRT strength reflects a genuine sub-theme rotation or idiosyncratic single-name moves — that gap will persist until the pipeline defect is fixed.

## 10. Next Week Validation

To confirm or falsify this week's read:
- Does the financials complex (Insurance, Banking, Brokers, Regional Banks) stabilize or continue declining? Continued decline across all four next week would upgrade the "broad rotation out of financials" read from Medium to High confidence.
- Do Cloud Computing / Telecom / Internet / Media build absolute score, or does their rank gain fade once financials stop declining? This distinguishes genuine capital rotation from relative-strength-by-default.
- Does Biotech/Healthcare score continue decaying while rank holds, or does it stabilize? A fourth and fifth consecutive down day would strengthen the distribution read.
- Does Financial Services (and Education, Cybersecurity, Automotive Technology) appear in `themes.details` next week? If yes, the propagation defect was fixed. If no, this is now a two-week-persistent pipeline defect warranting escalation beyond a single-report flag.

## 11. Highest Conviction Observations

1. Financial Services / Education / Cybersecurity / Automotive Technology are mapped-but-unscored themes — a confirmed, directly-verifiable pipeline defect (High confidence).
2. Insurance, Banking, and Brokers/Capital Markets all peaked 07-08 and declined synchronously through 07-11 (High confidence on pattern; Medium on interpretation as a common driver).
3. Aerospace & Defense declined monotonically all five days with no bounce (High confidence on pattern; Low on cause).
4. Biotech and Healthcare peaked 07-08 and decayed three straight days into Friday despite holding top-4 rank (High confidence on pattern; Low on cause).

## 12. Lowest Conviction Observations

1. Telecom, Internet, and Media "emerging leadership" — rank gains are real but score magnitudes are too small to distinguish genuine rotation from relative outperformance in a weak tape (Low-Medium confidence).
2. Brent Oil / Crude Oil score gains as a leadership signal — contradicted by unchanged/worsening rank; likely an oversold bounce, not conviction buying (Low confidence as a leadership signal; the bounce itself is High confidence as a fact).
3. Uranium Mining, Mlp, Timber small rank improvements (+2 to +3) — score changes are marginal (+0.07 to +1.92) against deeply negative bases and could reflect noise rather than a rotation signal (Low confidence).

## 13. Structural vs Tactical Rotation

**Likely structural (multi-day, monotonic, broad):** Aerospace & Defense decline; the financials complex unwind (Insurance/Banking/Brokers). Both show consistent day-over-day direction across the full week rather than a single-day spike, which per the evidence hierarchy's persistence-priority is the stronger signal of the two categories.

**Likely tactical (bounce, single-driver, or breadth-thin):** Brent/Crude Oil score gains (oversold bounce from bottom-2 ranks); Biotech/Healthcare's continued top-rank status despite score decay (looks structural on rank, tactical/fading on score — a genuine mixed signal worth flagging rather than forcing into one category).

**Indeterminate — needs more weeks:** Cloud Computing / Telecom / Internet / Media cluster. One week of rank improvement on thin score is not enough evidence to classify either way.

## 14. Open Questions

- Is the financials unwind sector-specific (rates, regulatory) or part of a broader risk-off move that hasn't yet reached other cyclicals? Not determinable from this file.
- Will the Financial Services / Education / Cybersecurity / Automotive Technology scoring gap self-resolve, or does it require a manual pipeline fix? This should be tracked explicitly until closed.
- Are MRX and VIRT's persistence signals representative of a broader "Financial - Miscellaneous Services" cohort, or are they outliers? Cannot be assessed while the theme remains unscored.
- Does the Biotech/Healthcare score decay reflect genuine institutional distribution, or a mechanical effect of the scoring model (e.g., mean reversion built into the score formula itself)? This review has no visibility into the scoring methodology needed to distinguish the two.
