"""Forward-only SQLite migrations for the forge state database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from loguru import logger

_SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    handle TEXT,
    proxy_uri TEXT,
    fingerprint_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    failure TEXT
);
CREATE INDEX IF NOT EXISTS idx_accounts_state ON accounts(state);

CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    total INTEGER NOT NULL,
    succeeded INTEGER NOT NULL DEFAULT 0,
    failed INTEGER NOT NULL DEFAULT 0
);
"""


def ensure_schema(db_path: Path) -> None:
    """Create the state schema if it doesn't already exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        conn.commit()
    logger.debug("schema ensured at {}", db_path)