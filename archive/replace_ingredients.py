#!/usr/bin/env python3
"""
Скрипт для замены ингредиентов в RecipeIngredient на основе данных из CSV
"""

import csv
import os
import sys
import django
from pathlib import Path

# Настройка Django
BASE_DIR = Path(__file__).resolve().parent  # Уже в папке cocktails
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_core.settings')
django.setup()

from apps.recipe.models import RecipeIngredient, Ingredient, IngredientCategory


def read_csv_data(csv_file_path):
    """Читает CSV файл и возвращает словарь с данными (только русские ликеры)"""
    ingredient_mapping = {}
    total_rows = 0
    russian_rows = 0
    english_rows = 0
    liqueur_rows = 0
    other_category_rows = 0
    
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ingredient_name = row['ingredient_name']
            subcategory_name = row['subcategory_name']
            language = row['language']
            category_id = row['category_id']
            category_name = row['category_name']
            
            if ingredient_name and subcategory_name:
                total_rows += 1
                
                # Очищаем имя от переносов строк и лишних пробелов
                ingredient_name = ' '.join(ingredient_name.split())
                subcategory_name = ' '.join(subcategory_name.split())
                
                if language == 'RUS':
                    russian_rows += 1
                    
                    # Проверяем, что категория - "Ликер" (id=23)
                    if category_id == '23' and category_name == 'Ликер':
                        liqueur_rows += 1
                        # Создаем новое имя ингредиента
                        new_ingredient_name = f"Ликер {subcategory_name.lower()}"
                        ingredient_mapping[ingredient_name] = new_ingredient_name
                    else:
                        other_category_rows += 1
                        
                elif language == 'ENG':
                    english_rows += 1
    
    print(f"Статистика CSV файла:")
    print(f"  Всего строк с данными: {total_rows}")
    print(f"  Русских записей: {russian_rows}")
    print(f"    - из них ликеры (category_id=23): {liqueur_rows}")
    print(f"    - из них другие категории (пропущено): {other_category_rows}")
    print(f"  Английских записей (пропущено): {english_rows}")
    
    return ingredient_mapping


def get_or_create_liqueur_ingredient(ingredient_name, original_ingredient=None):
    """Находит или создает ингредиент-ликер"""
    try:
        # Пытаемся найти существующий ингредиент
        ingredient = Ingredient.objects.get(name=ingredient_name)
        return ingredient
    except Ingredient.DoesNotExist:
        # Создаем новый ингредиент
        liqueur_category, _ = IngredientCategory.objects.get_or_create(
            name='Ликер',
            defaults={
                'language': 'RUS',
                'is_alcoholic': True
            }
        )
        
        new_ingredient = Ingredient.objects.create(
            name=ingredient_name,
            language='RUS',
            category=liqueur_category,
            is_alcoholic=True,
            description=f"Автоматически созданный ингредиент: {ingredient_name}"
        )
        
        return new_ingredient


def analyze_database_ingredients():
    """Анализирует ингредиенты-ликеры в базе данных"""
    try:
        liqueur_category = IngredientCategory.objects.get(id=23, name='Ликер')
        liqueur_ingredients = Ingredient.objects.filter(
            category=liqueur_category, 
            language='RUS'
        ).order_by('name')
        
        print(f"\nИнгредиенты-ликеры в БД (всего: {liqueur_ingredients.count()}):")
        for i, ingredient in enumerate(liqueur_ingredients[:20]):  # Показываем только первые 20
            print(f"  {i+1:2d}. '{ingredient.name}'")
        
        if liqueur_ingredients.count() > 20:
            print(f"  ... и еще {liqueur_ingredients.count() - 20} ингредиентов")
            
        return [ing.name for ing in liqueur_ingredients]
    except IngredientCategory.DoesNotExist:
        print("  Категория 'Ликер' не найдена в БД!")
        return []


