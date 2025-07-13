# BlueGuard A2A Security System

A comprehensive multi-agent system with Google A2A (Agent-to-Agent) architecture, Model Context Protocol (MCP) integration, and advanced security monitoring using BlueGuard.

## 🏗️ Architecture Overview

The system implements Google's A2A (Agent-to-Agent) SDK with the following components:

```
A2A MCP Server
├── Math Agent → Mathematical operations
├── Weather Agent → Weather information  
├── Translation Agent → Text translation
├── Malicious Agent → Security testing
└── BlueGuard → Security monitoring & threat detection
```

### Security Monitoring Flow
```
Agent Interactions → A2A MCP Server → BlueGuard Analysis → Security Reports
```

## 🚀 Features

### Multi-Agent System
- **Math Agent**: Basic mathematical operations (add, subtract, multiply, divide)
- **Weather Agent**: Weather information and forecasts
- **Translation Agent**: Text translation with security vulnerabilities for testing
- **Malicious Agent**: Intentional security vulnerabilities for testing

### Security Monitoring (BlueGuard)
- **Real-time threat detection** during agent interactions
- **Cross-agent threat detection** for data flow between agents
- **Pattern-based security heuristics** for multiple threat types
- **Comprehensive logging** of all interactions and security events
- **Automated security reports** with actionable recommendations

### Threat Detection
- **HTML Injection**: Detects malicious HTML tags and scripts
- **Prompt Injection**: Identifies instruction manipulation attempts
- **Data Exfiltration**: Monitors for data extraction patterns
- **Command Injection**: Detects command execution attempts
- **SQL Injection**: Identifies database attack patterns
- **XSS**: Cross-site scripting detection
- **Cross-Agent Threats**: Detects threats propagated between agents

## 📁 Project Structure

```
blueguard-mcp/
├── src/
│   ├── __init__.py
│   ├── a2a_sdk.py           # A2A SDK implementation
│   ├── a2a_mcp_server.py    # A2A MCP server
│   ├── a2a_agents/          # A2A agents
│   │   ├── __init__.py
│   │   ├── math_agent.py         # Mathematical operations
│   │   ├── weather_agent.py      # Weather information
│   │   ├── translation_agent.py  # Text translation
│   │   └── malicious_agent.py    # Security testing agent
│   └── security/
│       ├── __init__.py
│       ├── blueguard.py          # Security monitoring system
│       ├── a2a_threat_detector.py # Cross-agent threat detection
│       ├── heuristics.py         # Threat detection patterns
│       └── report_generator.py   # Security report generation
├── logs/                         # Interaction and security logs
├── reports/                      # Security reports
├── test_a2a_threat_detection.py  # Main demo script
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd blueguard-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google AI API key** (optional):
   ```bash
   export GOOGLE_AI_API_KEY="your-api-key-here"
   ```

## 🚀 Usage

### Run the Complete System
```bash
python test_a2a_threat_detection.py
```

This will:
1. Start the Real A2A MCP server
2. Register all agents with their tools
3. Run agent-to-agent communication scenarios
4. Execute security testing with malicious data flow
5. Generate comprehensive security reports with cross-agent threat analysis

### Expected Output
```
Starting A2A Threat Detection Test...
Real A2A Server initialized on localhost:8000
BlueGuard security monitoring initialized with A2A threat detection
Registered Real A2A agent: math_agent
Registered Real A2A agent: weather_agent
Registered Real A2A agent: translation_agent
Registered Real A2A agent: malicious_agent
Real A2A MCP Server initialized
Real A2A Server ready for agent interactions

