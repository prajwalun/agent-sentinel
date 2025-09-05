#!/usr/bin/env python3
"""
Test script for Tarot Reading Agent with Agent Sentinel SDK integration
"""

import os
import sys
import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the SDK to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent-sentinel-sdk', 'src'))

from agent_sentinel import monitor, sentinel
from agent_sentinel.core.sentinel import AgentSentinel

# Add the tarot app to the path
sys.path.insert(0, 'awesome-llm-apps-main 2/advanced_llm_apps/chat-with-tarots')

# Import the actual tarot app components
import app
import helpers.help_func as hf

@monitor
async def test_tarot_reading_agent():
    """Test the tarot reading agent with actual agent logic"""
    print("Testing Tarot Reading Agent with Agent Sentinel SDK...")
    
    # Test data
    test_context = "I'm considering a career change and want guidance on this decision."
    test_cards = [
        {'name': 'The Fool', 'is_reversed': False},
        {'name': 'The Magician', 'is_reversed': True},
        {'name': 'The High Priestess', 'is_reversed': False}
    ]
    
    # Test the actual analyzer chain
    try:
        print("Running tarot reading analysis...")
        analysis_result = app.analyzer.invoke({
            "cards": test_cards, 
            "context": test_context
        })
        
        print(f"Tarot reading result: {analysis_result.content}")
        return analysis_result.content
        
    except Exception as e:
        print(f"Error in tarot reading: {e}")
        return f"Error: {str(e)}"

@monitor
async def test_card_drawing_functionality():
    """Test the card drawing functionality"""
    print("Testing card drawing functionality...")
    
    try:
        # Test drawing different numbers of cards
        card_names_in_dataset = app.df['card'].unique().tolist()
        
        results = {}
        for num_cards in [3, 5, 7]:
            drawn_cards = hf.generate_random_draw(num_cards, card_names_in_dataset)
            results[f"{num_cards}_cards"] = drawn_cards
            print(f"Drew {num_cards} cards: {[card['name'] for card in drawn_cards]}")
        
        return results
        
    except Exception as e:
        print(f"Error in card drawing: {e}")
        return f"Error: {str(e)}"

@monitor
async def test_prompt_preparation():
    """Test the prompt preparation functionality"""
    print("Testing prompt preparation...")
    
    try:
        # Test the prompt preparation function
        test_input = {
            "cards": [
                {'name': 'The Fool', 'is_reversed': False},
                {'name': 'The Magician', 'is_reversed': True}
            ],
            "context": "Test question about love"
        }
        
        prepared_prompt = hf.prepare_prompt_input(test_input, app.card_meanings)
        print(f"Prepared prompt: {prepared_prompt}")
        
        return prepared_prompt
        
    except Exception as e:
        print(f"Error in prompt preparation: {e}")
        return f"Error: {str(e)}"

async def main():
    """Main test function"""
    print("Starting Tarot Reading Agent SDK Integration Test")
    print("=" * 50)
    
    # Initialize Agent Sentinel
    sentinel = AgentSentinel()
    
    try:
        # Test card drawing
        result1 = await test_card_drawing_functionality()
        print(f"✓ Card drawing test completed: {len(result1)} test cases")
        
        # Test prompt preparation
        result2 = await test_prompt_preparation()
        print(f"✓ Prompt preparation test completed")
        
        # Test tarot reading analysis
        result3 = await test_tarot_reading_agent()
        print(f"✓ Tarot reading analysis test completed")
        
        # Generate comprehensive report
        report = await sentinel.generate_comprehensive_report()
        
        # Save report to logs
        os.makedirs('logs', exist_ok=True)
        with open('logs/tarot_reading_agent_test_report.txt', 'w') as f:
            f.write("Tarot Reading Agent SDK Integration Test Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Card Drawing Results: {result1}\n\n")
            f.write(f"Prompt Preparation Result: {result2}\n\n")
            f.write(f"Tarot Reading Analysis Result: {result3}\n\n")
            f.write("Comprehensive Report:\n")
            f.write(report)
        
        print("✓ Test completed successfully")
        print("✓ Report saved to logs/tarot_reading_agent_test_report.txt")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 