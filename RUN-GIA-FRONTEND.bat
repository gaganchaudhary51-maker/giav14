@echo off
cd /d "%~dp0frontend"
title GIA Frontend
echo GIA Frontend - keep this window open while using GIA.
call npm run dev -- --host 127.0.0.1 --configLoader runner
echo.
echo GIA Frontend stopped. If this was unexpected, read the error above.
pause
