FROM python:3.11-bullseye

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libreoffice libreoffice-writer libreoffice-calc fonts-dejavu && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]