from app.voice.providers import route
def select(kind,preferred=None):
    return route(kind,preferred)
def fallback_chain(kind,failed_provider=None):
    x=route(kind)
    chain=x["chain"]
    if failed_provider: chain=[p for p in chain if p["id"]!=failed_provider]
    return chain
