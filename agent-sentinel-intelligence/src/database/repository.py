"""
Data-access layer for the intelligence backend.

Thin repository that wraps raw SQL so the rest of the application
never touches sqlite3 directly.  Each public method is a single
logical operation (insert, query, update) with explicit parameters.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from .connection import get_db

logger = logging.getLogger(__name__)


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row) if row else {}


class Repository:
    """
    Centralised data-access object.

    All write operations commit immediately so callers don't need
    to worry about transaction management for simple CRUD.
    """

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def create_user(
        self, email: str, password_hash: str, name: str = ""
    ) -> Dict[str, Any]:
        user_id = f"usr_{uuid.uuid4().hex[:16]}"
        db = get_db()
        db.execute(
            "INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
            (user_id, email, password_hash, name),
        )
        db.commit()
        return self.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        row = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        row = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------

    def upsert_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: str = "generic",
        status: str = "active",
    ) -> Dict[str, Any]:
        db = get_db()
        now = _utcnow()
        db.execute(
            """
            INSERT INTO agents (id, name, type, status, created_at, last_seen)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name      = excluded.name,
                type      = excluded.type,
                status    = excluded.status,
                last_seen = excluded.last_seen
            """,
            (agent_id, name, agent_type, status, now, now),
        )
        db.commit()
        return self.get_agent(agent_id)

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        row = get_db().execute("SELECT * FROM agents WHERE id = ?", (agent_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        if status:
            rows = get_db().execute(
                "SELECT * FROM agents WHERE status = ? ORDER BY last_seen DESC", (status,)
            ).fetchall()
        else:
            rows = get_db().execute("SELECT * FROM agents ORDER BY last_seen DESC").fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_agent_count(self, status: Optional[str] = None) -> int:
        if status:
            row = get_db().execute(
                "SELECT COUNT(*) AS cnt FROM agents WHERE status = ?", (status,)
            ).fetchone()
        else:
            row = get_db().execute("SELECT COUNT(*) AS cnt FROM agents").fetchone()
        return row["cnt"]

    # ------------------------------------------------------------------
    # Security events
    # ------------------------------------------------------------------

    def insert_event(
        self,
        agent_id: str,
        threat_type: str,
        severity: str,
        confidence: float,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        detection_method: str = "pattern_matching",
    ) -> Dict[str, Any]:
        event_id = f"evt_{uuid.uuid4().hex[:16]}"
        db = get_db()
        db.execute(
            """
            INSERT INTO security_events
                (id, agent_id, threat_type, severity, confidence, message, context_json, detection_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                agent_id,
                threat_type,
                severity,
                confidence,
                message,
                json.dumps(context) if context else None,
                detection_method,
            ),
        )
        db.commit()

        # Touch the agent's last_seen timestamp
        db.execute("UPDATE agents SET last_seen = ? WHERE id = ?", (_utcnow(), agent_id))
        db.commit()

        return self.get_event(event_id)

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        row = get_db().execute("SELECT * FROM security_events WHERE id = ?", (event_id,)).fetchone()
        return _row_to_dict(row) if row else None

    def list_events(
        self,
        agent_id: Optional[str] = None,
        severity: Optional[str] = None,
        threat_type: Optional[str] = None,
        since: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []

        if agent_id:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if threat_type:
            clauses.append("threat_type = ?")
            params.append(threat_type)
        if since:
            clauses.append("detected_at >= ?")
            params.append(since)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.extend([limit, offset])

        rows = get_db().execute(
            f"SELECT * FROM security_events {where} ORDER BY detected_at DESC LIMIT ? OFFSET ?",
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_event_count(
        self,
        agent_id: Optional[str] = None,
        severity: Optional[str] = None,
        since: Optional[str] = None,
    ) -> int:
        clauses: List[str] = []
        params: List[Any] = []

        if agent_id:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if since:
            clauses.append("detected_at >= ?")
            params.append(since)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        row = get_db().execute(
            f"SELECT COUNT(*) AS cnt FROM security_events {where}", params
        ).fetchone()
        return row["cnt"]

    def get_severity_counts(self, since: Optional[str] = None) -> Dict[str, int]:
        clauses = []
        params: List[Any] = []
        if since:
            clauses.append("detected_at >= ?")
            params.append(since)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = get_db().execute(
            f"SELECT severity, COUNT(*) AS cnt FROM security_events {where} GROUP BY severity",
            params,
        ).fetchall()
        return {r["severity"]: r["cnt"] for r in rows}

    # ------------------------------------------------------------------
    # API keys
    # ------------------------------------------------------------------

    def create_api_key(self, user_id: str, description: str = "") -> str:
        """
        Generate a new API key, store its SHA-256 hash, and return
        the raw key (only time it's ever available in plaintext).
        """
        key_id = uuid.uuid4().hex[:24]
        raw_key = f"as_{key_id}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        record_id = f"key_{uuid.uuid4().hex[:12]}"

        db = get_db()
        db.execute(
            """
            INSERT INTO api_keys (id, key_hash, user_id, description)
            VALUES (?, ?, ?, ?)
            """,
            (record_id, key_hash, user_id, description),
        )
        db.commit()
        logger.info("API key created for user=%s", user_id)
        return raw_key

    def validate_api_key(self, raw_key: str) -> Optional[Dict[str, Any]]:
        """
        Look up an API key by its hash.  Returns the key record if valid
        and active, or None.  Also increments call_count and updates
        last_used on successful validation.
        """
        if not raw_key or not raw_key.startswith("as_"):
            return None

        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        row = get_db().execute(
            "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1",
            (key_hash,),
        ).fetchone()

        if not row:
            return None

        now = _utcnow()
        get_db().execute(
            "UPDATE api_keys SET last_used = ?, call_count = call_count + 1 WHERE id = ?",
            (now, row["id"]),
        )
        get_db().commit()
        return _row_to_dict(row)

    def list_api_keys_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Return metadata for all keys belonging to a user (never raw keys)."""
        rows = get_db().execute(
            "SELECT id, user_id, description, created_at, last_used, call_count, is_active "
            "FROM api_keys WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def check_rate_limit(self, user_id: str, max_per_hour: int = 100) -> bool:
        """
        Sliding-window rate limit using a dedicated request_log table.

        Each authenticated request is recorded with a timestamp.
        This method counts rows in the last hour and compares to the cap.
        Old entries are pruned on every check to keep the table small.
        """
        db = get_db()
        now = _utcnow()
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        # Record this request
        db.execute(
            "INSERT INTO request_log (user_id, requested_at) VALUES (?, ?)",
            (user_id, now),
        )

        # Prune entries older than 1 hour (keeps table bounded)
        db.execute(
            "DELETE FROM request_log WHERE requested_at < ?", (one_hour_ago,)
        )
        db.commit()

        # Count requests in the window
        row = db.execute(
            "SELECT COUNT(*) AS cnt FROM request_log WHERE user_id = ? AND requested_at >= ?",
            (user_id, one_hour_ago),
        ).fetchone()
        return row["cnt"] <= max_per_hour

    # ------------------------------------------------------------------
    # Analysis runs
    # ------------------------------------------------------------------

    def create_analysis_run(self, agent_id: str, input_hash: str) -> str:
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        db = get_db()
        db.execute(
            "INSERT INTO analysis_runs (id, agent_id, input_hash) VALUES (?, ?, ?)",
            (run_id, agent_id, input_hash),
        )
        db.commit()
        return run_id

    def complete_analysis_run(
        self,
        run_id: str,
        risk_level: str,
        result: Dict[str, Any],
        duration_ms: int,
    ) -> None:
        db = get_db()
        db.execute(
            """
            UPDATE analysis_runs
            SET status = 'completed', risk_level = ?, result_json = ?,
                completed_at = ?, duration_ms = ?
            WHERE id = ?
            """,
            (risk_level, json.dumps(result), _utcnow(), duration_ms, run_id),
        )
        db.commit()

    def fail_analysis_run(self, run_id: str, error: str) -> None:
        db = get_db()
        db.execute(
            """
            UPDATE analysis_runs
            SET status = 'failed', result_json = ?, completed_at = ?
            WHERE id = ?
            """,
            (json.dumps({"error": error}), _utcnow(), run_id),
        )
        db.commit()

    def list_analysis_runs(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if agent_id:
            clauses.append("agent_id = ?")
            params.append(agent_id)
        if status:
            clauses.append("status = ?")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        rows = get_db().execute(
            f"SELECT * FROM analysis_runs {where} ORDER BY created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_analysis_run_count(self) -> int:
        row = get_db().execute("SELECT COUNT(*) AS cnt FROM analysis_runs").fetchone()
        return row["cnt"]

    # ------------------------------------------------------------------
    # Dashboard statistics
    # ------------------------------------------------------------------

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Single call that returns everything the dashboard stats panel needs.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

        total_agents = self.get_agent_count()
        active_agents = self.get_agent_count(status="active")
        total_events = self.get_event_count()
        events_today = self.get_event_count(since=today)
        severity_counts = self.get_severity_counts()
        severity_today = self.get_severity_counts(since=today)
        total_analyses = self.get_analysis_run_count()

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_events": total_events,
            "events_today": events_today,
            "severity_counts": severity_counts,
            "severity_today": severity_today,
            "total_analyses": total_analyses,
        }
