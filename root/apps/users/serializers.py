# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Public registration serializer. Keeps user inactive by default (email
    verification required). If you prefer instant activation, set is_active=True
    in create() and remove the activation flow.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", "display_name")
        read_only_fields = ("id",)

    def validate_password(self, value):
        # optional: run Django password validators
        from django.contrib.auth.password_validation import validate_password
        validate_password(value, user=None)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False  # keep inactive until verification
        user.save()
        # NOTE: call activation/email sending logic here (e.g. create Activation and send mail)
        # Example: ActivationService.create_activation_for(user, request=self.context.get("request"))
        return user


class UserSerializer(serializers.ModelSerializer):
    """Used for profile GET + update (self)."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "avatar")
        read_only_fields = ("id", "username", "email")


class AdminUserSerializer(serializers.ModelSerializer):
    """Used when admin/staff reads or updates other users."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "avatar", "is_active", "is_staff")
        read_only_fields = ("id",)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT TokenObtainPairSerializer to optionally include org_id and role
    into returned tokens if the user has a membership for that org.

    NOTE:
    - Expect org id as a string (UUID) in request.data['org_id'] or header 'X-ORGANIZATION-ID'.
    - Do not cast org_id to int when using UUID PKs.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")
        org_id = None
        if request is not None:
            # canonical header name: X-ORGANIZATION-ID
            org_id = request.data.get("org_id") or request.headers.get("X-ORGANIZATION-ID")

        if org_id:
            try:
                # Lazy import to avoid circular import during startup
                from apps.tenants.models import OrganizationMembership
                # Use string comparison to support UUID PKs or integer PKs consistently
                membership = OrganizationMembership.objects.filter(user=self.user, organization_id=str(org_id)).first()
                if membership:
                    # Create a fresh token with additional claims
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken.for_user(self.user)
                    access = refresh.access_token
                    # keep IDs as strings (UUIDs) to avoid int() failures
                    access["org_id"] = str(org_id)
                    access["role"] = membership.role

                    data["refresh"] = str(refresh)
                    data["access"] = str(access)
                    data["org_id"] = str(org_id)
                    data["role"] = membership.role
            except Exception as exc:
                # log the exception; do not silently swallow in production
                logger.exception("Error while adding org claim to token: %s", exc)

        return data
