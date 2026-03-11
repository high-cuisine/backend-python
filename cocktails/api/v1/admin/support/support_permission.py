from rest_framework import permissions


class SupportPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action == 'list':
            required_permission = 'channel.view_ticket'
            return request.user.has_perm(required_permission)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action == 'update' or view.action == 'partial_update':
            required_permission = 'channel.change_ticket'
            return request.user.has_perm(required_permission)
