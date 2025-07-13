# Agent Sentinel

**Enterprise Security Monitoring for AI Agents**

Agent Sentinel provides comprehensive security monitoring, threat detection, and performance analytics for AI agents. Secure any AI agent in just 3 lines of code with real-time threat detection, behavioral analysis, and unified reporting.

## 🏗️ Project Structure

This repository contains two main components:

### 📦 [Agent Sentinel SDK](./agent-sentinel-sdk/)
The core Python SDK that provides security monitoring and threat detection for AI agents.

**Features:**
- **3-line integration** with `@monitor` and `@monitor_mcp()` decorators
- **Real-time threat detection** (SQL injection, XSS, code injection, etc.)
- **Performance monitoring** with detailed metrics
- **Unified reporting** - comprehensive reports in a single file
- **Enterprise-grade security** with configurable detection rules

**Quick Start:**
```python
from agent_sentinel import monitor, sentinel, monitor_mcp

# Monitor individual functions
@monitor
def process_data(data: str) -> str:
    return data.upper()

# Monitor entire classes
@sentinel
class MyAgent:
    def analyze_data(self, data):
        return data.upper()

# Monitor MCP tools
@monitor_mcp()
def search_database(query: str) -> str:
    return f"Searching for: {query}"
```

### 🎨 [Agent Sentinel Dashboard](./agent-sentinel-dashboard/)
A modern, enterprise-grade web dashboard for visualizing monitoring data and security reports.

**Features:**
- **Real-time monitoring** with live security events
- **Unified report visualization** with comprehensive insights
- **Black & red enterprise theme** for professional appearance
- **Responsive design** for desktop and mobile
- **Authentication** with Google OAuth and Supabase
- **Export capabilities** (PDF, JSON)

## 🚀 Getting Started

### For SDK Users
1. **Install the SDK:**
   ```bash
   pip install agent-sentinel
   ```

2. **Add monitoring to your agents:**
   ```python
   from agent_sentinel import monitor, sentinel, monitor_mcp
   
   # Monitor individual functions
   @monitor
   def your_agent_function():
       # Your agent code here
       pass
   
   # Monitor entire classes
   @sentinel
   class YourAgent:
       def process_data(self, data):
           # Your agent code here
           pass
   
   # Monitor MCP tools
   @monitor_mcp()
   def your_mcp_tool():
       # Your MCP tool code here
       pass
   ```

3. **Generate reports:**
   ```python
   from agent_sentinel.core.sentinel import AgentSentinel
   
   sentinel = AgentSentinel(agent_id="my-agent")
   report_path = sentinel.generate_unified_report()
   ```

### For Dashboard Users
1. **Navigate to the dashboard directory:**
   ```bash
   cd agent-sentinel-dashboard
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

4. **Run the dashboard:**
   ```bash
   npm run dev
   ```

## 📊 Unified Reporting

Agent Sentinel generates comprehensive unified reports that combine:
- **Security events** with severity and confidence scores
- **Performance metrics** (response time, memory usage, etc.)
- **Threat analysis** with detailed breakdowns
- **Actionable recommendations**
- **Session logs** for complete audit trail

**Sample Report Structure:**
```json
{
  "agent_id": "MathAgent",
  "executive_summary": {
    "status": "WARNING",
    "risk_score": 28.5,
    "threats_detected": 4,
    "performance_score": 87.2
  },
  "security_events": [...],
  "performance_metrics": {...},
  "threat_analysis": {...},
  "recommendations": [...]
}
```

## 🛡️ Security Features

### Threat Detection
- **SQL Injection** - Detects and blocks malicious SQL patterns
- **XSS Attacks** - Prevents cross-site scripting attempts
- **Code Injection** - Monitors for unauthorized code execution
- **Input Validation** - Validates and sanitizes user inputs
- **Performance Monitoring** - Tracks resource usage and performance

### Enterprise Features
- **Row Level Security** - Data isolation per user/organization
- **Audit Logging** - Complete audit trail of all activities
- **Real-time Alerts** - Instant notifications for security events
- **Configurable Rules** - Customizable detection thresholds
- **API Rate Limiting** - Protection against abuse

## 🎨 Design Philosophy

### Visual Theme
- **Black & Red Enterprise Theme** - Professional, security-focused appearance
- **High Contrast** - Excellent accessibility and readability
- **Clean Typography** - Modern, readable fonts
- **Responsive Design** - Works perfectly on all devices

### User Experience
- **3-Line Integration** - Minimal code changes required
- **Real-time Updates** - Live monitoring and alerts
- **Comprehensive Reports** - Everything in one unified file
- **Actionable Insights** - Clear recommendations and next steps

## 📈 Performance

- **Lightweight SDK** - Minimal performance impact
- **Real-time Processing** - Instant threat detection
- **Scalable Architecture** - Handles high-volume monitoring
- **Efficient Storage** - Optimized data storage and retrieval

## 🔧 Configuration

### SDK Configuration
```yaml
# config/agent_sentinel.yaml
agent_id: "my-agent"
logging:
  level: "INFO"
  file: "logs/agent_sentinel.log"
security:
  sql_injection_threshold: 0.8
  xss_threshold: 0.7
  performance_warning_mb: 500
```

### Dashboard Configuration
- **Supabase Integration** - Authentication and data storage
- **Google OAuth** - Single sign-on capabilities
- **Real-time Updates** - WebSocket connections
- **Export Options** - PDF and JSON report export

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### Development Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/agent-sentinel.git
   cd agent-sentinel
   ```

2. **Set up SDK development:**
   ```bash
   cd agent-sentinel-sdk
   pip install -e .
   ```

3. **Set up dashboard development:**
   ```bash
   cd agent-sentinel-dashboard
   npm install
   ```

## 📄 Documentation

- **[SDK Documentation](./agent-sentinel-sdk/README.md)** - Complete SDK guide
- **[Dashboard Documentation](./agent-sentinel-dashboard/README.md)** - Dashboard setup and usage
- **[API Reference](./agent-sentinel-sdk/docs/)** - Detailed API documentation
- **[Security Guide](./SECURITY.md)** - Security best practices
- **[Changelog](./CHANGELOG.md)** - Version history and updates

## 🏢 Enterprise Support

For enterprise customers, we offer:
- **Custom integrations** and deployments
- **Advanced security features** and configurations
- **Dedicated support** and training
- **SLA guarantees** and uptime commitments

## 📞 Support

- **Documentation:** [docs.agentsentinel.com](https://docs.agentsentinel.com)
- **Issues:** [GitHub Issues](https://github.com/your-org/agent-sentinel/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-org/agent-sentinel/discussions)
- **Email:** support@agentsentinel.com

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python and TypeScript
- Powered by Supabase for authentication and data storage
- Designed for enterprise security and scalability

---

**Agent Sentinel** - Secure your AI agents with enterprise-grade monitoring and threat detection.
