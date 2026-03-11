#!/bin/bash

# Скрипт для восстановления PostgreSQL базы данных из бэкапа
# Использование: ./restore_db.sh <путь_к_файлу_бэкапа>

set -e

# Параметры
DOCKER_COMPOSE_FILE="docker-compose.local.yaml"
DB_SERVICE="db"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    log_error "Укажите путь к файлу бэкапа!"
    echo "Использование: $0 <путь_к_файлу_бэкапа>"
    echo "Пример: $0 ./backups/backup_cocktails_db_2025-01-22_15-30-45.sql"
    
    # Показать доступные бэкапы
    if [ -d "./backups" ]; then
        log_info "Доступные бэкапы:"
        ls -la ./backups/*.sql 2>/dev/null | tail -5
    fi
    exit 1
fi

BACKUP_FILE="$1"

# Проверка существования файла бэкапа
if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Файл бэкапа '$BACKUP_FILE' не найден!"
    exit 1
fi

# Получение переменных окружения
if [ -f ".env" ]; then
    source .env
else
    log_warn "Файл .env не найден."
    POSTGRES_DB=${POSTGRES_DB:-"cocktails_db"}
    POSTGRES_USER=${POSTGRES_USER:-"cocktails_user"}
fi

# Проверка что контейнер запущен
if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps "$DB_SERVICE" | grep -q "Up"; then
    log_error "Контейнер базы данных '$DB_SERVICE' не запущен!"
    log_info "Запустите контейнеры: docker compose -f $DOCKER_COMPOSE_FILE up -d"
    exit 1
fi

# Предупреждение
log_warn "ВНИМАНИЕ! Это действие полностью заменит данные в базе '$POSTGRES_DB'!"
log_warn "Текущие данные будут потеряны!"
echo -n "Продолжить? (y/N): "
read -r confirmation

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    log_info "Операция отменена."
    exit 0
fi

log_info "Восстанавливаю базу данных из файла: $BACKUP_FILE"
log_info "База данных: $POSTGRES_DB"

# Восстановление базы данных
if cat "$BACKUP_FILE" | docker compose -f "$DOCKER_COMPOSE_FILE" exec -T "$DB_SERVICE" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"; then
    log_info "База данных успешно восстановлена!"
    
    # Информация о восстановленной базе
    log_info "Проверяю восстановленную базу данных..."
    docker compose -f "$DOCKER_COMPOSE_FILE" exec -T "$DB_SERVICE" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT current_database(), current_user, now();"
    
else
    log_error "Ошибка при восстановлении базы данных!"
    exit 1
fi

log_info "Восстановление завершено успешно!"
