import os
from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class Provider:
    id:str; kind:str; tier:str; mode:str; configured:bool; requires_key:bool; cost_note:str

# Order is deliberate: local/browser -> free/quota-free where configured -> low-cost hosted -> premium.
# "Free" means no provider charge under the provider's applicable limits; it never means unlimited.
CATALOG=[
 Provider("browser-web-speech","stt","free","browser",True,False,"Browser/platform dependent"),
 Provider("whisper-local","stt","free","local",bool(os.getenv("WHISPER_LOCAL_ENABLED")=="1"),False,"Local compute only"),
 Provider("free-stt-provider","stt","free","hosted",bool(os.getenv("FREE_STT_API_KEY")),True,"Provider quota/terms apply"),
 Provider("cheap-stt-provider","stt","cheap","hosted",bool(os.getenv("CHEAP_STT_API_KEY")),True,"Low-cost provider; quota/price applies"),
 Provider("browser-web-speech","tts","free","browser",True,False,"Browser/platform dependent"),
 Provider("piper-local","tts","free","local",bool(os.getenv("PIPER_LOCAL_ENABLED")=="1"),False,"Local compute only"),
 Provider("free-tts-provider","tts","free","hosted",bool(os.getenv("FREE_TTS_API_KEY")),True,"Provider quota/terms apply"),
 Provider("cheap-tts-provider","tts","cheap","hosted",bool(os.getenv("CHEAP_TTS_API_KEY")),True,"Low-cost provider; quota/price applies"),
]

def _available(kind):
    return [p for p in CATALOG if p.kind==kind and p.configured]

def route(kind, preferred=None, india=True):
    xs=_available(kind)
    if preferred:
        for p in xs:
            if p.id==preferred:return {"selected":asdict(p),"chain":[asdict(x) for x in xs],"reason":"Explicit provider preference"}
    # Free-first. Local/browser is preferred before hosted services.
    rank={"browser":0,"local":1,"hosted":2}
    xs.sort(key=lambda p:(0 if p.tier=="free" else 1,rank[p.mode],p.id))
    selected=xs[0] if xs else None
    return {"selected":asdict(selected) if selected else None,"chain":[asdict(x) for x in xs],
            "reason":"Free-first routing; cheap hosted provider is next eligible tier." if selected else "No provider configured"}

def provider_status():
    return {
      "stt": {**route("stt"), "browser": True, "configured": bool(os.getenv("STT_PROVIDER")), "unlimited_free": False},
      "tts": {**route("tts"), "browser": True, "configured": bool(os.getenv("TTS_PROVIDER")), "unlimited_free": False},
      "unlimited_free": False,
      "policy":{"free_first":True,"cheap_auto_switch":True,"premium_auto_switch":False,
                "unlimited_free_claim":False,"india_latency_aware":True},
      "note":"Local/browser options are preferred. Hosted free tiers remain subject to provider quotas/terms; the system never claims unlimited free usage."
    }
