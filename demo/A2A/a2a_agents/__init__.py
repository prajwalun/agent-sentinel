"""
A2A Agents for BlueGuard Security System
Agents following Google A2A protocol standards
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