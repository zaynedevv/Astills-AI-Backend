FROM python:3.11-bullseye

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libreoffice-core libreoffice-writer libreoffice-calc \
        fonts-dejavu libxrender1 libxext6 libx11-6 ghostscript && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
