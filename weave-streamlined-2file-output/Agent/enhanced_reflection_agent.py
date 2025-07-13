from typing import Annotated, Sequence, List, Literal 
from pydantic import BaseModel, Field 
from langchain_core.messages import HumanMessage
from langgraph.types import Command 
from langgraph.graph import StateGraph, START, END, MessagesState
from dotenv import load_dotenv
import os
import weave

load_dotenv()

# Initialize Weave for tracing (optional)
weave = None
try:
    import weave
    import wandb
    
    # Login to W&B with API key
    wandb_api_key = os.getenv("WANDB_API_KEY")
    if wandb_api_key:
        wandb.login(key=wandb_api_key)
        weave.init('blueguard-security-agent')
        print("✅ Weave tracing initialized with W&B cloud logging")
    else:
        weave.init('blueguard-security-agent')
        print("⚠️  Weave tracing initialized locally (no WANDB_API_KEY found)")
except Exception as e:
    print(f"⚠️  Weave initialization failed: {e}")
    weave = None

# Create a trace for the entire workflow
def create_workflow_trace():
    if weave:
        return weave.trace("security-report-analysis")
    return None

# Add tracing to LLM calls
def traced_llm_call(llm, messages, node_name):
    if not weave:
        return llm.invoke(messages)
    
    try:
        with weave.trace(f"{node_name}-llm-call") as trace:
            trace.log({"node": node_name, "input_length": len(str(messages))})
            result = llm.invoke(messages)
            trace.log({"node": node_name, "output_length": len(result.content), "status": "completed"})
            return result
    except Exception as e:
        print(f"⚠️  Weave tracing failed for {node_name}: {e}")
        return llm.invoke(messages)

# Try to use OpenAI first, fallback to Google Gemini
try:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o")
    print("✅ Using OpenAI model")
except ImportError:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )
        print("✅ Using Google Gemini model")
    except Exception as e:
        print(f"❌ Error initializing LLM: {e}")
        print("Please set either OPENAI_API_KEY or GOOGLE_API_KEY in your .env file")
        exit(1)

# Initialize Exa.ai client
try:
    from exa_py import Exa
    exa_client = Exa(api_key=os.getenv("EXA_API_KEY"))
    print("✅ Exa.ai client initialized")
except ImportError:
    print("⚠️  Exa.ai not available. Install with: pip install exa-py")
    exa_client = None
except Exception as e:
    print(f"⚠️  Exa.ai initialization failed: {e}")
    exa_client = None

class EnhancedSupervisor(BaseModel):
    next: Literal["analyzer", "researcher", "reporter", "validator"] = Field(
        description="Determines which specialist to activate next in the workflow sequence: "
                    "'analyzer' when security report analysis is needed, "
                    "'researcher' when web research and crawling is required for additional context, "
                    "'reporter' when generating user-friendly report, "
                    "'validator' when final review and validation is required."
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )

