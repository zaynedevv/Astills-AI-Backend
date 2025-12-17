# Use headless LibreOffice as the base
FROM lcrea/libreoffice-headless:latest

# Set working directory
WORKDIR /app

# Install Python 3.11 and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.11 python3-pip python3.11-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose app port for Fly.io
EXPOSE 8080

# Start server
CMD ["python3.11", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
