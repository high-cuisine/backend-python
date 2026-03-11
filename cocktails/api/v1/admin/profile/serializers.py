from rest_framework import serializers
from apps.user.models import *
from apps.recipe.models import *
from django.db.models import Sum
from api.v1.recipe.serializers import RecipeDetailSerializer
from django.contrib.auth.hashers import make_password

__all__ = [
    'AdminUserSerializer',
    'AdminUserUpdateSerializer',
    'AdminUserCreateSerializer',
]


class AdminUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'os',
            'is_staff',
            'date_of_birth',
            'password',
            'first_name',
            'last_name',
            'is_active',
            'gender',
            'phone',
            'avatar',
            'user_permissions',
            'date_joined'
        ]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    avatar = serializers.FileField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)
    is_staff = serializers.BooleanField(write_only=True, required=False)
    is_active = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'os',
            'is_staff',
            'date_of_birth',
            'password',
            'first_name',
            'last_name',
            'is_active',
            'gender',
            'phone',
            'avatar',
            'user_permissions'
        ]

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user_permissions = validated_data.pop('user_permissions', [])

        if len(user_permissions) > 0:
            instance.user_permissions.set(user_permissions)

        if password:
            instance.password = make_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'is_staff',
            'os',
            'date_of_birth',
            'password',
            'first_name',
            'last_name',
            'is_active',
            'gender',
            'phone',
            'avatar',
            'user_permissions'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_permissions = validated_data.pop('user_permissions', [])

        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)

        if len(user_permissions) > 0:
            user.user_permissions.set(user_permissions)

        user.save()
        return user
