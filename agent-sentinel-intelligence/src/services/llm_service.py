"""
LLM Service for Agent Sentinel Intelligence Layer.

Provides a unified interface for LLM interactions with support for multiple
providers, retry logic, rate limiting, and proper error handling.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Union
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import BaseOutputParser

from models.config import LLMConfig

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if a request can be made within rate limits."""
        now = time.time()
        # Remove old requests outside the window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.window_seconds]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a new request."""
        self.requests.append(time.time())
    
    def wait_time(self) -> float:
        """Get the time to wait before next request."""
        if not self.requests:
            return 0.0
        oldest_request = min(self.requests)
        return max(0.0, self.window_seconds - (time.time() - oldest_request))


class LLMService:
    """Service for managing LLM interactions."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM service.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.primary_llm = None
        self.fallback_llm = None
        self.rate_limiter = RateLimiter()
        self.request_count = 0
        self.error_count = 0
        
        # Initialize LLMs
        self._initialize_llms()
        
    def _initialize_llms(self):
        """Initialize OpenAI LLM only."""
        self.primary_llm = self._try_initialize_openai()
        self.fallback_llm = None
        
        if not self.primary_llm:
            raise RuntimeError("Failed to initialize OpenAI LLM - check OPENAI_API_KEY environment variable")
    
    def _try_initialize_openai(self) -> Optional[BaseChatModel]:
        """Try to initialize OpenAI LLM."""
        try:
            from langchain_openai import ChatOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("⚠️  OPENAI_API_KEY not found in environment")
                return None
            
            # Use OpenAI model names for OpenAI provider
            model_name = self.config.model
            # If the model is a Google model, map to OpenAI equivalent
            if "gemini" in model_name.lower():
                model_name = "gpt-4o-mini"
            elif self.config.provider == "google":
                # Map to appropriate OpenAI model
                model_name = "gpt-4o-mini"
            
            llm = ChatOpenAI(
                model=model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries,
                api_key=api_key
            )
            
            # Test the connection
            test_messages = [SystemMessage(content="Test")]
            llm.invoke(test_messages)
            
            logger.info(f"✅ Initialized OpenAI LLM with model: {model_name}")
            return llm
            
        except Exception as e:
            logger.warning(f"⚠️  OpenAI initialization failed: {e}")
            return None
    

    
    def invoke(
        self, 
        messages: List[BaseMessage], 
        **kwargs
    ) -> str:
        """
        Invoke the LLM with messages and retry logic.
        
        Args:
            messages: List of messages to send to LLM
            **kwargs: Additional arguments for LLM invocation
            
        Returns:
            LLM response content
            
        Raises:
            Exception: If LLM invocation fails after all retries
        """
        # Validate input
        if not messages:
            raise ValueError("No messages provided for LLM invocation")
        
        # Check rate limiting
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"⚠️  Rate limit reached, waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
        
        # Try primary LLM first
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                self.rate_limiter.record_request()
                self.request_count += 1
                
                response = self.primary_llm.invoke(messages, **kwargs)
                
                if not response or not response.content:
                    raise ValueError("Empty response from LLM")
                
                return response.content
                
            except Exception as e:
                last_error = e
                self.error_count += 1
                logger.warning(f"⚠️  Primary LLM attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    # Exponential backoff
                    wait_time = min(2 ** attempt, 30)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Try fallback LLM if available
        if self.fallback_llm:
            logger.info("🔄 Trying fallback LLM...")
            for attempt in range(self.config.max_retries):
                try:
                    self.rate_limiter.record_request()
                    self.request_count += 1
                    
                    response = self.fallback_llm.invoke(messages, **kwargs)
                    
                    if not response or not response.content:
                        raise ValueError("Empty response from fallback LLM")
                    
                    logger.info("✅ Fallback LLM succeeded")
                    return response.content
                    
                except Exception as e:
                    last_error = e
                    self.error_count += 1
                    logger.warning(f"⚠️  Fallback LLM attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.config.max_retries - 1:
                        wait_time = min(2 ** attempt, 30)
                        logger.info(f"Retrying fallback in {wait_time} seconds...")
                        time.sleep(wait_time)
        
        # All attempts failed
        logger.error(f"❌ All LLM invocation attempts failed. Last error: {last_error}")
        raise Exception(f"LLM invocation failed after all retries: {last_error}")
    
    def invoke_structured(
        self,
        messages: List[BaseMessage],
        output_parser: BaseOutputParser,
        **kwargs
    ) -> Any:
        """
        Invoke the LLM with structured output parsing.
        
        Args:
            messages: List of messages to send to LLM
            output_parser: Parser for structured output
            **kwargs: Additional arguments for LLM invocation
            
        Returns:
            Parsed structured output
            
        Raises:
            Exception: If LLM invocation or parsing fails
        """
        # Validate input
        if not messages:
            raise ValueError("No messages provided for structured LLM invocation")
        if not output_parser:
            raise ValueError("No output parser provided")
        
        # Check rate limiting
        if not self.rate_limiter.can_make_request():
            wait_time = self.rate_limiter.wait_time()
            logger.warning(f"⚠️  Rate limit reached, waiting {wait_time:.1f} seconds")
            time.sleep(wait_time)
        
        # Try primary LLM first
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                self.rate_limiter.record_request()
                self.request_count += 1
                
                llm_with_parser = self.primary_llm.with_structured_output(output_parser)
                response = llm_with_parser.invoke(messages, **kwargs)
                
                if response is None:
                    raise ValueError("Empty structured response from LLM")
                
                return response
                
            except Exception as e:
                last_error = e
                self.error_count += 1
                logger.warning(f"⚠️  Primary LLM structured attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries - 1:
                    wait_time = min(2 ** attempt, 30)
                    logger.info(f"Retrying structured in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # Try fallback LLM if available
        if self.fallback_llm:
            logger.info("🔄 Trying fallback LLM for structured output...")
            for attempt in range(self.config.max_retries):
                try:
                    self.rate_limiter.record_request()
                    self.request_count += 1
                    
                    llm_with_parser = self.fallback_llm.with_structured_output(output_parser)
                    response = llm_with_parser.invoke(messages, **kwargs)
                    
                    if response is None:
                        raise ValueError("Empty structured response from fallback LLM")
                    
                    logger.info("✅ Fallback LLM structured succeeded")
                    return response
                    
                except Exception as e:
                    last_error = e
                    self.error_count += 1
                    logger.warning(f"⚠️  Fallback LLM structured attempt {attempt + 1} failed: {e}")
                    
                    if attempt < self.config.max_retries - 1:
                        wait_time = min(2 ** attempt, 30)
                        logger.info(f"Retrying fallback structured in {wait_time} seconds...")
                        time.sleep(wait_time)
        
        # All attempts failed
        logger.error(f"❌ All structured LLM invocation attempts failed. Last error: {last_error}")
        raise Exception(f"Structured LLM invocation failed after all retries: {last_error}")
    
    def create_system_message(self, content: str) -> SystemMessage:
        """Create a system message with validation."""
        if not content or not isinstance(content, str):
            raise ValueError("System message content must be a non-empty string")
        return SystemMessage(content=content.strip())
    
    def create_user_message(self, content: str) -> HumanMessage:
        """Create a user message with validation."""
        if not content or not isinstance(content, str):
            raise ValueError("User message content must be a non-empty string")
        return HumanMessage(content=content.strip())
    
    def create_messages(
        self, 
        system_prompt: str, 
        user_prompt: str
    ) -> List[BaseMessage]:
        """
        Create a list of messages with system and user prompts.
        
        Args:
            system_prompt: System prompt content
            user_prompt: User prompt content
            
        Returns:
            List of messages
        """
        if not system_prompt or not isinstance(system_prompt, str):
            raise ValueError("System prompt must be a non-empty string")
        if not user_prompt or not isinstance(user_prompt, str):
            raise ValueError("User prompt must be a non-empty string")
        
        return [
            self.create_system_message(system_prompt),
            self.create_user_message(user_prompt)
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "has_primary": self.primary_llm is not None,
            "has_fallback": self.fallback_llm is not None,
            "provider": self.config.provider,
            "model": self.config.model
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the LLM service."""
        status = {
            "healthy": True,
            "primary_available": False,
            "fallback_available": False,
            "errors": []
        }
        
        # Test primary LLM
        if self.primary_llm:
            try:
                test_messages = [SystemMessage(content="Health check")]
                self.primary_llm.invoke(test_messages)
                status["primary_available"] = True
            except Exception as e:
                status["errors"].append(f"Primary LLM failed: {e}")
        
        # Test fallback LLM
        if self.fallback_llm:
            try:
                test_messages = [SystemMessage(content="Health check")]
                self.fallback_llm.invoke(test_messages)
                status["fallback_available"] = True
            except Exception as e:
                status["errors"].append(f"Fallback LLM failed: {e}")
        
        # Overall health
        status["healthy"] = status["primary_available"] or status["fallback_available"]
        
        return status 