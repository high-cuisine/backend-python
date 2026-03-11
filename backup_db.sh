#!/bin/bash

# Скрипт для создания бэкапа PostgreSQL базы данных из Docker контейнера
# Использование: ./backup_db.sh

set -e  # Остановка при любой ошибке

# Настройки
DOCKER_COMPOSE_FILE="docker-compose.local.yaml"
DB_SERVICE="db"
BACKUP_DIR="./backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка существования docker-compose файла
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    log_error "Файл $DOCKER_COMPOSE_FILE не найден!"
    exit 1
fi

# Создание директории для бэкапов если она не существует
if [ ! -d "$BACKUP_DIR" ]; then
    log_info "Создаю директорию для бэкапов: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# Проверка что контейнер базы данных запущен
if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps "$DB_SERVICE" | grep -q "Up"; then
    log_error "Контейнер базы данных '$DB_SERVICE' не запущен!"
    log_info "Запустите контейнеры командой: docker compose -f $DOCKER_COMPOSE_FILE up -d"
    exit 1
fi

# Получение переменных окружения из .env файла
if [ -f ".env" ]; then
    source .env
else
    log_warn "Файл .env не найден. Используются значения по умолчанию."
    POSTGRES_DB=${POSTGRES_DB:-"cocktails_db"}
    POSTGRES_USER=${POSTGRES_USER:-"cocktails_user"}
fi

# Имя файла бэкапа
BACKUP_FILENAME="backup_${POSTGRES_DB}_${DATE}.sql"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILENAME"

log_info "Создаю бэкап базы данных '$POSTGRES_DB'..."
log_info "Файл бэкапа: $BACKUP_PATH"

# Создание бэкапа
if docker compose -f "$DOCKER_COMPOSE_FILE" exec -T "$DB_SERVICE" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-password --verbose > "$BACKUP_PATH"; then
    
    # Проверка что файл создан и не пустой
    if [ -s "$BACKUP_PATH" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
        log_info "Бэкап успешно создан!"
        log_info "Размер файла: $BACKUP_SIZE"
        log_info "Путь к файлу: $BACKUP_PATH"
        
        # Создание символической ссылки на последний бэкап
        LATEST_BACKUP_LINK="$BACKUP_DIR/latest_backup.sql"
        ln -sf "$BACKUP_FILENAME" "$LATEST_BACKUP_LINK"
        log_info "Создана ссылка на последний бэкап: $LATEST_BACKUP_LINK"
        
    else
        log_error "Файл бэкапа создан, но он пустой!"
        rm -f "$BACKUP_PATH"
        exit 1
    fi
else
    log_error "Ошибка при создании бэкапа!"
    exit 1
fi

# Показать список всех бэкапов
log_info "Список всех бэкапов:"
ls -lah "$BACKUP_DIR"/*.sql 2>/dev/null | tail -10 || log_warn "Бэкапы не найдены"

log_info "Бэкап завершен успешно!"
