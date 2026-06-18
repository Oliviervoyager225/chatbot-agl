FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "backend.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
