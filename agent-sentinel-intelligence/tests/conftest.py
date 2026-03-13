"""
Pytest configuration for Agent Sentinel Intelligence backend tests.

Suppresses Pydantic dependency warnings for a cleaner experience.
"""
import warnings

warnings.filterwarnings("ignore", module="pydantic._internal._generate_schema")
