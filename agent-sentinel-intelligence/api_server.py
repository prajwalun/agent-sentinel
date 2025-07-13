#!/usr/bin/env python3
"""
Enhanced Agent Sentinel Intelligence API Server with API Key Authentication.
"""

import os
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import json
from pydantic import ValidationError

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from workflow import SecurityAnalysisWorkflow, create_workflow_from_env
from models.config import IntelligenceConfig
from utils.logging_config import setup_enterprise_logging

# Setup logging
setup_enterprise_logging()
logger = logging.getLogger(__name__)

# Global workflow instance
workflow_instance: Optional[SecurityAnalysisWorkflow] = None

# API Key Management
API_KEYS_DB = {}  # In production, use a proper database
RATE_LIMITS = {}  # Track API usage

class APIKeyManager:
    """Manages API keys for authentication"""
    
    @staticmethod
    def generate_api_key(user_id: str, description: str = "") -> str:
        """Generate a new API key"""
        key_id = str(uuid.uuid4())
        api_key = f"as_{key_id.replace('-', '')[:24]}"
        
        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        API_KEYS_DB[key_hash] = {
            "user_id": user_id,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "is_active": True
        }
        
        logger.info(f"Generated API key for user: {user_id}")
        return api_key
    
    @staticmethod
    def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return user info"""
        if not api_key or not api_key.startswith("as_"):
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash in API_KEYS_DB:
            key_info = API_KEYS_DB[key_hash]
            
            if key_info["is_active"]:
                # Update usage
                key_info["last_used"] = datetime.utcnow().isoformat()
                key_info["usage_count"] += 1
                
                return key_info
        
        return None
    
    @staticmethod
    def check_rate_limit(user_id: str, limit_per_hour: int = 100) -> bool:
        """Check if user is within rate limits"""
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        if user_id not in RATE_LIMITS:
            RATE_LIMITS[user_id] = []
        
        # Clean old requests
        RATE_LIMITS[user_id] = [
            timestamp for timestamp in RATE_LIMITS[user_id]
            if timestamp > hour_ago
        ]
        
        # Check limit
        if len(RATE_LIMITS[user_id]) >= limit_per_hour:
            return False
        
        # Add current request
        RATE_LIMITS[user_id].append(now)
        return True

# Initialize some demo API keys
demo_keys = {
    "demo-user": APIKeyManager.generate_api_key("demo-user", "Demo user key"),
    "sdk-integration": APIKeyManager.generate_api_key("sdk-integration", "SDK integration key")
}

# Authentication dependency
security = HTTPBearer()

async def authenticate_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Authenticate API key from Authorization header"""
    api_key = credentials.credentials
    
    user_info = APIKeyManager.validate_api_key(api_key)
    if not user_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Check rate limit
    if not APIKeyManager.check_rate_limit(user_info["user_id"]):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 100 requests per hour."
        )
    
    return user_info

