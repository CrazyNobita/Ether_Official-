FROM python:3.11-slim

# Install uv
RUN pip install --no-cache-dir uv

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# System packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy project files
COPY . .

# Create folders
RUN mkdir -p /app/media /app/sessions /app/logs

# Expose Render port
EXPOSE 10000

# Start app
CMD ["python3", "main.py"]
