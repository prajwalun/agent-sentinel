#!/usr/bin/env python3
"""
Enterprise Agent Sentinel Intelligence Layer - Main Entry Point

A sophisticated multi-agent system for analyzing security reports and generating
comprehensive threat intelligence using LangGraph and advanced LLM orchestration.
"""

import logging
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.workflow import create_workflow_from_env, SecurityAnalysisWorkflow
from src.models.config import IntelligenceConfig

# Configure enterprise logging
def setup_logging(log_level: str = "INFO", log_file: str = "intelligence.log"):
    """Setup enterprise-grade logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

def read_security_report(report_path: Optional[str] = None) -> str:
    """
    Read security report from various sources.
    
    Args:
        report_path: Optional specific path to report file
        
    Returns:
        Report content or None if not found
    """
    if report_path and Path(report_path).exists():
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
                logger.error(f"Error reading specified report {report_path}: {e}")
    return ""
    
    # Try common report locations
    possible_files = [
        "a2a_security_report.txt",
        "agent_sentinel_report.json",
        "security_report.txt",
        "unified_report.json",
        "logs/agent_sentinel.log"
    ]
    
    for filename in possible_files:
        file_path = Path(filename)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"✅ Read security report from: {filename}")
                return content
            except Exception as e:
                logger.warning(f"⚠️  Failed to read {filename}: {e}")
    
    return ""

def create_enterprise_prompt(security_report: str, analysis_type: str = "comprehensive") -> str:
    """
    Create enterprise-grade prompt for security analysis.
    
    Args:
        security_report: Security report content
        analysis_type: Type of analysis to perform
        
    Returns:
        Formatted prompt
    """
    base_prompt = f"""
ENTERPRISE SECURITY INTELLIGENCE ANALYSIS

Please perform a {analysis_type} security analysis of the following report and provide:

**EXECUTIVE SUMMARY:**
- High-level overview of the security situation
- Key findings and risk assessment
- Business impact analysis

**THREAT ANALYSIS:**
- Detailed analysis of each detected threat
- Threat categorization and classification
- Attack vector identification
- Malicious agent behavior analysis

**RISK ASSESSMENT:**
- Severity and impact assessment
- Risk scoring and prioritization
- Potential damage estimation
- Compliance implications

**ATTACK PATTERNS:**
- MITRE ATT&CK framework alignment
- Attack technique identification
- Pattern recognition and correlation
- Sophistication level assessment

**THREAT INTELLIGENCE:**
- Research similar threats and IOCs
- CVE information and vulnerability analysis
- Threat actor profiling
- Attack campaign identification

**RECOMMENDATIONS:**
- Immediate action items (0-4 hours)
- Short-term mitigation (24-48 hours)
- Long-term security improvements
- Incident response procedures

**FUTURE PREVENTION:**
- Security architecture improvements
- Monitoring and detection enhancements
- Policy and procedure updates
- Training and awareness recommendations

SECURITY REPORT TO ANALYZE:
{security_report}

Please provide a comprehensive, enterprise-grade analysis with clear sections, 
actionable insights, and specific recommendations for each threat detected.
"""
    
    return base_prompt

def validate_environment() -> bool:
    """Validate that required environment variables are set."""
    required_vars = ["OPENAI_API_KEY"]
    optional_vars = ["GOOGLE_API_KEY", "EXA_API_KEY", "WANDB_API_KEY"]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    # Check optional variables
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        logger.warning(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
        logger.warning("Some features may be limited without these variables")
    
    return True

def run_enterprise_analysis(
    report_data: Optional[str] = None,
    report_path: Optional[str] = None,
    analysis_type: str = "comprehensive",
    output_format: str = "all"
) -> Dict[str, Any]:
    """
    Run enterprise security analysis.
    
    Args:
        report_data: Direct report data
        report_path: Path to report file
        analysis_type: Type of analysis to perform
        output_format: Output format (text, json, pdf, all)
        
    Returns:
        Analysis results
    """
    start_time = datetime.now()
    
    try:
        # Validate environment
        if not validate_environment():
            return {
                "success": False,
                "error": "Environment validation failed",
                "execution_time": 0
            }
        
        # Read security report
        if report_data:
            security_report = report_data
        else:
            security_report = read_security_report(report_path)
        
        if not security_report:
            return {
                "success": False,
                "error": "No security report found or provided",
                "execution_time": 0
            }
        
        logger.info(f"✅ Security report loaded ({len(security_report)} characters)")
        
        # Create workflow
        workflow = create_workflow_from_env()
        
        # Create enterprise prompt
        enterprise_prompt = create_enterprise_prompt(security_report, analysis_type)
        
        # Execute workflow
        logger.info("Starting Enterprise Security Analysis Workflow...")
        result = workflow.execute(enterprise_prompt)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        if result["success"]:
            logger.info("✅ Enterprise Security Analysis completed successfully!")
            
            # Save report if available
            if result["final_report"]:
                saved_files = workflow.save_report(result["final_report"])
                
                if saved_files:
                    logger.info("📁 Enhanced reports saved:")
                    for file_type, file_path in saved_files.items():
                        logger.info(f"   {file_type.upper()}: {file_path}")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "total_steps": result["total_steps"],
                "final_report": result["final_report"],
                "saved_files": saved_files if result["final_report"] else {},
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "execution_time": execution_time,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
    except Exception as e:
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.error(f"❌ Enterprise analysis failed: {e}")
        
        return {
            "success": False,
            "error": str(e),
            "execution_time": execution_time,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Agent Sentinel Enterprise Intelligence Layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Analyze default report
  python main.py --report path/to/report.txt       # Analyze specific report
  python main.py --type quick                      # Quick analysis
  python main.py --output json                     # JSON output only
        """
    )
    
    parser.add_argument(
        "--report", "-r",
        type=str,
        help="Path to security report file"
    )
    
    parser.add_argument(
        "--type", "-t",
        type=str,
        choices=["comprehensive", "quick", "detailed"],
        default="comprehensive",
        help="Type of analysis to perform"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        choices=["text", "json", "pdf", "all"],
        default="all",
        help="Output format"
    )
    
    parser.add_argument(
        "--log-level", "-l",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default="logs/intelligence.log",
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    global logger
    logger = logging.getLogger(__name__)
    
    print("🔍 Agent Sentinel Enterprise Intelligence Layer")
    print("=" * 60)
    print(f"Analysis Type: {args.type.title()}")
    print(f"Output Format: {args.output}")
    print(f"Log Level: {args.log_level}")
    print("=" * 60)
    
    try:
        # Run enterprise analysis
        result = run_enterprise_analysis(
            report_path=args.report,
            analysis_type=args.type,
            output_format=args.output
        )
        
        if result["success"]:
            print(f"\n✅ Analysis completed successfully!")
            print(f"📊 Execution time: {result['execution_time']:.2f} seconds")
            print(f"📋 Total steps: {result['total_steps']}")
            
            if result["saved_files"]:
                print(f"\n📁 Reports saved:")
                for file_type, file_path in result["saved_files"].items():
                    print(f"   {file_type.upper()}: {file_path}")
            
            # Display report preview
            if result["final_report"]:
                print(f"\n📋 Report Preview:")
                print("-" * 40)
                preview = result["final_report"][:1000] + "..." if len(result["final_report"]) > 1000 else result["final_report"]
                print(preview)
                
                if len(result["final_report"]) > 1000:
                    print(f"\n... (Full report saved to files above)")
            
            return 0
        else:
            print(f"\n❌ Analysis failed: {result['error']}")
            print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error in main execution")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 