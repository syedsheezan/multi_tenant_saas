# apps/tenants/models.py
import uuid
from django.db import models
from django.conf import settings
def generate_invite_token():
    # token_urlsafe returns a URL-safe text string; limit length by slicing if needed
    return secrets.token_urlsafe(32)

class Plan(models.Model):
    """
    Subscription plans (Free / Pro / Enterprise).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    max_users = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_organizations',
                              on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MEMBER, 'Member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='memberships', on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name='memberships', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # prefer UniqueConstraint with name for clarity and future migrations
        constraints = [
            models.UniqueConstraint(fields=('user', 'organization'), name='unique_membership_per_org')
        ]
        indexes = [
            models.Index(fields=['organization', 'user']),
        ]

    def __str__(self):
        return f"{self.user} @ {self.organization} ({self.role})"
    
# paste at the end of apps/tenants/models.py

import secrets
from django.utils import timezone

class OrganizationInvitation(models.Model):
    """
    Invitation to join an organization. Token is one-time use and may expire.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    invited_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='invitations_received', on_delete=models.SET_NULL)
    email = models.EmailField(null=True, blank=True)
    role = models.CharField(max_length=20, default=OrganizationMembership.ROLE_MEMBER)
    token = models.CharField(max_length=64, unique=True, db_index=True, default=lambda: secrets.token_urlsafe(32))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    token = models.CharField(max_length=64, unique=True, db_index=True, default=generate_invite_token)


    def is_expired(self):
        return self.expires_at is not None and timezone.now() > self.expires_at

    def __str__(self):
        return f"Invite {self.email or self.invited_user} -> {self.organization}"

