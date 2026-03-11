from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


filter_params = [
    openapi.Parameter(
        'q',
        openapi.IN_QUERY,
        description="Search by recipe name and ingredient name. Multiple word searches are supported.",
        type=openapi.TYPE_STRING
    ),
    openapi.Parameter(
        'ingredients',
        openapi.IN_QUERY,
        description="Filtering by main ingredient ID (multiple IDs with a hyphen, e.g. 12-5-56).",
        type=openapi.TYPE_STRING
    ),
    openapi.Parameter(
        'tools',
        openapi.IN_QUERY,
        description="Filtering by instrument ID (multiple IDs with a hyphen, e.g., 12-5-56).",
        type=openapi.TYPE_STRING
    ),
    openapi.Parameter(
        'ordering',
        openapi.IN_QUERY,
        description="Sort by recipe title (title) or video availability (video_url). Add a '-' in front of the field to sort by descending order.",
        type=openapi.TYPE_STRING,
        enum=['title', '-title', 'video_url', '-video_url']
    ),
    openapi.Parameter(
        'other_ingredients',
        openapi.IN_QUERY,
        description="Filtering by other ingredient ID (multiple IDs with a hyphen, e.g. 12-5-56).",
        type=openapi.TYPE_STRING
    ),
]