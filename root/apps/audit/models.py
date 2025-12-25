from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings
from apps.tenants.models import Organization


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("invite_sent", "Invite Sent"),
        ("invite_accepted", "Invite Accepted"),
        ("invite_rejected", "Invite Rejected"),
        ("task_created", "Task Created"),
        ("task_assigned", "Task Assigned"),
        ("task_deleted", "Task Deleted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=50)
    object_id = models.UUIDField(null=True, blank=True)

    message = models.TextField()
    metadata = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.actor}"
