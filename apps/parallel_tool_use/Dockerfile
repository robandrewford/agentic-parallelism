# Multi-stage Dockerfile for App 01: Parallel Tool Use

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy shared modules and app requirements
COPY shared/ /build/shared/
COPY setup.py /build/
COPY apps/parallel_tool_use/requirements.txt /build/app-requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r /build/app-requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY shared/ /app/shared/
COPY setup.py /app/
COPY apps/parallel_tool_use/ /app/apps/parallel_tool_use/

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# Run the application
CMD ["python", "-m", "uvicorn", "apps.parallel_tool_use.app:app", "--host", "0.0.0.0", "--port", "8000"]
