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
    db = get_db()
    # Seed a demo user so FK on api_keys is satisfied
    db.execute(
        "INSERT OR IGNORE INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
        ("demo-user", "demo@test.local", "not-a-real-hash", "Demo User"),
    )
    key_hash = hashlib.sha256(b"as_test_demo_key_123456").hexdigest()
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
        # Create the user first so FK is satisfied
        db = get_db()
        db.execute(
            "INSERT OR IGNORE INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)",
            ("new_user", "new@test.local", "hash", "New User"),
        )
        db.commit()

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
        # Create an event so the agent appears (agents are listed by events from this user)
        client.post(
            "/api/events",
            json={
                "agent_id": "a1",
                "threat_type": "sql_injection",
                "severity": "LOW",
                "confidence": 0.5,
                "message": "Test event",
            },
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


# -------------------------------------------------------------------
# User authentication
# -------------------------------------------------------------------


class TestUserAuth:
    def test_signup_creates_user(self):
        r = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "securepassword123",
            "name": "Test User",
        })
        assert r.status_code == 201
        data = r.json()
        assert "token" in data
        assert data["user"]["email"] == "test@example.com"
        assert "api_key" in data
        assert data["api_key"].startswith("as_")

    def test_signup_duplicate_email_fails(self):
        client.post("/api/auth/signup", json={
            "email": "dup@example.com",
            "password": "securepassword123",
            "name": "Dup User",
        })
        r = client.post("/api/auth/signup", json={
            "email": "dup@example.com",
            "password": "anotherpassword123",
            "name": "Another User",
        })
        assert r.status_code == 409

    def test_login_success(self):
        client.post("/api/auth/signup", json={
            "email": "login@example.com",
            "password": "mypassword123",
            "name": "Login User",
        })
        r = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "mypassword123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "token" in data
        assert data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self):
        client.post("/api/auth/signup", json={
            "email": "wrong@example.com",
            "password": "correctpassword",
            "name": "Wrong",
        })
        r = client.post("/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "incorrectpassword",
        })
        assert r.status_code == 401

    def test_jwt_auth_on_protected_endpoint(self):
        signup_resp = client.post("/api/auth/signup", json={
            "email": "jwt@example.com",
            "password": "jwtpassword123",
            "name": "JWT User",
        })
        token = signup_resp.json()["token"]
        r = client.get("/api/dashboard/stats", headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200

    def test_get_me(self):
        signup_resp = client.post("/api/auth/signup", json={
            "email": "me@example.com",
            "password": "mepassword123",
            "name": "Me User",
        })
        token = signup_resp.json()["token"]
        r = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200
        assert r.json()["email"] == "me@example.com"

    def test_self_service_api_key(self):
        signup_resp = client.post("/api/auth/signup", json={
            "email": "keys@example.com",
            "password": "keyspassword123",
            "name": "Keys User",
        })
        token = signup_resp.json()["token"]
        r = client.post("/api/keys", headers={
            "Authorization": f"Bearer {token}",
        })
        assert r.status_code == 200
        assert r.json()["api_key"].startswith("as_")

        r2 = client.get("/api/keys", headers={
            "Authorization": f"Bearer {token}",
        })
        assert r2.status_code == 200
        assert r2.json()["total"] >= 1


# -------------------------------------------------------------------
# Key revocation
# -------------------------------------------------------------------


class TestKeyRevocation:
    def _signup_and_get_token(self, email: str):
        resp = client.post("/api/auth/signup", json={
            "email": email,
            "password": "password123456",
            "name": "Revoke Tester",
        })
        return resp.json()["token"]

    def test_revoke_own_key(self):
        token = self._signup_and_get_token("revoke1@example.com")
        auth = {"Authorization": f"Bearer {token}"}

        new_key = client.post("/api/keys", headers=auth).json()["api_key"]
        keys = client.get("/api/keys", headers=auth).json()["keys"]
        active_key = next(k for k in keys if k["is_active"])

        r = client.delete(f"/api/keys/{active_key['id']}", headers=auth)
        assert r.status_code == 200

        keys_after = client.get("/api/keys", headers=auth).json()["keys"]
        revoked = next(k for k in keys_after if k["id"] == active_key["id"])
        assert revoked["is_active"] == 0

    def test_revoke_nonexistent_key_returns_404(self):
        token = self._signup_and_get_token("revoke2@example.com")
        auth = {"Authorization": f"Bearer {token}"}
        r = client.delete("/api/keys/nonexistent_id", headers=auth)
        assert r.status_code == 404

    def test_cannot_revoke_other_users_key(self):
        token_a = self._signup_and_get_token("revokeA@example.com")
        token_b = self._signup_and_get_token("revokeB@example.com")

        client.post("/api/keys", headers={"Authorization": f"Bearer {token_a}"})
        keys_a = client.get("/api/keys", headers={"Authorization": f"Bearer {token_a}"}).json()["keys"]
        key_id = keys_a[0]["id"]

        r = client.delete(
            f"/api/keys/{key_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 404

    def test_revoked_api_key_cannot_authenticate(self):
        token = self._signup_and_get_token("revoke3@example.com")
        auth = {"Authorization": f"Bearer {token}"}

        raw = client.post("/api/keys", headers=auth).json()["api_key"]
        # Verify it works before revoking
        r1 = client.get("/api/agents", headers={"Authorization": f"Bearer {raw}"})
        assert r1.status_code == 200

        keys = client.get("/api/keys", headers=auth).json()["keys"]
        # Find the key that was just created (not the default one)
        key_record = [k for k in keys if k["description"] != "Default key"][-1]

        client.delete(f"/api/keys/{key_record['id']}", headers=auth)

        r2 = client.get("/api/agents", headers={"Authorization": f"Bearer {raw}"})
        assert r2.status_code == 401


class TestKeyWithDescription:
    def test_custom_description(self):
        signup = client.post("/api/auth/signup", json={
            "email": "desc@example.com",
            "password": "password123456",
            "name": "Desc User",
        })
        token = signup.json()["token"]
        auth = {"Authorization": f"Bearer {token}"}

        client.post("/api/keys", json={"description": "Production"}, headers=auth)
        keys = client.get("/api/keys", headers=auth).json()["keys"]
        described = [k for k in keys if k["description"] == "Production"]
        assert len(described) == 1


# -------------------------------------------------------------------
# SSE authentication
# -------------------------------------------------------------------


class TestSSEAuth:
    def test_stream_rejects_without_token(self):
        r = client.get("/api/events/stream")
        assert r.status_code == 422  # missing required query param

    def test_stream_rejects_invalid_token(self):
        r = client.get("/api/events/stream?token=bad-token-here")
        assert r.status_code == 401


# -------------------------------------------------------------------
# Agent pagination
# -------------------------------------------------------------------


class TestAgentPagination:
    def test_pagination_params(self):
        for i in range(5):
            client.post(
                "/api/agents",
                json={"id": f"pg_{i}", "name": f"Paginated Agent {i}"},
                headers=AUTH,
            )
            # Create event so agent appears in list (filtered by user's events)
            client.post(
                "/api/events",
                json={
                    "agent_id": f"pg_{i}",
                    "threat_type": "sql_injection",
                    "severity": "LOW",
                    "confidence": 0.5,
                    "message": "test",
                },
                headers=AUTH,
            )
        r = client.get("/api/agents?limit=2&offset=0", headers=AUTH)
        data = r.json()
        assert len(data["agents"]) == 2
        assert data["total"] == 5
        assert data["offset"] == 0

        r2 = client.get("/api/agents?limit=2&offset=3", headers=AUTH)
        assert len(r2.json()["agents"]) == 2

    def test_agents_include_event_count(self):
        client.post(
            "/api/agents",
            json={"id": "cnt_agent", "name": "Count Agent"},
            headers=AUTH,
        )
        for _ in range(3):
            client.post(
                "/api/events",
                json={
                    "agent_id": "cnt_agent",
                    "threat_type": "xss",
                    "severity": "LOW",
                    "confidence": 0.5,
                    "message": "test",
                },
                headers=AUTH,
            )
        r = client.get("/api/agents", headers=AUTH)
        agent = next(a for a in r.json()["agents"] if a["id"] == "cnt_agent")
        assert agent["event_count"] == 3


# -------------------------------------------------------------------
# Analysis status DB fallback
# -------------------------------------------------------------------


class TestAnalysisStatusFallback:
    def test_nonexistent_run_returns_404(self):
        r = client.get("/api/analysis/no_such_run/status", headers=AUTH)
        assert r.status_code == 404

    def test_db_run_found_via_fallback(self):
        from database import Repository
        repo = Repository()
        client.post(
            "/api/agents",
            json={"id": "fb_agent", "name": "Fallback Agent"},
            headers=AUTH,
        )
        run_id = repo.create_analysis_run("fb_agent", "testhash", user_id="demo-user")
        r = client.get(f"/api/analysis/{run_id}/status", headers=AUTH)
        assert r.status_code == 200
        assert r.json()["status"] == "pending"


# -------------------------------------------------------------------
# Report total count
# -------------------------------------------------------------------


class TestReportTotal:
    def test_total_reflects_db_count(self):
        from database import Repository
        repo = Repository()
        client.post(
            "/api/agents",
            json={"id": "rpt_agent", "name": "Report Agent"},
            headers=AUTH,
        )
        for i in range(5):
            repo.create_analysis_run("rpt_agent", f"hash_{i}", user_id="demo-user")
        r = client.get("/api/reports?limit=2", headers=AUTH)
        data = r.json()
        assert len(data["reports"]) == 2
        assert data["total"] == 5
