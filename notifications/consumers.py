from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle websocket connections for notifications.
    """

    async def connect(self):
        """
        Called when a websocket connection is initiated.
        Updates the user's online status in the database.
        """
        self.user_id = self.scope["user"].id

        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            # Add user to WebSocket group
            await self.channel_layer.group_add(
                "notifications",
                self.channel_name
            )
            await self.accept()

            # Update user status in database
            await self.update_user_status(self.user_id, is_online=True)
            await self.send_user_status(self.user_id, is_online=True)

    async def disconnect(self, close_code):
        """
        Called when the websocket connection is closed.
        Updates the user's online status in the database.
        """
        # Remove user from WebSocket group
        await self.channel_layer.group_discard(
            "notifications",
            self.channel_name
        )

        # Update user status in database
        await self.update_user_status(self.user_id, is_online=False)
        await self.send_user_status(self.user_id, is_online=False)

    async def send_notification(self, event):
        """
        Sends a notification to the websocket.

        Args:
            event (dict): The event data containing the message to send.
        """
        message = event["message"]
        await self.send(text_data=json.dumps({
            "message": message,
            "type": "send_notification",
        }))

    async def send_user_status(self, user_id, is_online):
        """
        Sends a user status update to the WebSocket.

        Args:
            user_id (int): The ID of the user.
            is_online (bool): Whether the user is online.
        """
        await self.send(text_data=json.dumps({
            "user_id": user_id,
            "is_online": is_online,
            "type": "user_status",
        }))

    @staticmethod
    async def update_user_status(user_id, is_online):
        """
        Updates the user's online status in the database.

        Args:
            user_id (int): The ID of the user.
            is_online (bool): Whether the user is online.
        """
        from users.models import User
        from asgiref.sync import sync_to_async

        @sync_to_async
        def update_status():
            user = User.objects.get(id=user_id)
            user.is_online = is_online
            user.save(update_fields=["is_online"])

        await update_status()
