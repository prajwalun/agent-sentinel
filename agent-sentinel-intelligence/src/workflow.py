"""
Security analysis workflow.

Multi-agent pipeline built on LangGraph: Analyzer → Supervisor → Researcher →
Reporter → Validator, with iterative refinement (up to 3 loops).
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

from models.state import AgentState
from models.config import IntelligenceConfig
from services.llm_service import LLMService
from services.tracing_service import TracingService
from services.research_service import ResearchService
from agents.supervisor import SupervisorAgent
from agents.analyzer import SecurityAnalyzerAgent
from agents.researcher import WebResearcherAgent
from agents.reporter import ReportGeneratorAgent
from agents.validator import ValidatorAgent

logger = logging.getLogger(__name__)


class SecurityAnalysisWorkflow:
    """LangGraph workflow for multi-agent security analysis."""
    
    def __init__(self, config: IntelligenceConfig, max_iterations: int = 3):
        self.config = config
        self.llm_service = LLMService(config.llm)
        self.tracing_service = TracingService(config.tracing)
        self.research_service = ResearchService(config.research)
        self.max_iterations = max_iterations
        
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
        """
        Route from supervisor to the next agent.

        Phase progression:
          analyzer -> (researcher if needed) -> reporter -> validator
        After a validator rejection, the phase is reset to 'analyzer'
        so the cycle can repeat with the validator's feedback injected
        into the message history.
        """
        current_phase = state.get("phase", "analyzer")
        research_done = state.get("research_done", False)

        logger.info("Supervisor routing: phase=%s, research_done=%s", current_phase, research_done)

        if current_phase == "analyzer":
            messages = state.get("messages", [])
            needs_research = False
            if messages:
                last = messages[-1]
                content = getattr(last, "content", "").lower()
                research_keywords = [
                    "novel", "unknown", "cve", "research", "intelligence",
                    "high risk", "complex", "sophisticated", "advanced",
                    "zero-day", "apt", "campaign", "threat actor",
                ]
                needs_research = any(kw in content for kw in research_keywords)

            if needs_research and not research_done:
                state["phase"] = "researcher"
                return "researcher"

            state["phase"] = "reporter"
            return "reporter"

        if current_phase == "researcher":
            state["phase"] = "reporter"
            state["research_done"] = True
            return "reporter"

        if current_phase == "reporter":
            state["phase"] = "validator"
            return "validator"

        if current_phase == "validator":
            state["phase"] = "completed"
            return "__end__"

        logger.warning("Unknown phase '%s', defaulting to analyzer", current_phase)
        state["phase"] = "analyzer"
        return "analyzer"

    def _validator_router(self, state: AgentState) -> str:
        """
        Route from validator: finish if quality passes or max iterations
        reached, otherwise loop back to supervisor for refinement.
        """
        iteration = state.get("iteration_count", 0) + 1
        state["iteration_count"] = iteration

        if iteration >= self.max_iterations:
            state["phase"] = "completed"
            logger.info("Max iterations reached (%d), finishing workflow", iteration)
            return "__end__"

        messages = state.get("messages", [])
        if messages:
            last = messages[-1]
            content = getattr(last, "content", "")
            next_step = state.get("next", "")
            if next_step == "supervisor" or "supervisor" in content.lower()[:50]:
                state["phase"] = "analyzer"
                state["validator_feedback"] = content
                logger.info("Validator requested revision (iteration %d), routing back to supervisor", iteration)
                return "supervisor"

        state["phase"] = "completed"
        logger.info("Validation passed (iteration %d), workflow complete", iteration)
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
                "\n\nIMPORTANT: Limit the total number of agent iterations to 3 (or 2 if the report is not critical). Do not loop or repeat steps unnecessarily. Prioritize speed and concise analysis."
            )
        
        # Prepare initial state
        initial_content = self._prepare_initial_content(initial_prompt, report_data)
        
        inputs = {
            "messages": [
                SystemMessage(content="You are the Agent Sentinel Intelligence System. Analyze security reports and generate comprehensive threat intelligence."),
                HumanMessage(content=initial_content)
            ]
        }
        
        logger.info("Starting security analysis workflow...")
        results = []
        final_report = ""
        error_occurred = False
        iteration_count = 0
        
        try:
            if self.tracing_service.is_enabled():
                with self.tracing_service.trace("security-analysis") as trace:
                    if trace:
                        try:
                            # Log workflow start event
                            pass  # Trace logging handled by weave.op decorator
                        except Exception as e:
                            logger.warning(f"Failed to log workflow start: {e}")
                    
                    for event in self.app.stream(inputs):
                        if iteration_count >= self.max_iterations:
                            logger.info(f"Max agent iterations ({self.max_iterations}) reached. Stopping workflow.")
                            break
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
                        iteration_count += 1
            else:
                # Execute without tracing
                for event in self.app.stream(inputs):
                    if iteration_count >= self.max_iterations:
                        logger.info(f"Max agent iterations ({self.max_iterations}) reached. Stopping workflow.")
                        break
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
                        iteration_count += 1
            
            self.end_time = datetime.now()
            logger.info("Security analysis workflow completed successfully")
            
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
            logger.error(f"Workflow execution failed: {e}")
            
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

    def run_analysis(self, report_content: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Run analysis on a security report (API-friendly method).
        
        Args:
            report_content: The security report content to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info(f"Running {analysis_type} analysis on security report")
            
            # Prepare report data
            report_data = {
                "content": report_content,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Create analysis prompt
            prompt = f"""
            Please analyze the following security report and provide comprehensive intelligence insights:
            
            Analysis Type: {analysis_type}
            Report Content:
            {report_content}
            
            Please provide a detailed analysis including threat assessment, risk evaluation, 
            and actionable recommendations.
            """
            
            # Execute the workflow
            result = self.execute(initial_prompt=prompt, report_data=report_data)
            
            # Transform result for API compatibility
            if result.get("success"):
                return {
                    "enhanced_analysis": result.get("final_report", ""),
                    "threat_intelligence": result.get("final_report", ""),
                    "recommendations": self._extract_recommendations_from_report(result.get("final_report", "")),
                    "workflow_execution_time": result.get("execution_time", 0),
                    "status": "success"
                }
            else:
                return {
                    "enhanced_analysis": "",
                    "threat_intelligence": "",
                    "recommendations": [],
                    "workflow_execution_time": result.get("execution_time", 0),
                    "status": "error",
                    "error": result.get("error", "Unknown error")
                }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "enhanced_analysis": "",
                "threat_intelligence": "",
                "recommendations": [],
                "workflow_execution_time": 0,
                "status": "error",
                "error": str(e)
            }

    def _extract_recommendations_from_report(self, report_content: str) -> List[str]:
        """Extract recommendations from the final report."""
        recommendations = []
        
        if not report_content:
            return recommendations
        
        # Look for recommendations section
        lines = report_content.split('\n')
        in_recommendations = False
        
        for line in lines:
            if "## Recommendations" in line or "### Recommendations" in line:
                in_recommendations = True
                continue
            elif in_recommendations and line.strip().startswith(('##', '###')):
                break
            elif in_recommendations and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '*')):
                # Extract recommendation text
                rec_text = line.strip()
                if rec_text.startswith(('1.', '2.', '3.', '4.', '5.')):
                    rec_text = rec_text[2:].strip()
                elif rec_text.startswith(('-', '*')):
                    rec_text = rec_text[1:].strip()
                
                if rec_text:
                    recommendations.append(rec_text)
        
        # If no recommendations found, provide defaults
        if not recommendations:
            recommendations = [
                "Implement comprehensive security monitoring",
                "Conduct regular security assessments",
                "Enhance incident response procedures",
                "Provide security awareness training",
                "Review and update security policies"
            ]
        
        return recommendations[:10]  # Limit to 10 recommendations

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
                    logger.info("Read security report from: %s", filename)
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
                logger.info("Text report saved to: %s", text_filename)
            except Exception as e:
                logger.error("Failed to save text report: %s", e)
        
        # Save JSON report
        json_filename = output_dir / f"{filename}.json"
        try:
            report_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "workflow_version": "2.0.0",
                    "execution_time": getattr(self, 'execution_time', 0),
                    "total_steps": len(getattr(self, 'execution_history', [])),
                    "config": self.config.model_dump(mode="json")
                },
                "report_content": report_content,
                "workflow_results": getattr(self, 'execution_history', [])
            }
            
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            saved_files["json"] = str(json_filename)
            logger.info("JSON report saved to: %s", json_filename)
        except Exception as e:
            logger.error("Failed to save JSON report: %s", e)
        
        # Save PDF report
        if self.config.output.generate_pdf:
            pdf_filename = output_dir / f"{filename}.pdf"
            try:
                self._generate_pdf(report_content, pdf_filename)
                saved_files["pdf"] = str(pdf_filename)
                logger.info("PDF report saved to: %s", pdf_filename)
            except Exception as e:
                logger.error("Failed to save PDF report: %s", e)
        
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


def create_workflow_from_env() -> Optional[SecurityAnalysisWorkflow]:
    """Create workflow from environment configuration. Returns None if OPENAI_API_KEY is not set."""
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        return None

    config = IntelligenceConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        exa_api_key=os.getenv("EXA_API_KEY"),
        wandb_api_key=os.getenv("WANDB_API_KEY")
    )

    return SecurityAnalysisWorkflow(config) 