FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY uv.lock ./
COPY taskflow/ ./taskflow/
COPY run_service.py ./
COPY README.md ./

# Install uv for fast dependency installation
RUN pip install --no-cache-dir uv

# Install dependencies
RUN uv pip install --system -e .

# Create logs directory
RUN mkdir -p /app/logs

# Expose ports (Streamlit uses 8501)
EXPOSE 8501

# Default command (can be overridden in docker-compose)
CMD ["python", "run_service.py", "all"]
