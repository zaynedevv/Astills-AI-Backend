# syntax=docker/dockerfile:1.4
ARG BUILDKIT_INLINE_CACHE=0

FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install LibreOffice headless + fonts + other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-core \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
        libreoffice-common \
        libreoffice-java-common \
        libreoffice-help-en \
        fonts-dejavu \
        fonts-liberation \
        wget \
        unzip \
        curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (optional for clarity)
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
