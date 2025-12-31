from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone

class User(AbstractUser):
    """
    Simple extendable user model. Keep it light — add profile fields later.
    Uses username + email by default.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.URLField(blank=True, null=True)

    def __str__(self):
        # prefer display name, then full name, then username
        return self.display_name or self.get_full_name() or self.username

# Create your models here.
# apps/users/models.py


class Activation(models.Model):
    """
    One-time activation token for new users (email verification).
    Token is stored server-side for simplicity and revocation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activations')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["user"]),
        ]

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])
