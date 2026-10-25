$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$Report = Join-Path $Root ("GIA-VERIFY-" + $Stamp + ".txt")
$TestRoot = Join-Path $Root (".test-tmp\" + $Stamp)
$Results = @()

function Add-Result {
    param([string]$Name,[string]$Status,[string]$Detail = "")
    $script:Results += [PSCustomObject]@{ Check=$Name; Status=$Status; Detail=$Detail }
    Write-Host ("[" + $Status + "] " + $Name + " " + $Detail)
}

Write-Host ""
Write-Host "=== GIA UNIVERSAL AI - RELEASE CHECK ===" -ForegroundColor Cyan
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

# Isolate test writes on Windows instead of relying on POSIX /tmp defaults or
# the user's live GIA database/workspace. Keep any configured sandbox root out
# of the default TemporaryDirectory sandbox test, then restore it afterwards.
New-Item -ItemType Directory -Force -Path $TestRoot | Out-Null
$PreviousDataDir = $env:GIA_DATA_DIR
$PreviousAuditLog = $env:GIA_AUDIT_LOG
$PreviousWorkspaceRoot = $env:GIA_WORKSPACE_ROOT
$PreviousSandboxRoot = $env:GIA_SANDBOX_ROOT
$env:GIA_DATA_DIR = Join-Path $TestRoot "data"
$env:GIA_AUDIT_LOG = Join-Path $TestRoot "audit.jsonl"
$env:GIA_WORKSPACE_ROOT = Join-Path $TestRoot "workspace"
Remove-Item Env:GIA_SANDBOX_ROOT -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $env:GIA_DATA_DIR,$env:GIA_WORKSPACE_ROOT | Out-Null

if ($npm -and (Test-Path (Join-Path $Frontend "package-lock.json"))) {
    Write-Host ""
    Write-Host "--- Reproducible frontend dependency install ---" -ForegroundColor Yellow
    Push-Location $Frontend
    & npm ci --no-audit --no-fund
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -eq 0) {
        Add-Result "Frontend dependencies" "PASS" "npm ci completed"
        Write-Host ""
        Write-Host "--- Frontend production build ---" -ForegroundColor Yellow
        Push-Location $Frontend
        & npm run build
        $code = $LASTEXITCODE
        Pop-Location
        if ($code -eq 0) { Add-Result "Frontend build" "PASS" "Production bundle created" }
        else { Add-Result "Frontend build" "FAIL" ("exit=" + $code) }
    }
    else {
        Add-Result "Frontend dependencies" "FAIL" ("npm ci exit=" + $code)
    }
}
else {
    Add-Result "Frontend package" "FAIL" "frontend/package-lock.json missing or npm unavailable"
}

if ($python -and (Test-Path (Join-Path $Backend "requirements.txt"))) {
    Write-Host ""
    Write-Host "--- Backend syntax check ---" -ForegroundColor Yellow
    Push-Location $Backend
    $env:PYTHONPATH = $Backend
    & python -m compileall -q app tests
    $code = $LASTEXITCODE
    if ($code -eq 0) { Add-Result "Backend syntax" "PASS" "compileall completed" }
    else { Add-Result "Backend syntax" "FAIL" ("exit=" + $code) }

    Write-Host ""
    Write-Host "--- Backend tests ---" -ForegroundColor Yellow
    & python -m pytest -q tests --basetemp (Join-Path $TestRoot "pytest")
    $code = $LASTEXITCODE
    Pop-Location
    if ($code -eq 0) { Add-Result "Backend pytest" "PASS" "All tests passed" }
    else { Add-Result "Backend pytest" "FAIL" ("exit=" + $code) }
}
else {
    Add-Result "Backend tests" "FAIL" "Python/requirements/tests missing"
}

$pass = @($Results | Where-Object { $_.Status -eq "PASS" }).Count
$fail = @($Results | Where-Object { $_.Status -eq "FAIL" }).Count

Write-Host ""
Write-Host "=== AUTOMATED CHECKS ===" -ForegroundColor Cyan
$Results | Format-Table -AutoSize
Write-Host ("PASS=" + $pass + " FAIL=" + $fail)
$Results | Out-String | Set-Content -Path $Report
Write-Host ("Report: " + $Report)

if ($null -eq $PreviousDataDir) { Remove-Item Env:GIA_DATA_DIR -ErrorAction SilentlyContinue } else { $env:GIA_DATA_DIR = $PreviousDataDir }
if ($null -eq $PreviousAuditLog) { Remove-Item Env:GIA_AUDIT_LOG -ErrorAction SilentlyContinue } else { $env:GIA_AUDIT_LOG = $PreviousAuditLog }
if ($null -eq $PreviousWorkspaceRoot) { Remove-Item Env:GIA_WORKSPACE_ROOT -ErrorAction SilentlyContinue } else { $env:GIA_WORKSPACE_ROOT = $PreviousWorkspaceRoot }
if ($null -eq $PreviousSandboxRoot) { Remove-Item Env:GIA_SANDBOX_ROOT -ErrorAction SilentlyContinue } else { $env:GIA_SANDBOX_ROOT = $PreviousSandboxRoot }

if ($fail -gt 0) {
    Write-Host ""
    Write-Host "GIA CHECK: FAIL - resolve failures before release." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "GIA CHECK: PASS - automated checks passed. Live integrations, backup/restore and production deployment still require separate acceptance checks." -ForegroundColor Green
exit 0
