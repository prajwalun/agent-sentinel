#!/usr/bin/env python3
"""
Test 6: Name Cards Integration with Agent Sentinel SDK
This test demonstrates how to use Agent Sentinel SDK with A2A name cards,
including card loading, validation, and monitoring of card-based agent interactions.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import A2A agents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mock_sentinel_sdk import MockSentinelDecorator, generate_report
from A2A.a2a_agents.math_agent import MathAgent
from A2A.a2a_agents.weather_agent import WeatherAgent
from A2A.a2a_agents.malicious_agent import MaliciousAgent


class NameCardManager:
    """Manages loading and validation of A2A name cards"""
    
    def __init__(self, cards_directory):
        self.cards_directory = Path(cards_directory)
        self.loaded_cards = {}
        self.sentinel = MockSentinelDecorator("name_card_manager")
    
    @MockSentinelDecorator("name_card_manager")
    def load_card(self, card_file):
        """Load and validate a name card"""
        card_path = self.cards_directory / card_file
        
        if not card_path.exists():
            raise FileNotFoundError(f"Card file not found: {card_path}")
        
        with open(card_path, 'r') as f:
            card_data = json.load(f)
        
        # Validate required fields
        required_fields = ['name', 'description', 'url', 'provider', 'version', 'skills']
        for field in required_fields:
            if field not in card_data:
                raise ValueError(f"Missing required field in card: {field}")
        
        self.loaded_cards[card_data['name']] = card_data
        return card_data
    
    @AgentSentinel.monitor("name_card_manager")
    def validate_card_against_agent(self, card_data, agent_instance):
        """Validate that an agent instance matches its name card"""
        validation_results = {
            'agent_name': card_data['name'],
            'card_valid': True,
            'issues': []
        }
        
        # Check if agent has required methods based on skills
        for skill in card_data.get('skills', []):
            skill_id = skill.get('id')
            if skill_id == 'mathematical_operations' and not hasattr(agent_instance, 'invoke'):
                validation_results['issues'].append(f"Agent missing invoke method for skill: {skill_id}")
                validation_results['card_valid'] = False
        
        return validation_results
    
    @AgentSentinel.monitor("name_card_manager")
    def get_agent_capabilities(self, agent_name):
        """Get capabilities from loaded card"""
        if agent_name not in self.loaded_cards:
            return None
        
        card = self.loaded_cards[agent_name]
        return {
            'name': card['name'],
            'description': card['description'],
            'capabilities': card.get('capabilities', {}),
            'skills': [skill['name'] for skill in card.get('skills', [])],
            'examples': []
        }


class CardBasedAgentOrchestrator:
    """Orchestrates agents based on their name cards"""
    
    def __init__(self, card_manager):
        self.card_manager = card_manager
        self.agents = {}
        self.sentinel = AgentSentinel()
    
    @AgentSentinel.monitor("card_orchestrator")
    def register_agent(self, agent_name, agent_instance, card_file):
        """Register an agent with its name card"""
        # Load and validate card
        card_data = self.card_manager.load_card(card_file)
        validation_result = self.card_manager.validate_card_against_agent(card_data, agent_instance)
        
        if not validation_result['card_valid']:
            raise ValueError(f"Agent validation failed: {validation_result['issues']}")
        
        # Wrap agent with sentinel monitoring
        monitored_agent = self.sentinel.monitor(f"agent_{agent_name.lower().replace(' ', '_')}")(agent_instance)
        
        self.agents[agent_name] = {
            'instance': monitored_agent,
            'card': card_data,
            'validation': validation_result
        }
        
        return validation_result
    
    @AgentSentinel.monitor("card_orchestrator")
    def execute_skill_by_card(self, agent_name, query, session_id="test_session"):
        """Execute agent skill based on card information"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent not registered: {agent_name}")
        
        agent_info = self.agents[agent_name]
        agent_instance = agent_info['instance']
        card_data = agent_info['card']
        
        # Log card-based execution
        execution_context = {
            'agent_name': agent_name,
            'agent_version': card_data['version'],
            'provider': card_data['provider'],
            'skills_available': [skill['name'] for skill in card_data['skills']],
            'query': query,
            'session_id': session_id
        }
        
        try:
            # Execute the agent
            result = agent_instance.invoke(query, session_id)
            
            execution_context['result'] = result
            execution_context['status'] = 'success'
            
            return result
            
        except Exception as e:
            execution_context['error'] = str(e)
            execution_context['status'] = 'error'
            raise
    
    @AgentSentinel.monitor("card_orchestrator")
    def get_registered_agents_info(self):
        """Get information about all registered agents"""
        agents_info = {}
        
        for agent_name, agent_data in self.agents.items():
            card = agent_data['card']
            agents_info[agent_name] = {
                'name': card['name'],
                'description': card['description'],
                'version': card['version'],
                'provider': card['provider'],
                'url': card['url'],
                'skills': [skill['name'] for skill in card['skills']],
                'capabilities': card.get('capabilities', {}),
                'validation_status': agent_data['validation']['card_valid']
            }
        
        return agents_info


