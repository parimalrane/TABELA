@echo off
echo =========================================================
echo TABELA QUARTERLY IN-MEMORY BACKTESTING ENGINE
echo =========================================================
echo.

set PYTHONPATH=C:\TABELA
cd C:\TABELA\backtesting\tuners

echo [1/2] Executing Long Quarterly Sweep...
python run_quarterly_in_memory_tuner.py

echo.
echo [2/2] Executing Short Quarterly Sweep...
python run_quarterly_in_memory_tuner_short.py

echo.
echo =========================================================
echo FULL QUARTERLY BACKTEST RUN COMPLETED
echo =========================================================
pause
