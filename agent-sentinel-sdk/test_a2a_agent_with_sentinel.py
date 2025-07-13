#!/usr/bin/env python3
"""
Test Agent Sentinel SDK on A2A MCP Server Agent
Wraps the real A2A agent functions with security monitoring
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the weave-streamlined-2file-output directory to Python path
sys.path.append('../weave-streamlined-2file-output')

from agent_sentinel.wrappers.decorators import monitor, sentinel

# Import the A2A MCP server
from src.a2a_mcp_server import RealA2AMCPServer

@sentinel
class SecuredA2AMCPServer(RealA2AMCPServer):
    """A2A MCP Server wrapped with Agent Sentinel security monitoring"""
    
    def __init__(self):
        super().__init__()
        print("🔒 A2A MCP Server secured with Agent Sentinel")
    
    @monitor
    async def invoke_agent_tool(self, agent_name: str, tool_name: str, parameters: dict) -> str:
        """Secured version of agent tool invocation"""
        return await super().invoke_agent_tool(agent_name, tool_name, parameters)
    
    @monitor
    async def run_mcp_agent_workflow(self):
        """Secured version of MCP agent workflow"""
        return await super().run_mcp_agent_workflow()
    
    @monitor
    async def run_mcp_a2a_workflow(self):
        """Secured version of MCP-A2A workflow"""
        return await super().run_mcp_a2a_workflow()
    
    @monitor
    async def run_security_testing(self):
        """Secured version of security testing"""
        return await super().run_security_testing()
    
    @monitor
    async def generate_security_report(self):
        """Secured version of security report generation"""
        return await super().generate_security_report()

async def test_secured_a2a_agent():
    """Test the A2A agent wrapped with Agent Sentinel"""
    print("🚀 Testing A2A Agent with Agent Sentinel SDK")
    print("=" * 60)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Initialize secured A2A server
    secured_server = SecuredA2AMCPServer()
    
    try:
        # Start the A2A server
        await secured_server.a2a_server.start_server()
        
        print("\n📊 Phase 1: Testing Individual Agent Operations")
        print("-" * 40)
        
        # Test math agent
        print("🔢 Testing Math Agent...")
        math_result = await secured_server.invoke_agent_tool("math_agent", "add", {"a": 15, "b": 27})
        print(f"   Result: 15 + 27 = {math_result}")
        
        # Test weather agent
        print("🌤️ Testing Weather Agent...")
        weather_result = await secured_server.invoke_agent_tool("weather_agent", "get_weather", {"city": "New York"})
        print(f"   Result: {weather_result}")
        
        # Test translation agent
        print("🌍 Testing Translation Agent...")
        translate_result = await secured_server.invoke_agent_tool(
            "translation_agent", 
            "translate_text", 
            {"text": "Hello world", "source_lang": "en", "target_lang": "es"}
        )
        print(f"   Result: {translate_result}")
        
        # Test malicious agent (should trigger security alerts)
        print("⚠️ Testing Malicious Agent (Security Test)...")
        malicious_result = await secured_server.invoke_agent_tool(
            "malicious_agent", 
            "inject_html", 
            {"payload": "<script>alert('test')</script>"}
        )
        print(f"   Result: {malicious_result}")
        
        print("\n🔄 Phase 2: Testing Agent-to-Agent Workflows")
        print("-" * 40)
        
        # Test MCP agent workflow
        print("🔄 Running MCP Agent Workflow...")
        await secured_server.run_mcp_agent_workflow()
        
        # Test MCP-A2A workflow
        print("🔄 Running MCP-A2A Workflow...")
        await secured_server.run_mcp_a2a_workflow()
        
        print("\n🔒 Phase 3: Testing Security Scenarios")
        print("-" * 40)
        
        # Test security scenarios
        print("🔒 Running Security Testing...")
        await secured_server.run_security_testing()
        
        print("\n📋 Phase 4: Generating Security Reports")
        print("-" * 40)
        
        # Generate security report
        print("📋 Generating Security Report...")
        log_file, report_file, report_content = await secured_server.generate_security_report()
        
        # Stop the server
        await secured_server.a2a_server.stop_server()
        
        # Check for Agent Sentinel logs and reports
        print("\n📊 Agent Sentinel Output Analysis")
        print("-" * 40)
        
        sentinel_logs = [f for f in os.listdir("logs") if f.endswith(".json")]
        sentinel_reports = [f for f in os.listdir("reports") if f.endswith(".json")]
        
        print(f"Agent Sentinel Log Files: {len(sentinel_logs)}")
        for log_file in sentinel_logs:
            print(f"  📄 {log_file}")
        
        print(f"Agent Sentinel Report Files: {len(sentinel_reports)}")
        for report_file in sentinel_reports:
            print(f"  📊 {report_file}")
        
        # Display summary
        print("\n" + "=" * 60)
        print("🎉 A2A AGENT TESTING WITH AGENT SENTINEL COMPLETED")
        print("=" * 60)
        print(f"Total Interactions: {len(secured_server.interaction_log)}")
        print(f"Security Events: {len(secured_server.blueguard.security_events)}")
        print(f"Security Alerts: {len(secured_server.blueguard.alerts)}")
        print(f"Cross-Agent Threats: {len(secured_server.blueguard.cross_agent_threats)}")
        print(f"Agent Sentinel Logs: {len(sentinel_logs)}")
        print(f"Agent Sentinel Reports: {len(sentinel_reports)}")
        
        return {
            "success": True,
            "interactions": len(secured_server.interaction_log),
            "security_events": len(secured_server.blueguard.security_events),
            "alerts": len(secured_server.blueguard.alerts),
            "cross_agent_threats": len(secured_server.blueguard.cross_agent_threats),
            "sentinel_logs": len(sentinel_logs),
            "sentinel_reports": len(sentinel_reports)
        }
        
    except Exception as e:
        print(f"❌ Error testing A2A agent: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Main test function"""
    print("Agent Sentinel SDK - A2A Agent Integration Test")
    print("=" * 60)
    
    # Run the async test
    result = asyncio.run(test_secured_a2a_agent())
    
    if result["success"]:
        print("\n✅ All tests completed successfully!")
        print(f"📊 Summary: {result['interactions']} interactions monitored")
        print(f"🔒 Security: {result['security_events']} events detected")
        print(f"📄 Logs: {result['sentinel_logs']} files generated")
        print(f"📊 Reports: {result['sentinel_reports']} files generated")
    else:
        print(f"\n❌ Test failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main() 