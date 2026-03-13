"""
Agent Sentinel Intelligence — API Server

FastAPI application that provides:
  - Bearer-token authentication backed by SQLite
  - Security report analysis via LangGraph multi-agent workflow
  - CRUD endpoints for agents, events, and analysis runs
  - Dashboard statistics and a simple metrics endpoint
  - Server-Sent Events stream for live event updates
"""

import warnings

# Suppress requests/urllib3 version mismatch warning (cosmetic only)
warnings.filterwarnings("ignore", message=".*doesn't match a supported version.*")

import hashlib
import json
import logging
import os
import re
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import bcrypt
import jwt
from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load .env from project root (parent of agent-sentinel-intelligence) for manual runs
from dotenv import load_dotenv
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

from database import Repository, init_db
from utils.logging_config import setup_enterprise_logging

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
setup_enterprise_logging()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Globals initialised during lifespan
# ---------------------------------------------------------------------------
repo = Repository()
workflow_instance: Optional[Any] = None
_start_time: float = 0.0
_request_count: int = 0

# Confidence-score regex compiled once at module level
_CONFIDENCE_RE = re.compile(r"confidence[:\s]*(\d+\.?\d*)", re.IGNORECASE)

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "sentinel-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))


# ---------------------------------------------------------------------------
# Lifespan (replaces deprecated @app.on_event)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global workflow_instance, _start_time

    _start_time = time.monotonic()

    db_path = os.getenv("SENTINEL_DB_PATH", "sentinel.db")
    init_db(db_path)
    logger.info("Database ready at %s", db_path)

    # Seed a demo API key if the env var is set and no keys exist yet
    demo_key_raw = os.getenv("DEMO_API_KEY")
    if demo_key_raw:
        existing = repo.validate_api_key(demo_key_raw)
        if not existing:
            key_hash = hashlib.sha256(demo_key_raw.encode()).hexdigest()
            from database.connection import get_db

            db = get_db()
            db.execute(
                "INSERT OR IGNORE INTO api_keys (id, key_hash, user_id, description) VALUES (?, ?, ?, ?)",
                (f"key_demo", key_hash, "demo-user", "Seeded demo key"),
            )
            db.commit()
            logger.info("Demo API key seeded")

    try:
        from workflow import create_workflow_from_env

        workflow_instance = create_workflow_from_env()
        if workflow_instance:
            logger.info("LangGraph workflow initialised — AI analysis enabled")
        else:
            logger.info(
                "AI analysis disabled (no OPENAI_API_KEY). "
                "Event detection, dashboard, and API keys work normally. "
                "Add OPENAI_API_KEY to .env to enable report analysis."
            )
    except Exception as e:
        logger.warning(
            "Workflow init failed — analysis endpoints will return 503: %s",
            e,
            exc_info=False,
        )

    yield  # application runs

    logger.info("Shutting down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Agent Sentinel Intelligence API",
    description="Security analysis backend for the Agent Sentinel platform",
    version="2.1.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class AnalysisRequest(BaseModel):
    report_content: str = Field(..., min_length=1, max_length=1_000_000)
    analysis_type: str = "comprehensive"
    agent_id: Optional[str] = None


class AgentCreateRequest(BaseModel):
    id: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=256)
    type: str = Field(default="generic", max_length=64)


class EventCreateRequest(BaseModel):
    agent_id: str
    threat_type: str
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    message: str
    context: Optional[Dict[str, Any]] = None
    detection_method: str = "sdk"


class KeyGenerateRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    description: str = ""


class SignUpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=256)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1, max_length=256)
    password: str = Field(..., min_length=1, max_length=128)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def _create_jwt(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _decode_jwt(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
_bearer = HTTPBearer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Dict[str, Any]:
    """
    Validate Bearer token — supports both API keys (as_ prefix, for SDK)
    and JWT tokens (for dashboard sessions).
    """
    global _request_count
    _request_count += 1

    token = credentials.credentials

    # API key path (SDK clients)
    if token.startswith("as_"):
        key_record = repo.validate_api_key(token)
        if not key_record:
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")
        if not repo.check_rate_limit(key_record["user_id"]):
            raise HTTPException(status_code=429, detail="Rate limit exceeded (100 req/hr)")
        return {"user_id": key_record["user_id"], "auth_type": "api_key", **key_record}

    # JWT path (dashboard sessions)
    claims = _decode_jwt(token)
    user = repo.get_user_by_id(claims["sub"])
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=401, detail="User account not found or inactive")
    return {"user_id": user["id"], "email": user["email"], "auth_type": "jwt"}


async def require_admin(
    x_admin_token: str = Header(..., alias="X-Admin-Token"),
) -> None:
    """Protect admin-only routes with a shared secret from the environment."""
    expected = os.getenv("ADMIN_SECRET", "")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Invalid admin token")


# ---------------------------------------------------------------------------
# Health & metrics (public)
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.1.0",
        "workflow_ready": workflow_instance is not None,
        "database": "connected",
    }


@app.get("/api/metrics")
async def get_metrics():
    """Lightweight operational metrics for the dashboard and monitoring."""
    uptime = time.monotonic() - _start_time
    stats = repo.get_dashboard_stats()
    return {
        "uptime_seconds": round(uptime, 1),
        "total_requests": _request_count,
        "total_events_processed": stats["total_events"],
        "total_agents": stats["total_agents"],
        "total_analyses": stats["total_analyses"],
        "workflow_ready": workflow_instance is not None,
    }


# ---------------------------------------------------------------------------
# User authentication (public — no token required)
# ---------------------------------------------------------------------------


@app.post("/api/auth/signup", status_code=201)
async def signup(body: SignUpRequest):
    existing = repo.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    user = repo.create_user(email=body.email, password_hash=hashed, name=body.name)

    # Provision an initial API key so they can start using the SDK immediately
    api_key = repo.create_api_key(user["id"], description="Default key")
    token = _create_jwt(user["id"], user["email"])

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
        },
        "api_key": api_key,
    }


