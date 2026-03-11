"""
Django Management Command для импорта данных из Excel файла

Использование:
python manage.py import_ingredients_from_excel Ingredients_export.xlsx
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.recipe.models import IngredientCategory, Ingredient, IngredientCategorySection
import pandas as pd
import os
from typing import Dict, List, Optional


class Command(BaseCommand):
    help = 'Импорт ингредиентов и категорий из Excel файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_file',
            type=str,
            help='Путь к Excel файлу для импорта'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Запуск в режиме тестирования без сохранения в БД'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Обновлять существующие записи'
        )

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        dry_run = options['dry_run']
        update_existing = options['update_existing']

        if not os.path.exists(excel_file):
            raise CommandError(f'Файл {excel_file} не найден!')

        self.stdout.write(f'Начинаем импорт из файла: {excel_file}')

        if dry_run:
            self.stdout.write(self.style.WARNING('РЕЖИМ ТЕСТИРОВАНИЯ - изменения не будут сохранены'))

        try:
            with transaction.atomic():
                stats = self.import_from_excel(excel_file, update_existing)

                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING('Транзакция отменена (режим тестирования)'))

                self.print_import_statistics(stats)

        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {str(e)}')

    def import_from_excel(self, excel_file: str, update_existing: bool = False) -> Dict:
        """Импорт данных из Excel файла"""
        stats = {
            'categories_created': 0,
            'categories_updated': 0,
            'ingredients_created': 0,
            'ingredients_updated': 0,
            'sections_created': 0,
            'sections_updated': 0,
            'errors': []
        }

        try:
            # Читаем все листы Excel файла
            excel_data = pd.read_excel(excel_file, sheet_name=None)

            # Обрабатываем каждый лист
            if 'Лист1' in excel_data:
                self.process_ingredients_with_categories(
                    excel_data['Лист1'], stats, update_existing
                )

            if 'Лист2' in excel_data:
                self.process_ingredients_list(
                    excel_data['Лист2'], stats, update_existing
                )

            if 'Лист3' in excel_data:
                self.process_category_hierarchy(
                    excel_data['Лист3'], stats, update_existing
                )

        except Exception as e:
            stats['errors'].append(f'Ошибка чтения Excel файла: {str(e)}')

        return stats

    def process_ingredients_with_categories(self, df: pd.DataFrame, stats: Dict, update_existing: bool):
        """Обработка первого листа с ингредиентами и категориями"""
        df = df.dropna(subset=['Ингредиент', 'Категория'])

        language_map = {
            'Английский': 'ENG',
            'Русский': 'RUS'
        }

        for index, row in df.iterrows():
            try:
                ingredient_name = str(row['Ингредиент']).strip()
                language = language_map.get(str(row['Язык']).strip(), 'RUS')
                category_name = str(row['Категория']).strip()

                # Создаем или получаем категорию
                category, created = IngredientCategory.objects.get_or_create(
                    name=category_name,
                    language=language,
                    defaults={
                        'is_main': False,
                        'is_alcoholic': self.is_alcoholic_category(category_name)
                    }
                )

                if created:
                    stats['categories_created'] += 1
                    self.stdout.write(f'Создана категория: {category_name} ({language})')

                # Создаем или получаем ингредиент
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    language=language,
                    defaults={
                        'category': category,
                        'is_alcoholic': self.is_alcoholic_ingredient(ingredient_name, category_name)
                    }
                )

                if created:
                    stats['ingredients_created'] += 1
                    self.stdout.write(f'Создан ингредиент: {ingredient_name} ({language})')
                elif update_existing:
                    ingredient.category = category
                    ingredient.is_alcoholic = self.is_alcoholic_ingredient(ingredient_name, category_name)
                    ingredient.save()
                    stats['ingredients_updated'] += 1
                    self.stdout.write(f'Обновлен ингредиент: {ingredient_name} ({language})')

            except Exception as e:
                error_msg = f'Ошибка обработки строки {index + 1}: {str(e)}'
                stats['errors'].append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

    def process_ingredients_list(self, df: pd.DataFrame, stats: Dict, update_existing: bool):
        """Обработка второго листа со списком ингредиентов"""
        df = df.dropna(subset=['Ингредиент'])

        for index, row in df.iterrows():
            try:
                ingredient_name = str(row['Ингредиент']).strip()
                language = self.detect_language(ingredient_name)

                # Создаем ингредиент без категории, если его еще нет
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    language=language,
                    defaults={
                        'category': None,
                        'is_alcoholic': self.is_alcoholic_ingredient(ingredient_name)
                    }
                )

                if created:
                    stats['ingredients_created'] += 1
                    self.stdout.write(f'Создан ингредиент: {ingredient_name} ({language})')

            except Exception as e:
                error_msg = f'Ошибка обработки строки {index + 1} листа 2: {str(e)}'
                stats['errors'].append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

    def process_category_hierarchy(self, df: pd.DataFrame, stats: Dict, update_existing: bool):
        """Обработка третьего листа с иерархией категорий"""
        df = df.dropna(subset=['Основная категория'], how='all')

        current_main_category_ru = None
        current_main_category_en = None
        current_section_ru = None
        current_section_en = None

        for index, row in df.iterrows():
            try:
                # Обрабатываем основную категорию на русском
                if pd.notna(row['Основная категория']) and str(row['Основная категория']).strip():
                    current_main_category_ru = str(row['Основная категория']).strip()

                    category, created = IngredientCategory.objects.get_or_create(
                        name=current_main_category_ru,
                        language='RUS',
                        defaults={
                            'is_main': True,
                            'is_alcoholic': self.is_alcoholic_category(current_main_category_ru)
                        }
                    )

                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(f'Создана основная категория: {current_main_category_ru} (RUS)')

                    # Создаем секцию для основной категории
                    current_section_ru, created = IngredientCategorySection.objects.get_or_create(
                        name=current_main_category_ru,
                        language='RUS'
                    )

                    if created:
                        stats['sections_created'] += 1

                    current_section_ru.categories.add(category)

                # Обрабатываем основную категорию на английском
                if pd.notna(row['Main category']) and str(row['Main category']).strip():
                    current_main_category_en = str(row['Main category']).strip()

                    category, created = IngredientCategory.objects.get_or_create(
                        name=current_main_category_en,
                        language='ENG',
                        defaults={
                            'is_main': True,
                            'is_alcoholic': self.is_alcoholic_category(current_main_category_en)
                        }
                    )

                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(f'Создана основная категория: {current_main_category_en} (ENG)')

                    # Создаем секцию для основной категории
                    current_section_en, created = IngredientCategorySection.objects.get_or_create(
                        name=current_main_category_en,
                        language='ENG'
                    )

                    if created:
                        stats['sections_created'] += 1

                    current_section_en.categories.add(category)

                # Обрабатываем подкатегории
                if pd.notna(row['Подкатегория']) and str(row['Подкатегория']).strip():
                    subcategory_name = str(row['Подкатегория']).strip()

                    subcategory, created = IngredientCategory.objects.get_or_create(
                        name=subcategory_name,
                        language='RUS',
                        defaults={
                            'is_main': False,
                            'is_alcoholic': self.is_alcoholic_category(subcategory_name)
                        }
                    )

                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(f'Создана подкатегория: {subcategory_name} (RUS)')

                    # Добавляем в секцию
                    if current_section_ru:
                        current_section_ru.categories.add(subcategory)

                if pd.notna(row['Daughters category']) and str(row['Daughters category']).strip():
                    subcategory_name = str(row['Daughters category']).strip()

                    subcategory, created = IngredientCategory.objects.get_or_create(
                        name=subcategory_name,
                        language='ENG',
                        defaults={
                            'is_main': False,
                            'is_alcoholic': self.is_alcoholic_category(subcategory_name)
                        }
                    )

                    if created:
                        stats['categories_created'] += 1
                        self.stdout.write(f'Создана подкатегория: {subcategory_name} (ENG)')

                    # Добавляем в секцию
                    if current_section_en:
                        current_section_en.categories.add(subcategory)

            except Exception as e:
                error_msg = f'Ошибка обработки строки {index + 1} листа 3: {str(e)}'
                stats['errors'].append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

    def detect_language(self, text: str) -> str:
        """Определение языка текста"""
        # Проверяем наличие кириллических символов
        if any('\u0400' <= char <= '\u04ff' for char in text):
            return 'RUS'
        return 'ENG'

    def is_alcoholic_category(self, category_name: str) -> bool:
        """Определение алкогольности категории"""
        alcoholic_keywords = [
            'rum', 'vodka', 'whiskey', 'wine', 'beer', 'brandy', 'gin', 'tequila',
            'rum', 'водка', 'виски', 'вино', 'пиво', 'бренди', 'джин', 'текила',
            'liqueur', 'ликер', 'абсент', 'absinthe', 'коньяк', 'cognac', 'bitter'
        ]
        return any(keyword in category_name.lower() for keyword in alcoholic_keywords)

    def is_alcoholic_ingredient(self, ingredient_name: str, category_name: str = None) -> bool:
        """Определение алкогольности ингредиента"""
        if category_name and self.is_alcoholic_category(category_name):
            return True

        alcoholic_keywords = [
            'rum', 'vodka', 'whiskey', 'wine', 'beer', 'brandy', 'gin', 'tequila',
            'rum', 'водка', 'виски', 'вино', 'пиво', 'бренди', 'джин', 'текила',
            'liqueur', 'ликер', 'абсент', 'absinthe', 'коньяк', 'cognac', 'bitter'
        ]
        return any(keyword in ingredient_name.lower() for keyword in alcoholic_keywords)

    def print_import_statistics(self, stats: Dict):
        """Вывод статистики импорта"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('СТАТИСТИКА ИМПОРТА'))
        self.stdout.write('='*50)

        self.stdout.write(f'Категории создано: {stats["categories_created"]}')
        self.stdout.write(f'Категории обновлено: {stats["categories_updated"]}')
        self.stdout.write(f'Ингредиенты создано: {stats["ingredients_created"]}')
        self.stdout.write(f'Ингредиенты обновлено: {stats["ingredients_updated"]}')
        self.stdout.write(f'Секции создано: {stats["sections_created"]}')
        self.stdout.write(f'Секции обновлено: {stats["sections_updated"]}')

        if stats['errors']:
            self.stdout.write(f'\nОшибки: {len(stats["errors"])}')
            for error in stats['errors']:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        else:
            self.stdout.write(self.style.SUCCESS('\nОшибок не обнаружено!'))

        self.stdout.write('='*50)
        