"""
Создаёт английские секции/категории/ингредиенты по образцу русских.
Для категорий из-за unique=True на name использует имя с суффиксом " [EN]".
Запуск: python manage.py copy_ingredient_structure_rus_to_eng
После выполнения при User-Language: eng API отдаст списки для шага выбора ингредиентов.
"""
from django.core.management.base import BaseCommand
from apps.recipe.models import (
    IngredientCategorySection,
    IngredientCategory,
    Ingredient,
)

EN_SUFFIX = ' [EN]'


def eng_category_name(rus_name: str) -> str:
    """Уникальное имя ENG-категории (у IngredientCategory name unique глобально)."""
    return rus_name + EN_SUFFIX


class Command(BaseCommand):
    help = 'Copy RUS ingredient sections, categories and ingredients to ENG'

    def handle(self, *args, **options):
        rus_sections = IngredientCategorySection.objects.filter(language='RUS').prefetch_related('categories')
        if not rus_sections.exists():
            self.stdout.write(self.style.WARNING('No RUS sections found.'))
            return

        cat_rus_to_eng = {}  # RUS category id -> ENG category
        for rus_sec in rus_sections:
            eng_sec, created = IngredientCategorySection.objects.get_or_create(
                language='ENG',
                name=rus_sec.name,
                defaults={},
            )
            if created:
                self.stdout.write(f'Section ENG: {rus_sec.name}')

            eng_cat_ids = []
            for rus_cat in rus_sec.categories.filter(language='RUS'):
                eng_name = eng_category_name(rus_cat.name)
                eng_cat, created = IngredientCategory.objects.get_or_create(
                    language='ENG',
                    name=eng_name,
                    defaults={
                        'is_main': rus_cat.is_main,
                        'is_alcoholic': rus_cat.is_alcoholic,
                    },
                )
                cat_rus_to_eng[rus_cat.id] = eng_cat
                eng_cat_ids.append(eng_cat.id)
                if created:
                    self.stdout.write(f'  Category ENG: {eng_name}')

            eng_sec.categories.add(*eng_cat_ids)

        rus_ingredients = Ingredient.objects.filter(language='RUS').select_related('category')
        created_count = 0
        for rus_ing in rus_ingredients:
            eng_cat = None
            if rus_ing.category_id:
                eng_cat = cat_rus_to_eng.get(rus_ing.category_id)
            _, created = Ingredient.objects.get_or_create(
                language='ENG',
                name=rus_ing.name,
                defaults={
                    'category': eng_cat,
                    'is_alcoholic': rus_ing.is_alcoholic,
                    'description': rus_ing.description or '',
                },
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Done. ENG ingredients created: {created_count}'))
