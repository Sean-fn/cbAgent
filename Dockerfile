# Multi-stage build for PM Component Query System
# Stage 1: Builder - Install dependencies and Codex CLI
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Codex CLI from OpenAI GitHub releases
RUN curl -L -o /tmp/codex.tar.gz \
    "https://github.com/openai/codex/releases/latest/download/codex-aarch64-unknown-linux-gnu.tar.gz" \
    && tar -xzf /tmp/codex.tar.gz -C /tmp \
    && mv /tmp/codex-aarch64-unknown-linux-gnu /usr/local/bin/codex \
    && chmod +x /usr/local/bin/codex \
    && rm /tmp/codex.tar.gz \
    && codex --version

# Install Python dependencies
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user \
    openai>=1.50.0 \
    python-dotenv>=1.0.0 \
    aiofiles>=24.0.0 \
    prompt-toolkit>=3.0.0 \
    rich>=13.0.0 \
    gitpython>=3.1.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy Codex CLI from builder
COPY --from=builder /usr/local/bin/codex /usr/local/bin/codex

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Create non-root user for security
RUN useradd -m -u 1000 appuser \
    && mkdir -p /home/appuser/.codex /app/codex_logs \
    && chown -R appuser:appuser /home/appuser /app

# Set working directory
WORKDIR /app

# Copy application source code
COPY --chown=appuser:appuser src/ /app/src/

# Copy entrypoint script
COPY --chown=appuser:appuser docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Switch to non-root user
USER appuser

# Configure environment
ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    PYTHONUNBUFFERED=1 \
    REPO_PATH=/workspace/repo \
    CODEX_LOGS_DIR=/app/codex_logs

# Define volumes
VOLUME ["/workspace/repo", "/app/codex_logs"]

# Set entrypoint and default command
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "-m", "src.main"]
