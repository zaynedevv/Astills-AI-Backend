# syntax=docker/dockerfile:1.4

ARG BUILDKIT_INLINE_CACHE=0

FROM python:3.11-slim-bullseye

WORKDIR /app



COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-core \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libreoffice-common \
    libreoffice-headless \
    libreoffice-java-common \
    fonts-dejavu \
    fonts-liberation \
    libsm6 libxrender1 libxext6 \
    wget unzip curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
