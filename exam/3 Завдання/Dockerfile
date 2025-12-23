FROM python:3.9-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо програму
COPY 2_haniuk.py .

# Копіюємо requirements.txt
COPY requirements.txt .

# Встановлюємо залежності Python
RUN pip install --no-cache-dir -r requirements.txt

# Запускаємо програму
CMD ["python", "2_haniuk.py"]