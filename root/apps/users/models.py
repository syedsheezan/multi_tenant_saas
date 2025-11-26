from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Simple extendable user model. Keep it light — add profile fields later.
    Uses username + email by default.
    """
    display_name = models.CharField(max_length=150, blank=True)
    avatar = models.URLField(blank=True, null=True)

    def __str__(self):
        # prefer display name, then full name, then username
        return self.display_name or self.get_full_name() or self.username

# Create your models here.
