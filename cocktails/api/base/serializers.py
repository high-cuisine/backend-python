from rest_framework import serializers
from apps.user.models import User


class UserInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class BaseWithLikesSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    has_like = serializers.SerializerMethodField()
    has_dislike = serializers.SerializerMethodField()

    @staticmethod
    def get_likes_count(obj) -> int:
        return obj.likes_count if hasattr(obj, 'likes_count') else 0  # noqa

    @staticmethod
    def get_dislikes_count(obj) -> int:
        return obj.dislikes_count if hasattr(obj, 'dislikes_count') else 0  # noqa

    @staticmethod
    def get_has_like(obj) -> bool:
        return obj.has_like if hasattr(obj, 'has_like') else 0  # noqa

    @staticmethod
    def get_has_dislike(obj) -> bool:
        return obj.has_dislike if hasattr(obj, 'has_dislike') else 0  # noqa


class BaseWithCommentsSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    @staticmethod
    def get_comments_count(obj) -> int:
        return obj.comments_count if hasattr(obj, 'comments_count') else 0  # noqa


class BaseFIOSerializer(serializers.ModelSerializer):
    fio = serializers.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = User.objects.filter(profiles=instance).values('first_name', 'last_name', 'middle_name').first()
        data['fio'] = f'{user["last_name"]} {user["first_name"]} {user["middle_name"]}'.strip()
        return data

    @property
    def _readable_fields(self):
        for field in self.fields.values():
            if not field.write_only and field.field_name != 'fio':
                yield field

    @staticmethod
    def get_split_fio(fio):
        fio_list = fio.split()
        last_name = ''
        middle_name = ''
        if len(fio_list) == 1:
            first_name = fio_list[0]
        else:
            last_name, first_name = fio_list[:2]
            if len(fio_list) > 2:
                middle_name = ' '.join(fio_list[2:])

        return first_name, last_name, middle_name

    def update_fio_data(self, validated_data, instance=None):
        if 'fio' not in validated_data:
            return

        first_name, last_name, middle_name = self.get_split_fio(validated_data.pop('fio'))
        if instance and hasattr(instance, 'user'):
            user: User = instance.user
        else:
            user: User = validated_data.get('user') or self.context['request'].user
        user.first_name = first_name
        user.last_name = last_name
        user.middle_name = middle_name
        user.save(update_fields=['first_name', 'last_name', 'middle_name'])

    def create(self, validated_data):
        self.update_fio_data(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self.update_fio_data(validated_data, instance=instance)
        return super().update(instance, validated_data)
