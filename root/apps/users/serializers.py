from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.crypto import get_random_string

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Public registration serializer.
    By default we create the user with is_active=False so email verification
    can be required before allowing org actions. If you prefer instant activation,
    remove the line that sets is_active=False in create().
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name", "display_name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        # create inactive user (require email verification). Change as needed.
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = False  # require email verification OR admin activation
        user.save()
        # NOTE: send verification email here (implement send_verification_email)
        # Example placeholder:
        # send_verification_email(user, token=generate_token(user))
        return user


class UserSerializer(serializers.ModelSerializer):
    """Used for profile GET + update (self)."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "avatar")
        read_only_fields = ("id", "username", "email")  # email/username read-only for profile updates


class AdminUserSerializer(serializers.ModelSerializer):
    """Used when admin/staff reads or updates other users."""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "display_name", "avatar", "is_active", "is_staff")
        read_only_fields = ("id",)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT TokenObtainPairSerializer to accept optional 'org_id'
    and, if the user has a membership for that org, include `org_id` and `role`
    in the returned token pair.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        request = self.context.get("request")
        org_id = None
        if request is not None:
            org_id = request.data.get("org_id") or request.headers.get("X-Org-Id")

        if org_id:
            try:
                # Lazy import to avoid circular import during startup
                from apps.tenants.models import OrganizationMembership
                membership = OrganizationMembership.objects.filter(user=self.user, organization_id=org_id).first()
                if membership:
                    from rest_framework_simplejwt.tokens import RefreshToken
                    refresh = RefreshToken.for_user(self.user)
                    access = refresh.access_token
                    access["org_id"] = int(org_id)
                    access["role"] = membership.role

                    data["refresh"] = str(refresh)
                    data["access"] = str(access)
                    data["org_id"] = int(org_id)
                    data["role"] = membership.role
            except Exception:
                # tenants may not exist yet in your environment; ignore gracefully
                pass

        return data
