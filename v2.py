import sys, traceback
from pathlib import Path

result_path = Path("c:/TABELA/r.txt")
try:
    result_path.write_text("step1: script started\n", encoding="utf-8")

    from core.runtime_context import context
    result_path.write_text(
        f"step2: context loaded\nmarket_date={context.market_date}\nmarket_file={context.market_file}\nexists={context.market_file.exists()}\n",
        encoding="utf-8"
    )

except Exception as e:
    result_path.write_text(f"ERROR:\n{traceback.format_exc()}\n", encoding="utf-8")
