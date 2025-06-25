# Stage 1: Builder (with uv image)
FROM ghcr.io/astral-sh/uv:0.6.3-python3.13-alpine AS builder
WORKDIR /app

# Create a non-root user and group for security
RUN addgroup -S appuser && adduser -S -G appuser appuser

COPY pyproject.toml README.md uv.lock ./
COPY pkgs/core/pyproject.toml pkgs/core/README.md ./pkgs/core/

ENV UV_PROJECT_ENVIRONMENT="/app/.venv"
ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen --no-dev

COPY src/eunomia ./eunomia
COPY pkgs/core/src/eunomia_core ./eunomia_core


# Stage 2: Runtime
FROM python:3.13-alpine
WORKDIR /app

# Create a non-root user and group for security
RUN addgroup -S appuser && adduser -S -G appuser appuser

# Copy the venv and code from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/eunomia /app/eunomia
COPY --from=builder /app/eunomia_core /app/eunomia_core

# Switch to the non-root user for running the application
RUN chown -R appuser:appuser /app
USER appuser

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

HEALTHCHECK --interval=60s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "eunomia.api:app", "--host", "0.0.0.0", "--port", "8000"]
