@echo off
set PYTHONPATH=%~dp0
python runners\weekly_run.py %*
pause
