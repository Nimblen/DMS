from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from notifications.models import Notification


class NotificationService:
    """
    Service for creating and sending notifications to users.
    """

    def __init__(self, channel_layer=None):
        """
        Initialize the service with a channel layer.

        Args:
            channel_layer (optional): The channel layer to use for sending
                websocket messages. Defaults to the default channel layer.
        """
        if channel_layer is None:
            channel_layer = get_channel_layer()
        self.channel_layer = channel_layer

    def create_notification(self, user_id: int, message: str, is_read=False):
        """
        Create a new notification for a user.

        Args:
            user_id (int): The id of the user to create the notification for.
            message (str): The message for the notification.
            is_read (bool): Whether the notification is read or not.

        Returns:
            Notification: The created notification.
        """
        User = get_user_model()
        user = User.objects.get(id=user_id)
        return Notification.objects.create(
            user=user,
            message=message,
            is_read=is_read,
        )

    def send_websocket_notification(self, group_name: str, message_data: dict):
        """
        Send a websocket message to a group.

        Args:
            group_name (str): The name of the group to send the message to.
            message_data (dict): The data to send in the message.
        """
        async_to_sync(self.channel_layer.group_send)(group_name, message_data)

    def notify_user(
        self,
        user_id: int,
        message: str,
        ms_type: str = "send_notification",
        save_to_db=True,
        send_to_ws=True,
    ):
        """
        Notify a user with a message.

        Args:
            user_id (int): The id of the user to notify.
            message (str): The message for the notification.
            ms_type (str): The type of message to send. Defaults to
                "send_notification".
            save_to_db (bool): Whether to save the notification to the database.
                Defaults to True.
            send_to_ws (bool): Whether to send the notification over the websocket.
                Defaults to True.
        """
        if save_to_db:
            self.create_notification(user_id, message)
        if send_to_ws:
            self.send_websocket_notification(
                group_name=f"notifications_{user_id}",
                message_data={"type": ms_type, "message": message},
            )

