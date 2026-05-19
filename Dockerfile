FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for healthcheck + sqlite CLI (handy for ops)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts
COPY data ./data

RUN pip install --upgrade pip \
    && pip install .

# /data is the mounted Fly volume; SQLite file lives there
ENV DATABASE_URL=sqlite:////data/app.db \
    ALLOWED_ORIGINS=http://localhost:5173 \
    PORT=8080 \
    LOG_LEVEL=INFO \
    LOG_SQL=false

VOLUME ["/data"]

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:${PORT:-8080}/ || exit 1

# `--no-access-log` disables uvicorn's built-in per-request line so we
# don't double-log; our RequestContextMiddleware emits a structured JSON
# line for every request with method, path, status, duration_ms, and
# request_id.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --no-access-log"]
