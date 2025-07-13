"""
Real A2A Agents for BlueGuard Security System
Agents using Real A2A SDK implementation
"""

from .math_agent import MathAgent
from .weather_agent import WeatherAgent
from .translation_agent import TranslationAgent
from .malicious_agent import MaliciousAgent

__all__ = [
    "MathAgent",
    "WeatherAgent", 
    "TranslationAgent",
    "MaliciousAgent"
] 