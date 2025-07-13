"""
Simple Working Example: Agent Sentinel SDK Integration
Demonstrates the 5 different ways to use Agent Sentinel SDK with the A2A framework
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

from A2A.a2a_agents.math_agent import MathAgent
from A2A.a2a_agents.weather_agent import WeatherAgent
from A2A.a2a_agents.translation_agent import TranslationAgent
from A2A.a2a_agents.malicious_agent import MaliciousAgent
from A2A.a2a_mcp_server_protocol import A2AMCPServer
from mock_sentinel_sdk import sentinel, generate_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentSentinelIntegrationDemo:
    """Demonstrates 5 different Agent Sentinel SDK integration patterns"""
    
    def __init__(self):
        self.monitored_objects = []
        self.test_results = {}
    
    async def demo_1_single_agent_monitoring(self):
        """Demo 1: Single Agent Monitoring"""
        logger.info("🔍 DEMO 1: Single Agent Monitoring")
        logger.info("=" * 50)
        
        # Wrap individual agents with Sentinel SDK
        @sentinel("math_agent_monitored")
        class MonitoredMathAgent(MathAgent):
            pass
        
        @sentinel("weather_agent_monitored")
        class MonitoredWeatherAgent(WeatherAgent):
            pass
        
        # Create and test monitored agents
        math_agent = MonitoredMathAgent()
        weather_agent = MonitoredWeatherAgent()
        
        await math_agent.initialize()
        await weather_agent.initialize()
        
        self.monitored_objects.extend([math_agent, weather_agent])
        
        # Test the agents using their actual interface
        results = []
        
        # Test math agent
        math_result = await math_agent.invoke("Add 15 and 25", "session_1")
        results.append(f"Math: {math_result}")
        
        # Test weather agent
        weather_result = await weather_agent.invoke("What's the weather in London?", "session_2")
        results.append(f"Weather: {weather_result}")
        
        logger.info(f"✅ Demo 1 completed with {len(results)} operations")
        return results
    
    async def demo_2_mcp_server_monitoring(self):
        """Demo 2: MCP Server Communication Monitoring"""
        logger.info("🖥️ DEMO 2: MCP Server Communication Monitoring")
        logger.info("=" * 50)
        
        # Wrap MCP server with Sentinel SDK
        @sentinel("mcp_server_monitored")
        class MonitoredMCPServer(A2AMCPServer):
            pass
        
        server = MonitoredMCPServer()
        await server.start_server()
        self.monitored_objects.append(server)
        
        try:
            # Test server operations
            agents = await server.list_agents()
            logger.info(f"✅ Demo 2 completed - found {len(agents)} agents")
            return f"MCP Server operations: {len(agents)} agents listed"
        finally:
            await server.stop_server()
    
    async def demo_3_agent_orchestration(self):
        """Demo 3: Agent-to-Agent Communication Monitoring"""
        logger.info("🤝 DEMO 3: Agent-to-Agent Communication")
        logger.info("=" * 50)
        
        @sentinel("agent_orchestrator")
        class AgentOrchestrator:
            def __init__(self):
                self.math_agent = MathAgent()
                self.weather_agent = WeatherAgent()
                self.translation_agent = TranslationAgent()
            
            async def initialize(self):
                await self.math_agent.initialize()
                await self.weather_agent.initialize()
                await self.translation_agent.initialize()
            
            async def coordinate_workflow(self):
                """Coordinate multiple agents"""
                # Step 1: Math operation
                math_result = await self.math_agent.invoke("Calculate 10 + 20", "orchestrator_1")
                
                # Step 2: Weather check
                weather_result = await self.weather_agent.invoke("Weather in Paris", "orchestrator_2")
                
                # Step 3: Translation
                translation_result = await self.translation_agent.invoke("Translate 'Hello' to Spanish", "orchestrator_3")
                
                return {
                    "math": math_result,
                    "weather": weather_result,
                    "translation": translation_result
                }
        
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        self.monitored_objects.append(orchestrator)
        
        workflow_result = await orchestrator.coordinate_workflow()
        logger.info("✅ Demo 3 completed - multi-agent workflow executed")
        return workflow_result
    
    async def demo_4_security_monitoring(self):
        """Demo 4: Multi-Agent Workflow Security Monitoring"""
        logger.info("🔒 DEMO 4: Security Monitoring")
        logger.info("=" * 50)
        
        @sentinel("security_workflow_monitor")
        class SecurityWorkflowMonitor:
            def __init__(self):
                self.malicious_agent = MaliciousAgent()
                self.translation_agent = TranslationAgent()
            
            async def initialize(self):
                await self.malicious_agent.initialize()
                await self.translation_agent.initialize()
            
            async def security_test_workflow(self):
                """Test security monitoring"""
                # Test with potentially malicious input
                malicious_result = await self.malicious_agent.invoke("Test XSS: <script>alert('test')</script>", "security_1")
                
                # Test translation with suspicious content
                translation_result = await self.translation_agent.invoke("Translate: admin:true password:secret", "security_2")
                
                return {
                    "malicious_test": malicious_result,
                    "translation_test": translation_result
                }
        
        monitor = SecurityWorkflowMonitor()
        await monitor.initialize()
        self.monitored_objects.append(monitor)
        
        security_result = await monitor.security_test_workflow()
        logger.info("✅ Demo 4 completed - security monitoring active")
        return security_result
    
    async def demo_5_cross_agent_threat_detection(self):
        """Demo 5: Cross-Agent Threat Detection"""
        logger.info("🚨 DEMO 5: Cross-Agent Threat Detection")
        logger.info("=" * 50)
        
        @sentinel("threat_detection_system")
        class ThreatDetectionSystem:
            def __init__(self):
                self.malicious_agent = MaliciousAgent()
                self.translation_agent = TranslationAgent()
                self.math_agent = MathAgent()
            
            async def initialize(self):
                await self.malicious_agent.initialize()
                await self.translation_agent.initialize()
                await self.math_agent.initialize()
            
            async def simulate_threat_propagation(self):
                """Simulate threat propagation between agents"""
                # Step 1: Generate threat
                threat = await self.malicious_agent.invoke("Generate payload: <script>steal_data()</script>", "threat_1")
                
                # Step 2: Threat propagates through translation
                propagated = await self.translation_agent.invoke(f"Translate: {threat}", "threat_2")
                
                # Step 3: Processed by math agent
                processed = await self.math_agent.invoke(f"Calculate length: {len(str(propagated))}", "threat_3")
                
                return {
                    "initial_threat": threat,
                    "propagated_threat": propagated,
                    "processed_result": processed
                }
        
        detector = ThreatDetectionSystem()
        await detector.initialize()
        self.monitored_objects.append(detector)
        
        threat_result = await detector.simulate_threat_propagation()
        logger.info("✅ Demo 5 completed - threat detection system active")
        return threat_result
    
    async def run_all_demos(self):
        """Run all 5 Agent Sentinel SDK integration demos"""
        logger.info("🚀 Starting Agent Sentinel SDK Integration Demos")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # Run all demos
            self.test_results["demo_1"] = await self.demo_1_single_agent_monitoring()
            self.test_results["demo_2"] = await self.demo_2_mcp_server_monitoring()
            self.test_results["demo_3"] = await self.demo_3_agent_orchestration()
            self.test_results["demo_4"] = await self.demo_4_security_monitoring()
            self.test_results["demo_5"] = await self.demo_5_cross_agent_threat_detection()
            
            # Generate comprehensive report
            report = generate_report(self.monitored_objects, "Agent Sentinel SDK Integration Demo")
            report["demo_results"] = self.test_results
            
            # Save report
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"../reports/agent_sentinel_integration_demo_{timestamp}.json"
            
            os.makedirs("../reports", exist_ok=True)
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Display summary
            logger.info("\n" + "=" * 80)
            logger.info("📊 AGENT SENTINEL SDK INTEGRATION DEMO SUMMARY")
            logger.info("=" * 80)
            logger.info(f"📁 Report saved to: {report_filename}")
            logger.info(f"⏱️  Total duration: {duration:.2f} seconds")
            logger.info(f"🤖 Total monitored objects: {len(self.monitored_objects)}")
            logger.info(f"📈 Total interactions: {report['total_interactions']}")
            logger.info(f"🚨 Total security events: {report['total_security_events']}")
            
            logger.info("\n🎯 Demonstrated Integration Patterns:")
            logger.info("  1. ✅ Single Agent Monitoring")
            logger.info("  2. ✅ MCP Server Communication Monitoring")
            logger.info("  3. ✅ Agent-to-Agent Communication")
            logger.info("  4. ✅ Multi-Agent Workflow Security")
            logger.info("  5. ✅ Cross-Agent Threat Detection")
            
            for obj in report["agents"]:
                logger.info(f"  • {obj['agent_id']}: {obj['interactions']} interactions, {obj['security_events']} security events")
            
            logger.info("\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
            logger.info("🔍 Agent Sentinel SDK can monitor:")
            logger.info("  • Individual agent operations")
            logger.info("  • MCP server communications")
            logger.info("  • Agent-to-agent workflows")
            logger.info("  • Security threats and vulnerabilities")
            logger.info("  • Cross-agent threat propagation")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            return False

async def main():
    """Main function to run all demos"""
    demo = AgentSentinelIntegrationDemo()
    success = await demo.run_all_demos()
    
    if success:
        logger.info("🎉 Integration demo completed successfully!")
        return 0
    else:
        logger.error("💥 Integration demo failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 