def supervisor_node(state: MessagesState) -> Command[Literal["analyzer", "researcher", "reporter", "validator"]]:

    system_prompt = ('''
                 
        You are an Enhanced Security Workflow Supervisor managing a team of four specialized agents: Security Analyzer, Web Researcher, Report Generator, and Validator. Your role is to orchestrate the workflow by selecting the most appropriate next agent based on the current state and needs of the task. Provide a clear, concise rationale for each decision to ensure transparency in your decision-making process.

        **Team Members**:
        1. **Security Analyzer**: Always consider this agent first. They analyze security reports, identify threats, and extract key information for processing.
        2. **Web Researcher**: Specializes in web search, crawling, and research using Exa.ai to gather additional context, threat intelligence, and real-time information.
        3. **Report Generator**: Specializes in creating comprehensive, actionable security reports from technical findings and research data.
        4. **Validator**: Focuses on reviewing and validating the final report quality and completeness.

        **Your Responsibilities**:
        1. Analyze each security report and agent response for completeness, accuracy, and relevance.
        2. Route the task to the most appropriate agent at each decision point.
        3. Maintain workflow momentum by avoiding redundant agent assignments.
        4. Continue the process until the security report is fully analyzed, researched, and a comprehensive report is generated.

        **Smart Routing Guidelines**:
        - Start with Security Analyzer for technical analysis
        - Route to Web Researcher ONLY when:
          * The security analysis reveals unknown or novel attack techniques
          * Threat intelligence or CVE information would be valuable
          * Real-time information about attack patterns is needed
          * Additional context about threat actors or tools would enhance the report
          * The analysis suggests sophisticated or coordinated attacks
        - Route directly to Report Generator if the security analysis is comprehensive and sufficient
        - Route to Validator for final quality check

        **Cost Optimization**: Web research uses API calls and should only be used when it adds significant value to the analysis. If the security report contains standard, well-understood threats, skip web research.

        Your objective is to create an efficient workflow that leverages each agent's strengths while minimizing unnecessary steps and costs, ultimately delivering complete and accurate security analysis with enhanced context when needed.
                 
    ''')
    
    messages = [
        {"role": "system", "content": system_prompt},  
    ] + state["messages"] 

    response = traced_llm_call(llm.with_structured_output(EnhancedSupervisor), messages, "supervisor")

    goto = response.next
    reason = response.reason

    print(f"--- Workflow Transition: Supervisor → {goto.upper()} ---")
    
    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto=goto,  
    )

def analyzer_node(state: MessagesState) -> Command[Literal["researcher", "reporter"]]:

    """
        Security Analyzer agent node that processes security reports and extracts key information.
        Takes the security report and transforms it into structured analysis data.
    """
   
    system_prompt = (
        "You are a Security Analysis Specialist with expertise in analyzing security reports and threat assessment. Your responsibilities include:\n\n"
        "1. Reading and parsing security scan reports to identify all threats\n"
        "2. Categorizing threats by type (XSS, data exfiltration, injection attacks, etc.)\n"
        "3. Determining severity levels and potential impact\n"
        "4. Identifying the source agents responsible for malicious activity\n"
        "5. Extracting ALL technical details including:\n"
        "   - Specific tools used (inject_html, extract_data, translate_text, etc.)\n"
        "   - Attack techniques and methods\n"
        "   - Payloads and code snippets\n"
        "   - Timestamps and attack sequence\n"
        "   - Agent behaviors and patterns\n"
        "   - Threat categories and classifications\n"
        "6. Assessing whether web research would add value:\n"
        "   - Note if threats are standard/well-understood or novel/complex\n"
        "   - Identify if additional threat intelligence would be valuable\n"
        "   - Suggest if real-time information about attack patterns is needed\n\n"
        "Important: Provide comprehensive technical analysis with all specific details, tools, techniques, and attack methods. Include exact payloads, timestamps, and agent behaviors. Also indicate whether web research would enhance the analysis."
    )

    # Read the security report file directly
    try:
        with open("real_a2a_security_report_20250713_012303.txt", "r") as f:
            file_content = f.read()
    except FileNotFoundError:
        file_content = "Security report file not found."

    messages = [
        {"role": "system", "content": system_prompt},  
        {"role": "user", "content": f"Analyze this security report:\n\n{file_content}"}
    ]  

    analysis = traced_llm_call(llm, messages, "analyzer")

    print(f"--- Workflow Transition: Security Analyzer → Web Researcher ---")

    return Command(
        update={
            "messages": [  
                HumanMessage(
                    content=analysis.content, 
                    name="analyzer"  
                )
            ]
        },
        goto="researcher", 
    )

