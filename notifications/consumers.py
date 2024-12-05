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

    async def disconnect(self, close_code):
        """
        Called when the websocket connection is closed.
        Removes the user from the notifications group.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        """
        Sends a notification to the websocket.
        
        Args:
            event (dict): The event data containing the message to send.
        """
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
