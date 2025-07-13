"""
A2A Client for connecting to A2A servers following Google A2A protocol standards
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class A2AClient:
    """A2A Client for connecting to A2A servers."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.connected = False
        logger.info(f"A2A Client initialized for {server_url}")
    
    async def connect(self) -> None:
        """Connect to the A2A server."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        try:
            # Test connection
            async with self.session.get(f"{self.server_url}/health") as response:
                if response.status == 200:
                    self.connected = True
                    logger.info(f"A2A Client connected to {self.server_url}")
                else:
                    raise ConnectionError(f"Server returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to connect to A2A server: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from the A2A server."""
        if self.session:
            await self.session.close()
            self.session = None
        self.connected = False
        logger.info("A2A Client disconnected")
    
    async def get_agent_card(self, agent_name: str) -> Dict[str, Any]:
        """Get an agent card from the server."""
        if not self.connected:
            await self.connect()
        
        try:
            async with self.session.get(f"{self.server_url}/agents/{agent_name}/card") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"Agent {agent_name} not found")
        except Exception as e:
            logger.error(f"Error getting agent card for {agent_name}: {e}")
            raise
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents."""
        if not self.connected:
            await self.connect()
        
        try:
            async with self.session.get(f"{self.server_url}/agents") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError("Failed to list agents")
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            raise
    
    async def invoke_agent(
        self, 
        agent_name: str, 
        query: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Invoke an agent with a query."""
        if not self.connected:
            await self.connect()
        
        try:
            payload = {
                "query": query,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{self.server_url}/agents/{agent_name}/invoke",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"Failed to invoke agent {agent_name}")
        except Exception as e:
            logger.error(f"Error invoking agent {agent_name}: {e}")
            raise
    
    async def stream_agent(
        self, 
        agent_name: str, 
        query: str, 
        context_id: str
    ):
        """Stream response from an agent."""
        if not self.connected:
            await self.connect()
        
        try:
            payload = {
                "query": query,
                "context_id": context_id,
                "timestamp": datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{self.server_url}/agents/{agent_name}/stream",
                json=payload
            ) as response:
                if response.status == 200:
                    async for line in response.content:
                        if line:
                            try:
                                yield json.loads(line.decode('utf-8'))
                            except json.JSONDecodeError:
                                continue
                else:
                    raise ValueError(f"Failed to stream from agent {agent_name}")
        except Exception as e:
            logger.error(f"Error streaming from agent {agent_name}: {e}")
            raise
    
    async def find_agent_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Find agents suitable for a specific task."""
        if not self.connected:
            await self.connect()
        
        try:
            payload = {
                "task_description": task_description,
                "timestamp": datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{self.server_url}/find_agents",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError("Failed to find agents for task")
        except Exception as e:
            logger.error(f"Error finding agents for task: {e}")
            raise 