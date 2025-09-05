#!/usr/bin/env python3
"""
Test script to demonstrate the full API integration between frontend and backend.
This script simulates the workflow: file upload → backend analysis → enhanced report
"""

import requests
import json
import time

# Configuration
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"
API_KEY = "as_0f06cc25084a43a1a1b4418f"  # Demo key

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data['status']}")
            print(f"   Version: {health_data['version']}")
            print(f"   Workflow ready: {health_data['workflow_ready']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_frontend_health():
    """Test frontend health"""
    print("\n🔍 Testing frontend health...")
    try:
        response = requests.get(f"{FRONTEND_URL}/reports", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
            return True
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_api_integration():
    """Test the full API integration"""
    print("\n🔍 Testing API integration...")
    
    # Sample security report content
    report_content = """
    SECURITY REPORT - Agent: test_agent
    =====================================
    
    DETECTED THREATS:
    1. Command Injection Attack
       - Severity: HIGH
       - Confidence: 0.95
       - Description: Malicious command injection detected in user input
       - Impact: System compromise possible
    
    2. Data Exfiltration Attempt
       - Severity: HIGH  
       - Confidence: 0.88
       - Description: Unauthorized data access and extraction attempt
       - Impact: Sensitive data exposure
    
    3. Privilege Escalation
       - Severity: MEDIUM
       - Confidence: 0.75
       - Description: Attempt to gain elevated system privileges
       - Impact: Unauthorized access to restricted resources
    
    RISK ASSESSMENT:
    - Overall Risk Level: MEDIUM
    - Risk Score: 2.33/5.0
    - Immediate Action Required: Yes
    
    COMPLIANCE STATUS:
    - Data Protection: NON-COMPLIANT
    - Access Control: NON-COMPLIANT
    - Audit Logging: COMPLIANT
    - Incident Response: COMPLIANT
    
    RECOMMENDATIONS:
    1. Implement input validation and sanitization
    2. Deploy data loss prevention (DLP) controls
    3. Review and restrict agent permissions
    4. Enhance monitoring and alerting systems
    5. Conduct security awareness training
    """
    
    # Test API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "report_content": report_content,
        "analysis_type": "comprehensive",
        "agent_id": "test_agent"
    }
    
    try:
        print("   📤 Sending report for analysis...")
        response = requests.post(
            f"{BACKEND_URL}/analyze",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API integration successful!")
            print(f"   📊 Report ID: {result['report_id']}")
            print(f"   🤖 Agent ID: {result['agent_id']}")
            print(f"   ⚡ Analysis Time: {result['workflow_execution_time']:.2f}s")
            print(f"   🔍 Security Events: {len(result['security_events'])}")
            print(f"   📈 Risk Score: {result['summary']['risk_score']:.2f}")
            print(f"   🚨 Status: {result['summary']['status']}")
            
            # Display security events
            print("\n   🔐 Security Events:")
            for i, event in enumerate(result['security_events'][:3], 1):
                print(f"      {i}. {event['threat_type'].upper()} - {event['severity']} (confidence: {event['confidence']:.2f})")
            
            # Display recommendations
            print(f"\n   💡 Recommendations ({len(result['recommendations'])}):")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"      {i}. {rec[:60]}...")
            
            return True
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API integration failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Agent Sentinel Full Integration Test")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend_health()
    
    # Test frontend
    frontend_ok = test_frontend_health()
    
    # Test API integration
    if backend_ok:
        api_ok = test_api_integration()
    else:
        api_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    print(f"Backend Health:     {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Health:    {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"API Integration:    {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok and api_ok:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
        print("\n🌐 Access the dashboard at: http://localhost:3000/reports")
        print("📡 Backend API available at: http://localhost:8001")
    else:
        print("\n⚠️  Some tests failed. Please check the logs above.")
    
    return backend_ok and frontend_ok and api_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 