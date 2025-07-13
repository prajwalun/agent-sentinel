"""
Security Report Generator for BlueGuard A2A Security System
Generates comprehensive security reports in BlueGuard format
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityReportGenerator:
    """Generates comprehensive security reports in BlueGuard format"""
    
    def __init__(self):
        # Create reports directory
        Path("src/reports").mkdir(exist_ok=True)
        logger.info("Security Report Generator initialized")
    
    def generate_human_readable_report(self, security_data: Dict[str, Any]) -> str:
        """Generate a human-readable security report in BlueGuard format"""
        report = []
        report.append("=" * 60)
        report.append("BLUEGUARD SECURITY REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        
        # Count threats by severity
        total_alerts = len(security_data.get("alerts", []))
        critical_threats = 0
        high_threats = 0
        medium_threats = 0
        
        for alert in security_data.get("alerts", []):
            if alert.get("severity") == "critical":
                critical_threats += 1
            elif alert.get("severity") == "high":
                high_threats += 1
            elif alert.get("severity") == "medium":
                medium_threats += 1
        
        report.append(f"Total Alerts: {total_alerts}")
        report.append(f"Critical Threats: {critical_threats}")
        report.append(f"High Threats: {high_threats}")
        report.append(f"Medium Threats: {medium_threats}")
        report.append("")
        
        # Group alerts by severity
        critical_alerts = [alert for alert in security_data.get("alerts", []) if alert.get("severity") == "critical"]
        high_alerts = [alert for alert in security_data.get("alerts", []) if alert.get("severity") == "high"]
        medium_alerts = [alert for alert in security_data.get("alerts", []) if alert.get("severity") == "medium"]
        
        # Critical Threats Section
        if critical_alerts:
            report.append("CRITICAL THREATS:")
            report.append("-" * 40)
            for i, alert in enumerate(critical_alerts, 1):
                self._add_finding_to_report(report, i, alert)
            report.append("")
        
        # High Threats Section
        if high_alerts:
            report.append("HIGH THREATS:")
            report.append("-" * 40)
            for i, alert in enumerate(high_alerts, 1):
                self._add_finding_to_report(report, i, alert)
            report.append("")
        
        # Medium Threats Section
        if medium_alerts:
            report.append("MEDIUM THREATS:")
            report.append("-" * 40)
            for i, alert in enumerate(medium_alerts, 1):
                self._add_finding_to_report(report, i, alert)
            report.append("")
        
        # Summary if no threats
        if total_alerts == 0:
            report.append("NO THREATS DETECTED:")
            report.append("-" * 40)
            report.append("✅ All agent interactions appear to be secure.")
            report.append("✅ No security threats were identified in the analyzed content.")
            report.append("✅ The A2A system is operating within security parameters.")
            report.append("")
        
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _add_finding_to_report(self, report: List[str], finding_number: int, alert: Dict[str, Any]):
        """Add a finding to the report in BlueGuard format"""
        report.append(f"FINDING #{finding_number}")
        report.append("-" * 40)
        
        # Agent information
        agent_id = alert.get("agent_id", "Unknown")
        tool = alert.get("tool", "Unknown")
        timestamp = alert.get("timestamp", "Unknown")
        
        report.append(f"Agent: {agent_id}")
        report.append(f"Tool: {tool}")
        report.append(f"Time: {timestamp}")
        
        # Threat types
        threats = alert.get("threats", [])
        if threats:
            threat_types = []
            for threat in threats:
                threat_type = threat.get("type", "unknown")
                # Convert to readable format
                if threat_type == "html_injection":
                    threat_types.append("HTML/Comment injection")
                elif threat_type == "prompt_injection":
                    threat_types.append("Prompt injection")
                elif threat_type == "data_exfiltration":
                    threat_types.append("Data exfiltration")
                elif threat_type == "command_injection":
                    threat_types.append("Command injection")
                elif threat_type == "sql_injection":
                    threat_types.append("SQL injection")
                elif threat_type == "xss":
                    threat_types.append("XSS")
                else:
                    threat_types.append(threat_type.replace("_", " ").title())
            
            report.append(f"Threats: {', '.join(set(threat_types))}")
        
        # Content details
        report.append("Content:")
        if threats:
            # Show the first threat match as content
            first_threat = threats[0]
            content = {
                "type": "result" if "result" in first_threat.get("source", "") else "invocation",
                "agent": agent_id,
                "payload": {
                    "result": first_threat.get("match", "Unknown content"),
                    "tool": tool
                },
                "ts": timestamp
            }
            report.append(json.dumps(content, indent=2))
        else:
            content = {
                "type": "invocation",
                "agent": agent_id,
                "payload": {
                    "tool": tool,
                    "params": "Unknown parameters"
                },
                "ts": timestamp
            }
            report.append(json.dumps(content, indent=2))
        
        report.append("") 