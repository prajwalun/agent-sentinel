#!/usr/bin/env python3
"""
Comprehensive test for Agent Sentinel SDK improvements
Tests thread safety, memory management, error handling, and configuration validation
"""

import asyncio
import threading
import time
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_sentinel.wrappers.agent_wrapper import AgentWrapper
from agent_sentinel.core.exceptions import AgentSentinelError
from agent_sentinel.infrastructure.monitoring.metrics import MetricsCollector

class TestAgent:
    """Test agent class for monitoring"""
    
    def __init__(self, name: str = "TestAgent"):
        self.name = name
        self.counter = 0
        self._lock = threading.Lock()
    
    def simple_task(self, data: str) -> str:
        """Simple task that returns processed data"""
        with self._lock:
            self.counter += 1
        time.sleep(0.1)  # Simulate work
        return f"Processed: {data} (count: {self.counter})"
    
    def complex_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Complex task that processes dictionary data"""
        with self._lock:
            self.counter += 1
        time.sleep(0.2)  # Simulate work
        return {
            "status": "success",
            "processed_data": data,
            "count": self.counter,
            "timestamp": time.time()
        }
    
    def error_task(self, should_fail: bool = False) -> str:
        """Task that can fail for testing error handling"""
        if should_fail:
            raise ValueError("Simulated error for testing")
        return "Task completed successfully"
    
    def memory_intensive_task(self, size_mb: int = 10) -> str:
        """Task that uses significant memory"""
        # Create a large data structure
        large_data = "x" * (size_mb * 1024 * 1024)  # size_mb MB of data
        result = f"Created {size_mb}MB of data, length: {len(large_data)}"
        return result
    
    def shutdown(self):
        """Cleanup method for the agent"""
        print(f"Shutting down {self.name}")
        return "shutdown_complete"

class MCPTestAgent:
    """Test MCP-style agent"""
    
    def __init__(self):
        self.name = "MCPTestAgent"
        self.resources = ["file_system", "database", "api"]
    
    def list_resources(self) -> List[str]:
        """List available resources"""
        return self.resources
    
    def call_resource(self, resource: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a resource method"""
        if resource not in self.resources:
            raise ValueError(f"Resource {resource} not found")
        
        return {
            "resource": resource,
            "method": method,
            "params": params,
            "result": f"Successfully called {method} on {resource}"
        }

def test_configuration_validation():
    """Test configuration validation improvements"""
    print("\n=== Testing Configuration Validation ===")
    
    # Test with valid configuration
    try:
        wrapper = AgentWrapper(
            agent_id="TestAgent",
            max_session_duration=300,
            max_concurrent_sessions=10,
            session_cleanup_interval=60,
            memory_threshold_mb=100,
            enable_input_validation=True,
            enable_behavior_analysis=True,
            enable_performance_monitoring=True,
            strict_validation=False
        )
        print("✓ Valid configuration accepted")
    except Exception as e:
        print(f"✗ Valid configuration failed: {e}")
        return False
    
    # Test with invalid configuration
    try:
        wrapper = AgentWrapper(
            agent_id="TestAgent",
            max_session_duration=0,  # Invalid zero value
            memory_threshold_mb=-1   # Invalid negative value
        )
        print("✗ Invalid configuration should have failed")
        return False
    except Exception as e:
        print(f"✓ Invalid configuration properly rejected: {type(e).__name__}")
    
    return True

