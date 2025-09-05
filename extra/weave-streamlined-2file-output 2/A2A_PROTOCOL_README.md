# A2A Protocol Implementation for BlueGuard Security System

This document describes the implementation of the Google A2A (Agent-to-Agent) protocol standards in the BlueGuard Security System.

## Overview

The A2A protocol implementation follows the official Google A2A standards for agent-to-agent communication, ensuring compatibility and interoperability with other A2A-compliant systems.

## Architecture

### Core Components

1. **A2A Protocol Layer** (`src/a2a_protocol/`)
   - `base_agent.py`: Base agent class following A2A standards
   - `agent_runner.py`: Agent execution and streaming management
   - `a2a_client.py`: A2A client for connecting to servers
   - `a2a_server.py`: A2A server for hosting agents

2. **Agent Cards** (`agent_cards/`)
   - JSON schema files defining agent capabilities and endpoints
   - Follows A2A agent card specification
   - Includes proper name tags and formatting

3. **A2A Agents** (`src/a2a_agents/`)
   - Math Agent: Mathematical operations
   - Weather Agent: Weather information and forecasts
   - Translation Agent: Text translation services
   - Malicious Agent: Security testing and threat simulation

4. **MCP Server** (`src/a2a_mcp_server_protocol.py`)
   - Integrates A2A protocol with MCP
   - Coordinates agent interactions
   - Provides security monitoring

## Agent Cards

Each agent has a corresponding agent card in JSON format following the A2A specification:

### Structure
```json
{
    "name": "Agent Name",
    "description": "Agent description",
    "url": "http://localhost:port/",
    "provider": "BlueGuard Security",
    "version": "1.0.0",
    "capabilities": {
        "streaming": "True",
        "pushNotifications": "False",
        "stateTransitionHistory": "False"
    },
    "authentication": {
        "credentials": null,
        "schemes": ["public"]
    },
    "defaultInputModes": ["text", "text/plain"],
    "defaultOutputModes": ["text", "text/plain"],
    "skills": [
        {
            "id": "skill_id",
            "name": "Skill Name",
            "description": "Skill description",
            "tags": ["tag1", "tag2"],
            "examples": ["example1", "example2"],
            "inputModes": null,
            "outputModes": null
        }
    ]
}
```

### Available Agent Cards

1. **Math Agent** (`agent_cards/math_agent.json`)
   - Skills: Mathematical operations (add, subtract, multiply, divide)
   - Tags: math, arithmetic, calculation

2. **Weather Agent** (`agent_cards/weather_agent.json`)
   - Skills: Weather information and forecasts
   - Tags: weather, forecast, temperature, climate

3. **Translation Agent** (`agent_cards/translation_agent.json`)
   - Skills: Text translation between languages
   - Tags: translation, language, multilingual

4. **Malicious Agent** (`agent_cards/malicious_agent.json`)
   - Skills: Security testing and threat simulation
   - Tags: security, testing, threat_detection

5. **BlueGuard Security Agent** (`agent_cards/blueguard_security_agent.json`)
   - Skills: Security monitoring and threat detection
   - Tags: security, monitoring, blueguard

## Protocol Features

### 1. Agent Discovery
- Agents are discoverable via MCP server
- Agent cards provide capability information
- Task-based agent matching

### 2. Agent Invocation
- Standardized invoke method
- Session-based interactions
- Error handling and logging

### 3. Streaming Support
- Real-time response streaming
- Context and task management
- Progress updates

### 4. Security Integration
- BlueGuard security monitoring
- Threat detection and analysis
- Comprehensive logging

## Usage

### Running the A2A Protocol Server

```python
from src.a2a_mcp_server_protocol import A2AMCPServer

# Initialize server
server = A2AMCPServer()

# Start server
await server.start_server()

# Invoke agents
result = await server.invoke_agent("math_agent", "Add 5 and 3", "session_1")

# Find agents for tasks
agents = await server.find_agents_for_task("mathematical calculations")

# Generate security report
log_file, report_file, report = await server.generate_security_report()
```

### Testing the Implementation

Run the test script to verify the A2A protocol implementation:

```bash
python test_a2a_protocol.py
```

## Key Improvements

### 1. Protocol Compliance
- Follows Google A2A protocol standards
- Proper agent card format
- Standardized communication patterns

### 2. Clean Architecture
- Separation of concerns
- Modular design
- Extensible framework

### 3. Security Integration
- Built-in security monitoring
- Threat detection capabilities
- Comprehensive logging

### 4. Agent Management
- Dynamic agent registration
- Task-based discovery
- Standardized interfaces

## File Structure

```
blueguard-mcp/
├── agent_cards/                    # A2A agent cards
│   ├── math_agent.json
│   ├── weather_agent.json
│   ├── translation_agent.json
│   ├── malicious_agent.json
│   └── blueguard_security_agent.json
├── src/
│   ├── a2a_protocol/              # A2A protocol implementation
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── agent_runner.py
│   │   ├── a2a_client.py
│   │   └── a2a_server.py
│   ├── a2a_agents/                # A2A agents
│   │   ├── __init__.py
│   │   ├── math_agent.py
│   │   ├── weather_agent.py
│   │   ├── translation_agent.py
│   │   └── malicious_agent.py
│   ├── a2a_mcp_server_protocol.py # MCP server with A2A protocol
│   └── security/                  # Security components
├── test_a2a_protocol.py          # Test script
└── A2A_PROTOCOL_README.md        # This file
```

## Compliance with A2A Standards

The implementation follows the key A2A protocol requirements:

1. **Agent Cards**: Proper JSON schema with all required fields
2. **Communication**: Standardized invoke and stream methods
3. **Discovery**: Agent registration and task-based matching
4. **Security**: Authentication schemes and capability definitions
5. **Extensibility**: Modular design for easy agent addition

## Next Steps

1. **Integration**: Connect with external A2A-compliant systems
2. **Advanced Features**: Implement push notifications and state transitions
3. **Performance**: Optimize for high-throughput scenarios
4. **Security**: Enhanced threat detection and response mechanisms

## References

- [Google A2A Protocol Documentation](https://github.com/a2aproject/a2a-samples)
- [A2A Agent Card Specification](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/a2a_mcp)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 