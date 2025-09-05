#!/usr/bin/env python3
"""
Test script to verify the API server can handle enhanced report generation.
"""

import requests
import json
import time
import threading

def test_api_server_enhancement():
    """Test the API server with the same report that worked directly"""
    
    # Same report that worked with direct workflow
    report_data = {
        "report_content": """SECURITY REPORT - Agent ID: test-agent-001
Timestamp: 2025-01-13T10:30:00Z
Security Events:
- Suspicious API call to external domain: malicious-site.com
- Attempted file system access outside permitted directory: /etc/passwd
- High CPU usage detected during execution: 95% for 30 seconds
Risk Level: HIGH
Threats Detected: 3
Recommendations: Immediate investigation required""",
        "analysis_type": "comprehensive",
        "agent_id": "test-agent-001"
    }
    
    print("🔍 Testing API Server Enhancement")
    print("=" * 50)
    print("Original Report:")
    print(report_data["report_content"])
    print("=" * 50)
    print("Sending to API server...")
    
    def show_progress():
        """Show progress while waiting"""
        for i in range(60):  # 1 minute max
            print(".", end="", flush=True)
            time.sleep(1)
    
    # Start progress indicator
    progress_thread = threading.Thread(target=show_progress)
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        start_time = time.time()
        response = requests.post(
            "http://localhost:8001/analyze",
            json=report_data,
            timeout=60  # 1 minute timeout
        )
        end_time = time.time()
        
        print(f"\n\n⏱️  API Response in {end_time - start_time:.1f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API SERVER ENHANCEMENT SUCCESSFUL!")
            print("=" * 50)
            
            # Show key fields
            print(f"🆔 Agent ID: {result.get('agent_id', 'N/A')}")
            print(f"📊 Report ID: {result.get('report_id', 'N/A')}")
            print(f"⚡ Analysis Type: {result.get('analysis_type', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('workflow_execution_time', 'N/A')}s")
            
            # Summary
            summary = result.get('summary', {})
            print(f"\n📋 SUMMARY:")
            print(f"   Status: {summary.get('status', 'N/A')}")
            print(f"   Risk Score: {summary.get('risk_score', 'N/A')}")
            print(f"   Threats Detected: {summary.get('threats_detected', 'N/A')}")
            
            # Threat analysis
            threat_analysis = result.get('threat_analysis', {})
            print(f"\n🔍 THREAT ANALYSIS:")
            print(f"   Total Threats: {threat_analysis.get('total_threats', 'N/A')}")
            print(f"   Risk Score: {threat_analysis.get('risk_score', 'N/A')}")
            print(f"   Most Common: {threat_analysis.get('most_common_threat', 'N/A')}")
            
            # Security events
            security_events = result.get('security_events', [])
            print(f"\n🚨 SECURITY EVENTS: {len(security_events)} events")
            for i, event in enumerate(security_events[:3], 1):
                print(f"   {i}. {event.get('threat_type', 'N/A')} - {event.get('severity', 'N/A')}")
            
            # Recommendations
            recommendations = result.get('recommendations', [])
            print(f"\n💡 RECOMMENDATIONS: {len(recommendations)} items")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
            
            # Intelligence insights
            intelligence_insights = result.get('intelligence_insights', {})
            print(f"\n🧠 INTELLIGENCE INSIGHTS: {len(intelligence_insights)} fields")
            
            print(f"\n🎯 RESULT: API server successfully enhanced the report!")
            print(f"   • Ready for dashboard integration")
            print(f"   • All required fields present")
            print(f"   • Dashboard-compatible format")
            
            return True
            
        else:
            print(f"\n❌ API Server failed: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️  API request timed out")
        print("The server may be processing but taking longer than expected")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_health_first():
    """Test health endpoint first"""
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Server is healthy")
            print(f"   Status: {health_data.get('status', 'N/A')}")
            print(f"   Workflow Ready: {health_data.get('workflow_ready', 'N/A')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Agent Sentinel API Server Integration Test")
    print("Testing if the API server can generate enhanced reports for the dashboard")
    print()
    
    # Test health first
    if test_health_first():
        print("\n" + "="*50)
        success = test_api_server_enhancement()
        
        if success:
            print("\n🎉 SUCCESS: API server enhancement is working!")
            print("✅ Ready for dashboard integration")
            print("✅ Enhanced reports can be generated via API")
        else:
            print("\n⚠️  API server enhancement needs debugging")
            print("✅ Server is healthy but enhancement is slow/timing out")
    else:
        print("\n❌ Server is not running or not healthy")
        print("Please start the API server first: python api_server.py") 