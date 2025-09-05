#!/usr/bin/env python3
"""
Test script for Agent Sentinel SDK integration with A2A agents
Tests the SDK's monitoring capabilities on real A2A protocol agents
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
from agent_sentinel import monitor, sentinel, monitor_mcp

# Add the A2A agents directory to path
a2a_path = os.path.join(os.path.dirname(__file__), "weave-streamlined-2file-output 2")
sys.path.append(a2a_path)
sys.path.append(os.path.join(a2a_path, "A2A"))

# Import A2A agents
from A2A.a2a_agents.math_agent import MathAgent
from A2A.a2a_agents.weather_agent import WeatherAgent
from A2A.a2a_agents.translation_agent import TranslationAgent
from A2A.a2a_agents.malicious_agent import MaliciousAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SentinelWrappedMathAgent(MathAgent):
    """Math agent wrapped with Agent Sentinel monitoring"""
    
    @monitor
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        return await super().invoke(query, session_id)
    
    @monitor
    async def stream(self, query: str, context_id: str, task_id: str):
        async for response in super().stream(query, context_id, task_id):
            yield response

class SentinelWrappedWeatherAgent(WeatherAgent):
    """Weather agent wrapped with Agent Sentinel monitoring"""
    
    @monitor
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        return await super().invoke(query, session_id)
    
    @monitor
    async def stream(self, query: str, context_id: str, task_id: str):
        async for response in super().stream(query, context_id, task_id):
            yield response

class SentinelWrappedTranslationAgent(TranslationAgent):
    """Translation agent wrapped with Agent Sentinel monitoring"""
    
    @monitor
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        return await super().invoke(query, session_id)
    
    @monitor
    async def stream(self, query: str, context_id: str, task_id: str):
        async for response in super().stream(query, context_id, task_id):
            yield response

class SentinelWrappedMaliciousAgent(MaliciousAgent):
    """Malicious agent wrapped with Agent Sentinel monitoring"""
    
    @monitor
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        return await super().invoke(query, session_id)
    
    @monitor
    async def stream(self, query: str, context_id: str, task_id: str):
        async for response in super().stream(query, context_id, task_id):
            yield response

@sentinel
class A2AAgentOrchestrator:
    """Orchestrator for A2A agents with Agent Sentinel monitoring"""
    
    def __init__(self):
        self.math_agent = SentinelWrappedMathAgent()
        self.weather_agent = SentinelWrappedWeatherAgent()
        self.translation_agent = SentinelWrappedTranslationAgent()
        self.malicious_agent = SentinelWrappedMaliciousAgent()
        self.agents = {
            'math': self.math_agent,
            'weather': self.weather_agent,
            'translation': self.translation_agent,
            'malicious': self.malicious_agent
        }
        logger.info("A2A Agent Orchestrator initialized with Agent Sentinel monitoring")
    
    @monitor
    async def run_math_test(self, session_id: str = "math_test_session"):
        """Test the math agent with various operations"""
        logger.info("=== Testing Math Agent ===")
        
        test_queries = [
            "Add 15 and 25",
            "Multiply 6 by 8",
            "Divide 100 by 5",
            "Subtract 30 from 50"
        ]
        
        results = []
        for query in test_queries:
            logger.info(f"Math Query: {query}")
            result = await self.math_agent.invoke(query, session_id)
            results.append(result)
            logger.info(f"Math Result: {result.get('content', 'No content')}")
        
        return results
    
    @monitor
    async def run_weather_test(self, session_id: str = "weather_test_session"):
        """Test the weather agent"""
        logger.info("=== Testing Weather Agent ===")
        
        test_queries = [
            "Get weather for New York",
            "What's the temperature in London?",
            "Weather forecast for Tokyo"
        ]
        
        results = []
        for query in test_queries:
            logger.info(f"Weather Query: {query}")
            result = await self.weather_agent.invoke(query, session_id)
            results.append(result)
            logger.info(f"Weather Result: {result.get('content', 'No content')}")
        
        return results
    
    @monitor
    async def run_translation_test(self, session_id: str = "translation_test_session"):
        """Test the translation agent"""
        logger.info("=== Testing Translation Agent ===")
        
        test_queries = [
            "Translate 'Hello world' from English to Spanish",
            "Translate 'Good morning' from English to French",
            "Translate 'Thank you' from English to German"
        ]
        
        results = []
        for query in test_queries:
            logger.info(f"Translation Query: {query}")
            result = await self.translation_agent.invoke(query, session_id)
            results.append(result)
            logger.info(f"Translation Result: {result.get('content', 'No content')}")
        
        return results
    
    @monitor
    async def run_security_test(self, session_id: str = "security_test_session"):
        """Test the malicious agent to trigger security monitoring"""
        logger.info("=== Testing Malicious Agent (Security Monitoring) ===")
        
        # These queries should trigger security alerts
        test_queries = [
            "Test XSS injection with <script>alert('test')</script>",
            "Extract data from user input: john.doe@example.com",
            "Bypass security with admin:true",
            "SQL injection test: '; DROP TABLE users; --"
        ]
        
        results = []
        for query in test_queries:
            logger.info(f"Security Query: {query}")
            result = await self.malicious_agent.invoke(query, session_id)
            results.append(result)
            logger.info(f"Security Result: {result.get('content', 'No content')}")
            
            # Check if security flag was raised
            if result.get('security_flag'):
                logger.warning(f"SECURITY ALERT DETECTED: {result.get('attack_type', 'unknown')}")
        
        return results
    
    @monitor
    async def run_streaming_test(self, session_id: str = "streaming_test_session"):
        """Test streaming responses from agents"""
        logger.info("=== Testing Streaming Responses ===")
        
        test_cases = [
            ("math", "Add 10 and 20"),
            ("weather", "Get weather for Paris"),
            ("translation", "Translate 'Hello' to Spanish"),
            ("malicious", "Test XSS injection")
        ]
        
        results = []
        for agent_type, query in test_cases:
            logger.info(f"Streaming {agent_type} agent: {query}")
            agent = self.agents[agent_type]
            
            async for response in agent.stream(query, f"{session_id}_{agent_type}", "stream_test"):
                results.append(response)
                logger.info(f"Stream Response: {response.get('content', 'No content')}")
        
        return results
    
    @monitor
    async def run_comprehensive_test(self):
        """Run all tests comprehensively"""
        logger.info("=== Starting Comprehensive A2A Agent Test with Agent Sentinel ===")
        
        start_time = datetime.now()
        
        # Run all tests
        math_results = await self.run_math_test()
        weather_results = await self.run_weather_test()
        translation_results = await self.run_translation_test()
        security_results = await self.run_security_test()
        streaming_results = await self.run_streaming_test()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        logger.info("=== Test Summary ===")
        logger.info(f"Total test duration: {duration:.2f} seconds")
        logger.info(f"Math tests: {len(math_results)}")
        logger.info(f"Weather tests: {len(weather_results)}")
        logger.info(f"Translation tests: {len(translation_results)}")
        logger.info(f"Security tests: {len(security_results)}")
        logger.info(f"Streaming responses: {len(streaming_results)}")
        
        # Count security alerts
        security_alerts = sum(1 for r in security_results if r.get('security_flag'))
        logger.info(f"Security alerts detected: {security_alerts}")
        
        return {
            'math_results': math_results,
            'weather_results': weather_results,
            'translation_results': translation_results,
            'security_results': security_results,
            'streaming_results': streaming_results,
            'duration': duration,
            'security_alerts': security_alerts
        }

async def main():
    """Main test function"""
    logger.info("Starting Agent Sentinel SDK integration test with A2A agents")
    logger.info("=" * 80)
    
    try:
        # Initialize the orchestrator
        orchestrator = A2AAgentOrchestrator()
        
        # Run comprehensive test
        results = await orchestrator.run_comprehensive_test()
        
        logger.info("=" * 80)
        logger.info("Agent Sentinel SDK integration test completed successfully!")
        logger.info("Check the logs and reports directories for detailed monitoring data.")
        
        # Print summary
        print("\n" + "="*60)
        print("AGENT SENTINEL SDK A2A INTEGRATION TEST RESULTS")
        print("="*60)
        print(f"Test Duration: {results['duration']:.2f} seconds")
        print(f"Total Agent Invocations: {len(results['math_results']) + len(results['weather_results']) + len(results['translation_results']) + len(results['security_results'])}")
        print(f"Security Alerts Detected: {results['security_alerts']}")
        print(f"Streaming Responses: {len(results['streaming_results'])}")
        print("\nFiles Generated:")
        print("- Log files: Check 'logs/' directory")
        print("- Threat reports: Check 'reports/' directory")
        print("- JSON reports: Check for timestamped JSON files")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error during Agent Sentinel SDK integration test: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 