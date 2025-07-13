#!/usr/bin/env python3
"""
Run all Agent Sentinel SDK integration tests
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

def run_test(test_file):
    """Run a single test file and capture output"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        
        return {
            'test_file': test_file,
            'success': success,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            'test_file': test_file,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Test timed out after 30 seconds',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'test_file': test_file,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Run all tests and generate comprehensive report"""
    print("🚀 Agent Sentinel SDK Integration Tests")
    print("=" * 60)
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # List of all test files - prioritize working tests
    test_files = [
        "test_simple_working_example.py",  # Known working
        "test_1_single_agent_monitoring.py",  # Working (with issues but passes)
        "test_3_agent_to_agent_communication.py",  # Working (with issues but passes)
        "test_6_name_cards_working.py",  # Name cards test (may have issues)
        "test_2_mcp_server_monitoring.py",  # Has issues but tests important functionality
        "test_4_workflow_security_monitoring.py",  # Has issues
        "test_5_cross_agent_threat_detection.py",  # Has issues
    ]
    
    # Only run tests that exist
    available_tests = []
    for test_file in test_files:
        if os.path.exists(test_file):
            available_tests.append(test_file)
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    test_results = []
    successful_tests = 0
    failed_tests = 0
    
    for test_file in available_tests:
        result = run_test(test_file)
        test_results.append(result)
        
        if result['success']:
            successful_tests += 1
            print(f"✅ {test_file} - PASSED")
        else:
            failed_tests += 1
            print(f"❌ {test_file} - FAILED")
            if result['stderr']:
                # Show first few lines of error
                error_lines = result['stderr'].split('\n')[:3]
                for line in error_lines:
                    if line.strip():
                        print(f"   {line}")
    
    # Generate comprehensive test report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    comprehensive_report = {
        'test_suite': 'Agent Sentinel SDK Integration Tests',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': len(test_results),
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'success_rate': f"{(successful_tests/len(test_results)*100):.1f}%" if test_results else "0%"
        },
        'test_results': test_results,
        'integration_patterns_tested': [
            "Single Agent Monitoring",
            "MCP Server Communication Monitoring", 
            "Agent-to-Agent Communication",
            "Multi-Agent Workflow Security",
            "Cross-Agent Threat Detection",
            "Name Cards Integration"
        ]
    }
    
    # Save comprehensive report
    report_file = logs_dir / f"comprehensive_test_report_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump(comprehensive_report, f, indent=2)
    
    # Save detailed output log
    log_file = logs_dir / f"test_execution_log_{timestamp}.txt"
    with open(log_file, 'w') as f:
        f.write("Agent Sentinel SDK Integration Tests - Detailed Log\n")
        f.write("=" * 60 + "\n\n")
        
        for result in test_results:
            f.write(f"Test: {result['test_file']}\n")
            f.write(f"Status: {'PASSED' if result['success'] else 'FAILED'}\n")
            f.write(f"Return Code: {result['returncode']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write("-" * 40 + "\n")
            f.write("STDOUT:\n")
            f.write(result['stdout'])
            f.write("\n" + "-" * 40 + "\n")
            f.write("STDERR:\n")
            f.write(result['stderr'])
            f.write("\n" + "=" * 60 + "\n\n")
    
    # Print final summary
    print(f"\n{'='*60}")
    print(f"📊 Test Suite Summary")
    print(f"{'='*60}")
    print(f"Total Tests: {len(test_results)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/len(test_results)*100):.1f}%" if test_results else "0%")
    
    # Show working tests
    working_tests = [r for r in test_results if r['success']]
    if working_tests:
        print(f"\n✅ Working Tests:")
        for test in working_tests:
            print(f"  • {test['test_file']}")
    
    # Show failed tests
    failed_tests_list = [r for r in test_results if not r['success']]
    if failed_tests_list:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests_list:
            print(f"  • {test['test_file']}")
    
    print(f"\n📄 Reports saved:")
    print(f"  • Comprehensive report: {report_file}")
    print(f"  • Detailed log: {log_file}")
    
    # List all generated report files in logs directory
    report_files = list(logs_dir.glob("*.json"))
    if report_files:
        print(f"\n📋 All generated reports in logs/:")
        for report in sorted(report_files)[-10:]:  # Show last 10 reports
            print(f"  • {report.name}")
    
    # Show integration patterns tested
    print(f"\n🎯 Integration Patterns Tested:")
    for pattern in comprehensive_report['integration_patterns_tested']:
        print(f"  • {pattern}")
    
    return successful_tests == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 