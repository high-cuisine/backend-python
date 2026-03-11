from rest_framework.permissions import IsAuthenticated
from apps.user.models import User


class IsActiveUser(IsAuthenticated):
    def has_permission(self, request, view):
        user: User = request.user
        if not user.is_active:
            return False

        return user is not None and user.is_active


class IsAdmin(IsActiveUser):
    def has_permission(self, request, view):
        result = super().has_permission(request, view)
        return result and request.user.is_admin


class IsManager(IsActiveUser):
    def has_permission(self, request, view):
        result = super().has_permission(request, view)
        return result and request.user.is_manager
