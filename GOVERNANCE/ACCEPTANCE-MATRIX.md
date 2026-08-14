# GIA UNIVERSAL AI — ACCEPTANCE MATRIX
## V14 LOCKED

| ID | Gate | Required evidence | Status |
|---|---|---|---|
| A01 | Blueprint integrity | Canonical governance documents and metadata align | PASS |
| A02 | Architecture | Required core paths exist | PASS |
| A03 | Backend regression | Backend automated suite passes | PASS |
| A04 | Python syntax | Backend parses | PASS |
| A05 | Auth/security | Auth/security foundation and tests | PASS |
| A06 | Project isolation | Ownership boundaries enforced | PASS |
| A07 | Real builder | CRUD generation writes real files | PASS |
| A08 | Verification | VERIFIED requires evidence | PASS |
| A09 | Audit | Sensitive transitions audited | PASS |
| A10 | Approval | High-risk operations gated | PASS |
| A11 | Checkpoint/rollback | Recovery architecture exists | PASS |
| A12 | Agent orchestration | Registry + task graph/commander | PASS |
| A13 | Model routing | Router/escalation architecture | PASS |
| A14 | Memory/RAG | Project-scoped architecture | PASS |
| A15 | Voice | STT/TTS/session routing source | PASS |
| A16 | Responsive UI | Mobile-responsive source | PASS |
| A17 | Fresh npm install | Run on network-enabled PC | PENDING |
| A18 | Fresh frontend build | npm run build after install | PENDING |
| A19 | Live smoke test | Login → project → GIA → builder → verification | PENDING |
| A20 | Overall release | All mandatory gates evidenced | PENDING |

PENDING gates must never be relabeled PASS without actual evidence.

Local verifier:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\GIA-VERIFY.ps1
```
