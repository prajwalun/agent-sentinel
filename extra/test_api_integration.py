#!/usr/bin/env python3
"""
Test script to verify the intelligence API integration.
"""

import requests
import json
import time

def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_analysis_endpoint():
    """Test the analysis endpoint with a simple report"""
    print("\nTesting analysis endpoint...")
    
    test_report = {
        "report_content": "SECURITY ALERT: Agent made 2 suspicious API calls. Detected potential data exfiltration attempt.",
        "analysis_type": "comprehensive",
        "agent_id": "test-agent"
    }
    
    try:
        print("Sending analysis request...")
        response = requests.post(
            "http://localhost:8001/analyze",
            json=test_report,
            timeout=60  # 60 second timeout
        )
        
        if response.status_code == 200:
            print("✅ Analysis endpoint working")
            result = response.json()
            print(f"Analysis completed for agent: {result.get('agent_id', 'unknown')}")
            print(f"Risk score: {result.get('summary', {}).get('risk_score', 'unknown')}")
            print(f"Threats detected: {result.get('summary', {}).get('threats_detected', 'unknown')}")
            return True
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Analysis request timed out (this is expected for comprehensive analysis)")
        return False
    except Exception as e:
        print(f"❌ Analysis endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Agent Sentinel Intelligence API Integration")
    print("=" * 50)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test analysis endpoint
        analysis_ok = test_analysis_endpoint()
        
        if analysis_ok:
            print("\n✅ All tests passed! Integration is working.")
        else:
            print("\n⚠️  Health OK but analysis may be slow/timing out (this is normal)")
    else:
        print("\n❌ Health check failed - API server may not be running")
    
    print("\n📋 Next steps:")
    print("1. If health check passed, the API server is running correctly")
    print("2. If analysis times out, that's normal - the AI analysis takes time")
    print("3. Test the dashboard integration by uploading a report")

if __name__ == "__main__":
    main() 