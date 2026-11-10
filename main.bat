@echo off
setlocal

if /i "%~1"=="-o" goto sync
goto run

:sync
echo Syncing with GitHub (overwriting local changes if any)...
git fetch origin
git reset --hard origin/master

:run
python runners\main.py
pause