def find_similar_ingredient_name(target_name, db_ingredients):
    """Находит наиболее похожее имя ингредиента в БД"""
    target_lower = target_name.lower()
    
    # Точное совпадение
    for db_name in db_ingredients:
        if db_name.lower() == target_lower:
            return db_name
    
    # Частичное совпадение
    for db_name in db_ingredients:
        if target_lower in db_name.lower() or db_name.lower() in target_lower:
            return db_name
    
    return None


def replace_ingredients(ingredient_mapping):
    """Заменяет ингредиенты в RecipeIngredient"""
    total_replaced = 0
    not_found_count = 0
    
    # Получаем список всех ингредиентов-ликеров из БД
    db_ingredients = analyze_database_ingredients()
    
    for original_name, new_name in ingredient_mapping.items():
        print(f"Обрабатываем: {original_name} -> {new_name}")
        
        # Пытаемся найти похожий ингредиент
        similar_name = find_similar_ingredient_name(original_name, db_ingredients)
        
        if similar_name and similar_name != original_name:
            print(f"  Используем похожее имя: '{similar_name}' вместо '{original_name}'")
            search_name = similar_name
        else:
            search_name = original_name
        
        # Находим все RecipeIngredient с оригинальным ингредиентом (только русские ликеры)
        try:
            # Ищем ингредиент с языком RUS и категорией "Ликер"
            liqueur_category = IngredientCategory.objects.get(id=23, name='Ликер')
            original_ingredient = Ingredient.objects.get(
                name=search_name, 
                language='RUS', 
                category=liqueur_category
            )
        except (Ingredient.DoesNotExist, IngredientCategory.DoesNotExist):
            print(f"  Предупреждение: Русский ликер '{search_name}' не найден в БД")
            not_found_count += 1
            continue
        
        recipe_ingredients = RecipeIngredient.objects.filter(ingredient=original_ingredient)
        count = recipe_ingredients.count()
        
        if count == 0:
            print(f"  Не найдено RecipeIngredient для '{search_name}'")
            continue
        
        # Получаем или создаем новый ингредиент
        new_ingredient = get_or_create_liqueur_ingredient(new_name, original_ingredient)
        
        # Заменяем ингредиент во всех найденных записях
        updated = recipe_ingredients.update(ingredient=new_ingredient)
        total_replaced += updated
        
        print(f"  Заменено {updated} записей RecipeIngredient")
    
    print(f"\nИтоговая статистика:")
    print(f"  Не найдено в БД: {not_found_count}")
    print(f"  Успешно заменено записей: {total_replaced}")
    
    return total_replaced


def main():
    csv_file_path = 'stage2_success_all.csv'  # Теперь в той же папке
    
    if not os.path.exists(csv_file_path):
        print(f"Ошибка: Файл {csv_file_path} не найден!")
        return
    
    print("Начинаем обработку...")
    print(f"Читаем файл: {csv_file_path}")
    
    # Читаем данные из CSV
    ingredient_mapping = read_csv_data(csv_file_path)
    print(f"Найдено {len(ingredient_mapping)} записей для обработки")
    
    if not ingredient_mapping:
        print("Нет данных для обработки!")
        return
    
    # Показываем первые несколько примеров
    print("\nПримеры замен:")
    for i, (original, new) in enumerate(list(ingredient_mapping.items())[:5]):
        print(f"  {original} -> {new}")
    if len(ingredient_mapping) > 5:
        print(f"  ... и еще {len(ingredient_mapping) - 5} записей")
    
    # Подтверждение
    response = input("\nПродолжить с заменой ингредиентов? (y/N): ").lower()
    if response != 'y':
        print("Операция отменена.")
        return
    
    # Выполняем замену
    print("\nВыполняем замену ингредиентов...")
    total_replaced = replace_ingredients(ingredient_mapping)
    
    print(f"\nГотово! Всего заменено {total_replaced} записей RecipeIngredient")


if __name__ == '__main__':
    main()
