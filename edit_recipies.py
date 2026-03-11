import os

from django import setup
from django.core.files import File

from apps.recipe.models import Recipe

directory = 'english_photos'


def update_photo_field():
    for instance in Recipe.objects.all():
        title = instance.title
        list_title = title.split(' ')
        if title.isupper():  # Проверка на заглавные буквы
            title = instance.title.capitalize()
        if len(list_title) == 2:
            list_title[-1] = list_title[-1].capitalize()
            title = ' '.join(list_title)
        if instance.title != title:
            instance.title = title
            instance.save()  # сохраняем изменение имени в модели
        file_path = os.path.join(directory, f"{title}.jpg")  # Замените путь
        if os.path.exists(file_path):
            try:
                with open(file_path, 'rb') as f:
                    instance.photo.save(f"{title}.jpg", File(f), save=True)
                print(f"Фото для '{title}' добавлено.")
            except Exception as e:
                print(f"Ошибка при добавлении фото для '{title}': {e}")
        else:
            print(f"Файл '{file_path}' не найден для '{title}'.")
            
update_photo_field()
