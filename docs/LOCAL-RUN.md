# Local run

## Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export GIA_AUTH_SECRET="replace-with-long-random"
uvicorn app.main:app --reload --port 8000
```

## Tests
```bash
cd backend
pytest -q
```

## Frontend
```bash
cd frontend
npm install
npm run dev
```
Open on phone via laptop LAN IP, not only localhost, if testing iPhone Safari.

## Verify script (Windows)
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\GIA-VERIFY.ps1
```
