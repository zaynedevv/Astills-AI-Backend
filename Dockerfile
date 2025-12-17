# syntax=docker/dockerfile:1.4

FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install LibreOffice + dependencies + Python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        libreoffice-calc \
        libreoffice-impress \
        fonts-dejavu \
        fonts-liberation \
        python3 \
        python3-pip \
        python3-venv \
        wget \
        curl \
        unzip \
        ghostscript && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy your Python deps file
COPY requirements.txt .

# Install Python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose the port your FastAPI will run on
EXPOSE 8080

# Default command
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
