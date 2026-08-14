from difflib import unified_diff
def calculate_diff(old,new,path):
    return "".join(unified_diff(old.splitlines(True),new.splitlines(True),fromfile=path,tofile=path))
def apply_changes(current,changes):
    out=dict(current)
    for path,content in changes.items():
        if not path or path.startswith("/") or ".." in path.split("/"):
            raise ValueError("unsafe path")
        out[path]=content
    return out
