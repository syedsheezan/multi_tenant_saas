from django.db import models
from django.conf import settings
from django.utils import timezone

class WebhookSubscription(models.Model):
    EVENT_CHOICES = [
        ("task.created", "Task Created"),
        ("task.updated", "Task Updated"),
        ("task.deleted", "Task Deleted"),
        ("comment.added", "Task Comment Added"),
    ]

    organization = models.ForeignKey(
        "tenants.Organization",
        on_delete=models.CASCADE,
        related_name="webhook_subscriptions"
    )
    url = models.URLField()
    events = models.JSONField(default=list, blank=True, null=False)

    secret = models.CharField(max_length=255)   # used for HMAC SHA256 signing
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook({self.organization.name} → {self.url})"
