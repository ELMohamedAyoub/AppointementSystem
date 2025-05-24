import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_group_name = f'user_{self.user.id}_notifications'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications count on connect
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            if notification_id:
                success = await self.mark_notification_read(notification_id)
                await self.send(text_data=json.dumps({
                    'type': 'mark_read_response',
                    'success': success,
                    'notification_id': notification_id
                }))
            
            # Send updated unread count
            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': count
            }))
    
    # Receive message from room group
    async def notification_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def get_unread_count(self):
        return self.user.notifications.filter(is_read=False).count()
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        try:
            notification = self.user.notifications.get(id=notification_id)
            notification.is_read = True
            notification.save()
            return True
        except Exception:
            return False 