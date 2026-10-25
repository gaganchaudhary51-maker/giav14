param([switch]$SkipDependencyInstall)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

$python = (Get-Command python -ErrorAction Stop).Source
$venv = Join-Path $root ".desktop-build-venv"
$buildDir = Join-Path $root ".desktop-build"
$backendDist = Join-Path $root "backend\dist"

if (-not (Test-Path (Join-Path $venv "Scripts\python.exe"))) {
  & $python -m venv $venv
  if ($LASTEXITCODE -ne 0) { throw "Could not create isolated desktop build environment." }
}
$buildPython = Join-Path $venv "Scripts\python.exe"
if (-not $SkipDependencyInstall) {
  & $buildPython -m pip install -r backend\requirements.txt -r backend\requirements-desktop-build.txt
  if ($LASTEXITCODE -ne 0) { throw "Backend and desktop build dependencies could not be installed." }
  npm ci --prefix frontend --cache .npm-cache --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw "Frontend dependencies could not be installed." }
  npm ci --prefix frontend\electron --cache .npm-cache --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw "Desktop shell dependencies could not be installed." }
}

npm run build --prefix frontend
if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
npm test --prefix frontend\electron
if ($LASTEXITCODE -ne 0) { throw "Desktop provider settings checks failed." }

New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
New-Item -ItemType Directory -Path $backendDist -Force | Out-Null
& $buildPython -m PyInstaller --clean --noconfirm --onefile --noconsole --name gia-backend `
  --paths backend --distpath $backendDist --workpath (Join-Path $buildDir "pyinstaller") `
  --specpath $buildDir backend\desktop_entry.py
if ($LASTEXITCODE -ne 0) { throw "Bundled GIA backend build failed." }

npm run dist:win --prefix frontend\electron
if ($LASTEXITCODE -ne 0) { throw "Windows NSIS installer build failed." }

$installer = Get-ChildItem -LiteralPath (Join-Path $root "release\windows") -Filter "GIA-Setup-*.exe" -File |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $installer) { throw "Installer was not created." }
Write-Output "Desktop installer ready: $($installer.FullName)"
Write-Output "The setup installs per-user and keeps local data under %APPDATA%\GIA Universal AI."
