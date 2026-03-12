"""
Input validation and sanitization utilities.
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    # Security patterns
    MALICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',               # JavaScript URLs
        r'vbscript:',                # VBScript URLs
        r'on\w+\s*=',               # Event handlers
        r'expression\s*\(',         # CSS expressions
        r'@import',                 # CSS imports
        r'<iframe[^>]*>',           # Iframes
        r'<object[^>]*>',           # Objects
        r'<embed[^>]*>',            # Embeds
        r'<link[^>]*>',             # Links
        r'<meta[^>]*>',             # Meta tags
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
        r'(--|#|/\*|\*/)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)',
        r'(\bUNION\s+SELECT)',
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$(){}[\]<>]',
        r'\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|wget|curl)\b',
        r'\b(rm|mv|cp|mkdir|rmdir|chmod|chown|kill|killall)\b',
        r'\b(sudo|su|passwd|crontab|at|batch)\b',
    ]
    
    @staticmethod
    def validate_string(
        value: Any,
        min_length: int = 0,
        max_length: int = 10000,
        allow_empty: bool = True,
        sanitize: bool = True
    ) -> str:
        """
        Validate and sanitize string input.
        
        Args:
            value: Input value to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            allow_empty: Whether to allow empty strings
            sanitize: Whether to sanitize the input
            
        Returns:
            Validated and sanitized string
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            if allow_empty:
                return ""
            raise ValidationError("String value cannot be None")
        
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception as e:
                raise ValidationError(f"Cannot convert value to string: {e}")
        
        # Check length
        if len(value) < min_length:
            raise ValidationError(f"String too short (minimum {min_length} characters)")
        
        if len(value) > max_length:
            raise ValidationError(f"String too long (maximum {max_length} characters)")
        
        # Sanitize if requested
        if sanitize:
            value = InputValidator.sanitize_string(value)
        
        return value
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize string input by removing/escaping dangerous content.
        
        Args:
            value: String to sanitize
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # HTML encode
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        value = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        return value
    
    @staticmethod
    def check_malicious_content(value: str) -> List[str]:
        """
        Check for malicious content patterns.
        
        Args:
            value: String to check
            
        Returns:
            List of detected malicious patterns
        """
        detected_patterns = []
        
        if not isinstance(value, str):
            return detected_patterns
        
        value_lower = value.lower()
        
        # Check for XSS patterns
        for pattern in InputValidator.MALICIOUS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                detected_patterns.append(f"XSS: {pattern}")
        
        # Check for SQL injection patterns
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                detected_patterns.append(f"SQL_INJECTION: {pattern}")
        
        # Check for command injection patterns
        for pattern in InputValidator.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                detected_patterns.append(f"COMMAND_INJECTION: {pattern}")
        
        return detected_patterns
    
    @staticmethod
    def validate_file_path(
        path: Union[str, Path],
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        allowed_extensions: Optional[List[str]] = None
    ) -> Path:
        """
        Validate file path input.
        
        Args:
            path: Path to validate
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If validation fails
        """
        if not path:
            raise ValidationError("Path cannot be empty")
        
        try:
            path_obj = Path(path)
        except Exception as e:
            raise ValidationError(f"Invalid path format: {e}")
        
        # Check for path traversal
        if '..' in str(path_obj):
            raise ValidationError("Path traversal detected")
        
        # Check if path exists
        if must_exist and not path_obj.exists():
            raise ValidationError(f"Path does not exist: {path_obj}")
        
        # Check if it's a file
        if must_be_file and path_obj.exists() and not path_obj.is_file():
            raise ValidationError(f"Path is not a file: {path_obj}")
        
        # Check if it's a directory
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            raise ValidationError(f"Path is not a directory: {path_obj}")
        
        # Check file extension
        if allowed_extensions and path_obj.suffix.lower() not in allowed_extensions:
            raise ValidationError(f"File extension not allowed: {path_obj.suffix}")
        
        return path_obj
    
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Validate URL input.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If validation fails
        """
        if not url:
            raise ValidationError("URL cannot be empty")
        
        if not isinstance(url, str):
            raise ValidationError("URL must be a string")
        
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise ValidationError(f"Invalid URL format: {e}")
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError(f"Invalid URL scheme: {parsed.scheme}")
        
        # Check for malicious patterns
        malicious_patterns = InputValidator.check_malicious_content(url)
        if malicious_patterns:
            raise ValidationError(f"Malicious content detected in URL: {malicious_patterns}")
        
        return url
    
    @staticmethod
    def validate_json_data(
        data: Any,
        max_depth: int = 10,
        max_keys: int = 1000,
        max_string_length: int = 10000
    ) -> Any:
        """
        Validate JSON data structure.
        
        Args:
            data: Data to validate
            max_depth: Maximum nesting depth
            max_keys: Maximum number of keys
            max_string_length: Maximum string length
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        def _validate_recursive(obj, depth=0):
            if depth > max_depth:
                raise ValidationError(f"JSON depth exceeds maximum: {max_depth}")
            
            if isinstance(obj, dict):
                if len(obj) > max_keys:
                    raise ValidationError(f"JSON object has too many keys: {len(obj)}")
                
                for key, value in obj.items():
                    if not isinstance(key, str):
                        raise ValidationError(f"JSON key must be string: {type(key)}")
                    
                    if len(key) > max_string_length:
                        raise ValidationError(f"JSON key too long: {len(key)}")
                    
                    _validate_recursive(value, depth + 1)
            
            elif isinstance(obj, list):
                if len(obj) > max_keys:
                    raise ValidationError(f"JSON array too large: {len(obj)}")
                
                for item in obj:
                    _validate_recursive(item, depth + 1)
            
            elif isinstance(obj, str):
                if len(obj) > max_string_length:
                    raise ValidationError(f"JSON string too long: {len(obj)}")
                
                # Check for malicious content
                malicious_patterns = InputValidator.check_malicious_content(obj)
                if malicious_patterns:
                    logger.warning(f"Malicious content detected in JSON: {malicious_patterns}")
        
        _validate_recursive(data)
        return data
    
    @staticmethod
    def validate_api_key(api_key: str) -> str:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Validated API key
            
        Raises:
            ValidationError: If validation fails
        """
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        if not isinstance(api_key, str):
            raise ValidationError("API key must be a string")
        
        # Remove whitespace
        api_key = api_key.strip()
        
        # Check length (most API keys are 20-100 characters)
        if len(api_key) < 10:
            raise ValidationError("API key too short")
        
        if len(api_key) > 200:
            raise ValidationError("API key too long")
        
        # Check for suspicious characters
        if re.search(r'[<>"\'\s]', api_key):
            raise ValidationError("API key contains invalid characters")
        
        return api_key
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email address format.
        
        Args:
            email: Email to validate
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: If validation fails
        """
        if not email:
            raise ValidationError("Email cannot be empty")
        
        if not isinstance(email, str):
            raise ValidationError("Email must be a string")
        
        # Basic email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        # Check for malicious content
        malicious_patterns = InputValidator.check_malicious_content(email)
        if malicious_patterns:
            raise ValidationError(f"Malicious content detected in email: {malicious_patterns}")
        
        return email.lower()


