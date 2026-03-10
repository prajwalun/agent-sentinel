"""
AgentState definition for the multi-agent LangGraph workflow.

Tracks messages, workflow phase, and iteration metadata to support
the iterative analyze-research-report-validate loop.
"""

from typing import Annotated, List, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    phase: str
    research_done: bool
    iteration_count: int
    validator_feedback: str
