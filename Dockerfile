# Use Python 3.11 slim as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies: LibreOffice for conversion, fonts, and basic tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-core \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
        libreoffice-common \
        libreoffice-java-common \
        fonts-dejavu \
        fonts-liberation \
        wget \
        unzip \
        curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set default command (replace with your actual entry point if different)
CMD ["python", "main.py"]
