"""
Tracing Service for Agent Sentinel Intelligence Layer.

Provides tracing and monitoring capabilities using Weave and Weights & Biases.
"""

import os
import logging
from typing import Optional, Dict, Any, ContextManager
from contextlib import contextmanager

from models.config import TracingConfig

logger = logging.getLogger(__name__)

# Try to import weave and wandb at module level
try:
    import weave
    WEAVE_AVAILABLE = True
except ImportError:
    WEAVE_AVAILABLE = False
    logger.warning("⚠️  Weave not available - tracing will be disabled")

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    logger.warning("⚠️  W&B not available - some features will be disabled")


class TracingService:
    """Service for tracing and monitoring."""
    
    def __init__(self, config: TracingConfig):
        """
        Initialize the tracing service.
        
        Args:
            config: Tracing configuration
        """
        self.config = config
        self.weave_client = None
        self.wandb = None
        
        if config.enabled and WEAVE_AVAILABLE:
            self._initialize_tracing()
    
    def _initialize_tracing(self):
        """Initialize tracing providers."""
        if self.config.provider in ["weave", "wandb"] and WEAVE_AVAILABLE:
            try:
                # Initialize W&B if API key is provided
                if WANDB_AVAILABLE:
                    wandb_api_key = os.getenv("WANDB_API_KEY")
                    if wandb_api_key:
                        wandb.login(key=wandb_api_key)
                        logger.info("✅ W&B login successful")
                        self.wandb = wandb
                
                # Initialize Weave client
                self.weave_client = weave.init(self.config.project_name)
                
                logger.info(f"✅ Tracing initialized with project: {self.config.project_name}")
                
            except Exception as e:
                logger.warning(f"⚠️  Tracing initialization failed: {e}")
                self.weave_client = None
                self.wandb = None
    
    @contextmanager
    def trace(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Create a trace context manager.
        
        Args:
            name: Trace name
            metadata: Optional metadata for the trace
            
        Yields:
            Trace context (None if tracing disabled)
        """
        if not self.weave_client or not WEAVE_AVAILABLE:
            yield None
            return
        
        try:
            # Use weave.op decorator approach for tracing
            @weave.op(name=name)
            def trace_operation():
                return {"status": "traced", "metadata": metadata or {}}
            
            # Execute the traced operation
            result = trace_operation()
            yield result
            
        except Exception as e:
            logger.warning(f"⚠️  Tracing failed for {name}: {e}")
            yield None
    
    def log_event(self, event_name: str, metadata: Dict[str, Any]):
        """
        Log an event to the tracing system.
        
        Args:
            event_name: Name of the event
            metadata: Event metadata
        """
        if not self.weave_client or not WEAVE_AVAILABLE:
            return
        
        try:
            @weave.op(name=f"event_{event_name}")
            def log_event_operation():
                return {
                    "event": event_name,
                    "timestamp": metadata.get("timestamp"),
                    "data": metadata
                }
            
            # Execute the logged event
            log_event_operation()
            
        except Exception as e:
            logger.warning(f"⚠️  Event logging failed for {event_name}: {e}")
    
    def log_llm_call(
        self, 
        node_name: str, 
        input_length: int, 
        output_length: int, 
        status: str = "completed"
    ):
        """
        Log an LLM call to the tracing system.
        
        Args:
            node_name: Name of the node making the call
            input_length: Length of input
            output_length: Length of output
            status: Status of the call
        """
        metadata = {
            "node": node_name,
            "input_length": input_length,
            "output_length": output_length,
            "status": status
        }
        
        self.log_event(f"llm_call_{node_name}", metadata)
    
    def log_workflow_step(
        self, 
        step_name: str, 
        content_length: int, 
        status: str = "completed"
    ):
        """
        Log a workflow step to the tracing system.
        
        Args:
            step_name: Name of the workflow step
            content_length: Length of content processed
            status: Status of the step
        """
        metadata = {
            "step": step_name,
            "content_length": content_length,
            "status": status
        }
        
        self.log_event(f"workflow_step_{step_name}", metadata)
    
    def is_enabled(self) -> bool:
        """Check if tracing is enabled."""
        return self.weave_client is not None and WEAVE_AVAILABLE 