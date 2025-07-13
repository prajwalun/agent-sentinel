#!/usr/bin/env python3
"""
Test Agent Sentinel SDK on the A2A Threat Detection Agent from chat
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

# Import the A2A threat detection test
from test_a2a_threat_detection import run_dynamic_agent_interactions

@sentinel
class SecuredA2AThreatDetection:
    """A2A Threat Detection wrapped with Agent Sentinel security monitoring"""
    
    def __init__(self):
        print("🔒 A2A Threat Detection secured with Agent Sentinel")
        self.agent_id = "a2a_threat_detection"
    
    @monitor
    async def run_secured_dynamic_interactions(self):
        """Run the dynamic agent interactions with security monitoring"""
        print("🚀 Running secured dynamic A2A threat detection...")
        
        try:
            # Run the original function with our monitoring
            result = await run_dynamic_agent_interactions()
            
            print("✅ Secured A2A threat detection completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error in secured A2A threat detection: {e}")
            raise

async def test_chat_agent():
    """Test the chat agent with Agent Sentinel SDK"""
    print("🧪 Testing Chat Agent with Agent Sentinel SDK")
    print("=" * 60)
    
    # Create secured agent
    secured_agent = SecuredA2AThreatDetection()
    
    # Run the secured dynamic interactions
    result = await secured_agent.run_secured_dynamic_interactions()
    
    print("\n" + "=" * 60)
    print("📊 SECURED A2A THREAT DETECTION RESULTS")
    print("=" * 60)
    print(f"Total Interactions: {result.get('interactions', 0)}")
    print(f"Security Events: {result.get('security_events', 0)}")
    print(f"Security Alerts: {result.get('alerts', 0)}")
    print(f"Cross-Agent Threats: {result.get('cross_agent_threats', 0)}")
    print(f"Log File: {result.get('log_file', 'N/A')}")
    print(f"Report File: {result.get('report_file', 'N/A')}")
    
    # Check for generated logs and reports
    print("\n📁 Checking for generated logs and reports...")
    
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
        print(f"✅ Log files found: {len(log_files)}")
        for log_file in log_files[-3:]:  # Show last 3
            print(f"   - {log_file}")
    
    if os.path.exists("reports"):
        report_files = [f for f in os.listdir("reports") if f.endswith((".json", ".txt"))]
        print(f"✅ Report files found: {len(report_files)}")
        for report_file in report_files[-3:]:  # Show last 3
            print(f"   - {report_file}")
    
    print("\n🎉 Chat Agent Test Completed Successfully!")
    return result

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_chat_agent()) 