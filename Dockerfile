# syntax=docker/dockerfile:1.4

ARG BUILDKIT_INLINE_CACHE=0

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install LibreOffice headless and dependencies
RUN apt-get update && \
    apt-get install -y libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress \
    libreoffice-common libreoffice-java-common libreoffice-help-en \
    python3-pip wget unzip curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Optional: Install fonts for better DOCX rendering
RUN apt-get update && \
    apt-get install -y fonts-dejavu fonts-liberation && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
