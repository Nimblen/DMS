from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_EMPLOYEE = "employee"
    ROLE_MANAGER = "manager"
    ROLE_ASSISTANT = "assistant"

    ROLE_CHOICES = [
        (ROLE_EMPLOYEE, "Сотрудник"),
        (ROLE_MANAGER, "Начальник"),
        (ROLE_ASSISTANT, "Помощник"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_EMPLOYEE, db_index=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_online = models.BooleanField(default=False, db_index=True)
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)
    email = models.EmailField(db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)


    def is_employee(self):
        return self.role == self.ROLE_EMPLOYEE

    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    def is_assistant(self):
        return self.role == self.ROLE_ASSISTANT


class RoleRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    requested_role = models.CharField(max_length=10, choices=User.ROLE_CHOICES, db_index=True)
    is_approved = models.BooleanField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return (
            f"Запрос роли '{self.get_requested_role_display()}' от {self.user.username}"
        )


