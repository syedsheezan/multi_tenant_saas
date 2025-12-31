# apps/webhooks/serializers.py
from rest_framework import serializers
from .models import WebhookSubscription

ALLOWED_EVENTS = {"task.created", "task.updated", "task.deleted", "comment.added"}

class WebhookSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookSubscription
        fields = ["id", "organization", "url", "events", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]

    def validate_events(self, value):
        if not isinstance(value, (list, tuple)):
            raise serializers.ValidationError("events must be a list")
        invalid = [e for e in value if e not in ALLOWED_EVENTS]
        if invalid:
            raise serializers.ValidationError(f"Invalid events: {invalid}")
        return value

    def create(self, validated_data):
        # attach organization from request context
        validated_data["organization"] = self.context["request"].organization
        return super().create(validated_data)
