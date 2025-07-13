"""
Security Heuristics for BlueGuard A2A Security System
Defines patterns and rules for threat detection
"""

import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SecurityHeuristics:
    """Security heuristics for threat detection"""
    
    def __init__(self):
        self.threat_patterns = {
            "html_injection": [
                r"<!--.*?-->",
                r"<script.*?</script>",
                r"<.*?>",
                r"javascript:",
                r"on\w+\s*="
            ],
            "prompt_injection": [
                r"ignore\s+all\s+previous\s+instructions",
                r"ignore\s+previous\s+instructions",
                r"ignore\s+all\s+instructions",
                r"ignore\s+the\s+above",
                r"ignore\s+everything\s+above"
            ],
            "data_exfiltration": [
                r"send\s+secrets",
                r"send\s+data",
                r"extract\s+.*?data",
                r"user\s+data",
                r"personal\s+information",
                r"credit\s+card",
                r"password",
                r"api\s+key"
            ],
            "command_injection": [
                r";\s*\w+",
                r"`.*?`",
                r"\$\{.*?\}",
                r"eval\(",
                r"exec\(",
                r"system\(",
                r"subprocess\."
            ],
            "sql_injection": [
                r"union\s+select",
                r"drop\s+table",
                r"delete\s+from",
                r"insert\s+into",
                r"update\s+set",
                r"or\s+1\s*=\s*1",
                r"';"
            ],
            "xss": [
                r"<script>",
                r"javascript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*="
            ]
        }
        
        self.severity_levels = {
            "critical": ["command_injection", "sql_injection"],
            "high": ["html_injection", "data_exfiltration", "xss"],
            "medium": ["prompt_injection"],
            "low": []
        }
    
    def analyze_text(self, text: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """Analyze text for security threats"""
        threats = []
        
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    threat = {
                        "type": threat_type,
                        "pattern": pattern,
                        "match": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "severity": self._get_severity(threat_type),
                        "source": source,
                        "context": text[max(0, match.start()-50):match.end()+50]
                    }
                    threats.append(threat)
        
        return threats
    
    def _get_severity(self, threat_type: str) -> str:
        """Get severity level for a threat type"""
        for severity, types in self.severity_levels.items():
            if threat_type in types:
                return severity
        return "low"
    
    def get_threat_summary(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of threats"""
        summary = {
            "total_threats": len(threats),
            "by_type": {},
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }
        }
        
        for threat in threats:
            threat_type = threat["type"]
            severity = threat["severity"]
            
            # Count by type
            if threat_type not in summary["by_type"]:
                summary["by_type"][threat_type] = 0
            summary["by_type"][threat_type] += 1
            
            # Count by severity
            summary["by_severity"][severity] += 1
        
        return summary 