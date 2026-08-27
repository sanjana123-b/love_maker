import json
from channels.generic.websocket import AsyncWebsocketConsumer

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'
        
        # User must be authenticated to join a call
        if self.scope["user"].is_anonymous:
            await self.close()
            return
            
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others that this user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_message',
                'message': {
                    'type': 'peer_left',
                    'username': self.scope["user"].username
                }
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Broadcasting the WebRTC signaling message to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'call_message',
                'message': data,
                'sender_channel_name': self.channel_name
            }
        )

    async def call_message(self, event):
        message = event['message']
        sender_channel_name = event.get('sender_channel_name')
        
        # Don't echo the message back to the sender
        if sender_channel_name != self.channel_name:
            await self.send(text_data=json.dumps(message))
