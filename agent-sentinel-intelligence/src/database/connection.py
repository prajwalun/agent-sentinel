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

SCHEMA_VERSION = 2

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name          TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    is_active     INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TABLE IF NOT EXISTS agents (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'generic',
    status      TEXT NOT NULL DEFAULT 'active',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_seen   TEXT
);
CREATE INDEX IF NOT EXISTS idx_agents_last_seen ON agents(last_seen DESC);

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
CREATE INDEX IF NOT EXISTS idx_events_agent      ON security_events(agent_id);
CREATE INDEX IF NOT EXISTS idx_events_severity   ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_events_detected   ON security_events(detected_at);
CREATE INDEX IF NOT EXISTS idx_events_threat_type ON security_events(threat_type);
CREATE INDEX IF NOT EXISTS idx_events_agent_time  ON security_events(agent_id, detected_at DESC);

CREATE TABLE IF NOT EXISTS api_keys (
    id          TEXT PRIMARY KEY,
    key_hash    TEXT NOT NULL UNIQUE,
    user_id     TEXT NOT NULL REFERENCES users(id),
    description TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_used   TEXT,
    call_count  INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_keys_hash    ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_keys_user_id ON api_keys(user_id);

CREATE TABLE IF NOT EXISTS request_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL REFERENCES users(id),
    requested_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_reqlog_user_time  ON request_log(user_id, requested_at);
CREATE INDEX IF NOT EXISTS idx_reqlog_requested  ON request_log(requested_at);

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
CREATE INDEX IF NOT EXISTS idx_runs_agent      ON analysis_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_runs_input      ON analysis_runs(input_hash);
CREATE INDEX IF NOT EXISTS idx_runs_created_at ON analysis_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_status     ON analysis_runs(status);
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

    # Migration: add user_id to security_events and analysis_runs for per-user isolation
    _run_user_isolation_migration(conn)

    conn.commit()
    logger.info("Database initialised at %s (schema v%d)", _DB_PATH, SCHEMA_VERSION)


def _run_user_isolation_migration(conn: sqlite3.Connection) -> None:
    """Add user_id columns for per-user event/report isolation. Safe to run multiple times."""
    try:
        # security_events: add user_id if missing
        row = conn.execute("PRAGMA table_info(security_events)").fetchall()
        has_user_id = any(r[1] == "user_id" for r in row)
        if not has_user_id:
            conn.execute("ALTER TABLE security_events ADD COLUMN user_id TEXT REFERENCES users(id)")
            # Backfill existing rows with first user
            first_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            if first_user:
                conn.execute(
                    "UPDATE security_events SET user_id = ? WHERE user_id IS NULL",
                    (first_user[0],),
                )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_events_user ON security_events(user_id)"
            )
            logger.info("Migration: added user_id to security_events")

        # analysis_runs: add user_id if missing
        row = conn.execute("PRAGMA table_info(analysis_runs)").fetchall()
        has_user_id = any(r[1] == "user_id" for r in row)
        if not has_user_id:
            conn.execute("ALTER TABLE analysis_runs ADD COLUMN user_id TEXT REFERENCES users(id)")
            first_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            if first_user:
                conn.execute(
                    "UPDATE analysis_runs SET user_id = ? WHERE user_id IS NULL",
                    (first_user[0],),
                )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_runs_user ON analysis_runs(user_id)"
            )
            logger.info("Migration: added user_id to analysis_runs")
    except sqlite3.OperationalError as e:
        logger.warning("User isolation migration skipped or failed: %s", e)
