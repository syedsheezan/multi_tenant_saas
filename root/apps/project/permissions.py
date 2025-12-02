from rest_framework import permissions

class IsProjectOwnerOrReadOnly(permissions.BasePermission):
    """
    Safe methods allowed to members/viewers depending on is_public.
    Writes only allowed to owner or org admins.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # public projects visible, otherwise must be a member
            if obj.is_public:
                return True
            # check membership:
            return obj.memberships.filter(user=request.user).exists()
        # write methods:
        return obj.owner_id == request.user.id or getattr(request.user, 'is_admin', False)
