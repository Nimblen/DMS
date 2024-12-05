from django.shortcuts import redirect
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from notifications.models import Notification






class NotificationListView(LoginRequiredMixin, ListView):
    """
    View for listing user notifications. Inherits from LoginRequiredMixin and ListView.

    Attributes:
        model (Notification): The model for the view.
        template_name (str): The template to render.
        context_object_name (str): The context object name for the template.
    """
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        """
        Return the queryset of notifications for the current user.

        Returns:
            QuerySet: The notifications for the current user.
        """
        return self.request.user.notifications.all()
    
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to mark all user notifications as read
        and redirects back to the notification list.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            HttpResponseRedirect: Redirects to the notification list view.
        """
        self.request.user.notifications.filter(is_read=False).update(is_read=True)
        return redirect('notifications:notification_list')
