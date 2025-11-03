FROM python:3.11-slim

WORKDIR /app

# Install uv with specific version for stability
RUN pip install --no-cache-dir uv==0.4.18

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies without dev dependencies
RUN uv sync --no-dev

# Copy source code
COPY . .

EXPOSE 8000

# Default command (API server)
CMD ["uv", "run", "uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000"]