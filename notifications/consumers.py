from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle websocket connections for notifications.
    """

    async def connect(self):
        """
        Called when a websocket connection is initiated.
        Adds the user to a group for receiving notifications.
        """
        self.group_name = f'notifications_{self.scope["user"].id}'

        if self.scope["user"].is_anonymous:
            # Close the connection if the user is anonymous
            await self.close()
        else:
            # Add the user to the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            await self.update_user_status_in_db(self.scope["user"].id, True)
            await self.send_user_status(self.scope["user"].id, True)

    async def disconnect(self, close_code):
        """
        Called when the websocket connection is closed.
        Removes the user from the notifications group.
        """
        # Remove user from the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        # Update user status and notify others
        await self.update_user_status_in_db(self.scope["user"].id, False)
        await self.send_user_status(self.scope["user"].id, False)

    async def send_notification(self, event):
        """
        Sends a notification to the websocket.

        Args:
            event (dict): The event data containing the message to send.
        """
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message,
            'type': 'send_notification',
        }))

    async def send_user_status(self, user_id, is_online):
        """
        Sends a user status update to the WebSocket.

        Args:
            user_id (int): The ID of the user.
            is_online (bool): Whether the user is online.
        """
        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'is_online': is_online,
            'type': 'user_status',
        }))

    @staticmethod
    async def update_user_status_in_db(user_id, is_online):
        """
        Updates the user's online status in the database.

        Args:
            user_id (int): The ID of the user.
            is_online (bool): Whether the user is online.
        """
        from users.models import UserStatus  # Avoid circular imports
        from asgiref.sync import sync_to_async

        @sync_to_async
        def update_status():
            UserStatus.objects.filter(user_id=user_id).update(is_online=is_online)

        await update_status()