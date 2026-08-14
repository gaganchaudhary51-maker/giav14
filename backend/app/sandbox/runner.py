from dataclasses import dataclass
from pathlib import Path
import subprocess, sys, os

@dataclass(frozen=True)
class CommandPolicy:
    timeout_seconds: int = 10
    allowed: tuple[str,...] = ("python", "pytest")

class SandboxError(Exception):
    pass

def run(command: list[str], cwd: str, policy: CommandPolicy = CommandPolicy(), workspace_root: str|None = None) -> dict:
    if not command or command[0] not in policy.allowed:
        raise SandboxError("Command is not permitted by sandbox policy")
    root=Path(cwd).resolve()
    if not root.exists() or not root.is_dir():
        raise SandboxError("Workspace does not exist")
    if workspace_root:
        allowed_root=Path(workspace_root).resolve()
        try: root.relative_to(allowed_root)
        except ValueError: raise SandboxError("Workspace is outside the permitted sandbox root")
    if any(part == ".." for part in command):
        raise SandboxError("Path traversal is not permitted")
    try:
        p=subprocess.run(command,cwd=root,text=True,capture_output=True,
                         timeout=policy.timeout_seconds,env={
                             "PATH": os.environ.get("PATH",""),
                             "PYTHONPATH": str(root)
                         })
    except subprocess.TimeoutExpired:
        raise SandboxError("Command timed out")
    return {"returncode":p.returncode,"stdout":p.stdout[-10000:],"stderr":p.stderr[-10000:]}
