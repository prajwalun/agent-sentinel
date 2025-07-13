"""
Configuration models for the Agent Sentinel Intelligence Layer.
"""

import os
import logging
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    
    provider: Literal["openai", "google", "auto"] = Field(
        default="auto",
        description="LLM provider to use (auto will try OpenAI first, then Google)"
    )
    
    model: str = Field(
        default="gemini-1.5-flash",
        description="Model name to use"
    )
    
    temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM responses"
    )
    
    max_tokens: Optional[int] = Field(
        default=4096,
        ge=1,
        le=32768,
        description="Maximum tokens for responses"
    )
    
    timeout: int = Field(
        default=60,
        ge=5,
        le=300,
        description="Request timeout in seconds"
    )
    
    max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts"
    )
    
    @validator('model')
    def validate_model(cls, v, values):
        """Validate model name based on provider."""
        provider = values.get('provider', 'auto')
        
        # OpenAI models
        openai_models = [
            'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o', 'gpt-4o-mini'
        ]
        
        # Google models
        google_models = [
            'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-pro-vision'
        ]
        
        if provider == 'openai' and v not in openai_models:
            logger.warning(f"⚠️  Model '{v}' may not be valid for OpenAI")
        elif provider == 'google' and v not in google_models:
            logger.warning(f"⚠️  Model '{v}' may not be valid for Google")
        
        return v


class TracingConfig(BaseModel):
    """Configuration for tracing and monitoring."""
    
    enabled: bool = Field(
        default=True,
        description="Enable tracing and monitoring"
    )
    
    provider: Literal["weave", "wandb", "none"] = Field(
        default="weave",
        description="Tracing provider to use"
    )
    
    project_name: str = Field(
        default="agent-sentinel-intelligence",
        min_length=1,
        max_length=100,
        description="Project name for tracing"
    )
    
    capture_code: bool = Field(
        default=True,
        description="Capture code in traces"
    )
    
    capture_system_info: bool = Field(
        default=True,
        description="Capture system information"
    )
    
    @validator('project_name')
    def validate_project_name(cls, v):
        """Validate project name format."""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Project name must contain only alphanumeric characters, hyphens, and underscores")
        return v


class ResearchConfig(BaseModel):
    """Configuration for web research capabilities."""
    
    enabled: bool = Field(
        default=True,
        description="Enable web research capabilities"
    )
    
    max_research_queries: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of research queries per analysis"
    )
    
    research_timeout: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Timeout for research queries in seconds"
    )
    
    max_results_per_query: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum results per research query"
    )
    
    enable_caching: bool = Field(
        default=True,
        description="Enable caching of research results"
    )


class OutputConfig(BaseModel):
    """Configuration for output generation."""
    
    generate_text: bool = Field(
        default=True,
        description="Generate text report"
    )
    
    generate_pdf: bool = Field(
        default=True,
        description="Generate PDF report"
    )
    
    generate_json: bool = Field(
        default=True,
        description="Generate JSON report"
    )
    
    output_directory: Path = Field(
        default=Path("./reports"),
        description="Directory for output files"
    )
    
    max_report_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        ge=1024,
        description="Maximum report size in bytes"
    )
    
    @validator('output_directory')
    def validate_output_directory(cls, v):
        """Validate and create output directory."""
        try:
            v.mkdir(parents=True, exist_ok=True)
            if not v.is_dir():
                raise ValueError(f"Output directory path exists but is not a directory: {v}")
            if not os.access(v, os.W_OK):
                raise ValueError(f"Output directory is not writable: {v}")
        except Exception as e:
            logger.error(f"❌ Output directory validation failed: {e}")
            raise ValueError(f"Invalid output directory: {e}")
        return v