@app.post("/api/auth/login")
async def login(body: LoginRequest):
    user = repo.get_user_by_email(body.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = _create_jwt(user["id"], user["email"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "created_at": user["created_at"],
        },
    }


@app.get("/api/auth/me")
async def get_current_user(user_info: Dict[str, Any] = Depends(require_auth)):
    """Return the authenticated user's profile."""
    user = repo.get_user_by_id(user_info["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "created_at": user["created_at"],
    }


# ---------------------------------------------------------------------------
# API key management (admin-gated or self-service for authenticated users)
# ---------------------------------------------------------------------------


@app.post("/api/keys/generate")
async def generate_api_key(body: KeyGenerateRequest, _: None = Depends(require_admin)):
    raw_key = repo.create_api_key(body.user_id, body.description)
    return {
        "api_key": raw_key,
        "user_id": body.user_id,
        "message": "Store this key securely — it will not be shown again.",
    }


class CreateKeyRequest(BaseModel):
    description: str = Field(default="API key", max_length=256)


@app.post("/api/keys")
async def create_own_api_key(
    body: Optional[CreateKeyRequest] = None,
    user_info: Dict[str, Any] = Depends(require_auth),
):
    """Authenticated users can create new API keys for themselves."""
    desc = body.description if body else "API key"
    raw_key = repo.create_api_key(user_info["user_id"], description=desc)
    return {
        "api_key": raw_key,
        "message": "Store this key securely — it will not be shown again.",
    }


@app.get("/api/keys")
async def list_own_api_keys(user_info: Dict[str, Any] = Depends(require_auth)):
    """List the authenticated user's API keys (hashes and metadata, not raw keys)."""
    keys = repo.list_api_keys_for_user(user_info["user_id"])
    return {"keys": keys, "total": len(keys)}


@app.delete("/api/keys/{key_id}")
async def revoke_api_key(
    key_id: str, user_info: Dict[str, Any] = Depends(require_auth)
):
    """Deactivate an API key. Only the owning user can revoke their keys."""
    revoked = repo.revoke_api_key(key_id, user_info["user_id"])
    if not revoked:
        raise HTTPException(status_code=404, detail="Key not found or not owned by you")
    return {"message": "API key revoked"}


@app.get("/api/keys/validate")
async def validate_current_key(user_info: Dict[str, Any] = Depends(require_auth)):
    return {
        "valid": True,
        "user_id": user_info["user_id"],
    }


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------


@app.get("/api/dashboard/stats")
async def dashboard_stats(user_info: Dict[str, Any] = Depends(require_auth)):
    return repo.get_dashboard_stats(user_id=user_info["user_id"])


# ---------------------------------------------------------------------------
# Agents CRUD
# ---------------------------------------------------------------------------


@app.get("/api/agents")
async def list_agents(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_info: Dict[str, Any] = Depends(require_auth),
):
    agents = repo.list_agents(status=status, user_id=user_info["user_id"])
    event_counts = repo.get_event_counts_by_agent(user_id=user_info["user_id"])
    for agent in agents:
        agent["event_count"] = event_counts.get(agent["id"], 0)
    total = len(agents)
    paginated = agents[offset : offset + limit]
    return {"agents": paginated, "total": total, "limit": limit, "offset": offset}


@app.post("/api/agents", status_code=201)
async def register_agent(
    body: AgentCreateRequest, _: Dict[str, Any] = Depends(require_auth)
):
    agent = repo.upsert_agent(body.id, body.name, body.type)
    return agent


# ---------------------------------------------------------------------------
# Security events
# ---------------------------------------------------------------------------


@app.get("/api/events")
async def list_events(
    agent_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    threat_type: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_info: Dict[str, Any] = Depends(require_auth),
):
    events = repo.list_events(
        agent_id=agent_id,
        severity=severity,
        threat_type=threat_type,
        since=since,
        limit=limit,
        offset=offset,
        user_id=user_info["user_id"],
    )
    total = repo.get_event_count(
        agent_id=agent_id, severity=severity, since=since, user_id=user_info["user_id"]
    )
    return {"events": events, "total": total, "limit": limit, "offset": offset}


@app.post("/api/events", status_code=201)
async def create_event(
    body: EventCreateRequest, user_info: Dict[str, Any] = Depends(require_auth)
):
    """
    Ingest a security event — typically called by the SDK when
    it detects a threat during agent monitoring.
    """
    # Auto-register the agent if we haven't seen it before
    if not repo.get_agent(body.agent_id):
        repo.upsert_agent(body.agent_id, body.agent_id, "sdk")

    event = repo.insert_event(
        agent_id=body.agent_id,
        threat_type=body.threat_type,
        severity=body.severity,
        confidence=body.confidence,
        message=body.message,
        context=body.context,
        detection_method=body.detection_method,
        user_id=user_info["user_id"],
    )
    return event


@app.get("/api/events/stream")
async def event_stream(request: Request, token: str = Query(...)):
    """
    Server-Sent Events endpoint.  Pushes new security events to
    connected clients every 2 seconds.

    Requires a valid JWT passed as a query parameter because the
    browser EventSource API does not support custom headers.
    """
    claims = _decode_jwt(token)  # raises 401 if invalid/expired
    user_id = claims.get("sub")

    async def generate() -> AsyncGenerator[str, None]:
        last_seen_count = repo.get_event_count(user_id=user_id)
        while True:
            if await request.is_disconnected():
                break
            current_count = repo.get_event_count(user_id=user_id)
            if current_count > last_seen_count:
                new_events = repo.list_events(
                    limit=current_count - last_seen_count, user_id=user_id
                )
                for event in reversed(new_events):
                    yield f"data: {json.dumps(event)}\n\n"
                last_seen_count = current_count
            else:
                yield f": heartbeat\n\n"
            import asyncio

            await asyncio.sleep(2)

    return StreamingResponse(generate(), media_type="text/event-stream")


# ---------------------------------------------------------------------------
# Analysis runs / reports
# ---------------------------------------------------------------------------


@app.get("/api/reports")
async def list_reports(
    agent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    user_info: Dict[str, Any] = Depends(require_auth),
):
    runs = repo.list_analysis_runs(
        agent_id=agent_id, status=status, limit=limit, user_id=user_info["user_id"]
    )
    total = repo.get_analysis_run_count(user_id=user_info["user_id"])
    return {"reports": runs, "total": total}


# ---------------------------------------------------------------------------
# Async analysis — background processing with status polling
# ---------------------------------------------------------------------------

_running_analyses: Dict[str, Dict[str, Any]] = {}
_ANALYSIS_TTL_SECONDS = 600  # remove completed/failed entries after 10 minutes


def _schedule_eviction(run_id: str) -> None:
    """Remove a terminal analysis entry from memory after TTL expires."""
    import threading

    def _evict():
        _running_analyses.pop(run_id, None)

    threading.Timer(_ANALYSIS_TTL_SECONDS, _evict).start()


AsyncAnalysisRequest = AnalysisRequest  # same schema used by both sync and async


@app.post("/api/analysis/start", status_code=202)
async def start_analysis(
    body: AsyncAnalysisRequest, user_info: Dict[str, Any] = Depends(require_auth)
):
    """
    Kick off an LLM analysis in the background and return a run_id
    that the client can poll for status.
    """
    if not workflow_instance:
        raise HTTPException(status_code=503, detail="Analysis workflow not available")

    user_id = user_info["user_id"]
    agent_id = body.agent_id or "unknown"
    if not repo.get_agent(agent_id):
        repo.upsert_agent(agent_id, agent_id, "analysis")

    input_hash = hashlib.sha256(body.report_content.encode()).hexdigest()[:16]
    run_id = repo.create_analysis_run(agent_id, input_hash, user_id=user_id)

    _running_analyses[run_id] = {"status": "running", "phase": "initializing"}

    import threading

    def _background_analyze():
        start = time.monotonic()
        try:
            _running_analyses[run_id]["phase"] = "analyzing"
            result = workflow_instance.run_analysis(
                report_content=body.report_content,
                analysis_type=body.analysis_type,
            )
            duration_ms = int((time.monotonic() - start) * 1000)

            security_events = _extract_security_events(body.report_content)
            report = _build_report(result, agent_id, security_events, duration_ms)

            for evt in security_events:
                repo.insert_event(
                    agent_id=agent_id,
                    threat_type=evt["threat_type"],
                    severity=evt["severity"],
                    confidence=evt["confidence"],
                    message=evt["message"],
                    context=evt.get("details"),
                    detection_method="report_analysis",
                    user_id=user_id,
                )

            risk_level = report["summary"]["status"]
            repo.complete_analysis_run(run_id, risk_level, report, duration_ms)
            _running_analyses[run_id] = {
                "status": "completed",
                "phase": "done",
                "result": report,
            }
            _schedule_eviction(run_id)
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.error("Background analysis %s failed: %s", run_id, exc)
            repo.fail_analysis_run(run_id, str(exc))
            _running_analyses[run_id] = {
                "status": "failed",
                "phase": "error",
                "error": str(exc),
            }
            _schedule_eviction(run_id)

    threading.Thread(target=_background_analyze, daemon=True).start()

    return {"run_id": run_id, "status": "running", "message": "Analysis started in background"}


@app.get("/api/analysis/{run_id}/status")
async def get_analysis_status(
    run_id: str, user_info: Dict[str, Any] = Depends(require_auth)
):
    """Poll the current status of a background analysis run."""
    info = _running_analyses.get(run_id)
    if info:
        resp: Dict[str, Any] = {"run_id": run_id, "status": info["status"], "phase": info.get("phase")}
        if info["status"] == "completed":
            resp["result"] = info.get("result")
        elif info["status"] == "failed":
            resp["error"] = info.get("error")
        return resp

    # Fallback to database if not in memory (e.g. after restart)
    row = repo.get_analysis_run(run_id, user_id=user_info["user_id"])
    if row:
        result = None
        if row.get("result_json"):
            try:
                result = json.loads(row["result_json"])
            except (json.JSONDecodeError, TypeError):
                result = None
        return {
            "run_id": run_id,
            "status": row.get("status", "unknown"),
            "phase": "done" if row.get("status") == "completed" else row.get("status"),
            "result": result,
        }

    raise HTTPException(status_code=404, detail="Analysis run not found")


# ---------------------------------------------------------------------------
# Analysis endpoints (LLM-powered, synchronous)
# ---------------------------------------------------------------------------


@app.post("/analyze")
async def analyze_report(
    body: AnalysisRequest, user_info: Dict[str, Any] = Depends(require_auth)
):
    if not workflow_instance:
        raise HTTPException(status_code=503, detail="Analysis workflow not available")

    agent_id = body.agent_id or "unknown"

    # Auto-register agent
    if not repo.get_agent(agent_id):
        repo.upsert_agent(agent_id, agent_id, "analysis")

    input_hash = hashlib.sha256(body.report_content.encode()).hexdigest()[:16]
    run_id = repo.create_analysis_run(
        agent_id, input_hash, user_id=user_info["user_id"]
    )

    start = time.monotonic()
    try:
        result = workflow_instance.run_analysis(
            report_content=body.report_content,
            analysis_type=body.analysis_type,
        )
        duration_ms = int((time.monotonic() - start) * 1000)

        security_events = _extract_security_events(body.report_content)
        report = _build_report(result, agent_id, security_events, duration_ms)

        # Persist extracted events into the database
        for evt in security_events:
            repo.insert_event(
                agent_id=agent_id,
                threat_type=evt["threat_type"],
                severity=evt["severity"],
                confidence=evt["confidence"],
                message=evt["message"],
                context=evt.get("details"),
                detection_method="report_analysis",
                user_id=user_info["user_id"],
            )

        risk_level = report["summary"]["status"]
        repo.complete_analysis_run(run_id, risk_level, report, duration_ms)

        logger.info("Analysis completed for agent=%s run=%s (%dms)", agent_id, run_id, duration_ms)
        return report

    except HTTPException:
        raise
    except Exception as exc:
        repo.fail_analysis_run(run_id, str(exc))
        logger.error("Analysis failed for run=%s: %s", run_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@app.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    analysis_type: str = Form("comprehensive"),
    user_info: Dict[str, Any] = Depends(require_auth),
):
    allowed_extensions = (".txt", ".json", ".log", ".md")
    if not file.filename or not file.filename.endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )

    content = await file.read()
    try:
        report_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")

    agent_id = Path(file.filename).stem
    body = AnalysisRequest(
        report_content=report_content,
        analysis_type=analysis_type,
        agent_id=agent_id,
    )
    return await analyze_report(body, user_info)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SEVERITY_WEIGHTS = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}
_SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

_THREAT_KEYWORDS = {
    "command_injection": ["command injection"],
    "sql_injection": ["sql injection"],
    "xss": ["xss", "cross-site scripting"],
    "data_exfiltration": ["data exfiltration"],
    "privilege_escalation": ["privilege escalation"],
    "malware": ["malware"],
}

_EVENT_TRIGGERS = [
    "security event:", "threat detected", "vulnerability", "attack",
    "injection", "xss", "sql injection", "command injection",
    "data exfiltration", "privilege escalation", "malware",
    "suspicious activity", "breach", "intrusion",
]


def _extract_security_events(report_content: str) -> List[Dict[str, Any]]:
    """Parse free-text report content into structured security event dicts."""
    events: List[Dict[str, Any]] = []

    for line_num, raw_line in enumerate(report_content.split("\n"), start=1):
        line = raw_line.strip()
        lower = line.lower()

        if not any(kw in lower for kw in _EVENT_TRIGGERS):
            continue

        threat_type = "security_violation"
        for ttype, keywords in _THREAT_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                threat_type = ttype
                break

        severity = "MEDIUM"
        if "critical" in lower:
            severity = "CRITICAL"
        elif "high" in lower:
            severity = "HIGH"
        elif "low" in lower:
            severity = "LOW"

        confidence = 0.75
        match = _CONFIDENCE_RE.search(line)
        if match:
            val = float(match.group(1))
            confidence = val / 100.0 if val > 1.0 else val

        events.append(
            {
                "id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "threat_type": threat_type,
                "severity": severity,
                "confidence": round(confidence, 3),
                "message": line,
                "details": {"source": "report_analysis", "line_number": line_num},
            }
        )

    return events


