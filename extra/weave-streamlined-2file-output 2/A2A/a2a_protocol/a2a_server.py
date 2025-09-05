"""
A2A Server for hosting agents following Google A2A protocol standards
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class A2AServer:
    """A2A Server for hosting and managing agents."""
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.agents: Dict[str, Any] = {}
        self.agent_cards: Dict[str, Dict[str, Any]] = {}
        self.interaction_log = []
        self._running = False
        logger.info(f"A2A Server initialized on {host}:{port}")
    
    def register_agent(self, agent) -> None:
        """Register an agent with the A2A server."""
        self.agents[agent.agent_name] = agent
        self.agent_cards[agent.agent_name] = agent.get_agent_card()
        logger.info(f"Registered agent: {agent.agent_name}")
    
    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from the A2A server."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.agent_cards[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
    
    def get_agent(self, name: str) -> Optional[Any]:
        """Get an agent by name."""
        return self.agents.get(name)
    
    def get_agent_card(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an agent card by name."""
        return self.agent_cards.get(name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents."""
        return list(self.agent_cards.values())
    
    async def invoke_agent(
        self, 
        agent_name: str, 
        query: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Invoke an agent with a query."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        # Log the interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_name,
            "query": query,
            "session_id": session_id,
            "type": "invoke"
        }
        
        try:
            result = await agent.invoke(query, session_id)
            interaction["result"] = result
            interaction["success"] = "True"
        except Exception as e:
            interaction["result"] = str(e)
            interaction["success"] = "False"
            raise
        
        self.interaction_log.append(interaction)
        return result
    
    async def stream_agent(
        self, 
        agent_name: str, 
        query: str, 
        context_id: str
    ):
        """Stream response from an agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        agent = self.agents[agent_name]
        
        # Log the interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_name,
            "query": query,
            "context_id": context_id,
            "type": "stream"
        }
        
        try:
            async for chunk in agent.stream(query, context_id, f"task_{context_id}"):
                yield chunk
            interaction["success"] = "True"
        except Exception as e:
            interaction["error"] = str(e)
            interaction["success"] = "False"
            raise
        finally:
            self.interaction_log.append(interaction)
    
    async def find_agents_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Find agents suitable for a specific task."""
        # Simple keyword matching - in a real implementation, this would use
        # more sophisticated matching algorithms
        matching_agents = []
        
        for agent_name, agent_card in self.agent_cards.items():
            # Check skills and tags for matches
            for skill in agent_card.get("skills", []):
                tags = skill.get("tags", [])
                description = skill.get("description", "").lower()
                
                task_lower = task_description.lower()
                
                # Check if any tags or description match the task
                if any(tag.lower() in task_lower for tag in tags) or \
                   any(word in description for word in task_lower.split()):
                    matching_agents.append(agent_card)
                    break
        
        return matching_agents
    
    async def start_server(self) -> None:
        """Start the A2A server."""
        if self._running:
            logger.warning("A2A Server is already running")
            return
        
        self._running = True
        logger.info(f"A2A Server starting on {self.host}:{self.port}")
        
        # In a real implementation, this would start a FastAPI server
        # For demo purposes, we'll just log that it's ready
        logger.info("A2A Server ready for agent interactions")
    
    async def stop_server(self) -> None:
        """Stop the A2A server."""
        if not self._running:
            logger.warning("A2A Server is not running")
            return
        
        self._running = False
        logger.info("A2A Server stopped")
    
    def get_interaction_log(self) -> List[Dict[str, Any]]:
        """Get the interaction log."""
        return self.interaction_log.copy()
    
    def clear_interaction_log(self) -> None:
        """Clear the interaction log."""
        self.interaction_log.clear()
        logger.info("Interaction log cleared")
    
    def save_interaction_log(self, filepath: str) -> None:
        """Save the interaction log to a file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.interaction_log, f, indent=2)
        
        logger.info(f"Interaction log saved to {filepath}") 