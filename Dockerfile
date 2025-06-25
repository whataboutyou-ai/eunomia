# Stage 1: Builder (with uv image)
FROM ghcr.io/astral-sh/uv:0.6.3-python3.13-alpine AS builder
WORKDIR /app

# Create a non-root user and group for security.
RUN apk add --no-cache shadow
RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY pyproject.toml README.md uv.lock ./
COPY pkgs/core/pyproject.toml pkgs/core/README.md pkgs/core/

# Explicitly set the location for the uv virtual environment.
ENV UV_PROJECT_ENVIRONMENT="/app/.venv"

# Add the virtual environment's bin directory to the PATH for the builder stage.
ENV PATH="/app/.venv/bin:$PATH"

# Install all workspace dependencies.
RUN uv sync --frozen --no-dev

# Copy all source code.
COPY src/eunomia ./src/eunomia
COPY pkgs/core/src/eunomia_core ./pkgs/core/src/eunomia_core


# Stage 2: Runtime
FROM python:3.13-slim
WORKDIR /app

# Create the appuser and appgroup in the runtime stage
RUN groupadd --system appuser && useradd --system -g appuser appuser

# Copy the virtual environment and the application code from the builder stage.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

# Adjust permissions for the non-root user.
RUN chown -R appuser:appuser /app

# Set the PATH to include the virtual environment's bin directory in the runtime environment.
ENV PATH="/app/.venv/bin:$PATH"

# Switch to the non-root user for running the application.
USER appuser

# Set a default for the PORT environment variable.
ENV PORT=8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["/bin/sh", "-c", "uvicorn eunomia.api:app --host 0.0.0.0 --port ${PORT}"]
