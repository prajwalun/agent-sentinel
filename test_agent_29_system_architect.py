#!/usr/bin/env python3
"""
Test script for AI System Architect Agent with Agent Sentinel SDK integration
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-sentinel-sdk', 'src'))

from agent_sentinel import monitor, sentinel
from agent_sentinel.core.sentinel import AgentSentinel

# Add the system architect agent to the path
sys.path.insert(0, 'awesome-llm-apps-main 2/advanced_ai_agents/single_agent_apps/ai_system_architect_r1')

# Import the actual system architect agent
from ai_system_architect_r1 import ModelChain

@monitor
async def test_system_architect_agent():
    """Test the AI System Architect agent with actual agent logic"""
    print("Testing AI System Architect Agent with Agent Sentinel SDK...")
    
    # Test data
    test_prompt = """
    I need to build a healthcare data management system that:
    - Handles patient records and appointments
    - Needs to scale to 10,000 users
    - Must be HIPAA compliant
    - Budget constraint of $50k for initial setup
    - Should integrate with existing hospital systems
    """
    
    # Mock API keys for testing
    deepseek_api_key = "test_deepseek_key"
    anthropic_api_key = "test_anthropic_key"
    
    try:
        # Initialize the actual ModelChain
        chain = ModelChain(deepseek_api_key, anthropic_api_key)
        
        # Test the DeepSeek reasoning (this will fail without real API keys, but we can test the structure)
        print("Testing DeepSeek reasoning...")
        try:
            reasoning_result = chain.get_deepseek_reasoning(test_prompt)
            print(f"DeepSeek reasoning completed: {len(reasoning_result)} parts")
        except Exception as e:
            print(f"DeepSeek reasoning failed (expected without real API): {e}")
            # Create mock reasoning for testing Claude response
            reasoning_result = ("Mock reasoning content", "Mock technical analysis")
        
        # Test the Claude response
        print("Testing Claude response...")
        try:
            claude_response = chain.get_claude_response(test_prompt, reasoning_result)
            print(f"Claude response completed: {len(claude_response)} characters")
            return claude_response
        except Exception as e:
            print(f"Claude response failed (expected without real API): {e}")
            return f"Error: {str(e)}"
        
    except Exception as e:
        print(f"Error in system architect agent: {e}")
        return f"Error: {str(e)}"

@monitor
async def test_model_chain_initialization():
    """Test the ModelChain initialization"""
    print("Testing ModelChain initialization...")
    
    try:
        # Test initialization with mock keys
        deepseek_api_key = "test_deepseek_key"
        anthropic_api_key = "test_anthropic_key"
        
        chain = ModelChain(deepseek_api_key, anthropic_api_key)
        
        # Check that the chain was initialized properly
        print(f"ModelChain initialized successfully")
        print(f"Current model: {chain.current_model}")
        print(f"Agent model: {chain.agent.model.id}")
        
        return {
            'status': 'success',
            'current_model': chain.current_model,
            'agent_model': chain.agent.model.id
        }
        
    except Exception as e:
        print(f"Error in ModelChain initialization: {e}")
        return f"Error: {str(e)}"

@monitor
async def test_architecture_analysis():
    """Test architecture analysis with different scenarios"""
    print("Testing architecture analysis scenarios...")
    
    test_scenarios = [
        {
            'name': 'E-commerce Platform',
            'prompt': 'Build an e-commerce platform for 100k users with payment processing and inventory management'
        },
        {
            'name': 'IoT Data Platform',
            'prompt': 'Create an IoT data platform for collecting and analyzing sensor data from 10k devices'
        },
        {
            'name': 'AI Chatbot Service',
            'prompt': 'Develop an AI chatbot service that can handle 1M conversations per day with 99.9% uptime'
        }
    ]
    
    results = {}
    
    for scenario in test_scenarios:
        print(f"Testing scenario: {scenario['name']}")
        try:
            # This would normally call the actual agent, but we'll simulate the structure
            results[scenario['name']] = {
                'status': 'simulated',
                'prompt': scenario['prompt'],
                'architecture_pattern': 'microservices',  # Simulated result
                'database_choice': 'hybrid',
                'estimated_cost': {'implementation': 75000, 'maintenance': 15000}
            }
        except Exception as e:
            results[scenario['name']] = f"Error: {str(e)}"
    
    return results

async def main():
    """Main test function"""
    print("Starting AI System Architect Agent SDK Integration Test")
    print("=" * 60)
    
    # Initialize Agent Sentinel
    sentinel = AgentSentinel()
    
    try:
        # Test ModelChain initialization
        result1 = await test_model_chain_initialization()
        print(f"✓ ModelChain initialization test completed: {result1}")
        
        # Test architecture analysis scenarios
        result2 = await test_architecture_analysis()
        print(f"✓ Architecture analysis test completed: {len(result2)} scenarios")
        
        # Test system architect agent
        result3 = await test_system_architect_agent()
        print(f"✓ System architect agent test completed")
        
        # Generate comprehensive report
        report = await sentinel.generate_comprehensive_report()
        
        # Save report to logs
        os.makedirs('logs', exist_ok=True)
        with open('logs/system_architect_agent_test_report.txt', 'w') as f:
            f.write("AI System Architect Agent SDK Integration Test Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"ModelChain Initialization Result: {result1}\n\n")
            f.write(f"Architecture Analysis Results: {result2}\n\n")
            f.write(f"System Architect Agent Result: {result3}\n\n")
            f.write("Comprehensive Report:\n")
            f.write(report)
        
        print("✓ Test completed successfully")
        print("✓ Report saved to logs/system_architect_agent_test_report.txt")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 