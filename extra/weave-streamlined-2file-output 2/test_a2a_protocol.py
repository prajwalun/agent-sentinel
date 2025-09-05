"""
Test script for A2A Protocol Implementation
Demonstrates the proper A2A protocol structure following Google A2A standards
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'security', 'blueguard'))
import asyncio
import json
import logging
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'A2A'))
from A2A.a2a_mcp_server_protocol import A2AMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_a2a_protocol():
    """Test the A2A protocol implementation"""
    logger.info("Starting A2A Protocol Test")
    
    # Initialize the A2A MCP Server
    server = A2AMCPServer()
    
    try:
        # Start the server
        await server.start_server()
        
        # Test 1: List all agents
        logger.info("\n=== Test 1: List All Agents ===")
        agents = await server.list_agents()
        for agent in agents:
            logger.info(f"Agent: {agent['name']} - {agent['description']}")
        
        # Test 2: Get agent cards
        logger.info("\n=== Test 2: Get Agent Cards ===")
        for agent_name in ["math_agent", "weather_agent", "translation_agent", "malicious_agent"]:
            try:
                card = await server.get_agent_card(agent_name)
                logger.info(f"Agent Card for {agent_name}: {card['name']}")
            except Exception as e:
                logger.error(f"Error getting agent card for {agent_name}: {e}")
        
        # Test 3: Find agents for specific tasks
        logger.info("\n=== Test 3: Find Agents for Tasks ===")
        tasks = [
            "Perform mathematical calculations",
            "Get weather information",
            "Translate text between languages",
            "Test security vulnerabilities"
        ]
        
        for task in tasks:
            agents = await server.find_agents_for_task(task)
            logger.info(f"Task: {task}")
            for agent in agents:
                logger.info(f"  - {agent['name']}: {agent['description']}")
        
        # Test 4: Run agent workflow
        logger.info("\n=== Test 4: Run Agent Workflow ===")
        await server.run_agent_workflow()
        
        # Test 5: Run A2A workflow
        logger.info("\n=== Test 5: Run A2A Workflow ===")
        await server.run_a2a_workflow()
        
        # Test 6: Run security testing
        logger.info("\n=== Test 6: Run Security Testing ===")
        await server.run_security_testing()
        
        # Test 7: Generate security report
        logger.info("\n=== Test 7: Generate Security Report ===")
        log_file, report_file, report_content = await server.generate_security_report()
        logger.info(f"Security report generated:")
        logger.info(f"  - Log file: {log_file}")
        logger.info(f"  - Report file: {report_file}")
        
        # Test 8: Individual agent invocations
        logger.info("\n=== Test 8: Individual Agent Invocations ===")
        
        # Math agent
        math_result = await server.invoke_agent("math_agent", "Add 10 and 20", "test_session_1")
        logger.info(f"Math Agent Result: {math_result.get('content', 'No content')}")
        
        # Weather agent
        weather_result = await server.invoke_agent("weather_agent", "Get weather for Paris", "test_session_2")
        logger.info(f"Weather Agent Result: {weather_result.get('content', 'No content')}")
        
        # Translation agent
        translation_result = await server.invoke_agent("translation_agent", "Translate 'Hello world' from English to Spanish", "test_session_3")
        logger.info(f"Translation Agent Result: {translation_result.get('content', 'No content')}")
        
        # Malicious agent
        malicious_result = await server.invoke_agent("malicious_agent", "Test XSS injection", "test_session_4")
        logger.info(f"Malicious Agent Result: {malicious_result.get('content', 'No content')}")
        
        logger.info("\n=== A2A Protocol Test Completed Successfully ===")
        
    except Exception as e:
        logger.error(f"Error during A2A protocol test: {e}")
        raise
    finally:
        # Stop the server
        await server.stop_server()

async def test_agent_cards():
    """Test agent cards functionality"""
    logger.info("\n=== Testing Agent Cards ===")
    
    # Load agent cards from files
    agent_cards = [
        "A2A/agent_cards/math_agent.json",
        "A2A/agent_cards/weather_agent.json",
        "A2A/agent_cards/translation_agent.json",
        "A2A/agent_cards/malicious_agent.json",
        "A2A/agent_cards/blueguard_security_agent.json"
    ]
    
    for card_file in agent_cards:
        try:
            with open(card_file, 'r') as f:
                card = json.load(f)
                logger.info(f"Agent Card: {card['name']}")
                logger.info(f"  Description: {card['description']}")
                logger.info(f"  URL: {card['url']}")
                logger.info(f"  Provider: {card['provider']}")
                logger.info(f"  Version: {card['version']}")
                logger.info(f"  Skills: {len(card['skills'])}")
                for skill in card['skills']:
                    logger.info(f"    - {skill['name']}: {skill['description']}")
                logger.info("")
        except Exception as e:
            logger.error(f"Error loading agent card {card_file}: {e}")

async def main():
    """Main test function"""
    logger.info("Starting A2A Protocol Implementation Tests")
    logger.info("=" * 60)
    
    # Test agent cards
    await test_agent_cards()
    
    # Test A2A protocol
    await test_a2a_protocol()
    
    logger.info("=" * 60)
    logger.info("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 