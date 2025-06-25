FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN mkdir -p ./pkgs/core/src
RUN mkdir -p ./src/eunomia

COPY pyproject.toml README.md uv.lock ./
COPY pkgs/core/pyproject.toml pkgs/core/README.md ./pkgs/core
COPY pkgs/core/src/eunomia_core ./pkgs/core/src/eunomia_core

RUN uv sync --frozen --no-dev --package eunomia-ai

COPY src/eunomia ./src/eunomia

RUN chown -R appuser:appuser /app

ENV UV_NO_CACHE=1

USER appuser

EXPOSE 8000
ENV PORT=8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["uv", "run", "--no-dev", "eunomia", "server", "--host", "0.0.0.0", "--port", "${PORT}"]