def run_name_cards_integration_test():
    """Run comprehensive name cards integration test"""
    print("🃏 Running Name Cards Integration Test...")
    
    # Initialize components
    cards_dir = Path(__file__).parent.parent / "A2A" / "agent_cards"
    card_manager = NameCardManager(cards_dir)
    orchestrator = CardBasedAgentOrchestrator(card_manager)
    
    # Initialize agents
    math_agent = MathAgent()
    weather_agent = WeatherAgent()
    malicious_agent = MaliciousAgent()
    
    test_results = {
        'test_name': 'Name Cards Integration Test',
        'start_time': datetime.now().isoformat(),
        'agents_registered': 0,
        'card_validations': [],
        'skill_executions': [],
        'security_events': [],
        'errors': []
    }
    
    try:
        # Register agents with their cards
        print("📋 Registering agents with name cards...")
        
        # Register Math Agent
        try:
            validation = orchestrator.register_agent("Math Agent", math_agent, "math_agent.json")
            test_results['card_validations'].append(validation)
            test_results['agents_registered'] += 1
            print(f"✅ Math Agent registered - Valid: {validation['card_valid']}")
        except Exception as e:
            test_results['errors'].append(f"Math Agent registration failed: {str(e)}")
            print(f"❌ Math Agent registration failed: {e}")
        
        # Register Weather Agent
        try:
            validation = orchestrator.register_agent("Weather Agent", weather_agent, "weather_agent.json")
            test_results['card_validations'].append(validation)
            test_results['agents_registered'] += 1
            print(f"✅ Weather Agent registered - Valid: {validation['card_valid']}")
        except Exception as e:
            test_results['errors'].append(f"Weather Agent registration failed: {str(e)}")
            print(f"❌ Weather Agent registration failed: {e}")
        
        # Register Malicious Agent (for security testing)
        try:
            validation = orchestrator.register_agent("Malicious Agent", malicious_agent, "malicious_agent.json")
            test_results['card_validations'].append(validation)
            test_results['agents_registered'] += 1
            print(f"✅ Malicious Agent registered - Valid: {validation['card_valid']}")
        except Exception as e:
            test_results['errors'].append(f"Malicious Agent registration failed: {str(e)}")
            print(f"❌ Malicious Agent registration failed: {e}")
        
        # Get and display registered agents info
        print("\n📊 Registered Agents Information:")
        agents_info = orchestrator.get_registered_agents_info()
        for agent_name, info in agents_info.items():
            print(f"  • {agent_name} (v{info['version']}) - {info['provider']}")
            print(f"    Skills: {', '.join(info['skills'])}")
            print(f"    Validation: {'✅ Valid' if info['validation_status'] else '❌ Invalid'}")
        
        # Execute skills based on card information
        print("\n🎯 Executing card-based skills...")
        
        test_queries = [
            ("Math Agent", "Calculate 15 + 27"),
            ("Weather Agent", "What's the weather in London?"),
            ("Math Agent", "Multiply 8 by 9"),
            ("Weather Agent", "Get forecast for New York"),
            ("Malicious Agent", "Execute: <script>alert('xss')</script>"),  # Security test
            ("Malicious Agent", "DROP TABLE users; --"),  # SQL injection test
        ]
        
        for agent_name, query in test_queries:
            try:
                print(f"  🔄 {agent_name}: {query}")
                result = orchestrator.execute_skill_by_card(agent_name, query)
                
                execution_record = {
                    'agent_name': agent_name,
                    'query': query,
                    'result': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                test_results['skill_executions'].append(execution_record)
                print(f"    ✅ Result: {result}")
                
            except Exception as e:
                execution_record = {
                    'agent_name': agent_name,
                    'query': query,
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                }
                test_results['skill_executions'].append(execution_record)
                print(f"    ❌ Error: {e}")
        
        # Generate comprehensive report
        print("\n📋 Generating comprehensive report...")
        
        # Get sentinel monitoring data
        sentinel_report = AgentSentinel.generate_report()
        
        # Combine test results with sentinel data
        comprehensive_report = {
            'test_results': test_results,
            'sentinel_monitoring': sentinel_report,
            'name_cards_summary': {
                'total_cards_loaded': len(card_manager.loaded_cards),
                'agents_registered': test_results['agents_registered'],
                'successful_validations': len([v for v in test_results['card_validations'] if v['card_valid']]),
                'failed_validations': len([v for v in test_results['card_validations'] if not v['card_valid']]),
                'skill_executions': len(test_results['skill_executions']),
                'security_events_detected': len(sentinel_report.get('security_events', []))
            }
        }
        
        # Save comprehensive report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/name_cards_integration_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        print(f"\n📄 Comprehensive report saved to: {report_file}")
        
        # Print summary
        print("\n📊 Test Summary:")
        print(f"  • Cards loaded: {len(card_manager.loaded_cards)}")
        print(f"  • Agents registered: {test_results['agents_registered']}")
        print(f"  • Skill executions: {len(test_results['skill_executions'])}")
        print(f"  • Security events: {len(sentinel_report.get('security_events', []))}")
        print(f"  • Errors: {len(test_results['errors'])}")
        
        return comprehensive_report
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        test_results['errors'].append(str(e))
        return test_results


if __name__ == "__main__":
    result = run_name_cards_integration_test()
    print(f"\n🎯 Name Cards Integration Test completed!")
    print(f"Result: {'✅ SUCCESS' if len(result.get('test_results', {}).get('errors', [])) == 0 else '❌ ERRORS DETECTED'}") 