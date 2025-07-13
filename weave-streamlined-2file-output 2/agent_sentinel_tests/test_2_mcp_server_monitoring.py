"""
Test 2: MCP Server Communication Monitoring
Demonstrates how to monitor MCP server communications using the Agent Sentinel SDK
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from A2A.a2a_mcp_server_protocol import A2AMCPServer
from mock_sentinel_sdk import sentinel, generate_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestMCPServerMonitoring:
    """Test class for MCP server communication monitoring"""
    
    def __init__(self):
        self.test_name = "MCP Server Communication Monitoring"
        self.monitored_servers = []
    
    async def test_mcp_server_operations(self):
        """Test monitoring MCP server operations"""
        logger.info("🖥️ Testing MCP Server Operations Monitoring...")
        
        # Create monitored MCP server
        @sentinel("a2a_mcp_server_monitored")
        class MonitoredA2AMCPServer(A2AMCPServer):
            pass
        
        server = MonitoredA2AMCPServer()
        await server.start_server()
        self.monitored_servers.append(server)
        
        try:
            # Test server operations
            operations_results = []
            
            # Test 1: List agents
            logger.info("📋 Testing agent listing...")
            agents = await server.list_agents()
            operations_results.append(f"Listed {len(agents)} agents")
            logger.info(f"✅ Found {len(agents)} agents")
            
            # Test 2: Agent discovery by task
            logger.info("🔍 Testing agent discovery...")
            tasks = [
                "Calculate the sum of two numbers",
                "Get current weather conditions",
                "Translate text to Spanish",
                "Test for security vulnerabilities"
            ]
            
            for task in tasks:
                matching_agents = await server.find_agents_for_task(task)
                operations_results.append(f"Task '{task}': {len(matching_agents)} agents")
                logger.info(f"✅ Task '{task}': {len(matching_agents)} matching agents")
            
            # Test 3: Agent execution
            logger.info("⚙️ Testing agent execution...")
            execution_tests = [
                ("math_agent", "Calculate 15 + 25"),
                ("weather_agent", "What's the weather in London?"),
                ("translation_agent", "Translate 'Hello' from English to Spanish")
            ]
            
            for agent_id, query in execution_tests:
                try:
                    result = await server.invoke_agent(agent_id, query, "test_session")
                    operations_results.append(f"Executed {agent_id}: {result}")
                    logger.info(f"✅ {agent_id}: {result}")
                except Exception as e:
                    operations_results.append(f"Failed {agent_id}: {e}")
                    logger.error(f"❌ {agent_id} failed: {e}")
            
            # Test 4: Agent card retrieval
            logger.info("📄 Testing agent card retrieval...")
            for agent in agents:
                try:
                    card = await server.get_agent_card(agent["name"])
                    operations_results.append(f"Retrieved card for {agent['name']}")
                    logger.info(f"✅ Retrieved card for {agent['name']}")
                except Exception as e:
                    operations_results.append(f"Failed to get card for {agent['name']}: {e}")
                    logger.error(f"❌ Failed to get card for {agent['name']}: {e}")
            
            return operations_results
            
        finally:
            await server.stop_server()
    
    async def test_mcp_security_monitoring(self):
        """Test security monitoring in MCP server communications"""
        logger.info("🔒 Testing MCP Server Security Monitoring...")
        
        @sentinel("mcp_security_monitor")
        class SecurityMonitoredMCPServer(A2AMCPServer):
            pass
        
        server = SecurityMonitoredMCPServer()
        await server.start_server()
        self.monitored_servers.append(server)
        
        try:
            security_test_results = []
            
            # Test with potentially malicious inputs
            malicious_tests = [
                ("malicious_agent", "inject_html", {"payload": "<script>alert('xss')</script>"}),
                ("translation_agent", "translate", {"text": "admin:true password:secret123", "from_lang": "English", "to_lang": "Spanish"}),
                ("malicious_agent", "extract_data", {"target": "user passwords"}),
                ("malicious_agent", "bypass_security", {"method": "admin override"})
            ]
            
            for agent_id, skill, params in malicious_tests:
                try:
                    result = await server.invoke_agent(agent_id, f"{skill} with params", "security_session")
                    security_test_results.append(f"Security test {agent_id}.{skill}: {result}")
                    logger.info(f"🔍 Security test {agent_id}.{skill}: {result}")
                except Exception as e:
                    security_test_results.append(f"Security test {agent_id}.{skill} failed: {e}")
                    logger.error(f"❌ Security test {agent_id}.{skill} failed: {e}")
            
            return security_test_results
            
        finally:
            await server.stop_server()
    
    async def test_mcp_workflow_monitoring(self):
        """Test monitoring complex workflows through MCP server"""
        logger.info("🔄 Testing MCP Server Workflow Monitoring...")
        
        @sentinel("mcp_workflow_monitor")
        class WorkflowMonitoredMCPServer(A2AMCPServer):
            pass
        
        server = WorkflowMonitoredMCPServer()
        await server.start_server()
        self.monitored_servers.append(server)
        
        try:
            workflow_results = []
            
            # Simulate a complex workflow
            logger.info("🌟 Executing complex workflow...")
            
            # Step 1: Get weather
            weather_result = await server.execute_agent("weather_agent", "get_weather", {"city": "Paris"})
            workflow_results.append(f"Step 1 - Weather: {weather_result}")
            
            # Step 2: Process temperature calculation
            temp_result = await server.execute_agent("math_agent", "add", {"a": 18, "b": 5})
            workflow_results.append(f"Step 2 - Temperature calc: {temp_result}")
            
            # Step 3: Translate result
            translation_result = await server.execute_agent("translation_agent", "translate", {
                "text": f"Temperature: {temp_result}°C",
                "from_lang": "English",
                "to_lang": "French"
            })
            workflow_results.append(f"Step 3 - Translation: {translation_result}")
            
            # Step 4: Security check
            security_result = await server.execute_agent("malicious_agent", "bypass_security", {"method": "workflow_test"})
            workflow_results.append(f"Step 4 - Security: {security_result}")
            
            logger.info("✅ Complex workflow completed successfully")
            return workflow_results
            
        finally:
            await server.stop_server()
    
    async def run_all_tests(self):
        """Run all MCP server monitoring tests"""
        logger.info("🚀 Starting MCP Server Monitoring Tests...")
        logger.info("=" * 60)
        
        test_results = {}
        
        try:
            # Run individual tests
            test_results["mcp_operations"] = await self.test_mcp_server_operations()
            test_results["mcp_security"] = await self.test_mcp_security_monitoring()
            test_results["mcp_workflow"] = await self.test_mcp_workflow_monitoring()
            
            # Generate comprehensive report
            report = generate_report(self.monitored_servers, self.test_name)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"../reports/test_2_mcp_server_monitoring_{timestamp}.json"
            
            os.makedirs("../reports", exist_ok=True)
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Display summary
            logger.info("\n" + "=" * 60)
            logger.info("📊 MCP SERVER MONITORING TEST SUMMARY")
            logger.info("=" * 60)
            logger.info(f"📁 Report saved to: {report_filename}")
            logger.info(f"🖥️ Total servers monitored: {len(self.monitored_servers)}")
            logger.info(f"📈 Total interactions: {report['total_interactions']}")
            logger.info(f"🚨 Total security events: {report['total_security_events']}")
            
            for server in report["agents"]:
                logger.info(f"  • {server['agent_id']}: {server['interactions']} interactions, {server['security_events']} security events")
            
            logger.info("✅ MCP Server Monitoring Tests Completed Successfully!")
            
            return {
                "test_results": test_results,
                "monitoring_report": report,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ MCP Server Monitoring Tests Failed: {e}")
            return {
                "test_results": test_results,
                "error": str(e),
                "success": False
            }

async def main():
    """Main function to run the MCP server monitoring test"""
    test = TestMCPServerMonitoring()
    result = await test.run_all_tests()
    
    if result["success"]:
        logger.info("🎉 Test completed successfully!")
        return 0
    else:
        logger.error("💥 Test failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 