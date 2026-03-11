from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin


class BaseAdmin(admin.ModelAdmin):
    can_add = True
    can_change = True
    can_delete = True
    readonly = False

    def has_add_permission(self, request):
        if self.readonly or not self.can_add:
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if self.readonly or not self.can_change:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self.readonly or not self.can_delete:
            return False
        return super().has_delete_permission(request, obj)


class ListDisplayAdmin(BaseAdmin):

    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super().__init__(model, admin_site)


class ReadOnlyFieldsAdmin(InlineModelAdmin):
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseInline(InlineModelAdmin):
    readonly = False
    extra = 0

    def __init__(self, *args, **kwargs):
        if self.readonly:
            self.extra = 0
            self.readonly_fields = self.fields
        super().__init__(*args, **kwargs)

    def has_add_permission(self, request, obj):
        if self.readonly:
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self.readonly:
            return False
        return super().has_delete_permission(request, obj)

    def get_extra(self, request, obj=None, **kwargs):
        if self.readonly:
            return 0
        return super().get_extra(request, obj, **kwargs)


def short_description(description):
    """
    Sets 'short_description' attribute (this attribute is used by list_display).
    """

    def decorator(func):
        func.short_description = description
        return func

    return decorator


def order_field(field):
    """
    Sets 'admin_order_field' attribute (this attribute is used by list_display).
    """

    def decorator(func):
        func.admin_order_field = field
        return func

    return decorator
