"""
Enterprise Security Analysis Workflow for Agent Sentinel Intelligence Layer.

Orchestrates a sophisticated multi-agent system for comprehensive security report analysis
using LangGraph and advanced LLM orchestration with enterprise-grade features.
"""

import logging
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
# Command import removed - using simpler approach

from .models.state import AgentState
from .models.config import IntelligenceConfig
from .services.llm_service import LLMService
from .services.tracing_service import TracingService
from .services.research_service import ResearchService
from .agents.supervisor import SupervisorAgent
from .agents.analyzer import SecurityAnalyzerAgent
from .agents.researcher import WebResearcherAgent
from .agents.reporter import ReportGeneratorAgent
from .agents.validator import ValidatorAgent

logger = logging.getLogger(__name__)


class SecurityAnalysisWorkflow:
    """Enterprise workflow for security analysis using multi-agent system."""
    
    def __init__(self, config: IntelligenceConfig):
        self.config = config
        self.llm_service = LLMService(config.llm)
        self.tracing_service = TracingService(config.tracing)
        self.research_service = ResearchService(config.research)
        
        # Initialize agents
        self.supervisor_agent = SupervisorAgent(self.llm_service, self.tracing_service)
        self.analyzer_agent = SecurityAnalyzerAgent(self.llm_service, self.tracing_service)
        self.researcher_agent = WebResearcherAgent(
            self.llm_service, 
            self.tracing_service, 
            self.research_service
        )
        self.reporter_agent = ReportGeneratorAgent(self.llm_service, self.tracing_service)
        self.validator_agent = ValidatorAgent(self.llm_service, self.tracing_service)
        
        # Create workflow graph
        self.graph = self._create_workflow_graph()
        self.app = self.graph.compile()
        
        # Workflow state tracking
        self.execution_history = []
        self.start_time = None
        self.end_time = None
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the workflow graph with proper agent connections."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("supervisor", self.supervisor_agent.execute)
        graph.add_node("analyzer", self.analyzer_agent.execute)
        graph.add_node("researcher", self.researcher_agent.execute)
        graph.add_node("reporter", self.reporter_agent.execute)
        graph.add_node("validator", self.validator_agent.execute)
        
        # Add edges with conditional routing
        graph.add_edge(START, "supervisor")
        
        # Supervisor can route to any agent or finish
        graph.add_conditional_edges(
            "supervisor",
            self._supervisor_router,
            {
                "analyzer": "analyzer",
                "researcher": "researcher", 
                "reporter": "reporter",
                "validator": "validator",
                "__end__": END
            }
        )
        
        # Analyzer always goes to supervisor for next decision
        graph.add_edge("analyzer", "supervisor")
        
        # Researcher always goes to supervisor for next decision
        graph.add_edge("researcher", "supervisor")
        
        # Reporter always goes to validator
        graph.add_edge("reporter", "validator")
        
        # Validator can finish or go back to supervisor
        graph.add_conditional_edges(
            "validator",
            self._validator_router,
            {
                "supervisor": "supervisor",
                "__end__": END
            }
        )
        
        return graph
    
    def _supervisor_router(self, state: AgentState) -> str:
        """Route from supervisor to next agent. Use strict phase-based workflow to prevent loops."""
        # Get current phase from state, default to 'analyzer' if not set
        current_phase = state.get("phase", "analyzer")
        research_done = state.get("research_done", False)
        
        logger.info(f"Supervisor routing: current_phase={current_phase}, research_done={research_done}")
        
        # Strict phase progression to prevent loops
        if current_phase == "analyzer":
            # After analysis, determine if research is needed
            messages = state.get("messages", [])
            needs_research = False
            
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, 'content') and last_message.content:
                    content = last_message.content.lower()
                    # Check for keywords that indicate research is needed
                    research_keywords = [
                        "novel", "unknown", "cve", "research", "intelligence", 
                        "high risk", "complex", "sophisticated", "advanced",
                        "zero-day", "apt", "campaign", "threat actor"
                    ]
                    needs_research = any(keyword in content for keyword in research_keywords)
            
            if needs_research and not research_done:
                state["phase"] = "researcher"
                logger.info("Routing to researcher for additional intelligence")
                return "researcher"
            else:
                state["phase"] = "reporter"
                logger.info("Routing to reporter to generate final report")
                return "reporter"
                
        elif current_phase == "researcher":
            # After research, always go to reporter
            state["phase"] = "reporter"
            state["research_done"] = True
            logger.info("Research completed, routing to reporter")
            return "reporter"
            
        elif current_phase == "reporter":
            # After reporting, always go to validator
            state["phase"] = "validator"
            logger.info("Report generated, routing to validator")
            return "validator"
            
        elif current_phase == "validator":
            # After validation, always finish
            state["phase"] = "completed"
            logger.info("Validation completed, workflow finished")
            return "__end__"
            
        else:
            # Fallback for unknown phases
            logger.warning(f"Unknown phase '{current_phase}', defaulting to analyzer")
            state["phase"] = "analyzer"
            return "analyzer"

    def _validator_router(self, state: AgentState) -> str:
        """Route from validator to next step. Always finish after validator to prevent loops."""
        # Validator always completes the workflow
        state["phase"] = "completed"
        logger.info("Validator completed, ending workflow")
        return "__end__"
    
    def execute(self, initial_prompt: str = None, report_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the security analysis workflow.
        
        Args:
            initial_prompt: Initial prompt for analysis
            report_data: Optional report data to analyze
            
        Returns:
            Workflow execution results
        """
        self.start_time = datetime.now()
        
        if initial_prompt is None:
            initial_prompt = (
                "Analyze the provided security report comprehensively. Identify all threats, "
                "assess their severity, research additional context when needed, and generate "
                "a detailed, actionable security intelligence report."
            )
        
        # Prepare initial state
        initial_content = self._prepare_initial_content(initial_prompt, report_data)
        
        inputs = {
            "messages": [
                SystemMessage(content="You are the Agent Sentinel Intelligence System. Analyze security reports and generate comprehensive threat intelligence."),
                HumanMessage(content=initial_content)
            ]
        }
        
        logger.info("Starting Enterprise Security Analysis Workflow...")
        results = []
        final_report = ""
        error_occurred = False
        
        try:
            if self.tracing_service.is_enabled():
                with self.tracing_service.trace("enterprise-security-analysis") as trace:
                    if trace:
                        try:
                            # Log workflow start event
                            pass  # Trace logging handled by weave.op decorator
                        except Exception as e:
                            logger.warning(f"Failed to log workflow start: {e}")
                    
                    for event in self.app.stream(inputs):
                        for key, value in event.items():
                            if value is None:
                                continue
                            
                            messages = value.get("messages", [])
                            if not messages:
                                continue
                            
                            last_message = messages[-1]
                            if not hasattr(last_message, 'name'):
                                continue
                            
                            agent_name = last_message.name.upper()
                            content = last_message.content
                            
                            if content and isinstance(content, str):
                                logger.info(f"[{agent_name}]: {len(content)} characters")
                                results.append({
                                    "agent": agent_name,
                                    "content": content,
                                    "content_length": len(content),
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                self.tracing_service.log_workflow_step(
                                    step_name=f"agent_{agent_name.lower()}",
                                    content_length=len(content),
                                    status="completed"
                                )
                                
                                if agent_name == "REPORTER":
                                    final_report = content
                                    if trace:
                                        try:
                                            # Log report generation
                                            pass  # Trace logging handled by weave.op decorator
                                        except Exception as e:
                                            logger.warning(f"Failed to log report generation: {e}")
            else:
                # Execute without tracing
                for event in self.app.stream(inputs):
                    for key, value in event.items():
                        if value is None:
                            continue
                        
                        messages = value.get("messages", [])
                        if not messages:
                            continue
                        
                        last_message = messages[-1]
                        if not hasattr(last_message, 'name'):
                            continue
                        
                        agent_name = last_message.name.upper()
                        content = last_message.content
                        
                        if content and isinstance(content, str):
                            logger.info(f"[{agent_name}]: {len(content)} characters")
                            results.append({
                                "agent": agent_name,
                                "content": content,
                                "content_length": len(content),
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            if agent_name == "REPORTER":
                                final_report = content
            
            self.end_time = datetime.now()
            logger.info("Enterprise Security Analysis Workflow completed successfully")
            
            return {
                "success": True,
                "results": results,
                "final_report": final_report,
                "total_steps": len(results),
                "execution_time": (self.end_time - self.start_time).total_seconds(),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "error": None
            }
            
        except Exception as e:
            self.end_time = datetime.now()
            error_occurred = True
            logger.error(f"❌ Enterprise workflow execution failed: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "results": results,
                "final_report": final_report,
                "total_steps": len(results),
                "execution_time": (self.end_time - self.start_time).total_seconds() if self.start_time else 0,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None
            }
    
    def _prepare_initial_content(self, prompt: str, report_data: Optional[Dict[str, Any]] = None) -> str:
        """Prepare initial content for analysis."""
        if report_data:
            # Handle structured report data
            if isinstance(report_data, dict):
                return f"{prompt}\n\nREPORT DATA:\n{json.dumps(report_data, indent=2)}"
            else:
                return f"{prompt}\n\nREPORT DATA:\n{str(report_data)}"
        else:
            # Try to read from common report files
            report_content = self._read_report_files()
            if report_content:
                return f"{prompt}\n\nSECURITY REPORT:\n{report_content}"
            else:
                return prompt
    
    def _read_report_files(self) -> str:
        """Read security report from common file locations."""
        possible_files = [
            "a2a_security_report.txt",
            "agent_sentinel_report.json",
            "security_report.txt",
            "unified_report.json",
            "logs/agent_sentinel.log"
        ]
        
        for filename in possible_files:
            file_path = Path(filename)
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                    logger.info(f"✅ Read security report from: {filename}")
                    return content
                except Exception as e:
                    logger.warning(f"⚠️  Failed to read {filename}: {e}")
        
        return ""
    
    def save_report(self, report_content: str, filename: str = None) -> Dict[str, str]:
        """Save the generated report to files."""
        if not report_content:
            logger.warning("⚠️  No report content to save")
            return {}
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_security_report_{timestamp}"
        
        saved_files = {}
        output_dir = Path(self.config.output.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save text report
        if self.config.output.generate_text:
            text_filename = output_dir / f"{filename}.txt"
            try:
                with open(text_filename, "w", encoding="utf-8") as f:
                    f.write("AGENT SENTINEL ENHANCED SECURITY REPORT\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"Generated: {datetime.now().isoformat()}\n")
                    execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
                    f.write(f"Workflow Execution Time: {execution_time:.2f} seconds\n\n")
                    f.write(report_content)
                saved_files["text"] = str(text_filename)
                logger.info(f"✅ Text report saved to: {text_filename}")
            except Exception as e:
                logger.error(f"❌ Failed to save text report: {e}")
        
        # Save JSON report
        json_filename = output_dir / f"{filename}.json"
        try:
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "workflow_version": "2.0.0",
                    "execution_time": getattr(self, 'execution_time', 0),
                    "total_steps": len(getattr(self, 'execution_history', [])),
                    "config": self.config.dict()
                },
                "report_content": report_content,
                "workflow_results": getattr(self, 'execution_history', [])
            }
            
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            saved_files["json"] = str(json_filename)
            logger.info(f"✅ JSON report saved to: {json_filename}")
        except Exception as e:
            logger.error(f"❌ Failed to save JSON report: {e}")
        
        # Save PDF report
        if self.config.output.generate_pdf:
            pdf_filename = output_dir / f"{filename}.pdf"
            try:
                self._generate_pdf(report_content, pdf_filename)
                saved_files["pdf"] = str(pdf_filename)
                logger.info(f"✅ PDF report saved to: {pdf_filename}")
            except Exception as e:
                logger.error(f"❌ Failed to save PDF report: {e}")
        
        return saved_files
    
    def _generate_pdf(self, content: str, pdf_path: Path):
        """Generate PDF report."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("AGENT SENTINEL ENHANCED SECURITY REPORT", title_style))
            story.append(Spacer(1, 20))
            
            # Metadata
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Content
            lines = content.split('\n')
            for line in lines:
                if line.strip() == '':
                    story.append(Spacer(1, 12))
                elif line.startswith('**') and line.endswith('**'):
                    header_text = line.replace('**', '')
                    story.append(Paragraph(header_text, styles['Heading2']))
                    story.append(Spacer(1, 12))
                elif line.startswith('* **'):
                    bullet_text = line.replace('* **', '• ').replace('**', '')
                    story.append(Paragraph(bullet_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('    * **'):
                    sub_bullet_text = line.replace('    * **', '  ◦ ').replace('**', '')
                    story.append(Paragraph(sub_bullet_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('**High Priority'):
                    story.append(Paragraph("High Priority (Immediate Action):", styles['Heading3']))
                    story.append(Spacer(1, 12))
                elif line.startswith('**Medium Priority'):
                    story.append(Paragraph("Medium Priority (Within 24 Hours):", styles['Heading3']))
                    story.append(Spacer(1, 12))
                elif line.startswith('**Low Priority'):
                    story.append(Paragraph("Low Priority (Ongoing):", styles['Heading3']))
                    story.append(Spacer(1, 12))
                else:
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 6))
            
            doc.build(story)
            
        except ImportError:
            raise ImportError("PDF generation requires reportlab: pip install reportlab")
        except Exception as e:
            raise Exception(f"PDF generation failed: {e}")


def create_workflow_from_env() -> SecurityAnalysisWorkflow:
    """Create workflow from environment configuration."""
    load_dotenv()
    
    config = IntelligenceConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        exa_api_key=os.getenv("EXA_API_KEY"),
        wandb_api_key=os.getenv("WANDB_API_KEY")
    )
    
    return SecurityAnalysisWorkflow(config) 