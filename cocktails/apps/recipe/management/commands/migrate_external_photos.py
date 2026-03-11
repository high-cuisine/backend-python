import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.recipe.models import Recipe
from urllib.parse import urlparse
from django.conf import settings


class Command(BaseCommand):
    help = 'Migrate external photos to local storage'

    def handle(self, *args, **options):
        recipes = Recipe.objects.exclude(photo__isnull=True).exclude(photo='')

        for recipe in recipes:
            if not recipe.photo.name.startswith(('http://', 'https://')):
                self.stdout.write(f"Skipping recipe {recipe.id} - already local photo")
                continue

            try:
                self.stdout.write(f"Processing recipe {recipe.id} with photo URL: {recipe.photo.name}")

                response = requests.get(recipe.photo.name, stream=True)
                response.raise_for_status()

                url_path = urlparse(recipe.photo.name).path
                filename = os.path.basename(url_path) or f"recipe_{recipe.id}.jpg"

                recipe.photo.save(
                    filename,
                    ContentFile(response.content),
                    save=True
                )

                self.stdout.write(self.style.SUCCESS(f"Successfully migrated photo for recipe {recipe.id}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing recipe {recipe.id}: {str(e)}"))

                recipe.photo = None
                recipe.save()