============================================================
TESTING AGENT-TO-AGENT THREAT DETECTION
============================================================
Scenario 1: Malicious agent -> Translation agent data flow
Cross-agent threat detected: malicious_agent -> translation_agent: html_injection
Cross-agent threat detected: malicious_agent -> translation_agent: xss
...
============================================================
A2A THREAT DETECTION TEST COMPLETED
============================================================
Total Interactions: 6
Security Events: 8
Security Alerts: 8
Cross-Agent Threats: 8
```

## 📊 Security Reports

The system generates exactly 2 output files:

### 1. Communication Log (JSON)
- **Location**: `src/logs/real_a2a_communication_log_YYYYMMDD_HHMMSS.json`
- **Content**: Complete interaction logs, security events, alerts, and analysis
- **Size**: ~100KB, comprehensive data

### 2. Security Report (TXT)
- **Location**: `src/reports/real_a2a_security_report_YYYYMMDD_HHMMSS.txt`
- **Content**: Human-readable security report in BlueGuard format
- **Size**: ~3KB, actionable insights

## 🔍 Security Testing

The system includes intentional security vulnerabilities for testing:

### Translation Agent Vulnerabilities
- HTML injection through `translate_text`
- XSS through script injection
- Cross-agent threat propagation

### Malicious Agent
- HTML injection via `inject_html`
- Data exfiltration via `extract_data`
- Security bypass via `bypass_security`

### Cross-Agent Threat Scenarios
- **Scenario 1**: Malicious agent → Translation agent data flow
- **Scenario 2**: Multi-agent attack chains
- **Scenario 3**: Benign agent-to-agent communication

## 🛡️ Security Features

### Real-time Monitoring
- **Request Analysis**: Scans parameters before execution
- **Response Analysis**: Monitors agent outputs for threats
- **Cross-Agent Analysis**: Tracks data flow between agents
- **Pattern Matching**: Uses regex patterns for threat detection
- **Severity Classification**: Categorizes threats by severity level

### Cross-Agent Threat Detection
- **Data Flow Tracking**: Monitors data passed between agents
- **Threat Propagation**: Detects threats that spread between agents
- **Multi-Agent Attack Chains**: Identifies complex attack patterns
- **Agent Interaction Analysis**: Analyzes communication patterns

### Comprehensive Logging
- **Interaction Logs**: Records all agent interactions
- **Security Events**: Logs detected security threats
- **Cross-Agent Events**: Tracks agent-to-agent communications
- **Alerts**: Generates security alerts for immediate attention

### Report Generation
- **Automated Reports**: Generates reports after each run
- **Threat Analysis**: Breaks down threats by type and agent
- **Cross-Agent Analysis**: Shows threat propagation patterns
- **Recommendations**: Provides actionable security recommendations

## 🔧 Configuration

### Agent Configuration
Agents are configured in the Real A2A SDK with their tools and capabilities:

```python
# Example agent registration
await a2a_server.register_agent("math_agent", math_agent)
await a2a_server.register_agent("weather_agent", weather_agent)
await a2a_server.register_agent("translation_agent", translation_agent)
await a2a_server.register_agent("malicious_agent", malicious_agent)
```

### Security Patterns
Security heuristics are defined in `src/security/heuristics.py`:

```python
self.threat_patterns = {
    "html_injection": [r"<!--.*?-->", r"<script.*?</script>", ...],
    "prompt_injection": [r"ignore\s+all\s+previous\s+instructions", ...],
    "data_exfiltration": [r"user\s+data", r"password", ...],
    # ... more patterns
}
```

## 🧪 Testing

The system includes comprehensive testing scenarios:

1. **Benign Interactions**: Normal agent operations
2. **Malicious Interactions**: Security vulnerability testing
3. **Agent-to-Agent**: Multi-agent communication scenarios
4. **Cross-Agent Threats**: Data flow threat detection
5. **Security Monitoring**: Real-time threat detection

## 📈 Monitoring and Analytics

### Metrics Tracked
- Total interactions per agent
- Security threats by type
- Cross-agent threat propagation
- Threat severity distribution
- Agent-specific threat counts
- Response times and performance

### Log Analysis
- Interaction patterns
- Security event correlation
- Cross-agent communication analysis
- Threat trend analysis
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly with `test_a2a_threat_detection.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the logs in the `src/logs/` directory
2. Review the security reports in the `src/reports/` directory
3. Run `test_a2a_threat_detection.py` to verify system functionality
4. Open an issue on GitHub

## 🔮 Future Enhancements

- **Machine Learning**: ML-based threat detection
- **Real-time Dashboard**: Web-based monitoring interface
- **Integration APIs**: REST API for external integrations
- **Advanced Agents**: More sophisticated agent capabilities
- **Distributed Architecture**: Multi-server deployment
- **Enhanced Cross-Agent Analysis**: More sophisticated threat propagation detection 