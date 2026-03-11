#!/usr/bin/env python3
"""
Скрипт импорта подкатегорий в модель Ingredient.

Алгоритм:
1. Загружает subcategories.csv и categories.csv
2. Создает mapping category_id -> category_name  
3. Для каждой подкатегории создает или обновляет ингредиент
4. Устанавливает имя по формуле: "Название категории " + (название подкатегории).lower()
5. Связывает с соответствующей категорией
"""

import os
import sys
import csv
import logging
from typing import Dict, List, Tuple, Optional

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_core.settings')

import django
django.setup()

from apps.recipe.models import Ingredient, IngredientCategory
from django.db import connection

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_subcategories.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SubcategoryImporter:
    """Класс для импорта подкатегорий в модель Ingredient."""
    
    def __init__(self):
        self.categories_mapping: Dict[int, str] = {}
        self.stats = {
            'created': 0,
            'updated': 0,
            'errors': 0,
            'skipped': 0
        }
        
    def load_categories_mapping(self, categories_file: str) -> Dict[int, str]:
        """
        Загружает categories.csv и создает mapping id -> name.
        
        Args:
            categories_file: Путь к файлу categories.csv
            
        Returns:
            Словарь {category_id: category_name}
        """
        logger.info(f"Загрузка категорий из {categories_file}")
        
        mapping = {}
        try:
            with open(categories_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    category_id = int(row['id'])
                    category_name = row['name'].strip()
                    mapping[category_id] = category_name
                    
            logger.info(f"Загружено {len(mapping)} категорий")
            return mapping
            
        except FileNotFoundError:
            logger.error(f"Файл {categories_file} не найден")
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке категорий: {e}")
            raise
            
    def load_subcategories(self, subcategories_file: str) -> List[Dict]:
        """
        Загружает subcategories.csv.
        
        Args:
            subcategories_file: Путь к файлу subcategories.csv
            
        Returns:
            Список словарей с данными подкатегорий
        """
        logger.info(f"Загрузка подкатегорий из {subcategories_file}")
        
        subcategories = []
        try:
            with open(subcategories_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Пропускаем строки с пустыми данными
                    if not row['name'].strip():
                        continue
                        
                    subcategories.append({
                        'language': row['language'],
                        'name': row['name'].strip(),
                        'category_id': int(row['category_id'])
                    })
                    
            logger.info(f"Загружено {len(subcategories)} подкатегорий")
            return subcategories
            
        except FileNotFoundError:
            logger.error(f"Файл {subcategories_file} не найден")
            raise
        except Exception as e:
            logger.error(f"Ошибка при загрузке подкатегорий: {e}")
            raise
        
    def get_or_create_ingredient_category(self, category_id: int, language: str) -> Optional[IngredientCategory]:
        """
        Находит IngredientCategory по названию и языку.
        
        Args:
            category_id: ID категории из CSV
            language: Язык категории
            
        Returns:
            IngredientCategory объект или None если не найдена
        """
        if category_id not in self.categories_mapping:
            logger.error(f"Категория с ID {category_id} не найдена в mapping")
            return None
            
        category_name = self.categories_mapping[category_id]
        
        try:
            # Ищем категорию по имени и языку
            category = IngredientCategory.objects.filter(
                name=category_name,
                language=language
            ).first()
            
            if not category:
                logger.warning(f"IngredientCategory '{category_name}' ({language}) не найдена в базе данных")
                
            return category
            
        except Exception as e:
            logger.error(f"Ошибка при поиске категории '{category_name}': {e}")
            return None
            
    def process_subcategory(self, subcategory: Dict) -> bool:
        """
        Обрабатывает одну подкатегорию - создает или обновляет ингредиент.
        
        Args:
            subcategory: Словарь с данными подкатегории
            
        Returns:
            True если обработка успешна, False в случае ошибки
        """
        try:
            # Получаем название категории
            category_id = subcategory['category_id']
            if category_id not in self.categories_mapping:
                logger.error(f"Категория ID {category_id} не найдена для подкатегории '{subcategory['name']}'")
                self.stats['errors'] += 1
                return False
                
            category_name = self.categories_mapping[category_id]
            
            # Генерируем имя ингредиента
            ingredient_name = subcategory['name']
            
            # Ищем существующий ингредиент
            existing_ingredient = Ingredient.objects.filter(name=ingredient_name).first()
            
            # Получаем категорию ингредиента
            ingredient_category = self.get_or_create_ingredient_category(category_id, subcategory['language'])
            
            if existing_ingredient:
                # Обновляем существующий ингредиент
                updated = False
                
                if existing_ingredient.category != ingredient_category:
                    existing_ingredient.category = ingredient_category
                    updated = True
                    
                if existing_ingredient.language != subcategory['language']:
                    existing_ingredient.language = subcategory['language']
                    updated = True
                    
                # description не загружается из CSV, пропускаем это обновление
                # if subcategory['description'] and existing_ingredient.description != subcategory['description']:
                #     existing_ingredient.description = subcategory['description']
                #     updated = True
                    
                # Устанавливаем is_alcoholic на основе категории
                if ingredient_category and existing_ingredient.is_alcoholic != ingredient_category.is_alcoholic:
                    existing_ingredient.is_alcoholic = ingredient_category.is_alcoholic
                    updated = True
                    
                if updated:
                    existing_ingredient.save()
                    logger.info(f"Обновлен ингредиент: '{ingredient_name}'")
                    self.stats['updated'] += 1
                else:
                    logger.debug(f"Ингредиент '{ingredient_name}' не требует обновления")
                    self.stats['skipped'] += 1
                    
            else:
                # Создаем новый ингредиент (полностью доверяем PostgreSQL автоинкремент)
                try:
                    new_ingredient = Ingredient.objects.create(
                        name=ingredient_name,
                        description="",  # description не загружается из CSV, оставляем пустым
                        category=ingredient_category,
                        language=subcategory['language'],
                        is_alcoholic=ingredient_category.is_alcoholic if ingredient_category else False
                    )
                    
                    logger.info(f"Создан новый ингредиент: '{ingredient_name}' (ID: {new_ingredient.id})")
                    self.stats['created'] += 1
                    
                except Exception as create_error:
                    # Если все еще есть проблемы с ID, логируем детали
                    logger.error(f"Ошибка создания ингредиента '{ingredient_name}': {create_error}")
                    self.stats['errors'] += 1
                    return False
                
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке подкатегории '{subcategory['name']}': {e}")
            self.stats['errors'] += 1
            return False
            
    def reset_ingredient_sequence_before_import(self):
        """
        Сбрасывает PostgreSQL sequence ПЕРЕД импортом для предотвращения конфликтов ID.
        """
        try:
            with connection.cursor() as cursor:
                # Получаем название таблицы для модели Ingredient
                table_name = Ingredient._meta.db_table
                
                # Получаем максимальный ID и устанавливаем sequence на следующее значение
                cursor.execute(f"SELECT MAX(id) FROM {table_name};")
                max_id = cursor.fetchone()[0] or 0
                
                # Устанавливаем sequence на max_id + 1
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), {max_id + 1});")
                
                logger.info(f"PostgreSQL sequence установлена на {max_id + 1} (следующий доступный ID)")
                
        except Exception as e:
            logger.warning(f"Не удалось сбросить PostgreSQL sequence: {e}")
            
    def reset_ingredient_sequence_after_import(self):
        """
        Сбрасывает PostgreSQL sequence ПОСЛЕ импорта для корректировки.
        """
        try:
            with connection.cursor() as cursor:
                # Получаем название таблицы для модели Ingredient
                table_name = Ingredient._meta.db_table
                
                # Сбрасываем sequence до максимального существующего ID + 1
                cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), COALESCE(MAX(id), 1)) FROM {table_name};")
                
                logger.info("PostgreSQL sequence синхронизирована с максимальным ID в таблице")
                
        except Exception as e:
            logger.warning(f"Не удалось синхронизировать PostgreSQL sequence: {e}")
            
    def run_import(self, subcategories_file: str, categories_file: str):
        """
        Основной метод запуска импорта.
        
        Args:
            subcategories_file: Путь к файлу subcategories.csv
            categories_file: Путь к файлу categories.csv
        """
        logger.info("=== НАЧАЛО ИМПОРТА ПОДКАТЕГОРИЙ ===")
        
        try:
            # 1. Загружаем mapping категорий
            self.categories_mapping = self.load_categories_mapping(categories_file)
            
            # 2. Загружаем подкатегории
            subcategories = self.load_subcategories(subcategories_file)
            
            # 3. Сбрасываем PostgreSQL sequence ПЕРЕД импортом
            logger.info("Настраиваем PostgreSQL sequence перед импортом...")
            self.reset_ingredient_sequence_before_import()
            
            # 4. Обрабатываем каждую подкатегорию
            logger.info("Начинаем обработку подкатегорий...")
            
            for i, subcategory in enumerate(subcategories, 1):
                if i % 50 == 0:
                    logger.info(f"Обработано {i}/{len(subcategories)} подкатегорий")
                    
                self.process_subcategory(subcategory)
                
            # 5. Синхронизируем PostgreSQL sequence после импорта
            logger.info("Синхронизируем PostgreSQL sequence после импорта...")
            self.reset_ingredient_sequence_after_import()
            
            # 6. Выводим финальную статистику
            logger.info("=== ИМПОРТ ЗАВЕРШЕН ===")
            logger.info(f"Создано новых ингредиентов: {self.stats['created']}")
            logger.info(f"Обновлено существующих ингредиентов: {self.stats['updated']}")
            logger.info(f"Пропущено (без изменений): {self.stats['skipped']}")
            logger.info(f"Ошибок: {self.stats['errors']}")
            logger.info(f"Всего обработано записей: {len(subcategories)}")
            
        except Exception as e:
            logger.error(f"Критическая ошибка импорта: {e}")
            raise


def main():
    """Основная функция скрипта."""
    
    # Пути к файлам (относительно текущего каталога)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    subcategories_file = os.path.join(script_dir, 'subcategories.csv')
    categories_file = os.path.join(script_dir, 'categories.csv')
    
    # Проверяем существование файлов
    if not os.path.exists(subcategories_file):
        logger.error(f"Файл {subcategories_file} не найден")
        return
        
    if not os.path.exists(categories_file):
        logger.error(f"Файл {categories_file} не найден")
        return
        
    # Создаем и запускаем импортер
    importer = SubcategoryImporter()
    importer.run_import(subcategories_file, categories_file)


if __name__ == '__main__':
    main()
