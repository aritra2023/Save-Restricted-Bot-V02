FROM python:3.10-slim

# Faltu packages (neofetch, software-properties-common) hata diye hain
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    bash \
    ffmpeg \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -U -r requirements.txt

COPY . .

EXPOSE 8000

CMD flask run -h 0.0.0.0 -p 8000 & python3 -m devgagan
