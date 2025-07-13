"""
Real Agent Sentinel SDK Integration Test
Replaces mock SDK with actual Agent Sentinel SDK for all test patterns
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'agent-sentinel-sdk', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'A2A'))

from agent_sentinel import AgentSentinel, sentinel, monitor, get_all_events
from agent_sentinel.core.types import SecurityEvent
from agent_sentinel.core.constants import ThreatType, SeverityLevel
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import A2A agents
from a2a_agents.math_agent import MathAgent
from a2a_agents.weather_agent import WeatherAgent
from a2a_agents.translation_agent import TranslationAgent
from a2a_agents.malicious_agent import MaliciousAgent
from a2a_mcp_server_protocol import A2AMCPServer
from a2a_protocol.a2a_server import A2AServer
from a2a_protocol.a2a_client import A2AClient

class RealSDKIntegrationTest:
    """Integration test using the real Agent Sentinel SDK"""
    
    def __init__(self):
        # Initialize the real Agent Sentinel SDK
        self.sentinel = AgentSentinel(
            agent_id="integration_test",
            auto_start=True,
            enable_threat_intelligence=False
        )
        
        # Track security events
        self.security_events = []
        self.sentinel.add_event_handler(self._handle_security_event)
        
        # Test results
        self.test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "security_events": 0,
            "test_details": []
        }
    
    def _handle_security_event(self, event: SecurityEvent):
        """Handle security events from the real SDK"""
        logger.warning(f"🚨 [SENTINEL THREAT] {event.threat_type.value} detected: {event.message}")
        self.security_events.append(event)
        self.test_results["security_events"] += 1
    
    def create_monitored_agent(self, agent_class, agent_id: str):
        """Create a monitored version of an agent using the real SDK"""
        @sentinel
        class MonitoredAgent(agent_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._sentinel_agent_id = agent_id
        
        return MonitoredAgent
    
    async def test_single_agent_monitoring(self):
        """Test 1: Single Agent Monitoring"""
        logger.info("🧮 Test 1: Single Agent Monitoring")
        self.test_results["total_tests"] += 1
        
        try:
            # Create monitored agents
            MonitoredMathAgent = self.create_monitored_agent(MathAgent, "math_agent")
            MonitoredWeatherAgent = self.create_monitored_agent(WeatherAgent, "weather_agent")
            MonitoredTranslationAgent = self.create_monitored_agent(TranslationAgent, "translation_agent")
            
            # Test math agent
            math_agent = MonitoredMathAgent()
            result = await math_agent.execute_skill("add", {"a": 10, "b": 20})
            assert result["result"] == 30.0
            
            # Test weather agent
            weather_agent = MonitoredWeatherAgent()
            result = await weather_agent.execute_skill("get_weather", {"city": "London"})
            assert "weather_data" in result
            
            # Test translation agent
            translation_agent = MonitoredTranslationAgent()
            result = await translation_agent.execute_skill("translate", {"text": "Hello", "source_lang": "en", "target_lang": "es"})
            assert "translated_text" in result
            
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({"test": "Single Agent Monitoring", "status": "PASSED"})
            logger.info("✅ Test 1 PASSED")
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({"test": "Single Agent Monitoring", "status": "FAILED", "error": str(e)})
            logger.error(f"❌ Test 1 FAILED: {e}")
    
    async def test_mcp_server_monitoring(self):
        """Test 2: MCP Server Monitoring"""
        logger.info("🖥️ Test 2: MCP Server Monitoring")
        self.test_results["total_tests"] += 1
        
        try:
            # Create monitored MCP server
            @sentinel
            class MonitoredMCPServer(A2AMCPServer):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self._sentinel_agent_id = "mcp_server"
            
            # Initialize server components
            server = A2AServer("localhost", 8000)
            client = A2AClient("http://localhost:8000")
            
            # Create agents
            math_agent = MathAgent()
            weather_agent = WeatherAgent()
            translation_agent = TranslationAgent()
            malicious_agent = MaliciousAgent()
            
            # Register agents
            server.register_agent("math_agent", math_agent)
            server.register_agent("weather_agent", weather_agent)
            server.register_agent("translation_agent", translation_agent)
            server.register_agent("malicious_agent", malicious_agent)
            
            # Create monitored MCP server
            mcp_server = MonitoredMCPServer(server, client)
            
            # Test server operations
            await mcp_server.start_server()
            agents = await mcp_server.list_agents()
            assert len(agents) == 4
            
            # Test agent execution
            result = await mcp_server.execute_agent("math_agent", "add", {"a": 5, "b": 10})
            assert result["result"] == 15.0
            
            await mcp_server.stop_server()
            
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({"test": "MCP Server Monitoring", "status": "PASSED"})
            logger.info("✅ Test 2 PASSED")
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({"test": "MCP Server Monitoring", "status": "FAILED", "error": str(e)})
            logger.error(f"❌ Test 2 FAILED: {e}")
    
    async def test_agent_communication(self):
        """Test 3: Agent-to-Agent Communication"""
        logger.info("🤝 Test 3: Agent-to-Agent Communication")
        self.test_results["total_tests"] += 1
        
        try:
            # Create monitored agents
            MonitoredMathAgent = self.create_monitored_agent(MathAgent, "math_agent")
            MonitoredWeatherAgent = self.create_monitored_agent(WeatherAgent, "weather_agent")
            MonitoredTranslationAgent = self.create_monitored_agent(TranslationAgent, "translation_agent")
            
            # Create orchestrator
            @sentinel
            class AgentOrchestrator:
                def __init__(self):
                    self.math_agent = MonitoredMathAgent()
                    self.weather_agent = MonitoredWeatherAgent()
                    self.translation_agent = MonitoredTranslationAgent()
                    self._sentinel_agent_id = "orchestrator"
                
                async def coordinate_workflow(self):
                    # Step 1: Get weather
                    weather_result = await self.weather_agent.execute_skill("get_weather", {"city": "London"})
                    
                    # Step 2: Do math with temperature
                    temp = weather_result["weather_data"]["temperature"]
                    math_result = await self.math_agent.execute_skill("add", {"a": temp, "b": 5})
                    
                    # Step 3: Translate result
                    translation_result = await self.translation_agent.execute_skill("translate", {
                        "text": f"Temperature adjusted: {math_result['result']}°C",
                        "source_lang": "en",
                        "target_lang": "es"
                    })
                    
                    return {
                        "weather": weather_result,
                        "math": math_result,
                        "translation": translation_result
                    }
            
            # Test orchestration
            orchestrator = AgentOrchestrator()
            result = await orchestrator.coordinate_workflow()
            
            assert "weather" in result
            assert "math" in result
            assert "translation" in result
            
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({"test": "Agent Communication", "status": "PASSED"})
            logger.info("✅ Test 3 PASSED")
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({"test": "Agent Communication", "status": "FAILED", "error": str(e)})
            logger.error(f"❌ Test 3 FAILED: {e}")
    
    async def test_security_monitoring(self):
        """Test 4: Security Monitoring"""
        logger.info("🔒 Test 4: Security Monitoring")
        self.test_results["total_tests"] += 1
        
        try:
            # Create monitored malicious agent
            MonitoredMaliciousAgent = self.create_monitored_agent(MaliciousAgent, "malicious_agent")
            malicious_agent = MonitoredMaliciousAgent()
            
            # Test various security scenarios
            security_tests = [
                ("inject_html", {"payload": "<script>alert('xss')</script>"}),
                ("extract_data", {"query": "SELECT * FROM users WHERE password = 'admin'"}),
                ("bypass_security", {"method": "admin:true"}),
                ("sql_injection", {"query": "'; DROP TABLE users; --"})
            ]
            
            initial_events = len(self.security_events)
            
            for skill, params in security_tests:
                try:
                    result = await malicious_agent.execute_skill(skill, params)
                    logger.info(f"🔍 Security test {skill}: {result['security_flag'] if 'security_flag' in result else 'No flag'}")
                except Exception as e:
                    logger.info(f"🔍 Security test {skill}: Exception caught - {e}")
            
            # Verify security events were generated
            new_events = len(self.security_events) - initial_events
            assert new_events > 0, f"Expected security events, got {new_events}"
            
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({"test": "Security Monitoring", "status": "PASSED", "events": new_events})
            logger.info(f"✅ Test 4 PASSED - {new_events} security events detected")
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({"test": "Security Monitoring", "status": "FAILED", "error": str(e)})
            logger.error(f"❌ Test 4 FAILED: {e}")
    
    async def test_threat_detection(self):
        """Test 5: Cross-Agent Threat Detection"""
        logger.info("🚨 Test 5: Cross-Agent Threat Detection")
        self.test_results["total_tests"] += 1
        
        try:
            # Create monitored agents
            MonitoredMaliciousAgent = self.create_monitored_agent(MaliciousAgent, "malicious_agent")
            MonitoredTranslationAgent = self.create_monitored_agent(TranslationAgent, "translation_agent")
            
            # Create threat detection system
            @sentinel
            class ThreatDetectionSystem:
                def __init__(self):
                    self.malicious_agent = MonitoredMaliciousAgent()
                    self.translation_agent = MonitoredTranslationAgent()
                    self._sentinel_agent_id = "threat_detector"
                
                async def simulate_threat_propagation(self):
                    # Simulate a threat that propagates between agents
                    initial_events = len(self.security_events)
                    
                    # Step 1: Malicious agent generates threat
                    malicious_result = await self.malicious_agent.execute_skill("inject_html", {
                        "payload": "<script>alert('propagated threat')</script>"
                    })
                    
                    # Step 2: Try to translate the malicious content
                    try:
                        translation_result = await self.translation_agent.execute_skill("translate", {
                            "text": malicious_result.get("content", ""),
                            "source_lang": "en",
                            "target_lang": "es"
                        })
                    except Exception as e:
                        logger.info(f"Translation blocked malicious content: {e}")
                    
                    return len(self.security_events) - initial_events
            
            # Test threat detection
            threat_detector = ThreatDetectionSystem()
            threat_events = await threat_detector.simulate_threat_propagation()
            
            assert threat_events > 0, f"Expected threat events, got {threat_events}"
            
            self.test_results["passed_tests"] += 1
            self.test_results["test_details"].append({"test": "Threat Detection", "status": "PASSED", "events": threat_events})
            logger.info(f"✅ Test 5 PASSED - {threat_events} threat events detected")
            
        except Exception as e:
            self.test_results["failed_tests"] += 1
            self.test_results["test_details"].append({"test": "Threat Detection", "status": "FAILED", "error": str(e)})
            logger.error(f"❌ Test 5 FAILED: {e}")
    
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Real Agent Sentinel SDK Integration Tests")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        await self.test_single_agent_monitoring()
        await self.test_mcp_server_monitoring()
        await self.test_agent_communication()
        await self.test_security_monitoring()
        await self.test_threat_detection()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate final report
        self.generate_final_report(duration)
    
    def generate_final_report(self, duration: float):
        """Generate comprehensive test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 REAL AGENT SENTINEL SDK INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        
        # Test summary
        total = self.test_results["total_tests"]
        passed = self.test_results["passed_tests"]
        failed = self.test_results["failed_tests"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        logger.info(f"🎯 Test Results: {passed}/{total} ({success_rate:.1f}% success rate)")
        logger.info(f"⏱️ Duration: {duration:.2f} seconds")
        logger.info(f"🚨 Security Events: {self.test_results['security_events']}")
        
        # Detailed results
        logger.info("\n📋 Test Details:")
        for test_detail in self.test_results["test_details"]:
            status_emoji = "✅" if test_detail["status"] == "PASSED" else "❌"
            logger.info(f"  {status_emoji} {test_detail['test']}: {test_detail['status']}")
            if "error" in test_detail:
                logger.info(f"    Error: {test_detail['error']}")
            if "events" in test_detail:
                logger.info(f"    Security Events: {test_detail['events']}")
        
        # SDK metrics
        all_events = get_all_events()
        sdk_metrics = self.sentinel.get_metrics()
        
        logger.info(f"\n📈 SDK Metrics:")
        logger.info(f"  • Total events from SDK: {len(all_events)}")
        logger.info(f"  • SDK reported events: {sdk_metrics.get('total_events', 0)}")
        logger.info(f"  • Average confidence: {sdk_metrics.get('average_confidence', 0):.2f}")
        logger.info(f"  • Agent ID: {self.sentinel.agent_id}")
        logger.info(f"  • SDK Status: {'Running' if self.sentinel.is_running else 'Stopped'}")
        
        # Event breakdown
        if all_events:
            threat_types = {}
            severities = {}
            
            for event in all_events:
                threat_type = event.threat_type.value
                severity = event.severity.value
                
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
                severities[severity] = severities.get(severity, 0) + 1
            
            logger.info(f"\n🚨 Security Events by Type:")
            for threat_type, count in threat_types.items():
                logger.info(f"  • {threat_type}: {count}")
            
            logger.info(f"\n⚠️ Security Events by Severity:")
            for severity, count in severities.items():
                logger.info(f"  • {severity}: {count}")
        
        # Final status
        if passed == total:
            logger.info(f"\n🎉 ALL TESTS PASSED! Real Agent Sentinel SDK is fully functional!")
            logger.info("✨ The SDK successfully detected threats, monitored agents, and provided security insights!")
        else:
            logger.info(f"\n⚠️ {failed} test(s) failed. See details above.")
        
        logger.info("=" * 60)

async def main():
    """Main test runner"""
    test_runner = RealSDKIntegrationTest()
    
    try:
        await test_runner.run_all_tests()
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean shutdown
        test_runner.sentinel.stop()

if __name__ == "__main__":
    asyncio.run(main()) 