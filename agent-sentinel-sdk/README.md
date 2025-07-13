# Agent Sentinel SDK

**Enterprise Security Monitoring SDK for AI Agents**

The Agent Sentinel SDK provides comprehensive security monitoring, threat detection, and performance analytics for AI agents. Secure any AI agent in just 3 lines of code with real-time threat detection, behavioral analysis, and unified reporting.

## 🚀 Quick Start

### Installation

```bash
pip install agent-sentinel
```

### Basic Usage

```python
from agent_sentinel import monitor, monitor_mcp

# Monitor regular functions
@monitor
def process_data(data: str) -> str:
    return data.upper()

# Monitor MCP tools
@monitor_mcp()
def search_database(query: str) -> str:
    return f"Searching for: {query}"

# Use the functions
result = process_data("hello world")
search_result = search_database("user data")
```

## 📊 Unified Reporting

Agent Sentinel generates comprehensive unified reports that combine logs, security events, and analysis into a single file:

### Programmatic Usage

```python
from agent_sentinel.core.sentinel import AgentSentinel

# Initialize with monitoring
sentinel = AgentSentinel(agent_id="my_agent")

# Your monitored functions run here...

# Generate unified report
report_path = sentinel.generate_unified_report()
print(f"Report generated: {report_path}")

# Get report path
report_path = sentinel.get_unified_report_path()
```

### CLI Usage

```bash
# Generate unified report
agent-sentinel report --config config.yaml --agent-id my_agent

# With custom output
agent-sentinel report --output my_report.json --format json
```

### Report Contents

The unified report includes:

- **📊 Executive Summary**: Status, risk score, security events count
- **🔍 Threat Analysis**: Detailed breakdown of detected threats
- **📈 Performance Metrics**: Monitoring statistics and performance data
- **💡 Recommendations**: Actionable security recommendations
- **📝 Session Logs**: Real-time monitoring logs
- **🛡️ Security Events**: Detailed security event information

### Report Structure

```json
{
  "agent_id": "MathAgent",
  "start_time": "2025-07-13T02:12:39.200Z",
  "end_time": "2025-07-13T02:22:39.500Z",
  "session_logs": [...],
  "security_events": [...],
  "performance_metrics": {...},
  "threat_analysis": {...},
  "recommendations": [...],
  "summary": {
    "status": "CLEAN|WARNING|CRITICAL",
    "risk_score": 28.5,
    "threats_detected": 4,
    "performance_score": 87.2
  }
}
```

## 🛡️ Security Features

### Threat Detection

Agent Sentinel automatically detects and blocks 20+ threat types including:

- **SQL Injection** - Pattern-based detection of malicious SQL queries
- **XSS Attacks** - Cross-site scripting attack prevention  
- **Command Injection** - Shell command injection protection
- **Prompt Injection** - LLM prompt manipulation attempts
- **Data Exfiltration** - Unauthorized data access patterns
- **Behavioral Anomalies** - Unusual agent behavior patterns

### Enterprise Security

- **Circuit breaker pattern** for failure protection
- **Structured logging** with compliance tags (GDPR, SOC2, HIPAA)
- **Performance monitoring** and resource tracking
- **Multi-agent coordination** security
- **Row Level Security** for data isolation

## 🔧 Configuration

### Zero Configuration (Recommended)

```python
# Works out of the box
from agent_sentinel import monitor, monitor_mcp

@monitor
def my_function():
    pass
```

### Custom Configuration

```yaml
# config/agent_sentinel.yaml
agent_id: "production_agent"
environment: "production"
detection:
  enabled: true
  confidence_threshold: 0.8
logging:
  level: "INFO"
  format: "json"
security:
  sql_injection_threshold: 0.8
  xss_threshold: 0.7
  performance_warning_mb: 500
```

```python
from agent_sentinel.core.sentinel import AgentSentinel

sentinel = AgentSentinel(config_path="config/agent_sentinel.yaml")
```

## 📈 Performance

### Production Tested

- **Browser MCP Agent**: 49,508 ops/sec, 100% detection rate
- **GitHub MCP Agent**: 41,048 ops/sec, 100% detection rate  
- **Financial Coach Agent**: 98,319 ops/sec, 100% detection rate
- **Multi-Agent Researcher**: 45,246 ops/sec, 100% detection rate

### Security Analytics

