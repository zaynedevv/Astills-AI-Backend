FROM python:3.11-bullseye

WORKDIR /app

# Install LibreOffice and dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-core libreoffice-writer libreoffice-calc \
        fonts-dejavu libxrender1 libxext6 libx11-6 ghostscript && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Install Java separately ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-11-jre-headless && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for LibreOffice to detect
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
