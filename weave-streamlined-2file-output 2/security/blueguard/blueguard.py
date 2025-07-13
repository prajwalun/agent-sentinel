"""
BlueGuard Security Monitoring System
Monitors agent interactions for security threats including agent-to-agent communication
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from heuristics import SecurityHeuristics
# REMOVED: from .a2a_threat_detector import A2AThreatDetector

logger = logging.getLogger(__name__)

class BlueGuard:
    """BlueGuard security monitoring system with unified threat detection (individual + A2A)"""
    
    def __init__(self):
        self.heuristics = SecurityHeuristics()
        # self.a2a_detector = A2AThreatDetector()  # REMOVE
        self.security_events = []
        self.alerts = []
        self.cross_agent_threats = []
        # --- Begin merged A2AThreatDetector state ---
        self.agent_data_flow = {}  # Track data flow between agents
        # --- End merged A2AThreatDetector state ---
        
        # Create logs directory
        Path("logs").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)
        
        logger.info("BlueGuard security monitoring initialized with unified threat detection")

    # --- Begin merged A2AThreatDetector methods ---
    def track_data_flow(self, interaction: Dict[str, Any]):
        agent_id = interaction.get("agent_id")
        result = interaction.get("result", "")
        timestamp = interaction.get("timestamp")
        if agent_id not in self.agent_data_flow:
            self.agent_data_flow[agent_id] = []
        
        # Convert result to string for tracking
        if isinstance(result, dict):
            result_str = str(result.get("content", result))
        else:
            result_str = str(result)
        
        self.agent_data_flow[agent_id].append({
            "timestamp": timestamp,
            "result": result_str,
            "tool": interaction.get("tool")
        })
        logger.debug(f"Tracked data flow for {agent_id}: {result_str[:50]}...")

    def detect_cross_agent_threats(self, interaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        threats = []
        agent_id = interaction.get("agent_id")
        params = interaction.get("params", {})
        for key, value in params.items():
            if isinstance(value, str):
                source_agent = self._find_data_source(value)
                if source_agent and source_agent != agent_id and agent_id is not None:
                    cross_agent_threats = self._analyze_cross_agent_threat(
                        value, agent_id, source_agent, key
                    )
                    threats.extend(cross_agent_threats)
        return threats

    def _find_data_source(self, value: str) -> Optional[str]:
        for agent_id, data_flows in self.agent_data_flow.items():
            for data_flow in data_flows:
                if value in data_flow["result"] or data_flow["result"] in value:
                    return agent_id
        return None

    def _analyze_cross_agent_threat(self, value: str, target_agent: str, source_agent: str, param_key: str) -> List[Dict[str, Any]]:
        threats = []
        detected_threats = self.heuristics.analyze_text(value, f"cross_agent:{source_agent}->{target_agent}")
        for threat in detected_threats:
            enhanced_threat = {
                **threat,
                "cross_agent": True,
                "source_agent": source_agent,
                "target_agent": target_agent,
                "param_key": param_key,
                "threat_type": "cross_agent_data_flow",
                "description": f"Threat propagated from {source_agent} to {target_agent} via {param_key}"
            }
            threats.append(enhanced_threat)
            logger.warning(f"Cross-agent threat detected: {source_agent} -> {target_agent}: {threat['type']}")
        return threats

    def detect_multi_agent_attack_chains(self, interactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        attack_chains = []
        time_windows = self._group_by_time_windows(interactions, window_seconds=30)
        for window_start, window_interactions in time_windows.items():
            malicious_agents = []
            for interaction in window_interactions:
                if interaction.get("security_flags"):
                    malicious_agents.append(interaction.get("agent_id"))
            if len(malicious_agents) > 1:
                attack_chain = {
                    "timestamp": window_start,
                    "type": "multi_agent_attack_chain",
                    "agents_involved": list(set(malicious_agents)),
                    "interactions": window_interactions,
                    "severity": "high",
                    "description": f"Coordinated attack involving {len(set(malicious_agents))} agents"
                }
                attack_chains.append(attack_chain)
                logger.warning(f"Multi-agent attack chain detected: {malicious_agents}")
        return attack_chains

    def _group_by_time_windows(self, interactions: List[Dict[str, Any]], window_seconds: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        windows = {}
        for interaction in interactions:
            timestamp = interaction.get("timestamp")
            if timestamp:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                window_start = dt.replace(second=(dt.second // window_seconds) * window_seconds, microsecond=0)
                window_key = window_start.isoformat()
                if window_key not in windows:
                    windows[window_key] = []
                windows[window_key].append(interaction)
        return windows

    def get_a2a_threat_summary(self) -> Dict[str, Any]:
        return {
            "cross_agent_threats": len(self.cross_agent_threats),
            "data_flows_tracked": len(self.agent_data_flow),
            "agents_with_data_flow": list(self.agent_data_flow.keys()),
            "threat_types": self._count_a2a_threat_types()
        }

    def _count_a2a_threat_types(self) -> Dict[str, int]:
        threat_counts = {}
        for threat in self.cross_agent_threats:
            threat_type = threat.get("type", "unknown")
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        return threat_counts
    # --- End merged A2AThreatDetector methods ---

    async def analyze_interaction(self, interaction: Dict[str, Any]) -> List[str]:
        """Analyze a single agent interaction for security threats including A2A threats"""
        threats = []
        
        # Check if this is an agent card analysis
        if interaction.get("analysis_type") == "agent_card":
            return await self.analyze_agent_card(interaction)
        
        # Track data flow for A2A threat detection
        self.track_data_flow(interaction)
        
        # Analyze parameters
        params = interaction.get("params", {})
        for key, value in params.items():
            if isinstance(value, str):
                param_threats = self.heuristics.analyze_text(value, f"parameter:{key}")
                threats.extend(param_threats)
        
        # Analyze result
        result = interaction.get("result")
        if isinstance(result, str):
            result_threats = self.heuristics.analyze_text(result, "result")
            threats.extend(result_threats)
        elif isinstance(result, dict):
            # If result is a dict, analyze its content field
            content = result.get("content", "")
            if isinstance(content, str):
                result_threats = self.heuristics.analyze_text(content, "result_content")
                threats.extend(result_threats)
        
        # Detect cross-agent threats
        cross_agent_threats = self.detect_cross_agent_threats(interaction)
        if cross_agent_threats:
            threats.extend(cross_agent_threats)
            self.cross_agent_threats.extend(cross_agent_threats)
            logger.warning(f"Cross-agent threats detected in {interaction.get('agent_id')}: {len(cross_agent_threats)} threats")
        
        # Log security events
        if threats:
            event = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": interaction.get("agent_id"),
                "tool": interaction.get("tool"),
                "threats": threats,
                "interaction": interaction,
                "has_cross_agent_threats": any(t.get("cross_agent", False) for t in threats)
            }
            self.security_events.append(event)
            
            # Create alert
            alert = {
                "timestamp": datetime.now().isoformat(),
                "severity": "high" if any(t.get("severity") == "high" for t in threats) else "medium",
                "description": f"Security threats detected in {interaction.get('agent_id')} interaction",
                "threats": threats,
                "agent_id": interaction.get("agent_id"),
                "tool": interaction.get("tool"),
                "cross_agent": any(t.get("cross_agent", False) for t in threats)
            }
            self.alerts.append(alert)
            
            logger.warning(f"Security threats detected in {interaction.get('agent_id')}: {len(threats)} threats")
        
        return threats

    async def analyze_agent_card(self, interaction: Dict[str, Any]) -> List[str]:
        """Analyze agent card for security threats"""
        threats = []
        agent_id = interaction.get("agent_id")
        content = interaction.get("content", "")
        
        if not content:
            return threats
        
        # Analyze the agent card content for threats
        card_threats = self.heuristics.analyze_text(content, f"agent_card:{agent_id}")
        
        if card_threats:
            threats.extend(card_threats)
            
            # Log security event for agent card threats
            event = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "analysis_type": "agent_card",
                "threats": card_threats,
                "content": content,
                "has_cross_agent_threats": False
            }
            self.security_events.append(event)
            
            # Create alert for agent card threats
            alert = {
                "timestamp": datetime.now().isoformat(),
                "severity": "high" if any(t.get("severity") == "high" for t in card_threats) else "medium",
                "description": f"Security threats detected in {agent_id} agent card",
                "threats": card_threats,
                "agent_id": agent_id,
                "tool": "agent_card",
                "cross_agent": False
            }
            self.alerts.append(alert)
            
            logger.warning(f"Security threats detected in {agent_id} agent card: {len(card_threats)} threats")
        
        return threats

    async def analyze_interaction_log(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze entire interaction log for security threats including A2A threats"""
        total_threats = 0
        all_threats = []
        
        for interaction in interactions:
            threats = await self.analyze_interaction(interaction)
            total_threats += len(threats)
            all_threats.extend(threats)
        
        # Detect multi-agent attack chains
        attack_chains = self.detect_multi_agent_attack_chains(interactions)
        
        # Get A2A threat summary
        a2a_summary = self.get_a2a_threat_summary()
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_interactions": len(interactions),
            "total_threats": total_threats,
            "security_events": len(self.security_events),
            "alerts": len(self.alerts),
            "cross_agent_threats": len(self.cross_agent_threats),
            "multi_agent_attack_chains": len(attack_chains),
            "threats_by_type": self._count_threats_by_type(all_threats),
            "threats_by_agent": self._count_threats_by_agent(interactions),
            "a2a_threat_summary": a2a_summary,
            "events": self.security_events,
            "alerts": self.alerts,
            "attack_chains": attack_chains
        }
        
        return report
    
    def _count_threats_by_type(self, threats: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count threats by type"""
        threat_counts = {}
        for threat in threats:
            threat_type = threat.get("type", "unknown")
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        return threat_counts
    
    def _count_threats_by_agent(self, interactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count threats by agent"""
        agent_threats = {}
        for interaction in interactions:
            agent_id = interaction.get("agent_id", "unknown")
            threats = interaction.get("security_flags", [])
            agent_threats[agent_id] = agent_threats.get(agent_id, 0) + len(threats)
        return agent_threats 