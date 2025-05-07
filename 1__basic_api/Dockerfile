FROM python:3.11-slim

COPY . /app
WORKDIR /app

# Install uv
RUN pip install uv
RUN uv venv && uv sync --no-cache
ENV PATH="app/.venv/bin:$PATH"

EXPOSE 8080

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]