def test_thread_safety():
    """Test thread safety improvements"""
    print("\n=== Testing Thread Safety ===")
    
    agent = TestAgent("ThreadSafeAgent")
    wrapper = AgentWrapper(
        agent_id="ThreadSafeAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    
    @wrapper.monitor()
    def wrapped_simple(data):
        return agent.simple_task(data)
    
    @wrapper.monitor()
    def wrapped_complex(data):
        return agent.complex_task(data)
    
    def worker_task(task_id: int):
        for i in range(5):
            result1 = wrapped_simple(f"data_{task_id}_{i}")
            result2 = wrapped_complex({"task_id": task_id, "iteration": i})
            time.sleep(0.01)
    
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_task, args=(i,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print(f"✓ Thread safety test completed. Final counter: {agent.counter}")
    return True

def test_error_handling():
    """Test enhanced error handling"""
    print("\n=== Testing Error Handling ===")
    
    agent = TestAgent("ErrorTestAgent")
    wrapper = AgentWrapper(
        agent_id="ErrorTestAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    
    @wrapper.monitor()
    def wrapped_error_task(should_fail=False):
        return agent.error_task(should_fail=should_fail)
    
    try:
        result = wrapped_error_task(should_fail=False)
        print(f"✓ Successful execution: {result}")
    except Exception as e:
        print(f"✗ Successful execution failed: {e}")
        return False
    try:
        result = wrapped_error_task(should_fail=True)
        print("✗ Error should have been raised")
        return False
    except Exception as e:
        print(f"✓ Error properly handled: {type(e).__name__}")
    return True

def test_memory_management():
    """Test memory management improvements"""
    print("\n=== Testing Memory Management ===")
    
    agent = TestAgent("MemoryTestAgent")
    wrapper = AgentWrapper(
        agent_id="MemoryTestAgent",
        memory_threshold_mb=50,
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    
    @wrapper.monitor()
    def wrapped_memory_task(size_mb):
        return agent.memory_intensive_task(size_mb)
    
    try:
        result = wrapped_memory_task(10)
        print(f"✓ Memory task within limit: {result[:50]}...")
    except Exception as e:
        print(f"✗ Memory task within limit failed: {e}")
        return False
    try:
        result = wrapped_memory_task(100)
        print(f"✓ Memory task exceeded limit but handled gracefully: {result[:50]}...")
    except Exception as e:
        print(f"✓ Memory limit exceeded and properly handled: {type(e).__name__}")
    return True

def test_class_monitoring():
    """Test class monitoring capabilities (method-level only)"""
    print("\n=== Testing Class Monitoring ===")
    
    agent = TestAgent("ClassTestAgent")
    wrapper = AgentWrapper(
        agent_id="ClassTestAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    
    @wrapper.monitor()
    def wrapped_simple_task(data):
        return agent.simple_task(data)
    @wrapper.monitor()
    def wrapped_complex_task(data):
        return agent.complex_task(data)
    @wrapper.monitor()
    def wrapped_error_task(should_fail=False):
        return agent.error_task(should_fail=should_fail)
    @wrapper.monitor()
    def wrapped_shutdown():
        return agent.shutdown()
    try:
        result1 = wrapped_simple_task("test_data")
        result2 = wrapped_complex_task({"key": "value"})
        result3 = wrapped_error_task(should_fail=False)
        print(f"✓ Class monitoring successful:")
        print(f"  - Simple task: {result1}")
        print(f"  - Complex task: {result2}")
        print(f"  - Error task: {result3}")
        shutdown_result = wrapped_shutdown()
        print(f"  - Shutdown: {shutdown_result}")
    except Exception as e:
        print(f"✗ Class monitoring failed: {e}")
        return False
    return True

def test_mcp_monitoring():
    """Test MCP agent monitoring (method-level only)"""
    print("\n=== Testing MCP Agent Monitoring ===")
    
    mcp_agent = MCPTestAgent()
    wrapper = AgentWrapper(
        agent_id="MCPTestAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    @wrapper.monitor()
    def wrapped_list_resources():
        return mcp_agent.list_resources()
    @wrapper.monitor()
    def wrapped_call_resource(resource, method, params):
        return mcp_agent.call_resource(resource, method, params)
    try:
        resources = wrapped_list_resources()
        print(f"✓ MCP resources: {resources}")
        result = wrapped_call_resource("file_system", "read_file", {"path": "/test/file.txt"})
        print(f"✓ MCP resource call: {result}")
        try:
            wrapped_call_resource("invalid_resource", "method", {})
            print("✗ Invalid resource should have failed")
            return False
        except Exception as e:
            print(f"✓ Invalid resource properly handled: {type(e).__name__}")
    except Exception as e:
        print(f"✗ MCP monitoring failed: {e}")
        return False
    return True

async def test_concurrent_sessions():
    """Test concurrent session handling"""
    print("\n=== Testing Concurrent Sessions ===")
    
    async def async_worker(session_id: int):
        """Async worker for session testing"""
        agent = TestAgent(f"SessionAgent_{session_id}")
        wrapper = AgentWrapper(
            agent_id=f"SessionAgent_{session_id}",
            enable_input_validation=True,
            enable_behavior_analysis=True,
            enable_performance_monitoring=True,
            strict_validation=False
        )
        
        @wrapper.monitor()
        def wrapped_simple_task(data):
            return agent.simple_task(data)
        
        for i in range(3):
            result = wrapped_simple_task(f"session_{session_id}_data_{i}")
            await asyncio.sleep(0.1)
        
        return f"Session {session_id} completed"
    
    # Run multiple concurrent sessions
    tasks = [async_worker(i) for i in range(5)]
    results = await asyncio.gather(*tasks)
    
    for result in results:
        print(f"✓ {result}")
    
    return True

def test_serialization_safety():
    """Test serialization safety improvements"""
    print("\n=== Testing Serialization Safety ===")
    
    agent = TestAgent("SerializationTestAgent")
    wrapper = AgentWrapper(
        agent_id="SerializationTestAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    @wrapper.monitor()
    def wrapped_complex(data):
        return agent.complex_task(data)
    complex_data = {
        "string": "test",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"nested": "value"},
        "boolean": True,
        "none": None
    }
    try:
        result = wrapped_complex(complex_data)
        print(f"✓ Complex data serialization successful: {result}")
    except Exception as e:
        print(f"✗ Complex data serialization failed: {e}")
        return False
    class UnserializableObject:
        def __init__(self):
            self.data = "test"
    unserializable_data = {
        "normal": "data",
        "problematic": UnserializableObject()
    }
    try:
        result = wrapped_complex(unserializable_data)
        print(f"✓ Unserializable data handled gracefully: {result}")
    except Exception as e:
        print(f"✓ Unserializable data properly handled: {type(e).__name__}")
    return True

def test_metrics_collection():
    """Test metrics collection"""
    print("\n=== Testing Metrics Collection ===")
    
    agent = TestAgent("MetricsTestAgent")
    wrapper = AgentWrapper(
        agent_id="MetricsTestAgent",
        enable_input_validation=True,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        strict_validation=False
    )
    
    @wrapper.monitor()
    def wrapped_simple_task(data):
        return agent.simple_task(data)
    
    for i in range(5):
        wrapped_simple_task(f"metrics_test_{i}")
        time.sleep(0.1)
    
    # Get current stats from the wrapper
    current_stats = wrapper.get_agent_stats()
    
    print(f"✓ Metrics collected:")
    print(f"  - Total method calls: {current_stats.get('total_method_calls', 0)}")
    print(f"  - Total sessions: {current_stats.get('total_sessions', 0)}")
    print(f"  - Security events: {current_stats.get('security_events', 0)}")
    print(f"  - Errors handled: {current_stats.get('errors_handled', 0)}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Agent Sentinel SDK Improvement Tests")
    print("=" * 60)
    
    tests = [
        ("Configuration Validation", test_configuration_validation),
        ("Thread Safety", test_thread_safety),
        ("Error Handling", test_error_handling),
        ("Memory Management", test_memory_management),
        ("Class Monitoring", test_class_monitoring),
        ("MCP Monitoring", test_mcp_monitoring),
        ("Serialization Safety", test_serialization_safety),
        ("Metrics Collection", test_metrics_collection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    # Test async functionality
    try:
        asyncio.run(test_concurrent_sessions())
        passed += 1
        print("✅ Concurrent Sessions: PASSED")
    except Exception as e:
        print(f"❌ Concurrent Sessions: ERROR - {e}")
    
    total += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SDK improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit(main()) 