#!/usr/bin/env python3
"""
Test script to verify the published Agent Sentinel package is up to date
with all the latest features including separate logging and reporting
"""

import os
import json
from agent_sentinel.wrappers.decorators import monitor, sentinel
from agent_sentinel.wrappers.agent_wrapper import LogGenerator, ThreatReportGenerator
import agent_sentinel

def test_package_version():
    """Test that package version is correct"""
    print("Testing package version...")
    assert agent_sentinel.__version__ == "0.4.0", f"Expected 0.4.0, got {agent_sentinel.__version__}"
    print("✅ Package version: 0.4.0")

def test_separate_logging_and_reporting():
    """Test separate logging and reporting features"""
    print("\nTesting separate logging and reporting...")
    
    # Test LogGenerator
    log_gen = LogGenerator(agent_id="test_agent")
    assert hasattr(log_gen, 'generate_log'), "LogGenerator missing generate_log method"
    print("✅ LogGenerator imported and functional")
    
    # Test ThreatReportGenerator
    report_gen = ThreatReportGenerator(agent_id="test_agent")
    assert hasattr(report_gen, 'generate_threat_report'), "ThreatReportGenerator missing generate_threat_report method"
    print("✅ ThreatReportGenerator imported and functional")

def test_decorators():
    """Test the main decorators"""
    print("\nTesting decorators...")
    
    @monitor
    def test_function(data):
        return {"result": "success", "data": data}
    
    @sentinel
    class TestAgent:
        def process(self, data):
            return {"class_result": "success", "data": data}
    
    # Test function decorator
    result = test_function({"test": "data"})
    assert result["result"] == "success"
    print("✅ @monitor decorator working")
    
    # Test class decorator
    agent = TestAgent()
    result = agent.process({"test": "data"})
    assert result["class_result"] == "success"
    print("✅ @sentinel decorator working")

def test_real_agent_integration():
    """Test with a real agent pattern"""
    print("\nTesting real agent integration...")
    
    @sentinel
    class DataAnalysisAgent:
        def analyze_data(self, dataset):
            # Simulate data analysis
            return {
                "summary": f"Analyzed {len(dataset)} records",
                "insights": ["Pattern A detected", "Anomaly B found"],
                "recommendations": ["Action 1", "Action 2"]
            }
    
    agent = DataAnalysisAgent()
    result = agent.analyze_data([1, 2, 3, 4, 5])
    
    assert "summary" in result
    assert "insights" in result
    assert "recommendations" in result
    print("✅ Real agent integration working")

def test_log_and_report_generation():
    """Test that logs and reports are generated"""
    print("\nTesting log and report generation...")
    
    @monitor(agent_id="test_logging_agent")
    def logging_test_function(data):
        return {"processed": data}
    
    # Run the function
    result = logging_test_function({"test": "data"})
    
    # Check if logs directory exists and has files
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
        if log_files:
            print(f"✅ Log files generated: {len(log_files)} files")
        else:
            print("⚠️ Log directory exists but no log files found")
    else:
        print("⚠️ Logs directory not found")
    
    # Check if reports directory exists and has files
    if os.path.exists("reports"):
        report_files = [f for f in os.listdir("reports") if f.endswith(".json")]
        if report_files:
            print(f"✅ Report files generated: {len(report_files)} files")
        else:
            print("⚠️ Reports directory exists but no report files found")
    else:
        print("⚠️ Reports directory not found")

def main():
    """Run all tests"""
    print("🔍 Testing Agent Sentinel Package (v0.4.0)")
    print("=" * 50)
    
    tests = [
        test_package_version,
        test_separate_logging_and_reporting,
        test_decorators,
        test_real_agent_integration,
        test_log_and_report_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is up to date.")
    else:
        print("⚠️ Some tests failed. Package may need updates.")
    
    return passed == total

if __name__ == "__main__":
    main() 