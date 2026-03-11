#!/bin/bash

# Простой скрипт для быстрого бэкапа PostgreSQL базы данных
# Использование: ./quick_backup.sh [имя_базы]

# Параметры по умолчанию
DOCKER_COMPOSE_FILE="docker-compose.local.yaml"
DB_SERVICE="db"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Получение имени базы из аргумента или .env
if [ -n "$1" ]; then
    DB_NAME="$1"
elif [ -f ".env" ]; then
    source .env
    DB_NAME="${POSTGRES_DB:-cocktails_db}"
else
    DB_NAME="cocktails_db"
fi

# Получение пользователя из .env
if [ -f ".env" ]; then
    source .env
    DB_USER="${POSTGRES_USER:-cocktails_user}"
else
    DB_USER="cocktails_user"
fi

BACKUP_FILE="backup_${DB_NAME}_${DATE}.sql"

echo "🗃️  Создаю бэкап базы данных '$DB_NAME'..."
echo "📁 Файл: $BACKUP_FILE"

# Создание бэкапа
docker compose -f "$DOCKER_COMPOSE_FILE" exec -T "$DB_SERVICE" pg_dump \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-password \
    --verbose \
    --clean \
    --if-exists > "$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Бэкап создан успешно!"
    echo "📊 Размер: $SIZE"
    echo "📍 Путь: $(pwd)/$BACKUP_FILE"
else
    echo "❌ Ошибка при создании бэкапа!"
    [ -f "$BACKUP_FILE" ] && rm "$BACKUP_FILE"
    exit 1
fi
