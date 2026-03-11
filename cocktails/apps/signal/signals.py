from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.user.models import Point, Notification, User
from apps.recipe.models import Recipe
from apps.channel.models import Message
from apps.goods.models import Goods
from apps.common.models import Mailing, Config


@receiver(post_save, sender=Point)
def create_notification_for_point(sender, instance, created, **kwargs):
    if created and not instance.charge:
        Notification.objects.create(
            user=instance.user,
            topik="Начисление баллов",
            topik_eng="Accrual of points",
            message_eng=f"You've been awarded {instance.points} points.",
            message=f"Вам начислено {instance.points} баллов.",
            is_read=False
        )


@receiver(post_save, sender=Recipe)
def create_notification_for_recipe_approval(sender, instance, **kwargs):
    if instance.moderation_status == 'Approved' and instance.user:
        Notification.objects.create(
            user=instance.user,
            topik="Рецепт одобрен",
            topik_eng="Recipe approved",
            message_eng=f"Your recipe '{instance.title}' has been published.",
            message=f"Ваш рецепт '{instance.title}' был опубликован.",
            is_read=False
        )

        if instance.user:
            try:
                cost = Config.objects.get(code='write_recipe')
                cost = int(cost.value)
            except Config.DoesNotExist:
                cost = 100

            Point.objects.create(user=instance.user, text='Рецепт коктейля одобрен', points=cost, charge=False)

        other_users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False).exclude(
            id=instance.user.id)
        for user in other_users:
            Notification.objects.create(
                user=user,
                topik="Новый рецепт",
                topik_eng="New Recipe",
                message_eng=f"The new recipe '{instance.title}' has been added.",
                message=f"Новый рецепт '{instance.title}' был добавлен.",
                is_read=False
            )


@receiver(post_save, sender=Message)
def create_notification_for_new_message(sender, instance, created, **kwargs):
    if created:
        if instance.user != instance.ticket.user:
            Notification.objects.create(
                user=instance.ticket.user,
                topik="Новое сообщение",
                topik_eng="New message",
                message_eng=f"You have a new message on the '{instance.ticket.subject}' ticket.",
                message=f"У вас новое сообщение по тикету '{instance.ticket.subject}'.",
                is_read=False
            )


@receiver(post_save, sender=Goods)
def create_notification_for_new_good(sender, instance, created, **kwargs):
    if created:
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        for user in users:
            Notification.objects.create(
                user=user,
                topik="Новый товар",
                topik_eng="New product",
                message_eng=f"Added a new product: '{instance.name}' to the store.",
                message=f"Добавлен новый товар: '{instance.name}' в магазин.",
                is_read=False
            )


@receiver(post_save, sender=Mailing)
def create_notification_for_mailing(sender, instance, created, **kwargs):
    if created:
        users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
        if instance.url:
            message = f'{instance.description}. Ссылка: {instance.url}'
            message_eng = f'{instance.description_eng}. URL: {instance.url}'
        else:
            message = instance.description
            message_eng = instance.description_eng
        for user in users:
            Notification.objects.create(
                user=user,
                topik=instance.title,
                topik_eng=instance.title_eng,
                message_eng=message_eng,
                message=message,
                is_read=False
            )
