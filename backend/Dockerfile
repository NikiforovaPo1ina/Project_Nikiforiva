FROM python:3.10-slim

# Устанавливаем ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем backend (исправленный путь!)
COPY backend ./backend

# Создаём папку для результатов
RUN mkdir -p results

EXPOSE 8000

# Используем PORT от Railway или 8000 по умолчанию
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]