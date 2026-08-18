@echo off
cd /d "%~dp0.."
python market\update_market_metrics.py
pause
