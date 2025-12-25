from django.db import models
from django.conf import settings
from apps.tenants.models import Organization
import uuid

class Project(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    tenant = models.ForeignKey('tenants.Organization', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=False)  # you may enforce unique per tenant
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_projects')
    is_public = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True, blank=True,related_name="assigned_projects")

    class Meta:
        unique_together = (('tenant','slug'),)
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.tenant})"

class ProjectMembership(models.Model):
    ROLE_CHOICES = (('owner','Owner'),('member','Member'),('viewer','Viewer'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('project','user'),)
