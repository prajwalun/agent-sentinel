"""
Enterprise Logging Configuration for Agent Sentinel Intelligence Layer.

Provides structured logging with proper formatting, rotation, security filtering,
and enterprise-grade logging standards.
"""

import os
import sys
import json
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback

# Custom log levels
AUDIT_LEVEL = 25
SECURITY_LEVEL = 35

# Add custom log levels
logging.addLevelName(AUDIT_LEVEL, "AUDIT")
logging.addLevelName(SECURITY_LEVEL, "SECURITY")


class SecurityFilter(logging.Filter):
    """Filter to remove sensitive information from logs."""
    
    SENSITIVE_PATTERNS = [
        'api_key', 'token', 'password', 'secret', 'credential',
        'auth', 'bearer', 'session', 'cookie', 'jwt'
    ]
    
    def filter(self, record):
        """Filter sensitive information from log records."""
        # Check message
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            if any(pattern in message.lower() for pattern in self.SENSITIVE_PATTERNS):
                # Redact sensitive information
                for pattern in self.SENSITIVE_PATTERNS:
                    if pattern in message.lower():
                        record.msg = record.msg.replace(pattern, '[REDACTED]')
        
        # Check args
        if hasattr(record, 'args') and record.args:
            filtered_args = []
            for arg in record.args:
                if isinstance(arg, str) and any(pattern in arg.lower() for pattern in self.SENSITIVE_PATTERNS):
                    filtered_args.append('[REDACTED]')
                else:
                    filtered_args.append(arg)
            record.args = tuple(filtered_args)
        
        return True


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for enterprise logging."""
    
    def __init__(self, include_extra=True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record):
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': record.process,
            'thread_id': record.thread,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                              'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process', 'message']:
                    extra_fields[key] = value
            
            if extra_fields:
                log_entry['extra'] = extra_fields
        
        return json.dumps(log_entry, default=str)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for development and debugging."""
    
    def __init__(self):
        super().__init__()
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def format(self, record):
        """Format log record for human readability."""
        return self.formatter.format(record)


