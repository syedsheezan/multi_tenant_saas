from rest_framework import serializers
from django.conf import settings
from .models import Project, ProjectMembership
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    tenant = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id','tenant','name','slug','description','owner','is_public','archived','created_at','updated_at']
        read_only_fields = ['id','tenant','owner','created_at','updated_at']

    def create(self, validated_data):
        request = self.context['request']
        # tenant should be injected by middleware or view
        validated_data['owner'] = request.user
        validated_data['tenant'] = request.tenant
        return super().create(validated_data)

class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ProjectMembership
        fields = ['id','project','user','role','joined_at']
        read_only_fields = ['id','joined_at']

