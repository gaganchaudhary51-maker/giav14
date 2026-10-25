"""Local Holographic Reduced Representation helpers for project memory vectors.

NumPy is optional at import time; lexical memory search remains available without it.
Adaptation attribution is recorded in THIRD-PARTY-NOTICES.md.
"""
from __future__ import annotations

import hashlib
import math
import struct

try:
    import numpy as np
except ImportError:  # Preserve lexical-only operation when optional runtime deps are absent.
    np = None

_TWO_PI = 2.0 * math.pi
_PREFIX = b"HRR1"
DIM = 1024


def available() -> bool:
    return np is not None


def _require_numpy() -> None:
    if np is None:
        raise RuntimeError("NumPy is required for local HRR memory vectors")


def encode_atom(word: str, dim: int = DIM):
    _require_numpy()
    values = [value for i in range(math.ceil(dim / 16))
              for value in struct.unpack("<16H", hashlib.sha256(f"{word}:{i}".encode()).digest())]
    return np.array(values[:dim], dtype=np.float64) * (_TWO_PI / 65536.0)


def bundle(*vectors):
    _require_numpy()
    if not vectors:
        raise ValueError("At least one vector is required")
    return np.angle(np.sum([np.exp(1j * vector) for vector in vectors], axis=0)) % _TWO_PI


def encode_text(text: str, dim: int = DIM):
    _require_numpy()
    tokens = [token for token in
              (part.strip(".,!?;:\"'()[]{}") for part in str(text).lower().split()) if token]
    if not tokens:
        tokens = ["__hrr_empty__"]
    return bundle(*(encode_atom(token, dim) for token in tokens))


def similarity(left, right) -> float:
    _require_numpy()
    return float(np.mean(np.cos(left - right)))


def to_bytes(vector, dim: int = DIM) -> bytes:
    _require_numpy()
    return _PREFIX + np.asarray(vector, dtype=np.float32).reshape(dim).tobytes()


def from_bytes(blob: bytes, dim: int = DIM):
    _require_numpy()
    expected = len(_PREFIX) + dim * 4
    if not isinstance(blob, bytes) or len(blob) != expected or not blob.startswith(_PREFIX):
        raise ValueError("Invalid HRR memory vector payload")
    return np.frombuffer(blob[len(_PREFIX):], dtype=np.float32).astype(np.float64)
