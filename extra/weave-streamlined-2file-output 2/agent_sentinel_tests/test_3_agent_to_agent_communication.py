"""
Test 3: Agent-to-Agent Communication Monitoring
Demonstrates how to monitor direct agent-to-agent communication using the Agent Sentinel SDK
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
from mock_sentinel_sdk import sentinel, generate_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAgentToAgentCommunication:
    """Test class for agent-to-agent communication monitoring"""
    
    def __init__(self):
        self.test_name = "Agent-to-Agent Communication Monitoring"
        self.monitored_orchestrators = []
    
    async def test_simple_agent_orchestration(self):
        """Test simple agent orchestration with monitoring"""
        logger.info("🤝 Testing Simple Agent Orchestration...")
        
        @sentinel("simple_orchestrator")
        class SimpleAgentOrchestrator:
            def __init__(self):
                self.math_agent = MathAgent()
                self.weather_agent = WeatherAgent()
                self.translation_agent = TranslationAgent()
            
            async def initialize(self):
                await self.math_agent.initialize()
                await self.weather_agent.initialize()
                await self.translation_agent.initialize()
            
            async def coordinate_simple_task(self, task_type: str):
                """Coordinate agents for a simple task"""
                if task_type == "math_weather":
                    # Get weather temperature (simulated as 18)
                    weather_result = await self.weather_agent.execute_skill("get_weather", {"city": "London"})
                    
                    # Add 5 degrees to temperature
                    math_result = await self.math_agent.execute_skill("add", {"a": 18, "b": 5})
                    
                    return {
                        "weather": weather_result,
                        "adjusted_temp": math_result,
                        "task_type": task_type
                    }
                
                elif task_type == "translate_math":
                    # Calculate something
                    math_result = await self.math_agent.execute_skill("multiply", {"a": 7, "b": 8})
                    
                    # Translate the result
                    translation_result = await self.translation_agent.execute_skill("translate", {
                        "text": f"The result is {math_result}",
                        "from_lang": "English",
                        "to_lang": "Spanish"
                    })
                    
                    return {
                        "calculation": math_result,
                        "translation": translation_result,
                        "task_type": task_type
                    }
                
                return {"error": "Unknown task type"}
        
        orchestrator = SimpleAgentOrchestrator()
        await orchestrator.initialize()
        self.monitored_orchestrators.append(orchestrator)
        
        # Test different coordination tasks
        tasks = ["math_weather", "translate_math"]
        results = []
        
        for task in tasks:
            try:
                result = await orchestrator.coordinate_simple_task(task)
                results.append(f"Task {task}: {result}")
                logger.info(f"✅ Task {task} completed: {result}")
            except Exception as e:
                results.append(f"Task {task} failed: {e}")
                logger.error(f"❌ Task {task} failed: {e}")
        
        return results
    
    async def test_complex_agent_workflow(self):
        """Test complex multi-agent workflow with monitoring"""
        logger.info("🔄 Testing Complex Agent Workflow...")
        
        @sentinel("complex_workflow_orchestrator")
        class ComplexWorkflowOrchestrator:
            def __init__(self):
                self.math_agent = MathAgent()
                self.weather_agent = WeatherAgent()
                self.translation_agent = TranslationAgent()
            
            async def initialize(self):
                await self.math_agent.initialize()
                await self.weather_agent.initialize()
                await self.translation_agent.initialize()
            
            async def execute_travel_planning_workflow(self, destination: str):
                """Execute a complex travel planning workflow"""
                workflow_steps = []
                
                # Step 1: Get weather for destination
                weather_result = await self.weather_agent.execute_skill("get_weather", {"city": destination})
                workflow_steps.append(f"Weather check: {weather_result}")
                
                # Step 2: Calculate travel budget (simulated)
                budget_result = await self.math_agent.execute_skill("multiply", {"a": 100, "b": 7})  # $100/day for 7 days
                workflow_steps.append(f"Budget calculation: ${budget_result}")
                
                # Step 3: Translate weather info to local language
                translation_result = await self.translation_agent.execute_skill("translate", {
                    "text": f"Weather: {weather_result}",
                    "from_lang": "English",
                    "to_lang": "Spanish"
                })
                workflow_steps.append(f"Translation: {translation_result}")
                
                # Step 4: Calculate final cost with tax
                final_cost = await self.math_agent.execute_skill("multiply", {"a": budget_result, "b": 1.1})  # 10% tax
                workflow_steps.append(f"Final cost with tax: ${final_cost}")
                
                return {
                    "destination": destination,
                    "workflow_steps": workflow_steps,
                    "final_cost": final_cost,
                    "weather_info": weather_result,
                    "translated_info": translation_result
                }
        
        orchestrator = ComplexWorkflowOrchestrator()
        await orchestrator.initialize()
        self.monitored_orchestrators.append(orchestrator)
        
        # Test workflow for different destinations
        destinations = ["Paris", "Tokyo", "New York"]
        results = []
        
        for destination in destinations:
            try:
                result = await orchestrator.execute_travel_planning_workflow(destination)
                results.append(f"Travel plan for {destination}: {result}")
                logger.info(f"✅ Travel plan for {destination} completed")
            except Exception as e:
                results.append(f"Travel plan for {destination} failed: {e}")
                logger.error(f"❌ Travel plan for {destination} failed: {e}")
        
        return results
    
    async def test_agent_communication_patterns(self):
        """Test different agent communication patterns"""
        logger.info("📡 Testing Agent Communication Patterns...")
        
        @sentinel("communication_pattern_monitor")
        class CommunicationPatternMonitor:
            def __init__(self):
                self.math_agent = MathAgent()
                self.weather_agent = WeatherAgent()
                self.translation_agent = TranslationAgent()
            
            async def initialize(self):
                await self.math_agent.initialize()
                await self.weather_agent.initialize()
                await self.translation_agent.initialize()
            
            async def test_sequential_communication(self):
                """Test sequential agent communication"""
                # Agent A → Agent B → Agent C
                result1 = await self.math_agent.execute_skill("add", {"a": 10, "b": 20})
                result2 = await self.weather_agent.execute_skill("get_weather", {"city": "London"})
                result3 = await self.translation_agent.execute_skill("translate", {
                    "text": f"Result: {result1}, Weather: {result2}",
                    "from_lang": "English",
                    "to_lang": "French"
                })
                
                return {
                    "pattern": "sequential",
                    "step1": result1,
                    "step2": result2,
                    "step3": result3
                }
            
            async def test_parallel_communication(self):
                """Test parallel agent communication"""
                # Agent A, B, C all execute simultaneously
                tasks = [
                    self.math_agent.execute_skill("multiply", {"a": 5, "b": 6}),
                    self.weather_agent.execute_skill("get_weather", {"city": "Berlin"}),
                    self.translation_agent.execute_skill("translate", {
                        "text": "Hello parallel world",
                        "from_lang": "English",
                        "to_lang": "German"
                    })
                ]
                
                results = await asyncio.gather(*tasks)
                
                return {
                    "pattern": "parallel",
                    "math_result": results[0],
                    "weather_result": results[1],
                    "translation_result": results[2]
                }
            
            async def test_feedback_loop_communication(self):
                """Test feedback loop communication"""
                # Agent A → Agent B → Agent A → Agent C
                initial_value = 10
                
                # Math agent processes initial value
                step1 = await self.math_agent.execute_skill("add", {"a": initial_value, "b": 5})
                
                # Weather agent processes (simulated)
                step2 = await self.weather_agent.execute_skill("get_weather", {"city": "Madrid"})
                
                # Math agent processes again (feedback)
                step3 = await self.math_agent.execute_skill("multiply", {"a": step1, "b": 2})
                
                # Translation agent finalizes
                step4 = await self.translation_agent.execute_skill("translate", {
                    "text": f"Final result: {step3}",
                    "from_lang": "English",
                    "to_lang": "Spanish"
                })
                
                return {
                    "pattern": "feedback_loop",
                    "initial_value": initial_value,
                    "step1": step1,
                    "step2": step2,
                    "step3": step3,
                    "step4": step4
                }
        
        monitor = CommunicationPatternMonitor()
        await monitor.initialize()
        self.monitored_orchestrators.append(monitor)
        
        # Test different communication patterns
        patterns = ["sequential", "parallel", "feedback_loop"]
        results = []
        
        for pattern in patterns:
            try:
                if pattern == "sequential":
                    result = await monitor.test_sequential_communication()
                elif pattern == "parallel":
                    result = await monitor.test_parallel_communication()
                elif pattern == "feedback_loop":
                    result = await monitor.test_feedback_loop_communication()
                
                results.append(f"Pattern {pattern}: {result}")
                logger.info(f"✅ Communication pattern {pattern} completed")
            except Exception as e:
                results.append(f"Pattern {pattern} failed: {e}")
                logger.error(f"❌ Communication pattern {pattern} failed: {e}")
        
        return results
    
    async def run_all_tests(self):
        """Run all agent-to-agent communication tests"""
        logger.info("🚀 Starting Agent-to-Agent Communication Tests...")
        logger.info("=" * 60)
        
        test_results = {}
        
        try:
            # Run individual tests
            test_results["simple_orchestration"] = await self.test_simple_agent_orchestration()
            test_results["complex_workflow"] = await self.test_complex_agent_workflow()
            test_results["communication_patterns"] = await self.test_agent_communication_patterns()
            
            # Generate comprehensive report
            report = generate_report(self.monitored_orchestrators, self.test_name)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"../reports/test_3_agent_to_agent_communication_{timestamp}.json"
            
            os.makedirs("../reports", exist_ok=True)
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Display summary
            logger.info("\n" + "=" * 60)
            logger.info("📊 AGENT-TO-AGENT COMMUNICATION TEST SUMMARY")
            logger.info("=" * 60)
            logger.info(f"📁 Report saved to: {report_filename}")
            logger.info(f"🤝 Total orchestrators monitored: {len(self.monitored_orchestrators)}")
            logger.info(f"📈 Total interactions: {report['total_interactions']}")
            logger.info(f"🚨 Total security events: {report['total_security_events']}")
            
            for orchestrator in report["agents"]:
                logger.info(f"  • {orchestrator['agent_id']}: {orchestrator['interactions']} interactions, {orchestrator['security_events']} security events")
            
            logger.info("✅ Agent-to-Agent Communication Tests Completed Successfully!")
            
            return {
                "test_results": test_results,
                "monitoring_report": report,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Agent-to-Agent Communication Tests Failed: {e}")
            return {
                "test_results": test_results,
                "error": str(e),
                "success": False
            }

async def main():
    """Main function to run the agent-to-agent communication test"""
    test = TestAgentToAgentCommunication()
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