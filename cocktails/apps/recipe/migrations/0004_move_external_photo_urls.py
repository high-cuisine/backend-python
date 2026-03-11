# Data migration to move external URLs from photo to external_photo_url

from django.db import migrations
from django.db.models import Q


def move_external_urls(apps, schema_editor):
    Recipe = apps.get_model('recipe', 'Recipe')
    
    # Find recipes with external URLs in photo field
    external_url_recipes = Recipe.objects.filter(
        Q(photo__startswith='http://') | 
        Q(photo__startswith='https://') |
        Q(photo__contains='http%3A') |  # URL-encoded HTTP
        Q(photo__contains='https%3A')  # URL-encoded HTTPS
    )
    
    moved_count = 0
    for recipe in external_url_recipes:
        # Move URL to external field
        recipe.external_photo_url = recipe.photo
        # Clear the photo field
        recipe.photo = None
        recipe.save()
        moved_count += 1
    
    print(f"Migrated {moved_count} recipes with external URLs")


def reverse_move_external_urls(apps, schema_editor):
    Recipe = apps.get_model('recipe', 'Recipe')
    
    # Move back external URLs to photo field (for rollback)
    recipes_with_external = Recipe.objects.filter(
        external_photo_url__isnull=False
    ).exclude(external_photo_url='')
    
    moved_count = 0
    for recipe in recipes_with_external:
        recipe.photo = recipe.external_photo_url
        recipe.external_photo_url = None
        recipe.save()
        moved_count += 1
        
    print(f"Rolled back {moved_count} recipes to photo field")


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0003_recipe_external_photo_url'),
    ]

    operations = [
        migrations.RunPython(
            move_external_urls,
            reverse_move_external_urls
        ),
    ]
