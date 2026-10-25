"""SIM-less telephony/webhook scaffolding and WhatsApp template rendering.
Provider-specific production callbacks require a DID/SIP vendor configuration and HMAC secret.
"""
from __future__ import annotations
import hashlib, hmac, json, os
from typing import Any
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field
from app.auth.security import verify_token

router=APIRouter(prefix="/telephony",tags=["telephony"])

def _auth(header: str | None) -> str:
    if not header or not header.startswith("Bearer ") or not verify_token(header[7:]):
        raise HTTPException(401,"Authentication required")
    return verify_token(header[7:]) or ""

def _verify_webhook(raw: bytes, signature: str | None):
    secret=os.getenv("GIA_VOIP_WEBHOOK_SECRET","")
    if not secret:
        raise HTTPException(503,"VoIP webhook is disabled until GIA_VOIP_WEBHOOK_SECRET is configured.")
    supplied=(signature or "").removeprefix("sha256=")
    expected=hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    if not supplied or not hmac.compare_digest(expected,supplied):
        raise HTTPException(401,"Invalid webhook signature")

@router.get("/providers")
def provider_status(authorization: str | None = Header(default=None)):
    _auth(authorization)
    return {
      "telephony_mode":"virtual-voip-webhook",
      "incoming_webhook_configured":bool(os.getenv("GIA_VOIP_WEBHOOK_SECRET") and os.getenv("GIA_VOIP_PROVIDER")),
      "provider":os.getenv("GIA_VOIP_PROVIDER") or None,
      "groq_stt_configured":bool(os.getenv("GROQ_API_KEY")),
      "gemini_configured":bool(os.getenv("GEMINI_API_KEY")),
      "kokoro_tts_configured":bool(os.getenv("KOKORO_TTS_URL")),
      "whatsapp_configured":bool(os.getenv("WHATSAPP_ACCESS_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID")),
      "estimated_cost_per_minute_inr":None,
      "note":"No provider is considered live until credentials, vendor callbacks, audio flow, and billing are verified. Costs are not guaranteed."
    }

@router.post("/webhooks/voip/incoming")
async def incoming_voip(request: Request, x_gia_webhook_signature: str | None = Header(default=None)):
    raw=await request.body()
    _verify_webhook(raw,x_gia_webhook_signature)
    try: payload=json.loads(raw or b"{}")
    except json.JSONDecodeError: raise HTTPException(400,"Webhook body must be JSON")
    call_id=str(payload.get("call_id") or payload.get("CallSid") or "")
    if not call_id: raise HTTPException(422,"Missing call_id")
    # Acknowledges an authenticated event only. Vendor-specific call control is an adapter task.
    return {"accepted":True,"call_id":call_id,"state":"RECEIVED","next_step":"provider_adapter_required",
            "message":"Webhook signature verified; no call was answered or recorded by this endpoint."}

@router.post("/webhooks/voip/transcript")
async def transcript_event(request: Request, x_gia_webhook_signature: str | None = Header(default=None)):
    raw=await request.body()
    _verify_webhook(raw,x_gia_webhook_signature)
    try: payload=json.loads(raw or b"{}")
    except json.JSONDecodeError: raise HTTPException(400,"Webhook body must be JSON")
    if not payload.get("call_id") or not payload.get("text"):
        raise HTTPException(422,"call_id and text are required")
    # Explicitly avoid silently appending this to personal memory or RAG.
    return {"accepted":True,"call_id":str(payload["call_id"]),"transcript_received":True,
            "persisted":False,"reason":"Configure a tenant-scoped call-session store before production use."}

class WhatsAppTemplate(BaseModel):
    template: str = Field(min_length=1,max_length=4000)
    variables: dict[str,str] = Field(default_factory=dict)
    allowed_variables: list[str] = Field(default_factory=list,max_length=50)

@router.post("/whatsapp/template/render")
def render_whatsapp_template(payload: WhatsAppTemplate, authorization: str | None = Header(default=None)):
    _auth(authorization)
    # Only named, explicitly allowed variables may be substituted; no eval or expression language.
    result=payload.template
    for key,value in payload.variables.items():
        if key not in payload.allowed_variables:
            raise HTTPException(400,f"Variable '{key}' is not allowlisted")
        if len(value)>1000:
            raise HTTPException(422,f"Variable '{key}' is too long")
        result=result.replace("{{"+key+"}}",value)
    import re
    unresolved=re.findall(r"\{\{([a-zA-Z0-9_]+)\}\}",result)
    if unresolved:
        raise HTTPException(422,"Missing template variables: "+", ".join(sorted(set(unresolved))))
    return {"rendered":result,"provider_sent":False,"note":"Rendered only; connect an approved WhatsApp Business provider to send."}
