#!/usr/bin/env python3
"""
Test script to verify report enhancement works.
"""

import requests
import json
import time

def test_report_enhancement():
    """Test the report enhancement with a realistic security report"""
    
    # Sample security report (like what the SDK would generate)
    security_report = {
        "report_content": """AGENT SENTINEL SECURITY REPORT
        
Agent ID: test-agent-001
Session Start: 2025-01-13T10:30:00Z
Session End: 2025-01-13T10:45:00Z

SECURITY EVENTS DETECTED:
1. Suspicious API Call - External domain access: malicious-site.com
2. File System Violation - Attempted access outside permitted directory: /etc/passwd
3. Resource Anomaly - High CPU usage spike: 95% for 30 seconds

PERFORMANCE METRICS:
- Total Function Calls: 15
- Average Response Time: 250ms
- Memory Usage: 45MB
- Success Rate: 80%

RISK ASSESSMENT:
Risk Level: HIGH
Threats Detected: 3
Confidence: 0.85

RECOMMENDATIONS:
- Immediate investigation required
- Review agent permissions
- Monitor for additional suspicious activity
""",
        "analysis_type": "comprehensive",
        "agent_id": "test-agent-001"
    }
    
    print("🔍 Testing Report Enhancement")
    print("=" * 40)
    print(f"Original Report Length: {len(security_report['report_content'])} characters")
    print("Sending to intelligence API...")
    
    try:
        # Send to intelligence API
        response = requests.post(
            "http://localhost:8001/analyze",
            json=security_report,
            timeout=90  # 90 second timeout
        )
        
        if response.status_code == 200:
            enhanced_report = response.json()
            
            print("\n✅ Enhancement Successful!")
            print("=" * 40)
            
            # Display key enhancements
            print(f"Agent ID: {enhanced_report.get('agent_id', 'N/A')}")
            print(f"Report ID: {enhanced_report.get('report_id', 'N/A')}")
            print(f"Analysis Type: {enhanced_report.get('analysis_type', 'N/A')}")
            print(f"Workflow Execution Time: {enhanced_report.get('workflow_execution_time', 'N/A')}s")
            
            # Summary information
            summary = enhanced_report.get('summary', {})
            print(f"\nSUMMARY:")
            print(f"  Status: {summary.get('status', 'N/A')}")
            print(f"  Risk Score: {summary.get('risk_score', 'N/A')}")
            print(f"  Threats Detected: {summary.get('threats_detected', 'N/A')}")
            print(f"  Performance Score: {summary.get('performance_score', 'N/A')}")
            
            # Threat analysis
            threat_analysis = enhanced_report.get('threat_analysis', {})
            print(f"\nTHREAT ANALYSIS:")
            print(f"  Total Threats: {threat_analysis.get('total_threats', 'N/A')}")
            print(f"  Risk Score: {threat_analysis.get('risk_score', 'N/A')}")
            print(f"  Most Common Threat: {threat_analysis.get('most_common_threat', 'N/A')}")
            print(f"  Highest Severity: {threat_analysis.get('highest_severity', 'N/A')}")
            
            # Security events
            security_events = enhanced_report.get('security_events', [])
            print(f"\nSECURITY EVENTS: {len(security_events)} events")
            for i, event in enumerate(security_events[:3]):  # Show first 3
                print(f"  {i+1}. {event.get('threat_type', 'N/A')} - {event.get('severity', 'N/A')}")
            
            # Recommendations
            recommendations = enhanced_report.get('recommendations', [])
            print(f"\nRECOMMENDATIONS: {len(recommendations)} items")
            for i, rec in enumerate(recommendations[:3]):  # Show first 3
                print(f"  {i+1}. {rec}")
            
            # Intelligence insights
            intelligence_insights = enhanced_report.get('intelligence_insights', {})
            if intelligence_insights:
                print(f"\nINTELLIGENCE INSIGHTS:")
                for key, value in intelligence_insights.items():
                    if isinstance(value, str) and len(value) < 100:
                        print(f"  {key}: {value}")
            
            print("\n🎉 Report enhancement completed successfully!")
            print("The original report has been enhanced with AI analysis, threat intelligence, and actionable recommendations.")
            
            return True
            
        else:
            print(f"❌ Enhancement failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timed out - analysis may still be running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_report_enhancement()
    if success:
        print("\n✅ Integration test passed - report enhancement is working!")
    else:
        print("\n❌ Integration test failed - check server logs") 