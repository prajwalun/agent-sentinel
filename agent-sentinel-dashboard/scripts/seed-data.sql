-- Insert sample agents for demo user
INSERT INTO agents (user_id, name, description, status, last_active, threat_count, performance_score) VALUES
  ((SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'DataBot', 'AI agent for data processing and analysis', 'active', NOW() - INTERVAL '2 minutes', 1, 98.5),
  ((SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'ChatBot', 'Customer service AI assistant', 'active', NOW() - INTERVAL '5 minutes', 0, 95.2),
  ((SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'MathAgent', 'Mathematical computation agent', 'active', NOW() - INTERVAL '12 minutes', 0, 99.1),
  ((SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'WebBot', 'Web scraping and analysis agent', 'inactive', NOW() - INTERVAL '1 hour', 2, 87.3);

-- Insert sample security events
INSERT INTO security_events (agent_id, user_id, event_type, severity, message, metadata) VALUES
  ((SELECT id FROM agents WHERE name = 'DataBot' LIMIT 1), (SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'security', 'critical', 'SQL injection detected in Agent "DataBot"', '{"query": "SELECT * FROM users WHERE id = 1 OR 1=1", "blocked": true}'),
  ((SELECT id FROM agents WHERE name = 'ChatBot' LIMIT 1), (SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'performance', 'medium', 'Performance warning in Agent "ChatBot"', '{"response_time": 2500, "threshold": 2000}'),
  ((SELECT id FROM agents WHERE name = 'MathAgent' LIMIT 1), (SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'info', 'low', 'Agent "MathAgent" completed successfully', '{"operations": 156, "success_rate": 100}'),
  ((SELECT id FROM agents WHERE name = 'WebBot' LIMIT 1), (SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'security', 'critical', 'XSS attempt blocked in Agent "WebBot"', '{"payload": "<script>alert(1)</script>", "blocked": true}');

-- Insert sample reports
INSERT INTO reports (agent_id, user_id, title, status, risk_score, executive_summary, security_events, performance_metrics, recommendations) VALUES
  ((SELECT id FROM agents WHERE name = 'MathAgent' LIMIT 1), (SELECT id FROM users WHERE email = 'demo@agentsentinel.com' LIMIT 1), 'MathAgent Security Report - 2025-01-13', 'clean', 12, 
   '{"overall_status": "CLEAN", "risk_score": 12, "threats_detected": 0, "performance": "Excellent", "recommendations_count": 2}',
   '{"total_events": 156, "security_events": 0, "performance_events": 2, "info_events": 154}',
   '{"response_time_avg": 245, "memory_usage": 45, "function_calls": 156, "success_rate": 99.8}',
   '[{"type": "optimization", "message": "Consider implementing caching for frequently used calculations"}, {"type": "monitoring", "message": "Add more detailed logging for complex operations"}]');
