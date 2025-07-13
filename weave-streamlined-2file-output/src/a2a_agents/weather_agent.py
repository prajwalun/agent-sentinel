"""
Weather Agent using Real A2A SDK
Provides weather information through A2A framework
"""

from src.a2a_sdk import Agent, Tool, ToolCall, create_tool
from typing import Dict, Any
import logging
from agent_sentinel import sentinel

logger = logging.getLogger(__name__)

@sentinel
class WeatherAgent(Agent):
    """Weather agent for providing weather information using Real A2A SDK"""
    
    def __init__(self):
        tools = [
            create_tool(
                name="get_weather",
                description="Get current weather for a city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"]
                }
            ),
            create_tool(
                name="get_forecast",
                description="Get weather forecast for a city",
                parameters={
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"}
                    },
                    "required": ["city"]
                }
            )
        ]
        
        super().__init__(
            name="weather_agent",
            description="Provides weather information for cities",
            tools=tools
        )
        
        # Register tool handlers
        self.register_tool_handler("get_weather", self.get_weather)
        self.register_tool_handler("get_forecast", self.get_forecast)
    
    async def get_weather(self, tool_call: ToolCall) -> str:
        """Get current weather for a city"""
        city = tool_call.parameters.get("city", "Unknown")
        result = f"Weather in {city}: 22°C, Partly Cloudy"
        logger.info(f"WeatherAgent.get_weather({city}) = {result}")
        return result
    
    async def get_forecast(self, tool_call: ToolCall) -> str:
        """Get weather forecast for a city"""
        city = tool_call.parameters.get("city", "Unknown")
        result = f"Forecast for {city}: Sunny tomorrow, Rain on Wednesday"
        logger.info(f"WeatherAgent.get_forecast({city}) = {result}")
        return result 