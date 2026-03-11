from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class TicketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from apps.user.models import User
        logger.info(self.scope)
        query = self.scope['query_string'].decode()
        params = query.split('&')

        user_id = None
        ticket_id = None

        for param in params:
            if 'user_id=' in param:
                user_id = param.split('user_id=')[1]
            elif 'ticket_id=' in param:
                ticket_id = param.split('ticket_id=')[1]

        logger.info('user_id')
        logger.info(user_id)
        if user_id:
            try:
                self.user = await sync_to_async(User.objects.get)(id=user_id)
                logger.info('user')
                logger.info(self.user)
            except User.DoesNotExist:
                logger.info('User DoesNotExist')
                self.user = None
            except Exception as e:
                logger.error(f"Error while fetching user: {e}")
                self.user = None
        else:
            self.user = None

        if not self.user:
            logger.info('not authenticated')
            await self.close()
            return

        self.ticket_admin_id = None

        if self.user.is_staff:
            self.ticket_admin_id = ticket_id

        self.ticket, created = await self.get_or_create_ticket()
        self.ticket_group_name = f'ticket_{self.ticket.id}'

        await self.channel_layer.group_add(
            self.ticket_group_name,
            self.channel_name
        )

        await self.accept()

        history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'history': history
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'ticket_group_name'):
            logger.info(f"User disconnected, ticket_group_name: {self.ticket_group_name}")
            await self.channel_layer.group_discard(
                self.ticket_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'request_chat_history':
            history = await self.get_chat_history()
            await self.send(text_data=json.dumps({
                'type': 'chat_history',
                'history': history
            }))
        else:
            message = data['message']

            await self.save_message(self.user.id, message)

            await self.channel_layer.group_send(
                self.ticket_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': self.user.id,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'user_id': user_id,
        }))

    async def chat_history(self, event):
        history = event['history']

        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'history': history
        }))

    @sync_to_async
    def get_or_create_ticket(self):
        from apps.channel.models import Ticket
        if self.ticket_admin_id:
            ticket = Ticket.objects.get(id=self.ticket_admin_id)
            created = False
        else:
            ticket, created = Ticket.objects.get_or_create(
                user=self.user,
                status="open",
                defaults={
                    'subject': 'Support Ticket',
                    'description': 'Created via WebSocket',
                }
            )
        return ticket, created

    @sync_to_async
    def save_message(self, user_id, message):
        from apps.user.models import User
        from apps.channel.models import Message
        user = User.objects.get(id=user_id)
        Message.objects.create(user=user, ticket=self.ticket, content=message)

    @sync_to_async
    def get_chat_history(self):
        from apps.channel.models import Message
        messages = Message.objects.filter(ticket=self.ticket).order_by('timestamp')
        return [{
            'message': msg.content,
            'user_id': msg.user.id,
            'timestamp': msg.timestamp.isoformat()
        } for msg in messages]
