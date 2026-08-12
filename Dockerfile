FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Create a non-privileged user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -m -s /bin/false appuser

# 2. Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application code and set ownership to appuser
COPY --chown=appuser:appgroup . .

# 4. Switch to the unprivileged user context
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]