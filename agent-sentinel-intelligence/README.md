# Agent Sentinel Intelligence Layer

A sophisticated multi-agent system for analyzing security reports and generating comprehensive threat intelligence using LangGraph and advanced LLM orchestration.

## Overview

The Agent Sentinel Intelligence Layer is a production-ready, enterprise-grade system that processes security reports through a coordinated workflow of specialized AI agents:

- **Supervisor Agent**: Orchestrates the workflow and routes tasks to appropriate specialists
- **Security Analyzer**: Processes security reports and extracts key threat information
- **Web Researcher**: Performs threat intelligence research using Exa.ai
- **Report Generator**: Creates comprehensive, actionable security reports
- **Validator**: Reviews and validates final reports for quality and completeness

## Features

- **Multi-Agent Orchestration**: Coordinated workflow using LangGraph
- **Threat Intelligence**: Web research capabilities with Exa.ai integration
- **Comprehensive Reporting**: Generate both text and PDF reports
- **Tracing & Monitoring**: Built-in support for Weave and Weights & Biases
- **Multiple LLM Providers**: Support for OpenAI and Google Gemini
- **Production Ready**: Enterprise-grade error handling, logging, and configuration
- **Modular Architecture**: Clean separation of concerns and extensible design

## Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for your chosen LLM provider(s)
- Optional: Exa.ai API key for web research
- Optional: Weights & Biases API key for tracing

### Installation

1. Clone the repository:
```bash
git clone https://github.com/agent-sentinel/intelligence.git
cd agent-sentinel-intelligence
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create a `.env` file with your API keys:

```env
# LLM Providers (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Web Research (optional)
EXA_API_KEY=your_exa_api_key_here

# Tracing & Monitoring (optional)
WANDB_API_KEY=your_wandb_api_key_here
```

### Usage

#### Basic Usage

```python
from src.workflow import create_workflow_from_env

# Create workflow from environment
workflow = create_workflow_from_env()

# Execute analysis
result = workflow.execute()

if result["success"]:
    print("Analysis completed successfully!")
    print(f"Final report: {result['final_report'][:200]}...")
else:
    print(f"Analysis failed: {result['error']}")
```

#### Command Line

```bash
python main.py
```

#### Programmatic Usage

```python
from src.models.config import IntelligenceConfig
from src.workflow import SecurityAnalysisWorkflow

# Create custom configuration
config = IntelligenceConfig(
    openai_api_key="your_key_here",
    exa_api_key="your_exa_key_here"
)

# Create workflow
workflow = SecurityAnalysisWorkflow(config)

# Execute with custom prompt
result = workflow.execute(
    "Analyze this security report and provide detailed threat assessment"
)

# Save reports
saved_files = workflow.save_report(
    result["final_report"], 
    filename="my_security_analysis"
)
```

## Architecture

### Directory Structure

```
agent-sentinel-intelligence/
├── src/
│   ├── agents/           # Individual agent implementations
│   │   ├── supervisor.py
│   │   ├── analyzer.py
│   │   ├── researcher.py
│   │   ├── reporter.py
│   │   └── validator.py
│   ├── models/           # Data models and configuration
│   │   └── config.py
│   ├── services/         # Core services
│   │   ├── llm_service.py
│   │   ├── tracing_service.py
│   │   └── research_service.py
│   ├── utils/            # Utility functions
│   ├── api/              # API endpoints (future)
│   └── workflow.py       # Main workflow orchestration
├── config/               # Configuration files
├── tests/                # Test suite
├── docs/                 # Documentation
├── main.py               # Entry point
├── requirements.txt      # Dependencies
└── pyproject.toml        # Project metadata
```

### Workflow Flow

1. **Supervisor** receives the initial request and routes to the appropriate agent
2. **Security Analyzer** processes the security report and extracts threat information
3. **Web Researcher** (optional) performs additional threat intelligence research
4. **Report Generator** creates a comprehensive, actionable security report
5. **Validator** reviews the report for quality and completeness
6. **Supervisor** decides whether to continue or finish the workflow

## Configuration

### IntelligenceConfig

The main configuration class supports extensive customization:

```python
from src.models.config import IntelligenceConfig

config = IntelligenceConfig(
    # LLM Configuration
    llm=LLMConfig(
        provider="openai",
        model="gpt-4o",
        temperature=0.1
    ),
    
    # Tracing Configuration
    tracing=TracingConfig(
        enabled=True,
        provider="weave",
        project_name="my-security-project"
    ),
    
    # Research Configuration
    research=ResearchConfig(
        enabled=True,
        max_research_queries=5,
        research_timeout=30
    ),
    
    # Output Configuration
    output=OutputConfig(
        generate_text=True,
        generate_pdf=True,
        output_directory="./reports"
    )
)
```

## API Reference

### SecurityAnalysisWorkflow

The main workflow class that orchestrates the entire analysis process.

#### Methods

- `execute(initial_prompt: str = None) -> Dict[str, Any]`: Execute the workflow
- `save_report(report_content: str, filename: str = None) -> Dict[str, str]`: Save reports to files

### Agent Classes

Each agent is implemented as a separate class with an `execute()` method:

- `SupervisorAgent`: Orchestrates workflow routing
- `SecurityAnalyzerAgent`: Analyzes security reports
- `WebResearcherAgent`: Performs threat intelligence research
- `ReportGeneratorAgent`: Generates comprehensive reports
- `ValidatorAgent`: Validates report quality

### Service Classes

Core services provide functionality across agents:

- `LLMService`: Manages LLM interactions with fallback support
- `TracingService`: Handles tracing and monitoring
- `ResearchService`: Manages web research capabilities

## Development

### Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:
```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests

```bash
pytest
```

### Code Quality

The project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

Run all quality checks:

```bash
black src/
isort src/
mypy src/
flake8 src/
```

### Adding New Agents

1. Create a new agent class in `src/agents/`
2. Implement the `execute()` method
3. Add the agent to the workflow in `src/workflow.py`
4. Update the routing logic in the supervisor agent

Example:

```python
class NewAgent:
    def __init__(self, llm_service, tracing_service):
        self.llm_service = llm_service
        self.tracing_service = tracing_service
    
    def execute(self, state: MessagesState) -> Command[Literal["next_agent"]]:
        # Agent logic here
        return Command(
            update={"messages": [HumanMessage(content="result", name="new_agent")]},
            goto="next_agent"
        )
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://docs.agentsentinel.com/intelligence](https://docs.agentsentinel.com/intelligence)
- Issues: [https://github.com/agent-sentinel/intelligence/issues](https://github.com/agent-sentinel/intelligence/issues)
- Discussions: [https://github.com/agent-sentinel/intelligence/discussions](https://github.com/agent-sentinel/intelligence/discussions)

## Security

This project is designed for security analysis and follows security best practices:

- No sensitive data is logged or stored
- API keys are handled securely through environment variables
- All external API calls use proper authentication
- Input validation and sanitization are implemented throughout

For security issues, please contact security@agentsentinel.com. 