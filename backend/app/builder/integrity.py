from pathlib import Path
import hashlib, json

def file_sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def manifest(root: str) -> dict:
    base=Path(root).resolve()
    items={}
    if base.exists():
        for p in sorted(base.rglob("*")):
            if p.is_file() and ".gia-checkpoints" not in p.parts:
                items[str(p.relative_to(base))]=file_sha256(p)
    return {"root":str(base),"files":items}
