from rest_framework import serializers
from .models import Organization, OrganizationMembership, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'name', 'max_users']


class OrganizationSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    plan_id = serializers.PrimaryKeyRelatedField(queryset=Plan.objects.all(), source='plan', write_only=True, required=False)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'owner', 'plan', 'plan_id', 'created_at', 'is_active']
        read_only_fields = ['id', 'owner', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        # Owner: set from request.user if provided
        if request and request.user and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = OrganizationMembership
        fields = ['id', 'user', 'organization', 'role', 'joined_at', 'is_active']
        read_only_fields = ['id', 'joined_at']
