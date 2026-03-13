#!/usr/bin/env bash
#
# Reset the Agent Sentinel stack: stop containers and remove volumes.
# This deletes the database (users, events, agents, API keys) — fresh start.
#
# Usage:
#   ./scripts/reset_stack.sh
#   ./scripts/reset_stack.sh --start   # reset and start again
#

set -e

cd "$(dirname "$0")/.."

COMPOSE="docker compose"
if ! docker compose version &>/dev/null; then
  COMPOSE="docker-compose"
fi

echo "Stopping containers and removing volumes..."
$COMPOSE down -v

if [[ "${1:-}" == "--start" ]]; then
  echo "Starting fresh stack..."
  $COMPOSE up --build -d
  echo "Backend: http://localhost:8001"
  echo "Dashboard: http://localhost:3000"
  echo "Sign up again and add SENTINEL_API_KEY to .env"
fi

echo "Done. Database reset."
