from rest_framework import serializers
from .models import File


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "organization",
            "project",
            "task",
            "file",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if not attrs.get("project") and not attrs.get("task"):
            raise serializers.ValidationError(
                "File must be attached to either a project or a task"
            )
        return attrs
