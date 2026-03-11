from rest_framework import permissions


class ProfilePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action == 'list':
            required_permission = 'user.view_user'
            return request.user.has_perm(required_permission)

        elif view.action == 'create':
            required_permission = 'user.add_user'
            return request.user.has_perm(required_permission)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if obj.is_superuser:
            return False

        if obj.user == request.user:
            return False

        if view.action == 'update' or view.action == 'partial_update':
            required_permission = 'user.change_user'
            return request.user.has_perm(required_permission)

        if view.action == 'delete':
            required_permission = 'user.delete_user'
            return request.user.has_perm(required_permission)
