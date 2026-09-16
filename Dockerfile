FROM python:3.10-slim

# System dependencies install
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    bash \
    neofetch \
    ffmpeg \
    python3-pip \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements file copy karke python packages install karein
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -U -r requirements.txt

# Baaki saara code copy karein
COPY . .

EXPOSE 8000

CMD flask run -h 0.0.0.0 -p 8000 & python3 -m devgagan
