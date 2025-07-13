#!/usr/bin/env python3
"""
Example showing how user logs connect to the Intelligence API for LLM analysis.
This demonstrates the complete flow from user code to enhanced reports.
"""

import requests
import json
import time
from datetime import datetime

# Simulated SDK functionality
class AgentSentinelSDK:
    """Simulated SDK that captures user agent logs"""
    
    def __init__(self, intelligence_api_url="http://localhost:8001"):
        self.intelligence_api_url = intelligence_api_url
        self.logs = []
        self.security_events = []
    
    def monitor_function(self, func):
        """Decorator that monitors function calls"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute user function
                result = func(*args, **kwargs)
                
                # Log successful execution
                self._log_event({
                    "function": func.__name__,
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration": time.time() - start_time,
                    "args": str(args)[:100],  # Truncate for security
                })
                
                return result
                
            except Exception as e:
                # Log error
                self._log_event({
                    "function": func.__name__,
                    "status": "error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "duration": time.time() - start_time,
                    "error": str(e)
                })
                
                # Check for security threats
                if "malicious" in str(e).lower() or "hack" in str(e).lower():
                    self._log_security_event({
                        "threat_type": "suspicious_error",
                        "severity": "HIGH",
                        "message": f"Suspicious error in {func.__name__}: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                raise
        
        return wrapper
    
    def _log_event(self, event):
        """Log a regular event"""
        self.logs.append(event)
        print(f"📝 SDK Log: {event['function']} - {event['status']}")
    
    def _log_security_event(self, event):
        """Log a security event"""
        self.security_events.append(event)
        print(f"🚨 Security Event: {event['threat_type']} - {event['severity']}")
    
    def generate_report(self):
        """Generate a security report from collected logs"""
        if not self.logs and not self.security_events:
            return "No activity recorded"
        
        report = f"""AGENT SENTINEL SECURITY REPORT
Generated: {datetime.utcnow().isoformat()}
Total Events: {len(self.logs)}
Security Events: {len(self.security_events)}

ACTIVITY SUMMARY:
"""
        
        # Add regular logs
        for log in self.logs[-5:]:  # Last 5 events
            report += f"- {log['timestamp']}: {log['function']} ({log['status']})\n"
        
        # Add security events
        if self.security_events:
            report += f"\nSECURITY EVENTS:\n"
            for event in self.security_events:
                report += f"- {event['timestamp']}: {event['threat_type']} - {event['severity']}\n"
                report += f"  Message: {event['message']}\n"
        
        return report
    
    def send_to_intelligence_api(self, report):
        """Send report to Intelligence API for LLM analysis"""
        try:
            print(f"\n📤 Sending report to Intelligence API...")
            print(f"Report length: {len(report)} characters")
            
            response = requests.post(
                f"{self.intelligence_api_url}/analyze",
                json={
                    "report_content": report,
                    "analysis_type": "comprehensive",
                    "agent_id": "user-agent-001"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                enhanced_report = response.json()
                print(f"✅ Intelligence API analysis successful!")
                return enhanced_report
            else:
                print(f"❌ Intelligence API failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error sending to Intelligence API: {e}")
            return None

# Example usage - simulating user's application
def demonstrate_integration():
    """Demonstrate how user logs connect to LLM analysis"""
    
    print("🚀 Agent Sentinel Integration Demo")
    print("=" * 50)
    
    # Initialize SDK
    sdk = AgentSentinelSDK()
    
    # User's agent functions with SDK monitoring
    @sdk.monitor_function
    def user_agent_function():
        """Simulated user agent function"""
        print("🤖 User agent is processing...")
        time.sleep(0.1)  # Simulate processing
        return "Agent completed successfully"
    
    @sdk.monitor_function
    def suspicious_function():
        """Simulated suspicious function"""
        print("⚠️  Suspicious activity detected...")
        raise Exception("Malicious activity detected: unauthorized access attempt")
    
    @sdk.monitor_function
    def api_call_function():
        """Simulated API call"""
        print("🌐 Making API call...")
        time.sleep(0.2)
        return {"status": "success", "data": "API response"}
    
    # Simulate user running their agent
    print("\n1. User runs their agent with SDK monitoring:")
    print("-" * 40)
    
    # Normal function call
    try:
        result1 = user_agent_function()
        print(f"Result: {result1}")
    except:
        pass
    
    # API call
    try:
        result2 = api_call_function()
        print(f"API Result: {result2}")
    except:
        pass
    
    # Suspicious activity
    try:
        result3 = suspicious_function()
    except Exception as e:
        print(f"Caught exception: {e}")
    
    # Generate report from logs
    print("\n2. SDK generates security report:")
    print("-" * 40)
    raw_report = sdk.generate_report()
    print(raw_report)
    
    # Send to Intelligence API for LLM analysis
    print("\n3. Intelligence API enhances report with LLM:")
    print("-" * 40)
    enhanced_report = sdk.send_to_intelligence_api(raw_report)
    
    if enhanced_report:
        print(f"✅ Enhanced report generated!")
        print(f"🆔 Agent ID: {enhanced_report.get('agent_id', 'N/A')}")
        print(f"📊 Risk Score: {enhanced_report.get('summary', {}).get('risk_score', 'N/A')}")
        print(f"🚨 Threats: {enhanced_report.get('summary', {}).get('threats_detected', 'N/A')}")
        print(f"💡 Recommendations: {len(enhanced_report.get('recommendations', []))} items")
        
        # Show first recommendation
        recommendations = enhanced_report.get('recommendations', [])
        if recommendations:
            print(f"   First recommendation: {recommendations[0]}")
    
    print("\n4. Dashboard displays enhanced report:")
    print("-" * 40)
    print("📊 Dashboard shows:")
    print("   • Risk assessment and scoring")
    print("   • Threat analysis with MITRE ATT&CK mapping")
    print("   • AI-generated recommendations")
    print("   • Timeline and event correlation")
    print("   • Actionable security insights")
    
    print(f"\n🎯 COMPLETE FLOW:")
    print(f"   User Code → SDK Monitoring → Raw Logs → Intelligence API → LLM Analysis → Enhanced Report → Dashboard")

if __name__ == "__main__":
    demonstrate_integration() 