$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Report = Join-Path $Root ("GIA-VERIFY-" + $Stamp + ".txt")
$Results = @()

function Add-Result {
    param([string]$Name,[string]$Status,[string]$Detail = "")
    $script:Results += [PSCustomObject]@{ Check=$Name; Status=$Status; Detail=$Detail }
    Write-Host ("[" + $Status + "] " + $Name + " " + $Detail)
}

Write-Host ""
Write-Host "=== GIA UNIVERSAL AI - ONE COMMAND VERIFY ===" -ForegroundColor Cyan
Write-Host ("Project: " + $Root)

if (-not (Test-Path (Join-Path $Root "GOVERNANCE\BLUEPRINT-PATH.json"))) {
    Add-Result "Blueprint" "FAIL" "Run this script from the GIA project root."
    exit 2
}
Add-Result "Blueprint files" "PASS" "Governance path found"

$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if ($node) { Add-Result "Node.js" "PASS" (& node --version) }
else { Add-Result "Node.js" "FAIL" "Node.js not found" }

if ($npm) { Add-Result "npm" "PASS" (& npm --version) }
else { Add-Result "npm" "FAIL" "npm not found" }

if ($python) { Add-Result "Python" "PASS" (& python --version) }
else { Add-Result "Python" "FAIL" "Python not found" }

if ($npm -and (Test-Path (Join-Path $Frontend "package.json"))) {
    Write-Host ""
    Write-Host "--- Frontend npm install ---" -ForegroundColor Yellow
    Push-Location $Frontend
    & npm install --no-audit --no-fund
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -eq 0) {
        Add-Result "npm install" "PASS" "Dependencies installed"
        Write-Host ""
        Write-Host "--- Frontend production build ---" -ForegroundColor Yellow
        Push-Location $Frontend
        & npm run build
        $code = $LASTEXITCODE
        Pop-Location
        if ($code -eq 0) { Add-Result "Frontend build" "PASS" "Build completed" }
        else { Add-Result "Frontend build" "FAIL" ("exit=" + $code) }
    }
    else {
        Add-Result "npm install" "FAIL" ("exit=" + $code)
    }
}
else {
    Add-Result "Frontend package" "FAIL" "frontend/package.json missing or npm unavailable"
}

if ($python -and (Test-Path (Join-Path $Backend "requirements.txt"))) {
    Write-Host ""
    Write-Host "--- Backend tests ---" -ForegroundColor Yellow
    Push-Location $Backend
    $env:PYTHONPATH = $Backend
    & python -m pytest -q tests
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -eq 0) { Add-Result "Backend pytest" "PASS" "Tests passed" }
    else { Add-Result "Backend pytest" "FAIL" ("exit=" + $code) }
}
else {
    Add-Result "Backend tests" "FAIL" "Python/requirements/tests missing"
}

$pass = @($Results | Where-Object { $_.Status -eq "PASS" }).Count
$fail = @($Results | Where-Object { $_.Status -eq "FAIL" }).Count

Write-Host ""
Write-Host "=== FINAL GATE ===" -ForegroundColor Cyan
$Results | Format-Table -AutoSize
Write-Host ("PASS=" + $pass + " FAIL=" + $fail)
$Results | Out-String | Set-Content -Path $Report
Write-Host ("Report: " + $Report)

if ($fail -gt 0) {
    Write-Host ""
    Write-Host "GIA VERIFY: FAIL - fix failures before release." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "GIA VERIFY: PASS - automated gates passed." -ForegroundColor Green
exit 0