def researcher_node(state: MessagesState) -> Command[Literal["reporter"]]:

    """
        Web Researcher agent node that uses Exa.ai to search, crawl, and research web-related information.
        Enhances security analysis with real-time threat intelligence and context.
    """
    
    system_prompt = (
        "You are a Web Research Specialist with expertise in using Exa.ai for security research and threat intelligence. Your responsibilities include:\n\n"
        "1. Using Exa.ai to search for relevant threat intelligence, CVE information, and security advisories\n"
        "2. Crawling and analyzing web content related to identified threats and attack techniques\n"
        "3. Gathering real-time information about threat actors, tools, and attack patterns\n"
        "4. Researching mitigation strategies and best practices for identified vulnerabilities\n"
        "5. Providing context and additional insights to enhance the security analysis\n\n"
        "IMPORTANT: Only report real, confirmed CVEs and vulnerabilities found through research. If no specific CVEs are found, state 'no known CVEs found' rather than using hypothetical or placeholder CVEs. Focus on finding actionable intelligence that can improve the security report and provide better mitigation strategies."
    )

    # Get the analysis from previous node
    analysis_content = ""
    for message in state["messages"]:
        if hasattr(message, 'name') and message.name == "analyzer":
            analysis_content = message.content
            break

    research_results = ""
    
    if exa_client:
        try:
            # Extract key terms for research
            research_terms = [
                "XSS attack techniques inject_html",
                "data exfiltration extract_data translate_text",
                "malicious agent security threats",
                "web application security vulnerabilities",
                "threat intelligence 2025",
                "security incident response best practices"
            ]
            
            all_results = []
            
            for term in research_terms:
                try:
                    # Search using Exa.ai
                    search_response = exa_client.search(term, num_results=3)
                    
                    # Extract search results directly
                    if hasattr(search_response, 'results') and search_response.results:
                        for result in search_response.results[:2]:
                            if hasattr(result, 'url'):
                                # Get basic info from search result
                                title = getattr(result, 'title', 'No title')
                                all_results.append(f"Source: {result.url}\nTitle: {title}\n")
                            
                except Exception as e:
                    print(f"⚠️  Exa.ai search failed for term '{term}': {e}")
                    continue
            
            if all_results:
                research_results = "\n\n".join(all_results)
            else:
                research_results = "No web research results available."
                
        except Exception as e:
            research_results = f"Exa.ai research failed: {e}"
    else:
        research_results = "Exa.ai client not available for web research."

    # Combine analysis with research
    combined_content = f"Security Analysis:\n{analysis_content}\n\nWeb Research Results:\n{research_results}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Enhance this security analysis with web research:\n\n{combined_content}"}
    ]

    enhanced_analysis = traced_llm_call(llm, messages, "researcher")

    print(f"--- Workflow Transition: Web Researcher → Report Generator ---")

    return Command(
        update={
            "messages": [ 
                HumanMessage(
                    content=enhanced_analysis.content,  
                    name="researcher"  
                )
            ]
        },
        goto="reporter", 
    )

def reporter_node(state: MessagesState) -> Command[Literal["validator"]]:

    """
        Report Generator agent node that creates comprehensive security reports.
        Takes the enhanced analysis and generates a detailed, actionable report.
    """
    
    system_prompt = (
        "You are a Security Report Generator with expertise in creating comprehensive security reports. Your responsibilities include:\n\n"
        "1. Converting technical security findings into clear, detailed reports\n"
        "2. Including ALL technical details: tools, agents, techniques, attack methods, timestamps\n"
        "3. Incorporating web research findings and threat intelligence\n"
        "4. Structuring reports with clear summary, threats, sources, and actionable steps\n"
        "5. Prioritizing actions by urgency and importance\n"
        "6. Making recommendations specific and actionable\n\n"
        "IMPORTANT: Only reference real, confirmed CVEs and vulnerabilities. If no specific CVEs are found, state 'no known CVEs found' rather than using hypothetical or placeholder CVEs.\n\n"
        "Create reports following this exact structure:\n"
        "1. Clear Summary: Purpose and main takeaway with technical overview\n"
        "2. Threats Explained: Detailed technical findings including:\n"
        "   - Specific attack techniques used (XSS, data exfiltration, injection, etc.)\n"
        "   - Tools and methods employed by attackers\n"
        "   - Payloads and code snippets\n"
        "   - Timestamps and attack sequence\n"
        "   - Web research findings and threat intelligence\n"
        "3. Source Identification: Detailed breakdown of:\n"
        "   - All agents involved (malicious_agent, translation_agent, etc.)\n"
        "   - Specific tools used by each agent\n"
        "   - Attack patterns and techniques\n"
        "4. Actionable Steps: Prioritized list with technical details and research-backed recommendations"
    )

    # Get the enhanced analysis from previous node
    enhanced_content = ""
    for message in state["messages"]:
        if hasattr(message, 'name') and message.name == "researcher":
            enhanced_content = message.content
            break

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Generate a comprehensive security report based on this enhanced analysis:\n\n{enhanced_content}"}
    ]

    report = traced_llm_call(llm, messages, "reporter")

    print(f"--- Workflow Transition: Report Generator → Validator ---")

    return Command(
        update={
            "messages": [ 
                HumanMessage(
                    content=report.content,  
                    name="reporter"  
                )
            ]
        },
        goto="validator", 
    )

