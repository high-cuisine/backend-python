from celery import shared_task

from apps.recipe.models import Recipe
from main_core import settings
from services.s3_client import S3Client
from services.youtube_api_client import YouTubeApiClient

s3_client = S3Client(
    access_key=settings.AWS_ACCESS_KEY,
    secret_key=settings.AWS_SECRET_KEY
)

youtube_api_client = YouTubeApiClient()


@shared_task
def publish_video_from_aws(s3_key: str, recipe_id: int):
    recipe: Recipe = Recipe.objects.filter(id=recipe_id).first()
    s3_video = s3_client.get_video_file(bucket_name=settings.AWS_BUCKET_NAME, s3_key=s3_key)
    youtube_video = youtube_api_client.upload_video(
        video_stream=s3_video,
        title=recipe.title,
        description=recipe.description if recipe.description else 'No description',
        tags=['Коктейль', 'cocktail', recipe.title]
    )
    recipe.video_url = youtube_video
    recipe.save()

    return recipe
