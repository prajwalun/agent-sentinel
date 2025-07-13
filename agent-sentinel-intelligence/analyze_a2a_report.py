#!/usr/bin/env python3
"""
Analyze A2A Security Report with Intelligence Agent

This script reads the A2A security report and feeds it to the
sentinel-intelligence agent for enhanced analysis.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def read_security_report(report_path: str) -> str:
    """Read the security report file."""
    try:
        with open(report_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error reading report: {e}")
        return None

def create_intelligence_prompt(security_report: str) -> str:
    """Create a comprehensive prompt for the intelligence agent."""
    return f"""
ANALYZE THIS SECURITY REPORT AND PROVIDE ENHANCED THREAT INTELLIGENCE

Please analyze the following security report from an A2A (Agent-to-Agent) system and provide:

1. **Executive Summary**: High-level overview of the security situation
2. **Threat Analysis**: Detailed analysis of each detected threat
3. **Risk Assessment**: Severity and impact assessment
4. **Attack Patterns**: Identify attack patterns and techniques used
5. **Threat Intelligence**: Research similar threats and IOCs
6. **Recommendations**: Specific actionable steps to mitigate threats
7. **Future Prevention**: How to prevent similar attacks

SECURITY REPORT TO ANALYZE:
{security_report}

Please provide a comprehensive analysis with clear sections, actionable insights, and specific recommendations for each threat detected.
"""

def main():
    """Main execution function."""
    print("🔍 Agent Sentinel Intelligence Analysis")
    print("=" * 60)
    
    # Path to the security report
    report_path = "a2a_security_report.txt"
    
    # Read the security report
    print("📖 Reading security report...")
    security_report = read_security_report(report_path)
    if not security_report:
        return
    
    print(f"✅ Report loaded ({len(security_report)} characters)")
    print(f"📊 Report contains: {security_report.count('FINDING')} security findings")
    
    # Create intelligence prompt
    print("\n🤖 Creating intelligence analysis prompt...")
    intelligence_prompt = create_intelligence_prompt(security_report)
    
    # Import and run the intelligence workflow
    try:
        print("\n🚀 Starting Intelligence Analysis...")
        print("=" * 60)
        
        from workflow import create_workflow_from_env
        
        # Create workflow
        workflow = create_workflow_from_env()
        
        # Execute with our security report
        result = workflow.execute(intelligence_prompt)
        
        if result["success"]:
            print("\n✅ Intelligence Analysis Completed!")
            print(f"📊 Total steps: {result['total_steps']}")
            
            # Save enhanced report
            if result["final_report"]:
                saved_files = workflow.save_report(
                    result["final_report"], 
                    "a2a_intelligence_analysis"
                )
                
                if saved_files:
                    print("\n📁 Enhanced Reports Saved:")
                    for file_type, file_path in saved_files.items():
                        print(f"   {file_type.upper()}: {file_path}")
                
                # Display final report preview
                print("\n📋 Enhanced Intelligence Report Preview:")
                print("=" * 60)
                preview = result["final_report"][:1000] + "..." if len(result["final_report"]) > 1000 else result["final_report"]
                print(preview)
                
                if len(result["final_report"]) > 1000:
                    print(f"\n... (Full report saved to files above)")
            
        else:
            print(f"\n❌ Intelligence analysis failed: {result.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and the intelligence layer is properly set up")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 