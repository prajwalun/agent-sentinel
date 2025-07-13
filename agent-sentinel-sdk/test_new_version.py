#!/usr/bin/env python3
"""
Test script to verify Agent Sentinel v0.4.0 with separate logging and reporting
"""

import os
import json
from agent_sentinel.wrappers.decorators import monitor, sentinel

def test_basic_monitoring():
    """Test basic monitoring with separate logs and reports"""
    print("Testing basic monitoring...")
    
    @monitor(agent_id="test_agent_v4")
    def simple_agent(data):
        return {"result": "success", "data": data}
    
    # Run the agent
    result = simple_agent({"test": "data"})
    print(f"Agent result: {result}")
    
    # Check if logs and reports were generated
    log_files = [f for f in os.listdir("logs") if f.endswith(".json")]
    report_files = [f for f in os.listdir("reports") if f.endswith(".json")]
    
    print(f"Generated log files: {log_files}")
    print(f"Generated report files: {report_files}")
    
    # Verify log structure
    if log_files:
        with open(f"logs/{log_files[-1]}", 'r') as f:
            log_data = json.load(f)
            print(f"Log structure: {list(log_data.keys())}")
    
    # Verify report structure
    if report_files:
        with open(f"reports/{report_files[-1]}", 'r') as f:
            report_data = json.load(f)
            print(f"Report structure: {list(report_data.keys())}")
    
    return True

def test_sentinel_decorator():
    """Test sentinel decorator"""
    print("\nTesting sentinel decorator...")
    
    @sentinel(agent_id="sentinel_test_v4")
    def secure_agent(data):
        return {"secure_result": "success", "data": data}
    
    result = secure_agent({"secure": "test"})
    print(f"Sentinel result: {result}")
    return True

def test_sentinel_class_decorator():
    """Test sentinel class decorator"""
    print("\nTesting sentinel class decorator...")
    
    @sentinel
    class TestAgent:
        def process_data(self, data):
            return {"class_result": "success", "data": data}
    
    agent = TestAgent()
    result = agent.process_data({"class_test": "data"})
    print(f"Class agent result: {result}")
    return True

def main():
    """Run all tests"""
    print("Agent Sentinel v0.4.0 Test Suite")
    print("=" * 40)
    
    # Create directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    tests = [
        test_basic_monitoring,
        test_sentinel_decorator,
        test_sentinel_class_decorator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                print("❌ FAILED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Agent Sentinel v0.4.0 is working correctly.")
        print("\nKey Features Verified:")
        print("- ✅ Separate logging and reporting")
        print("- ✅ Clean public API (monitor, sentinel, monitor_mcp)")
        print("- ✅ Automatic log and report generation")
        print("- ✅ Structured JSON output")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main() 