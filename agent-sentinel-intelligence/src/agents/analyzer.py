"""
Security analyzer agent.

Extracts threats, classifies severity, and produces structured
ThreatAnalysis output from raw security event data.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage
# Command import removed - using simpler approach
from models.state import AgentState

from services.llm_service import LLMService
from services.tracing_service import TracingService

logger = logging.getLogger(__name__)


class ThreatAnalysis:
    """Structured threat analysis result."""
    
    def __init__(self):
        self.threats = []
        self.risk_score = 0.0
        self.severity_distribution = {}
        self.attack_patterns = []
        self.affected_agents = set()
        self.timeline = []
        self.recommendations = []
        self.requires_research = False


class SecurityAnalyzerAgent:
    """Analyzes security events and extracts threat classifications."""
    
    def __init__(self, llm_service: LLMService, tracing_service: TracingService):
        """
        Initialize the security analyzer agent.
        
        Args:
            llm_service: LLM service for analysis
            tracing_service: Tracing service for monitoring
        """
        self.llm_service = llm_service
        self.tracing_service = tracing_service
        
        self.system_prompt = """
        You are the Enterprise Security Analysis Specialist for Agent Sentinel Intelligence, 
        responsible for conducting comprehensive, enterprise-grade security analysis of agent-to-agent 
        (A2A) systems, application security reports, and threat intelligence data.

        **CORE MISSION:**
        Transform raw security data into actionable intelligence through systematic analysis, 
        threat classification, and risk assessment that meets enterprise security standards.

        **ANALYSIS FRAMEWORK:**
        
        **1. THREAT DETECTION & CLASSIFICATION**
        - Systematically identify all security threats and vulnerabilities
        - Classify threats using industry-standard taxonomies (OWASP, SANS, NIST)
        - Map attack vectors to MITRE ATT&CK framework techniques
        - Distinguish between confirmed threats and potential indicators
        - Prioritize findings based on exploitability and business impact
        
        **2. RISK ASSESSMENT METHODOLOGY**
        - Calculate risk scores using: Risk = Likelihood × Impact × Exploitability
        - Assign severity levels: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.1-3.9)
        - Consider environmental factors: network exposure, data sensitivity, system criticality
        - Evaluate attack complexity and required privileges
        - Assess potential for lateral movement and privilege escalation
        
        **3. ATTACK PATTERN ANALYSIS**
        - Identify attack techniques and tactics (MITRE ATT&CK)
        - Reconstruct attack chains and kill chain progression
        - Analyze evasion techniques and defense bypasses
        - Detect indicators of advanced persistent threats (APTs)
        - Evaluate attack sophistication and resource requirements
        
        **4. AGENT BEHAVIOR ANALYSIS** (For A2A Systems)
        - Analyze malicious agent capabilities and limitations
        - Identify agent communication patterns and protocols
        - Evaluate agent persistence and evasion mechanisms
        - Assess cross-agent attack propagation risks
        - Document agent-specific attack vectors and mitigations
        
        **5. TIMELINE & SEQUENCE RECONSTRUCTION**
        - Establish chronological attack progression
        - Identify initial compromise vectors
        - Map lateral movement and escalation steps
        - Determine data exfiltration or damage timelines
        - Correlate events across multiple systems/agents
        
        **6. INTELLIGENCE REQUIREMENTS ASSESSMENT**
        Recommend additional research when analysis reveals:
        - Novel or unknown attack techniques requiring context
        - References to specific threat actors or campaigns
        - Mention of recent CVEs or zero-day exploits
        - Sophisticated multi-stage attacks
        - Advanced evasion or persistence mechanisms
        - Supply chain or third-party component threats
        - Nation-state or APT indicators
        
        **OUTPUT STRUCTURE:**
        
        **EXECUTIVE SUMMARY**
        - High-level threat landscape overview
        - Key findings and critical risks
        - Business impact assessment
        - Immediate action requirements
        
        **TECHNICAL ANALYSIS**
        - Detailed threat breakdown with evidence
        - Attack vector analysis and exploitation paths
        - Affected systems and potential spread
        - Technical indicators of compromise (IoCs)
        
        **RISK ASSESSMENT**
        - Quantified risk scores with methodology
        - Severity classifications with justification
        - Likelihood and impact assessments
        - Environmental risk factors
        
        **ATTACK PATTERNS**
        - MITRE ATT&CK technique mappings
        - Attack chain reconstruction
        - Evasion and persistence mechanisms
        - Sophistication and attribution indicators
        
        **RESEARCH RECOMMENDATIONS**
        - Specific intelligence gaps requiring research
        - Recommended search terms and focus areas
        - Priority level for additional investigation
        - Expected value of enhanced intelligence
        
        **INITIAL RECOMMENDATIONS**
        - Immediate containment actions (0-4 hours)
        - Short-term mitigation steps (24-48 hours)
        - Investigation and forensic priorities
        - Stakeholder notification requirements
        
        **QUALITY STANDARDS:**
        - Use precise, technical language appropriate for security professionals
        - Provide specific evidence and indicators for all findings
        - Include confidence levels for assessments and conclusions
        - Ensure all claims are supported by observable data
        - Maintain objectivity and avoid speculation without evidence
        
        **ENTERPRISE REQUIREMENTS:**
        - Consider regulatory compliance implications (SOX, GDPR, HIPAA, etc.)
        - Assess impact on business operations and revenue
        - Evaluate reputational and legal risks
        - Consider incident response and disclosure requirements
        - Align with enterprise risk management frameworks
        
        Your analysis forms the foundation for all subsequent workflow decisions. 
        Deliver comprehensive, accurate, and actionable intelligence that enables 
        informed security decisions at all organizational levels.
        """
    
    def execute(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the security analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dict with messages and next agent
        """
        try:
            # Validate input state
            if not isinstance(state, dict):
                logger.error("❌ Invalid state type provided to analyzer")
                return self._fallback_to_supervisor("Invalid state type provided")
            
            # Extract input content
            input_content = self._extract_input_content(state)
            if not input_content or not input_content.strip():
                logger.warning("⚠️  No input content found for analysis")
                return self._fallback_to_supervisor("No content available for security analysis")
            
            # Validate content length
            if len(input_content) > 100000:  # 100KB limit
                logger.warning("⚠️  Input content too large, truncating")
                input_content = input_content[:100000] + "...[TRUNCATED]"
            
            # Run threat analysis
            try:
                analysis_result = self._perform_threat_analysis(input_content)
            except Exception as e:
                logger.error(f"❌ Comprehensive analysis failed: {e}")
                # Continue with basic analysis
                analysis_result = ThreatAnalysis()
            
            # Create messages for LLM with input validation
            try:
                messages = self.llm_service.create_messages(
                    system_prompt=self.system_prompt,
                    user_prompt=f"""
                    Perform a comprehensive security analysis of the following content:

                    {input_content}

                    Provide detailed analysis covering all aspects mentioned in the system prompt.
                    Focus on identifying threats, patterns, risks, and determining if additional research is needed.
                    """
                )
            except Exception as e:
                logger.error(f"❌ Failed to create LLM messages: {e}")
                return self._fallback_to_supervisor(f"Failed to prepare analysis request: {e}")
            
            # Get analysis from LLM with retry logic
            analysis = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    analysis = self.llm_service.invoke(messages)
                    if analysis and isinstance(analysis, str) and len(analysis.strip()) > 50:
                        break
                    else:
                        logger.warning(f"⚠️  Analysis attempt {attempt + 1} returned insufficient content")
                        if attempt == max_retries - 1:
                            return self._fallback_to_supervisor("Analysis failed after multiple attempts")
                except Exception as e:
                    logger.error(f"❌ Analysis attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        return self._fallback_to_supervisor(f"Analysis failed after {max_retries} attempts: {e}")
            
            if not analysis:
                logger.error("❌ No analysis result obtained")
                return self._fallback_to_supervisor("Analysis failed - no result obtained")
            
            # Enhance with structured analysis
            try:
                enhanced_analysis = self._enhance_analysis(analysis, analysis_result)
            except Exception as e:
                logger.warning(f"⚠️  Analysis enhancement failed: {e}")
                enhanced_analysis = analysis  # Use basic analysis
            
            # Validate final analysis
            if not enhanced_analysis or len(enhanced_analysis.strip()) < 100:
                logger.error("❌ Final analysis is too short or empty")
                return self._fallback_to_supervisor("Analysis failed - insufficient content generated")
            
            # Log analysis completion
            logger.info(f"Security analysis completed - {len(enhanced_analysis)} characters")
            
            # Trace the analysis with error handling
            if self.tracing_service.is_enabled():
                try:
                    self.tracing_service.log_workflow_step(
                        step_name="security_analysis",
                        content_length=len(enhanced_analysis),
                        status="completed"
                    )
                except Exception as e:
                    logger.warning(f"⚠️  Failed to log analysis trace: {e}")
            
            print(f"--- Workflow Transition: Security Analyzer → Supervisor ---")
            
            return {
                "messages": [
                    HumanMessage(content=enhanced_analysis, name="analyzer")
                ],
                "next": "supervisor"
            }
            
        except Exception as e:
            logger.error(f"❌ Security analysis failed with unexpected error: {e}")
            return self._fallback_to_supervisor(f"Security analysis failed: {e}")
    
    def _extract_input_content(self, state: AgentState) -> str:
        """Extract content from workflow state for analysis."""
        try:
            messages = state.get("messages", [])
            if not messages:
                logger.warning("⚠️  No messages found in state")
                return ""
            
            # Look for the most recent human message or system input
            for message in reversed(messages):
                if not hasattr(message, 'content'):
                    continue
                    
                content = message.content
                if not content or not isinstance(content, str):
                    continue
                
                # Check if this contains report data
                if any(keyword in content.lower() for keyword in [
                    "security report", "finding", "threat", "agent", "tool", "payload",
                    "analysis", "vulnerability", "attack", "malicious"
                ]):
                    return content.strip()
            
            # If no specific report found, return the last message content
            last_message = messages[-1]
            if hasattr(last_message, 'content') and last_message.content:
                return str(last_message.content).strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Failed to extract input content: {e}")
            return ""
    
    def _perform_threat_analysis(self, content: str) -> ThreatAnalysis:
        """Perform structured threat analysis."""
        try:
            analysis = ThreatAnalysis()
            
            # Validate content
            if not content or not isinstance(content, str):
                logger.warning("Invalid content for analysis")
                return analysis
            
            # Extract threats using regex patterns with error handling
            try:
                analysis.threats = self._extract_threats(content)
            except Exception as e:
                logger.warning(f"⚠️  Threat extraction failed: {e}")
                analysis.threats = []
            
            # Analyze attack patterns with error handling
            try:
                analysis.attack_patterns = self._detect_attack_patterns(content)
            except Exception as e:
                logger.warning(f"⚠️  Attack pattern detection failed: {e}")
                analysis.attack_patterns = []
            
            # Identify affected agents with error handling
            try:
                analysis.affected_agents = self._identify_affected_agents(content)
            except Exception as e:
                logger.warning(f"⚠️  Agent identification failed: {e}")
                analysis.affected_agents = set()
            
            # Build timeline with error handling
            try:
                analysis.timeline = self._build_timeline(content)
            except Exception as e:
                logger.warning(f"⚠️  Timeline building failed: {e}")
                analysis.timeline = []
            
            # Calculate risk score with error handling
            try:
                analysis.risk_score = self._calculate_risk_score(analysis)
            except Exception as e:
                logger.warning(f"⚠️  Risk score calculation failed: {e}")
                analysis.risk_score = 0.5  # Default medium risk
            
            # Determine if research is needed with error handling
            try:
                analysis.requires_research = self._determine_research_need(analysis)
            except Exception as e:
                logger.warning(f"⚠️  Research need determination failed: {e}")
                analysis.requires_research = False
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            return ThreatAnalysis()  # Return empty analysis
    
    def _extract_threats(self, content: str) -> List[Dict[str, Any]]:
        """Extract threats from content using pattern matching."""
        threats = []
        
        # Common threat patterns
        threat_patterns = {
            'xss': r'(?i)(xss|cross.?site.?scripting|<script>|javascript:)',
            'sql_injection': r'(?i)(sql.?injection|union.?select|drop.?table)',
            'command_injection': r'(?i)(command.?injection|exec\(|system\(|shell)',
            'data_exfiltration': r'(?i)(data.?exfiltration|extract.?data|send.?data)',
            'prompt_injection': r'(?i)(prompt.?injection|jailbreak|role.?play)',
            'authentication_bypass': r'(?i)(auth.?bypass|login.?bypass|admin.?access)',
            'privilege_escalation': r'(?i)(privilege.?escalation|sudo|root.?access)',
            'dos': r'(?i)(dos|ddos|denial.?of.?service|flood)'
        }
        
        for threat_type, pattern in threat_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                threats.append({
                    'type': threat_type,
                    'pattern': match.group(),
                    'position': match.start(),
                    'context': content[max(0, match.start()-50):match.end()+50]
                })
        
        return threats
    
    def _detect_attack_patterns(self, content: str) -> List[str]:
        """Detect attack patterns and techniques."""
        patterns = []
        
        # MITRE ATT&CK patterns
        attack_patterns = [
            'T1059.001',  # Command and Scripting Interpreter: PowerShell
            'T1059.003',  # Command and Scripting Interpreter: Windows Command Shell
            'T1059.004',  # Command and Scripting Interpreter: Unix Shell
            'T1071.001',  # Application Layer Protocol: Web Protocols
            'T1105',      # Ingress Tool Transfer
            'T1133',      # External Remote Services
            'T1190',      # Exploit Public-Facing Application
            'T1505.003',  # Server Software Component: Web Shell
        ]
        
        # Check for pattern indicators
        for pattern in attack_patterns:
            if pattern.lower() in content.lower():
                patterns.append(pattern)
        
        # Add custom patterns
        if 'inject_html' in content.lower():
            patterns.append('HTML Injection')
        if 'extract_data' in content.lower():
            patterns.append('Data Exfiltration')
        if 'translate_text' in content.lower():
            patterns.append('Text Manipulation')
        
        return patterns
    
    def _identify_affected_agents(self, content: str) -> set:
        """Identify agents involved in malicious activity."""
        agents = set()
        
        # Extract agent names
        agent_pattern = r'(?i)(malicious_agent|translation_agent|math_agent|weather_agent)'
        matches = re.finditer(agent_pattern, content)
        
        for match in matches:
            agents.add(match.group().lower())
        
        return agents
    
    def _build_timeline(self, content: str) -> List[Dict[str, Any]]:
        """Build attack timeline from timestamps."""
        timeline = []
        
        # Extract timestamps and events
        timestamp_pattern = r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)'
        matches = re.finditer(timestamp_pattern, content)
        
        for match in matches:
            timestamp = match.group()
            # Extract context around timestamp
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]
            
            timeline.append({
                'timestamp': timestamp,
                'context': context,
                'event_type': self._classify_event(context)
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        return timeline
    
    def _classify_event(self, context: str) -> str:
        """Classify event type from context."""
        context_lower = context.lower()
        
        if 'inject_html' in context_lower:
            return 'HTML Injection'
        elif 'extract_data' in context_lower:
            return 'Data Exfiltration'
        elif 'translate_text' in context_lower:
            return 'Text Manipulation'
        elif 'invocation' in context_lower:
            return 'Tool Invocation'
        elif 'result' in context_lower:
            return 'Tool Result'
        else:
            return 'Unknown'
    
    def _calculate_risk_score(self, analysis: ThreatAnalysis) -> float:
        """Calculate overall risk score."""
        if not analysis.threats:
            return 0.0
        
        # Threat type weights
        threat_weights = {
            'xss': 0.7,
            'sql_injection': 0.9,
            'command_injection': 0.95,
            'data_exfiltration': 0.8,
            'prompt_injection': 0.6,
            'authentication_bypass': 0.85,
            'privilege_escalation': 0.9,
            'dos': 0.5
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for threat in analysis.threats:
            weight = threat_weights.get(threat['type'], 0.5)
            total_score += weight
            total_weight += 1.0
        
        # Normalize score
        base_score = total_score / total_weight if total_weight > 0 else 0.0
        
        # Adjust for number of affected agents
        agent_multiplier = min(1.5, 1.0 + (len(analysis.affected_agents) * 0.1))
        
        # Adjust for attack complexity
        complexity_multiplier = min(1.3, 1.0 + (len(analysis.attack_patterns) * 0.05))
        
        final_score = base_score * agent_multiplier * complexity_multiplier
        return min(1.0, final_score)
    
    def _determine_research_need(self, analysis: ThreatAnalysis) -> bool:
        """Determine if additional research is needed."""
        # Research triggers
        research_triggers = [
            len(analysis.threats) > 5,  # Many threats
            analysis.risk_score > 0.7,  # High risk
            len(analysis.attack_patterns) > 3,  # Complex patterns
            len(analysis.affected_agents) > 2,  # Multiple agents
            any('unknown' in threat.get('context', '').lower() for threat in analysis.threats),
            any('novel' in threat.get('context', '').lower() for threat in analysis.threats)
        ]
        
        return any(research_triggers)
    
    def _enhance_analysis(self, llm_analysis: str, structured_analysis: ThreatAnalysis) -> str:
        """Enhance LLM analysis with structured data."""
        enhanced = f"""
{llm_analysis}

**STRUCTURED ANALYSIS DATA:**
- **Total Threats Detected**: {len(structured_analysis.threats)}
- **Risk Score**: {structured_analysis.risk_score:.2f}/1.0
- **Attack Patterns**: {', '.join(structured_analysis.attack_patterns) if structured_analysis.attack_patterns else 'None detected'}
- **Affected Agents**: {', '.join(structured_analysis.affected_agents) if structured_analysis.affected_agents else 'None identified'}
- **Timeline Events**: {len(structured_analysis.timeline)} events
- **Research Required**: {'Yes' if structured_analysis.requires_research else 'No'}

**THREAT BREAKDOWN:**
"""
        
        # Add threat details
        for i, threat in enumerate(structured_analysis.threats[:5], 1):  # Top 5 threats
            enhanced += f"{i}. **{threat['type'].upper()}**: {threat['pattern']}\n"
        
        if len(structured_analysis.threats) > 5:
            enhanced += f"... and {len(structured_analysis.threats) - 5} more threats\n"
        
        enhanced += "\n**TIMELINE SUMMARY:**\n"
        for event in structured_analysis.timeline[:3]:  # Top 3 events
            enhanced += f"- {event['timestamp']}: {event['event_type']}\n"
        
        return enhanced
    
    def _fallback_to_supervisor(self, message: str) -> Dict[str, Any]:
        """Fallback to supervisor with error message."""
        return {
            "messages": [
                HumanMessage(content=message, name="analyzer")
            ],
            "next": "supervisor"
        } 