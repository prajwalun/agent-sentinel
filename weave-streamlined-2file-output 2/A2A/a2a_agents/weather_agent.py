"""
Weather Agent following A2A protocol standards
Provides weather information and forecasts through A2A framework
"""

import asyncio
import logging
import random
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from a2a_protocol.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Weather agent for providing weather information following A2A protocol standards."""
    
    def __init__(self):
        super().__init__(
            agent_name="weather_agent",
            description="Provides current weather information and forecasts for cities worldwide",
            url="http://localhost:10102/",
            version="1.0.0",
            provider="BlueGuard Security"
        )
        self._initialized = False
        self._weather_data = {
            "London": {"temperature": 18, "condition": "Cloudy", "humidity": 75},
            "New York": {"temperature": 22, "condition": "Sunny", "humidity": 60},
            "Tokyo": {"temperature": 25, "condition": "Rainy", "humidity": 80},
            "Paris": {"temperature": 20, "condition": "Partly Cloudy", "humidity": 70},
            "Sydney": {"temperature": 28, "condition": "Clear", "humidity": 65}
        }
        logger.info(f"WeatherAgent initialized: {self.agent_name}")
    
    async def initialize(self) -> None:
        """Initialize the weather agent."""
        if not self._initialized:
            self._initialized = True
            logger.info(f"WeatherAgent {self.agent_name} initialized")
    
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Invoke the weather agent with a query."""
        await self.initialize()
        
        query_lower = query.lower()
        
        # Extract city name from query
        city = self._extract_city(query)
        
        if not city:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': "Please specify a city name for weather information",
                'error': True
            }
        
        # Get weather data for the city
        if city in self._weather_data:
            weather = self._weather_data[city]
            response = f"Weather in {city}: {weather['temperature']}°C, {weather['condition']}, Humidity: {weather['humidity']}%"
            
            return {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': response,
                'city': city,
                'weather_data': weather
            }
        else:
            # Generate mock weather data for unknown cities
            mock_weather = {
                "temperature": random.randint(10, 35),
                "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Clear"]),
                "humidity": random.randint(40, 90)
            }
            
            response = f"Weather in {city}: {mock_weather['temperature']}°C, {mock_weather['condition']}, Humidity: {mock_weather['humidity']}%"
            
            return {
                'response_type': 'data',
                'is_task_complete': True,
                'require_user_input': False,
                'content': response,
                'city': city,
                'weather_data': mock_weather,
                'note': 'Mock data generated'
            }
    
    async def stream(self, query: str, context_id: str, task_id: str):
        """Stream response from the weather agent."""
        await self.initialize()
        
        # First yield a processing message
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Fetching weather information...',
        }
        
        # Process the query
        result = await self.invoke(query, f"{context_id}_{task_id}")
        
        # Yield the final result
        yield result
    
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get the skills/capabilities of this agent."""
        return [
            {
                "id": "weather_information",
                "name": "Weather Information",
                "description": "Retrieves current weather conditions and forecasts for specified cities",
                "tags": [
                    "weather",
                    "forecast",
                    "temperature",
                    "climate",
                    "meteorology"
                ],
                "examples": [
                    "Get weather for London",
                    "What's the forecast for New York?",
                    "Current weather in Tokyo"
                ],
                "inputModes": None,
                "outputModes": None
            }
        ]
    
    def _extract_city(self, text: str) -> str:
        """Extract city name from text."""
        import re
        
        # Common city patterns
        cities = ["London", "New York", "Tokyo", "Paris", "Sydney", "Berlin", "Moscow", "Beijing", "Mumbai", "Cairo"]
        
        for city in cities:
            if city.lower() in text.lower():
                return city
        
        # Try to extract any capitalized word that might be a city
        words = text.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                return word
        
        return "" 