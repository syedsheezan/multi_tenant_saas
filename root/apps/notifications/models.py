import uuid
from django.db import models
from django.conf import settings
from apps.tenants.models import Organization


class Notification(models.Model):
    LEVEL_INFO = "info"
    LEVEL_WARNING = "warning"
    LEVEL_ERROR = "error"

    LEVEL_CHOICES = [
        (LEVEL_INFO, "Info"),
        (LEVEL_WARNING, "Warning"),
        (LEVEL_ERROR, "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actor_notifications"
    )

    verb = models.CharField(max_length=100)  # e.g. "task_assigned"

    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default=LEVEL_INFO
    )

    title = models.CharField(max_length=255, blank=True)

    # JSON payload (works for all DBs, not just Postgres)
    data = models.JSONField(blank=True, null=True)

    is_read = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.verb} -> {self.recipient}"
