"""
Report generator agent.

Produces structured security reports with executive summary, threat
breakdown, recommendations, and next actions as JSON.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage
# Command import removed - using simpler approach
from models.state import AgentState

from services.llm_service import LLMService
from services.tracing_service import TracingService

logger = logging.getLogger(__name__)


class ReportSection:
    """Structured report section."""
    
    def __init__(self, title: str, content: str, priority: str = "normal"):
        self.title = title
        self.content = content
        self.priority = priority


class ReportFormatter:
    """Formats raw analysis output into structured report sections."""
    
    def __init__(self):
        self.sections = []
        self.metadata = {}
    
    def add_section(self, section: ReportSection):
        """Add a section to the report."""
        self.sections.append(section)
    
    def set_metadata(self, metadata: Dict[str, Any]):
        """Set report metadata."""
        self.metadata = metadata
    
    def generate_report(self) -> str:
        """Generate the complete report."""
        report = []
        
        # Header
        report.append("# AGENT SENTINEL ENHANCED SECURITY INTELLIGENCE REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Metadata
        if self.metadata:
            report.append("## REPORT METADATA")
            for key, value in self.metadata.items():
                report.append(f"**{key.replace('_', ' ').title()}**: {value}")
            report.append("")
        
        # Executive Summary (always first)
        executive_section = next((s for s in self.sections if "executive" in s.title.lower()), None)
        if executive_section:
            report.append(f"## {executive_section.title.upper()}")
            report.append(executive_section.content)
            report.append("")
        
        # Other sections
        for section in self.sections:
            if "executive" not in section.title.lower():
                report.append(f"## {section.title.upper()}")
                report.append(section.content)
                report.append("")
        
        return "\n".join(report)


class ReportGeneratorAgent:
    """Generates structured security intelligence reports."""
    
    def __init__(self, llm_service: LLMService, tracing_service: TracingService):
        """
        Initialize the report generator agent.
        
        Args:
            llm_service: LLM service for report generation
            tracing_service: Tracing service for monitoring
        """
        self.llm_service = llm_service
        self.tracing_service = tracing_service
        
        self.system_prompt = """
        You are an Enterprise Security Intelligence Report Generator. Your role is to create 
        comprehensive, professional security reports that combine technical analysis with 
        executive-level insights and actionable recommendations.

        **Report Structure Requirements:**
        1. **Executive Summary** - High-level overview for C-level executives
        2. **Threat Analysis** - Detailed technical analysis of all threats
        3. **Risk Assessment** - Severity levels, impact analysis, and risk scoring
        4. **Attack Patterns** - MITRE ATT&CK framework alignment and technique analysis
        5. **Agent Behavior Analysis** - Malicious agent capabilities and behaviors
        6. **Timeline Analysis** - Chronological attack sequence and event correlation
        7. **Threat Intelligence** - Additional context from research (if available)
        8. **Recommendations** - Prioritized, actionable mitigation steps
        9. **Future Prevention** - Long-term security improvements and best practices

        **Report Guidelines:**
        - Use clear, professional language suitable for both technical and executive audiences
        - Prioritize threats by severity and potential impact
        - Provide specific, actionable recommendations with priority levels
        - Include relevant CVE information, attack patterns, and mitigation strategies
        - Use markdown formatting for better readability and structure
        - Include executive summary that non-technical stakeholders can understand
        - Provide technical details for security teams and incident responders

        **Priority Levels for Recommendations:**
        - **Critical Priority**: Immediate action required (0-4 hours)
        - **High Priority**: Action within 24 hours
        - **Medium Priority**: Action within 1 week
        - **Low Priority**: Ongoing improvements and best practices

        **Formatting Standards:**
        - Use clear section headers with markdown formatting
        - Include bullet points and numbered lists for readability
        - Use bold text for emphasis on key findings
        - Include code blocks for technical details when appropriate
        - Use tables for structured data presentation

        Create a report that is comprehensive, actionable, and professional for enterprise use.
        """
    
    def execute(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the report generation.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dict with messages and next agent
        """
        try:
            # Collect all workflow content
            workflow_content = self._collect_workflow_content(state.get("messages", []))
            if not workflow_content:
                logger.warning("⚠️  No workflow content found for report generation")
                return self._fallback_to_validator("No content available for report generation")
            
            report = self._generate_structured_report(workflow_content)
            
            # Validate report quality
            if not report or (isinstance(report, dict) and len(json.dumps(report)) < 100):
                logger.error("❌ Generated report is too short or empty")
                return self._fallback_to_validator("Report generation failed - insufficient content")
            
            # Log report generation
            logger.info(f"Security report generated - {len(report)} characters")
            
            # Trace the report generation
            if self.tracing_service.is_enabled():
                self.tracing_service.log_workflow_step(
                    step_name="report_generation",
                    content_length=len(report),
                    status="completed"
                )
            
            print(f"--- Workflow Transition: Report Generator → Validator ---")
            
            return {
                "messages": [
                    HumanMessage(content=json.dumps(report, indent=2), name="reporter")
                ],
                "next": "validator"
            }
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            return self._fallback_to_validator(f"Report generation failed: {e}")
    
    def _collect_workflow_content(self, messages: list) -> str:
        """
        Collect and format all workflow content for report generation.
        
        Args:
            messages: List of workflow messages
            
        Returns:
            Formatted content string
        """
        content_sections = []
        
        for message in messages:
            if not hasattr(message, 'name') or not isinstance(message.name, str):
                continue
            if not hasattr(message, 'content') or not message.content:
                continue
            
            agent_name = message.name.upper()
            content = message.content
            
            if not isinstance(content, str) or not content.strip():
                continue
            
            content_sections.append(f"**{agent_name} ANALYSIS:**")
            content_sections.append(content)
            content_sections.append("")
        
        return "\n".join(content_sections)
    
    def _generate_structured_report(self, workflow_content: str) -> dict:
        """
        Generate comprehensive security report as structured JSON.
        
        Args:
            workflow_content: Content from all workflow agents
        
        Returns:
            Complete security report as dict
        """
        import re, json
        # UnifiedReport schema for the LLM
        unified_report_schema = '''
{
  "agent_id": "...",
  "start_time": "...",
  "end_time": "...",
  "session_logs": [ { "timestamp": "...", "level": "...", "agent_id": "...", "message": "..." } ],
  "security_events": [ { "id": "...", "timestamp": "...", "threat_type": "...", "severity": "LOW|MEDIUM|HIGH|CRITICAL", "message": "...", "confidence": 0.0, "details": { } } ],
  "performance_metrics": {
    "total_function_calls": 0,
    "average_response_time_ms": 0,
    "memory_usage_mb": 0,
    "cpu_usage_percent": 0,
    "success_rate": 0,
    "error_rate": 0,
    "security_events_count": 0,
    "session_duration_seconds": 0,
    "throughput_requests_per_minute": 0
  },
  "threat_analysis": {
    "total_threats": 0,
    "threat_breakdown": { },
    "severity_distribution": { },
    "confidence_analysis": {
      "average_confidence": 0,
      "high_confidence_threats": 0,
      "confidence_distribution": { }
    },
    "risk_score": 0,
    "most_common_threat": "",
    "highest_severity": ""
  },
  "recommendations": [ "..." ],
  "summary": {
    "status": "CLEAN|WARNING|CRITICAL",
    "risk_score": 0,
    "threats_detected": 0,
    "performance_score": 0,
    "key_insights": [ "..." ],
    "next_actions": [ "..." ]
  },
  "report_id": "...",
  "analysis_type": "...",
  "workflow_execution_time": 0,
  "intelligence_insights": {
    "enhanced_analysis": "...",
    "threat_intelligence": "...",
    "recommendations": [ "..." ]
  }
}
'''
        # LLM prompt
        sdk_sample_json = '''
{
  "agent_id": "test_agent",
  "report_id": "threat_report_test_agent_20250713_121254",
  "generated_at": "2025-07-13 19:12:54.984460+00:00",
  "time_range": {
    "start": "2025-07-13 19:12:54.984404+00:00",
    "end": "2025-07-13 19:12:54.984404+00:00"
  },
  "threat_summary": {
    "total_threats": 3,
    "threat_level": "MEDIUM",
    "threat_breakdown": {
      "command_injection": 1,
      "data_exfiltration": 1,
      "privilege_escalation": 1
    },
    "severity_breakdown": {
      "HIGH": 2,
      "MEDIUM": 1
    },
    "most_common_threat": "command_injection",
    "highest_severity": "HIGH",
    "time_distribution": {
      "19": 3
    }
  },
  "security_events": [
    "SecurityEvent(command_injection, HIGH, 0.95)",
    "SecurityEvent(data_exfiltration, HIGH, 0.88)",
    "SecurityEvent(privilege_escalation, MEDIUM, 0.75)"
  ],
  "risk_assessment": {
    "overall_risk_score": 2.33,
    "risk_level": "MEDIUM",
    "risk_factors": [
      "High confidence threat: command_injection",
      "High severity data_exfiltration detected",
      "High severity command_injection detected"
    ],
    "trend_analysis": "STABLE",
    "risk_distribution": {
      "low": 1,
      "medium": 2,
      "high": 0
    }
  },
  "threat_analysis": {
    "threat_patterns": {
      "command_injection": {
        "count": 1,
        "severities": [
          "HIGH"
        ],
        "confidences": [
          0.95
        ],
        "timestamps": [
          "2025-07-13T19:12:54.984349+00:00"
        ]
      },
      "data_exfiltration": {
        "count": 1,
        "severities": [
          "HIGH"
        ],
        "confidences": [
          0.88
        ],
        "timestamps": [
          "2025-07-13T19:12:54.984356+00:00"
        ]
      },
      "privilege_escalation": {
        "count": 1,
        "severities": [
          "MEDIUM"
        ],
        "confidences": [
          0.75
        ],
        "timestamps": [
          "2025-07-13T19:12:54.984359+00:00"
        ]
      }
    },
    "attack_vectors": {
      "Command Injection": 1,
      "Data Exfiltration": 1,
      "Privilege Escalation": 1
    },
    "vulnerability_analysis": {
      "Input Validation": 1,
      "Data Access Control": 1,
      "Permission Management": 1
    },
    "threat_intelligence": {
      "known_threats": 2,
      "novel_threats": 0,
      "threat_sources": [
        "Data Access Abuse",
        "Malicious Input",
        "Permission Exploitation"
      ]
    }
  },
  "recommendations": [
    "Implement data loss prevention (DLP) controls and monitor data access patterns.",
    "Strengthen input validation and implement command execution restrictions.",
    "Review and restrict agent permissions. Implement principle of least privilege.",
    "Regularly review and update security policies and monitoring rules.",
    "Implement comprehensive logging and audit trails for all agent activities.",
    "Consider integrating with external threat intelligence feeds for enhanced detection."
  ],
  "compliance_check": {
    "overall_compliance": "COMPLIANT",
    "standards": {
      "data_protection": "NON_COMPLIANT",
      "access_control": "NON_COMPLIANT",
      "audit_logging": "COMPLIANT",
      "incident_response": "COMPLIANT"
    },
    "violations": [
      "Data exfiltration attempts detected",
      "Privilege escalation attempts detected"
    ],
    "recommendations": [
      "Implement immediate remediation for detected violations",
      "Review and update security controls",
      "Conduct security awareness training"
    ]
  },
  "executive_summary": "Security monitoring for agent 'test_agent' detected 3 security events with an overall risk level of MEDIUM (score: 2.33). High severity events: 2. The system is operating within acceptable security parameters."
}
'''
        unified_report_sample = '''
{
  "agent_id": "AGT-123456",
  "start_time": "2025-07-13T10:00:00Z",
  "end_time": "2025-07-13T10:30:00Z",
  "session_logs": [
    {"timestamp": "2025-07-13T10:01:00Z", "level": "INFO", "agent_id": "AGT-123456", "message": "Agent started monitoring."},
    {"timestamp": "2025-07-13T10:05:00Z", "level": "WARNING", "agent_id": "AGT-123456", "message": "Suspicious file access detected."}
  ],
  "security_events": [
    {"id": "SE-1", "timestamp": "2025-07-13T10:05:00Z", "threat_type": "File Access", "severity": "HIGH", "message": "Unauthorized file access attempt.", "confidence": 0.95, "details": {"file": "/etc/passwd"}},
    {"id": "SE-2", "timestamp": "2025-07-13T10:10:00Z", "threat_type": "Network", "severity": "MEDIUM", "message": "Unusual outbound connection.", "confidence": 0.85, "details": {"ip": "192.168.1.100"}}
  ],
  "performance_metrics": {
    "total_function_calls": 1200,
    "average_response_time_ms": 120,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 45,
    "success_rate": 99.2,
    "error_rate": 0.8,
    "security_events_count": 2,
    "session_duration_seconds": 1800,
    "throughput_requests_per_minute": 40
  },
  "threat_analysis": {
    "total_threats": 2,
    "threat_breakdown": {"File Access": 1, "Network": 1},
    "severity_distribution": {"HIGH": 1, "MEDIUM": 1, "LOW": 0, "CRITICAL": 0},
    "confidence_analysis": {"average_confidence": 0.9, "high_confidence_threats": 2, "confidence_distribution": {"high": 2}},
    "risk_score": 0.72,
    "most_common_threat": "File Access",
    "highest_severity": "HIGH"
  },
  "recommendations": [
    "Implement stricter file access controls.",
    "Monitor outbound network connections.",
    "Review agent permissions."
  ],
  "summary": {
    "status": "WARNING",
    "risk_score": 0.72,
    "threats_detected": 2,
    "performance_score": 88,
    "key_insights": [
      "Multiple high-severity threats detected.",
      "Agent attempted unauthorized file access.",
      "Unusual network activity observed."
    ],
    "next_actions": [
      "Isolate affected agent.",
      "Conduct forensic analysis.",
      "Update security policies."
    ]
  },
  "report_id": "AS-INTEL-20250713-100000",
  "analysis_type": "comprehensive",
  "workflow_execution_time": 34,
  "intelligence_insights": {
    "enhanced_analysis": "## Executive Summary\nThe agent exhibited suspicious behavior, including unauthorized file access and unusual network activity.\n\n## Threat Analysis\n- File Access: High severity, targeted /etc/passwd.\n- Network: Medium severity, outbound connection to unknown IP.\n\n## Recommendations\n- Implement stricter file access controls.\n- Monitor outbound network connections.\n- Review agent permissions.",
    "threat_intelligence": "### Threat Actor Profile\n- Likely motivated by data exfiltration.\n- Techniques align with MITRE ATT&CK T1005, T1041.\n\n### Vulnerability Analysis\n- Exploited weak file permissions.\n- Lack of network monitoring enabled outbound connection.",
    "recommendations": [
      "Isolate affected agent.",
      "Conduct forensic analysis.",
      "Update security policies."
    ]
  }
}
'''
        user_prompt = f"""
You are an enterprise security analyst specializing in Agent Sentinel security reports.

**Your Task:** Analyze the provided Agent Sentinel security report (see the JSON input sample below) and generate a complete UnifiedReport JSON that accurately maps all fields from the input report.

**Input Analysis:** The input contains an Agent Sentinel security report with:
- agent_id, report_id, generated_at timestamps
- threat_summary with total_threats, threat_level, breakdowns
- security_events array with threat types, severities, confidences (as strings)
- risk_assessment with risk scores and factors
- threat_analysis with patterns, attack vectors, vulnerability analysis
- recommendations array
- compliance_check with standards and violations
- executive_summary

**Output Requirements:**
- If the input is already a valid UnifiedReport JSON (matches the schema below), return it unchanged.
- Otherwise, generate a complete JSON object matching the UnifiedReport schema.
- Map security_events from the input to the UnifiedReport security_events format (convert string format to object format)
- Convert threat_summary data to threat_analysis fields
- Use risk_assessment data for summary fields
- Include all recommendations from the input
- Generate realistic session_logs based on the security events
- Calculate performance_metrics based on the report data
- Ensure all timestamps are in ISO format
- Use the agent_id and report_id from the input
- **All summary and intelligence_insights fields must be strings, not objects.**
- **Do NOT output any objects for summaries or threat_intelligence—always output human-readable markdown or text.**
- All fields must be present and non-null (empty arrays/objects are fine if no data).
- Never return extra fields or change the schema.
- Output only the JSON object, nothing else.

**UnifiedReport schema:**
{unified_report_schema}

**Sample Input (Agent Sentinel SDK JSON):**
{sdk_sample_json}

**Sample Output (UnifiedReport):**
{unified_report_sample}

**Agent Sentinel Security Report Content:**
{workflow_content}

**IMPORTANT:** Respond ONLY with the valid JSON object. Do NOT include any text outside the JSON.
"""
        messages = self.llm_service.create_messages(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt
        )
        # LLM call
        raw_output = self.llm_service.invoke(messages)
        logger.info(f"Raw LLM output: {raw_output}")
        # Extract JSON from LLM output
        def extract_json_from_text(text):
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return None
            return None
        structured_report = extract_json_from_text(raw_output)
        if structured_report:
            # Normalize field names to match frontend schema
            def normalize_report_fields(report):
                # Top-level logs
                if "[REDACTED]_logs" in report:
                    report["session_logs"] = report.pop("[REDACTED]_logs")
                # Performance metrics duration
                if "performance_metrics" in report and "[REDACTED]_duration_seconds" in report["performance_metrics"]:
                    report["performance_metrics"]["session_duration_seconds"] = report["performance_metrics"].pop("[REDACTED]_duration_seconds")
                return report
            structured_report = normalize_report_fields(structured_report)
        if not structured_report:
            logger.error("LLM did not return valid JSON. Returning fallback structure.")
            return {"error": "LLM did not return valid JSON."}

        # Fill missing fields with sensible defaults to match UnifiedReport
        def fill_unified_report_fields(report):
            # Top-level fields
            report.setdefault("agent_id", "unknown")
            report.setdefault("start_time", "")
            report.setdefault("end_time", "")
            report.setdefault("session_logs", [])
            report.setdefault("security_events", [])
            report.setdefault("performance_metrics", {
                "total_function_calls": 0,
                "average_response_time_ms": 0,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "success_rate": 0,
                "error_rate": 0,
                "security_events_count": 0,
                "session_duration_seconds": 0,
                "throughput_requests_per_minute": 0
            })
            report.setdefault("threat_analysis", {
                "total_threats": 0,
                "threat_breakdown": {},
                "severity_distribution": {},
                "confidence_analysis": {
                    "average_confidence": 0,
                    "high_confidence_threats": 0,
                    "confidence_distribution": {}
                },
                "risk_score": 0,
                "most_common_threat": "",
                "highest_severity": ""
            })
            report.setdefault("recommendations", [])
            report.setdefault("summary", {
                "status": "CLEAN",
                "risk_score": 0,
                "threats_detected": 0,
                "performance_score": 0,
                "key_insights": [],
                "next_actions": []
            })
            report.setdefault("report_id", "")
            report.setdefault("analysis_type", "")
            report.setdefault("workflow_execution_time", 0)
            report.setdefault("intelligence_insights", {
                "enhanced_analysis": "",
                "threat_intelligence": "",
                "recommendations": []
            })
            return report

        complete_report = fill_unified_report_fields(structured_report)
        return complete_report
    
    def _enhance_report_formatting(self, report: str, workflow_content: str) -> str:
        """
        Enhance report with additional formatting and metadata.
        
        Args:
            report: Base report from LLM
            workflow_content: Original workflow content
            
        Returns:
            Enhanced report
        """
        # Extract metadata from workflow content
        metadata = self._extract_metadata(workflow_content)
        
        # Add report header
        enhanced = f"""
# AGENT SENTINEL ENHANCED SECURITY INTELLIGENCE REPORT

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Report ID**: {metadata.get('report_id', 'AS-INTEL-001')}  
**Analysis Type**: Enterprise Security Intelligence  
**Threat Level**: {metadata.get('threat_level', 'High')}  
**Risk Score**: {metadata.get('risk_score', '0.75')}/1.0

---

{report}

---

## REPORT METADATA

**Analysis Timestamp**: {datetime.now().isoformat()}  
**Total Threats Detected**: {metadata.get('total_threats', 'Multiple')}  
**Affected Agents**: {metadata.get('affected_agents', 'malicious_agent, translation_agent')}  
**Attack Patterns**: {metadata.get('attack_patterns', 'HTML Injection, Data Exfiltration')}  
**Analysis Confidence**: {metadata.get('confidence', 'High')}  
**Research Performed**: {metadata.get('research_performed', 'Yes')}

**Report Generated By**: Agent Sentinel Intelligence System v2.0  
**Classification**: Enterprise Security Intelligence  
**Distribution**: Internal Security Team, Executive Leadership
"""
        
        return enhanced
    
    def _extract_metadata(self, workflow_content: str) -> Dict[str, Any]:
        """
        Extract metadata from workflow content.
        
        Args:
            workflow_content: Content from workflow
            
        Returns:
            Extracted metadata
        """
        metadata = {
            'report_id': f"AS-INTEL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            'threat_level': 'High',
            'risk_score': '0.75',
            'total_threats': 'Multiple',
            'affected_agents': 'malicious_agent, translation_agent',
            'attack_patterns': 'HTML Injection, Data Exfiltration',
            'confidence': 'High',
            'research_performed': 'Yes'
        }
        
        # Extract information from content
        content_lower = workflow_content.lower()
        
        # Count threats
        threat_count = content_lower.count('threat') + content_lower.count('finding')
        if threat_count > 0:
            metadata['total_threats'] = str(threat_count)
        
        # Extract agents
        agents = []
        if 'malicious_agent' in content_lower:
            agents.append('malicious_agent')
        if 'translation_agent' in content_lower:
            agents.append('translation_agent')
        if 'math_agent' in content_lower:
            agents.append('math_agent')
        if 'weather_agent' in content_lower:
            agents.append('weather_agent')
        
        if agents:
            metadata['affected_agents'] = ', '.join(agents)
        
        # Extract attack patterns
        patterns = []
        if 'html injection' in content_lower or 'inject_html' in content_lower:
            patterns.append('HTML Injection')
        if 'data exfiltration' in content_lower or 'extract_data' in content_lower:
            patterns.append('Data Exfiltration')
        if 'xss' in content_lower or 'cross-site scripting' in content_lower:
            patterns.append('XSS')
        if 'sql injection' in content_lower:
            patterns.append('SQL Injection')
        
        if patterns:
            metadata['attack_patterns'] = ', '.join(patterns)
        
        # Determine threat level
        if any(keyword in content_lower for keyword in ['critical', 'high risk', 'severe']):
            metadata['threat_level'] = 'Critical'
        elif any(keyword in content_lower for keyword in ['medium', 'moderate']):
            metadata['threat_level'] = 'Medium'
        elif any(keyword in content_lower for keyword in ['low', 'minor']):
            metadata['threat_level'] = 'Low'
        
        # Check if research was performed
        if 'research' in content_lower or 'intelligence' in content_lower:
            metadata['research_performed'] = 'Yes'
        else:
            metadata['research_performed'] = 'No'
        
        return metadata
    
    def _fallback_to_validator(self, message: str) -> Dict[str, Any]:
        """Fallback to validator with error message."""
        # Ensure message is a string for HumanMessage
        if not isinstance(message, str):
            msg_str = "Error: LLM did not return valid JSON."
        else:
            msg_str = message
        return {
            "messages": [
                HumanMessage(content="Error: LLM did not return valid JSON.", name="reporter")
            ],
            "next": "validator"
        } 