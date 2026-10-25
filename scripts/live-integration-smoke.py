"""Opt-in smoke tests against explicitly configured integrations.

Does not send WhatsApp messages, place calls, or write Supabase data.
Provider test sends one short prompt to the configured LLM.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.agents import provider_adapter

results = []
def record(name, status, detail):
    results.append((name, status, detail))
    print(f"{status:7} {name}: {detail}")

# Real model provider: one minimal request, only when explicitly enabled.
config = provider_adapter.get_config()
problem = provider_adapter.config_problem(config)
if problem:
    record("LLM provider", "SKIP", problem)
else:
    try:
        response = provider_adapter.invoke("planner", "Reply with exactly: GIA_PROVIDER_SMOKE_OK")
        if "GIA_PROVIDER_SMOKE_OK" in response.get("output", ""):
            record("LLM provider", "PASS", f"live response received from {response.get('provider')} / {response.get('model')}")
        else:
            record("LLM provider", "WARN", "live response received but did not echo smoke token")
    except Exception as exc:
        record("LLM provider", "FAIL", f"{type(exc).__name__}: {exc}")

# Supabase: configuration presence only, to avoid writing into a real tenant table.
supa_url = os.getenv("SUPABASE_URL", "").strip()
supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
if not supa_url or not supa_key:
    record("Supabase", "SKIP", "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not configured")
else:
    try:
        import httpx
        response = httpx.get(supa_url.rstrip("/") + "/rest/v1/",
                             headers={"apikey": supa_key, "Authorization": "Bearer " + supa_key},
                             timeout=8)
        if response.status_code < 500:
            record("Supabase", "PASS", f"REST endpoint reachable (HTTP {response.status_code}); table permissions not proven")
        else:
            record("Supabase", "FAIL", f"REST endpoint HTTP {response.status_code}")
    except Exception as exc:
        record("Supabase", "FAIL", f"{type(exc).__name__}: {exc}")

# Telephony and WhatsApp: report configured status only. No calls/messages are initiated.
voip = bool(os.getenv("GIA_VOIP_WEBHOOK_SECRET") and os.getenv("GIA_VOIP_PROVIDER"))
record("VoIP webhook", "CONFIG" if voip else "SKIP",
       "provider and webhook secret present; vendor callback/audio path still needs a real vendor test" if voip else "GIA_VOIP_PROVIDER / GIA_VOIP_WEBHOOK_SECRET not configured")
whatsapp = bool(os.getenv("WHATSAPP_ACCESS_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
record("WhatsApp Business", "CONFIG" if whatsapp else "SKIP",
       "credentials present; no message sent (requires approved template, consented recipient, and explicit test approval)" if whatsapp else "WHATSAPP_ACCESS_TOKEN / WHATSAPP_PHONE_NUMBER_ID not configured")
groq = bool(os.getenv("GROQ_API_KEY"))
gemini = bool(os.getenv("GEMINI_API_KEY"))
kokoro = bool(os.getenv("KOKORO_TTS_URL"))
record("Groq STT", "CONFIG" if groq else "SKIP", "key present; audio transcription not tested" if groq else "GROQ_API_KEY not configured")
record("Gemini", "CONFIG" if gemini else "SKIP", "key present; prompt evolution call not tested" if gemini else "GEMINI_API_KEY not configured")
record("Kokoro TTS", "CONFIG" if kokoro else "SKIP", "URL present; audio synthesis not tested" if kokoro else "KOKORO_TTS_URL not configured")

failures = [r for r in results if r[1] == "FAIL"]
print("\nSummary:", json.dumps({"results": results, "failures": len(failures)}, indent=2))
raise SystemExit(1 if failures else 0)
