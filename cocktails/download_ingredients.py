import pandas as pd
from django.db import models

from apps.recipe.models import Ingredient


def export_ingredients_to_excel():
    # Получаем все ингредиенты из базы данных
    ingredients = Ingredient.objects.all()

    # Создаем список словарей для DataFrame
    data = []
    for ingredient in ingredients:
        data.append({
            'ID': ingredient.id,
            'Ингредиент': ingredient.name,
            'Язык': ingredient.get_language_display(),  # Получаем читаемое значение выбора
            'Категория': ''  # Оставляем пустым по условию задачи
        })

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Сохраняем в Excel файл
    output_path = 'Ingredients_export.xlsx'
    df.to_excel(output_path, index=False, sheet_name='Лист1')

    return output_path


# Вызываем функцию экспорта
exported_file = export_ingredients_to_excel()
print(f"Данные экспортированы в файл: {exported_file}")