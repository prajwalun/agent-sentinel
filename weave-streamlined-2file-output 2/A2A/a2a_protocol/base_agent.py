"""
Base Agent class following A2A protocol standards
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class BaseAgent(BaseModel, ABC):
    """Base class for A2A agents following Google A2A protocol standards."""
    
    model_config = {
        'arbitrary_types_allowed': True,
        'extra': 'allow',
    }
    
    agent_name: str = Field(
        description='The name of the agent.',
    )
    
    description: str = Field(
        description="A brief description of the agent's purpose.",
    )
    
    content_types: List[str] = Field(
        description='Supported content types.',
        default_factory=lambda: ['text', 'text/plain']
    )
    
    url: str = Field(
        description='The endpoint URL for this agent.',
        default="http://localhost:8000/"
    )
    
    version: str = Field(
        description='The version of this agent.',
        default="1.0.0"
    )
    
    provider: Optional[str] = Field(
        description='The provider of this agent.',
        default="BlueGuard Security"
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialized = False
        logger.info(f"Initialized {self.agent_name}")
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with required resources."""
        pass
    
    @abstractmethod
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Invoke the agent with a query."""
        pass
    
    @abstractmethod
    async def stream(self, query: str, context_id: str, task_id: str):
        """Stream response from the agent."""
        pass
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Get the agent card in A2A format."""
        return {
            "name": self.agent_name,
            "description": self.description,
            "url": self.url,
            "provider": self.provider,
            "version": self.version,
            "capabilities": {
                "streaming": "True",
                "pushNotifications": "False",
                "stateTransitionHistory": "False"
            },
            "authentication": {
                "credentials": None,
                "schemes": ["public"]
            },
            "defaultInputModes": self.content_types,
            "defaultOutputModes": self.content_types,
            "skills": self.get_skills()
        }
    
    @abstractmethod
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get the skills/capabilities of this agent."""
        pass 