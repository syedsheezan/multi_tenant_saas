# apps/tenants/permissions.py
from rest_framework import permissions
from .models import OrganizationMembership

class IsTenantProvided(permissions.BasePermission):
    """
    Require organization context in request (set by TenantMiddleware).
    """
    message = "Organization (tenant) is required in request header: X-ORGANIZATION-ID"

    def has_permission(self, request, view):
        return getattr(request, 'organization', None) is not None


class IsOrgOwnerOrAdmin(permissions.BasePermission):
    """
    Allow only Owner/Admin users to manage organization data.

    Behavior:
    - Superusers bypass the check (optional; remove that branch if you DO NOT want superuser bypass).
    - Owner (org.owner_id) has full access.
    - Active membership with role in (owner, admin) has access.
    """

    def has_permission(self, request, view):
        org = getattr(request, 'organization', None)
        user = request.user

        if not org or not user or not user.is_authenticated:
            return False

        # Optional: superuser bypass
        if getattr(user, "is_superuser", False):
            return True

        # If owner_id may be UUID or string, compare via pk for safety
        # `org.owner_id` could be a UUID object or string depending on DB/driver
        try:
            if str(org.owner_id) == str(user.pk):
                return True
        except Exception:
            # fallback to direct equality (defensive)
            if getattr(org, "owner_id", None) == getattr(user, "pk", None):
                return True

        # Check for an active membership with allowed roles
        return OrganizationMembership.objects.filter(
            user=user,
            organization=org,
            is_active=True,
            role__in=(OrganizationMembership.ROLE_OWNER, OrganizationMembership.ROLE_ADMIN)
        ).exists()
