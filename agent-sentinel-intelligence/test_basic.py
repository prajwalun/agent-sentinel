#!/usr/bin/env python3
"""
Basic test for Agent Sentinel Intelligence Layer.

This test verifies that the new modular structure works correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all modules can be imported successfully."""
    print("Testing imports...")
    
    try:
        # Test core imports
        from src.models.config import IntelligenceConfig
        print("✅ IntelligenceConfig imported successfully")
        
        from src.services.llm_service import LLMService
        print("✅ LLMService imported successfully")
        
        from src.services.tracing_service import TracingService
        print("✅ TracingService imported successfully")
        
        from src.services.research_service import ResearchService
        print("✅ ResearchService imported successfully")
        
        # Test agent imports
        from src.agents.supervisor import SupervisorAgent
        print("✅ SupervisorAgent imported successfully")
        
        from src.agents.analyzer import SecurityAnalyzerAgent
        print("✅ SecurityAnalyzerAgent imported successfully")
        
        from src.agents.researcher import WebResearcherAgent
        print("✅ WebResearcherAgent imported successfully")
        
        from src.agents.reporter import ReportGeneratorAgent
        print("✅ ReportGeneratorAgent imported successfully")
        
        from src.agents.validator import ValidatorAgent
        print("✅ ValidatorAgent imported successfully")
        
        # Test workflow import
        from src.workflow import SecurityAnalysisWorkflow
        print("✅ SecurityAnalysisWorkflow imported successfully")
        
        # Test utility imports
        from src.utils.file_utils import read_security_report, save_report
        print("✅ File utilities imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_config():
    """Test configuration creation."""
    print("\nTesting configuration...")
    
    try:
        from src.models.config import IntelligenceConfig
        
        # Test default configuration
        config = IntelligenceConfig()
        print("✅ Default configuration created successfully")
        
        # Test with environment variables
        os.environ["OPENAI_API_KEY"] = "test_key"
        config_with_env = IntelligenceConfig()
        print("✅ Configuration with environment variables created successfully")
        
        print("🎉 Configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_services():
    """Test service initialization."""
    print("\nTesting services...")
    
    try:
        from src.models.config import IntelligenceConfig
        from src.services.llm_service import LLMService
        from src.services.tracing_service import TracingService
        from src.services.research_service import ResearchService
        
        config = IntelligenceConfig()
        
        # Test service creation (without actual API calls)
        llm_service = LLMService(config.llm)
        print("✅ LLMService created successfully")
        
        tracing_service = TracingService(config.tracing)
        print("✅ TracingService created successfully")
        
        research_service = ResearchService(config.research)
        print("✅ ResearchService created successfully")
        
        print("🎉 Service tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Agent Sentinel Intelligence Layer - Basic Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_services
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The new structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 