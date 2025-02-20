FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Делаем entrypoint.sh исполняемым и устанавливаем правильные права доступа
RUN chmod +x entrypoint.sh && \
    dos2unix entrypoint.sh

# Запуск entrypoint
ENTRYPOINT ["./entrypoint.sh"] 