from django.contrib import admin
from apps.reaction.models import Claim

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id')
    list_filter = ('user', 'content_type')
    search_fields = ('user__username', 'content_type__model', 'object_id')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'content_type', 'object_id')
        }),
    )
