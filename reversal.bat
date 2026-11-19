@echo off
set PYTHONPATH=%~dp0
python runners\run_reversal_scan.py %*
pause
