"""
Agent Sentinel Intelligence — API Server

FastAPI application that provides:
  - Bearer-token authentication backed by SQLite
  - Security report analysis via LangGraph multi-agent workflow
  - CRUD endpoints for agents, events, and analysis runs
  - Dashboard statistics and a simple metrics endpoint
  - Server-Sent Events stream for live event updates
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

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
        logger.info("LangGraph workflow initialised")
    except Exception:
        logger.warning("Workflow init failed — analysis endpoints will return 503", exc_info=True)

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


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------
_bearer = HTTPBearer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Dict[str, Any]:
    """Validate Bearer token against the api_keys table."""
    global _request_count
    _request_count += 1

    key_record = repo.validate_api_key(credentials.credentials)
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    if not repo.check_rate_limit(key_record["user_id"]):
        raise HTTPException(status_code=429, detail="Rate limit exceeded (100 req/hr)")

    return key_record


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
# API key management (admin-gated)
# ---------------------------------------------------------------------------


@app.post("/api/keys/generate")
async def generate_api_key(body: KeyGenerateRequest, _: None = Depends(require_admin)):
    raw_key = repo.create_api_key(body.user_id, body.description)
    return {
        "api_key": raw_key,
        "user_id": body.user_id,
        "message": "Store this key securely — it will not be shown again.",
    }


@app.get("/api/keys/validate")
async def validate_current_key(user_info: Dict[str, Any] = Depends(require_auth)):
    return {
        "valid": True,
        "user_id": user_info["user_id"],
        "call_count": user_info["call_count"],
        "created_at": user_info["created_at"],
    }


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------


@app.get("/api/dashboard/stats")
async def dashboard_stats(_: Dict[str, Any] = Depends(require_auth)):
    return repo.get_dashboard_stats()


# ---------------------------------------------------------------------------
# Agents CRUD
# ---------------------------------------------------------------------------


@app.get("/api/agents")
async def list_agents(
    status: Optional[str] = Query(None), _: Dict[str, Any] = Depends(require_auth)
):
    agents = repo.list_agents(status=status)
    # Enrich with event counts
    for agent in agents:
        agent["event_count"] = repo.get_event_count(agent_id=agent["id"])
    return {"agents": agents, "total": len(agents)}


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
    _: Dict[str, Any] = Depends(require_auth),
):
    events = repo.list_events(
        agent_id=agent_id,
        severity=severity,
        threat_type=threat_type,
        since=since,
        limit=limit,
        offset=offset,
    )
    total = repo.get_event_count(agent_id=agent_id, severity=severity, since=since)
    return {"events": events, "total": total, "limit": limit, "offset": offset}


@app.post("/api/events", status_code=201)
async def create_event(body: EventCreateRequest, _: Dict[str, Any] = Depends(require_auth)):
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
    )
    return event


@app.get("/api/events/stream")
async def event_stream(request: Request):
    """
    Server-Sent Events endpoint.  Pushes new security events to
    connected clients every 2 seconds.
    """

    async def generate() -> AsyncGenerator[str, None]:
        last_seen_count = repo.get_event_count()
        while True:
            if await request.is_disconnected():
                break
            current_count = repo.get_event_count()
            if current_count > last_seen_count:
                new_events = repo.list_events(limit=current_count - last_seen_count)
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
    _: Dict[str, Any] = Depends(require_auth),
):
    runs = repo.list_analysis_runs(agent_id=agent_id, status=status, limit=limit)
    return {"reports": runs, "total": len(runs)}


# ---------------------------------------------------------------------------
# Analysis endpoints (LLM-powered)
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
    run_id = repo.create_analysis_run(agent_id, input_hash)

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

    # Pull recommendations from workflow or use sensible defaults
    recs = workflow_result.get("recommendations", [])
    if isinstance(recs, str):
        recs = [recs]
    if not recs:
        recs = [
            "Review detected security events and apply mitigations",
            "Implement input validation at agent boundaries",
            "Enable continuous monitoring with the Agent Sentinel SDK",
        ]

    now = datetime.now(timezone.utc).isoformat()
    return {
        "report_id": f"AS-INTEL-{uuid.uuid4().hex[:8]}",
        "agent_id": agent_id,
        "start_time": now,
        "end_time": now,
        "analysis_type": "comprehensive",
        "workflow_execution_time": duration_ms / 1000.0,
        "security_events": events,
        "performance_metrics": {
            "security_events_count": len(events),
            "session_duration_seconds": duration_ms / 1000.0,
        },
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
            "key_insights": _extract_insights(workflow_result),
            "next_actions": recs[:3],
        },
        "intelligence_insights": {
            "enhanced_analysis": workflow_result.get("enhanced_analysis", ""),
            "threat_intelligence": workflow_result.get("threat_intelligence", ""),
        },
    }


def _extract_insights(workflow_result: Dict[str, Any]) -> List[str]:
    """Pull key insights from the LLM workflow output."""
    insights: List[str] = []
    analysis = workflow_result.get("enhanced_analysis", "")
    if analysis:
        for line in analysis.split("\n"):
            stripped = line.strip().lstrip("- *")
            if stripped and len(stripped) > 20:
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
