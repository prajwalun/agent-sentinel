# Agent Sentinel SDK — Dockerfile
#
# This image installs the SDK as a library and runs the CLI monitor.
# The SDK is a library, not a server, so no port is exposed.
#
# Build:   docker build -t agent-sentinel-sdk .
# Run:     docker run --env-file .env agent-sentinel-sdk
# Dev:     docker build --target development -t agent-sentinel-sdk-dev .

# ---------------------------------------------------------------------------
# Builder stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --upgrade pip setuptools wheel && pip install -e "."

# ---------------------------------------------------------------------------
# Production stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    AGENT_SENTINEL_ENV=production

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security
RUN groupadd -r agent-sentinel && useradd -r -g agent-sentinel agent-sentinel

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app
COPY src/ ./src/
COPY README.md LICENSE ./

RUN mkdir -p /app/logs /app/config /app/reports \
    && chown -R agent-sentinel:agent-sentinel /app

USER agent-sentinel

# CLI entry point — run `agent-sentinel monitor` to start watching
CMD ["agent-sentinel", "monitor"]

# ---------------------------------------------------------------------------
# Development stage
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGENT_SENTINEL_ENV=development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --upgrade pip setuptools wheel && pip install -e ".[dev,test,docs]"

WORKDIR /app
COPY . .
RUN mkdir -p /app/logs /app/config /app/reports /app/tests

CMD ["agent-sentinel", "monitor"]
