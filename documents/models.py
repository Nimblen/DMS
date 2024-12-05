from django.db import models
from django.conf import settings


from documents.validators import validate_file_size


class Document(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "На рассмотрении"),
        (STATUS_ACCEPTED, "Принято"),
        (STATUS_REJECTED, "Отклонено"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents"
    )
    pdf_file = models.FileField(upload_to="documents/", validators=[validate_file_size])
    mfo = models.CharField(max_length=9)
    document_type = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "assigned_to"]),
        ]

    def __str__(self):
        return f"{self.employee} - {self.status}"