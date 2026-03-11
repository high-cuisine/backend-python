from django.db import models
from apps.user.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

__all__ = [
    'Ticket',
    'Message',
]


class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Message)
def update_ticket_timestamp(sender, instance, **kwargs):
    ticket = instance.ticket
    ticket.save()