class Validator(BaseModel):
    next: Literal["supervisor", "FINISH"] = Field(
        description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate."
    )
    reason: str = Field(
        description="The reason for the decision."
    )

def validator_node(state: MessagesState) -> Command[Literal["supervisor", "__end__"]]:

    """
        Validator agent node that reviews the final report for quality and completeness.
        Ensures the report meets quality standards before completion.
    """

    system_prompt = '''
    Your task is to ensure reasonable quality for the security report. 
    Specifically, you must:
    - Review the original security report (the first message in the workflow).
    - Review the generated comprehensive report (the last message in the workflow).
    - If the report addresses the core security findings, includes web research insights, and provides actionable guidance, signal to end the workflow with 'FINISH'.
    - Only route back to the supervisor if the report is completely off-topic, missing critical information, or fundamentally misunderstands the security threats.
    
    - Accept reports that are "good enough" rather than perfect
    - Prioritize workflow completion over perfect responses
    - Give benefit of doubt to borderline reports
    
    Routing Guidelines:
    1. 'supervisor' Agent: ONLY for reports that are completely incorrect or missing critical security information.
    2. Respond with 'FINISH' in all other cases to end the workflow.
'''

    user_question = state["messages"][0].content
    agent_answer = state["messages"][-1].content

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": agent_answer},
    ]

    response = traced_llm_call(llm.with_structured_output(Validator), messages, "validator")

    goto = response.next
    reason = response.reason

    if goto == "FINISH":
        goto = "__end__"  
        print(" --- Transitioning to END ---")  
    else:
        print(f"--- Workflow Transition: Validator → Supervisor ---")
 

    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="validator")
            ]
        },
        goto=goto, 
    )

# Create the workflow graph
graph = StateGraph(MessagesState)

# Add nodes
graph.add_node("supervisor", supervisor_node) 
graph.add_node("analyzer", analyzer_node)  
graph.add_node("researcher", researcher_node)
graph.add_node("reporter", reporter_node) 
graph.add_node("validator", validator_node)  

# Add edges
graph.add_edge(START, "supervisor")  

# Compile the graph
app = graph.compile()

