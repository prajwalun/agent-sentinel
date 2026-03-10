"""
Decorators for Agent Sentinel

Public decorator API for monitoring AI agents, multi-agent systems, and MCP servers.
Supports both bare-decorator and parameterized usage:

    @monitor
    def my_func(query): ...

    @monitor(agent_id="my_agent", validate_inputs=True)
    def my_func(query): ...

    @sentinel
    class MyAgent: ...

    @sentinel(agent_id="prod_agent", enable_threat_reports=True)
    class MyAgent: ...
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator, Optional, Type

from .agent_wrapper import AgentWrapper
from ..logging.structured_logger import SecurityLogger


def monitor(
    _func: Optional[Callable] = None,
    *,
    agent_id: Optional[str] = None,
    validate_inputs: bool = True,
    validate_outputs: bool = False,
    enable_separate_logs: bool = True,
    enable_threat_reports: bool = True,
    strict_validation: bool = False,
):
    """
    Decorator to monitor an individual function or method for security threats.

    Supports both bare and parameterized usage:

        @monitor
        def process(query: str): ...

        @monitor(agent_id="search_agent", validate_inputs=True)
        def process(query: str): ...

    Args:
        agent_id: Identifier for this agent (defaults to module.function_name).
        validate_inputs: Run security validation on all call arguments.
        validate_outputs: Run security validation on return values.
        enable_separate_logs: Write a dedicated log file per agent.
        enable_threat_reports: Generate JSON threat reports on events.
        strict_validation: Block on suspicious inputs (not just critical).
    """
    def decorator(func: Callable) -> Callable:
        aid = agent_id or f"{func.__module__}.{func.__qualname__}"
        wrapper_instance = AgentWrapper(
            agent_id=aid,
            enable_input_validation=validate_inputs,
            strict_validation=strict_validation,
            enable_behavior_analysis=True,
            enable_performance_monitoring=True,
            enable_separate_logs=enable_separate_logs,
            enable_threat_reports=enable_threat_reports,
        )
        return wrapper_instance.monitor(
            validate_inputs=validate_inputs,
            validate_outputs=validate_outputs,
        )(func)

    # Support both @monitor and @monitor(...)
    if _func is not None:
        return decorator(_func)
    return decorator


def sentinel(
    _cls: Optional[Type] = None,
    *,
    agent_id: Optional[str] = None,
    enable_separate_logs: bool = True,
    enable_threat_reports: bool = True,
    log_format: str = "json",
    report_format: str = "json",
    strict_validation: bool = False,
):
    """
    Class decorator that applies security monitoring to all public methods.

    Supports both bare and parameterized usage:

        @sentinel
        class MyAgent: ...

        @sentinel(agent_id="prod_agent", enable_threat_reports=True)
        class MyAgent: ...

    Args:
        agent_id: Identifier for this agent (defaults to the class name).
        enable_separate_logs: Write a dedicated log file per agent.
        enable_threat_reports: Generate JSON threat reports on events.
        log_format: Log file format — "json", "text", or "csv".
        report_format: Report file format — "json" or "html".
        strict_validation: Block on suspicious inputs (not just critical).
    """
    def decorator(cls: Type) -> Type:
        aid = agent_id or cls.__name__
        wrapper_instance = AgentWrapper(
            agent_id=aid,
            enable_input_validation=True,
            strict_validation=strict_validation,
            enable_behavior_analysis=True,
            enable_performance_monitoring=True,
            enable_separate_logs=enable_separate_logs,
            enable_threat_reports=enable_threat_reports,
            log_format=log_format,
            report_format=report_format,
        )

        # Wrap every public, callable method on the class
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue
            attr = getattr(cls, attr_name, None)
            if callable(attr):
                wrapped = wrapper_instance.monitor()(attr)
                setattr(cls, attr_name, wrapped)

        setattr(cls, "_agent_wrapper", wrapper_instance)
        return cls

    # Support both @sentinel and @sentinel(...)
    if _cls is not None:
        return decorator(_cls)
    return decorator


@contextmanager
def monitor_agent_session(
    agent_id: str,
    session_name: Optional[str] = None,
    logger: Optional[SecurityLogger] = None,
) -> Generator[AgentWrapper, None, None]:
    """
    Context manager for monitoring a block of code as a named agent session.

    Usage:
        with monitor_agent_session("data_agent", "ingestion_run") as wrapper:
            result = process_data(inputs)
            events = wrapper.get_agent_stats()
    """
    wrapper = AgentWrapper(
        agent_id=agent_id,
        logger=logger,
        enable_input_validation=True,
        strict_validation=False,
        enable_separate_logs=True,
        enable_threat_reports=True,
    )

    with wrapper.monitor_session(session_name) as session_id:
        setattr(wrapper, "current_session_id", session_id)
        try:
            yield wrapper
        finally:
            # Ensure any pending reports are flushed
            try:
                wrapper.shutdown()
            except Exception:
                pass


class SecurityContext:
    """
    Context manager for scoped security monitoring of any code block.

    Usage:
        with SecurityContext("mcp_agent") as wrapper:
            tool_result = call_mcp_tool(params)
    """

    def __init__(
        self,
        agent_id: str,
        strict_validation: bool = False,
        enable_input_validation: bool = True,
        enable_performance_monitoring: bool = True,
        enable_threat_reports: bool = True,
        logger: Optional[SecurityLogger] = None,
    ):
        self.agent_id = agent_id
        self.strict_validation = strict_validation
        self.enable_input_validation = enable_input_validation
        self.enable_performance_monitoring = enable_performance_monitoring
        self.enable_threat_reports = enable_threat_reports
        self.logger = logger
        self.wrapper: Optional[AgentWrapper] = None

    def __enter__(self) -> AgentWrapper:
        self.wrapper = AgentWrapper(
            agent_id=self.agent_id,
            logger=self.logger,
            enable_input_validation=self.enable_input_validation,
            strict_validation=self.strict_validation,
            enable_performance_monitoring=self.enable_performance_monitoring,
            enable_threat_reports=self.enable_threat_reports,
        )
        return self.wrapper

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.wrapper:
            try:
                self.wrapper.shutdown()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Inspection helpers
# ---------------------------------------------------------------------------

def get_agent_wrapper(obj: Any) -> Optional[AgentWrapper]:
    """Return the AgentWrapper attached to a sentinel-decorated class, or None."""
    return getattr(obj, "_agent_wrapper", None)


def is_secured(obj: Any) -> bool:
    """Return True if the object has been decorated with @sentinel."""
    return hasattr(obj, "_agent_wrapper")


def get_security_stats(obj: Any) -> Optional[dict]:
    """Return security statistics for a sentinel-decorated object, or None."""
    wrapper = get_agent_wrapper(obj)
    return wrapper.get_agent_stats() if wrapper else None
