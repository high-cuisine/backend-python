import logging
from django.db import models
from apps.user.models import User, Notification
from base.models import BaseModel, CreatedUpdatedModel
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericRelation
from apps.reaction.models import Claim


__all__ = [
    'IngredientCategory',
    'Ingredient',
    'IngredientCategorySection',
    'Tool',
    'Recipe',
    'FavoriteRecipe',
    'RecipeIngredient',
]

logger = logging.getLogger(__name__)


class IngredientCategory(CreatedUpdatedModel):
    LANG_CHOICES = [
        ('ENG', 'Английский'),
        ('RUS', 'Русский'),
    ]

    language = models.CharField(
        max_length=20,
        choices=LANG_CHOICES,
        default='RUS',
        verbose_name='Язык'
    )

    name = models.CharField(max_length=255, unique=True, db_index=True, verbose_name='Название категории')
    is_main = models.BooleanField(default=False, verbose_name='Основная?')
    is_alcoholic = models.BooleanField(default=False, verbose_name='Алкогольный?')

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория ингредиента'
        verbose_name_plural = 'Категории ингредиентов'

    def __str__(self):
        return self.name


class IngredientCategorySection(CreatedUpdatedModel):
    LANG_CHOICES = [
        ('ENG', 'Английский'),
        ('RUS', 'Русский'),
    ]

    language = models.CharField(
        max_length=20,
        choices=LANG_CHOICES,
        default='RUS',
        verbose_name='Язык'
    )
    name = models.CharField(max_length=255, verbose_name='Название блока категорий')
    categories = models.ManyToManyField(IngredientCategory, related_name='category_blocks', verbose_name='Категории')

    class Meta:
        verbose_name = 'Блок категорий'
        verbose_name_plural = 'Блоки категорий'

    def __str__(self):
        return self.name



class Ingredient(CreatedUpdatedModel):
    LANG_CHOICES = [
        ('ENG', 'Английский'),
        ('RUS', 'Русский'),
    ]

    language = models.CharField(
        max_length=20,
        choices=LANG_CHOICES,
        default='RUS',
        verbose_name='Язык'
    )

    name = models.CharField(max_length=255, db_index=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        IngredientCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingredients',
        verbose_name='Категория'
    )
    is_alcoholic = models.BooleanField(default=False, verbose_name='Алкогольный?')

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Tool(CreatedUpdatedModel):
    LANG_CHOICES = [
        ('ENG', 'Английский'),
        ('RUS', 'Русский'),
    ]

    language = models.CharField(
        max_length=20,
        choices=LANG_CHOICES,
        default='RUS',
        verbose_name='Язык'
    )

    name = models.CharField(max_length=255, db_index=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    history = models.TextField(null=True, blank=True, verbose_name='История')
    how_to_use = models.TextField(null=True, blank=True, verbose_name='Как использовать')
    photo = models.ImageField(upload_to='tool_photos/', null=True, blank=True, verbose_name='Фото')
    links = ArrayField(models.URLField(), null=True, blank=True, verbose_name='Ссылки')

    class Meta:
        ordering = ['id']
        verbose_name = 'Инструмент'
        verbose_name_plural = 'Инструменты'

    def __str__(self):
        return '{}'.format(self.name)


class Recipe(BaseModel):
    MODERATION_STATUS_CHOICES = [
        ('Draft', 'Черновик'),
        ('Pending', 'На модерации'),
        ('Approved', 'Одобрено'),
        ('Rejected', 'Отклонено'),
        ('Archive', 'Архив')
    ]

    LANG_CHOICES = [
        ('ENG', 'Английский'),
        ('RUS', 'Русский'),
    ]

    title = models.CharField(max_length=255, db_index=True, verbose_name='Название')
    description = models.TextField(null=True, blank=True, verbose_name='Описание')
    instruction = models.JSONField(null=True, blank=True, verbose_name='Инструкция')
    isEnabled = models.BooleanField(default=False, verbose_name='Доступен?')
    photo = models.ImageField(upload_to='recipes/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes_user', verbose_name='Пользователь')
    tools = models.ManyToManyField(Tool, blank=True, related_name='recipes_tool', verbose_name='Инструменты')
    is_alcoholic = models.BooleanField(default=True, verbose_name='Алкогольный?')

    language = models.CharField(
        max_length=20,
        choices=LANG_CHOICES,
        default='RUS',
        verbose_name='Язык'
    )

    moderation_status = models.CharField(
        max_length=10,
        choices=MODERATION_STATUS_CHOICES,
        default='Draft',
        verbose_name='Статус модерации'
    )

    video_url = models.URLField(null=True, blank=True, verbose_name='Ссылка на видео')
    video_aws_key = models.CharField(null=True, blank=True, default=None, max_length=255,  verbose_name='Ключ файла от aws s3 ')
    external_photo_url = models.URLField(null=True, blank=True, verbose_name='External Photo URL', help_text='URL for external images (e.g., Google Drive, CDN)')

    claims = GenericRelation(Claim)

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return '{}'.format(self.title)


class RecipeIngredient(models.Model):
    MEASURE = [
        ('ounce', 'унция'),
        ('ml', 'мл'),
        ('gram', 'грамм'),
        ('piece', 'шт'),
        ('spoon', 'ложка'),
        ('cup', 'кружка'),
        ('tablespoon', 'столовая ложка'),
        ('teaspoon', 'чайная ложка'),
        ('slice', 'ломтик'),
        ('twist', 'твист'),
        ('cube', 'кубик'),
        ('sprig', 'веточка'),
        ('pinch', 'щепотка'),
        ('spiral', 'спираль'),
        ('wedge', 'долька'),
        ('dash', 'дэш'),
        ('block', 'блок'),
        ('circle', 'кружок'),
        ('bottle', 'бутылка'),
    ]
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Количество')
    type = models.CharField(
        max_length=30,
        choices=MEASURE,
        default='ounce',
        verbose_name='Мера'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f'{self.quantity} of {self.ingredient.name} in {self.recipe.title}'


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'