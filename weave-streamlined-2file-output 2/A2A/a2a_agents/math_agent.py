"""
Math Agent following A2A protocol standards
Provides mathematical operations through A2A framework
"""

import asyncio
import logging
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from a2a_protocol.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MathAgent(BaseAgent):
    """Math agent for performing mathematical operations following A2A protocol standards."""
    
    def __init__(self):
        super().__init__(
            agent_name="math_agent",
            description="Performs basic mathematical operations including addition, subtraction, multiplication, and division",
            url="http://localhost:10101/",
            version="1.0.0",
            provider="BlueGuard Security"
        )
        self._initialized = False
        logger.info(f"MathAgent initialized: {self.agent_name}")
    
    async def initialize(self) -> None:
        """Initialize the math agent."""
        if not self._initialized:
            self._initialized = True
            logger.info(f"MathAgent {self.agent_name} initialized")
    
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Invoke the math agent with a query."""
        await self.initialize()
        
        # Parse the query to determine the operation
        query_lower = query.lower()
        
        if "add" in query_lower or "+" in query:
            # Extract numbers from query
            numbers = self._extract_numbers(query)
            if len(numbers) >= 2:
                result = numbers[0] + numbers[1]
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f'Result: {result}',
                    'operation': 'add',
                    'numbers': numbers[:2],
                    'result': result
                }
        
        elif "subtract" in query_lower or "-" in query:
            numbers = self._extract_numbers(query)
            if len(numbers) >= 2:
                result = numbers[0] - numbers[1]
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f'Result: {result}',
                    'operation': 'subtract',
                    'numbers': numbers[:2],
                    'result': result
                }
        
        elif "multiply" in query_lower or "*" in query:
            numbers = self._extract_numbers(query)
            if len(numbers) >= 2:
                result = numbers[0] * numbers[1]
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f'Result: {result}',
                    'operation': 'multiply',
                    'numbers': numbers[:2],
                    'result': result
                }
        
        elif "divide" in query_lower or "/" in query:
            numbers = self._extract_numbers(query)
            if len(numbers) >= 2 and numbers[1] != 0:
                result = numbers[0] / numbers[1]
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f'Result: {result}',
                    'operation': 'divide',
                    'numbers': numbers[:2],
                    'result': result
                }
        
        return {
            'response_type': 'text',
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'I can help with basic math operations. Please provide two numbers and an operation (add, subtract, multiply, divide).',
            'error': True
        }
    
    async def execute_skill(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific skill - wrapper for invoke method to match expected interface."""
        await self.initialize()
        
        if skill_name == "add" and "a" in params and "b" in params:
            result = float(params["a"]) + float(params["b"])
            return {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Result: {result}',
                'operation': 'add',
                'numbers': [float(params["a"]), float(params["b"])],
                'result': result
            }
        elif skill_name == "subtract" and "a" in params and "b" in params:
            result = float(params["a"]) - float(params["b"])
            return {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Result: {result}',
                'operation': 'subtract',
                'numbers': [float(params["a"]), float(params["b"])],
                'result': result
            }
        elif skill_name == "multiply" and "a" in params and "b" in params:
            result = float(params["a"]) * float(params["b"])
            return {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': f'Result: {result}',
                'operation': 'multiply',
                'numbers': [float(params["a"]), float(params["b"])],
                'result': result
            }
        elif skill_name == "divide" and "a" in params and "b" in params:
            if float(params["b"]) != 0:
                result = float(params["a"]) / float(params["b"])
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': f'Result: {result}',
                    'operation': 'divide',
                    'numbers': [float(params["a"]), float(params["b"])],
                    'result': result
                }
            else:
                return {
                    'response_type': 'error',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': 'Error: Division by zero is not allowed',
                    'error': True
                }
        else:
            return {
                'response_type': 'error',
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'Unknown skill: {skill_name}. Available skills: add, subtract, multiply, divide',
                'error': True
            }
    
    async def stream(self, query: str, context_id: str, task_id: str):
        """Stream response from the math agent."""
        await self.initialize()
        
        # First yield a processing message
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Processing mathematical operation...',
        }
        
        # Process the query
        result = await self.invoke(query, f"{context_id}_{task_id}")
        
        # Yield the final result
        yield result
    
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get the skills/capabilities of this agent."""
        return [
            {
                "id": "mathematical_operations",
                "name": "Mathematical Operations",
                "description": "Performs basic arithmetic operations on numbers",
                "tags": [
                    "math",
                    "arithmetic",
                    "calculation",
                    "addition",
                    "subtract",
                    "multiplication",
                    "division"
                ],
                "examples": [
                    "Add 5 and 3",
                    "Multiply 6 by 7",
                    "Divide 20 by 4",
                    "Subtract 10 from 15"
                ],
                "inputModes": None,
                "outputModes": None
            }
        ]
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numbers from text."""
        import re
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(num) for num in numbers] 