import pandas as pd
import django
import os

from apps.recipe.models import Ingredient, IngredientCategory


def update_ingredient_categories():
    # Чтение Excel файла
    try:
        df = pd.read_excel('Ingredients_import.xlsx')
    except FileNotFoundError:
        print('Ошибка: Файл Ingredients_import.xlsx не найден')
        return

    # Словарь для хранения неудачных обновлений
    failed_updates = []
    success_count = 0

    # Обработка каждой строки в файле
    for index, row in df.iterrows():
        ingredient_id = int(row['ID']) if not pd.isna(row['ID']) else None
        category_name = row['Категория'] if not pd.isna(row['Категория']) else None

        if not ingredient_id or not category_name:
            continue

        try:
            # Находим ингредиент
            ingredient = Ingredient.objects.get(id=ingredient_id)

            # Пытаемся найти категорию (без создания новой)
            try:
                category = IngredientCategory.objects.get(name=category_name)
                ingredient.category = category
                ingredient.save()
                success_count += 1
            except IngredientCategory.DoesNotExist:
                failed_updates.append({
                    'id': ingredient_id,
                    'name': ingredient.name,
                    'category': category_name,
                    'reason': 'Категория не найдена'
                })

        except Ingredient.DoesNotExist:
            failed_updates.append({
                'id': ingredient_id,
                'name': row['Ингредиент'],
                'category': category_name,
                'reason': 'Ингредиент не найден'
            })

    # Вывод результатов
    if failed_updates:
        print('\nНе удалось обновить следующие ингредиенты:')
        for item in failed_updates:
            print(
                f"ID: {item['id']}, Ингредиент: {item['name']}, "
                f"Категория: {item['category']}, Причина: {item['reason']}"
            )
    else:
        print('Все категории успешно обновлены!')

    print(f"\nСтатистика:")
    print(f"Обработано строк: {len(df)}")
    print(f"Успешно обновлено: {success_count}")
    print(f"Не удалось обновить: {len(failed_updates)}")


if __name__ == '__main__':
    update_ingredient_categories()
