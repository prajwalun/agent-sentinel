#!/usr/bin/env python3
"""
Demo: send test events to the dashboard (cross-platform, including Windows).

Loads .env from project root and runs verify_stack.
Use when the shell script doesn't work (e.g. Windows).

Usage: python scripts/demo_dashboard.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def _load_env(path: Path) -> None:
    """Load KEY=VALUE from .env into os.environ (simple parser)."""
    if not path.exists():
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:].strip()
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value


def main() -> int:
    _load_env(ENV_FILE)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_stack.py")],
        cwd=str(ROOT),
        env=os.environ.copy(),
    )
    if result.returncode == 0:
        print("\nCheck http://localhost:3000 for events in the dashboard.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
