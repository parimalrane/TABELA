@echo off
cd /d "%~dp0"
echo ==============================================
echo STARTING TABELA HISTORICAL REGRESSION
echo ==============================================
echo.

python run_historical.py

echo.
echo ==============================================
echo REGRESSION PIPELINE COMPLETE
echo ==============================================
pause
