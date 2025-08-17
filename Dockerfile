# Multi-stage Dockerfile for memU MCP Server

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

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy installed packages and application from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src

# Create directories for configuration and logs
RUN mkdir -p /app/config /app/logs && \
    chown -R appuser:appuser /app

# Copy configuration files
COPY config/example.json /app/config/
COPY .env.example /app/

# Switch to non-root user
USER appuser

# Expose port (if needed for future HTTP transport)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "memu_mcp_server.main"]

# Development stage
FROM production as development

# Switch back to root for development tools installation
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy development files
COPY tests/ /app/tests/
COPY examples/ /app/examples/
COPY Makefile /app/
COPY pyproject.toml /app/

# Install development Python packages
RUN pip install pytest pytest-asyncio pytest-cov black flake8 mypy

# Switch back to app user
USER appuser

# Override command for development
CMD ["python", "-m", "memu_mcp_server.main", "--log-level", "DEBUG"]