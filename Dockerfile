# syntax=docker/dockerfile:1.4
ARG BUILDKIT_INLINE_CACHE=0

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install LibreOffice + dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port and start server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
