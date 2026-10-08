@echo off
echo =========================================================
echo TABELA BACKTESTING HOUSEKEEPING SCRIPT
echo =========================================================
echo.
echo Deleting obsolete directories...
rmdir /S /Q "C:\TABELA\backtesting\results"
rmdir /S /Q "C:\TABELA\backtesting\attribution"
rmdir /S /Q "C:\TABELA\backtesting\tuners\archived_experiments"

echo.
echo Deleting root legacy engine files...
del /F /Q "C:\TABELA\backtesting\backtest_engine.py" 2>nul
del /F /Q "C:\TABELA\backtesting\vectorized_backtest.py" 2>nul
del /F /Q "C:\TABELA\backtesting\clean.py" 2>nul
del /F /Q "C:\TABELA\backtesting\force_purge.bat" 2>nul
del /F /Q "C:\TABELA\backtesting\purge_status.txt" 2>nul

echo.
echo Deleting obsolete tuners and test scripts...
cd /d "C:\TABELA\backtesting\tuners"
del /F /Q "debug_load.txt" 2>nul
del /F /Q "phase1_short_test_output.csv" 2>nul
del /F /Q "phase1_test_output.csv" 2>nul
del /F /Q "rewrite_engine.py" 2>nul
del /F /Q "run.bat" 2>nul
del /F /Q "run_cartesian_long.py" 2>nul
del /F /Q "run_cartesian_short.py" 2>nul
del /F /Q "run_quarterly_tuner.py" 2>nul
del /F /Q "run_tuner.py" 2>nul
del /F /Q "run_tuner_short_v2.py" 2>nul
del /F /Q "run_vectorized_garage_tuner.py" 2>nul
del /F /Q "run_vectorized_short_tuner.py" 2>nul
del /F /Q "run_vectorized_tuner.py" 2>nul
del /F /Q "test_run.py" 2>nul

echo.
echo =========================================================
echo CLEANUP COMPLETE. 
echo Only the production Quarterly Engine files remain.
echo =========================================================
pause
