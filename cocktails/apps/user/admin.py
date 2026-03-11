from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.user.models import *
from base.admin import BaseAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'phone', 'os')}),
        ('Личная информаця', {'fields': ('first_name', 'last_name', 'date_of_birth', 'avatar', 'gender')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser'
    )
    list_display = ('id', 'username', 'fio', 'date_joined', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name',)
    ordering = ('id',)

    change_list_template = 'admin/user_profile_change_list.html'

    @display(description='ФИ')
    def fio(self, obj: User):
        return f'{obj.last_name or ""} {obj.first_name or ""}'.strip()


@admin.register(TempCode)
class TempCodeAdmin(BaseAdmin):
    list_display = ('id', 'email', 'verification_code', 'created_at', 'verified')
    search_fields = ('id', 'email', 'verification_code', 'created_at', 'verified')
    ordering = ('id',)


@admin.register(Referral)
class ReferralAdmin(BaseAdmin):
    list_display = ('id', 'user', 'code', 'description')
    search_fields = ('user__email', 'code', 'user__username', 'user__phone')
    ordering = ('id',)


@admin.register(Point)
class PointAdmin(BaseAdmin):
    list_display = ('id', 'user', 'points', 'charge', 'text', 'created_at')
    search_fields = ('user__email', 'points', 'user__username', 'user__phone')
    ordering = ('id',)


@admin.register(Notification)
class NotificationAdmin(BaseAdmin):
    list_display = ('id', 'user', 'topik', 'topik_eng', 'message', 'message_eng', 'is_read', 'created_at')
    search_fields = ('user__email', 'topik', 'topik_eng', 'user__username', 'user__phone')
    ordering = ('-created_at',)