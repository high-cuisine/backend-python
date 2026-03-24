"""
Заменить связи рецепт–ингредиент для безалкогольных моктейлей (id 4000–4029 RUS, 4100–4129 ENG).

Проблема: в CSV non_alcoholic_recipes_with_ingredients.csv были неверные ingredient_id;
в PostgreSQL остались именно эти старые связи — в приложении по-прежнему «абрикосовый ликёр» и т.д.

Исправленные данные: файл non_alcoholic_recipe_ingredient.csv в корне репозитория cocktails.git
(пересобрать: python3 scripts/build_non_alcoholic_recipe_ingredient.py из корня репозитория).

Запуск из каталога с manage.py:
  python manage.py load_non_alcoholic_recipe_ingredients
  python manage.py load_non_alcoholic_recipe_ingredients --dry-run
  python manage.py load_non_alcoholic_recipe_ingredients --csv /path/to/non_alcoholic_recipe_ingredient.csv
"""
import csv
import os
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.recipe.models import RecipeIngredient, Ingredient


def _default_csv_path() -> Path:
    """Корень репозитория: .../cocktails.git/non_alcoholic_recipe_ingredient.csv"""
    base = Path(settings.BASE_DIR).resolve()
    # BASE_DIR = .../cocktails/backend/cocktails
    repo_root = base.parent.parent.parent
    return repo_root / "non_alcoholic_recipe_ingredient.csv"


MOCKTAIL_RECIPE_IDS = list(range(4000, 4030)) + list(range(4100, 4130))


class Command(BaseCommand):
    help = "Удалить старые RecipeIngredient для моктейлей и загрузить из non_alcoholic_recipe_ingredient.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            dest="csv_path",
            default=None,
            help="Путь к non_alcoholic_recipe_ingredient.csv (по умолчанию — корень репозитория)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать, что будет сделано, без записи в БД",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]) if options["csv_path"] else _default_csv_path()
        dry_run = options["dry_run"]

        if not csv_path.is_file():
            raise CommandError(
                f"Файл не найден: {csv_path}\n"
                "Укажите --csv или положите non_alcoholic_recipe_ingredient.csv в корень репозитория cocktails.git"
            )

        rows = []
        with csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(
                    {
                        "quantity": Decimal(row["quantity"]),
                        "type": row["type"].strip(),
                        "ingredient_id": int(row["ingredient_id"]),
                        "recipe_id": int(row["recipe_id"]),
                    }
                )

        ingredient_ids = {r["ingredient_id"] for r in rows}
        missing = sorted(iid for iid in ingredient_ids if not Ingredient.objects.filter(pk=iid).exists())
        if missing:
            raise CommandError(
                f"В БД нет ингредиентов с id: {missing[:20]}{'...' if len(missing) > 20 else ''}. "
                "Сначала импортируйте recipe_ingredient_catalog.csv в recipe_ingredient."
            )

        to_delete = RecipeIngredient.objects.filter(recipe_id__in=MOCKTAIL_RECIPE_IDS)
        delete_count = to_delete.count()

        self.stdout.write(f"CSV: {csv_path}")
        self.stdout.write(f"Строк в CSV: {len(rows)}")
        self.stdout.write(f"Удалить существующих связей (recipe_id в моктейлях): {delete_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY-RUN — запись отменена"))
            for r in rows[:5]:
                self.stdout.write(f"  пример: recipe={r['recipe_id']} ing={r['ingredient_id']} {r['quantity']} {r['type']}")
            if len(rows) > 5:
                self.stdout.write(f"  ... и ещё {len(rows) - 5} строк")
            return

        with transaction.atomic():
            deleted, _ = to_delete.delete()
            objs = [
                RecipeIngredient(
                    recipe_id=r["recipe_id"],
                    ingredient_id=r["ingredient_id"],
                    quantity=r["quantity"],
                    type=r["type"],
                )
                for r in rows
            ]
            RecipeIngredient.objects.bulk_create(objs, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"Удалено записей: {deleted}, создано: {len(objs)}"))
        self.stdout.write("Перезапустите API / обновите кэш клиента, если используется.")
