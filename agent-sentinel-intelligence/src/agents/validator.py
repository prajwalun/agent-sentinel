"""
Validator Agent for Agent Sentinel Intelligence Layer.

Reviews and validates the final security report for quality and completeness.
"""

import logging
from typing import Literal, Dict, Any
try:
    from pydantic import BaseModel, Field
except ImportError:
    from pydantic.v1 import BaseModel, Field
from langchain_core.messages import HumanMessage
from ..models.state import AgentState

from ..services.llm_service import LLMService
from ..services.tracing_service import TracingService

logger = logging.getLogger(__name__)


class Validator(BaseModel):
    """Validator decision model."""
    
    next: Literal["supervisor", "FINISH"] = Field(
        description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate."
    )
    
    reason: str = Field(
        description="Detailed explanation of the validation decision and any issues found."
    )


class ValidatorAgent:
    """Validator agent that reviews and validates the final report."""
    
    def __init__(self, llm_service: LLMService, tracing_service: TracingService):
        """
        Initialize the validator agent.
        
        Args:
            llm_service: LLM service for validation
            tracing_service: Tracing service for monitoring
        """
        self.llm_service = llm_service
        self.tracing_service = tracing_service
        
        self.system_prompt = """
        You are a Security Report Validator Specialist. Your role is to review and validate 
        security reports for quality, completeness, and accuracy.

        **Validation Criteria:**
        1. **Completeness** - All required sections are present and comprehensive
        2. **Accuracy** - Technical details are correct and well-documented
        3. **Actionability** - Recommendations are specific and implementable
        4. **Clarity** - Report is well-structured and easy to understand
        5. **Professionalism** - Language and formatting are appropriate for the audience

        **Required Sections:**
        - Executive Summary
        - Threat Analysis
        - Technical Details
        - Risk Assessment
        - Recommendations
        - Research Context (if applicable)

        **Quality Standards:**
        - Clear threat categorization and severity levels
        - Specific technical details and attack methods
        - Actionable recommendations with priority levels
        - Professional formatting and structure
        - Appropriate level of detail for target audience

        **Decision Guidelines:**
        - If the report meets all quality standards, recommend FINISH
        - If significant issues are found, recommend returning to supervisor for improvement
        - Provide specific feedback on what needs to be improved

        Your goal is to ensure the final report is of the highest quality and ready for delivery.
        """
    
    def execute(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the validation process.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dict with messages and next step
        """
        try:
            # Get the last message (should be the report)
            messages = state.get("messages", [])
            last_message = messages[-1] if messages else None
            
            if not last_message:
                logger.warning("⚠️  No report found for validation")
                return self._finish_workflow("No report available for validation")
            
            # Create messages for LLM
            messages_for_llm = self.llm_service.create_messages(
                system_prompt=self.system_prompt,
                user_prompt=f"""
                Validate this security report for quality, completeness, and accuracy:

                {last_message.content}

                Provide a structured validation decision with specific feedback on the report quality.
                """
            )
            
            # Get validation decision from LLM
            response = self.llm_service.invoke_structured(
                messages=messages_for_llm,
                output_parser=Validator
            )
            
            goto = response.next
            reason = response.reason
            
            # Log validation decision
            logger.info(f"Validation decision: {goto} - {reason}")
            
            # Trace the validation
            if self.tracing_service.is_enabled():
                self.tracing_service.log_workflow_step(
                    step_name="validation",
                    content_length=len(reason),
                    status="completed"
                )
            
            # Handle the decision
            if goto == "FINISH":
                print("--- Workflow Complete: Validation Passed ---")
                return {
                    "messages": [
                        HumanMessage(content=reason, name="validator")
                    ],
                    "next": "__end__"
                }
            else:
                print(f"--- Workflow Transition: Validator → Supervisor ---")
                return {
                    "messages": [
                        HumanMessage(content=reason, name="validator")
                    ],
                    "next": "supervisor"
                }
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return self._finish_workflow(f"Validation failed: {e}")
    
    def _finish_workflow(self, reason: str) -> Dict[str, Any]:
        """Finish the workflow with the given reason."""
        return {
            "messages": [
                HumanMessage(content=reason, name="validator")
            ],
            "next": "__end__"
        } 