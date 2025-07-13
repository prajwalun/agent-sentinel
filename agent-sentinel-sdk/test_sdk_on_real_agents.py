import os
import json
from agent_sentinel.wrappers.decorators import monitor, sentinel

def test_function_agent():
    print("\nTesting function agent with @monitor...")
    @monitor
    def data_analysis_agent(data):
        # Simulate some analysis
        return {"summary": f"Processed {data['input']}"}
    result = data_analysis_agent({"input": "test data"})
    print(f"Function agent result: {result}")
    return True

def test_class_agent():
    print("\nTesting class agent with @sentinel...")
    @sentinel
    class ResearchAgent:
        def analyze(self, topic):
            return {"insight": f"Deep research on {topic}"}
    agent = ResearchAgent()
    result = agent.analyze("AI safety")
    print(f"Class agent result: {result}")
    return True

def check_logs_and_reports():
    print("\nChecking logs and reports...")
    log_files = [f for f in os.listdir("logs") if f.endswith(".json")]
    report_files = [f for f in os.listdir("reports") if f.endswith(".json")]
    print(f"Log files: {log_files}")
    print(f"Report files: {report_files}")
    # Print a sample log and report structure
    if log_files:
        with open(f"logs/{log_files[-1]}", 'r') as f:
            log_data = json.load(f)
            print(f"Sample log keys: {list(log_data.keys())}")
    if report_files:
        with open(f"reports/{report_files[-1]}", 'r') as f:
            report_data = json.load(f)
            print(f"Sample report keys: {list(report_data.keys())}")
    return bool(log_files) and bool(report_files)

def main():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    passed = 0
    if test_function_agent():
        print("✅ Function agent test passed")
        passed += 1
    if test_class_agent():
        print("✅ Class agent test passed")
        passed += 1
    if check_logs_and_reports():
        print("✅ Logs and reports generated")
        passed += 1
    print(f"\nSummary: {passed}/3 checks passed.")
    if passed == 3:
        print("🎉 SDK works on real agents and generates logs/reports as expected.")
    else:
        print("⚠️  Some checks failed. Please review the output.")

if __name__ == "__main__":
    main() 