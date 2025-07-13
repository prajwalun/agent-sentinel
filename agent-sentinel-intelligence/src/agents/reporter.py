"""
Enterprise Report Generator Agent for Agent Sentinel Intelligence Layer.

Generates comprehensive, actionable security intelligence reports with advanced
formatting, executive summaries, and enterprise-grade presentation.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage
# Command import removed - using simpler approach
from ..models.state import AgentState

from ..services.llm_service import LLMService
from ..services.tracing_service import TracingService

logger = logging.getLogger(__name__)


class ReportSection:
    """Structured report section."""
    
    def __init__(self, title: str, content: str, priority: str = "normal"):
        self.title = title
        self.content = content
        self.priority = priority


class EnterpriseReportGenerator:
    """Enterprise report generator with advanced formatting."""
    
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
    """Enterprise report generator agent that creates comprehensive security reports."""
    
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
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(workflow_content)
            
            # Validate report quality
            if not report or len(report.strip()) < 100:
                logger.error("❌ Generated report is too short or empty")
                return self._fallback_to_validator("Report generation failed - insufficient content")
            
            # Log report generation
            logger.info(f"Enterprise security report generated - {len(report)} characters")
            
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
                    HumanMessage(content=report, name="reporter")
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
    
    def _generate_comprehensive_report(self, workflow_content: str) -> str:
        """
        Generate comprehensive security report.
        
        Args:
            workflow_content: Content from all workflow agents
            
        Returns:
            Complete security report
        """
        # Create messages for LLM
        messages = self.llm_service.create_messages(
            system_prompt=self.system_prompt,
            user_prompt=f"""
            Generate a comprehensive enterprise security intelligence report based on the following 
            workflow analysis data:

            {workflow_content}

            Create a professional, structured report that includes all required sections:
            1. Executive Summary
            2. Threat Analysis  
            3. Risk Assessment
            4. Attack Patterns
            5. Agent Behavior Analysis
            6. Timeline Analysis
            7. Threat Intelligence (if research was performed)
            8. Recommendations (with priority levels)
            9. Future Prevention

            Ensure the report is well-structured, comprehensive, and provides clear, actionable 
            recommendations for addressing the identified threats. Use proper markdown formatting 
            and maintain professional language throughout.
            """
        )
        
        # Generate report from LLM
        report = self.llm_service.invoke(messages)
        
        # Enhance with structured formatting
        enhanced_report = self._enhance_report_formatting(report, workflow_content)
        
        return enhanced_report
    
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
        return {
            "messages": [
                HumanMessage(content=message, name="reporter")
            ],
            "next": "validator"
        } 