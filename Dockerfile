# syntax=docker/dockerfile:1.4

ARG BUILDKIT_INLINE_CACHE=0

FROM python:3.11-slim

WORKDIR /app



COPY requirements.txt .


# Install dependencies for LibreOffice
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        fonts-dejavu \
        fonts-liberation \
        default-jre \
        libx11-6 \
        libglib2.0-0 \
        wget \
        unzip \
        curl \
        python3-pip \
        xz-utils \
        ghostscript && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
