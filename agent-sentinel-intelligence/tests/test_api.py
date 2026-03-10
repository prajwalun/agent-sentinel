"""
Integration tests for the API server.

Uses httpx + FastAPI TestClient to hit every endpoint without
needing a running server or external dependencies.
"""

import hashlib
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Override DB path before importing the app
os.environ["SENTINEL_DB_PATH"] = ":memory:"
os.environ["ADMIN_SECRET"] = "test-admin-secret"
os.environ["DEMO_API_KEY"] = "as_test_demo_key_123456"

from api_server import app
from database import Repository, init_db
from database.connection import get_db


@pytest.fixture(autouse=True)
def _reset_db():
    """Reinitialise the in-memory database before each test."""
    init_db(":memory:")
    # Seed demo key
    key_hash = hashlib.sha256(b"as_test_demo_key_123456").hexdigest()
    db = get_db()
    db.execute(
        "INSERT OR IGNORE INTO api_keys (id, key_hash, user_id, description) VALUES (?, ?, ?, ?)",
        ("key_demo", key_hash, "demo-user", "Test demo key"),
    )
    db.commit()
    yield


client = TestClient(app)
DEMO_KEY = "as_test_demo_key_123456"
AUTH = {"Authorization": f"Bearer {DEMO_KEY}"}
ADMIN = {"X-Admin-Token": "test-admin-secret"}


# -------------------------------------------------------------------
# Health & metrics (public)
# -------------------------------------------------------------------


class TestHealthAndMetrics:
    def test_health_returns_200(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert "database" in data

    def test_metrics_returns_200(self):
        r = client.get("/api/metrics")
        assert r.status_code == 200
        data = r.json()
        assert "uptime_seconds" in data
        assert "total_requests" in data


# -------------------------------------------------------------------
# Auth
# -------------------------------------------------------------------


class TestAuth:
    def test_missing_token_returns_403(self):
        r = client.get("/api/agents")
        assert r.status_code in (401, 403)

    def test_invalid_token_returns_401(self):
        r = client.get("/api/agents", headers={"Authorization": "Bearer bad_key"})
        assert r.status_code == 401

    def test_valid_token_passes(self):
        r = client.get("/api/agents", headers=AUTH)
        assert r.status_code == 200

    def test_validate_key(self):
        r = client.get("/api/keys/validate", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["valid"] is True


# -------------------------------------------------------------------
# API key management (admin)
# -------------------------------------------------------------------


class TestKeyManagement:
    def test_generate_key_requires_admin(self):
        r = client.post("/api/keys/generate", json={"user_id": "new_user"})
        assert r.status_code in (401, 403, 422)

    def test_generate_key_with_admin(self):
        r = client.post(
            "/api/keys/generate",
            json={"user_id": "new_user", "description": "test key"},
            headers=ADMIN,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["api_key"].startswith("as_")
        assert "shown again" in data["message"].lower() or "store" in data["message"].lower()


# -------------------------------------------------------------------
# Agents
# -------------------------------------------------------------------


class TestAgents:
    def test_list_agents_empty(self):
        r = client.get("/api/agents", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_register_agent(self):
        r = client.post(
            "/api/agents",
            json={"id": "test_agent", "name": "Test Agent", "type": "sdk"},
            headers=AUTH,
        )
        assert r.status_code == 201
        assert r.json()["id"] == "test_agent"

    def test_list_agents_after_register(self):
        client.post(
            "/api/agents",
            json={"id": "a1", "name": "Agent One"},
            headers=AUTH,
        )
        r = client.get("/api/agents", headers=AUTH)
        assert r.json()["total"] >= 1


# -------------------------------------------------------------------
# Events
# -------------------------------------------------------------------


class TestEvents:
    def _create_agent(self):
        client.post(
            "/api/agents",
            json={"id": "evt_agent", "name": "Event Agent"},
            headers=AUTH,
        )

    def test_create_event(self):
        self._create_agent()
        r = client.post(
            "/api/events",
            json={
                "agent_id": "evt_agent",
                "threat_type": "sql_injection",
                "severity": "HIGH",
                "confidence": 0.92,
                "message": "SQL injection detected in query parameter",
            },
            headers=AUTH,
        )
        assert r.status_code == 201
        assert r.json()["threat_type"] == "sql_injection"

    def test_list_events(self):
        self._create_agent()
        client.post(
            "/api/events",
            json={
                "agent_id": "evt_agent",
                "threat_type": "xss",
                "severity": "MEDIUM",
                "confidence": 0.85,
                "message": "XSS payload detected",
            },
            headers=AUTH,
        )
        r = client.get("/api/events", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_filter_events_by_severity(self):
        self._create_agent()
        client.post(
            "/api/events",
            json={
                "agent_id": "evt_agent",
                "threat_type": "xss",
                "severity": "CRITICAL",
                "confidence": 0.99,
                "message": "Critical XSS",
            },
            headers=AUTH,
        )
        r = client.get("/api/events?severity=CRITICAL", headers=AUTH)
        assert r.status_code == 200
        for event in r.json()["events"]:
            assert event["severity"] == "CRITICAL"


# -------------------------------------------------------------------
# Dashboard stats
# -------------------------------------------------------------------


class TestDashboardStats:
    def test_dashboard_stats(self):
        r = client.get("/api/dashboard/stats", headers=AUTH)
        assert r.status_code == 200
        data = r.json()
        assert "total_agents" in data
        assert "total_events" in data
        assert "severity_counts" in data


# -------------------------------------------------------------------
# Reports
# -------------------------------------------------------------------


class TestReports:
    def test_list_reports_empty(self):
        r = client.get("/api/reports", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["total"] == 0


# -------------------------------------------------------------------
# Status determination
# -------------------------------------------------------------------


class TestStatusLogic:
    def test_clean_for_empty(self):
        from api_server import _determine_status
        assert _determine_status([]) == "CLEAN"

    def test_clean_for_low_only(self):
        from api_server import _determine_status
        events = [{"severity": "LOW"}, {"severity": "MEDIUM"}]
        assert _determine_status(events) == "CLEAN"

    def test_warning_for_high(self):
        from api_server import _determine_status
        events = [{"severity": "HIGH"}]
        assert _determine_status(events) == "WARNING"

    def test_critical_for_critical(self):
        from api_server import _determine_status
        events = [{"severity": "CRITICAL"}]
        assert _determine_status(events) == "CRITICAL"
