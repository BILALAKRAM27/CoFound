import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from Entrepreneurs.models import Message, User
from asgiref.sync import sync_to_async
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        self.other_user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_name = self.get_room_name(self.user.id, self.other_user_id)
        self.room_group_name = f'chat_{self.room_name}'
        
        # Strict privacy enforcement - reject connection if not allowed
        allowed = await self.is_allowed(self.user.id, int(self.other_user_id))
        if not allowed:
            print(f"WebSocket connection rejected: User {self.user.id} cannot message user {self.other_user_id} due to privacy settings")
            await self.close(code=4001, reason="Privacy violation: User not allowed to message this user")
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'send_message':
            await self.handle_send_message(data)
        elif action == 'mark_read':
            await self.handle_mark_read(data)

    async def handle_send_message(self, data):
        content = data.get('content', '')
        message_type = data.get('message_type', 'text')
        file_data = data.get('file_data')  # base64 encoded, if any
        file_name = data.get('file_name')
        file_type = data.get('file_type')
        file_size = data.get('file_size')
        receiver_id = int(self.other_user_id)
        # Save message
        msg = await self.create_message(
            sender_id=self.user.id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            file_data=file_data,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size
        )
        if msg is None:
            return
        # Only send to group, not echo to sender as receiver
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': msg.id,
                    'content': msg.content,
                    'sender': msg.sender.id,
                    'receiver': msg.receiver.id,
                    'timestamp': msg.timestamp.isoformat(),
                    'is_read': msg.is_read,
                    'message_type': msg.message_type,
                    'file_name': msg.file_name,
                    'file_type': msg.file_type,
                    'file_size': msg.file_size,
                    'file_base64': msg.file_data.decode('utf-8') if msg.file_data else None
                },
                'sender_id': self.user.id
            }
        )

    async def handle_mark_read(self, data):
        message_ids = data.get('message_ids', [])
        await self.mark_messages_read(message_ids)
        # Optionally notify sender of read receipt
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_ids': message_ids,
                'reader_id': self.user.id
            }
        )

    async def chat_message(self, event):
        # Only send to the correct user (sender or receiver)
        message = event['message']
        sender_id = event.get('sender_id')
        # Only send to the user if they are sender or receiver
        if self.user.id == message['sender'] or self.user.id == message['receiver']:
            await self.send(text_data=json.dumps({
                'type': 'chat_message',
                'message': message
            }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_ids': event['message_ids'],
            'reader_id': event['reader_id']
        }))

    def get_room_name(self, user1_id, user2_id):
        """Create a unique room name for two users"""
        return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

    @database_sync_to_async
    def is_allowed(self, user_id, other_user_id):
        """Check if user can message the other user"""
        try:
            user = User.objects.get(id=user_id)
            other = User.objects.get(id=other_user_id)
            
            # Allow if other user is public
            if other.message_privacy == 'public':
                return True
            
            # Allow if either user follows the other (more permissive friendship)
            is_friend = (user.favorites.filter(target_user=other).exists() or
                         user.favorited_by.filter(user=other).exists())
            return is_friend
        except User.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, sender_id, receiver_id, content, message_type, file_data, file_name, file_type, file_size):
        """Create a new message"""
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
            
            # Double privacy enforcement - even though connection is protected
            if receiver.message_privacy == 'private':
                is_friend = (sender.favorites.filter(target_user=receiver).exists() or
                             sender.favorited_by.filter(user=receiver).exists())
                if not is_friend:
                    print(f"Privacy violation blocked: User {sender_id} attempted to message private user {receiver_id}")
                    return None
            
            msg = Message.objects.create(
                sender=sender,
                receiver=receiver,
                content=content,
                message_type=message_type,
                file_data=file_data.encode('utf-8') if file_data else None,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size
            )
            return msg
        except Exception as e:
            print(f"Error creating message: {e}")
            return None

    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """Mark messages as read"""
        try:
            Message.objects.filter(
                id__in=message_ids,
                receiver=self.user,
                is_read=False
            ).update(is_read=True)
        except Exception as e:
            print(f"Error marking messages as read: {e}")
