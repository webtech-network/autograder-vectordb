FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Trust Zscaler corporate proxy CA
COPY zscaler-ca.crt /usr/local/share/ca-certificates/zscaler-ca.crt
RUN update-ca-certificates
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev

# --- Runtime stage ---
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install runtime system deps (ca-certificates for HTTPS, poppler/tesseract for PDF OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Trust Zscaler corporate proxy CA
COPY zscaler-ca.crt /usr/local/share/ca-certificates/zscaler-ca.crt
RUN update-ca-certificates

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Append Zscaler CA to certifi's bundle (used by httpx/upstash-vector)
RUN cat /usr/local/share/ca-certificates/zscaler-ca.crt >> $(find /app/.venv -path "*/certifi/cacert.pem" | head -1)

COPY pyproject.toml uv.lock /app/
COPY app /app/app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
