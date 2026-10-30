# Multi-stage Dockerfile for NEXUS-CORE
FROM python:3.11-slim AS runtime
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core-engine/ ./core-engine/
COPY validators/ ./validators/
COPY identity-zkp/ ./identity-zkp/
COPY scripts/ ./scripts/
COPY smart-contracts/ ./smart-contracts/

# Create non-root user
RUN useradd -m -u 1000 nexus && chown -R nexus:nexus /app
USER nexus

ENV PYTHONUNBUFFERED=1
ENV NEXUS_ENV=production

EXPOSE 8080

CMD ["python3", "-m", "core-engine.serve"]
