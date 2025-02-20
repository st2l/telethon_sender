#!/bin/bash

# Ждем, пока база данных будет готова
echo "Waiting for postgres..."

# Применяем миграции
python manage.py makemigrations
python manage.py migrate

# Создаем суперпользователя
python manage.py shell << END
from django.contrib.auth.models import User
try:
    User.objects.get(username='${DJANGO_SUPERUSER_USERNAME}')
    print('Superuser already exists')
except User.DoesNotExist:
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', 
                                '${DJANGO_SUPERUSER_EMAIL}', 
                                '${DJANGO_SUPERUSER_PASSWORD}')
    print('Superuser created successfully')
END

# Запускаем сервер
python manage.py runserver 0.0.0.0:8000 &

# Запускаем бота
python manage.py runbot 