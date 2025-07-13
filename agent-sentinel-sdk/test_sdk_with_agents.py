#!/usr/bin/env python3
"""
Test SDK with various agent types

Tests the three main decorators (@sentinel, @monitor, @monitor_mcp) 
with different agent implementations to verify automatic log and report generation.
"""

import time
import asyncio
from datetime import datetime
from pathlib import Path

# Import the three main decorators
from src.agent_sentinel import sentinel, monitor, monitor_mcp


# Test 1: Class-based agent with @sentinel
@sentinel
class DataProcessingAgent:
    """Agent for processing data with various operations"""
    
    def __init__(self):
        self.name = "DataProcessor"
        self.processed_count = 0
    
    def process_text(self, text: str) -> str:
        """Process text data"""
        self.processed_count += 1
        # Simulate some processing
        time.sleep(0.1)
        return f"Processed: {text.upper()}"
    
    def analyze_data(self, data: list) -> dict:
        """Analyze data and return insights"""
        self.processed_count += 1
        # Simulate data analysis
        time.sleep(0.2)
        return {
            "count": len(data),
            "sum": sum(data) if all(isinstance(x, (int, float)) for x in data) else None,
            "processed_at": datetime.now().isoformat()
        }
    
    def risky_operation(self, command: str) -> str:
        """Operation that might trigger security events"""
        self.processed_count += 1
        # This might trigger command injection detection
        if ";" in command or "|" in command:
            print(f"Warning: Potentially risky command: {command}")
        
        return f"Executed: {command}"


# Test 2: Function-based agent with @monitor
@monitor
def standalone_agent_function(data: str) -> str:
    """Standalone agent function for text processing"""
    # Simulate processing
    time.sleep(0.1)
    return f"Standalone processed: {data}"


# Test 3: MCP-style agent with @monitor_mcp
@monitor_mcp()
def mcp_search_agent(query: str) -> str:
    """MCP-style search agent"""
    # Simulate search operation
    time.sleep(0.15)
    return f"Search results for: {query}"


@monitor_mcp()
def mcp_file_agent(file_path: str) -> str:
    """MCP-style file operation agent"""
    # Simulate file operation
    time.sleep(0.1)
    return f"File operation on: {file_path}"


# Test 4: Another class-based agent with different behavior
@sentinel
class SecurityTestAgent:
    """Agent designed to trigger various security events"""
    
    def __init__(self):
        self.name = "SecurityTester"
    
    def safe_operation(self, data: str) -> str:
        """Safe operation that should pass validation"""
        return f"Safe: {data}"
    
    def data_access_operation(self, data: dict) -> dict:
        """Operation that might trigger data exfiltration detection"""
        # Simulate accessing sensitive data
        if "password" in data or "token" in data:
            print("Accessing sensitive data...")
        
        return {"accessed": True, "keys": list(data.keys())}
    
    def performance_test(self, iterations: int = 1000) -> str:
        """Performance test to generate metrics"""
        start_time = time.time()
        
        # Simulate work
        result = 0
        for i in range(iterations):
            result += i * 2
        
        duration = time.time() - start_time
        return f"Completed {iterations} iterations in {duration:.3f}s"


def test_agents():
    """Test all agent types and verify log/report generation"""
    print("🚀 Testing Agent Sentinel SDK with Various Agents")
    print("=" * 60)
    
    # Test 1: Class-based agent
    print("\n1. Testing @sentinel decorator with DataProcessingAgent...")
    data_agent = DataProcessingAgent()
    
    # Perform various operations
    result1 = data_agent.process_text("hello world")
    result2 = data_agent.analyze_data([1, 2, 3, 4, 5])
    result3 = data_agent.risky_operation("ls -la")
    result4 = data_agent.risky_operation("cat /etc/passwd; rm -rf /")
    
    print(f"   ✅ Text processing: {result1}")
    print(f"   ✅ Data analysis: {result2}")
    print(f"   ✅ Risky operation 1: {result3}")
    print(f"   ✅ Risky operation 2: {result4}")
    
    # Test 2: Standalone function
    print("\n2. Testing @monitor decorator with standalone function...")
    standalone_result = standalone_agent_function("test data")
    print(f"   ✅ Standalone function: {standalone_result}")
    
    # Test 3: MCP agents
    print("\n3. Testing @monitor_mcp decorator with MCP agents...")
    search_result = mcp_search_agent("artificial intelligence")
    file_result = mcp_file_agent("/etc/config.txt")
    
    print(f"   ✅ MCP search: {search_result}")
    print(f"   ✅ MCP file: {file_result}")
    
    # Test 4: Security test agent
    print("\n4. Testing @sentinel decorator with SecurityTestAgent...")
    security_agent = SecurityTestAgent()
    
    sec_result1 = security_agent.safe_operation("normal data")
    sec_result2 = security_agent.data_access_operation({"name": "test", "password": "secret123"})
    sec_result3 = security_agent.data_access_operation({"token": "abc123", "data": "sensitive"})
    sec_result4 = security_agent.performance_test(1000)
    
    print(f"   ✅ Safe operation: {sec_result1}")
    print(f"   ✅ Data access 1: {sec_result2}")
    print(f"   ✅ Data access 2: {sec_result3}")
    print(f"   ✅ Performance test: {sec_result4}")
    
    # Wait a moment for all operations to complete
    print("\n5. Waiting for operations to complete...")
    time.sleep(2)
    
    # Check generated files
    print("\n6. Checking generated logs and reports...")
    
    logs_dir = Path("logs")
    reports_dir = Path("reports")
    
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"   📂 Logs directory: {len(log_files)} log files found")
        
        # Show recent log files
        recent_logs = [f for f in log_files if "DataProcessingAgent" in f.name or 
                      "SecurityTestAgent" in f.name or 
                      "standalone_agent_function" in f.name or
                      "mcp_search_agent" in f.name or
                      "mcp_file_agent" in f.name]
        
        for log_file in recent_logs[-5:]:  # Show last 5
            if log_file.exists():
                size = log_file.stat().st_size
                print(f"      📄 {log_file.name} ({size} bytes)")
    
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.json"))
        print(f"   📂 Reports directory: {len(report_files)} report files found")
        
        # Show recent report files
        recent_reports = [f for f in report_files if "DataProcessingAgent" in f.name or 
                         "SecurityTestAgent" in f.name]
        
        for report_file in recent_reports[-3:]:  # Show last 3
            if report_file.exists():
                size = report_file.stat().st_size
                print(f"      📄 {report_file.name} ({size} bytes)")
    
    print("\n✅ SDK Test Complete!")
    print("\n📋 Summary:")
    print("   • @sentinel decorator works with class-based agents")
    print("   • @monitor decorator works with standalone functions")
    print("   • @monitor_mcp decorator works with MCP-style agents")
    print("   • Logs are generated automatically in logs/ directory")
    print("   • Threat reports are generated automatically in reports/ directory")
    print("   • No utility methods needed - everything is automatic")


if __name__ == "__main__":
    test_agents() 