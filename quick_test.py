#!/usr/bin/env python3
"""
Quick test to verify the enhancement API responds.
"""

import requests
import json
import time

def quick_test():
    """Quick test with a minimal report"""
    
    # Minimal security report
    report = {
        "report_content": "SECURITY ALERT: Agent made suspicious API call to external domain. Risk: HIGH. Action needed.",
        "analysis_type": "comprehensive",
        "agent_id": "quick-test"
    }
    
    print("🚀 Quick Enhancement Test")
    print("=" * 30)
    print("Testing with minimal report...")
    
    try:
        # Start request
        print("Sending request...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8001/analyze",
            json=report,
            timeout=30  # 30 second timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Response received in {duration:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhancement successful!")
            print(f"Agent ID: {result.get('agent_id', 'N/A')}")
            print(f"Report ID: {result.get('report_id', 'N/A')}")
            print(f"Risk Score: {result.get('summary', {}).get('risk_score', 'N/A')}")
            print(f"Threats: {result.get('summary', {}).get('threats_detected', 'N/A')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️  Timeout - analysis is taking longer than expected")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Quick test passed!")
    else:
        print("\n❌ Quick test failed") 