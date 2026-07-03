import io
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

from core.pipeline import run_tabela_pipeline


if __name__ == "__main__":

    buffer = io.StringIO()

    with redirect_stdout(buffer):
        run_tabela_pipeline()

    output = buffer.getvalue()

    # Print to terminal
    print(output, end="")

    # Save daily report
    report_dir = Path("market_data") / "daily_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"{datetime.today():%Y-%m-%d}.txt"
    report_file.write_text(output, encoding="utf-8")