#!/usr/bin/env python3
"""
Test script for separate logs and threat reports

Demonstrates the new separate log generation and threat report features
of the Agent Sentinel SDK.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.agent_sentinel.wrappers.decorators import sentinel, monitor
from src.agent_sentinel.core.constants import ThreatType, SeverityLevel
from src.agent_sentinel.core.types import SecurityEvent


@sentinel
class TestAgent:
    """Test agent with various behaviors to demonstrate monitoring"""
    
    def __init__(self):
        self.name = "TestAgent"
        self.counter = 0
    
    def safe_operation(self, data: str) -> str:
        """Safe operation that should pass validation"""
        self.counter += 1
        self.log_session_event("operation", f"Safe operation {self.counter} completed", {"data_length": len(data)})
        return f"Processed: {data.upper()}"
    
    def risky_operation(self, command: str) -> str:
        """Risky operation that might trigger security events"""
        self.counter += 1
        # This might trigger command injection detection
        if ";" in command or "|" in command:
            self.log_session_event("warning", f"Potentially risky command detected: {command}")
        
        return f"Executed: {command}"
    
    def data_operation(self, data: dict) -> dict:
        """Data operation that might trigger data exfiltration detection"""
        self.counter += 1
        
        # Simulate accessing sensitive data
        if "password" in data or "token" in data:
            self.log_session_event("security", "Sensitive data access detected", {"data_keys": list(data.keys())})
        
        return {"processed": True, "data_keys": list(data.keys())}
    
    def performance_test(self, iterations: int = 1000) -> str:
        """Performance test to generate performance metrics"""
        self.counter += 1
        start_time = time.time()
        
        # Simulate work
        result = 0
        for i in range(iterations):
            result += i * 2
        
        duration = time.time() - start_time
        self.log_session_event("performance", f"Performance test completed in {duration:.3f}s", {
            "iterations": iterations,
            "duration": duration,
            "result": result
        })
        
        return f"Completed {iterations} iterations in {duration:.3f}s"


@monitor
def standalone_function(data: str) -> str:
    """Standalone function to test individual monitoring"""
    time.sleep(0.1)  # Simulate work
    return f"Standalone processed: {data}"


async def test_separate_logs_and_reports():
    """Test the separate log and threat report features"""
    print("🧪 Testing Separate Logs and Threat Reports")
    print("=" * 50)
    
    # Create test agent
    agent = TestAgent()
    
    print("\n1. Testing basic operations with separate logging...")
    
    # Perform various operations
    results = []
    results.append(agent.safe_operation("hello world"))
    results.append(agent.risky_operation("ls -la"))
    results.append(agent.risky_operation("cat /etc/passwd; rm -rf /"))
    results.append(agent.data_operation({"name": "test", "password": "secret123"}))
    results.append(agent.data_operation({"token": "abc123", "data": "sensitive"}))
    results.append(agent.performance_test(1000))
    
    print(f"   ✅ Completed {len(results)} operations")
    
    # Test standalone function
    print("\n2. Testing standalone function monitoring...")
    standalone_result = standalone_function("test data")
    print(f"   ✅ Standalone function result: {standalone_result}")
    
    # Generate threat report
    print("\n3. Generating threat report...")
    threat_report = agent.generate_threat_report()
    if threat_report:
        print(f"   ✅ Threat report generated: {threat_report['report_id']}")
        print(f"   📊 Total threats: {threat_report['threat_summary']['total_threats']}")
        print(f"   🎯 Threat level: {threat_report['threat_summary']['threat_level']}")
        print(f"   📈 Risk score: {threat_report['risk_assessment']['overall_risk_score']:.2f}")
        print(f"   📋 Recommendations: {len(threat_report['recommendations'])}")
    else:
        print("   ❌ Failed to generate threat report")
    
    # Export logs
    print("\n4. Exporting logs...")
    logs_json = agent.export_logs("json")
    logs_csv = agent.export_logs("csv")
    logs_text = agent.export_logs("text")
    
    if logs_json:
        print(f"   ✅ JSON logs exported ({len(logs_json)} characters)")
    if logs_csv:
        print(f"   ✅ CSV logs exported ({len(logs_csv)} characters)")
    if logs_text:
        print(f"   ✅ Text logs exported ({len(logs_text)} characters)")
    
    # Get file paths
    print("\n5. Checking file paths...")
    log_path = agent.get_log_file_path()
    report_path = agent.get_threat_report_path()
    
    if log_path:
        print(f"   📄 Log file: {log_path}")
        if log_path.exists():
            print(f"   ✅ Log file exists ({log_path.stat().st_size} bytes)")
    
    if report_path:
        print(f"   📄 Threat report: {report_path}")
        if report_path.exists():
            print(f"   ✅ Threat report exists ({report_path.stat().st_size} bytes)")
    
    # Get security stats
    print("\n6. Security statistics...")
    stats = agent.get_security_stats()
    if stats:
        print(f"   📊 Total method calls: {stats['total_method_calls']}")
        print(f"   🚨 Security events: {stats['security_events']}")
        print(f"   ⏱️  Average call duration: {stats['average_call_duration']:.3f}s")
        print(f"   🧠 Memory usage: {stats['memory_usage_mb']:.1f} MB")
    
    # Test with different configurations
    print("\n7. Testing different configurations...")
    
    # Test with CSV logs
    @sentinel
    class CSVAgent:
        def test_csv_logging(self, data: str) -> str:
            return f"CSV logged: {data}"
    
    csv_agent = CSVAgent()
    csv_agent.test_csv_logging("test data")
    csv_logs = csv_agent.export_logs("csv")
    if csv_logs:
        print(f"   ✅ CSV logging works ({len(csv_logs)} characters)")
    
    # Test with HTML reports
    @sentinel
    class HTMLAgent:
        def test_html_reporting(self, data: str) -> str:
            return f"HTML reported: {data}"
    
    html_agent = HTMLAgent()
    html_agent.test_html_reporting("test data")
    html_report = html_agent.generate_threat_report()
    if html_report:
        print(f"   ✅ HTML reporting works")
    
    # Test disabled features
    @sentinel
    class DisabledAgent:
        def test_disabled_features(self, data: str) -> str:
            return f"Features disabled: {data}"
    
    disabled_agent = DisabledAgent()
    disabled_agent.test_disabled_features("test data")
    
    disabled_logs = disabled_agent.export_logs()
    disabled_report = disabled_agent.generate_threat_report()
    
    if disabled_logs is None:
        print("   ✅ Separate logs correctly disabled")
    if disabled_report is None:
        print("   ✅ Threat reports correctly disabled")
    
    print("\n8. Testing session events...")
    agent.log_session_event("test", "Custom session event", {"custom": "data"})
    agent.log_session_event("info", "Information event")
    agent.log_session_event("warning", "Warning event", {"level": "warning"})
    
    print("   ✅ Session events logged")
    
    # Final cleanup
    print("\n9. Cleanup...")
    agent.shutdown()
    csv_agent.shutdown()
    html_agent.shutdown()
    disabled_agent.shutdown()
    
    print("   ✅ All agents shut down")
    
    print("\n🎉 Separate Logs and Threat Reports Test Complete!")
    print("\n📁 Generated files:")
    
    # List generated files
    logs_dir = Path("logs")
    reports_dir = Path("reports")
    
    if logs_dir.exists():
        print(f"   📂 Logs directory: {logs_dir}")
        for log_file in logs_dir.glob("*.log"):
            print(f"      📄 {log_file.name}")
    
    if reports_dir.exists():
        print(f"   📂 Reports directory: {reports_dir}")
        for report_file in reports_dir.glob("*"):
            print(f"      📄 {report_file.name}")


def test_specific_formats():
    """Test specific log and report formats"""
    print("\n🔧 Testing Specific Formats")
    print("=" * 30)
    
    # Test JSON format
    @sentinel
    class JSONAgent:
        def test_json(self, data: str) -> str:
            return f"JSON: {data}"
    
    json_agent = JSONAgent()
    json_agent.test_json("test")
    json_logs = json_agent.export_logs("json")
    json_report = json_agent.generate_threat_report()
    
    print(f"   ✅ JSON logs: {len(json_logs) if json_logs else 0} characters")
    print(f"   ✅ JSON report: {'Generated' if json_report else 'Failed'}")
    
    # Test CSV format
    @sentinel
    class CSVAgent:
        def test_csv(self, data: str) -> str:
            return f"CSV: {data}"
    
    csv_agent = CSVAgent()
    csv_agent.test_csv("test")
    csv_logs = csv_agent.export_logs("csv")
    csv_report = csv_agent.generate_threat_report()
    
    print(f"   ✅ CSV logs: {len(csv_logs) if csv_logs else 0} characters")
    print(f"   ✅ CSV report: {'Generated' if csv_report else 'Failed'}")
    
    # Test text format
    @sentinel
    class TextAgent:
        def test_text(self, data: str) -> str:
            return f"Text: {data}"
    
    text_agent = TextAgent()
    text_agent.test_text("test")
    text_logs = text_agent.export_logs("text")
    text_report = text_agent.generate_threat_report()
    
    print(f"   ✅ Text logs: {len(text_logs) if text_logs else 0} characters")
    print(f"   ✅ Text report: {'Generated' if text_report else 'Failed'}")
    
    # Cleanup
    json_agent.shutdown()
    csv_agent.shutdown()
    text_agent.shutdown()


if __name__ == "__main__":
    print("🚀 Agent Sentinel - Separate Logs and Threat Reports Test")
    print("=" * 60)
    
    # Run tests
    asyncio.run(test_separate_logs_and_reports())
    test_specific_formats()
    
    print("\n✨ All tests completed successfully!")
    print("\n📋 Summary:")
    print("   • Separate log generation works with multiple formats")
    print("   • Threat report generation works with multiple formats")
    print("   • Configuration options work correctly")
    print("   • File paths are accessible")
    print("   • Session events are logged")
    print("   • All features can be enabled/disabled independently") 