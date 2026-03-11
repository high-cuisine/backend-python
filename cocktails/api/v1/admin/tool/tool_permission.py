from rest_framework import permissions


class ToolPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action == 'list':
            required_permission = 'recipe.view_tool'
            return request.user.has_perm(required_permission)

        elif view.action == 'create':
            required_permission = 'recipe.add_tool'
            return request.user.has_perm(required_permission)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action == 'update' or view.action == 'partial_update':
            required_permission = 'recipe.change_tool'
            return request.user.has_perm(required_permission)

        if view.action == 'delete':
            required_permission = 'recipe.delete_tool'
            return request.user.has_perm(required_permission)