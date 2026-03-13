#!/usr/bin/env bash
#
# Demo: send test events to the dashboard.
# Run after docker-compose up and signup. Loads .env and runs verify_stack.
#
# Usage: ./scripts/demo_with_dashboard.sh
#

set -e

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

python scripts/verify_stack.py
echo ""
echo "Check http://localhost:3000 for events in the dashboard."
