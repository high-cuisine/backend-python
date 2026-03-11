#!/bin/bash

# Скрипт для восстановления дампа PostgreSQL в Docker контейнере
# Использование: ./restore_dump.sh [путь_к_дампу] [docker-compose_файл]

set -e  # Остановить выполнение при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Параметры по умолчанию
DUMP_FILE="${1:-archive/db_with_coctails.dump}"
COMPOSE_FILE="${2:-docker-compose.local.yaml}"
DB_NAME="cocktails"
DB_USER="cocktails"
DB_CONTAINER="backend-db-1"
TEMP_DUMP_PATH="/tmp/$(basename $DUMP_FILE)"

# Проверка существования файлов
if [[ ! -f "$DUMP_FILE" ]]; then
    error "Файл дампа не найден: $DUMP_FILE"
    echo "Использование: $0 [путь_к_дампу] [docker-compose_файл]"
    exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
    error "Docker Compose файл не найден: $COMPOSE_FILE"
    exit 1
fi

log "Начинаем восстановление дампа: $DUMP_FILE"
log "Docker Compose файл: $COMPOSE_FILE"

# 1. Остановка контейнеров для освобождения подключений к БД
log "Остановка контейнеров web, celery-worker, celery-beat..."
docker compose -f "$COMPOSE_FILE" stop web celery-worker celery-beat || {
    warning "Некоторые контейнеры могут быть уже остановлены"
}

# 2. Ожидание остановки контейнеров
sleep 3

# 3. Принудительное завершение всех подключений к базе данных
log "Завершение всех активных подключений к базе данных '$DB_NAME'..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME' 
  AND pid <> pg_backend_pid();" || {
    warning "Не удалось завершить некоторые подключения"
}

# Дополнительное ожидание
sleep 2

# 4. Удаление существующей базы данных
log "Удаление существующей базы данных '$DB_NAME'..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || {
    error "Не удалось удалить базу данных"
    exit 1
}

# 5. Создание новой пустой базы данных
log "Создание новой пустой базы данных '$DB_NAME'..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || {
    error "Не удалось создать базу данных"
    exit 1
}

# 6. Копирование дампа в контейнер
log "Копирование дампа в контейнер..."
docker cp "$DUMP_FILE" "$DB_CONTAINER:$TEMP_DUMP_PATH" || {
    error "Не удалось скопировать дамп в контейнер"
    exit 1
}

# 7. Восстановление дампа
log "Восстановление дампа в базу данных..."
docker compose -f "$COMPOSE_FILE" exec db pg_restore -U "$DB_USER" -d "$DB_NAME" -v --clean --if-exists "$TEMP_DUMP_PATH" || {
    error "Ошибка при восстановлении дампа"
    exit 1
}

# 8. Удаление временного файла дампа из контейнера
log "Удаление временного файла дампа из контейнера..."
docker compose -f "$COMPOSE_FILE" exec db rm -f "$TEMP_DUMP_PATH" || {
    warning "Не удалось удалить временный файл дампа"
}

# 9. Запуск всех контейнеров
log "Запуск всех контейнеров..."
docker compose -f "$COMPOSE_FILE" up -d || {
    error "Не удалось запустить контейнеры"
    exit 1
}

# 10. Ожидание запуска контейнеров
sleep 5

# 11. Проверка восстановленных данных
log "Проверка восстановленных данных..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT 
    'recipe_recipe' as table_name, COUNT(*) as count 
FROM recipe_recipe 
UNION ALL 
SELECT 'recipe_ingredient', COUNT(*) FROM recipe_ingredient 
UNION ALL 
SELECT 'user_user', COUNT(*) FROM user_user 
UNION ALL 
SELECT 'goods_goods', COUNT(*) FROM goods_goods 
ORDER BY table_name;
" || {
    warning "Не удалось проверить данные, но восстановление могло пройти успешно"
}

log "✅ Восстановление дампа завершено успешно!"
log "База данных '$DB_NAME' готова к использованию"
log "Доступ: localhost:5432, пользователь: $DB_USER"

echo ""
echo "Для проверки статуса контейнеров выполните:"
echo "docker compose -f $COMPOSE_FILE ps"