class SecurityConfig(BaseModel):
    """Configuration for security settings."""
    
    sanitize_inputs: bool = Field(
        default=True,
        description="Sanitize input data"
    )
    
    max_input_size: int = Field(
        default=1024 * 1024,  # 1MB
        ge=1024,
        description="Maximum input size in bytes"
    )
    
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    
    max_requests_per_minute: int = Field(
        default=60,
        ge=1,
        le=1000,
        description="Maximum requests per minute"
    )
    
    allowed_domains: Optional[list] = Field(
        default=None,
        description="List of allowed domains for research"
    )


class IntelligenceConfig(BaseModel):
    """Main configuration for the intelligence layer."""
    
    llm: LLMConfig = Field(
        default_factory=LLMConfig,
        description="LLM configuration"
    )
    
    tracing: TracingConfig = Field(
        default_factory=TracingConfig,
        description="Tracing configuration"
    )
    
    research: ResearchConfig = Field(
        default_factory=ResearchConfig,
        description="Research configuration"
    )
    
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="Output configuration"
    )
    
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )
    
    # Environment variables
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key"
    )
    
    exa_api_key: Optional[str] = Field(
        default=None,
        description="Exa.ai API key"
    )
    
    wandb_api_key: Optional[str] = Field(
        default=None,
        description="Weights & Biases API key"
    )
    
    @root_validator(skip_on_failure=True)
    def validate_config(cls, values):
        """Validate the entire configuration."""
        # Check for required API keys based on enabled features
        llm_config = values.get('llm', {})
        tracing_config = values.get('tracing', {})
        research_config = values.get('research', {})
        
        provider = llm_config.get('provider', 'auto') if isinstance(llm_config, dict) else getattr(llm_config, 'provider', 'auto')
        
        # Validate LLM provider keys
        if provider == 'openai' and not values.get('openai_api_key'):
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                logger.warning("⚠️  OpenAI provider selected but no API key provided")
            else:
                values['openai_api_key'] = openai_key
        
        if provider == 'google' and not values.get('google_api_key'):
            google_key = os.getenv('GOOGLE_API_KEY')
            if not google_key:
                logger.warning("⚠️  Google provider selected but no API key provided")
            else:
                values['google_api_key'] = google_key
        
        # Auto-detect available providers
        if provider == 'auto':
            if not values.get('openai_api_key'):
                values['openai_api_key'] = os.getenv('OPENAI_API_KEY')
            if not values.get('google_api_key'):
                values['google_api_key'] = os.getenv('GOOGLE_API_KEY')
        
        # Validate tracing keys
        tracing_provider = tracing_config.get('provider', 'weave') if isinstance(tracing_config, dict) else getattr(tracing_config, 'provider', 'weave')
        if tracing_provider in ['weave', 'wandb'] and not values.get('wandb_api_key'):
            wandb_key = os.getenv('WANDB_API_KEY')
            if wandb_key:
                values['wandb_api_key'] = wandb_key
        
        # Validate research keys
        research_enabled = research_config.get('enabled', True) if isinstance(research_config, dict) else getattr(research_config, 'enabled', True)
        if research_enabled and not values.get('exa_api_key'):
            exa_key = os.getenv('EXA_API_KEY')
            if exa_key:
                values['exa_api_key'] = exa_key
        
        return values
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate the environment and return status."""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'available_providers': []
        }
        
        # Check LLM providers
        if self.openai_api_key:
            status['available_providers'].append('openai')
        else:
            status['warnings'].append('OpenAI API key not available')
        
        if self.google_api_key:
            status['available_providers'].append('google')
        else:
            status['warnings'].append('Google API key not available')
        
        if not status['available_providers']:
            status['valid'] = False
            status['errors'].append('No LLM provider API keys available')
        
        # Check optional services
        if self.research.enabled and not self.exa_api_key:
            status['warnings'].append('Research enabled but Exa API key not available')
        
        if self.tracing.enabled and self.tracing.provider in ['weave', 'wandb'] and not self.wandb_api_key:
            status['warnings'].append('Tracing enabled but W&B API key not available')
        
        # Check output directory
        try:
            self.output.output_directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            status['errors'].append(f'Output directory error: {e}')
            status['valid'] = False
        
        return status
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True 