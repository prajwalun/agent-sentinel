#!/usr/bin/env python3
"""
Simple Agent Sentinel Decorator Test
Tests only the 3 main decorators that users should use
"""

from agent_sentinel import monitor, sentinel, monitor_mcp

def test_monitor_decorator():
    """Test the @monitor decorator for individual functions."""
    print("🔍 Testing @monitor decorator...")
    
    @monitor
    def process_data(data: str) -> str:
        print(f"🤖 Processing data: {data}")
        return data.upper()
    
    result = process_data("hello world")
    print(f"✅ @monitor result: {result}")
    return True

def test_sentinel_decorator():
    """Test the @sentinel decorator for entire classes."""
    print("🔍 Testing @sentinel class decorator...")
    
    @sentinel
    class DataProcessor:
        def analyze_data(self, data: str) -> str:
            print(f"🤖 Analyzing data: {data}")
            return f"Analysis: {data.upper()}"
        
        def generate_report(self, findings: str) -> str:
            print(f"🤖 Generating report: {findings}")
            return f"Report: {findings}"
    
    processor = DataProcessor()
    result1 = processor.analyze_data("test data")
    result2 = processor.generate_report("findings")
    print(f"✅ @sentinel results: {result1}, {result2}")
    return True

def test_monitor_mcp_decorator():
    """Test the @monitor_mcp decorator for MCP tools."""
    print("🔍 Testing @monitor_mcp decorator...")
    
    @monitor_mcp()
    def search_database(query: str) -> str:
        print(f"🤖 Searching database: {query}")
        return f"Search results for: {query}"
    
    result = search_database("test query")
    print(f"✅ @monitor_mcp result: {result}")
    return True

def main():
    """Run all decorator tests."""
    print("🚀 Agent Sentinel Simple Decorator Test")
    print("=" * 50)
    print("Testing the 3 main decorators users should use:")
    print("1. @monitor - for individual functions")
    print("2. @sentinel - for entire classes")
    print("3. @monitor_mcp - for MCP tools")
    print("=" * 50)
    
    results = []
    
    # Test all decorators
    results.append(("@monitor", test_monitor_decorator()))
    results.append(("@sentinel", test_sentinel_decorator()))
    results.append(("@monitor_mcp", test_monitor_mcp_decorator()))
    
    # Display results
    print("\n📊 Test Results:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All 3 decorators working perfectly!")
        print("✅ Users should only use: @monitor, @sentinel, @monitor_mcp")
    else:
        print("⚠️  Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    main() 