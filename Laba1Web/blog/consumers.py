import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from django.contrib.auth import models as auth_models
from .models import BlogUser

from .models import ConnectedUser


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "global_chat"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        if isinstance(self.scope['user'], auth_models.User):
            ConnectedUser.objects.update_or_create(user=self.scope['user'])
            self.username = self.scope['user'].username
            self.user_pk = self.scope['user'].pk
            self.accept()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': "User %s has joined chat" % self.username,
                    'sender': 'System',
                    'class': 'system'
                }
            )

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "%s has left the chat" % self.username,
                'sender': 'System',
                'class': 'system'
            }
        )
        ConnectedUser.objects.filter(user__pk=self.user_pk).delete()

    def receive(self, text_data):
        data = json.loads(text_data)
        try:
            # data['sender'] = data['sender'].strip('"')
            user = auth_models.User.objects.get(username=data['sender'])   # username=data['sender']
            if user.is_staff:
                data['class'] = 'admin'
            else:
                data['class'] = 'user'
            data['sender'] = user.username
            data['type'] = 'chat_message'
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                data
            )
        except auth_models.User.DoesNotExist:
            pass

    def chat_message(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': event['message'],
            'author': event['sender'],  # renamed to distinct
            'class': event['class'],
        }))
