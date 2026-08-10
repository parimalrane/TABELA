import sys, traceback, json, io
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr

out = []

try:
    from core.runtime_context import context
    out.append(f"market_date: {context.market_date}")
    out.append(f"market_file: {context.market_file}")
    out.append(f"market_file exists: {context.market_file.exists()}")

    from engines.market_context_engine import run_market_context_engine
    result = run_market_context_engine(context.market_date)
    out.append("run_market_context_engine: SUCCESS")
    out.append(json.dumps(result, indent=2)[:800])

except Exception as e:
    out.append(f"ERROR: {e}")
    out.append(traceback.format_exc())

Path("c:/TABELA/verify_result.txt").write_text("\n".join(out), encoding="utf-8")
