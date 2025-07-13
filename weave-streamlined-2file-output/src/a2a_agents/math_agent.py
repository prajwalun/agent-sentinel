"""
Math Agent using Real A2A SDK
Provides mathematical operations through A2A framework
"""

from src.a2a_sdk import Agent, Tool, ToolCall, create_tool
from typing import Dict, Any
import logging
from agent_sentinel import sentinel

logger = logging.getLogger(__name__)

@sentinel
class MathAgent(Agent):
    """Math agent for performing mathematical operations using Real A2A SDK"""
    
    def __init__(self):
        tools = [
            create_tool(
                name="add",
                description="Add two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            ),
            create_tool(
                name="subtract",
                description="Subtract two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            ),
            create_tool(
                name="multiply",
                description="Multiply two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            ),
            create_tool(
                name="divide",
                description="Divide two numbers",
                parameters={
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"}
                    },
                    "required": ["a", "b"]
                }
            )
        ]
        
        super().__init__(
            name="math_agent",
            description="Performs basic mathematical operations",
            tools=tools
        )
        
        # Register tool handlers
        self.register_tool_handler("add", self.add)
        self.register_tool_handler("subtract", self.subtract)
        self.register_tool_handler("multiply", self.multiply)
        self.register_tool_handler("divide", self.divide)
    
    async def add(self, tool_call: ToolCall) -> str:
        """Add two numbers"""
        a = tool_call.parameters.get("a", 0)
        b = tool_call.parameters.get("b", 0)
        result = a + b
        logger.info(f"MathAgent.add({a}, {b}) = {result}")
        return f"Result: {result}"
    
    async def subtract(self, tool_call: ToolCall) -> str:
        """Subtract two numbers"""
        a = tool_call.parameters.get("a", 0)
        b = tool_call.parameters.get("b", 0)
        result = a - b
        logger.info(f"MathAgent.subtract({a}, {b}) = {result}")
        return f"Result: {result}"
    
    async def multiply(self, tool_call: ToolCall) -> str:
        """Multiply two numbers"""
        a = tool_call.parameters.get("a", 0)
        b = tool_call.parameters.get("b", 0)
        result = a * b
        logger.info(f"MathAgent.multiply({a}, {b}) = {result}")
        return f"Result: {result}"
    
    async def divide(self, tool_call: ToolCall) -> str:
        """Divide two numbers"""
        a = tool_call.parameters.get("a", 0)
        b = tool_call.parameters.get("b", 1)
        if b == 0:
            raise ValueError("Division by zero")
        result = a / b
        logger.info(f"MathAgent.divide({a}, {b}) = {result}")
        return f"Result: {result}" 