# DataWhisperer - Production Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for uvx / npx based MCP servers)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install uv (for uvx to run mcp-server-sqlite)
RUN pip install uv

# Pre-install mcp-server-sqlite so uvx doesn't need to download at runtime
RUN uvx --from mcp-server-sqlite mcp-server-sqlite --help || true

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Seed the database at build time
RUN python setup/seed_db.py

# Set environment variables
ENV PORT=8080
ENV DB_PATH=/app/data/ecommerce.db
ENV PYTHONPATH=/app

# Run the FastAPI server
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
