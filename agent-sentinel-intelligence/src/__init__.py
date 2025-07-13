"""
Agent Sentinel Intelligence Layer

A sophisticated multi-agent system for analyzing security reports and generating
comprehensive threat intelligence using LangGraph and advanced LLM orchestration.
"""

__version__ = "1.0.0"
__author__ = "Agent Sentinel Team"
__description__ = "Intelligence layer for Agent Sentinel security monitoring"

from .models.config import IntelligenceConfig
from .services.llm_service import LLMService
from .services.tracing_service import TracingService
from .services.research_service import ResearchService

__all__ = [
    "IntelligenceConfig", 
    "LLMService",
    "TracingService",
    "ResearchService"
] 