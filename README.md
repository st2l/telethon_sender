# Инструкция по запуску проекта

## 1. Подготовка проекта

1. Создайте файл `.env` в корневой директории проекта со следующими переменными:
```plaintext
POSTGRES_DB=your_db_name
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=postgres_template
POSTGRES_PORT=5432

TELEGRAM_TOKEN=your_telegram_bot_token

DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your_secret_key
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=your_admin_password


TELEGRAM_API_ID=your_api_id  # from my.telegram.org
TELEGRAM_API_HASH=your_api_hash
```

## 2. Изменение docker-compose.yml

⚠️ **Важно**: Во избежание конфликтов с другими проектами, измените:

1. Название сервиса PostgreSQL (сейчас `postgres_template`)
2. Название сервиса веб-приложения (сейчас `web`)
3. Название volume (сейчас `postgres_data_template`)

Например:
```yaml
services:
  postgres_myproject:  # Измененное название
    ...
  
  web_myproject:      # Измененное название
    ...

volumes:
  postgres_data_myproject:  # Измененное название
```

## 3. Запуск проекта

1. Соберите и запустите контейнеры:
```bash
docker-compose up --build
```

2. После успешного запуска:
- Django админ-панель будет доступна по адресу: `http://localhost:8000/admin`
- Telegram бот начнет работу автоматически

## 4. Дополнительные команды

- Остановка контейнеров:
```bash
docker-compose down
```

- Просмотр логов:
```bash
docker-compose logs -f
```

## Проверка работоспособности

1. Откройте админ-панель Django (`http://localhost:8000/admin`) и войдите используя credentials из `.env`:
   - Username: `DJANGO_SUPERUSER_USERNAME`
   - Password: `DJANGO_SUPERUSER_PASSWORD`

2. Найдите вашего бота в Telegram и отправьте команду `/start`

## Возможные проблемы

1. Если порт 5432 или 8000 уже занят, измените маппинг портов в `docker-compose.yml`
2. Убедитесь, что все переменные в `.env` заполнены корректно
3. Проверьте валидность токена Telegram бота
