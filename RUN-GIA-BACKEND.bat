@echo off
cd /d "%~dp0backend"
title GIA Backend
echo GIA Backend - keep this window open while using GIA.
"..\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
echo.
echo GIA Backend stopped. If this was unexpected, read the error above.
pause
