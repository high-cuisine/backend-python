from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if "@" in username:
            email = self.normalize_email(username)
            username = email
        else:
            username = username
            email = ""

        if 'email' not in extra_fields:
            extra_fields['email'] = email
        user = self.model(username=username, **extra_fields)
        if password is None:
            password = self.make_random_password()
        user.set_password(password)
        user.save()

        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self._create_user(username, password, **extra_fields)

    def get_queryset(self):
        return super().get_queryset()
