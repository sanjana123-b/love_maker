# -------------------------------------------------------------
# LoveMatch — Multi-Stage Production Dockerfile
# Python 3.12 · Non-root user · Daphne ASGI · Static compilation
# -------------------------------------------------------------

# Stage 1: Build Dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Production Image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/loveuser/.local/bin:$PATH \
    DJANGO_SETTINGS_MODULE=lovematch.settings

# Install runtime libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create secure non-root user
RUN useradd -m -u 1000 loveuser && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R loveuser:loveuser /app

# Copy python dependencies from builder
COPY --from=builder --chown=loveuser:loveuser /root/.local /home/loveuser/.local

# Copy application source code
COPY --chown=loveuser:loveuser . .

USER loveuser

# Expose HTTP/WebSocket ASGI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Launch Daphne ASGI Server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "lovematch.asgi:application"]
