# 🎮 Agent Sentinel SDK Demo Collection

This folder contains 4 different demo agents that showcase various capabilities of the Agent Sentinel SDK [[memory:3070509]]. Each agent demonstrates different integration patterns and use cases.

## 🚀 Demo Agents

### 1. **A2A Agent Communication** (`1_a2a_agent_communication.py`)
**Demonstrates:** Agent-to-Agent (A2A) communication with security monitoring

- **Features:** Multi-agent discovery, task routing, security monitoring
- **Use Case:** Shows how agents can communicate with each other and find suitable agents for specific tasks
- **Key Components:**
  - Agent discovery and capability matching
  - Secure inter-agent communication
  - BlueGuard security integration
  - Task-based agent selection

### 2. **Single MCP Agent** (`2_single_mcp_agent.py`)
**Demonstrates:** Basic MCP (Model Context Protocol) agent patterns

- **Features:** Individual MCP agent functions with monitoring
- **Use Case:** Shows how to wrap MCP-style functions with Agent Sentinel
- **Key Components:**
  - GitHub MCP operations
  - Notion MCP operations
  - Calendar MCP operations
  - Search MCP operations
  - Multi-MCP orchestration

### 3. **Multi-Agent MCP System** (`3_multi_mcp_agents.py`)
**Demonstrates:** Complex MCP orchestration with multiple specialized agents

- **Features:** Comprehensive MCP agent ecosystem
- **Use Case:** Shows advanced MCP patterns for travel planning, web automation, and more
- **Key Components:**
  - Travel planning agents (Airbnb, Google Maps, Weather)
  - Browser automation agents (Navigation, Interaction, Screenshots)
  - Productivity agents (Calendar, Email, File System)
  - Advanced orchestration patterns

### 4. **Meeting Agent Pattern** (`4_meeting_agent_pattern.py`)
**Demonstrates:** Real-world agent implementation with mocking

- **Features:** Practical agent pattern with external dependencies
- **Use Case:** Shows how to build production-ready agents with proper testing
- **Key Components:**
  - AI meeting preparation
  - Component-based architecture
  - Mock integration for testing
  - Streamlit UI integration

## 🔧 Requirements

All demos use the Agent Sentinel SDK with the following decorators:
- `@monitor` - For monitoring individual functions
- `@sentinel` - For monitoring entire classes  
- `@monitor_mcp()` - For monitoring MCP-style operations

## 🚀 Running the Demos

### Setup
```bash
# Make sure you're in the demo directory
cd demo

# Install dependencies (if needed)
pip install -e ../agent-sentinel-sdk
```

### Run Individual Demos
```bash
# 1. A2A Agent Communication
python 1_a2a_agent_communication.py

# 2. Single MCP Agent
python 2_single_mcp_agent.py

# 3. Multi-Agent MCP System
python 3_multi_mcp_agents.py

# 4. Meeting Agent Pattern
python 4_meeting_agent_pattern.py
```

## 📊 Expected Output

Each demo will:
1. **Execute agent operations** with real-time monitoring
2. **Generate security reports** showing threat detection
3. **Create unified reports** with performance metrics
4. **Demonstrate SDK integration** with minimal code changes

## 🛡️ Security Monitoring

All demos include comprehensive security monitoring:
- **Threat Detection**: SQL injection, XSS, code injection
- **Performance Monitoring**: Response time, memory usage
- **Behavioral Analysis**: Pattern recognition and anomaly detection
- **Unified Reporting**: Single file with all insights

## 📁 Support Files

- **`A2A/`**: Agent-to-Agent communication protocol and agents
- **`A2A/a2a_agents/`**: Individual A2A agent implementations
- **`A2A/agent_cards/`**: Agent capability cards and metadata

## 🎯 Key Takeaways

1. **3-Line Integration**: Add monitoring with minimal code changes
2. **Comprehensive Coverage**: Monitor any type of agent operation
3. **Enterprise Security**: Production-ready threat detection
4. **Unified Reporting**: All insights in one place
5. **Flexible Patterns**: Works with any agent architecture

---

**Ready to secure your AI agents?** Start with any of these demos and see how Agent Sentinel provides enterprise-grade security monitoring with just a few lines of code! 