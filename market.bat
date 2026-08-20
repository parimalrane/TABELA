@echo off
set PYTHONPATH=%~dp0
python runners\update_market_metrics.py %*
pause
