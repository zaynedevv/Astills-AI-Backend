# Start from LibreOffice prebuilt image
FROM libreoffice/office:7.6.7.2

# Set working directory
WORKDIR /app

# Install Python + pip (if not included)
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your FastAPI app code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8080

# Start FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
