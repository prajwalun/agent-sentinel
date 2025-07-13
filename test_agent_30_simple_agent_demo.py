#!/usr/bin/env python3
"""
Simple Agent Demo with Agent Sentinel SDK integration
This demonstrates how our SDK can wrap any agent function without complex dependencies.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-sentinel-sdk', 'src'))

from agent_sentinel import monitor, sentinel
from agent_sentinel.core.sentinel import AgentSentinel

# Simple agent functions that demonstrate different types of AI agent logic
@monitor
async def simple_text_analysis_agent(text: str) -> dict:
    """Simple text analysis agent that analyzes sentiment and extracts key information."""
    print(f"Analyzing text: {text[:50]}...")
    
    # Simulate AI processing
    analysis_result = {
        "text_length": len(text),
        "word_count": len(text.split()),
        "sentiment": "positive" if any(word in text.lower() for word in ["good", "great", "excellent", "happy"]) else "neutral",
        "key_topics": [word for word in text.lower().split() if len(word) > 5],
        "timestamp": datetime.now().isoformat(),
        "agent_type": "text_analysis"
    }
    
    return analysis_result

@monitor
async def data_processing_agent(data: list) -> dict:
    """Data processing agent that analyzes and transforms data."""
    print(f"Processing {len(data)} data points...")
    
    # Simulate data processing
    processed_data = {
        "total_items": len(data),
        "average_value": sum(data) / len(data) if data else 0,
        "min_value": min(data) if data else 0,
        "max_value": max(data) if data else 0,
        "processed_at": datetime.now().isoformat(),
        "agent_type": "data_processing"
    }
    
    return processed_data

@monitor
async def decision_making_agent(context: dict) -> dict:
    """Decision making agent that evaluates options and makes recommendations."""
    print(f"Making decision based on context: {list(context.keys())}")
    
    # Simulate decision making logic
    decision_result = {
        "recommendation": "proceed" if context.get("confidence", 0) > 0.7 else "review",
        "confidence_score": context.get("confidence", 0.5),
        "factors_considered": list(context.keys()),
        "decision_time": datetime.now().isoformat(),
        "agent_type": "decision_making"
    }
    
    return decision_result

@monitor
async def content_generation_agent(prompt: str, style: str = "professional") -> dict:
    """Content generation agent that creates text based on prompts."""
    print(f"Generating content with style: {style}")
    
    # Simulate content generation
    generated_content = {
        "content": f"Generated content based on: {prompt[:30]}...",
        "style": style,
        "word_count": len(prompt.split()) * 2,  # Simulate expansion
        "generated_at": datetime.now().isoformat(),
        "agent_type": "content_generation"
    }
    
    return generated_content

@monitor
async def multi_agent_orchestration():
    """Multi-agent orchestration that coordinates multiple agents."""
    print("Orchestrating multiple agents...")
    
    # Simulate multi-agent workflow
    text = "This is a great product that makes me very happy with its excellent features."
    data = [10, 20, 30, 40, 50]
    context = {"confidence": 0.8, "budget": 10000, "timeline": "3 months"}
    prompt = "Create a business proposal for a new software product"
    
    # Run multiple agents
    text_result = await simple_text_analysis_agent(text)
    data_result = await data_processing_agent(data)
    decision_result = await decision_making_agent(context)
    content_result = await content_generation_agent(prompt)
    
    # Combine results
    orchestration_result = {
        "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agents_executed": 4,
        "results": {
            "text_analysis": text_result,
            "data_processing": data_result,
            "decision_making": decision_result,
            "content_generation": content_result
        },
        "orchestration_completed_at": datetime.now().isoformat(),
        "agent_type": "multi_agent_orchestration"
    }
    
    return orchestration_result

@monitor
async def security_monitoring_agent(events: list) -> dict:
    """Security monitoring agent that analyzes events for threats."""
    print(f"Monitoring {len(events)} security events...")
    
    # Simulate security analysis
    threat_count = sum(1 for event in events if event.get("severity") == "high")
    security_result = {
        "total_events": len(events),
        "threats_detected": threat_count,
        "risk_level": "high" if threat_count > 2 else "medium" if threat_count > 0 else "low",
        "recommendations": [
            "Review high-severity events",
            "Update security policies",
            "Conduct security audit"
        ] if threat_count > 0 else ["Continue monitoring"],
        "analyzed_at": datetime.now().isoformat(),
        "agent_type": "security_monitoring"
    }
    
    return security_result

async def main():
    """Main test function demonstrating SDK integration with various agent types."""
    print("Starting Simple Agent Demo with Agent Sentinel SDK")
    print("=" * 60)
    
    # Initialize Agent Sentinel
    sentinel = AgentSentinel()
    
    try:
        # Test 1: Text Analysis Agent
        print("\n1. Testing Text Analysis Agent...")
        text_result = await simple_text_analysis_agent("This is an excellent product that makes me very happy!")
        print(f"✓ Text analysis completed: {text_result['sentiment']} sentiment")
        
        # Test 2: Data Processing Agent
        print("\n2. Testing Data Processing Agent...")
        data_result = await data_processing_agent([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        print(f"✓ Data processing completed: average = {data_result['average_value']}")
        
        # Test 3: Decision Making Agent
        print("\n3. Testing Decision Making Agent...")
        decision_result = await decision_making_agent({"confidence": 0.9, "budget": 50000})
        print(f"✓ Decision made: {decision_result['recommendation']}")
        
        # Test 4: Content Generation Agent
        print("\n4. Testing Content Generation Agent...")
        content_result = await content_generation_agent("Create a business plan", "professional")
        print(f"✓ Content generated: {content_result['word_count']} words")
        
        # Test 5: Security Monitoring Agent
        print("\n5. Testing Security Monitoring Agent...")
        security_events = [
            {"id": 1, "severity": "low", "type": "login"},
            {"id": 2, "severity": "high", "type": "unauthorized_access"},
            {"id": 3, "severity": "medium", "type": "data_access"}
        ]
        security_result = await security_monitoring_agent(security_events)
        print(f"✓ Security monitoring completed: {security_result['threats_detected']} threats detected")
        
        # Test 6: Multi-Agent Orchestration
        print("\n6. Testing Multi-Agent Orchestration...")
        orchestration_result = await multi_agent_orchestration()
        print(f"✓ Multi-agent orchestration completed: {orchestration_result['agents_executed']} agents executed")
        
        # Generate comprehensive report
        print("\n7. Generating comprehensive report...")
        report = sentinel.generate_unified_report()
        
        # Save report to logs
        os.makedirs('logs', exist_ok=True)
        with open('logs/simple_agent_demo_test_report.txt', 'w') as f:
            f.write("Simple Agent Demo SDK Integration Test Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Text Analysis Result: {json.dumps(text_result, indent=2)}\n\n")
            f.write(f"Data Processing Result: {json.dumps(data_result, indent=2)}\n\n")
            f.write(f"Decision Making Result: {json.dumps(decision_result, indent=2)}\n\n")
            f.write(f"Content Generation Result: {json.dumps(content_result, indent=2)}\n\n")
            f.write(f"Security Monitoring Result: {json.dumps(security_result, indent=2)}\n\n")
            f.write(f"Multi-Agent Orchestration Result: {json.dumps(orchestration_result, indent=2)}\n\n")
            f.write("Comprehensive Report:\n")
            f.write(report)
        
        print("✓ All tests completed successfully")
        print("✓ Report saved to logs/simple_agent_demo_test_report.txt")
        print("\n🎉 Agent Sentinel SDK successfully integrated with multiple agent types!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 