class LoggingConfig:
    """Enterprise logging configuration manager."""
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_dir: str = "logs",
        app_name: str = "agent-sentinel-intelligence",
        structured_logging: bool = True,
        enable_security_filter: bool = True,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 10,
        enable_audit_log: bool = True,
        enable_security_log: bool = True
    ):
        """
        Initialize logging configuration.
        
        Args:
            log_level: Default logging level
            log_dir: Directory for log files
            app_name: Application name for log files
            structured_logging: Enable structured JSON logging
            enable_security_filter: Enable security filtering
            max_file_size: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            enable_audit_log: Enable separate audit log
            enable_security_log: Enable separate security log
        """
        self.log_level = log_level.upper()
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.structured_logging = structured_logging
        self.enable_security_filter = enable_security_filter
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_audit_log = enable_audit_log
        self.enable_security_log = enable_security_log
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup console handler
        self._setup_console_handler(root_logger)
        
        # Setup file handlers
        self._setup_file_handlers(root_logger)
        
        # Setup audit log if enabled
        if self.enable_audit_log:
            self._setup_audit_log()
        
        # Setup security log if enabled
        if self.enable_security_log:
            self._setup_security_log()
    
    def _setup_console_handler(self, logger):
        """Setup console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        
        # Use human-readable format for console
        console_formatter = HumanReadableFormatter()
        console_handler.setFormatter(console_formatter)
        
        # Add security filter if enabled
        if self.enable_security_filter:
            console_handler.addFilter(SecurityFilter())
        
        logger.addHandler(console_handler)
    
    def _setup_file_handlers(self, logger):
        """Setup file logging handlers."""
        # Main application log
        app_log_file = self.log_dir / f"{self.app_name}.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(getattr(logging, self.log_level))
        
        # Choose formatter based on configuration
        if self.structured_logging:
            app_formatter = StructuredFormatter()
        else:
            app_formatter = HumanReadableFormatter()
        
        app_handler.setFormatter(app_formatter)
        
        # Add security filter if enabled
        if self.enable_security_filter:
            app_handler.addFilter(SecurityFilter())
        
        logger.addHandler(app_handler)
        
        # Error log (ERROR and above)
        error_log_file = self.log_dir / f"{self.app_name}_error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(app_formatter)
        
        if self.enable_security_filter:
            error_handler.addFilter(SecurityFilter())
        
        logger.addHandler(error_handler)
    
    def _setup_audit_log(self):
        """Setup audit logging."""
        audit_logger = logging.getLogger('audit')
        audit_logger.setLevel(AUDIT_LEVEL)
        
        # Audit log file
        audit_log_file = self.log_dir / f"{self.app_name}_audit.log"
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        audit_handler.setLevel(AUDIT_LEVEL)
        
        # Always use structured format for audit logs
        audit_formatter = StructuredFormatter()
        audit_handler.setFormatter(audit_formatter)
        
        # Don't filter audit logs for security information
        audit_logger.addHandler(audit_handler)
        audit_logger.propagate = False  # Don't propagate to root logger
    
    def _setup_security_log(self):
        """Setup security logging."""
        security_logger = logging.getLogger('security')
        security_logger.setLevel(SECURITY_LEVEL)
        
        # Security log file
        security_log_file = self.log_dir / f"{self.app_name}_security.log"
        security_handler = logging.handlers.RotatingFileHandler(
            security_log_file,
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        security_handler.setLevel(SECURITY_LEVEL)
        
        # Always use structured format for security logs
        security_formatter = StructuredFormatter()
        security_handler.setFormatter(security_formatter)
        
        # Don't filter security logs
        security_logger.addHandler(security_handler)
        security_logger.propagate = False  # Don't propagate to root logger
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)
    
    @staticmethod
    def audit_log(message: str, **kwargs):
        """Log an audit event."""
        audit_logger = logging.getLogger('audit')
        audit_logger.log(AUDIT_LEVEL, message, extra=kwargs)
    
    @staticmethod
    def security_log(message: str, **kwargs):
        """Log a security event."""
        security_logger = logging.getLogger('security')
        security_logger.log(SECURITY_LEVEL, message, extra=kwargs)


class ContextualLogger:
    """Logger with contextual information."""
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize contextual logger.
        
        Args:
            name: Logger name
            context: Additional context to include in all log messages
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _log_with_context(self, level: int, message: str, *args, **kwargs):
        """Log message with context."""
        # Merge context with any extra kwargs
        extra = kwargs.get('extra', {})
        extra.update(self.context)
        kwargs['extra'] = extra
        
        self.logger.log(level, message, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, *args, **kwargs)
    
    def audit(self, message: str, **kwargs):
        """Log audit message with context."""
        merged_kwargs = {**self.context, **kwargs}
        LoggingConfig.audit_log(message, **merged_kwargs)
    
    def security(self, message: str, **kwargs):
        """Log security message with context."""
        merged_kwargs = {**self.context, **kwargs}
        LoggingConfig.security_log(message, **merged_kwargs)


def setup_enterprise_logging(
    log_level: str = None,
    log_dir: str = None,
    structured: bool = None
) -> LoggingConfig:
    """
    Setup enterprise logging with environment variable support.
    
    Args:
        log_level: Log level (overrides environment)
        log_dir: Log directory (overrides environment)
        structured: Enable structured logging (overrides environment)
        
    Returns:
        Configured LoggingConfig instance
    """
    # Get configuration from environment variables
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    log_dir = log_dir or os.getenv('LOG_DIR', 'logs')
    structured = structured if structured is not None else os.getenv('STRUCTURED_LOGGING', 'true').lower() == 'true'
    
    # Additional configuration from environment
    max_file_size = int(os.getenv('LOG_MAX_FILE_SIZE', 10 * 1024 * 1024))
    backup_count = int(os.getenv('LOG_BACKUP_COUNT', 10))
    enable_security_filter = os.getenv('LOG_SECURITY_FILTER', 'true').lower() == 'true'
    
    config = LoggingConfig(
        log_level=log_level,
        log_dir=log_dir,
        structured_logging=structured,
        enable_security_filter=enable_security_filter,
        max_file_size=max_file_size,
        backup_count=backup_count
    )
    
    return config


def get_contextual_logger(name: str, **context) -> ContextualLogger:
    """
    Get a contextual logger with additional context.
    
    Args:
        name: Logger name
        **context: Additional context to include in all log messages
        
    Returns:
        ContextualLogger instance
    """
    return ContextualLogger(name, context) 