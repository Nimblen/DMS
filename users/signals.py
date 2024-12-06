from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from users.models import RoleRequest, User, UserStatus
from notifications.utils import NotificationService


notification_sender = NotificationService()


@receiver(post_save, sender=RoleRequest)
def notify_admins_on_role_request(sender, instance, created, **kwargs):
    """
    Notify all superusers about new role request.
    """
    if created:
        admins = User.objects.filter(is_superuser=True)
        message = f"Пользователь {instance.user.username} запрашивает изменение роли на {instance.get_requested_role_display()}."
        for admin in admins:
            notification_sender.notify_user(admin.id, message)


@receiver(pre_save, sender=RoleRequest)
def save_old_is_approved(sender, instance, **kwargs):
    """
    Save old value of is_approved field to be able to check if it has changed.
    """
    if instance.pk:
        try:
            instance._old_is_approved = RoleRequest.objects.get(
                pk=instance.pk
            ).is_approved
        except RoleRequest.DoesNotExist:
            instance._old_is_approved = None
    else:
        instance._old_is_approved = None


@receiver(post_save, sender=RoleRequest)
def notify_user_on_role_request_update(sender, instance, **kwargs):
    """
    Notify user about role request update results.
    """
    if hasattr(instance, "_old_is_approved"):
        old_is_approved = instance._old_is_approved
        new_is_approved = instance.is_approved
        if old_is_approved != new_is_approved and new_is_approved is not None:
            if new_is_approved:
                message = (
                    f"Ваш запрос на изменение роли на «{instance.get_requested_role_display()}» был <<одобрен>>."
                )
                user = instance.user
                user.role = instance.requested_role
                user.save()
            else:
                message = (
                    f"Ваш запрос на изменение роли на «{instance.get_requested_role_display()}» был <<отклонен>>."
                )
            notification_sender.notify_user(instance.user.id, message)




@receiver(post_save, sender=User)
def create_user_status(sender, instance, created, **kwargs):
    if created:
        UserStatus.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_status(sender, instance, **kwargs):
    instance.status.save() 