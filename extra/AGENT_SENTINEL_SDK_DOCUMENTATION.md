# Agent Sentinel SDK - Complete Technical Documentation

## Table of Contents
1. [SDK Overview](#sdk-overview)
2. [Architecture & Design](#architecture--design)
3. [Core Components](#core-components)
4. [Security Implementation](#security-implementation)
5. [Detection Engine](#detection-engine)
6. [Wrappers & Decorators](#wrappers--decorators)
7. [Usage Examples](#usage-examples)
8. [Configuration](#configuration)
9. [API Reference](#api-reference)
10. [Security Features](#security-features)
11. [Performance & Monitoring](#performance--monitoring)
12. [Best Practices](#best-practices)

---

## SDK Overview

**Agent Sentinel SDK** is a comprehensive Python library designed to provide enterprise-grade security monitoring for AI agents. It offers real-time threat detection, behavioral analysis, input validation, and comprehensive logging with minimal integration effort.

### Key Features
- **🛡️ Real-time Threat Detection**: Multi-layered security monitoring
- **🔍 Behavioral Analysis**: Anomaly detection and pattern recognition
- **✅ Input Validation**: Comprehensive security validation
- **📊 Separate Logging & Reporting**: Structured logs and threat reports
- **⚡ Performance Optimized**: Thread-safe and memory-efficient
- **🎯 Easy Integration**: 2-line setup with decorators

---

## Architecture & Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Sentinel SDK                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Wrappers  │  │   Security  │  │  Detection  │        │
│  │  & Decorators│  │   Layer     │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Core     │  │   Logging   │  │ Intelligence│        │
│  │  Sentinel   │  │   System    │  │   Engine    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Event     │  │   Report    │  │   Threat    │        │
│  │  Registry   │  │  Generator  │  │  Analysis   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### 1. Core Sentinel (`core/sentinel.py`)
- **Main Interface**: Primary SDK entry point
- **Event Management**: Thread-safe event handling
- **Configuration**: Centralized configuration management
- **Session Management**: Agent session tracking

#### 2. Security Layer (`security/validators.py`)
- **Input Validation**: Comprehensive security validation
- **Threat Detection**: Pattern-based threat identification
- **Sanitization**: Input/output sanitization
- **Risk Scoring**: Dynamic risk assessment

#### 3. Detection Engine (`detection/`)
- **Multi-Layer Detection**: Rule-based, pattern-based, ML-based
- **Real-time Analysis**: Continuous threat monitoring
- **Behavioral Analysis**: Anomaly detection
- **Performance Monitoring**: Resource usage tracking

#### 4. Wrappers (`wrappers/`)
- **Decorators**: Easy integration with existing code
- **Agent Wrapper**: Comprehensive agent monitoring
- **MCP Wrapper**: Model Context Protocol integration
- **Communication Wrapper**: Inter-agent communication monitoring

---

## Core Components

### 1. AgentSentinel Class

```python
class AgentSentinel:
    """
    Main class for AgentSentinel security monitoring SDK.
    
    Provides the primary interface for monitoring AI agents,
    detecting security threats, and managing security events.
    """
    
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
        auto_start: bool = True,
        enable_threat_intelligence: bool = True,
    ) -> None:
        """
        Initialize AgentSentinel with configuration.
        
        Args:
            config_path: Path to YAML configuration file
            config_dict: Dictionary configuration
            agent_id: Agent identifier
            environment: Environment name
            auto_start: Whether to automatically start monitoring
        """
```

**Key Methods:**
- `start_monitoring()`: Start security monitoring
- `stop_monitoring()`: Stop security monitoring
- `create_security_event()`: Create a security event
- `get_events()`: Retrieve security events
- `get_metrics()`: Get performance metrics
- `generate_security_report()`: Generate security report

### 2. Event Registry

```python
class EventRegistry:
    """
    Thread-safe event registry for managing security events
    across multiple agents and sessions.
    """
    
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.lock = threading.RLock()
        self.event_handlers: List[Callable] = []
    
    def add_event(self, event: SecurityEvent) -> None:
        """Add a security event to the registry."""
        with self.lock:
            self.events.append(event)
            self._notify_handlers(event)
    
    def get_events(
        self,
        agent_id: Optional[str] = None,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SeverityLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[SecurityEvent]:
        """Retrieve filtered security events."""
```

### 3. Configuration Management

```python
class Config:
    """
    Configuration management for AgentSentinel.
    
    Supports YAML files, environment variables, and dictionary
    configuration with validation and defaults.
    """
    
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        agent_id: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        self.agent_id = agent_id or os.getenv("AGENT_SENTINEL_AGENT_ID", "default")
        self.environment = environment or os.getenv("AGENT_SENTINEL_ENVIRONMENT", "development")
        
        # Load configuration from multiple sources
        self.config = self._load_config(config_path, config_dict)
        self._validate_config()
```

---

## Security Implementation

### 1. Input Validation System

```python
class InputValidator(BaseValidator):
    """
    Comprehensive input validator that checks for multiple threat types
    including script injection, SQL injection, prompt injection, and more.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize specialized validators
        self.script_validator = ScriptInjectionValidator()
        self.sql_validator = SQLInjectionValidator()
        self.prompt_validator = PromptInjectionValidator()
        self.data_exfiltration_validator = DataExfiltrationValidator()
        self.privilege_escalation_validator = PrivilegeEscalationValidator()
    
    def validate(self, input_data: str) -> ValidationResponse:
        """Validate input data against all threat types."""
        # Check input length
        if len(input_data) > self.max_input_length:
            return ValidationResponse(
                result=ValidationResult.BLOCKED,
                is_safe=False,
                confidence_score=1.0,
                threat_type=ThreatType.INPUT_OVERFLOW,
                violations=["Input exceeds maximum allowed length"],
                risk_score=1.0
            )
        
        # Run all validators
        results = []
        results.append(self.script_validator.validate(input_data))
        results.append(self.sql_validator.validate(input_data))
        results.append(self.prompt_validator.validate(input_data))
        results.append(self.data_exfiltration_validator.validate(input_data))
        results.append(self.privilege_escalation_validator.validate(input_data))
        
        # Aggregate results
        return self._aggregate_results(results, input_data)
```

### 2. Threat Detection Patterns

```python
class ScriptInjectionValidator(BaseValidator):
    """Detect script injection attacks (XSS, JavaScript injection)."""
    
    def __init__(self):
        super().__init__()
        self.patterns = [
            # HTML script tags
            r"<script[^>]*>.*?</script>",
            r"<script[^>]*>",
            r"</script>",
            
            # JavaScript protocol
            r"javascript:",
            r"vbscript:",
            r"data:text/html",
            
            # Event handlers
            r"on\w+\s*=",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            
            # JavaScript functions
            r"alert\s*\(",
            r"confirm\s*\(",
            r"prompt\s*\(",
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            
            # DOM manipulation
            r"document\.write",
            r"innerHTML\s*=",
            r"outerHTML\s*=",
            
            # Encoded payloads
            r"&#x?[0-9a-fA-F]+;",
            r"%[0-9a-fA-F]{2}",
            r"\\x[0-9a-fA-F]{2}",
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.patterns]
    
    def validate(self, input_data: str) -> ValidationResponse:
        """Validate input for script injection threats."""
        violations = []
        threat_indicators = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            if pattern.search(input_data):
                violations.append(f"Script injection pattern detected: {self.patterns[i]}")
                threat_indicators.append({
                    "pattern": self.patterns[i],
                    "match": pattern.search(input_data).group()
                })
        
        if violations:
            return ValidationResponse(
                result=ValidationResult.BLOCKED if self.strict_mode else ValidationResult.SUSPICIOUS,
                is_safe=False,
                confidence_score=0.9,
                threat_type=ThreatType.SCRIPT_INJECTION,
                violations=violations,
                risk_score=0.9,
                metadata={"threat_indicators": threat_indicators}
            )
        
        return ValidationResponse(
            result=ValidationResult.VALID,
            is_safe=True,
            confidence_score=1.0,
            risk_score=0.0
        )
```

### 3. Data Sanitization

```python
class DataSanitizer:
    """Sanitize data to prevent injection attacks."""
    
    @staticmethod
    def sanitize_html(input_data: str) -> str:
        """Sanitize HTML content."""
        return html.escape(input_data, quote=True)
    
    @staticmethod
    def sanitize_sql(input_data: str) -> str:
        """Sanitize SQL input (basic)."""
        # Remove dangerous characters
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_"]
        sanitized = input_data
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized
    
    @staticmethod
    def sanitize_url(input_data: str) -> str:
        """Sanitize URL input."""
        return urllib.parse.quote(input_data, safe=':/?=&')
    
    @staticmethod
    def sanitize_prompt(input_data: str) -> str:
        """Sanitize prompt input to prevent injection."""
        # Remove common prompt injection patterns
        injection_patterns = [
            r"ignore\s+all\s+previous\s+instructions",
            r"ignore\s+the\s+above",
            r"system\s+prompt\s+override",
            r"bypass\s+security",
            r"ignore\s+safety",
        ]
        
        sanitized = input_data
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
```

---

## Detection Engine

### 1. Multi-Layer Detection Architecture

```python
class MultiLayerDetectionEngine:
    """
    Enterprise-grade detection engine with modular plugin architecture.
    
    Implements a robust, extensible runtime security framework similar to
    enterprise security tools like Datadog Security, Snyk, and Wiz.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detectors: List[BaseDetector] = []
        self.detection_queue = Queue()
        self.is_running = False
        
        # Initialize detectors
        self._initialize_detectors()
    
    def _initialize_detectors(self):
        """Initialize all detection modules."""
        self.detectors.extend([
            RuleBasedDetector(self.config.get("rules", [])),
            PatternBasedDetector(self.config.get("patterns", [])),
            AnomalyDetector(self.config.get("anomaly_config", {})),
            BehavioralDetector(self.config.get("behavior_config", {})),
            MLBasedDetector(self.config.get("ml_config", {})),
        ])
    
    async def detect_threats(self, context: DetectionContext) -> List[DetectionResult]:
        """Run all detectors on the given context."""
        results = []
        
        for detector in self.detectors:
            if detector.enabled:
                try:
                    detector_results = await detector.detect(context)
                    results.extend(detector_results)
                except Exception as e:
                    logger.error(f"Detector {detector.name} failed: {e}")
        
        return results
```

### 2. Rule-Based Detection

```python
class RuleBasedDetector(BaseDetector):
    """Rule-based detector for time-based, threshold, and domain-specific rules."""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        super().__init__("RuleBasedDetector")
        self.rules = rules
        self.call_history: Dict[str, List[float]] = {}
        self.sensitive_token_patterns = [
            r"\b(password|secret|key|token|credential)\b",
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        ]
    
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        results = []
        
        # Time-based rules
        results.extend(self._check_time_based_rules(context))
        
        # Threshold rules
        results.extend(self._check_threshold_rules(context))
        
        # Sensitive data detection
        results.extend(self._check_sensitive_data(context))
        
        # Domain-specific rules
        results.extend(self._check_domain_rules(context))
        
        return results
    
    def _check_sensitive_data(self, context: DetectionContext) -> List[DetectionResult]:
        """Check for sensitive data in inputs/outputs."""
        results = []
        
        # Check inputs
        for key, value in context.inputs.items():
            if isinstance(value, str):
                for pattern in self.sensitive_token_patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        results.append(DetectionResult(
                            threat_type=ThreatType.DATA_EXFILTRATION,
                            severity=SeverityLevel.MEDIUM,
                            confidence=0.8,
                            message=f"Sensitive data detected in input '{key}'",
                            context={"input_key": key, "pattern": pattern},
                            detection_method=DetectionMethod.RULE_BASED,
                            detector_name=self.name
                        ))
        
        return results
```

### 3. Behavioral Analysis

```python
class BehavioralDetector(BaseDetector):
    """Detect anomalous behavior patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("BehavioralDetector")
        self.config = config
        self.behavior_profiles: Dict[str, Dict[str, Any]] = {}
        self.anomaly_threshold = config.get("anomaly_threshold", 0.7)
    
    async def detect(self, context: DetectionContext) -> List[DetectionResult]:
        results = []
        
        # Update behavior profile
        self._update_behavior_profile(context)
        
        # Check for anomalies
        anomalies = self._detect_anomalies(context)
        results.extend(anomalies)
        
        # Check for suspicious patterns
        suspicious_patterns = self._detect_suspicious_patterns(context)
        results.extend(suspicious_patterns)
        
        return results
    
    def _detect_anomalies(self, context: DetectionContext) -> List[DetectionResult]:
        """Detect behavioral anomalies."""
        results = []
        
        if context.agent_id not in self.behavior_profiles:
            return results
        
        profile = self.behavior_profiles[context.agent_id]
        
        # Check call frequency
        current_time = time.time()
        recent_calls = [t for t in profile.get("call_times", []) 
                       if current_time - t < 3600]  # Last hour
        
        if len(recent_calls) > profile.get("max_calls_per_hour", 100):
            results.append(DetectionResult(
                threat_type=ThreatType.RATE_LIMITING,
                severity=SeverityLevel.MEDIUM,
                confidence=0.8,
                message="Unusual call frequency detected",
                context={"calls_per_hour": len(recent_calls)},
                detection_method=DetectionMethod.ANOMALY_DETECTION,
                detector_name=self.name
            ))
        
        return results
```

---

## Wrappers & Decorators

### 1. Main Decorators

```python
def sentinel(
    cls,
    enable_separate_logs: bool = True,
    enable_threat_reports: bool = True,
    log_format: str = "json",
    report_format: str = "json"
):
    """
    Simple decorator to monitor an entire agent class
    
    This decorator automatically wraps all public methods of a class
    with security monitoring.
    
    Usage:
        @sentinel
        class MyAgent:
            def process_data(self, data: str) -> str:
                return data.upper()
    """
    # Create wrapper instance
    wrapper_instance = AgentWrapper(
        agent_id=getattr(cls, '__name__', 'UnknownClass'),
        enable_input_validation=True,
        strict_validation=False,
        enable_behavior_analysis=True,
        enable_performance_monitoring=True,
        enable_separate_logs=enable_separate_logs,
        enable_threat_reports=enable_threat_reports,
        log_format=log_format,
        report_format=report_format
    )
    
    # Wrap all public methods
    for attr_name in dir(cls):
        if not attr_name.startswith('_'):
            attr = getattr(cls, attr_name)
            if callable(attr):
                wrapped_method = wrapper_instance.monitor()(attr)
                setattr(cls, attr_name, wrapped_method)
    
    return cls


def monitor(func):
    """
    Simple decorator to monitor individual methods
    
    Usage:
        @monitor
        def process_data(self, data: str) -> str:
            return data.upper()
    """
    wrapper_instance = AgentWrapper(
        agent_id=f"{getattr(func, '__module__', 'unknown')}.{getattr(func, '__name__', 'unknown')}"
    )
    return wrapper_instance.monitor()(func)
```

### 2. Agent Wrapper

```python
class AgentWrapper:
    """
    Comprehensive wrapper for monitoring AI agents with security features.
    """
    
    def __init__(
        self,
        agent_id: str,
        enable_input_validation: bool = True,
        strict_validation: bool = False,
        enable_behavior_analysis: bool = True,
        enable_performance_monitoring: bool = True,
        enable_separate_logs: bool = True,
        enable_threat_reports: bool = True,
        log_format: str = "json",
        report_format: str = "json"
    ):
        self.agent_id = agent_id
        self.enable_input_validation = enable_input_validation
        self.strict_validation = strict_validation
        self.enable_behavior_analysis = enable_behavior_analysis
        self.enable_performance_monitoring = enable_performance_monitoring
        
        # Initialize components
        self.sentinel = AgentSentinel(agent_id=agent_id)
        self.validator = InputValidator(strict_mode=strict_validation)
        self.detector = MultiLayerDetectionEngine({})
        self.logger = SecurityLogger(agent_id=agent_id)
        
        # Start monitoring
        self.sentinel.start_monitoring()
    
    def monitor(self):
        """Create a monitoring decorator."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    # Input validation
                    if self.enable_input_validation:
                        self._validate_inputs(args, kwargs)
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Output validation
                    if self.enable_input_validation:
                        self._validate_output(result)
                    
                    # Record success
                    execution_time = time.time() - start_time
                    self._record_success(func.__name__, execution_time, args, kwargs, result)
                    
                    return result
                    
                except Exception as e:
                    # Record failure
                    execution_time = time.time() - start_time
                    self._record_failure(func.__name__, execution_time, args, kwargs, e)
                    raise
                
            return wrapper
        return decorator
    
    def _validate_inputs(self, args, kwargs):
        """Validate function inputs."""
        for arg in args:
            if isinstance(arg, str):
                validation_result = self.validator.validate(arg)
                if not validation_result.is_safe:
                    self.sentinel.create_security_event(
                        threat_type=validation_result.threat_type,
                        severity=SeverityLevel.HIGH,
                        description=f"Input validation failed: {validation_result.violations}",
                        details={"validation_result": validation_result.__dict__}
                    )
```

### 3. MCP Wrapper

```python
def secure_mcp_method(func):
    """
    Secure MCP (Model Context Protocol) method decorator.
    
    Provides security monitoring for MCP server methods.
    
    Usage:
        @secure_mcp_method
        def tools_list(self, arguments: dict) -> dict:
            return {"tools": [...]}
    """
    @functools.wraps(func)
    def wrapper(self, arguments: dict, *args, **kwargs):
        # Create security context
        context = DetectionContext(
            agent_id=f"{self.__class__.__name__}.{func.__name__}",
            method_name=func.__name__,
            inputs=arguments,
            session_id=getattr(self, 'session_id', None)
        )
        
        # Validate inputs
        validator = InputValidator()
        for key, value in arguments.items():
            if isinstance(value, str):
                validation_result = validator.validate(value)
                if not validation_result.is_safe:
                    raise SecurityError(f"Input validation failed: {validation_result.violations}")
        
        # Execute with monitoring
        try:
            result = func(self, arguments, *args, **kwargs)
            
            # Validate outputs
            if isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, str):
                        validation_result = validator.validate(value)
                        if not validation_result.is_safe:
                            # Log security event but don't block
                            logger.warning(f"Output validation failed: {validation_result.violations}")
            
            return result
            
        except Exception as e:
            # Record security event
            logger.error(f"MCP method failed: {e}")
            raise
    
    return wrapper
```

---

## Usage Examples

### 1. Basic Function Monitoring

```python
from agent_sentinel.wrappers.decorators import monitor

@monitor
def process_user_data(data: str) -> str:
    """Process user data with security monitoring."""
    return data.upper()

# Usage
result = process_user_data("hello world")
```

### 2. Class-Based Agent Monitoring

```python
from agent_sentinel.wrappers.decorators import sentinel

@sentinel
class DataProcessingAgent:
    def __init__(self):
        self.processed_count = 0
    
    def process_data(self, data: str) -> dict:
        """Process data with automatic security monitoring."""
        self.processed_count += 1
        return {
            "processed": data.upper(),
            "count": self.processed_count
        }
    
    def analyze_data(self, data: list) -> dict:
        """Analyze data with security monitoring."""
        return {
            "analysis": "completed",
            "items": len(data)
        }

# Usage
agent = DataProcessingAgent()
result = agent.process_data("sensitive data")
```

### 3. Context Manager Usage

```python
from agent_sentinel.wrappers.decorators import monitor_agent_session

def complex_data_processing():
    with monitor_agent_session("data_processor", "batch_processing") as wrapper:
        # Your code here
        result = process_large_dataset()
        return result
```

### 4. MCP Server Integration

```python
from agent_sentinel.wrappers.decorators import secure_mcp_method

class MyMCPServer:
    @secure_mcp_method
    def tools_list(self, arguments: dict) -> dict:
        """List available tools with security monitoring."""
        return {
            "tools": [
                {"name": "tool1", "description": "Description 1"},
                {"name": "tool2", "description": "Description 2"}
            ]
        }
    
    @secure_mcp_method
    def call_tool(self, arguments: dict) -> dict:
        """Call a tool with security monitoring."""
        tool_name = arguments.get("name")
        tool_args = arguments.get("arguments", {})
        
        # Tool execution logic here
        return {"result": "success"}
```

### 5. Advanced Configuration

```python
from agent_sentinel import AgentSentinel

# Initialize with custom configuration
sentinel = AgentSentinel(
    config_dict={
        "agent_id": "my_advanced_agent",
        "environment": "production",
        "security": {
            "strict_validation": True,
            "enable_ml_detection": True,
            "threat_intelligence": True
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file_path": "/var/log/agent_sentinel.log"
        },
        "monitoring": {
            "enable_performance_tracking": True,
            "memory_threshold": 512,  # MB
            "cpu_threshold": 80  # %
        }
    }
)

# Start monitoring
sentinel.start_monitoring()

# Create custom security event
sentinel.create_security_event(
    threat_type="custom_threat",
    severity="HIGH",
    description="Custom security event",
    details={"custom_field": "value"}
)

# Get metrics
metrics = sentinel.get_metrics()
print(f"Risk Score: {metrics.risk_score}")
```

---

## Configuration

### 1. YAML Configuration

```yaml
# config.yaml
agent_id: "my_agent"
environment: "production"

security:
  strict_validation: true
  enable_ml_detection: true
  threat_intelligence: true
  input_validation:
    max_length: 10000
    block_suspicious: true
  detection:
    enable_behavioral_analysis: true
    enable_anomaly_detection: true
    sensitivity_threshold: 0.7

logging:
  level: "INFO"
  format: "json"
  file_path: "/var/log/agent_sentinel.log"
  max_file_size: "10MB"
  backup_count: 5

monitoring:
  enable_performance_tracking: true
  memory_threshold: 512  # MB
  cpu_threshold: 80  # %
  session_timeout: 3600  # seconds

reporting:
  enable_threat_reports: true
  report_format: "json"
  auto_generate: true
  retention_days: 30
```

### 2. Environment Variables

```bash
# Agent configuration
AGENT_SENTINEL_AGENT_ID=my_agent
AGENT_SENTINEL_ENVIRONMENT=production

# Security settings
AGENT_SENTINEL_STRICT_VALIDATION=true
AGENT_SENTINEL_ENABLE_ML_DETECTION=true
AGENT_SENTINEL_THREAT_INTELLIGENCE=true

# Logging
AGENT_SENTINEL_LOG_LEVEL=INFO
AGENT_SENTINEL_LOG_FORMAT=json
AGENT_SENTINEL_LOG_PATH=/var/log/agent_sentinel.log

# Monitoring
AGENT_SENTINEL_ENABLE_PERFORMANCE=true
AGENT_SENTINEL_MEMORY_THRESHOLD=512
AGENT_SENTINEL_CPU_THRESHOLD=80
```

---

## API Reference

### Core Classes

#### AgentSentinel
```python
class AgentSentinel:
    def __init__(self, config_path=None, config_dict=None, agent_id=None, environment=None)
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def create_security_event(self, threat_type, severity, description, details=None) -> None
    def get_events(self, **filters) -> List[SecurityEvent]
    def get_metrics(self) -> Dict[str, Any]
    def generate_security_report(self) -> Dict[str, Any]
    def health_check(self) -> Dict[str, Any]
```

#### SecurityEvent
```python
@dataclass
class SecurityEvent:
    id: str
    timestamp: datetime
    agent_id: str
    threat_type: ThreatType
    severity: SeverityLevel
    description: str
    details: Optional[Dict[str, Any]]
    confidence: float = 1.0
    session_id: Optional[str] = None
    user_id: Optional[str] = None
```

#### ValidationResponse
```python
@dataclass
class ValidationResponse:
    result: ValidationResult
    is_safe: bool
    confidence_score: float
    threat_type: Optional[ThreatType] = None
    violations: Optional[List[str]] = None
    sanitized_input: Optional[str] = None
    risk_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
```

### Threat Types

```python
class ThreatType(Enum):
    SCRIPT_INJECTION = "script_injection"
    SQL_INJECTION = "sql_injection"
    PROMPT_INJECTION = "prompt_injection"
    DATA_EXFILTRATION = "data_exfiltration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RATE_LIMITING = "rate_limiting"
    ANOMALY_DETECTION = "anomaly_detection"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    INPUT_OVERFLOW = "input_overflow"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
```

### Severity Levels

```python
class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

---

## Security Features

### 1. Multi-Layer Threat Detection

- **Pattern-Based Detection**: Regex patterns for known attack vectors
- **Rule-Based Detection**: Configurable security rules and thresholds
- **Behavioral Analysis**: Anomaly detection based on agent behavior
- **ML-Based Detection**: Machine learning models for threat detection
- **External Intelligence**: Integration with threat intelligence feeds

### 2. Input Validation & Sanitization

- **HTML Sanitization**: Prevent XSS attacks
- **SQL Sanitization**: Prevent SQL injection
- **Prompt Sanitization**: Prevent prompt injection
- **URL Sanitization**: Prevent URL-based attacks
- **Data Type Validation**: Ensure correct data types

### 3. Real-time Monitoring

- **Event Streaming**: Real-time security event processing
- **Performance Monitoring**: Resource usage tracking
- **Session Management**: Secure session handling
- **Audit Logging**: Comprehensive audit trails

### 4. Threat Intelligence

- **CVE Integration**: Common Vulnerabilities and Exposures
- **Threat Feeds**: Real-time threat intelligence
- **Risk Scoring**: Dynamic risk assessment
- **Recommendations**: Automated security recommendations

---

## Performance & Monitoring

### 1. Performance Metrics

```python
@dataclass
class PerformanceMetrics:
    total_events: int = 0
    security_events: int = 0
    average_response_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    success_rate: float = 1.0
    error_rate: float = 0.0
    risk_score: float = 0.0
```

### 2. Memory Management

- **Automatic Cleanup**: Background cleanup processes
- **Memory Monitoring**: Real-time memory usage tracking
- **Threshold Alerts**: Memory threshold notifications
- **Garbage Collection**: Optimized garbage collection

### 3. Thread Safety

- **Lock-Free Operations**: Minimize blocking operations
- **Concurrent Access**: Thread-safe event handling
- **Atomic Operations**: Atomic event creation and retrieval
- **Deadlock Prevention**: Careful lock ordering

### 4. Scalability

- **Horizontal Scaling**: Multiple agent instances
- **Load Distribution**: Event distribution across instances
- **Resource Pooling**: Connection and resource pooling
- **Caching**: Intelligent caching strategies

---

## Best Practices

### 1. Integration Best Practices

```python
# ✅ Good: Use decorators for simple integration
@monitor
def process_data(data: str) -> str:
    return data.upper()

# ✅ Good: Use context managers for complex operations
with monitor_agent_session("my_agent", "batch_processing") as wrapper:
    result = process_large_dataset()

# ✅ Good: Configure for production
sentinel = AgentSentinel(
    config_dict={
        "agent_id": "production_agent",
        "environment": "production",
        "security": {"strict_validation": True}
    }
)
```

### 2. Security Best Practices

```python
# ✅ Good: Validate all inputs
@monitor
def process_user_input(user_data: str) -> str:
    # Input is automatically validated by the decorator
    return process_data(user_data)

# ✅ Good: Handle security events
def handle_security_event(event: SecurityEvent):
    if event.severity == SeverityLevel.CRITICAL:
        # Immediate action required
        send_alert(event)
        block_user(event.user_id)

# ✅ Good: Regular security audits
def perform_security_audit():
    events = sentinel.get_events(
        start_time=datetime.now() - timedelta(days=7)
    )
    generate_security_report(events)
```

### 3. Performance Best Practices

```python
# ✅ Good: Monitor performance metrics
def check_performance():
    metrics = sentinel.get_metrics()
    if metrics.memory_usage_mb > 512:
        logger.warning("High memory usage detected")
    
    if metrics.risk_score > 0.8:
        logger.critical("High risk score detected")

# ✅ Good: Use appropriate log levels
import logging
logging.getLogger("agent_sentinel").setLevel(logging.INFO)

# ✅ Good: Configure retention policies
sentinel = AgentSentinel(
    config_dict={
        "logging": {
            "retention_days": 30,
            "max_file_size": "10MB"
        }
    }
)
```

### 4. Error Handling

```python
# ✅ Good: Handle validation errors
try:
    result = process_data(user_input)
except ValidationError as e:
    logger.error(f"Input validation failed: {e}")
    return {"error": "Invalid input"}

# ✅ Good: Handle security events
def process_with_security(data: str) -> str:
    try:
        return process_data(data)
    except SecurityError as e:
        sentinel.create_security_event(
            threat_type=ThreatType.SCRIPT_INJECTION,
            severity=SeverityLevel.HIGH,
            description=f"Security error: {e}"
        )
        raise
```

---

## Conclusion

The Agent Sentinel SDK provides a comprehensive, enterprise-grade security monitoring solution for AI agents. With its multi-layered threat detection, real-time monitoring, and easy integration, it offers robust protection against various security threats while maintaining high performance and scalability.

Key strengths include:
- **Easy Integration**: 2-line setup with decorators
- **Comprehensive Security**: Multi-layer threat detection
- **Performance Optimized**: Thread-safe and memory-efficient
- **Enterprise Ready**: Production-grade features and monitoring
- **Extensible**: Modular architecture for custom extensions

The SDK is designed to work seamlessly with any Python-based AI agent while providing the security features needed for production deployments.
