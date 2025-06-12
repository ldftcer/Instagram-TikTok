FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir aiogram==3.0.0 \
    && pip install --no-cache-dir yt-dlp==2023.0.0 \
    && pip install --no-cache-dir python-dotenv==1.0.0 \
    && pip install --no-cache-dir aiohttp==3.8.0 \
    && pip install --no-cache-dir asyncio==3.4.3 \
    && pip install --no-cache-dir psutil==5.9.0 \
    && pip install --no-cache-dir aiofiles==23.1.0

COPY . .

RUN mkdir -p data downloads logs

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
