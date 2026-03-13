"""
Pytest configuration for Agent Sentinel SDK tests.

Disables console logging during tests to keep output clean.
Suppresses Pydantic dependency warnings for a cleaner experience.
"""
import os
import warnings

os.environ.setdefault("AGENT_SENTINEL_CONSOLE", "false")
warnings.filterwarnings("ignore", module="pydantic._internal._generate_schema")
