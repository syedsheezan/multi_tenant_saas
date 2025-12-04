from rest_framework import permissions
from apps.tenants.models import OrganizationMembership

class IsOrgMember(permissions.BasePermission):
    def has_permission(self, request, view):
        org = getattr(request, "organization", None)
        if not org or not request.user.is_authenticated:
            return False
        return OrganizationMembership.objects.filter(
            user=request.user,
            organization=org,
            is_active=True
        ).exists()


class IsOrgAdminOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        org = getattr(request, "organization", None)
        user = request.user

        if org.owner_id == user.id:
            return True

        try:
            membership = OrganizationMembership.objects.get(user=user, organization=org)
            return membership.role in ("admin", "owner")
        except:
            return False