# Main execution
if __name__ == "__main__":
    print("🔍 Enhanced Security Report Reflection Agent with Exa.ai")
    print("=" * 60)
    
    inputs = {
        "messages": [
            HumanMessage(content="Analyze the security report, research web intelligence, and generate a comprehensive report with clear summary, threats, sources, and actionable steps.")
        ]
    }
    
    print("Starting Enhanced Security Report Analysis...")
    print("=" * 60)
    
    # Start Weave trace
    final_report = ""
    if weave:
        try:
            with weave.trace("security-report-analysis") as trace:
                trace.log({"event": "analysis_started", "timestamp": "2025-07-13"})
                
                for event in app.stream(inputs):
                    for key, value in event.items():
                        if value is None:
                            continue
                        last_message = value.get("messages", [])[-1] if "messages" in value else None
                        if last_message and hasattr(last_message, 'name'):
                            print(f"\n[{last_message.name.upper()}]:")
                            print("-" * 30)
                            print(last_message.content)
                            print()
                            
                            # Log each agent step to Weave
                            trace.log({
                                "agent": last_message.name,
                                "content_length": len(last_message.content),
                                "step": "completed"
                            })
                            
                            # Save the final report from the reporter
                            if last_message.name == "reporter":
                                final_report = last_message.content
                                trace.log({"event": "report_generated", "report_length": len(final_report)})
        except Exception as e:
            print(f"⚠️  Weave tracing failed: {e}")
            # Fallback to normal execution
            for event in app.stream(inputs):
                for key, value in event.items():
                    if value is None:
                        continue
                    last_message = value.get("messages", [])[-1] if "messages" in value else None
                    if last_message and hasattr(last_message, 'name'):
                        print(f"\n[{last_message.name.upper()}]:")
                        print("-" * 30)
                        print(last_message.content)
                        print()
                        
                        # Save the final report from the reporter
                        if last_message.name == "reporter":
                            final_report = last_message.content
    else:
        # Normal execution without Weave
        for event in app.stream(inputs):
            for key, value in event.items():
                if value is None:
                    continue
                last_message = value.get("messages", [])[-1] if "messages" in value else None
                if last_message and hasattr(last_message, 'name'):
                    print(f"\n[{last_message.name.upper()}]:")
                    print("-" * 30)
                    print(last_message.content)
                    print()
                    
                    # Save the final report from the reporter
                    if last_message.name == "reporter":
                        final_report = last_message.content
    
    # Save the final report to a file
    if final_report:
        output_filename = "enhanced_blueguard_security_report.txt"
        pdf_filename = "enhanced_blueguard_security_report.pdf"
        
        # Save as text file
        with open(output_filename, "w") as f:
            f.write("ENHANCED BLUEGUARD SECURITY REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(final_report)
        
        # Save as PDF file
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            story.append(Paragraph("ENHANCED BLUEGUARD SECURITY REPORT", title_style))
            story.append(Spacer(1, 20))
            
            # Convert markdown-style content to PDF
            lines = final_report.split('\n')
            for line in lines:
                if line.strip() == '':
                    story.append(Spacer(1, 12))
                elif line.startswith('**') and line.endswith('**'):
                    # Bold headers
                    header_text = line.replace('**', '')
                    story.append(Paragraph(header_text, styles['Heading2']))
                    story.append(Spacer(1, 12))
                elif line.startswith('* **'):
                    # Bullet points
                    bullet_text = line.replace('* **', '• ').replace('**', '')
                    story.append(Paragraph(bullet_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('    * **'):
                    # Sub-bullet points
                    sub_bullet_text = line.replace('    * **', '  ◦ ').replace('**', '')
                    story.append(Paragraph(sub_bullet_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('1. **'):
                    # Numbered lists
                    numbered_text = line.replace('1. **', '1. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('2. **'):
                    numbered_text = line.replace('2. **', '2. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('3. **'):
                    numbered_text = line.replace('3. **', '3. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('4. **'):
                    numbered_text = line.replace('4. **', '4. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('5. **'):
                    numbered_text = line.replace('5. **', '5. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('6. **'):
                    numbered_text = line.replace('6. **', '6. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
                    story.append(Spacer(1, 6))
                elif line.startswith('7. **'):
                    numbered_text = line.replace('7. **', '7. ').replace('**', '')
                    story.append(Paragraph(numbered_text, styles['Normal']))
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
                    # Regular text
                    if line.strip():
                        story.append(Paragraph(line, styles['Normal']))
                        story.append(Spacer(1, 6))
            
            doc.build(story)
            print(f"\n✅ Enhanced PDF Report saved to: {pdf_filename}")
            print(f"📁 PDF location: {os.path.abspath(pdf_filename)}")
            
        except ImportError:
            print("\n⚠️  PDF generation failed. Install reportlab: pip install reportlab")
        except Exception as e:
            print(f"\n⚠️  PDF generation failed: {e}")
        
        print(f"\n✅ Enhanced Text Report saved to: {output_filename}")
        print(f"📁 Text location: {os.path.abspath(output_filename)}") 