from rest_framework import permissions
from .models import OrganizationMembership

class IsTenantProvided(permissions.BasePermission):
    """
    Require organization context in request (via TenantMiddleware).
    """
    message = "Organization (tenant) is required in request header: X-ORGANIZATION-ID"

    def has_permission(self, request, view):
        return getattr(request, 'organization', None) is not None


class IsOrgOwnerOrAdmin(permissions.BasePermission):
    """
    Allow only Owner/Admin users to manage organization data.
    """

    def has_permission(self, request, view):
        org = getattr(request, 'organization', None)
        user = request.user

        if not org or not user or not user.is_authenticated:
            return False

        # User is owner → Full access
        if org.owner_id == user.id:
            return True

        # User is member → Check role
        try:
            membership = OrganizationMembership.objects.get(
                user=user,
                organization=org,
                is_active=True
            )
            return membership.role in (
                OrganizationMembership.ROLE_OWNER,
                OrganizationMembership.ROLE_ADMIN
            )
        except OrganizationMembership.DoesNotExist:
            return False
