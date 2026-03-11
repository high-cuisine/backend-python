from rest_framework import permissions


class TeacherPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_superuser or request.user.roles.filter(name__in=['Учитель']).exists()
