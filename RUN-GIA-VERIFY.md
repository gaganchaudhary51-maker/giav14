# GIA One-Command Verification

## Where to put/run it

Keep `GIA-VERIFY.ps1` in the **same root folder** that contains:

- `backend`
- `frontend`
- `GOVERNANCE`

Example:

GIA-MASTER-BUILD-v14.0/
├── GIA-VERIFY.ps1
├── backend/
├── frontend/
└── GOVERNANCE/

## First run

Open **PowerShell** in this exact project root folder and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\GIA-VERIFY.ps1
```

Or right-click the folder → Open in Terminal, then use the commands above.

## What it checks

1. Blueprint/governance presence
2. Node.js
3. npm
4. Python
5. `npm install`
6. React/Vite frontend production build
7. Backend pytest suite
8. Production npm audit
9. Final PASS/FAIL/WARN gate

A timestamped `GIA-VERIFY-YYYYMMDD-HHMMSS.txt` report is created in the project root.

**Important:** PASS means the automated checks passed on that PC. It does not by itself prove external provider credentials, production deployment, MongoDB production connectivity, or every browser/device combination. Those require their corresponding live acceptance tests.
