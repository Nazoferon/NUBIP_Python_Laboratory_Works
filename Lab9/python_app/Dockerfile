# Використовуємо стабільну версію Python
FROM python:3.11-slim

WORKDIR /app

# Встановлюємо залежності для системи (якщо потрібно) і оновлюємо pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо файл вимог і встановлюємо бібліотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код програми
COPY . .

# Запуск програми без буферизації виводу (щоб бачити логи відразу)
CMD ["python", "-u", "app.py"]