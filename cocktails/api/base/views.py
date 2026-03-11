from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Exists, OuterRef, Q
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from api.base.permissions import IsAdmin
from apps.reaction.models import Like


class BaseGenericViewSet(GenericViewSet):
    # Решили полностью убрать PUT запросы во вьюсетах и оставить только PATCH,
    # т. к. он удобнее тем, что не обязательно передавать все поля сериалайзера и сваггер будет менее громоздким
    http_method_names = ['get', 'post', 'patch', 'delete', 'options']
    create_serializer_class = None
    update_serializer_class = None
    list_serializer_class = None
    retrieve_serializer_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for action in ('create', 'update', 'list', 'retrieve'):
            field_name = f'{action}_serializer_class'
            if not getattr(self, field_name, None):
                setattr(self, field_name, self.serializer_class)
            elif not self.serializer_class:
                self.serializer_class = getattr(self, field_name)

    def get_serializer_class(self):
        if self.action == 'create':
            return self.create_serializer_class
        if self.action in ['update', 'partial_update']:
            return self.update_serializer_class
        if self.action == 'list':
            return self.list_serializer_class
        if self.action == 'retrieve':
            return self.retrieve_serializer_class
        return super().get_serializer_class()


class BulkCreateModelMixin(mixins.CreateModelMixin):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True, allow_empty=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class BaseContentTypeViewMixin:
    content_type = None

    def __init__(self, *args, **kwargs):
        self.content_type = ContentType.objects.get_for_model(self.queryset.model)
        super().__init__(*args, **kwargs)


class WithLikesViewMixin(BaseContentTypeViewMixin):
    def get_queryset(self):
        qs = super().get_queryset()

        if self.request.user.is_anonymous:
            return qs

        like_sq = Like.objects.filter(object_id=OuterRef('id'), content_type=self.content_type, user=self.request.user)
        return qs.select_related('user').annotate(
            likes_count=Count('likes', filter=Q(likes__value=True)),
            dislikes_count=Count('likes', filter=Q(likes__value=False)),
            has_like=Exists(like_sq.filter(value=True)),
            has_dislike=Exists(like_sq.filter(value=False)),
        )


class AdminGenericViewSet(BaseGenericViewSet):
    permission_classes = [IsAdmin]