```python
# Get comprehensive security insights
metrics = sentinel.get_security_metrics()
{
    "total_threats_blocked": 1247,
    "detection_rate": 100.0,
    "avg_response_time": "0.05ms",
    "threat_breakdown": {
        "sql_injection": 423,
        "xss_attack": 312,
        "prompt_injection": 289
    }
}
```

## 🏗️ Architecture

### Modular Design

```
agent_sentinel/
├── core/           # Core SDK functionality
├── detection/      # Threat detection engines
├── infrastructure/ # Monitoring & metrics
├── intelligence/   # Threat intelligence
├── logging/        # Structured logging
├── security/       # Security utilities
├── services/       # Core services
└── wrappers/       # Agent integration
```

### Plugin Architecture

- **Custom detectors**: Add domain-specific threat detection
- **Intelligence sources**: Integrate external threat feeds
- **Export formats**: Custom data export formats
- **Notification systems**: Slack, email, webhook integrations

## 🔌 Framework Integration

### LangChain

```python
from langchain.agents import AgentExecutor
from agent_sentinel import monitor

@monitor
class SecureAgentExecutor(AgentExecutor):
    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)
```

### AutoGen

```python
from autogen import AssistantAgent
from agent_sentinel import monitor

@monitor
class SecureAssistantAgent(AssistantAgent):
    def generate_reply(self, *args, **kwargs):
        return super().generate_reply(*args, **kwargs)
```

### Custom Frameworks

```python
from agent_sentinel import monitor

@monitor
def your_custom_agent_function(input_data):
    # Your agent logic here
    return processed_result
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/agent-sentinel.git
cd agent-sentinel/agent-sentinel-sdk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

```bash
# Install all development tools
pip install -e .[dev,test,docs]

# Or install individually
pip install -e .[dev]      # Development tools (black, isort, mypy, etc.)
pip install -e .[test]     # Testing framework (pytest, coverage, etc.)
pip install -e .[docs]     # Documentation tools (sphinx, etc.)
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_sentinel --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m security      # Security tests
pytest -m slow          # Slow running tests
```

### Security Validation

```bash
# Run comprehensive security tests
python -m pytest tests/test_security.py

# Performance benchmarks
python -m pytest tests/test_performance.py
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
bandit -r src/
```

## 📚 Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs
make html

# View documentation
open _build/html/index.html
```

### Documentation Structure

- **User Guide**: Getting started and basic usage
- **API Reference**: Complete API documentation
- **Examples**: Code examples and tutorials
- **Architecture**: System design and components
- **Deployment**: Production deployment guides

## 🚀 Deployment

### Production Deployment

```bash
# Install production version
pip install agent-sentinel

# Configure environment
export AGENT_SENTINEL_ENVIRONMENT=production
export AGENT_SENTINEL_AGENT_ID=your_agent_id

# Run with monitoring
agent-sentinel monitor --config production.yaml
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["agent-sentinel", "monitor"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-sentinel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-sentinel
  template:
    metadata:
      labels:
        app: agent-sentinel
    spec:
      containers:
      - name: agent-sentinel
        image: agentsentinel/agent-sentinel:latest
        ports:
        - containerPort: 8080
```

## 🔒 Security & Compliance

- **GDPR**: Data privacy and retention controls
- **SOC2**: Audit trails and access controls  
- **HIPAA**: Healthcare data protection
- Local processing by default
- Configurable data retention policies
- Encryption for sensitive data

## 📞 Support

### Get Help

- [Documentation](https://docs.agentsentinel.dev): Comprehensive guides and API reference
- [GitHub Issues](https://github.com/your-org/agent-sentinel/issues): Bug reports and feature requests
- [Discord Community](https://discord.gg/agentsentinel): Community support and discussions
- [Enterprise Support](mailto:enterprise@agentsentinel.dev): Professional support and consulting

### Quick Links

- [Dashboard Demo](https://demo.agentsentinel.dev): Live security dashboard
- [Security Playground](https://playground.agentsentinel.dev): Test threat detection
- [Performance Benchmarks](https://benchmarks.agentsentinel.dev): Latest performance data
- [Threat Intelligence Feed](https://intel.agentsentinel.dev): Real-time threat data

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python and enterprise security practices
- Designed for high-performance, scalable monitoring
- Community-driven development and testing

---

**Ready to secure your AI agents? Get started in 30 seconds:**

```bash
pip install agent-sentinel && python -c "
from agent_sentinel import monitor, monitor_mcp
print('Agent Sentinel SDK is ready!')
"
``` 