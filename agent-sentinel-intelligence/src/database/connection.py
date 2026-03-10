"""
SQLite connection management.

Uses stdlib sqlite3 — no ORM overhead, no extra dependency.
WAL mode is enabled for concurrent reads during analysis.
"""

import logging
import sqlite3
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DB_PATH: Optional[str] = None
_LOCAL = threading.local()
_SHARED_CONN: Optional[sqlite3.Connection] = None

SCHEMA_VERSION = 1

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'generic',
    status      TEXT NOT NULL DEFAULT 'active',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_seen   TEXT
);

CREATE TABLE IF NOT EXISTS security_events (
    id              TEXT PRIMARY KEY,
    agent_id        TEXT NOT NULL,
    threat_type     TEXT NOT NULL,
    severity        TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    confidence      REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    message         TEXT NOT NULL,
    context_json    TEXT,
    detection_method TEXT,
    detected_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
CREATE INDEX IF NOT EXISTS idx_events_agent    ON security_events(agent_id);
CREATE INDEX IF NOT EXISTS idx_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_events_detected ON security_events(detected_at);

CREATE TABLE IF NOT EXISTS api_keys (
    id          TEXT PRIMARY KEY,
    key_hash    TEXT NOT NULL UNIQUE,
    user_id     TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_used   TEXT,
    call_count  INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_keys_hash    ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_keys_user_id ON api_keys(user_id);

CREATE TABLE IF NOT EXISTS request_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    TEXT NOT NULL,
    requested_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_reqlog_user_time ON request_log(user_id, requested_at);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id           TEXT PRIMARY KEY,
    agent_id     TEXT NOT NULL,
    input_hash   TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending',
    risk_level   TEXT,
    result_json  TEXT,
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at TEXT,
    duration_ms  INTEGER,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
CREATE INDEX IF NOT EXISTS idx_runs_agent ON analysis_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_runs_input ON analysis_runs(input_hash);
"""


def _get_connection() -> sqlite3.Connection:
    """
    Return a connection to the database.

    For :memory: databases a single shared connection is used (otherwise
    each call would get a separate, empty DB).  For file-backed databases
    connections are thread-local.
    """
    global _SHARED_CONN

    if _DB_PATH is None:
        raise RuntimeError("Database not initialised — call init_db() first")

    # In-memory: reuse a single connection
    if _DB_PATH == ":memory:":
        if _SHARED_CONN is None:
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON")
            _SHARED_CONN = conn
        return _SHARED_CONN

    # File-backed: thread-local connections with WAL
    if not hasattr(_LOCAL, "conn") or _LOCAL.conn is None:
        conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _LOCAL.conn = conn
    return _LOCAL.conn


def get_db() -> sqlite3.Connection:
    """Public accessor for the thread-local database connection."""
    return _get_connection()


def init_db(db_path: str = "sentinel.db") -> None:
    """
    Initialise the database: create the file, run the schema, set WAL mode.

    Safe to call multiple times — uses CREATE IF NOT EXISTS.
    """
    global _DB_PATH, _SHARED_CONN
    _DB_PATH = db_path

    # Reset shared connection for :memory: so a fresh schema is applied
    if db_path == ":memory:":
        _SHARED_CONN = None
    else:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = _get_connection()
    conn.executescript(_SCHEMA_SQL)

    # Track schema version for future migrations
    cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
    if cursor.fetchone()[0] == 0:
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    conn.commit()
    logger.info("Database initialised at %s (schema v%d)", _DB_PATH, SCHEMA_VERSION)