def _determine_status(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "CLEAN"
    severities = {e["severity"] for e in events}
    if "CRITICAL" in severities:
        return "CRITICAL"
    if "HIGH" in severities:
        return "WARNING"
    return "CLEAN"


def _calculate_risk_score(events: List[Dict[str, Any]]) -> float:
    if not events:
        return 0.0
    total = sum(_SEVERITY_WEIGHTS.get(e["severity"], 0.5) for e in events)
    return round(min(total / len(events), 1.0), 3)


def _get_highest_severity(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "LOW"
    severities = {e["severity"] for e in events}
    for sev in reversed(_SEVERITY_ORDER):
        if sev in severities:
            return sev
    return "LOW"


def _extract_reporter_data(workflow_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the reporter agent's JSON-encoded UnifiedReport and extract all
    useful fields: prose insights, performance metrics, recommendations,
    and next actions.

    The reporter serialises the full UnifiedReport into the HumanMessage
    content, so ``workflow_result["enhanced_analysis"]`` is typically a JSON
    string containing every field the LLM produced.
    """
    empty: Dict[str, Any] = {
        "enhanced_analysis": "",
        "threat_intelligence": "",
        "recommendations": [],
        "next_actions": [],
        "performance_metrics": {},
        "key_insights": [],
    }

    raw = workflow_result.get("enhanced_analysis", "")
    if not raw or not raw.strip().startswith("{"):
        return empty

    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return empty

    if not isinstance(parsed, dict):
        return empty

    ii = parsed.get("intelligence_insights", {}) or {}
    summary = parsed.get("summary", {}) or {}
    perf = parsed.get("performance_metrics", {}) or {}

    return {
        "enhanced_analysis": ii.get("enhanced_analysis", "") or "",
        "threat_intelligence": ii.get("threat_intelligence", "") or "",
        "recommendations": parsed.get("recommendations", []) or [],
        "next_actions": summary.get("next_actions", []) or [],
        "performance_metrics": perf,
        "key_insights": summary.get("key_insights", []) or [],
    }


def _prose_or_empty(value: str) -> str:
    """Return the string only if it is actual prose, not serialised JSON."""
    if not value or not value.strip():
        return ""
    s = value.strip()
    if s.startswith(("{", "[")):
        try:
            json.loads(s)
            return ""
        except json.JSONDecodeError:
            pass
    return value


def _generate_fallback_insights(
    events: List[Dict[str, Any]],
    threat_breakdown: Dict[str, int],
    severity_dist: Dict[str, int],
    risk_score: float,
) -> tuple:
    """
    Build readable prose summaries from structured event data when the LLM
    did not produce usable narrative insights.
    """
    if not events:
        return (
            "No security events were detected during this analysis session. "
            "The monitored agent operated within expected parameters.",
            "No active threat indicators were identified. Continue routine monitoring.",
        )

    total = len(events)
    high_sev = severity_dist.get("HIGH", 0) + severity_dist.get("CRITICAL", 0)
    top_threat = max(threat_breakdown, key=threat_breakdown.get) if threat_breakdown else "unknown"
    top_count = threat_breakdown.get(top_threat, 0)

    enhanced_lines = [
        f"## Analysis Overview",
        f"The analysis identified {total} security event{'s' if total != 1 else ''} "
        f"with an overall risk score of {risk_score:.2f}.",
        "",
    ]
    if high_sev:
        enhanced_lines.append(
            f"- {high_sev} event{'s' if high_sev != 1 else ''} rated HIGH or CRITICAL severity, requiring immediate attention."
        )
    enhanced_lines.append(
        f"- Most prevalent threat: {top_threat.replace('_', ' ').title()} ({top_count} occurrence{'s' if top_count != 1 else ''})."
    )

    breakdown_items = sorted(threat_breakdown.items(), key=lambda x: x[1], reverse=True)
    if len(breakdown_items) > 1:
        enhanced_lines.append("")
        enhanced_lines.append("## Threat Breakdown")
        for ttype, count in breakdown_items:
            enhanced_lines.append(f"- {ttype.replace('_', ' ').title()}: {count} event{'s' if count != 1 else ''}")

    sev_parts = []
    for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
        if severity_dist.get(sev, 0):
            sev_parts.append(f"{severity_dist[sev]} {sev}")
    if sev_parts:
        enhanced_lines.append("")
        enhanced_lines.append("## Severity Distribution")
        enhanced_lines.append(f"- {', '.join(sev_parts)}")

    threat_intel_lines = [
        f"### Threat Landscape",
        f"The detected threats span {len(threat_breakdown)} distinct categor{'ies' if len(threat_breakdown) != 1 else 'y'}.",
        "",
    ]
    for ttype, count in breakdown_items[:3]:
        readable = ttype.replace("_", " ").title()
        threat_intel_lines.append(f"- {readable} — {count} occurrence{'s' if count != 1 else ''}. "
                                  "Review agent inputs/outputs for exploitation patterns.")

    if high_sev:
        threat_intel_lines.append("")
        threat_intel_lines.append(
            f"### Risk Assessment\n"
            f"With {high_sev} high-severity event{'s' if high_sev != 1 else ''}, "
            f"the current risk posture warrants escalation to the security team."
        )

    return "\n".join(enhanced_lines), "\n".join(threat_intel_lines)


def _generate_fallback_next_actions(
    events: List[Dict[str, Any]],
    threat_breakdown: Dict[str, int],
) -> List[str]:
    """Generate distinct, immediate next-action items from event data."""
    actions: List[str] = []

    if not events:
        return ["Continue routine security monitoring"]

    severity_set = {e["severity"] for e in events}
    if "CRITICAL" in severity_set or "HIGH" in severity_set:
        actions.append("Immediately investigate HIGH/CRITICAL severity events and isolate affected agents")

    threat_types = set(threat_breakdown.keys())
    if "sql_injection" in threat_types:
        actions.append("Audit database query construction and enforce parameterized queries")
    if "prompt_injection" in threat_types:
        actions.append("Add prompt hardening and input pre-screening before LLM calls")
    if "data_exfiltration" in threat_types:
        actions.append("Review outbound data flows and enforce URL allowlisting")
    if "xss" in threat_types:
        actions.append("Sanitize all agent outputs rendered in web contexts")
    if "command_injection" in threat_types:
        actions.append("Restrict shell/command execution and validate all command arguments")
    if "path_traversal" in threat_types:
        actions.append("Enforce path canonicalization and restrict file system access scope")

    if not actions:
        actions.append("Review detected events and apply targeted mitigations")

    actions.append("Schedule a follow-up security review within 48 hours")
    return actions[:5]


def _build_report(
    workflow_result: Dict[str, Any],
    agent_id: str,
    events: List[Dict[str, Any]],
    duration_ms: int,
) -> Dict[str, Any]:
    """Assemble the final report dict returned from /analyze."""
    threat_breakdown: Dict[str, int] = {}
    severity_dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}

    for e in events:
        threat_breakdown[e["threat_type"]] = threat_breakdown.get(e["threat_type"], 0) + 1
        severity_dist[e["severity"]] = severity_dist.get(e["severity"], 0) + 1

    risk_score = _calculate_risk_score(events)
    avg_confidence = (
        round(sum(e["confidence"] for e in events) / len(events), 3) if events else 0.0
    )
    most_common = max(threat_breakdown, key=threat_breakdown.get) if threat_breakdown else "none"

    reporter_data = _extract_reporter_data(workflow_result)

    # --- Recommendations ---------------------------------------------------
    recs = reporter_data["recommendations"] or workflow_result.get("recommendations", [])
    if isinstance(recs, str):
        recs = [recs]
    if not recs:
        recs = [
            "Review detected security events and apply mitigations",
            "Implement input validation at agent boundaries",
            "Enable continuous monitoring with the Agent Sentinel SDK",
        ]

    # --- Next actions (must differ from recommendations) -------------------
    next_actions = reporter_data["next_actions"]
    if not next_actions or next_actions == recs[:len(next_actions)]:
        next_actions = _generate_fallback_next_actions(events, threat_breakdown)

    # --- Performance metrics (merge reporter LLM output with known data) ---
    rp = reporter_data["performance_metrics"]
    perf_metrics: Dict[str, Any] = {
        "security_events_count": len(events),
        "session_duration_seconds": round(duration_ms / 1000.0, 3),
    }
    if rp.get("total_function_calls"):
        perf_metrics["total_function_calls"] = rp["total_function_calls"]
    else:
        perf_metrics["total_function_calls"] = len(events)

    if rp.get("success_rate") is not None and rp["success_rate"] != 0:
        perf_metrics["success_rate"] = rp["success_rate"]
    else:
        safe_count = sum(1 for e in events if e.get("severity") in ("LOW", "MEDIUM"))
        perf_metrics["success_rate"] = round(
            (safe_count / len(events) * 100) if events else 100.0, 1
        )

    # --- Intelligence insights ---------------------------------------------
    enhanced_prose = _prose_or_empty(reporter_data["enhanced_analysis"])
    threat_intel_prose = _prose_or_empty(reporter_data["threat_intelligence"])

    if not enhanced_prose or not threat_intel_prose:
        fb_enhanced, fb_threat = _generate_fallback_insights(
            events, threat_breakdown, severity_dist, risk_score,
        )
        if not enhanced_prose:
            enhanced_prose = fb_enhanced
        if not threat_intel_prose:
            threat_intel_prose = fb_threat

    # --- Key insights ------------------------------------------------------
    key_insights = reporter_data["key_insights"]
    if not key_insights:
        key_insights = _extract_key_insights(enhanced_prose)

    now = datetime.now(timezone.utc).isoformat()
    return {
        "report_id": f"AS-INTEL-{uuid.uuid4().hex[:8]}",
        "agent_id": agent_id,
        "start_time": now,
        "end_time": now,
        "analysis_type": "comprehensive",
        "workflow_execution_time": duration_ms / 1000.0,
        "security_events": events,
        "performance_metrics": perf_metrics,
        "threat_analysis": {
            "total_threats": len(events),
            "threat_breakdown": threat_breakdown,
            "severity_distribution": severity_dist,
            "confidence_analysis": {
                "average_confidence": avg_confidence,
                "high_confidence_threats": len([e for e in events if e["confidence"] > 0.8]),
            },
            "risk_score": risk_score,
            "most_common_threat": most_common,
            "highest_severity": _get_highest_severity(events),
        },
        "recommendations": recs,
        "summary": {
            "status": _determine_status(events),
            "risk_score": risk_score,
            "threats_detected": len(events),
            "performance_score": 85.0,
            "key_insights": key_insights,
            "next_actions": next_actions,
        },
        "intelligence_insights": {
            "enhanced_analysis": enhanced_prose,
            "threat_intelligence": threat_intel_prose,
        },
    }


def _extract_key_insights(prose: str) -> List[str]:
    """Pull key insight bullet points from prose text."""
    insights: List[str] = []
    if not prose:
        return ["Security analysis completed", "Review events for details"]
    for line in prose.split("\n"):
        stripped = line.strip().lstrip("- *#")
        if stripped and len(stripped) > 20 and not stripped.startswith("{"):
            insights.append(stripped)
        if len(insights) >= 5:
            break
    if not insights:
        insights = ["Security analysis completed", "Review events for details"]
    return insights[:5]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),
        log_level="info",
        reload=os.getenv("SENTINEL_ENV", "development") == "development",
    )