class SecurityValidator:
    """Advanced security validation utilities."""
    
    @staticmethod
    def validate_report_content(content: str) -> Dict[str, Any]:
        """
        Validate security report content.
        
        Args:
            content: Report content to validate
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'issues': [],
            'sanitized_content': content,
            'size_bytes': len(content.encode('utf-8')),
            'malicious_patterns': []
        }
        
        try:
            # Validate as string
            content = InputValidator.validate_string(
                content,
                min_length=10,
                max_length=1000000,  # 1MB limit
                sanitize=False  # Don't sanitize report content
            )
            
            # Check for malicious patterns
            malicious_patterns = InputValidator.check_malicious_content(content)
            if malicious_patterns:
                results['malicious_patterns'] = malicious_patterns
                results['issues'].append("Malicious content patterns detected")
            
            # Check content size
            if results['size_bytes'] > 10 * 1024 * 1024:  # 10MB
                results['valid'] = False
                results['issues'].append("Content too large")
            
        except ValidationError as e:
            results['valid'] = False
            results['issues'].append(str(e))
        
        return results
    
    @staticmethod
    def validate_workflow_state(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow state object.
        
        Args:
            state: Workflow state to validate
            
        Returns:
            Validation results
        """
        results = {
            'valid': True,
            'issues': [],
            'sanitized_state': state.copy() if isinstance(state, dict) else {}
        }
        
        try:
            if not isinstance(state, dict):
                results['valid'] = False
                results['issues'].append("State must be a dictionary")
                return results
            
            # Validate JSON structure
            InputValidator.validate_json_data(
                state,
                max_depth=5,
                max_keys=100,
                max_string_length=100000
            )
            
            # Validate required fields
            if 'messages' not in state:
                results['issues'].append("Missing 'messages' field")
            
            # Validate phase field
            if 'phase' in state:
                valid_phases = ['analyzer', 'researcher', 'reporter', 'validator', 'completed']
                if state['phase'] not in valid_phases:
                    results['issues'].append(f"Invalid phase: {state['phase']}")
            
        except ValidationError as e:
            results['valid'] = False
            results['issues'].append(str(e))
        
        return results 