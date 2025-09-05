"""
Mock Agent Sentinel SDK for Testing
Provides a simplified version of the Agent Sentinel SDK for demonstration purposes
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Callable
import functools

logger = logging.getLogger(__name__)

class MockSentinelDecorator:
    """Mock Agent Sentinel SDK decorator for demonstration purposes"""
    
    def __init__(self, agent_id: str = None):
        self.agent_id = agent_id or "unknown_agent"
        self.interactions = []
        self.security_events = []
        
    def __call__(self, func_or_class):
        if isinstance(func_or_class, type):
            # Class decorator
            return self._wrap_class(func_or_class)
        else:
            # Function decorator
            return self._wrap_function(func_or_class)
    
    def _wrap_class(self, cls):
        """Wrap all methods of a class with monitoring"""
        original_methods = {}
        
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_') and attr_name not in ['get_skills']:
                original_methods[attr_name] = attr
                setattr(cls, attr_name, self._wrap_method(attr, attr_name))
        
        # Add monitoring capabilities to the class
        original_init = cls.__init__
        
        def new_init(self_instance, *args, **kwargs):
            original_init(self_instance, *args, **kwargs)
            self_instance._sentinel_interactions = self.interactions
            self_instance._sentinel_security_events = self.security_events
            self_instance._sentinel_agent_id = self.agent_id
        
        cls.__init__ = new_init
        return cls
    
    def _wrap_method(self, method, method_name):
        """Wrap a single method with monitoring"""
        if asyncio.iscoroutinefunction(method):
            @functools.wraps(method)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_with_monitoring(method, method_name, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(method)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(self._execute_with_monitoring(method, method_name, *args, **kwargs))
            return sync_wrapper
    
    async def _execute_with_monitoring(self, method, method_name, *args, **kwargs):
        """Execute method with monitoring"""
        start_time = datetime.now()
        
        # Log the interaction
        interaction = {
            "timestamp": start_time.isoformat(),
            "agent_id": self.agent_id,
            "method": method_name,
            "args": str(args[1:]) if len(args) > 1 else "[]",  # Skip 'self'
            "kwargs": str(kwargs),
            "type": "method_call"
        }
        
        try:
            # Execute the original method
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            
            # Log successful completion
            end_time = datetime.now()
            interaction.update({
                "status": "success",
                "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "end_time": end_time.isoformat()
            })
            
            # Basic security analysis
            self._analyze_security(interaction, result)
            
            self.interactions.append(interaction)
            
            logger.info(f"🔍 [SENTINEL] {self.agent_id}.{method_name} - Success ({interaction['duration_ms']:.2f}ms)")
            
            return result
            
        except Exception as e:
            # Log error
            end_time = datetime.now()
            interaction.update({
                "status": "error",
                "error": str(e),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "end_time": end_time.isoformat()
            })
            
            self.interactions.append(interaction)
            
            logger.error(f"🚨 [SENTINEL] {self.agent_id}.{method_name} - Error: {e}")
            
            raise
    
    def _wrap_function(self, func):
        """Wrap a standalone function with monitoring"""
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._execute_function_with_monitoring(func, *args, **kwargs)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(self._execute_function_with_monitoring(func, *args, **kwargs))
            return sync_wrapper
    
    async def _execute_function_with_monitoring(self, func, *args, **kwargs):
        """Execute function with monitoring"""
        start_time = datetime.now()
        
        interaction = {
            "timestamp": start_time.isoformat(),
            "agent_id": self.agent_id,
            "function": func.__name__,
            "args": str(args),
            "kwargs": str(kwargs),
            "type": "function_call"
        }
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            end_time = datetime.now()
            interaction.update({
                "status": "success",
                "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "end_time": end_time.isoformat()
            })
            
            self._analyze_security(interaction, result)
            self.interactions.append(interaction)
            
            logger.info(f"🔍 [SENTINEL] {func.__name__} - Success ({interaction['duration_ms']:.2f}ms)")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            interaction.update({
                "status": "error",
                "error": str(e),
                "duration_ms": (end_time - start_time).total_seconds() * 1000,
                "end_time": end_time.isoformat()
            })
            
            self.interactions.append(interaction)
            logger.error(f"🚨 [SENTINEL] {func.__name__} - Error: {e}")
            
            raise
    
    def _analyze_security(self, interaction: Dict, result: Any):
        """Basic security analysis of interactions"""
        security_patterns = {
            "script_injection": ["<script", "javascript:", "onerror="],
            "sql_injection": ["drop table", "union select", "'; --"],
            "command_injection": ["rm -rf", "cat /etc/passwd", "wget", "curl"],
            "data_exfiltration": ["password", "secret", "token", "api_key"],
            "prompt_injection": ["ignore all previous", "system:", "admin:"]
        }
        
        args_str = str(interaction.get('args', ''))
        kwargs_str = str(interaction.get('kwargs', ''))
        result_str = str(result)
        content = f"{args_str} {kwargs_str} {result_str}".lower()
        
        for threat_type, patterns in security_patterns.items():
            for pattern in patterns:
                if pattern in content:
                    security_event = {
                        "timestamp": interaction["timestamp"],
                        "agent_id": self.agent_id,
                        "threat_type": threat_type,
                        "pattern": pattern,
                        "context": interaction.get("method", interaction.get("function", "unknown")),
                        "severity": "high" if threat_type in ["script_injection", "sql_injection"] else "medium"
                    }
                    
                    self.security_events.append(security_event)
                    logger.warning(f"🚨 [SENTINEL THREAT] {threat_type} detected in {self.agent_id}: {pattern}")

# Create the main sentinel decorator
sentinel = MockSentinelDecorator

def get_monitoring_stats(monitored_object):
    """Get monitoring statistics from a monitored object"""
    if hasattr(monitored_object, '_sentinel_interactions'):
        return {
            "interactions": len(monitored_object._sentinel_interactions),
            "security_events": len(monitored_object._sentinel_security_events),
            "agent_id": monitored_object._sentinel_agent_id
        }
    return {"interactions": 0, "security_events": 0, "agent_id": "unknown"}

def generate_report(monitored_objects: List[Any], test_name: str) -> Dict:
    """Generate a monitoring report for a test"""
    report = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "total_interactions": 0,
        "total_security_events": 0,
        "agents": []
    }
    
    for obj in monitored_objects:
        if hasattr(obj, '_sentinel_interactions'):
            agent_report = {
                "agent_id": obj._sentinel_agent_id,
                "interactions": len(obj._sentinel_interactions),
                "security_events": len(obj._sentinel_security_events),
                "interaction_details": obj._sentinel_interactions,
                "security_event_details": obj._sentinel_security_events
            }
            report["agents"].append(agent_report)
            report["total_interactions"] += agent_report["interactions"]
            report["total_security_events"] += agent_report["security_events"]
    
    return report 