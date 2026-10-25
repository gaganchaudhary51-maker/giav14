"""Repeatable local release checks. Run with Python from the project root."""
from __future__ import annotations
import os, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VOICE_SLICE = ROOT / "hrgen_universal_monorepo"

# Never let release tests touch the candidate's persistent user/project DB.
# The child pytest processes inherit this isolated location; TemporaryDirectory
# removes the test database when this verification process exits.
_original_data_dir = os.environ.get("GIA_DATA_DIR")
_audit_data_dir = tempfile.TemporaryDirectory(prefix="gia-release-data-")
os.environ["GIA_DATA_DIR"] = _audit_data_dir.name

def run(label, command, cwd, timeout=180):
    print(f"\n== {label} ==")
    print("$", " ".join(map(str, command)))
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        print(f"BLOCKED: {type(exc).__name__}: {exc}")
        return False
    print((result.stdout + result.stderr)[-6000:])
    print("PASS" if result.returncode == 0 else f"FAIL (exit {result.returncode})")
    return result.returncode == 0

ok = True
ok &= run("Backend regression tests", [sys.executable, "-m", "pytest", "-q"], ROOT, 180)
ok &= run("Backend Python syntax compilation", [sys.executable, "-m", "compileall", "-q", "backend/app"], ROOT, 60)
ok &= run("HRGEN voice integration tests", [sys.executable, "-m", "pytest", "-q"], VOICE_SLICE, 120)
ok &= run("HRGEN voice Python syntax compilation", [sys.executable, "-m", "compileall", "-q", "backend"], VOICE_SLICE, 60)
npm = "npm.cmd" if os.name == "nt" else "npm"
if (FRONTEND / "node_modules" / ".bin" / ("tsc.cmd" if os.name == "nt" else "tsc")).exists():
    ok &= run("Frontend production build", [npm, "run", "build"], FRONTEND, 180)
else:
    print("\n== Frontend production build ==\nBLOCKED: frontend dependencies are not installed. Run `npm ci` in frontend, then `npm run build`.")
    ok = False

if _original_data_dir is None:
    os.environ.pop("GIA_DATA_DIR", None)
else:
    os.environ["GIA_DATA_DIR"] = _original_data_dir

print("\nRELEASE CHECK:", "PASS" if ok else "INCOMPLETE — see blocked/failed checks above")
raise SystemExit(0 if ok else 2)
