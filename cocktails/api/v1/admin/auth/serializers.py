from rest_framework import serializers
from apps.user.models import User
from base.backends import UsernameBackend

__all__ = [
    'AdminWebSignInRequestSerializer',
    'AdminRegisterUserSerializer',
]


class AdminWebSignInRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    class Meta:
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs: dict):
        self.authenticate(login=attrs['username'], password=attrs['password'])

        if self.user is None:
            raise serializers.ValidationError({'errors': ['Invalid login or password']})

        if not self.user.is_active:
            raise serializers.ValidationError({'errors': ['Your account has been deactivated by the administrator.']})

        if not self.user.is_staff:
            raise serializers.ValidationError({'errors': ['Not enough rights']})

        return attrs

    def authenticate(self, **kwargs):
        back = UsernameBackend()
        self.user: User = back.authenticate(**kwargs)


class AdminRegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
