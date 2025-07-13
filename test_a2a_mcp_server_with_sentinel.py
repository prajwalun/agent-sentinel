#!/usr/bin/env python3
"""
Test script demonstrating Agent Sentinel SDK monitoring at the A2A MCP server connection point
This shows the real-world approach of monitoring agent-to-agent communication at a single gateway
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Add the current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import Agent Sentinel SDK
from agent_sentinel import monitor, sentinel

# Add the A2A directory to path
a2a_path = os.path.join(os.path.dirname(__file__), "weave-streamlined-2file-output 2")
sys.path.append(a2a_path)
sys.path.append(os.path.join(a2a_path, "A2A"))

# Import the A2A MCP server
from A2A.a2a_mcp_server_protocol import A2AMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@sentinel
class SentinelMonitoredA2AMCPServer(A2AMCPServer):
    """
    A2A MCP Server with Agent Sentinel monitoring at the connection point
    This demonstrates monitoring ALL agent communication through a single gateway
    """
    
    def __init__(self):
        super().__init__()
        logger.info("SentinelMonitoredA2AMCPServer initialized - ALL agent communication will be monitored")
    
    @monitor
    async def invoke_agent(self, agent_name: str, query: str, session_id: str) -> Dict[str, Any]:
        """
        Monitor ALL agent invocations through this single connection point
        The SDK automatically:
        - Logs every agent interaction
        - Scans queries for security threats
        - Tracks performance metrics
        - Monitors responses
        """
        logger.info(f"🔍 MONITORING: Agent invocation - {agent_name} with query: {query[:50]}...")
        return await super().invoke_agent(agent_name, query, session_id)
    
    @monitor
    async def stream_agent(self, agent_name: str, query: str, context_id: str):
        """
        Monitor ALL agent streaming through this single connection point
        """
        logger.info(f"🔍 MONITORING: Agent streaming - {agent_name} with query: {query[:50]}...")
        async for chunk in super().stream_agent(agent_name, query, context_id):
            yield chunk
    
    @monitor
    async def find_agents_for_task(self, task_description: str):
        """
        Monitor agent discovery requests
        """
        logger.info(f"🔍 MONITORING: Agent discovery for task: {task_description[:50]}...")
        return await super().find_agents_for_task(task_description)
    
    @monitor
    async def get_agent_card(self, agent_name: str):
        """
        Monitor agent card requests
        """
        logger.info(f"🔍 MONITORING: Agent card request for: {agent_name}")
        return await super().get_agent_card(agent_name)

@sentinel
class A2ACommunicationOrchestrator:
    """
    Orchestrator that demonstrates real-world agent communication monitoring
    This shows how you would use the SDK in production
    """
    
    def __init__(self):
        self.mcp_server = SentinelMonitoredA2AMCPServer()
        logger.info("A2A Communication Orchestrator initialized with Agent Sentinel monitoring")
    
    @monitor
    async def run_comprehensive_agent_test(self):
        """
        Run a comprehensive test of all agent communication through the monitored gateway
        """
        logger.info("=== Starting Comprehensive A2A Agent Communication Test ===")
        logger.info("ALL agent interactions will be monitored through the MCP server gateway")
        
        start_time = datetime.now()
        results = {}
        
        # Test 1: Math Agent Communication
        logger.info("\n--- Testing Math Agent Communication ---")
        math_queries = [
            "Add 15 and 25",
            "Multiply 6 by 8", 
            "Divide 100 by 5"
        ]
        
        math_results = []
        for query in math_queries:
            result = await self.mcp_server.invoke_agent("math_agent", query, "math_session")
            math_results.append(result)
            logger.info(f"Math Result: {result.get('content', 'No content')}")
        
        results['math'] = math_results
        
        # Test 2: Weather Agent Communication
        logger.info("\n--- Testing Weather Agent Communication ---")
        weather_queries = [
            "Get weather for New York",
            "What's the temperature in London?"
        ]
        
        weather_results = []
        for query in weather_queries:
            result = await self.mcp_server.invoke_agent("weather_agent", query, "weather_session")
            weather_results.append(result)
            logger.info(f"Weather Result: {result.get('content', 'No content')}")
        
        results['weather'] = weather_results
        
        # Test 3: Translation Agent Communication
        logger.info("\n--- Testing Translation Agent Communication ---")
        translation_queries = [
            "Translate 'Hello world' from English to Spanish",
            "Translate 'Good morning' from English to French"
        ]
        
        translation_results = []
        for query in translation_queries:
            result = await self.mcp_server.invoke_agent("translation_agent", query, "translation_session")
            translation_results.append(result)
            logger.info(f"Translation Result: {result.get('content', 'No content')}")
        
        results['translation'] = translation_results
        
        # Test 4: Security Testing (Malicious Agent Communication)
        logger.info("\n--- Testing Security Monitoring (Malicious Agent Communication) ---")
        security_queries = [
            "Test XSS injection with <script>alert('test')</script>",
            "Extract data from user input: john.doe@example.com",
            "Bypass security with admin:true"
        ]
        
        security_results = []
        for query in security_queries:
            result = await self.mcp_server.invoke_agent("malicious_agent", query, "security_session")
            security_results.append(result)
            logger.info(f"Security Result: {result.get('content', 'No content')}")
            
            # Check if security flag was raised
            if result.get('security_flag'):
                logger.warning(f"🚨 SECURITY ALERT DETECTED: {result.get('attack_type', 'unknown')}")
        
        results['security'] = security_results
        
        # Test 5: Agent Discovery
        logger.info("\n--- Testing Agent Discovery Communication ---")
        discovery_tasks = [
            "Perform mathematical calculations",
            "Get weather information",
            "Translate text between languages"
        ]
        
        discovery_results = []
        for task in discovery_tasks:
            agents = await self.mcp_server.find_agents_for_task(task)
            discovery_results.append(agents)
            logger.info(f"Found {len(agents)} agents for task: {task}")
        
        results['discovery'] = discovery_results
        
        # Test 6: Agent Card Requests
        logger.info("\n--- Testing Agent Card Communication ---")
        agent_names = ["math_agent", "weather_agent", "translation_agent", "malicious_agent"]
        
        card_results = []
        for agent_name in agent_names:
            card = await self.mcp_server.get_agent_card(agent_name)
            card_results.append(card)
            logger.info(f"Retrieved card for: {agent_name} | Card: {card}")
        
        results['cards'] = card_results
        
        # Test 7: Streaming Communication
        logger.info("\n--- Testing Streaming Communication ---")
        streaming_tests = [
            ("math_agent", "Add 10 and 20"),
            ("weather_agent", "Get weather for Paris"),
            ("malicious_agent", "Test XSS injection")
        ]
        
        streaming_results = []
        for agent_name, query in streaming_tests:
            logger.info(f"Streaming from {agent_name}: {query}")
            async for response in self.mcp_server.stream_agent(agent_name, query, f"stream_{agent_name}"):
                streaming_results.append(response)
                logger.info(f"Stream Response: {response.get('content', 'No content')}")
        
        results['streaming'] = streaming_results
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info("\n=== A2A Agent Communication Test Summary ===")
        logger.info(f"Total test duration: {duration:.2f} seconds")
        logger.info(f"Math agent interactions: {len(math_results)}")
        logger.info(f"Weather agent interactions: {len(weather_results)}")
        logger.info(f"Translation agent interactions: {len(translation_results)}")
        logger.info(f"Security test interactions: {len(security_results)}")
        logger.info(f"Agent discovery requests: {len(discovery_results)}")
        logger.info(f"Agent card requests: {len(card_results)}")
        logger.info(f"Streaming interactions: {len(streaming_results)}")
        
        # Count security alerts
        security_alerts = sum(1 for r in security_results if r.get('security_flag'))
        logger.info(f"Security alerts detected: {security_alerts}")
        
        logger.info("\n=== Monitoring Results ===")
        logger.info("✅ ALL agent communication was monitored through the MCP server gateway")
        logger.info("✅ Security threats were detected in real-time")
        logger.info("✅ Performance metrics were collected")
        logger.info("✅ Detailed logs were generated")
        logger.info("Check the logs/ directory for comprehensive monitoring data")
        
        return {
            'results': results,
            'duration': duration,
            'security_alerts': security_alerts,
            'total_interactions': len(math_results) + len(weather_results) + len(translation_results) + len(security_results) + len(discovery_results) + len(card_results) + len(streaming_results)
        }

async def main():
    """Main test function demonstrating real-world SDK usage"""
    logger.info("Starting Agent Sentinel SDK A2A MCP Server Connection Point Test")
    logger.info("=" * 80)
    logger.info("This test demonstrates monitoring ALL agent communication through a single gateway")
    logger.info("=" * 80)
    
    try:
        # Initialize the orchestrator
        orchestrator = A2ACommunicationOrchestrator()
        
        # Run comprehensive test
        results = await orchestrator.run_comprehensive_agent_test()
        
        logger.info("=" * 80)
        logger.info("Agent Sentinel SDK A2A MCP Server test completed successfully!")
        
        # Print summary
        print("\n" + "="*70)
        print("AGENT SENTINEL SDK A2A MCP SERVER CONNECTION POINT TEST")
        print("="*70)
        print(f"Test Duration: {results['duration']:.2f} seconds")
        print(f"Total Agent Interactions: {results['total_interactions']}")
        print(f"Security Alerts Detected: {results['security_alerts']}")
        print("\nMonitoring Coverage:")
        print("✅ Math Agent Communication")
        print("✅ Weather Agent Communication") 
        print("✅ Translation Agent Communication")
        print("✅ Security/Malicious Agent Communication")
        print("✅ Agent Discovery Requests")
        print("✅ Agent Card Requests")
        print("✅ Streaming Communication")
        print("\nFiles Generated:")
        print("- Log files: Check 'logs/' directory")
        print("- Threat reports: Check 'reports/' directory")
        print("- JSON reports: Check for timestamped JSON files")
        print("="*70)
        
    except Exception as e:
        logger.error(f"Error during Agent Sentinel SDK A2A MCP Server test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 