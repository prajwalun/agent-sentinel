"""
Configuration models for the Agent Sentinel Intelligence Layer.

All models use Pydantic v2 APIs (field_validator, model_validator).
"""

import os
import logging
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["openai", "google", "auto"] = Field(
        default="auto",
        description="LLM provider — auto tries OpenAI first, then Google",
    )
    model: str = Field(
        default="gemini-1.5-flash",
        description="Model identifier",
    )
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=4096, ge=1, le=32768)
    timeout: int = Field(default=60, ge=5, le=300, description="Seconds")
    max_retries: int = Field(default=3, ge=1, le=10)

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str, info) -> str:
        provider = info.data.get("provider", "auto")
        openai_models = {"gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"}
        google_models = {"gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "gemini-pro-vision"}

        if provider == "openai" and v not in openai_models:
            logger.warning("Model '%s' may not be valid for OpenAI", v)
        elif provider == "google" and v not in google_models:
            logger.warning("Model '%s' may not be valid for Google", v)

        return v


class TracingConfig(BaseModel):
    """W&B Weave / tracing configuration."""

    enabled: bool = True
    provider: Literal["weave", "wandb", "none"] = "weave"
    project_name: str = Field(
        default="agent-sentinel-intelligence", min_length=1, max_length=100,
    )
    capture_code: bool = True
    capture_system_info: bool = True

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError(
                "Project name must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v


class ResearchConfig(BaseModel):
    """Exa web-research configuration."""

    enabled: bool = True
    max_research_queries: int = Field(default=5, ge=1, le=20)
    research_timeout: int = Field(default=30, ge=5, le=120, description="Seconds")
    max_results_per_query: int = Field(default=5, ge=1, le=20)
    enable_caching: bool = True


class OutputConfig(BaseModel):
    """Report output configuration."""

    generate_text: bool = True
    generate_pdf: bool = True
    generate_json: bool = True
    output_directory: Path = Field(default=Path("./reports"))
    max_report_size: int = Field(default=10 * 1024 * 1024, ge=1024)

    @field_validator("output_directory")
    @classmethod
    def validate_output_directory(cls, v: Path) -> Path:
        try:
            v.mkdir(parents=True, exist_ok=True)
            if not v.is_dir():
                raise ValueError(f"Path exists but is not a directory: {v}")
            if not os.access(v, os.W_OK):
                raise ValueError(f"Directory is not writable: {v}")
        except OSError as exc:
            raise ValueError(f"Invalid output directory: {exc}") from exc
        return v


class SecurityConfig(BaseModel):
    """Security / rate-limiting configuration."""

    sanitize_inputs: bool = True
    max_input_size: int = Field(default=1024 * 1024, ge=1024)
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = Field(default=60, ge=1, le=1000)
    allowed_domains: Optional[list] = None


class IntelligenceConfig(BaseModel):
    """Root configuration — aggregates all sub-configs."""

    llm: LLMConfig = Field(default_factory=LLMConfig)
    tracing: TracingConfig = Field(default_factory=TracingConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    exa_api_key: Optional[str] = None
    wandb_api_key: Optional[str] = None

    @model_validator(mode="after")
    def resolve_env_keys(self) -> "IntelligenceConfig":
        """Fill API keys from environment when not provided explicitly.

        Use object.__setattr__ to avoid triggering Pydantic's validate_assignment
        which would re-invoke this validator and cause infinite recursion.
        """
        if not self.openai_api_key:
            object.__setattr__(self, "openai_api_key", os.getenv("OPENAI_API_KEY"))
        if not self.google_api_key:
            object.__setattr__(self, "google_api_key", os.getenv("GOOGLE_API_KEY"))
        if not self.exa_api_key:
            object.__setattr__(self, "exa_api_key", os.getenv("EXA_API_KEY"))
        if not self.wandb_api_key:
            object.__setattr__(self, "wandb_api_key", os.getenv("WANDB_API_KEY"))

        if self.llm.provider == "openai" and not self.openai_api_key:
            logger.warning("OpenAI provider selected but OPENAI_API_KEY is not set")
        if self.llm.provider == "google" and not self.google_api_key:
            logger.warning("Google provider selected but GOOGLE_API_KEY is not set")

        return self

    def validate_environment(self) -> Dict[str, Any]:
        """Check environment readiness and return a diagnostic dict."""
        status: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "available_providers": [],
        }

        if self.openai_api_key:
            status["available_providers"].append("openai")
        else:
            status["warnings"].append("OpenAI API key not available")

        if self.google_api_key:
            status["available_providers"].append("google")
        else:
            status["warnings"].append("Google API key not available")

        if not status["available_providers"]:
            status["valid"] = False
            status["errors"].append("No LLM provider API keys available")

        if self.research.enabled and not self.exa_api_key:
            status["warnings"].append("Research enabled but EXA_API_KEY not set")

        if self.tracing.enabled and self.tracing.provider in ("weave", "wandb") and not self.wandb_api_key:
            status["warnings"].append("Tracing enabled but WANDB_API_KEY not set")

        return status

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "validate_assignment": True,
    }
