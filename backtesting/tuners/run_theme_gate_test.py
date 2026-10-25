"""
THEME GATE TEST (read-only)
===========================
Replays the saved daily stock history (market_data/stock_universe/*_stock_history.json)
and compares two theme-gate settings for each side:

  CURRENT : theme lists exactly as defined in config.py
  STRICT  : Long  -> Leading + Unclassified Leader   (mild: block Lagging)
            Short -> Lagging only                     (mild: block Leading + Unclassified Leader)

Uses the LIVE theme_class stored for each stock on each day (not a proxy).
All other gates are read from config.py. This script NEVER writes to config.py.

Win rate / average return are measured two ways:
  TO-DATE : entry close -> last date in the data (same metric the other tuners use)
  FWD-10D : entry close -> close 10 trading days later (only entries with 10 days of future data)

Decision rule (agreed with the user), evaluated per side on TO-DATE, Strong + Mild combined:
  PASS if  strict_WR >= current_WR - 1.0   AND   strict_trades >= 0.5 * current_trades
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("c:/TABELA")
sys.path.append(str(BASE_DIR))

from config.config import (  # noqa: E402  (read-only import)
    LONG_ENTRY,
    SHORT_ENTRY,
    MILD_LONG_ENTRY,
    MILD_SHORT_ENTRY,
)

HISTORY_DIR = BASE_DIR / "market_data" / "stock_universe"
RESULTS_DIR = BASE_DIR / "backtesting" / "results"
FWD_DAYS = 10


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
def load_history():
    """Returns (dates, rows_by_date) where rows_by_date[date][ticker] = record."""
    rows_by_date = {}
    for fp in sorted(HISTORY_DIR.rglob("*_stock_history.json")):
        date = fp.name.replace("_stock_history.json", "")
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        day = {}
        for rec in data:
            t = str(rec.get("ticker", "")).replace("*", "").strip().upper()
            if t:
                day[t] = rec
        if day:
            rows_by_date[date] = day
    dates = sorted(rows_by_date.keys())
    return dates, rows_by_date


def num(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


# ----------------------------------------------------------------------------
# Criteria (mirror of lifecycle/stock_transition_engine._meets_criteria)
# ----------------------------------------------------------------------------
def liquid(rec, crit):
    if num(rec.get("last_close")) < crit.get("MIN_PRICE", 0.0):
        return False
    if num(rec.get("avg_volume")) < crit.get("MIN_VOLUME", 0):
        return False
    return True


def zacks_ok(rec, crit):
    z = int(num(rec.get("zacks_rank")))
    if "BLOCKED_ZACKS" in crit and z in crit["BLOCKED_ZACKS"]:
        return False
    if "ALLOWED_ZACKS" in crit and z not in crit["ALLOWED_ZACKS"]:
        return False
    return True


def long_strong(rec, themes):
    c = LONG_ENTRY
    return (
        rec.get("theme_class") in themes
        and num(rec.get("rs_rating")) >= c["MIN_RS"]
        and num(rec.get("long_score")) >= c["MIN_LONG_SCORE"]
        and zacks_ok(rec, c)
        and liquid(rec, c)
    )


def long_mild(rec, blocked):
    c = MILD_LONG_ENTRY
    return (
        rec.get("theme_class") not in blocked
        and num(rec.get("rs_rating")) >= c["MIN_RS"]
        and num(rec.get("long_score")) >= c["MIN_LONG_SCORE"]
        and zacks_ok(rec, c)
        and liquid(rec, c)
    )


def short_strong(rec, themes):
    c = SHORT_ENTRY
    sr = num(rec.get("short_rs_rating"))
    return (
        rec.get("theme_class") in themes
        and c["MIN_SHORT_RS"] <= sr <= c["MAX_SHORT_RS"]
        and num(rec.get("short_score")) <= c["MAX_SHORT_SCORE"]
        and zacks_ok(rec, c)
        and liquid(rec, c)
    )


def short_mild(rec, blocked):
    c = MILD_SHORT_ENTRY
    return (
        rec.get("theme_class") not in blocked
        and num(rec.get("short_rs_rating")) <= c["MAX_SHORT_RS"]
        and num(rec.get("short_score")) <= c["MAX_SHORT_SCORE"]
        and zacks_ok(rec, c)
        and liquid(rec, c)
    )


# ----------------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------------
def simulate(dates, rows_by_date, is_strong, is_mild, mild_days):
    """
    One Strong entry per ticker (first day it qualifies).
    After it stops qualifying, a drop clock runs; if it meets the mild criteria
    within mild_days it gets one Mild entry. Re-qualifying as Strong resets the clock.
    Returns a list of entry dicts.
    """
    entries = []
    state = {}  # ticker -> {"strong": bool, "mild": bool, "drop_start": idx or None}

    for i, date in enumerate(dates):
        day = rows_by_date[date]
        for t, rec in day.items():
            price = num(rec.get("last_close"))
            if price <= 0:
                continue
            st = state.setdefault(t, {"strong": False, "mild": False, "drop_start": None})

            if is_strong(rec):
                st["drop_start"] = None
                if not st["strong"]:
                    st["strong"] = True
                    entries.append(
                        {"ticker": t, "bucket": "Strong", "idx": i, "date": date,
                         "price": price, "theme_class": rec.get("theme_class")}
                    )
            elif st["strong"]:
                if st["drop_start"] is None:
                    st["drop_start"] = i
                days = i - st["drop_start"] + 1
                if days > mild_days:
                    continue
                if not st["mild"] and is_mild(rec):
                    st["mild"] = True
                    entries.append(
                        {"ticker": t, "bucket": "Mild", "idx": i, "date": date,
                         "price": price, "theme_class": rec.get("theme_class")}
                    )
    return entries


def returns(entries, dates, rows_by_date, side):
    """Attach TO-DATE and FWD-10D returns (percent). Short side inverts sign."""
    last = rows_by_date[dates[-1]]
    sign = 1.0 if side == "long" else -1.0
    for e in entries:
        t, p0 = e["ticker"], e["price"]
        p_last = num(last.get(t, {}).get("last_close"))
        e["ret_todate"] = sign * (p_last - p0) / p0 * 100.0 if p_last > 0 else None
        j = e["idx"] + FWD_DAYS
        if j < len(dates):
            p_f = num(rows_by_date[dates[j]].get(t, {}).get("last_close"))
            e["ret_fwd"] = sign * (p_f - p0) / p0 * 100.0 if p_f > 0 else None
        else:
            e["ret_fwd"] = None
    return entries


def summarize(entries, key):
    vals = [e[key] for e in entries if e.get(key) is not None]
    if not vals:
        return {"n": 0, "wr": 0.0, "avg": 0.0}
    return {
        "n": len(vals),
        "wr": sum(1 for v in vals if v > 0) / len(vals) * 100.0,
        "avg": sum(vals) / len(vals),
    }


def fmt(s):
    return f"{s['n']:>5} trades  WR {s['wr']:>5.1f}%  Avg {s['avg']:>6.2f}%"


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def run_side(side, dates, rows_by_date):
    if side == "long":
        cur_themes = LONG_ENTRY["THEMES"]
        cur_blocked = MILD_LONG_ENTRY.get("BLOCKED_THEMES", [])
        strict_themes = ["Leading", "Unclassified Leader"]
        strict_blocked = ["Lagging"]
        mild_days = int(LONG_ENTRY.get("MILD_DAYS", 21))
        strong_fn, mild_fn = long_strong, long_mild
    else:
        cur_themes = SHORT_ENTRY["THEMES"]
        cur_blocked = MILD_SHORT_ENTRY.get("BLOCKED_THEMES", [])
        strict_themes = ["Lagging"]
        strict_blocked = ["Leading", "Unclassified Leader"]
        mild_days = int(SHORT_ENTRY.get("MILD_DAYS", 21))
        strong_fn, mild_fn = short_strong, short_mild

    variants = {
        "CURRENT": (cur_themes, cur_blocked),
        "STRICT": (strict_themes, strict_blocked),
    }
    if side == "short":
        # Extra read-only check: keep Neutral, drop Unknown (the theme-less bucket)
        variants["MIDDLE"] = (["Lagging", "Neutral"], strict_blocked)

    out = {}
    for name, (themes, blocked) in variants.items():
        entries = simulate(
            dates, rows_by_date,
            lambda r, th=themes: strong_fn(r, th),
            lambda r, bl=blocked: mild_fn(r, bl),
            mild_days,
        )
        out[name] = returns(entries, dates, rows_by_date, side)
    return out, (cur_themes, cur_blocked, strict_themes, strict_blocked)


def main():
    dates, rows_by_date = load_history()
    if len(dates) < 2:
        print("Not enough history found in market_data/stock_universe.")
        return
    print(f"History: {len(dates)} trading days, {dates[0]} -> {dates[-1]}")
    print(f"Forward window: {FWD_DAYS} trading days\n")

    csv_rows = []
    verdicts = {}

    for side in ("long", "short"):
        result, (ct, cb, st, sb) = run_side(side, dates, rows_by_date)
        print("=" * 78)
        print(f"{side.upper()} SIDE")
        print(f"  CURRENT themes={ct}  mild_blocked={cb}")
        print(f"  STRICT  themes={st}  mild_blocked={sb}")
        print("=" * 78)

        for name in [n for n in ("CURRENT", "STRICT", "MIDDLE") if n in result]:
            ents = result[name]
            for bucket in ("Strong", "Mild", "ALL"):
                sub = ents if bucket == "ALL" else [e for e in ents if e["bucket"] == bucket]
                td, fw = summarize(sub, "ret_todate"), summarize(sub, "ret_fwd")
                print(f"  {name:<8} {bucket:<7} TO-DATE: {fmt(td)}   |  FWD-10D: {fmt(fw)}")
                csv_rows.append({
                    "side": side, "variant": name, "bucket": bucket,
                    "todate_n": td["n"], "todate_wr": round(td["wr"], 2), "todate_avg": round(td["avg"], 3),
                    "fwd_n": fw["n"], "fwd_wr": round(fw["wr"], 2), "fwd_avg": round(fw["avg"], 3),
                })
            print()

        # Breakdown of CURRENT trades by theme class (shows what the extra classes contribute)
        print("  CURRENT trades by theme class (TO-DATE | FWD-10D):")
        classes = sorted({e["theme_class"] for e in result["CURRENT"]}, key=str)
        for cls in classes:
            sub = [e for e in result["CURRENT"] if e["theme_class"] == cls]
            td, fw = summarize(sub, "ret_todate"), summarize(sub, "ret_fwd")
            print(f"    {str(cls):<22} {fmt(td)}   |  {fmt(fw)}")
            csv_rows.append({
                "side": side, "variant": "CURRENT_BY_CLASS", "bucket": str(cls),
                "todate_n": td["n"], "todate_wr": round(td["wr"], 2), "todate_avg": round(td["avg"], 3),
                "fwd_n": fw["n"], "fwd_wr": round(fw["wr"], 2), "fwd_avg": round(fw["avg"], 3),
            })

        cur_all = summarize(result["CURRENT"], "ret_todate")
        str_all = summarize(result["STRICT"], "ret_todate")
        wr_ok = str_all["wr"] >= cur_all["wr"] - 1.0
        n_ok = str_all["n"] >= 0.5 * cur_all["n"]
        verdict = "PASS" if (wr_ok and n_ok) else "FAIL"
        verdicts[side] = verdict
        if "MIDDLE" in result:
            mid_all = summarize(result["MIDDLE"], "ret_todate")
            mid_ok = mid_all["wr"] >= cur_all["wr"] - 1.0 and mid_all["n"] >= 0.5 * cur_all["n"]
            print(f"  (extra) MIDDLE {side}: WR {mid_all['wr']:.1f}% vs {cur_all['wr']:.1f}%, trades {mid_all['n']} vs {cur_all['n']} -> {'PASS' if mid_ok else 'FAIL'}")
        print()
        print(f"  DECISION RULE ({side}): WR {str_all['wr']:.1f}% vs {cur_all['wr']:.1f}% (need >= current-1.0) -> {'ok' if wr_ok else 'NO'}")
        print(f"                       trades {str_all['n']} vs {cur_all['n']} (need >= 50%) -> {'ok' if n_ok else 'NO'}")
        print(f"  VERDICT {side.upper()}: {verdict}\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULTS_DIR / f"theme_gate_test_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)
    print(f"Saved: {out_csv}")
    print(f"FINAL VERDICTS: {verdicts}")


if __name__ == "__main__":
    main()
