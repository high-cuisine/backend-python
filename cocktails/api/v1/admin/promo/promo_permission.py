from rest_framework import permissions


class PromoPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if view.action == 'list':
            required_permission = 'goods.view_promo'
            return request.user.has_perm(required_permission)

        elif view.action == 'create':
            required_permission = 'goods.add_promo'
            return request.user.has_perm(required_permission)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if view.action == 'update' or view.action == 'partial_update':
            required_permission = 'goods.change_promo'
            return request.user.has_perm(required_permission)

        if view.action == 'delete':
            required_permission = 'goods.delete_promo'
            return request.user.has_perm(required_permission)