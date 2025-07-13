"""
Agent Runner for managing agent execution following A2A protocol standards
"""

import asyncio
import logging
from typing import Dict, Any, AsyncIterable
from collections.abc import AsyncIterable

logger = logging.getLogger(__name__)

class AgentRunner:
    """Agent runner for managing agent execution and streaming responses."""
    
    def __init__(self):
        self.active_sessions = {}
        logger.info("AgentRunner initialized")
    
    async def run_stream(
        self, 
        agent, 
        query: str, 
        context_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Run an agent with streaming response."""
        try:
            logger.info(f"Running agent {agent.agent_name} for context {context_id}")
            
            # Initialize agent if not already done
            if not hasattr(agent, '_initialized') or not agent._initialized:
                await agent.initialize()
                agent._initialized = True
            
            # Stream the response
            async for chunk in agent.stream(query, context_id, f"task_{context_id}"):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error running agent {agent.agent_name}: {e}")
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Error: {str(e)}',
                'error': True
            }
    
    async def run_sync(
        self, 
        agent, 
        query: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Run an agent synchronously and return the result."""
        try:
            logger.info(f"Running agent {agent.agent_name} for session {session_id}")
            
            # Initialize agent if not already done
            if not hasattr(agent, '_initialized') or not agent._initialized:
                await agent.initialize()
                agent._initialized = True
            
            # Get the result
            result = await agent.invoke(query, session_id)
            return result
            
        except Exception as e:
            logger.error(f"Error running agent {agent.agent_name}: {e}")
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Error: {str(e)}',
                'error': True
            }
    
    def register_session(self, session_id: str, agent_name: str):
        """Register an active session."""
        self.active_sessions[session_id] = {
            'agent_name': agent_name,
            'start_time': asyncio.get_event_loop().time()
        }
        logger.info(f"Registered session {session_id} for agent {agent_name}")
    
    def unregister_session(self, session_id: str):
        """Unregister an active session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Unregistered session {session_id}")
    
    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active sessions."""
        return self.active_sessions.copy() 