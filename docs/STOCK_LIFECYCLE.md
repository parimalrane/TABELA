# TABELA Data Flow & Stock Lifecycle Architecture

> **Purpose:** This document maps the authoritative flow of a stock candidate throughout the TABELA Market Intelligence Platform. It outlines the precise triggers for promotion, grace persistence, demotion, structural tracking, and ultimate eviction from the system.

## 1. System Data Flow Diagram

```mermaid
graph TD
    %% Base Data
    Universe[External ETF / Stock CSVs] --> scoring(Scoring & Classification)
    
    %% Engine Pipeline
    scoring --> LC_Natural[Natural Long Watchlist]
    scoring --> LC_Instit[Institutional Leaders]

    %% Long Candidates Pool
    LC_Natural --> LC_Pool{Long Candidate Universe}
    LC_Instit --> LC_Pool
    Grace[Grace / Memory Injection] --> LC_Pool
    
    %% Registry Evaluation
    LC_Pool --> RE_Valid[Registry Engine Validates State]
    
    %% State Machine Transitions
    RE_Valid -- Sustains Breakout --> State_Long[STATE: LONG]
    RE_Valid -- Drops Below 80 RS or L_Score --> State_Obs[STATE: OBSERVATION]
    State_Obs -- Re-triggers 85/85 Breakout (Not Lagging) --> State_Long
    State_Obs -- "Wait Duration (21 Days) OR Long Score < 60" --> RE_D_Test{Distribution Engine Test}
    RE_D_Test -- Exhibits Accumulation Dumping (Neutral/Lagging) --> State_Dist[STATE: DISTRIBUTION]
    RE_D_Test -- Benign Bleed OR Leading Theme --> Purge[Purged / Untracked]
    State_Dist -- Re-triggers 85/85 Breakout (Not Lagging) --> State_Long
    State_Dist -- Theme turns Leading --> Purge
```

## 2. Definitive Lifecycle Breakdown

### Phase 1: Entry into LONG
A stock enters the `LONG` tracking state organically by qualifying as a top-tier candidate on any given trading day.
* **Via Natural List:** It must belong to a `Leading` or `Unclassified Leader` theme, and possess structural baseline strength (`RS_Rating >= 90`, `Long_Score >= 85`).
* **Via Institutional Elite:** It must strictly belong to a `Leading` theme and boast ultra-premium metrics (`Composite_Score >= 90` OR `RS_Rating >= 95`).
* **Via Re-Entry (Recovery):** If a stock currently tracked in `OBSERVATION` or `DISTRIBUTION` recovers to `RS_Rating >= 85` and `Long_Score >= 85`, and its theme is not `Lagging`, it is immediately promoted to `LONG` and prefixed with `^` (e.g. `^WDC`).
* *Action:* TABELA writes the stock into `registry.json` as `"LONG"`.

### Phase 2: Sustaining LONG (The Grace Period)
Because highly-ranked stocks experience temporary daily pullbacks (e.g., a Leading theme drifting to Neutral for two days), TABELA implements a **Grace Leniency** to prevent rapid flickering.
* **The Mechanism:** When a previously-LONG stock falls out of the natural generation lists, the Transition Engine checks a fallback threshold before discarding it.
* **The Rule:** If the stock's `Long_Score >= 80` AND its `RS_Rating >= 80`, it is granted an extension. It is allowed to stay in the `LONG` state within the registry.
* **The Output Injection:** The `pipeline/` script automatically scoops up any stock in the registry with a `"LONG"` stamp and aggressively injects it back into the daily presentation report—regardless of its current Theme limitations. 

### Phase 3: Demotion to OBSERVATION
When a stock's baseline structure genuinely breaks down, patience runs out.
* **The Trigger:** Inside the Transition Engine, if *either* the `Long_Score` collapses below `80` OR the `RS_Rating` drops below `80`, the stock violently fails its grace check.
* **The Action:** The engine revokes its `"LONG"` identity and overwrites its registry state to `"OBSERVATION"`, starting a countdown clock (`state_days = 1`).
* **Reporting:** The stock exits the Long Candidates screen and populates the Observation Watchlist.

### Phase 4: Navigating OBSERVATION
Observation serves as an analytical waiting room (a purgatory) to determine if a pullback was merely a shakeout or the start of institutional distribution.
* **The Timeline:** A stock typically resides in Observation pending exactly 21 trading days (`OBSERVATION_MAX_DAYS`). 
* **Fast Failure:** If at any point during observation the stock's `Long_Score` plummets below 60, it instantly fails out of the grace period early.
* **Recovery Route:** If the stock structurally repairs itself (RS >= 85, Long Score >= 85), its memory is wiped, and it is promoted back to `"LONG"` Phase 1 as a Re-Entry `^`. 

### Phase 5: Distribution vs. Eviction
When the Observation clock expires (hitting Day 22) OR the stock fast-fails (Long Score < 60), TABELA makes a definitive binary decision about the stock's future. 

**Path A: DISTRIBUTION**
* **The Test:** On the deadline execution day, the Distribution Engine takes a snapshot of the stock's macro state.
* **The Trigger:** If the stock is in a `Neutral` or `Lagging` theme, and its `RS_Rating >= 40`, it earns the `"DISTRIBUTION"` label in the registry. It will now continuously populate the Distribution Watchlist.

**Path B: PURGE / UNTRACKED**
* **The Action:** If the expiring Observation stock exhibits a `Leading` theme (too dangerous to short squeeze) or drops below 40 RS (penny-stock breakdown), it fails the distribution test. 
* **The Ghosting Protocol:** TABELA simply deletes the tracking record natively: `del registry[ticker]`. The stock vanishes entirely from the platform's daily output until it organically breaks out into Phase 1 again on a later date.

### Edge Case: Ghost Purge
* If a stock undergoes a corporate merger, de-listing, or ticker change and physically vanishes from the CSV snapshots, it is purged.

### Edge Case: Distribution Theme Safety Net
* If a stock aggressively tracked in `DISTRIBUTION` suddenly finds its macro theme turned `Leading` (but the stock itself still hasn't mathematically rallied past 85/85), TABELA instantly aborts the short track. It deletes the record natively to protect the system from unexpected ETF short-squeezes.
