# Multi-stage build for CB Agent System
# Builder - Install dependencies and Codex CLI
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/codex.tar.gz \
    "https://github.com/openai/codex/releases/latest/download/codex-aarch64-unknown-linux-gnu.tar.gz" \
    && tar -xzf /tmp/codex.tar.gz -C /tmp \
    && mv /tmp/codex-aarch64-unknown-linux-gnu /usr/local/bin/codex \
    && chmod +x /usr/local/bin/codex \
    && rm /tmp/codex.tar.gz \
    && codex --version

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

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/bin/codex /usr/local/bin/codex
COPY --from=builder /root/.local /home/appuser/.local

RUN useradd -m -u 1000 appuser \
    && mkdir -p /home/appuser/.codex /app \
    && chown -R appuser:appuser /home/appuser /app

WORKDIR /app

COPY --chown=appuser:appuser src/ /app/src/

COPY --chown=appuser:appuser docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER appuser

ENV PATH="/home/appuser/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    REPO_PATH=/workspace/repo

VOLUME ["/workspace/repo"]

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python", "-m", "src.main"]
