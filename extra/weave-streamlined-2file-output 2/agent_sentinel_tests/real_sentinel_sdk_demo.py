"""
Real Agent Sentinel SDK Demo
Demonstrates using the actual Agent Sentinel SDK instead of the mock version
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'agent-sentinel-sdk', 'src'))

from agent_sentinel import AgentSentinel, sentinel, monitor, get_all_events
from agent_sentinel.core.types import SecurityEvent
from agent_sentinel.core.constants import ThreatType, SeverityLevel
import time
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealSentinelDemo:
    """Demo using the actual Agent Sentinel SDK"""
    
    def __init__(self):
        # Initialize the real Agent Sentinel SDK
        self.sentinel = AgentSentinel(
            agent_id="demo_agent",
            auto_start=True,
            enable_threat_intelligence=False  # Disable for demo
        )
        
        # Add custom event handler
        self.sentinel.add_event_handler(self._handle_security_event)
        
        self.security_events = []
        self.interactions = []
    
    def _handle_security_event(self, event: SecurityEvent):
        """Handle security events from the SDK"""
        logger.warning(f"🚨 [SENTINEL THREAT] {event.threat_type.value} detected: {event.message}")
        self.security_events.append({
            "timestamp": event.timestamp.isoformat(),
            "threat_type": event.threat_type.value,
            "severity": event.severity.value,
            "message": event.message,
            "confidence": event.confidence,
            "agent_id": event.agent_id,
            "context": event.context
        })
    
    def create_monitored_agent(self, agent_class, agent_id: str):
        """Create a monitored version of an agent using the real SDK"""
        
        # Use the real sentinel decorator
        @sentinel
        class MonitoredAgent(agent_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._sentinel_agent_id = agent_id
        
        return MonitoredAgent
    
    async def test_basic_monitoring(self):
        """Test basic monitoring with the real SDK"""
        logger.info("🚀 Testing Real Agent Sentinel SDK...")
        
        # Import the A2A agents
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'A2A'))
        from a2a_agents.math_agent import MathAgent
        from a2a_agents.weather_agent import WeatherAgent
        from a2a_agents.translation_agent import TranslationAgent
        from a2a_agents.malicious_agent import MaliciousAgent
        
        # Create monitored versions
        MonitoredMathAgent = self.create_monitored_agent(MathAgent, "math_agent_real")
        MonitoredWeatherAgent = self.create_monitored_agent(WeatherAgent, "weather_agent_real")
        MonitoredTranslationAgent = self.create_monitored_agent(TranslationAgent, "translation_agent_real")
        MonitoredMaliciousAgent = self.create_monitored_agent(MaliciousAgent, "malicious_agent_real")
        
        # Test each agent
        logger.info("🧮 Testing Math Agent...")
        math_agent = MonitoredMathAgent()
        try:
            result = await math_agent.execute_skill("add", {"a": 10, "b": 20})
            logger.info(f"✅ Math result: {result}")
        except Exception as e:
            logger.error(f"❌ Math agent error: {e}")
        
        logger.info("🌤️ Testing Weather Agent...")
        weather_agent = MonitoredWeatherAgent()
        try:
            result = await weather_agent.execute_skill("get_weather", {"city": "London"})
            logger.info(f"✅ Weather result: {result}")
        except Exception as e:
            logger.error(f"❌ Weather agent error: {e}")
        
        logger.info("🌍 Testing Translation Agent...")
        translation_agent = MonitoredTranslationAgent()
        try:
            result = await translation_agent.execute_skill("translate", {"text": "Hello", "source_lang": "en", "target_lang": "es"})
            logger.info(f"✅ Translation result: {result}")
        except Exception as e:
            logger.error(f"❌ Translation agent error: {e}")
        
        logger.info("🔒 Testing Malicious Agent (for security detection)...")
        malicious_agent = MonitoredMaliciousAgent()
        try:
            # This should trigger security events
            result = await malicious_agent.execute_skill("inject_html", {"payload": "<script>alert('xss')</script>"})
            logger.info(f"🔍 Malicious result: {result}")
        except Exception as e:
            logger.error(f"❌ Malicious agent error: {e}")
        
        # Get all events from the SDK
        all_events = get_all_events()
        logger.info(f"📊 Total security events detected: {len(all_events)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate a summary of the demo"""
        logger.info("\n" + "="*60)
        logger.info("📊 REAL AGENT SENTINEL SDK DEMO SUMMARY")
        logger.info("="*60)
        
        # Get events from the SDK
        all_events = get_all_events()
        
        logger.info(f"🔍 Total security events: {len(all_events)}")
        logger.info(f"🤖 Monitoring agent: {self.sentinel.agent_id}")
        logger.info(f"⏱️ SDK status: {'Running' if self.sentinel.is_running else 'Stopped'}")
        
        # Show event breakdown
        if all_events:
            threat_types = {}
            severities = {}
            
            for event in all_events:
                threat_type = event.threat_type.value
                severity = event.severity.value
                
                threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
                severities[severity] = severities.get(severity, 0) + 1
            
            logger.info("\n🚨 Security Events by Type:")
            for threat_type, count in threat_types.items():
                logger.info(f"  • {threat_type}: {count}")
            
            logger.info("\n⚠️ Security Events by Severity:")
            for severity, count in severities.items():
                logger.info(f"  • {severity}: {count}")
        
        # Show SDK metrics
        metrics = self.sentinel.get_metrics()
        logger.info(f"\n📈 SDK Metrics:")
        logger.info(f"  • Total events: {metrics.get('total_events', 0)}")
        logger.info(f"  • Average confidence: {metrics.get('average_confidence', 0):.2f}")
        
        logger.info("\n🎉 Real Agent Sentinel SDK Demo completed!")
        logger.info("✨ This demonstrates actual threat detection capabilities!")

async def main():
    """Main demo function"""
    demo = RealSentinelDemo()
    
    try:
        await demo.test_basic_monitoring()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean shutdown
        demo.sentinel.stop()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 