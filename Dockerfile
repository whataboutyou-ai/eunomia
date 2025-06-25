# Stage 1: Builder (with uv image)
FROM ghcr.io/astral-sh/uv:0.6.3-python3.13-bookworm-slim AS builder
WORKDIR /app

# Create a non-root user and group for security.
RUN groupadd --system appuser && useradd --system -g appuser appuser

COPY pyproject.toml README.md uv.lock ./
COPY pkgs/core/pyproject.toml pkgs/core/README.md ./pkgs/core/

# Set venv location.
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"
ENV PATH="/app/.venv/bin:$PATH"

# Install all workspace dependencies.
RUN uv sync --frozen --no-dev

# Copy all source code.
COPY src/eunomia ./eunomia
COPY pkgs/core/src/eunomia_core ./eunomia_core


# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app

# Install curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create the appuser and appgroup in the runtime stage
RUN groupadd --system appuser && useradd --system -g appuser appuser

# Copy the virtual environment and the application code from the builder stage.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Adjust permissions for the non-root user.
RUN chown -R appuser:appuser /app

# Set venv location.
ENV PATH="/app/.venv/bin:$PATH"

# Switch to the non-root user for running the application.
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "eunomia.api:app", "--host", "0.0.0.0", "--port", "8000"]
