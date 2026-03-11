from django.contrib import admin
from apps.recipe.models import *
from base.admin import BaseAdmin


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'quantity', 'type')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class IngredientCategoryInline(admin.TabularInline):
    model = IngredientCategorySection.categories.through
    extra = 1


@admin.register(IngredientCategorySection)
class IngredientCategorySectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'language']
    search_fields = ['name']
    inlines = [IngredientCategoryInline]
    exclude = ('categories',)


@admin.register(Recipe)
class RecipeAdmin(BaseAdmin):
    fieldsets = (
        (None, {'fields': ('language', 'title', 'isEnabled', 'is_alcoholic', 'user', 'moderation_status')}),
        ('Media Files', {'fields': ('photo', 'external_photo_url', 'video_url', 'video_aws_key')}),
        ('Информация', {'fields': ('description', 'instruction')}),
        ('Ингредиенты/Инструменты', {'fields': ('tools', )}),
    )
    list_filter = (
        'isEnabled',
        'moderation_status'
    )
    list_display = ('id', 'title', 'user', 'isEnabled', 'is_alcoholic', 'moderation_status', 'language')
    search_fields = ('title', 'user__username', 'user__email', 'user__phone')
    ordering = ('id',)
    inlines = [RecipeIngredientInline]

    change_list_template = 'admin/user_profile_change_list.html'


@admin.register(IngredientCategory)
class IngredientCategoryAdmin(BaseAdmin):
    list_display = ('id', 'name', 'language', 'is_main', 'is_alcoholic')
    search_fields = ('name', )
    ordering = ('id',)





@admin.register(Ingredient)
class IngredientAdmin(BaseAdmin):
    list_filter = (
        'category__name',
        'is_alcoholic'
    )
    list_display = ('id', 'name', 'language', 'description', 'category', 'is_alcoholic', 'get_recipes')
    search_fields = ('name', 'category__name')
    ordering = ('id',)

    def get_recipes(self, obj: Ingredient):
        return [recipe for recipe in obj.ingredient_recipes.all()]
    get_recipes.short_description = 'Recipes'


@admin.register(Tool)
class ToolAdmin(BaseAdmin):
    list_filter = ('name',)
    list_display = ('id', 'name', 'language', 'description', 'history', 'how_to_use', 'photo', 'links', 'get_recipes')
    search_fields = ('name',)
    ordering = ('id', )

    def get_recipes(self, obj: Tool):
        return [recipe.title for recipe in obj.recipes_tool.all()]
    get_recipes.short_description = 'Recipes'


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(BaseAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__title')
    ordering = ('id',)
