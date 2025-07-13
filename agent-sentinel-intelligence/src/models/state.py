"""
AgentState definition for LangGraph 0.5.x+.
"""
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    phase: str
    research_done: bool
    # Add more fields as needed for your workflow 