#!/bin/bash

# Скрипт для восстановления дампа PostgreSQL на продакшн сервере
# Использование: ./restore_dump_prod.sh [путь_к_дампу]

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

# Параметры по умолчанию для продакшн
DUMP_FILE="${1:-archive/db_with_coctails.dump}"
COMPOSE_FILE="docker-compose.yml"
DB_NAME="cocktails"
DB_USER="cocktails"
DB_CONTAINER="cocktails-db-1"  # Обычно в продакшне другое именование
TEMP_DUMP_PATH="/tmp/$(basename $DUMP_FILE)"

# Проверка существования файлов
if [[ ! -f "$DUMP_FILE" ]]; then
    error "Файл дампа не найден: $DUMP_FILE"
    echo "Использование: $0 [путь_к_дампу]"
    exit 1
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
    error "Docker Compose файл не найден: $COMPOSE_FILE"
    exit 1
fi

# Предупреждение для продакшн среды
warning "⚠️  ВНИМАНИЕ! Этот скрипт предназначен для ПРОДАКШН сервера!"
warning "Это приведет к полной очистке базы данных и простою сервиса!"
read -p "Вы уверены, что хотите продолжить? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    log "Операция отменена пользователем"
    exit 0
fi

log "Начинаем восстановление дампа на ПРОДАКШН сервере: $DUMP_FILE"

# Определение имени контейнера базы данных автоматически
DB_CONTAINER=$(docker compose -f "$COMPOSE_FILE" ps --services | grep -E "(db|postgres)" | head -1)
if [[ -z "$DB_CONTAINER" ]]; then
    # Попробуем найти по запущенным контейнерам
    DB_CONTAINER=$(docker compose -f "$COMPOSE_FILE" ps -q db 2>/dev/null) 
    if [[ -z "$DB_CONTAINER" ]]; then
        error "Не удалось найти контейнер базы данных"
        exit 1
    fi
    # Получаем полное имя контейнера
    DB_CONTAINER=$(docker inspect --format='{{.Name}}' $DB_CONTAINER | sed 's/^\/*//')
else
    # Получаем имя контейнера с префиксом проекта
    PROJECT_NAME=$(basename "$(pwd)")
    DB_CONTAINER="${PROJECT_NAME}-${DB_CONTAINER}-1"
fi

log "Используется контейнер базы данных: $DB_CONTAINER"

# 1. Создание резервной копии текущей БД (на всякий случай)
log "Создание резервной копии текущей базы данных..."
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).sql"
docker compose -f "$COMPOSE_FILE" exec db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_NAME" || {
    warning "Не удалось создать резервную копию, но продолжаем..."
}

if [[ -f "$BACKUP_NAME" ]]; then
    log "Резервная копия сохранена как: $BACKUP_NAME"
fi

# 2. Остановка веб-сервисов (оставляем БД и инфраструктуру)
log "Остановка веб-сервисов..."
docker compose -f "$COMPOSE_FILE" stop web celery-worker celery-beat || {
    warning "Некоторые контейнеры могут быть уже остановлены"
}

# Ожидание остановки
sleep 5

# 3. Удаление существующей базы данных
log "Удаление существующей базы данных '$DB_NAME'..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" || {
    error "Не удалось удалить базу данных"
    exit 1
}

# 4. Создание новой пустой базы данных
log "Создание новой пустой базы данных '$DB_NAME'..."
docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || {
    error "Не удалось создать базу данных"
    exit 1
}

# 5. Копирование дампа в контейнер
log "Копирование дампа в контейнер..."
docker cp "$DUMP_FILE" "$DB_CONTAINER:$TEMP_DUMP_PATH" || {
    error "Не удалось скопировать дамп в контейнер"
    exit 1
}

# 6. Восстановление дампа
log "Восстановление дампа в базу данных..."
docker compose -f "$COMPOSE_FILE" exec db pg_restore -U "$DB_USER" -d "$DB_NAME" -v --clean --if-exists "$TEMP_DUMP_PATH" || {
    error "Ошибка при восстановлении дампа"
    
    # Попытка восстановить из бэкапа при ошибке
    if [[ -f "$BACKUP_NAME" ]]; then
        warning "Попытка восстановления из резервной копии..."
        docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
        docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        docker cp "$BACKUP_NAME" "$DB_CONTAINER:/tmp/backup.sql"
        docker compose -f "$COMPOSE_FILE" exec db psql -U "$DB_USER" -d "$DB_NAME" -f /tmp/backup.sql
        docker compose -f "$COMPOSE_FILE" exec db rm -f /tmp/backup.sql
        warning "Восстановлена резервная копия базы данных"
    fi
    
    exit 1
}

# 7. Удаление временного файла дампа из контейнера
log "Удаление временного файла дампа из контейнера..."
docker compose -f "$COMPOSE_FILE" exec db rm -f "$TEMP_DUMP_PATH" || {
    warning "Не удалось удалить временный файл дампа"
}

# 8. Запуск всех сервисов
log "Запуск всех сервисов..."
docker compose -f "$COMPOSE_FILE" up -d || {
    error "Не удалось запустить контейнеры"
    exit 1
}

# 9. Ожидание запуска сервисов
log "Ожидание запуска сервисов..."
sleep 10

# 10. Проверка восстановленных данных
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

# 11. Проверка состояния сервисов
log "Проверка состояния сервисов..."
docker compose -f "$COMPOSE_FILE" ps

log "✅ Восстановление дампа на продакшн сервере завершено успешно!"
log "База данных '$DB_NAME' готова к использованию"

if [[ -f "$BACKUP_NAME" ]]; then
    log "💾 Резервная копия доступна: $BACKUP_NAME"
    log "Рекомендуется сохранить её в надежном месте"
fi

log "🔍 Рекомендуется провести дополнительную проверку функциональности сервиса"
