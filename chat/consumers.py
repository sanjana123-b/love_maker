import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from matching.models import Match
from .models import Message, MessageReaction


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'chat_{self.match_id}'
        self.user = self.scope['user']

        # Reject unauthenticated connections
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verify user is a member of this active match
        is_member = await self.verify_match_membership(self.match_id, self.user)
        if not is_member:
            await self.close(code=4003)
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action', 'chat_message')

            if action == 'chat_message':
                content = data.get('content', '').strip()
                if content:
                    msg = await self.save_message(self.match_id, self.user, content)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message_broadcast',
                            'message_id': msg.id,
                            'sender_id': self.user.id,
                            'sender_name': self.user.first_name or self.user.username,
                            'content': msg.content,
                            'timestamp': msg.timestamp.strftime('%I:%M %p'),
                            'is_read': False,
                        }
                    )

            elif action == 'typing_status':
                is_typing = bool(data.get('is_typing', False))
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_broadcast',
                        'sender_id': self.user.id,
                        'is_typing': is_typing,
                    }
                )

            elif action == 'read_receipt':
                await self.mark_messages_as_read(self.match_id, self.user)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_receipt_broadcast',
                        'read_by_id': self.user.id,
                    }
                )

            elif action == 'reaction':
                message_id = data.get('message_id')
                emoji = data.get('emoji', '❤️')
                if message_id:
                    added = await self.toggle_reaction(message_id, self.user, emoji)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'reaction_broadcast',
                            'message_id': message_id,
                            'user_id': self.user.id,
                            'emoji': emoji,
                            'added': added,
                        }
                    )

        except Exception as e:
            pass

    # Group message broadcast handlers
    async def chat_message_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read'],
        }))

    async def typing_broadcast(self, event):
        # Don't echo typing events back to the sender
        if event['sender_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_status',
                'sender_id': event['sender_id'],
                'is_typing': event['is_typing'],
            }))

    async def read_receipt_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'read_by_id': event['read_by_id'],
        }))

    async def reaction_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'emoji': event['emoji'],
            'added': event['added'],
        }))

    # Database Helpers
    @database_sync_to_async
    def verify_match_membership(self, match_id, user):
        return Match.objects.filter(
            id=match_id,
            is_active=True
        ).filter(
            models.Q(user1=user) | models.Q(user2=user)
        ).exists()

    @database_sync_to_async
    def save_message(self, match_id, sender, content):
        match = Match.objects.get(id=match_id)
        return Message.objects.create(match=match, sender=sender, content=content)

    @database_sync_to_async
    def mark_messages_as_read(self, match_id, reading_user):
        match = Match.objects.get(id=match_id)
        other_user = match.get_other_user(reading_user)
        return Message.objects.filter(match=match, sender=other_user, is_read=False).update(is_read=True)

    @database_sync_to_async
    def toggle_reaction(self, message_id, user, emoji):
        message = Message.objects.get(id=message_id)
        existing = MessageReaction.objects.filter(message=message, user=user, emoji=emoji).first()
        if existing:
            existing.delete()
            return False
        else:
            MessageReaction.objects.create(message=message, user=user, emoji=emoji)
            return True
