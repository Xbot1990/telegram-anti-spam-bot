FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем Python зависимости БЕЗ системных пакетов
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя без привилегий (для безопасности)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Порт для Flask веб-сервера
EXPOSE 8080

# Запускаем бота
CMD ["python", "bot.py"]
