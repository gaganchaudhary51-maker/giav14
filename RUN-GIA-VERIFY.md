# GIA Release Verification

Keep `GIA-VERIFY.ps1` in the GIA project root beside `backend`, `frontend`, and `GOVERNANCE`.

The script uses the already-installed frontend lockfile dependencies, builds the production frontend, runs Python syntax checks, and runs the complete GIA and HRGen voice pytest suites. It writes a timestamped report into the project root.

Prepare one Python environment for both backend slices before running the release check:

```powershell
python -m pip install -r requirements-test.txt
```

That file includes both backend requirement sets and the async pytest plugin used by the tests. Install the frontend dependencies from its lockfile once with `npm ci` in `frontend`. The release script points test subprocesses at a temporary SQLite directory and removes that test data on exit so they do not pollute the candidate's account database.

A passing script means the local automated checks passed on that computer. It does **not** certify that a live Hermes bridge, external model provider, production deployment, or backup/restore setup is working. Those are separate acceptance checks.

On Windows, open PowerShell in the project root and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\GIA-VERIFY.ps1
```

If network access is unavailable, `npm ci` may fail because packages cannot be downloaded; that is a dependency-install failure, not proof of a frontend source defect.
