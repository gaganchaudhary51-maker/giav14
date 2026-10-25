@echo off
setlocal
cd /d "%~dp0"
title GIA Universal AI - Startup
echo.
echo =====================================================
echo   GIA UNIVERSAL AI - EASY START
echo =====================================================
echo.
if not exist "GOVERNANCE\BLUEPRINT-PATH.json" (
  echo ERROR: This does not look like the GIA project folder.
  echo Please keep START-GIA.bat beside the backend and frontend folders.
  pause
  exit /b 2
)
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found. Install Python 3.11 or newer, then try again.
  echo During installation, enable the option to add Python to PATH.
  pause
  exit /b 2
)
where node >nul 2>nul
if errorlevel 1 (
  echo ERROR: Node.js was not found. Install the current LTS version, then try again.
  pause
  exit /b 2
)
where npm >nul 2>nul
if errorlevel 1 (
  echo ERROR: npm was not found. Repair or reinstall Node.js, then try again.
  pause
  exit /b 2
)
echo [1/5] Checking Python environment...
if not exist "backend\.venv\Scripts\python.exe" (
  python -m venv "backend\.venv"
  if errorlevel 1 (
    echo ERROR: Could not create the backend Python environment.
    pause
    exit /b 1
  )
)
echo [2/5] Checking backend packages...
"backend\.venv\Scripts\python.exe" "scripts\check-dependencies.py"
if errorlevel 1 (
  echo Installing backend packages. Internet access is required for first-time setup...
  "backend\.venv\Scripts\python.exe" -m pip install --upgrade pip
  if errorlevel 1 (
    echo ERROR: Could not prepare pip. Check your internet connection.
    pause
    exit /b 1
  )
  "backend\.venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
  if errorlevel 1 (
    echo ERROR: Backend package installation failed. No app windows were started.
    pause
    exit /b 1
  )
)
"backend\.venv\Scripts\python.exe" "scripts\check-dependencies.py"
if errorlevel 1 (
  echo ERROR: Backend dependencies are still incomplete or incompatible.
  pause
  exit /b 1
)
echo [3/5] Checking frontend packages...
if not exist "frontend\node_modules\vite\bin\vite.js" (
  echo Installing frontend packages from the locked package list. Internet access is required...
  pushd "frontend"
  call npm ci --no-audit --no-fund
  if errorlevel 1 (
    popd
    echo ERROR: Frontend package installation failed. Check internet access and retry.
    pause
    exit /b 1
  )
  popd
)
echo [4/5] Starting backend and frontend on this PC only...
start "GIA Backend" "%~dp0RUN-GIA-BACKEND.bat"
start "GIA Frontend" "%~dp0RUN-GIA-FRONTEND.bat"
echo [5/5] Waiting for the backend health check...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 40;$i++){try{$r=Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 2;if($r.status -eq 'healthy'){$ok=$true;break}}catch{};Start-Sleep -Seconds 1};if($ok){Write-Host 'Backend health: PASS' -ForegroundColor Green;exit 0}else{Write-Host 'Backend health: NOT READY. Check the GIA Backend window.' -ForegroundColor Red;exit 1}"
if errorlevel 1 (
  echo.
  echo GIA did not confirm backend readiness. Check the GIA Backend window for errors.
  echo The frontend window may still be starting; no browser was opened automatically.
  pause
  exit /b 1
)
echo.
echo Opening GIA in your browser...
start "" "http://127.0.0.1:5173/"
echo.
echo GIA startup request complete. Keep both GIA windows open while using the app.
echo Close the two GIA windows when you want to stop the local services.
echo This startup script does not publish GIA to the internet.
echo.
pause
