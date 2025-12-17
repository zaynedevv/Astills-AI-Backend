# Use a prebuilt headless LibreOffice image
FROM libreoffice/libreoffice:headless

# Set working directory
WORKDIR /app

# Install Python 3.11 and pip
RUN apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt .
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose port
EXPOSE 8080

# Start your FastAPI / uvicorn app
CMD ["python3.11", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
