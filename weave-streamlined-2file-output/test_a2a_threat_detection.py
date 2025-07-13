"""
Dynamic A2A Threat Detection
Runs real agent interactions, captures logs, and analyzes them for threats dynamically
"""

import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
from src.a2a_mcp_server import RealA2AMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/logs/a2a_dynamic_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def run_dynamic_agent_interactions():
    """Run real agent interactions and capture them in logs"""
    logger.info("Starting Dynamic A2A Threat Detection...")
    
    # Create necessary directories
    Path("src/logs").mkdir(exist_ok=True)
    Path("src/reports").mkdir(exist_ok=True)
    
    # Initialize Real A2A MCP Server
    real_a2a_server = RealA2AMCPServer()
    
    try:
        # Start the A2A server
        await real_a2a_server.a2a_server.start_server()
        
        logger.info("=" * 60)
        logger.info("RUNNING DYNAMIC AGENT INTERACTIONS")
        logger.info("=" * 60)
        
        # Phase 1: Run various agent interactions (real usage scenarios)
        logger.info("Phase 1: Executing agent interactions...")
        
        # Math agent operations
        logger.info("Math Agent Operations:")
        add_result = await real_a2a_server.invoke_agent_tool("math_agent", "add", {"a": 15, "b": 27})
        logger.info(f"  Add: 15 + 27 = {add_result}")
        
        multiply_result = await real_a2a_server.invoke_agent_tool("math_agent", "multiply", {"a": 8, "b": 9})
        logger.info(f"  Multiply: 8 * 9 = {multiply_result}")
        
        # Weather agent operations
        logger.info("Weather Agent Operations:")
        weather_result = await real_a2a_server.invoke_agent_tool("weather_agent", "get_weather", {"city": "New York"})
        logger.info(f"  Weather: {weather_result}")
        
        forecast_result = await real_a2a_server.invoke_agent_tool("weather_agent", "get_forecast", {"city": "Tokyo"})
        logger.info(f"  Forecast: {forecast_result}")
        
        # Translation agent operations
        logger.info("Translation Agent Operations:")
        translate_result = await real_a2a_server.invoke_agent_tool(
            "translation_agent", 
            "translate_text", 
            {"text": "Hello world", "source_lang": "en", "target_lang": "es"}
        )
        logger.info(f"  Translation: {translate_result}")
        
        # Malicious agent operations (these will trigger threats)
        logger.info("Malicious Agent Operations (Testing Security):")
        malicious_result = await real_a2a_server.invoke_agent_tool(
            "malicious_agent", 
            "inject_html", 
            {"payload": "<script>alert('test')</script>"}
        )
        logger.info(f"  Malicious: {malicious_result}")
        
        # Phase 2: Agent-to-agent data flow (real cross-agent scenarios)
        logger.info("Phase 2: Agent-to-agent data flow...")
        
        # Weather data flows to math agent
        weather_data = await real_a2a_server.invoke_agent_tool("weather_agent", "get_weather", {"city": "London"})
        logger.info(f"  Weather data: {weather_data}")
        
        # Extract temperature number from weather data for math operations
        temp_str = weather_data.split("°")[0].split(":")[-1].strip()
        try:
            temp = int(temp_str)
            math_result = await real_a2a_server.invoke_agent_tool("math_agent", "add", {"a": temp, "b": 10})
            logger.info(f"  Math with weather data: {temp} + 10 = {math_result}")
        except:
            logger.info(f"  Could not extract temperature from: {weather_data}")
        
        # Malicious data flows to translation agent (this should trigger cross-agent threats)
        malicious_data = await real_a2a_server.invoke_agent_tool(
            "malicious_agent", 
            "extract_data", 
            {"query": "sensitive information"}
        )
        logger.info(f"  Malicious data: {malicious_data}")
        
        # Translation agent processes malicious data
        if malicious_data:
            translation_result = await real_a2a_server.invoke_agent_tool(
                "translation_agent",
                "translate_text",
                {"text": malicious_data, "source_lang": "en", "target_lang": "fr"}
            )
            logger.info(f"  Translation of malicious data: {translation_result}")
        
        # Phase 3: Generate comprehensive security analysis
        logger.info("Phase 3: Generating security analysis...")
        
        log_file, report_file, report_content = await real_a2a_server.generate_security_report()
        
        # Stop the A2A server
        await real_a2a_server.a2a_server.stop_server()
        
        # Display summary
        logger.info("=" * 60)
        logger.info("DYNAMIC A2A THREAT DETECTION COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total Interactions: {len(real_a2a_server.interaction_log)}")
        logger.info(f"Security Events: {len(real_a2a_server.blueguard.security_events)}")
        logger.info(f"Security Alerts: {len(real_a2a_server.blueguard.alerts)}")
        logger.info(f"Cross-Agent Threats: {len(real_a2a_server.blueguard.cross_agent_threats)}")
        logger.info(f"Communication Log: {log_file}")
        logger.info(f"Security Report: {report_file}")
        
        # Print the security report
        print("\n" + "=" * 60)
        print("DYNAMIC A2A THREAT DETECTION REPORT")
        print("=" * 60)
        print(report_content)
        
        return {
            "interactions": len(real_a2a_server.interaction_log),
            "security_events": len(real_a2a_server.blueguard.security_events),
            "alerts": len(real_a2a_server.blueguard.alerts),
            "cross_agent_threats": len(real_a2a_server.blueguard.cross_agent_threats),
            "log_file": log_file,
            "report_file": report_file
        }
        
    except Exception as e:
        logger.error(f"Error in dynamic A2A threat detection: {e}")
        raise

async def analyze_logs_for_threats(log_file_path):
    """Analyze existing log files for threats (can be run separately)"""
    logger.info("Analyzing existing log files for threats...")
    
    try:
        with open(log_file_path, 'r') as f:
            log_data = json.load(f)
        
        # Extract interactions from log
        interactions = log_data.get('interactions', [])
        
        # Initialize BlueGuard for analysis
        from src.security.blueguard import BlueGuard
        blueguard = BlueGuard()
        
        # Analyze all interactions
        analysis_result = await blueguard.analyze_interaction_log(interactions)
        
        logger.info(f"Log Analysis Results:")
        logger.info(f"  Total Interactions: {analysis_result['total_interactions']}")
        logger.info(f"  Total Threats: {analysis_result['total_threats']}")
        logger.info(f"  Cross-Agent Threats: {analysis_result['cross_agent_threats']}")
        logger.info(f"  Multi-Agent Attack Chains: {analysis_result['multi_agent_attack_chains']}")
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error analyzing logs: {e}")
        return None

if __name__ == "__main__":
    # Run dynamic agent interactions
    result = asyncio.run(run_dynamic_agent_interactions())
    
    # Optionally analyze existing logs
    # asyncio.run(analyze_logs_for_threats("src/logs/your_log_file.json")) 