# FastAPI app
app = FastAPI(
    title="Agent Sentinel Intelligence API",
    description="AI-powered security analysis for agent monitoring",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SecurityEvent(BaseModel):
    """Security event model matching dashboard expectations"""
    id: str
    timestamp: str
    threat_type: str
    severity: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    message: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    details: Dict[str, Any] = Field(default_factory=dict)

class PerformanceMetrics(BaseModel):
    """Performance metrics model"""
    total_function_calls: int = 0
    average_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    success_rate: float = 1.0
    error_rate: float = 0.0
    security_events_count: int = 0
    session_duration_seconds: float = 0.0
    throughput_requests_per_minute: float = 0.0

class ThreatAnalysis(BaseModel):
    """Threat analysis model"""
    total_threats: int
    threat_breakdown: Dict[str, int]
    severity_distribution: Dict[str, int]
    confidence_analysis: Dict[str, Any]
    risk_score: float
    most_common_threat: str
    highest_severity: str

class ReportSummary(BaseModel):
    """Report summary model"""
    status: str = Field(..., pattern="^(CLEAN|WARNING|CRITICAL)$")
    risk_score: float
    threats_detected: int
    performance_score: float = 85.0
    key_insights: List[str]
    next_actions: List[str]

class EnhancedIntelligenceReport(BaseModel):
    """Enhanced intelligence report model matching dashboard expectations"""
    agent_id: str
    start_time: str
    end_time: str
    session_logs: List[Dict[str, Any]] = Field(default_factory=list)
    security_events: List[SecurityEvent]
    performance_metrics: PerformanceMetrics
    threat_analysis: ThreatAnalysis
    recommendations: List[str]
    summary: ReportSummary
    
    # Additional intelligence fields
    report_id: str
    analysis_type: str
    workflow_execution_time: float
    intelligence_insights: Dict[str, Any] = Field(default_factory=dict)

class AnalysisRequest(BaseModel):
    """Request model for analysis"""
    report_content: str
    analysis_type: str = "comprehensive"
    agent_id: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the workflow on startup"""
    global workflow_instance
    try:
        setup_enterprise_logging()
        workflow_instance = create_workflow_from_env()
        logger.info("✅ Agent Sentinel Intelligence API started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize workflow: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "workflow_ready": workflow_instance is not None
    }

@app.post("/api-keys/generate")
async def generate_api_key(user_id: str, description: str = ""):
    """Generate a new API key for a user"""
    try:
        api_key = APIKeyManager.generate_api_key(user_id, description)
        return {
            "api_key": api_key,
            "user_id": user_id,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "message": "API key generated successfully"
        }
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate API key")

@app.get("/api-keys/demo")
async def get_demo_keys():
    """Get demo API keys for testing"""
    return {
        "demo_keys": demo_keys,
        "note": "These are demo keys for testing. In production, use /api-keys/generate"
    }

@app.get("/api-keys/validate")
async def validate_current_key(user_info: Dict[str, Any] = Depends(authenticate_api_key)):
    """Validate the current API key and return usage info"""
    return {
        "valid": True,
        "user_id": user_info["user_id"],
        "description": user_info["description"],
        "usage_count": user_info["usage_count"],
        "last_used": user_info["last_used"],
        "created_at": user_info["created_at"]
    }

@app.post("/analyze", response_model=EnhancedIntelligenceReport)
async def analyze_report(request: AnalysisRequest, user_info: Dict[str, Any] = Depends(authenticate_api_key)):
    """
    Analyze a security report and return enhanced intelligence insights
    """
    try:
        # Remove UnifiedReport skip logic. Always run the intelligence workflow (LLM)
        if not workflow_instance:
            raise HTTPException(status_code=500, detail="Workflow not initialized")
        logger.info(f"Starting analysis for agent: {request.agent_id or 'unknown'}")
        start_time = datetime.utcnow()
        result = workflow_instance.run_analysis(
            report_content=request.report_content,
            analysis_type=request.analysis_type
        )
        end_time = datetime.utcnow()
        enhanced_report = _transform_to_dashboard_format(
            result, 
            request.agent_id or "unknown",
            start_time,
            end_time,
            request.report_content
        )
        logger.info(f"✅ Analysis completed for agent: {request.agent_id}")
        return enhanced_report
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/file")
async def analyze_file(file: UploadFile = File(...), analysis_type: str = "comprehensive"):
    """
    Analyze a security report file and return enhanced intelligence insights
    """
    try:
        if not file.filename.endswith(('.txt', '.json', '.log')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        content = await file.read()
        report_content = content.decode('utf-8')
        
        request = AnalysisRequest(
            report_content=report_content,
            analysis_type=analysis_type,
            agent_id=file.filename.split('.')[0]
        )
        
        return await analyze_report(request)
        
    except Exception as e:
        logger.error(f"❌ File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

def _transform_to_dashboard_format(
    workflow_result: Dict[str, Any],
    agent_id: str,
    start_time: datetime,
    end_time: datetime,
    original_report: str
) -> EnhancedIntelligenceReport:
    """
    Transform workflow result into dashboard-compatible format
    """
    # Parse the original report to extract security events
    security_events = _extract_security_events(original_report)
    
    # Create threat analysis
    threat_analysis = ThreatAnalysis(
        total_threats=len(security_events),
        threat_breakdown=_calculate_threat_breakdown(security_events),
        severity_distribution=_calculate_severity_distribution(security_events),
        confidence_analysis={
            "average_confidence": sum(e.confidence for e in security_events) / len(security_events) if security_events else 0.0,
            "high_confidence_threats": len([e for e in security_events if e.confidence > 0.8]),
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0}
        },
        risk_score=_calculate_risk_score(security_events),
        most_common_threat=_get_most_common_threat(security_events),
        highest_severity=_get_highest_severity(security_events)
    )
    
    # Create performance metrics
    performance_metrics = PerformanceMetrics(
        security_events_count=len(security_events),
        session_duration_seconds=(end_time - start_time).total_seconds()
    )
    
    # Create summary
    summary = ReportSummary(
        status=_determine_status(security_events),
        risk_score=threat_analysis.risk_score,
        threats_detected=len(security_events),
        key_insights=_extract_key_insights(workflow_result),
        next_actions=_extract_next_actions(workflow_result)
    )
    
    return EnhancedIntelligenceReport(
        agent_id=agent_id,
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        security_events=security_events,
        performance_metrics=performance_metrics,
        threat_analysis=threat_analysis,
        recommendations=_extract_recommendations(workflow_result),
        summary=summary,
        report_id=f"AS-INTEL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        analysis_type="comprehensive",
        workflow_execution_time=(end_time - start_time).total_seconds(),
        intelligence_insights={
            "enhanced_analysis": workflow_result.get("enhanced_analysis", ""),
            "threat_intelligence": workflow_result.get("threat_intelligence", ""),
            "recommendations": workflow_result.get("recommendations", [])
        }
    )

def _extract_security_events(report_content: str) -> List[SecurityEvent]:
    """Extract security events from the original report"""
    events = []
    
    # Parse the report content to find security events
    lines = report_content.split('\n')
    current_event = None
    
    for i, line in enumerate(lines):
        if "FINDING #" in line:
            if current_event:
                events.append(current_event)
            
            # Extract event details
            event_id = f"event_{len(events) + 1}"
            timestamp = datetime.utcnow().isoformat()
            
            # Look for threat type and severity in next lines
            threat_type = "Unknown"
            severity = "MEDIUM"
            message = "Security event detected"
            
            for j in range(i + 1, min(i + 10, len(lines))):
                if "Threats:" in lines[j]:
                    threat_type = lines[j].split("Threats:")[1].strip()
                    severity = "HIGH" if "XSS" in threat_type or "injection" in threat_type else "MEDIUM"
                    message = f"Threat detected: {threat_type}"
                    break
            
            current_event = SecurityEvent(
                id=event_id,
                timestamp=timestamp,
                threat_type=threat_type,
                severity=severity,
                message=message,
                confidence=0.85,
                details={"source": "Security Report"}
            )
    
    if current_event:
        events.append(current_event)
    
    return events

def _calculate_threat_breakdown(events: List[SecurityEvent]) -> Dict[str, int]:
    """Calculate threat breakdown by type"""
    breakdown = {}
    for event in events:
        threat_type = event.threat_type
        breakdown[threat_type] = breakdown.get(threat_type, 0) + 1
    return breakdown

def _calculate_severity_distribution(events: List[SecurityEvent]) -> Dict[str, int]:
    """Calculate severity distribution"""
    distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for event in events:
        distribution[event.severity] = distribution.get(event.severity, 0) + 1
    return distribution

def _calculate_risk_score(events: List[SecurityEvent]) -> float:
    """Calculate overall risk score"""
    if not events:
        return 0.0
    
    severity_weights = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}
    total_score = sum(severity_weights.get(event.severity, 0.5) for event in events)
    return min(total_score / len(events), 1.0)

def _get_most_common_threat(events: List[SecurityEvent]) -> str:
    """Get the most common threat type"""
    if not events:
        return "None"
    
    threat_counts = {}
    for event in events:
        threat_counts[event.threat_type] = threat_counts.get(event.threat_type, 0) + 1
    
    if not threat_counts:
        return "None"
    
    return max(threat_counts, key=threat_counts.get)

def _get_highest_severity(events: List[SecurityEvent]) -> str:
    """Get the highest severity level"""
    if not events:
        return "LOW"
    
    severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    severities = [event.severity for event in events]
    
    for severity in reversed(severity_order):
        if severity in severities:
            return severity
    
    return "LOW"

def _determine_status(events: List[SecurityEvent]) -> str:
    """Determine overall status"""
    if not events:
        return "CLEAN"
    
    has_critical = any(event.severity == "CRITICAL" for event in events)
    has_high = any(event.severity == "HIGH" for event in events)
    
    if has_critical:
        return "CRITICAL"
    elif has_high:
        return "WARNING"
    else:
        return "WARNING"

def _extract_key_insights(workflow_result: Dict[str, Any]) -> List[str]:
    """Extract key insights from workflow result"""
    insights = []
    
    # Extract insights from the enhanced analysis
    if "enhanced_analysis" in workflow_result:
        analysis = workflow_result["enhanced_analysis"]
        if "Executive Summary" in analysis:
            insights.append("Multiple high-severity threats detected requiring immediate attention")
        if "Ransomware" in analysis:
            insights.append("Ransomware attack detected with potential for data encryption")
        if "Phishing" in analysis:
            insights.append("Phishing campaign targeting employee credentials")
    
    if not insights:
        insights = ["Security analysis completed", "Threat patterns identified", "Recommendations generated"]
    
    return insights[:5]  # Limit to 5 insights

def _extract_next_actions(workflow_result: Dict[str, Any]) -> List[str]:
    """Extract next actions from workflow result"""
    actions = []
    
    # Extract actions from recommendations
    if "recommendations" in workflow_result:
        recommendations = workflow_result["recommendations"]
        if isinstance(recommendations, list):
            actions.extend(recommendations[:3])  # Top 3 recommendations
    
    if not actions:
        actions = [
            "Review security events and implement immediate mitigations",
            "Conduct security awareness training for employees",
            "Update security policies and procedures"
        ]
    
    return actions[:3]  # Limit to 3 actions

def _extract_recommendations(workflow_result: Dict[str, Any]) -> List[str]:
    """Extract recommendations from workflow result"""
    recommendations = []
    
    if "recommendations" in workflow_result:
        recs = workflow_result["recommendations"]
        if isinstance(recs, list):
            recommendations.extend(recs)
    
    if not recommendations:
        recommendations = [
            "Implement multi-factor authentication across all systems",
            "Conduct regular security awareness training",
            "Deploy endpoint detection and response solutions",
            "Establish incident response procedures",
            "Regular security assessments and penetration testing"
        ]
    
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info") 