"""
Web Researcher Agent for Agent Sentinel Intelligence Layer.

Performs web research and threat intelligence gathering using Exa.ai.
"""

import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from ..models.state import AgentState

from ..services.llm_service import LLMService
from ..services.tracing_service import TracingService
from ..services.research_service import ResearchService

logger = logging.getLogger(__name__)


class WebResearcherAgent:
    """Web researcher agent that performs threat intelligence research."""
    
    def __init__(
        self, 
        llm_service: LLMService, 
        tracing_service: TracingService,
        research_service: ResearchService
    ):
        """
        Initialize the web researcher agent.
        
        Args:
            llm_service: LLM service for research analysis
            tracing_service: Tracing service for monitoring
            research_service: Research service for web queries
        """
        self.llm_service = llm_service
        self.tracing_service = tracing_service
        self.research_service = research_service
        
        self.system_prompt = """
        You are the Enterprise Threat Intelligence Research Specialist for Agent Sentinel Intelligence, 
        responsible for conducting targeted, high-value research that enhances security analysis with 
        external intelligence sources, threat actor profiling, and real-time threat landscape data.

        **CORE MISSION:**
        Transform security analysis findings into comprehensive threat intelligence through systematic 
        research, contextual analysis, and actionable intelligence synthesis that supports executive 
        decision-making and operational security responses.

        **RESEARCH METHODOLOGY:**
        
        **1. INTELLIGENCE COLLECTION FRAMEWORK**
        - Conduct targeted searches based on specific threat indicators
        - Gather contextual information from authoritative security sources
        - Collect threat actor attribution and campaign intelligence
        - Research vulnerability details and exploitation techniques
        - Identify similar attacks and historical patterns
        
        **2. THREAT INTELLIGENCE PRIORITIES**
        
        **HIGH PRIORITY RESEARCH AREAS:**
        - Novel attack techniques and zero-day exploits
        - Advanced persistent threat (APT) campaigns and tactics
        - Threat actor profiling and attribution indicators
        - Supply chain and third-party component vulnerabilities
        - Nation-state sponsored attacks and geopolitical threats
        - Ransomware families and criminal organization profiles
        - Critical infrastructure targeting and industrial espionage
        
        **MEDIUM PRIORITY RESEARCH AREAS:**
        - Recent CVE details and proof-of-concept exploits
        - Emerging malware families and variants
        - Social engineering and phishing campaign trends
        - Cloud security threats and misconfigurations
        - Mobile and IoT security vulnerabilities
        - Cryptocurrency and blockchain-related threats
        
        **3. SOURCE EVALUATION CRITERIA**
        - Prioritize authoritative sources (CISA, NIST, vendor advisories)
        - Validate information through multiple independent sources
        - Assess source credibility and recency of information
        - Consider geopolitical and industry-specific context
        - Evaluate threat intelligence provider reputation
        
        **4. RESEARCH SYNTHESIS APPROACH**
        - Correlate findings with original security analysis
        - Identify gaps in initial threat assessment
        - Provide additional context for risk evaluation
        - Enhance mitigation recommendations with proven strategies
        - Support incident response planning with historical precedents
        
        **INTELLIGENCE OUTPUT STRUCTURE:**
        
        **THREAT LANDSCAPE CONTEXT**
        - Current threat environment overview
        - Relevant attack trends and patterns
        - Industry-specific threat considerations
        - Geopolitical factors affecting threat landscape
        
        **THREAT ACTOR INTELLIGENCE**
        - Attribution indicators and campaign analysis
        - Threat actor capabilities and motivations
        - Historical attack patterns and methodologies
        - Associated infrastructure and tools
        - Targeting preferences and victim profiles
        
        **VULNERABILITY INTELLIGENCE**
        - Detailed CVE information and CVSS scores
        - Exploitation complexity and requirements
        - Available proof-of-concept code or exploits
        - Vendor patches and mitigation timelines
        - Real-world exploitation incidents
        
        **ATTACK TECHNIQUE ANALYSIS**
        - Detailed technique descriptions and variations
        - Detection and prevention strategies
        - Evasion methods and defensive bypasses
        - Tool and framework associations
        - Countermeasure effectiveness assessments
        
        **CONTEXTUAL INTELLIGENCE**
        - Similar incidents and case studies
        - Industry-specific impact assessments
        - Regulatory and compliance implications
        - Business continuity considerations
        - Stakeholder communication requirements
        
        **ENHANCED RECOMMENDATIONS**
        - Research-informed mitigation strategies
        - Threat hunting and detection guidance
        - Incident response procedure updates
        - Long-term security architecture improvements
        - Threat intelligence sharing opportunities
        
        **RESEARCH QUALITY STANDARDS:**
        - Cite all sources with URLs and publication dates
        - Distinguish between confirmed facts and assessments
        - Provide confidence levels for intelligence assessments
        - Include multiple perspectives on controversial topics
        - Maintain objectivity and avoid speculation
        - Focus on actionable intelligence over general information
        
        **ENTERPRISE INTELLIGENCE REQUIREMENTS:**
        - Consider business impact and operational disruption
        - Evaluate competitive intelligence implications
        - Assess regulatory reporting and disclosure requirements
        - Align with organizational risk tolerance and priorities
        - Support strategic security planning and investment decisions
        
        **RESEARCH EFFICIENCY GUIDELINES:**
        - Focus on high-value intelligence gaps identified in analysis
        - Prioritize recent and relevant information over historical data
        - Limit research scope to directly applicable findings
        - Synthesize information rather than simply aggregating sources
        - Provide clear value proposition for each research finding
        
        **OUTPUT INTEGRATION:**
        Your research must seamlessly integrate with the original security analysis to create 
        a comprehensive intelligence product. Ensure that your findings directly support:
        - Enhanced threat assessment and risk scoring
        - Improved mitigation and response strategies
        - Better understanding of threat actor motivations
        - More accurate business impact projections
        - Stronger security architecture recommendations
        
        Remember: Your research transforms technical security findings into strategic intelligence 
        that enables informed decision-making at all organizational levels. Focus on delivering 
        high-value, actionable intelligence that directly supports enterprise security objectives.
        """
    
    def execute(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the web research.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dict with messages and next agent
        """
        try:
            # Validate input state
            if not isinstance(state, dict):
                logger.error("❌ Invalid state type provided to researcher")
                return self._fallback_to_supervisor("Invalid state type provided")
            
            # Extract the last message (should be from analyzer)
            messages = state.get("messages", [])
            if not messages:
                logger.warning("⚠️  No messages found in state")
                return self._fallback_to_supervisor("No messages available for research")
            
            last_message = messages[-1]
            if not hasattr(last_message, 'content') or not last_message.content:
                logger.warning("⚠️  No previous analysis found for research")
                return self._fallback_to_supervisor("No analysis available for research")
            
            # Validate content
            content = last_message.content
            if not isinstance(content, str) or len(content.strip()) < 50:
                logger.warning("⚠️  Analysis content too short for meaningful research")
                return self._fallback_to_supervisor("Analysis content insufficient for research")
            
            # Perform web research based on analysis with comprehensive error handling
            try:
                research_results = self._perform_research(content)
            except Exception as e:
                logger.error(f"❌ Research execution failed: {e}")
                research_results = "Research service encountered an error. Proceeding with available analysis."
            
            # Validate research results
            if not research_results or not isinstance(research_results, str):
                logger.warning("⚠️  No research results obtained")
                research_results = "No additional research findings available."
            
            # Create messages for LLM to synthesize research with error handling
            try:
                messages_for_llm = self.llm_service.create_messages(
                    system_prompt=self.system_prompt,
                    user_prompt=f"""
                    Based on the security analysis below, synthesize the research findings and provide 
                    additional threat intelligence context:

                    SECURITY ANALYSIS:
                    {content}

                    RESEARCH FINDINGS:
                    {research_results}
                    """
                )
            except Exception as e:
                logger.error(f"❌ Failed to create LLM messages: {e}")
                return self._fallback_to_supervisor(f"Failed to prepare research synthesis: {e}")
            
            # Get synthesized research from LLM with retry logic
            synthesis = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    synthesis = self.llm_service.invoke(messages_for_llm)
                    if synthesis and isinstance(synthesis, str) and len(synthesis.strip()) > 100:
                        break
                    else:
                        logger.warning(f"⚠️  Research synthesis attempt {attempt + 1} returned insufficient content")
                        if attempt == max_retries - 1:
                            return self._fallback_to_supervisor("Research synthesis failed after multiple attempts")
                except Exception as e:
                    logger.error(f"❌ Research synthesis attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        return self._fallback_to_supervisor(f"Research synthesis failed after {max_retries} attempts: {e}")
            
            if not synthesis:
                logger.error("❌ No synthesis result obtained")
                return self._fallback_to_supervisor("Research synthesis failed - no result obtained")
            
            # Validate final synthesis
            if len(synthesis.strip()) < 100:
                logger.warning("⚠️  Research synthesis too short, using fallback")
                synthesis = f"Research completed with limited results:\n\n{research_results}"
            
            # Log research completion
            logger.info(f"Web research completed - {len(synthesis)} characters")
            
            # Trace the research with error handling
            if self.tracing_service.is_enabled():
                try:
                    self.tracing_service.log_workflow_step(
                        step_name="web_research",
                        content_length=len(synthesis),
                        status="completed"
                    )
                except Exception as e:
                    logger.warning(f"⚠️  Failed to log research trace: {e}")
            
            print(f"--- Workflow Transition: Web Researcher → Supervisor ---")
            
            return {
                "messages": [
                    HumanMessage(content=synthesis, name="researcher")
                ],
                "next": "supervisor"
            }
            
        except Exception as e:
            logger.error(f"❌ Web research failed with unexpected error: {e}")
            return self._fallback_to_supervisor(f"Research failed: {e}")
    
    def _perform_research(self, analysis_content: str) -> str:
        """
        Perform web research based on security analysis.
        
        Args:
            analysis_content: Content from security analysis
            
        Returns:
            Research results as formatted string
        """
        try:
            # Check if research service is available
            if not self.research_service.is_available():
                logger.warning("⚠️  Research service not available")
                return "Research service not available. Proceeding without additional research."
            
            # Validate input content
            if not analysis_content or not isinstance(analysis_content, str):
                logger.warning("⚠️  Invalid analysis content for research")
                return "Invalid analysis content provided for research."
            
            research_findings = []
            
            # Extract threat types from analysis for targeted research
            try:
                threat_types = self._extract_threat_types(analysis_content)
                if not threat_types:
                    logger.warning("⚠️  No threat types identified for research")
                    return "No specific threat types identified for targeted research."
            except Exception as e:
                logger.error(f"❌ Threat type extraction failed: {e}")
                return "Failed to extract threat types for research."
            
            # Perform research for each threat type (limit to 3 to control costs)
            for threat_type in threat_types[:3]:
                try:
                    # Search for threat intelligence with timeout
                    result = self.research_service.search_threat_intelligence(
                        threat_type=threat_type,
                        technique="attack"
                    )
                    
                    if result and hasattr(result, 'results') and result.results:
                        research_findings.append(f"**{threat_type.upper()} RESEARCH:**")
                        for i, res in enumerate(result.results[:2], 1):  # Top 2 results
                            try:
                                title = res.get('title', 'No title')
                                url = res.get('url', 'No URL')
                                text = res.get('text', 'No content')
                                
                                research_findings.append(f"{i}. {title}")
                                research_findings.append(f"   URL: {url}")
                                research_findings.append(f"   Summary: {text[:200]}...")
                                research_findings.append("")
                            except Exception as e:
                                logger.warning(f"⚠️  Failed to process research result: {e}")
                                continue
                    else:
                        logger.warning(f"⚠️  No results found for threat type: {threat_type}")
                        research_findings.append(f"**{threat_type.upper()} RESEARCH:**")
                        research_findings.append("No specific research results found.")
                        research_findings.append("")
                    
                except Exception as e:
                    logger.warning(f"⚠️  Research failed for {threat_type}: {e}")
                    research_findings.append(f"**{threat_type.upper()} RESEARCH:**")
                    research_findings.append(f"Research failed: {e}")
                    research_findings.append("")
            
            if not research_findings:
                return "No additional research findings available."
            
            return "\n".join(research_findings)
            
        except Exception as e:
            logger.error(f"❌ Research execution failed: {e}")
            return f"Research execution failed: {e}"
    
    def _extract_threat_types(self, analysis_content: str) -> list:
        """
        Extract threat types from analysis content for targeted research.
        
        Args:
            analysis_content: Content from security analysis
            
        Returns:
            List of threat types to research
        """
        try:
            # Validate input
            if not analysis_content or not isinstance(analysis_content, str):
                logger.warning("⚠️  Invalid content for threat type extraction")
                return []
            
            threat_types = []
            
            # Common threat patterns with improved matching
            threat_patterns = [
                ("SQL injection", ["sql injection", "sqli", "union select", "drop table"]),
                ("XSS", ["xss", "cross-site scripting", "script injection"]),
                ("Command injection", ["command injection", "code injection", "shell injection"]),
                ("Data exfiltration", ["data exfiltration", "data theft", "information disclosure"]),
                ("Prompt injection", ["prompt injection", "jailbreak", "prompt manipulation"]),
                ("CSRF", ["csrf", "cross-site request forgery"]),
                ("Authentication bypass", ["auth bypass", "authentication bypass", "login bypass"]),
                ("Privilege escalation", ["privilege escalation", "privesc", "elevation"]),
                ("DoS", ["dos", "ddos", "denial of service", "resource exhaustion"]),
                ("Buffer overflow", ["buffer overflow", "stack overflow", "heap overflow"]),
                ("Path traversal", ["path traversal", "directory traversal", "../"]),
                ("File inclusion", ["file inclusion", "lfi", "rfi"])
            ]
            
            content_lower = analysis_content.lower()
            for threat_name, patterns in threat_patterns:
                if any(pattern in content_lower for pattern in patterns):
                    threat_types.append(threat_name)
            
            # Remove duplicates and limit results
            unique_threats = list(dict.fromkeys(threat_types))
            return unique_threats[:5]  # Return top 5 threats
            
        except Exception as e:
            logger.error(f"❌ Threat type extraction failed: {e}")
            return []
    
    def _fallback_to_supervisor(self, message: str) -> Dict[str, Any]:
        """Fallback to supervisor with error message."""
        return {
            "messages": [
                HumanMessage(content=message, name="researcher")
            ],
            "next": "supervisor"
        } 