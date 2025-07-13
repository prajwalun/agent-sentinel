# BlueGuard Security Report Reflection Agent

A LangGraph-based reflection agent that uses Google Gemini and Exa.ai to analyze security reports and generate comprehensive, actionable reports with web research capabilities.

## Features

- **Multi-Agent Workflow**: Uses LangGraph to orchestrate specialized agents
- **Google Gemini Integration**: Leverages Google's Gemini 1.5 Flash model for analysis
- **Exa.ai Web Research**: Integrates Exa.ai for web search, crawling, and threat intelligence
- **Structured Output**: Generates reports in a consistent, comprehensive format
- **Automatic File Detection**: Automatically finds and analyzes security report files
- **PDF Generation**: Creates professional PDF reports alongside text versions

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   EXA_API_KEY=your_exa_api_key_here
   ```

3. **Get API Keys**:
   - **Google API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Exa API Key**: Visit [Exa.ai](https://exa.ai/) to get your API key

## Usage

### Basic Security Report Analysis
```bash
python reflection_agent.py
```

### Enhanced Analysis with Web Research
```bash
python enhanced_reflection_agent.py
```

### Test Exa.ai Integration
```bash
python test_exa_integration.py
```

### Custom File Analysis
```python
from enhanced_reflection_agent import app

# Analyze a specific file
inputs = {
    "messages": [
        HumanMessage(content="Analyze this security report with web research...")
    ]
}

for event in app.stream(inputs):
    # Process results
    pass
```

## Workflow

The enhanced agent follows a 5-stage workflow:

1. **Supervisor**: Orchestrates the workflow and routes to appropriate agents
2. **Security Analyzer**: Processes security reports and extracts key information
3. **Web Researcher**: Uses Exa.ai to gather threat intelligence and web research
4. **Report Generator**: Creates comprehensive, actionable reports
5. **Validator**: Reviews and validates the final report quality

## Exa.ai Integration

The enhanced agent includes Exa.ai capabilities for:

- **Web Search**: Search for threat intelligence, CVE information, and security advisories
- **Content Crawling**: Retrieve and analyze web content related to security threats
- **Real-time Research**: Gather current information about attack techniques and mitigation strategies
- **Threat Intelligence**: Enhance security analysis with up-to-date threat data

## Report Format

The generated reports follow this structure:

1. **Clear Summary**: Purpose and main takeaway with technical overview
2. **Threats Explained**: Detailed technical findings including:
   - Specific attack techniques used (XSS, data exfiltration, injection, etc.)
   - Tools and methods employed by attackers
   - Payloads and code snippets
   - Timestamps and attack sequence
   - Web research findings and threat intelligence
3. **Source Identification**: Detailed breakdown of:
   - All agents involved (malicious_agent, translation_agent, etc.)
   - Specific tools used by each agent
   - Attack patterns and techniques
4. **Actionable Steps**: Prioritized list with technical details and research-backed recommendations

## Output Files

The agent generates two types of reports:

- **Text Report**: `blueguard_security_report.txt` or `enhanced_blueguard_security_report.txt`
- **PDF Report**: `blueguard_security_report.pdf` or `enhanced_blueguard_security_report.pdf`

## File Structure

```
├── reflection_agent.py              # Basic security report agent
├── enhanced_reflection_agent.py     # Enhanced agent with Exa.ai integration
├── test_exa_integration.py          # Test script for Exa.ai
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── .env                             # Environment variables (create this)
├── real_a2a_security_report_20250713_012303.txt  # Example security report
├── blueguard_security_report.txt    # Generated basic report
├── blueguard_security_report.pdf    # Generated basic PDF report
├── enhanced_blueguard_security_report.txt  # Generated enhanced report
└── enhanced_blueguard_security_report.pdf # Generated enhanced PDF report
```

## Example Output

The enhanced agent provides comprehensive reports including:

- Technical analysis of security threats
- Web research findings and threat intelligence
- Real-time information about attack techniques
- Research-backed mitigation strategies
- Professional PDF formatting

## Dependencies

- `langchain-core`: Core LangChain functionality
- `langchain-google-genai`: Google Gemini integration
- `langgraph`: Multi-agent workflow orchestration
- `exa-py`: Exa.ai web search and crawling
- `reportlab`: PDF generation
- `pydantic`: Data validation
- `python-dotenv`: Environment variable management 