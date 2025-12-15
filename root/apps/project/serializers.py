from rest_framework import serializers
from .models import Project, ProjectMembership
from apps.tenants.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    # tenant comes from request body (UUID)
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        write_only=True,
        required=False
    )

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "tenant",
            "name",
            "slug",
            "description",
            "owner",
            "is_public",
            "archived",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["tenant"] = str(instance.tenant_id)
        return data


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjectMembership
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]
