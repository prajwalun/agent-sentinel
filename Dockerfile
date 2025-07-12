# Multi-stage Dockerfile for Sentinel
# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e ".[monitoring,security]"

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    SENTINEL_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r sentinel && useradd -r -g sentinel sentinel

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY src/ ./src/
COPY README.md ./
COPY LICENSE ./

# Create necessary directories
RUN mkdir -p /app/logs /app/config /app/data \
    && chown -R sentinel:sentinel /app

# Switch to non-root user
USER sentinel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose ports
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.agent_sentinel.cli", "monitor", "--config", "config.yaml"]

# Development stage
FROM python:3.11-slim as development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    SENTINEL_ENV=development

# Install development dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install development dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e ".[dev,test,docs,monitoring,security]"

# Create application directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/config /app/data /app/tests

# Expose ports
EXPOSE 8000

# Default command for development
CMD ["python", "-m", "src.agent_sentinel.cli", "monitor", "--config", "config.yaml"] 