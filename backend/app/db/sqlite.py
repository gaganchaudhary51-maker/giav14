"""Small SQLite persistence helper shared by GIA stores.

SQLite is the local-first default. Set GIA_DATA_DIR to choose a durable data directory.
MongoDB-backed project/user stores remain supported separately.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def database_path() -> Path:
    configured = os.getenv("GIA_DATA_DIR")
    if configured:
        base = Path(configured).expanduser()
    else:
        base = Path(__file__).resolve().parents[2] / "data"
    base.mkdir(parents=True, exist_ok=True)
    return base / "gia.sqlite3"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(database_path()), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn
