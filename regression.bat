@echo off
set PYTHONPATH=%~dp0
python runners\run_historical.py %*
pause
