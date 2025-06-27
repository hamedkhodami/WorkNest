import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

from . import models


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        self.room_group_name = f'chat_{self.room_id}'

        self.room = await self.get_room()
        if not self.room:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data.get('message')

        if not content:
            return

        message = await self.save_message(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message['content'],
                'sender': message['sender'],
                'timestamp': message['timestamp']
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_room(self):
        try:
            room = models.ChatRoomModel.objects.prefetch_related('participants').get(id=self.room_id)
            if self.user in room.participants.all():
                return room
            return None
        except models.ChatRoomModel.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content):
        msg = models.MessageModel.objects.create(
            room=self.room,
            sender=self.user,
            content=content,
            is_read=False
        )
        return {
            'content': msg.content,
            'sender': self.user.full_name(),
            'timestamp': msg.created_at.strftime('%Y-%m-%d %H:%M')

        }
